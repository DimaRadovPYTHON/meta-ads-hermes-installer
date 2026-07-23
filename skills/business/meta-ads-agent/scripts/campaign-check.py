#!/usr/bin/env python3
"""
Meta Ads Campaign Check Script
Runs as a cron job to evaluate campaigns against automation rules.
Outputs JSON for the Hermes agent to process and deliver.

Environment variables:
  META_ADS_TOKEN — Meta Access Token
  META_ADS_ACCOUNT_ID — Ad Account ID
"""

import os
import json
import sys
from datetime import datetime, timedelta

try:
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.api import FacebookAdsApi
except ImportError:
    print(json.dumps({"error": "facebook-business SDK not installed. Run: pip3 install facebook-business>=19.0.0"}))
    sys.exit(1)

# ── Config ─────────────────────────────────────────────────────────────────

TOKEN = os.environ.get("META_ADS_TOKEN", "")
ACCOUNT_ID = os.environ.get("META_ADS_ACCOUNT_ID", "act_")

# Default thresholds (override via env vars)
TARGET_ROAS = float(os.environ.get("META_ADS_TARGET_ROAS", "4.0"))
MAX_CPA = float(os.environ.get("META_ADS_MAX_CPA", "20.0"))
PAUSE_THRESHOLD = float(os.environ.get("META_ADS_PAUSE_THRESHOLD", "2.0"))
SCALE_THRESHOLD = float(os.environ.get("META_ADS_SCALE_THRESHOLD", "1.3"))
SCALE_DAYS = int(os.environ.get("META_ADS_SCALE_DAYS", "3"))
SCALE_INCREMENT = float(os.environ.get("META_ADS_SCALE_INCREMENT", "0.2"))
FATIGUE_FREQ = float(os.environ.get("META_ADS_FATIGUE_FREQUENCY", "3.5"))
FATIGUE_CTR_DROP = float(os.environ.get("META_ADS_FATIGUE_CTR_DROP", "0.25"))
ALERT_ONLY = os.environ.get("META_ADS_ALERT_ONLY", "false").lower() == "true"

# ── Helpers ────────────────────────────────────────────────────────────────

def fmt_usd(cents):
    """Convert cents to dollar string."""
    return f"${float(cents or 0):.2f}"

def fmt_pct(val):
    """Format a ratio as percentage string."""
    return f"{float(val or 0)*100:.1f}%"

def fmt_float(val, decimals=2):
    return round(float(val or 0), decimals)

def get_7d_insights(ad_object, fields=None):
    """Get 7-day insights for a given ad object."""
    if fields is None:
        fields = [
            "spend", "impressions", "clicks", "reach", "frequency",
            "ctr", "cpc", "cpm", "conversions", "cost_per_conversion",
            "conversion_values", "roas"
        ]
    params = {
        "date_preset": "last_7d",
        "time_increment": 1,
    }
    try:
        return ad_object.get_insights(fields=fields, params=params)
    except Exception as e:
        return []

def get_prev_7d_ctr(ad_object):
    """Get CTR from the 7-14 day period for fatigue comparison."""
    fields = ["ctr"]
    now = datetime.now()
    params = {
        "time_range": {
            "since": (now - timedelta(days=14)).strftime("%Y-%m-%d"),
            "until": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
        }
    }
    try:
        insights = ad_object.get_insights(fields=fields, params=params)
        if insights:
            return float(insights[0].get("ctr", 0))
    except:
        pass
    return 0.0

# ── Rule Evaluators ────────────────────────────────────────────────────────

def evaluate_ad_set(ad_set, insights_data, prev_ctr):
    """
    Evaluate a single ad set against all rules.
    Returns list of actions and alerts.
    """
    actions = []
    alerts = []
    name = ad_set.get("name", "Unknown")
    ad_set_id = ad_set.get("id", "")

    # Get latest insights (last 7 days aggregated)
    spend = float(insights_data.get("spend", 0))
    impressions = int(insights_data.get("impressions", 0))
    clicks = int(insights_data.get("clicks", 0))
    reach = int(insights_data.get("reach", 0))
    frequency = float(insights_data.get("frequency", 0))
    ctr = float(insights_data.get("ctr", 0))
    conversions = int(insights_data.get("conversions", 0))
    cost_per_conv = float(insights_data.get("cost_per_conversion", 0))
    roas = float(insights_data.get("roas", 0))

    status = ad_set.get("status", "")
    daily_budget = float(ad_set.get("daily_budget", 0)) / 100  # cents to dollars

    # Skip if already paused or not spending
    if status == "PAUSED" or spend == 0:
        return actions, alerts

    # ── Rule 1: Pause underperformers ──
    if conversions >= 5:
        cpa_ratio = cost_per_conv / MAX_CPA if MAX_CPA > 0 else 0
        if cpa_ratio > PAUSE_THRESHOLD and spend >= daily_budget * 0.5:
            action = {
                "type": "pause",
                "target_id": ad_set_id,
                "target_name": name,
                "reason": f"CPA ${cost_per_conv:.2f} is {cpa_ratio:.1f}x target (${MAX_CPA})",
                "metric": "cpa",
                "value": cost_per_conv,
                "threshold": MAX_CPA * PAUSE_THRESHOLD,
            }
            if not ALERT_ONLY:
                actions.append(action)
            alert = {
                "severity": "warning",
                "message": f"Ad set '{name}' CPA ${cost_per_conv:.2f} exceeds {PAUSE_THRESHOLD}x target",
                "suggested_action": "pause" if ALERT_ONLY else "auto-paused",
            }
            alerts.append(alert)

    # ── Rule 2: Scale winners ──
    if roas >= TARGET_ROAS * SCALE_THRESHOLD and spend > 0:
        action = {
            "type": "scale",
            "target_id": ad_set_id,
            "target_name": name,
            "reason": f"ROAS {roas:.2f}x is >= {SCALE_THRESHOLD}x target ({TARGET_ROAS})",
            "metric": "roas",
            "value": roas,
            "threshold": TARGET_ROAS * SCALE_THRESHOLD,
            "budget_increase_pct": SCALE_INCREMENT * 100,
        }
        if not ALERT_ONLY:
            actions.append(action)
        alert = {
            "severity": "info",
            "message": f"Ad set '{name}' ROAS {roas:.2f}x — candidate for +{SCALE_INCREMENT*100:.0f}% budget increase",
            "suggested_action": "scale" if ALERT_ONLY else "auto-scaled",
        }
        alerts.append(alert)

    # ── Rule 3: Creative fatigue ──
    if frequency > FATIGUE_FREQ and prev_ctr > 0 and ctr > 0:
        ctr_drop = (prev_ctr - ctr) / prev_ctr if prev_ctr > 0 else 0
        if ctr_drop > FATIGUE_CTR_DROP:
            action = {
                "type": "pause_creative",
                "target_id": ad_set_id,
                "target_name": name,
                "reason": f"Fatigue: freq={frequency:.1f}, CTR dropped {ctr_drop*100:.0f}%",
                "metric": "frequency",
                "value": frequency,
                "ctr_drop_pct": ctr_drop * 100,
                "threshold_freq": FATIGUE_FREQ,
                "threshold_ctr_drop": FATIGUE_CTR_DROP * 100,
            }
            if not ALERT_ONLY:
                actions.append(action)
            alert = {
                "severity": "warning",
                "message": f"Creative fatigue in '{name}': frequency={frequency:.1f}, CTR dropped {ctr_drop*100:.0f}%",
                "suggested_action": "rotate creatives" if ALERT_ONLY else "auto-paused",
            }
            alerts.append(alert)

    # ── Rule 4: Budget pacing alert ──
    if daily_budget > 0:
        spend_pct = (spend / daily_budget) * 100
        if spend_pct > 80:
            alert = {
                "severity": "info",
                "message": f"Ad set '{name}' spent {spend_pct:.0f}% of daily budget (${spend:.2f}/${daily_budget:.2f})",
                "suggested_action": "monitor",
            }
            alerts.append(alert)

    return actions, alerts


def check_campaigns():
    """Main evaluation loop over all active campaigns."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "account_id": ACCOUNT_ID,
        "summary": {"campaigns_checked": 0, "ad_sets_evaluated": 0, "actions_taken": 0, "alerts_generated": 0},
        "campaigns": [],
        "actions": [],
        "alerts": [],
    }

    if not TOKEN or TOKEN == "":
        results["error"] = "META_ADS_TOKEN not set"
        return results

    try:
        FacebookAdsApi.init(access_token=TOKEN)
        account = AdAccount(ACCOUNT_ID)
    except Exception as e:
        results["error"] = f"Auth failed: {str(e)}"
        return results

    # Fetch active campaigns
    try:
        campaigns = account.get_campaigns(
            fields=["id", "name", "status", "daily_budget", "lifetime_budget"],
            params={"effective_status": ["ACTIVE"]},
        )
    except Exception as e:
        results["error"] = f"Failed to fetch campaigns: {str(e)}"
        return results

    for campaign in campaigns:
        camp_data = {
            "id": campaign.get("id", ""),
            "name": campaign.get("name", ""),
            "status": campaign.get("status", ""),
            "ad_sets": [],
        }
        results["summary"]["campaigns_checked"] += 1

        # Fetch ad sets in this campaign
        try:
            ad_sets = campaign.get_ad_sets(
                fields=[
                    "id", "name", "status", "daily_budget", "lifetime_budget",
                    "bid_strategy", "optimization_goal",
                ],
                params={"effective_status": ["ACTIVE"]},
            )
        except Exception as e:
            camp_data["error"] = str(e)
            results["campaigns"].append(camp_data)
            continue

        for ad_set in ad_sets:
            as_data = {
                "id": ad_set.get("id", ""),
                "name": ad_set.get("name", ""),
                "status": ad_set.get("status", ""),
                "budget": ad_set.get("daily_budget", 0),
            }
            results["summary"]["ad_sets_evaluated"] += 1

            # Get insights
            insights_data = {}
            prev_ctr = 0.0
            try:
                insights_list = get_7d_insights(ad_set)
                if insights_list:
                    insights_data = dict(insights_list[0])
                prev_ctr = get_prev_7d_ctr(ad_set)
            except Exception as e:
                as_data["error"] = str(e)
                camp_data["ad_sets"].append(as_data)
                continue

            # Add metrics to ad set data
            as_data["metrics"] = {
                "spend": fmt_float(insights_data.get("spend", 0)),
                "impressions": int(insights_data.get("impressions", 0)),
                "clicks": int(insights_data.get("clicks", 0)),
                "ctr": fmt_pct(insights_data.get("ctr", 0)),
                "frequency": fmt_float(insights_data.get("frequency", 0)),
                "cpa": fmt_float(insights_data.get("cost_per_conversion", 0)),
                "roas": fmt_float(insights_data.get("roas", 0)),
                "conversions": int(insights_data.get("conversions", 0)),
                "reach": int(insights_data.get("reach", 0)),
            }

            # Evaluate rules
            actions, alerts = evaluate_ad_set(ad_set, insights_data, prev_ctr)
            as_data["actions_taken"] = len(actions)
            as_data["alerts"] = len(alerts)

            results["actions"].extend(actions)
            results["alerts"].extend(alerts)
            camp_data["ad_sets"].append(as_data)

        results["campaigns"].append(camp_data)

    results["summary"]["actions_taken"] = len(results["actions"])
    results["summary"]["alerts_generated"] = len(results["alerts"])
    return results


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = check_campaigns()
    print(json.dumps(result, indent=2, default=str))

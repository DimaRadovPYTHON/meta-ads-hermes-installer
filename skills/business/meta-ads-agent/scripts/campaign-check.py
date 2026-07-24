#!/usr/bin/env python3
"""
Meta Ads Campaign Check — MCP-based
Runs as a cron job or standalone to evaluate campaigns via Meta's official MCP.
Uses the Hermes MCP infrastructure to call Meta Ads tools.
Outputs JSON for the Hermes agent to process and deliver.

Usage:
  # Through Hermes cron (recommended)
  # Just load the meta-ads-agent skill and ask the agent to check campaigns

  # Standalone test (requires META_ADS_MCP_TOKEN env var)
  python3 campaign-check.py
"""

import os
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# ── Config ─────────────────────────────────────────────────────────────────

MCP_URL = "https://mcp.facebook.com/ads"
MCP_TOKEN = os.environ.get("META_ADS_MCP_TOKEN", "")
ACCOUNT_ID = os.environ.get("META_ADS_ACCOUNT_ID", "")
TARGET_ROAS = float(os.environ.get("META_ADS_TARGET_ROAS", "4.0"))
MAX_CPA = float(os.environ.get("META_ADS_MAX_CPA", "20.0"))
PAUSE_THRESHOLD = float(os.environ.get("META_ADS_PAUSE_THRESHOLD", "2.0"))
SCALE_THRESHOLD = float(os.environ.get("META_ADS_SCALE_THRESHOLD", "1.3"))
FATIGUE_FREQ = float(os.environ.get("META_ADS_FATIGUE_FREQUENCY", "3.5"))
FATIGUE_CTR_DROP = float(os.environ.get("META_ADS_FATIGUE_CTR_DROP", "0.25"))
ALERT_ONLY = os.environ.get("META_ADS_ALERT_ONLY", "true").lower() == "true"


# ── MCP Client ─────────────────────────────────────────────────────────────

def mcp_call(tool_name, arguments=None):
    """Call a Meta MCP tool via JSON-RPC over HTTP."""
    if not MCP_TOKEN:
        return {"error": "META_ADS_MCP_TOKEN not set — run through Hermes with MCP configured"}

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }

    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MCP_TOKEN}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if "error" in result:
                return {"error": result["error"]["message"]}
            # MCP returns result.content as list of content items
            content = result.get("result", {}).get("content", [])
            text = ""
            for item in content:
                if item.get("type") == "text":
                    text += item.get("text", "")
            if text:
                return json.loads(text)
            return result.get("result", {})
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


# ── Rule Evaluators ────────────────────────────────────────────────────────

def evaluate_campaign(campaign, ad_sets):
    """Evaluate a campaign's ad sets against all rules."""
    actions = []
    alerts = []
    name = campaign.get("name", "Unknown")
    campaign_id = campaign.get("id", "")

    for ad_set in ad_sets:
        as_name = ad_set.get("name", "Unknown")
        as_id = ad_set.get("id", "")

        metrics = ad_set.get("insights", {}).get("data", [{}])
        if not metrics:
            continue
        m = metrics[0] if isinstance(metrics, list) else metrics

        spend = float(m.get("spend", 0))
        impressions = int(m.get("impressions", 0))
        frequency = float(m.get("frequency", 0))
        ctr = float(m.get("ctr", 0))
        conversions = int(m.get("conversions", 0))
        cost_per_conv = float(m.get("cost_per_conversion", 0))
        roas = float(m.get("roas", 0))

        status = ad_set.get("status", "")
        daily_budget = float(ad_set.get("daily_budget", 0))

        if status == "PAUSED" or spend == 0:
            continue

        # Rule 1: Pause underperformers
        if conversions >= 5:
            cpa_ratio = cost_per_conv / MAX_CPA if MAX_CPA > 0 else 0
            if cpa_ratio > PAUSE_THRESHOLD and spend >= daily_budget * 0.5:
                action = {
                    "type": "pause",
                    "target_id": as_id,
                    "target_name": as_name,
                    "reason": f"CPA ${cost_per_conv:.2f} is {cpa_ratio:.1f}x target (${MAX_CPA})",
                }
                if not ALERT_ONLY:
                    actions.append(action)
                alerts.append({
                    "severity": "warning",
                    "message": f"Ad set '{as_name}' CPA ${cost_per_conv:.2f} exceeds threshold",
                })

        # Rule 2: Scale winners
        if roas >= TARGET_ROAS * SCALE_THRESHOLD and spend > 0:
            action = {
                "type": "scale",
                "target_id": as_id,
                "target_name": as_name,
                "reason": f"ROAS {roas:.2f}x >= {SCALE_THRESHOLD}x target ({TARGET_ROAS})",
            }
            if not ALERT_ONLY:
                actions.append(action)
            alerts.append({
                "severity": "info",
                "message": f"Ad set '{as_name}' ROAS {roas:.2f}x — candidate for scaling",
            })

        # Rule 3: Creative fatigue
        prev_ctr = float(m.get("ctr_7d_ago", 0))
        if frequency > FATIGUE_FREQ and prev_ctr > 0 and ctr > 0:
            ctr_drop = (prev_ctr - ctr) / prev_ctr if prev_ctr > 0 else 0
            if ctr_drop > FATIGUE_CTR_DROP:
                action = {
                    "type": "pause_creative",
                    "target_id": as_id,
                    "target_name": as_name,
                    "reason": f"Fatigue: freq={frequency:.1f}, CTR dropped {ctr_drop*100:.0f}%",
                }
                if not ALERT_ONLY:
                    actions.append(action)
                alerts.append({
                    "severity": "warning",
                    "message": f"Creative fatigue in '{as_name}': freq={frequency:.1f}",
                })

    return actions, alerts


# ── Main ───────────────────────────────────────────────────────────────────

def check_campaigns():
    """Fetch campaigns via MCP and evaluate them."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "account_id": ACCOUNT_ID,
        "summary": {"campaigns_checked": 0, "actions_taken": 0, "alerts_generated": 0},
        "campaigns": [],
        "actions": [],
        "alerts": [],
    }

    # Fetch campaigns via MCP
    campaigns_data = mcp_call("get_campaigns", {
        "account_id": ACCOUNT_ID if ACCOUNT_ID.startswith("act_") else f"act_{ACCOUNT_ID}"
    })

    if "error" in campaigns_data:
        results["error"] = campaigns_data["error"]
        return results

    campaigns = campaigns_data.get("data", campaigns_data.get("campaigns", []))
    if isinstance(campaigns_data, dict) and not campaigns:
        campaigns = [campaigns_data]

    for campaign in campaigns:
        camp_name = campaign.get("name", "Unknown")
        camp_id = campaign.get("id", "")
        results["summary"]["campaigns_checked"] += 1

        # Fetch ad sets for this campaign
        ad_sets_data = mcp_call("get_ad_sets", {
            "campaign_id": camp_id,
            "account_id": ACCOUNT_ID
        })

        ad_sets = ad_sets_data.get("data", ad_sets_data.get("ad_sets", []))
        if isinstance(ad_sets_data, dict) and not ad_sets and "name" in ad_sets_data:
            ad_sets = [ad_sets_data]

        # Fetch insights for the campaign
        insights_data = mcp_call("get_insights", {
            "campaign_id": camp_id,
            "account_id": ACCOUNT_ID,
            "date_preset": "last_7d"
        })

        actions, alerts = evaluate_campaign(campaign, ad_sets)
        results["actions"].extend(actions)
        results["alerts"].extend(alerts)

        results["campaigns"].append({
            "id": camp_id,
            "name": camp_name,
            "ad_sets_count": len(ad_sets),
            "actions_taken": len(actions),
        })

    results["summary"]["actions_taken"] = len(results["actions"])
    results["summary"]["alerts_generated"] = len(results["alerts"])
    return results


if __name__ == "__main__":
    result = check_campaigns()
    print(json.dumps(result, indent=2, default=str))

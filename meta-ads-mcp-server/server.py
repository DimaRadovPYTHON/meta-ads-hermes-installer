#!/usr/bin/env python3
"""
Meta Ads MCP Server
Model Context Protocol server that exposes Meta Marketing API as tools.
Uses stdio JSON-RPC (same pattern as Hermes Hound MCP server).

Environment:
  META_ADS_TOKEN — Meta Access Token with ads_management permission

Tools:
  get_campaigns      — List campaigns with performance insights
  get_ad_sets        — List ad sets with metrics (spend, CPA, ROAS, frequency)
  get_insights       — Get performance data
  pause_ad_set       — Pause an underperforming ad set
  update_budget      — Update campaign daily budget
  check_creative_fatigue — Check frequency + CTR trends across all ads
  get_alerts          — Generate alerts based on CPA/ROAS thresholds
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta

import requests

try:
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.ad import Ad
    from facebook_business.api import FacebookAdsApi
    HAS_FB_SDK = True
except ImportError:
    HAS_FB_SDK = False

# ── Config ─────────────────────────────────────────────────────────────────

TOKEN = os.environ.get("META_ADS_TOKEN", "")

# ── MCP Protocol ───────────────────────────────────────────────────────────

def mcp_respond(response):
    """Send a JSON-RPC response on stdout."""
    msg = json.dumps(response, default=str)
    sys.stdout.write(f"Content-Length: {len(msg)}\r\n\r\n{msg}")
    sys.stdout.flush()


def mcp_tool_result(request_id, result):
    """Send a successful tool result."""
    mcp_respond({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]},
    })


def mcp_error(request_id, code, message):
    """Send an error response."""
    mcp_respond({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    })


# ── Tool Implementations ──────────────────────────────────────────────────

def init_api():
    """Initialize the Facebook API with token."""
    if not HAS_FB_SDK:
        raise RuntimeError("facebook-business SDK not installed")
    if not TOKEN:
        raise RuntimeError("META_ADS_TOKEN environment variable not set")
    FacebookAdsApi.init(access_token=TOKEN)


def tool_get_campaigns(args):
    """List campaigns with insights."""
    init_api()
    account_id = args.get("ad_account_id", "")
    status_filter = args.get("status", "ACTIVE")

    if not account_id:
        return {"error": "ad_account_id is required"}

    try:
        account = AdAccount(account_id)
        campaigns = account.get_campaigns(
            fields=["id", "name", "status", "objective", "daily_budget", "lifetime_budget",
                    "bid_strategy", "created_time"],
            params={"effective_status": [status_filter]} if status_filter != "ALL" else {},
        )
        results = []
        for c in campaigns:
            data = dict(c)
            # Get 7-day insights
            try:
                insights = c.get_insights(
                    fields=["spend", "impressions", "clicks", "ctr", "cpc", "cpm",
                            "reach", "frequency", "conversions", "cost_per_conversion",
                            "conversion_values", "roas"],
                    params={"date_preset": "last_7d"},
                )
                if insights:
                    data["insights_7d"] = dict(insights[0])
            except Exception:
                data["insights_7d"] = {}
            results.append(data)
        return {"campaigns": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_ad_sets(args):
    """List ad sets with performance metrics."""
    init_api()
    account_id = args.get("ad_account_id", "")
    campaign_id = args.get("campaign_id", None)

    if not account_id:
        return {"error": "ad_account_id is required"}

    try:
        if campaign_id:
            campaign = Campaign(campaign_id)
            ad_sets = campaign.get_ad_sets(
                fields=["id", "name", "status", "daily_budget", "lifetime_budget",
                        "bid_strategy", "optimization_goal", "targeting"],
                params={"effective_status": ["ACTIVE", "PAUSED"]},
            )
        else:
            account = AdAccount(account_id)
            ad_sets = account.get_ad_sets(
                fields=["id", "name", "status", "daily_budget", "lifetime_budget",
                        "bid_strategy", "optimization_goal", "targeting"],
                params={"effective_status": ["ACTIVE", "PAUSED"]},
            )

        results = []
        for a in ad_sets:
            data = dict(a)
            # Get 7-day insights
            try:
                insights = a.get_insights(
                    fields=["spend", "impressions", "clicks", "ctr", "cpc", "cpm",
                            "reach", "frequency", "conversions", "cost_per_conversion",
                            "conversion_values", "roas"],
                    params={"date_preset": "last_7d"},
                )
                if insights:
                    data["insights_7d"] = dict(insights[0])
            except Exception:
                data["insights_7d"] = {}
            results.append(data)
        return {"ad_sets": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e)}


def tool_get_insights(args):
    """Get performance data for an ad account."""
    init_api()
    account_id = args.get("ad_account_id", "")
    level = args.get("level", "campaign")
    date_preset = args.get("date_preset", "last_7d")

    if not account_id:
        return {"error": "ad_account_id is required"}

    try:
        account = AdAccount(account_id)
        insights = account.get_insights(
            fields=["campaign_name", "campaign_id", "adset_name", "adset_id",
                    "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
                    "reach", "frequency", "conversions", "cost_per_conversion",
                    "conversion_values", "roas"],
            params={
                "level": level,
                "date_preset": date_preset,
                "time_increment": 1,
            },
        )
        results = [dict(i) for i in insights]
        return {"insights": results, "count": len(results), "level": level, "date_preset": date_preset}
    except Exception as e:
        return {"error": str(e)}


def tool_pause_ad_set(args):
    """Pause an ad set."""
    init_api()
    ad_set_id = args.get("ad_set_id", "")

    if not ad_set_id:
        return {"error": "ad_set_id is required"}

    try:
        ad_set = AdSet(ad_set_id)
        result = ad_set.api_update(params={"status": "PAUSED"})
        return {"ad_set_id": ad_set_id, "status": "PAUSED", "result": result}
    except Exception as e:
        return {"error": str(e)}


def tool_update_budget(args):
    """Update daily budget for a campaign."""
    init_api()
    campaign_id = args.get("campaign_id", "")
    daily_budget = args.get("daily_budget", 0)

    if not campaign_id:
        return {"error": "campaign_id is required"}
    if daily_budget <= 0:
        return {"error": "daily_budget must be positive"}

    try:
        campaign = Campaign(campaign_id)
        # Meta API expects budget in cents
        budget_cents = int(daily_budget * 100)
        result = campaign.api_update(params={"daily_budget": budget_cents})
        return {"campaign_id": campaign_id, "daily_budget": daily_budget, "budget_cents": budget_cents, "result": result}
    except Exception as e:
        return {"error": str(e)}


def tool_check_creative_fatigue(args):
    """Check for creative fatigue across active ads."""
    init_api()
    account_id = args.get("ad_account_id", "")
    freq_threshold = float(args.get("frequency_threshold", 3.5))
    ctr_drop_threshold = float(args.get("ctr_drop_threshold", 0.25))

    if not account_id:
        return {"error": "ad_account_id is required"}

    try:
        account = AdAccount(account_id)
        # Get current period CTR (last 7 days)
        current_insights = account.get_insights(
            fields=["ad_id", "ad_name", "frequency", "ctr", "spend", "impressions"],
            params={"level": "ad", "date_preset": "last_7d"},
        )
        # Get previous period CTR (7-14 days ago)
        now = datetime.now()
        prev_insights = account.get_insights(
            fields=["ad_id", "ad_name", "ctr"],
            params={
                "level": "ad",
                "time_range": {
                    "since": (now - timedelta(days=14)).strftime("%Y-%m-%d"),
                    "until": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                },
            },
        )

        # Build previous CTR lookup
        prev_ctr_map = {}
        for p in prev_insights:
            pid = p.get("ad_id")
            if pid:
                prev_ctr_map[pid] = float(p.get("ctr", 0))

        fatigued_ads = []
        for c in current_insights:
            ad_id = c.get("ad_id")
            ad_name = c.get("ad_name", "Unknown")
            frequency = float(c.get("frequency", 0))
            ctr = float(c.get("ctr", 0))
            prev_ctr = prev_ctr_map.get(ad_id, 0)

            if frequency > freq_threshold and prev_ctr > 0:
                ctr_drop = (prev_ctr - ctr) / prev_ctr
                if ctr_drop > ctr_drop_threshold:
                    fatigued_ads.append({
                        "ad_id": ad_id,
                        "ad_name": ad_name,
                        "frequency": round(frequency, 2),
                        "current_ctr": round(ctr, 4),
                        "previous_ctr": round(prev_ctr, 4),
                        "ctr_drop_pct": round(ctr_drop * 100, 1),
                        "spend": float(c.get("spend", 0)),
                        "severity": "high" if ctr_drop > 0.5 else "medium",
                    })

        return {
            "fatigued_ads": fatigued_ads,
            "fatigued_count": len(fatigued_ads),
            "total_ads_checked": len(current_insights),
            "frequency_threshold": freq_threshold,
            "ctr_drop_threshold": ctr_drop_threshold,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_get_alerts(args):
    """Generate alerts based on CPA and ROAS thresholds."""
    init_api()
    account_id = args.get("ad_account_id", "")
    target_cpa = float(args.get("target_cpa", 20.0))
    target_roas = float(args.get("target_roas", 4.0))

    if not account_id:
        return {"error": "ad_account_id is required"}

    alerts = []

    try:
        account = AdAccount(account_id)
        ad_sets = account.get_ad_sets(
            fields=["id", "name", "status", "daily_budget"],
            params={"effective_status": ["ACTIVE"]},
        )

        for a in ad_sets:
            try:
                insights = a.get_insights(
                    fields=["spend", "conversions", "cost_per_conversion", "roas", "frequency", "ctr"],
                    params={"date_preset": "last_7d"},
                )
                if not insights:
                    continue
                i = insights[0]
                cpa = float(i.get("cost_per_conversion", 0))
                roas = float(i.get("roas", 0))
                freq = float(i.get("frequency", 0))
                spend = float(i.get("spend", 0))

                name = a.get("name", "Unknown")

                # CPA breach
                if cpa > target_cpa * 2 and spend > 0:
                    alerts.append({
                        "type": "cpa_breach",
                        "severity": "critical",
                        "ad_set_id": a["id"],
                        "ad_set_name": name,
                        "message": f"CPA ${cpa:.2f} exceeds 2x target (${target_cpa})",
                        "cpa": round(cpa, 2),
                        "spend": round(spend, 2),
                    })

                # ROAS below target
                if roas > 0 and roas < target_roas * 0.5:
                    alerts.append({
                        "type": "roas_below_target",
                        "severity": "critical",
                        "ad_set_id": a["id"],
                        "ad_set_name": name,
                        "message": f"ROAS {roas:.2f}x below 50% of target ({target_roas}x)",
                        "roas": round(roas, 2),
                        "spend": round(spend, 2),
                    })

                # High frequency (potential fatigue)
                if freq > 3.5:
                    alerts.append({
                        "type": "high_frequency",
                        "severity": "warning",
                        "ad_set_id": a["id"],
                        "ad_set_name": name,
                        "message": f"Frequency {freq:.1f} exceeds 3.5 — possible creative fatigue",
                        "frequency": round(freq, 1),
                    })

            except Exception:
                continue

        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "target_cpa": target_cpa,
            "target_roas": target_roas,
            "account_id": account_id,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_send_webhook(args):
    """Send a structured alert or report to a webhook URL."""
    webhook_url = args.get("webhook_url", "")
    message = args.get("message", "")
    title = args.get("title", "Meta Ads Agent Alert")
    severity = args.get("severity", "info")
    payload = args.get("payload", {})

    if not webhook_url:
        return {"error": "webhook_url is required"}
    if not message:
        return {"error": "message is required"}

    try:
        body = {
            "title": title,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "source": "meta-ads-agent",
        }
        if payload:
            body["payload"] = payload

        resp = requests.post(
            webhook_url,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        return {
            "success": resp.ok,
            "status_code": resp.status_code,
            "webhook_url": webhook_url,
        }
    except requests.RequestException as e:
        return {"error": f"Webhook request failed: {str(e)}"}


# ── Tool Registry ──────────────────────────────────────────────────────────

TOOLS = {
    "get_campaigns": {
        "description": "List ad campaigns with 7-day performance insights",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID (act_XXX)"},
                "status": {"type": "string", "description": "Status filter: ACTIVE, PAUSED, ALL (default: ACTIVE)"},
            },
            "required": ["ad_account_id"],
        },
        "handler": tool_get_campaigns,
    },
    "get_ad_sets": {
        "description": "List ad sets with performance metrics",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID (act_XXX)"},
                "campaign_id": {"type": "string", "description": "Optional campaign ID to filter by"},
            },
            "required": ["ad_account_id"],
        },
        "handler": tool_get_ad_sets,
    },
    "get_insights": {
        "description": "Get performance data with time breakdown",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID (act_XXX)"},
                "level": {"type": "string", "description": "Report level: campaign, adset, ad (default: campaign)"},
                "date_preset": {"type": "string", "description": "Date range: today, yesterday, last_7d, last_14d, last_30d, last_month (default: last_7d)"},
            },
            "required": ["ad_account_id"],
        },
        "handler": tool_get_insights,
    },
    "pause_ad_set": {
        "description": "Pause an underperforming ad set",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_set_id": {"type": "string", "description": "Ad set ID to pause"},
            },
            "required": ["ad_set_id"],
        },
        "handler": tool_pause_ad_set,
    },
    "update_budget": {
        "description": "Update a campaign's daily budget (respects scaling rules)",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID to update"},
                "daily_budget": {"type": "number", "description": "New daily budget in dollars"},
            },
            "required": ["campaign_id", "daily_budget"],
        },
        "handler": tool_update_budget,
    },
    "check_creative_fatigue": {
        "description": "Check all ads for creative fatigue (frequency + CTR drop)",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID (act_XXX)"},
                "frequency_threshold": {"type": "number", "description": "Frequency threshold (default: 3.5)"},
                "ctr_drop_threshold": {"type": "number", "description": "CTR drop ratio threshold (default: 0.25)"},
            },
            "required": ["ad_account_id"],
        },
        "handler": tool_check_creative_fatigue,
    },
    "get_alerts": {
        "description": "Generate alerts based on CPA and ROAS thresholds",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID (act_XXX)"},
                "target_cpa": {"type": "number", "description": "Target CPA in dollars (default: 20)"},
                "target_roas": {"type": "number", "description": "Target ROAS multiplier (default: 4.0)"},
            },
            "required": ["ad_account_id"],
        },
        "handler": tool_get_alerts,
    },
    "send_webhook": {
        "description": "Send an alert, report, or notification to any webhook URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "webhook_url": {"type": "string", "description": "Webhook URL to send to (Discord, Slack, custom)"},
                "message": {"type": "string", "description": "Main message content"},
                "title": {"type": "string", "description": "Optional title (default: Meta Ads Agent Alert)"},
                "severity": {"type": "string", "description": "Severity level: info, warning, critical (default: info)"},
                "payload": {"type": "object", "description": "Additional structured data to include"},
            },
            "required": ["webhook_url", "message"],
        },
        "handler": tool_send_webhook,
    },
}


# ── Main Loop ──────────────────────────────────────────────────────────────

def handle_initialize(request):
    """Handle the initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
        },
        "serverInfo": {
            "name": "meta-ads-mcp-server",
            "version": "1.0.0",
        },
    }


def handle_list_tools(request):
    """Handle tools/list request."""
    return {
        "tools": [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["input_schema"],
            }
            for name, info in TOOLS.items()
        ]
    }


def handle_call_tool(request):
    """Handle tools/call request."""
    tool_name = request["params"]["name"]
    arguments = request["params"].get("arguments", {})

    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    return TOOLS[tool_name]["handler"](arguments)


def main():
    """Main MCP server loop — reads JSON-RPC from stdin."""
    buffer = ""
    content_length = 0

    if not HAS_FB_SDK:
        # Send a startup warning via stderr
        sys.stderr.write("WARNING: facebook-business SDK not installed. Install: pip3 install facebook-business>=19.0.0\n")

    while True:
        try:
            chunk = sys.stdin.read(4096)
            if not chunk:
                break
            buffer += chunk

            while True:
                # Parse headers
                if content_length == 0:
                    header_end = buffer.find("\r\n\r\n")
                    if header_end == -1:
                        break
                    header_part = buffer[:header_end]
                    for line in header_part.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            content_length = int(line.split(":")[1].strip())
                    buffer = buffer[header_end + 4:]

                if content_length == 0 or len(buffer) < content_length:
                    break

                # Parse message
                msg = buffer[:content_length]
                buffer = buffer[content_length:]
                content_length = 0

                try:
                    request = json.loads(msg)
                except json.JSONDecodeError as e:
                    continue

                method = request.get("method", "")
                req_id = request.get("id", str(uuid.uuid4()))

                try:
                    if method == "initialize":
                        result = handle_initialize(request)
                    elif method == "tools/list":
                        result = handle_list_tools(request)
                    elif method == "tools/call":
                        result = handle_call_tool(request)
                    elif method == "notifications/initialized":
                        continue  # No response needed
                    else:
                        mcp_error(req_id, -32601, f"Method not found: {method}")
                        continue

                    mcp_respond({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result,
                    })
                except Exception as e:
                    mcp_error(req_id, -32603, str(e))

        except (EOFError, KeyboardInterrupt):
            break
        except Exception:
            break


if __name__ == "__main__":
    main()

---
name: meta-ads-agent
description: "Deploy a Meta Ads Agent for a client — $200 setup / $50mo. Automated campaign management with bidding optimization, ROAS alerts, creative fatigue detection, and daily reports."
version: 1.0.0
author: Dima's AI Agency
platforms: [macos, linux]
metadata:
  hermes:
    tags: [meta-ads, facebook-ads, campaign-management, bidding, automation, service-package]
---

# Meta Ads Agent — Operation Guide

## Trigger

Use this skill when:
- Running the 15-minute campaign health check
- Analysing campaign performance data
- Deciding whether to pause or scale an ad set
- Generating daily performance reports
- Responding to alerts from the campaign check script

## What It Does

- Monitors Meta Ads campaigns every 15 minutes via the Marketing API
- Pauses underperforming ad sets below client's ROAS/CPA threshold
- Increases budget on winning campaigns (20% increments, never >50% weekly)
- Detects creative fatigue (frequency >3.5 AND CTR drop >25%)
- Sends daily performance reports and instant alerts to client's delivery channel

## The 5 Essential Automation Rules

| Rule | Trigger | Action |
|------|---------|--------|
| Pause underperformer | CPA > 2x target CPA AND spent ≥50% of daily budget AND ≥5 conversions | Pause ad set |
| Scale winner | ROAS ≥ 1.3x target for 3+ consecutive days | +20% budget increase (cap +50%/wk) |
| Creative fatigue | Frequency >3.5 AND CTR drop >25% from previous 7 days | Pause ad set, flag for creative rotation |
| Budget pacing | Spend >80% of daily budget before 6pm | Alert to monitor |
| Learning phase stuck | Campaign in learning limited for 7+ days | Alert to simplify targeting |

## Pricing

- **Setup:** $200 one-time
- **Monthly:** $50
- **Client pays API costs:** $10-50/mo (capped)

## Setup Steps

1. Install Hermes on client's machine (Mac recommended) or VPS
2. Run install.sh from the meta-ads-hermes-installer repo
3. During onboarding: connect Meta Marketing API (OAuth token + Ad Account ID)
4. Configure thresholds: target ROAS, max CPA, auto-pause vs alert-only
5. Choose delivery channel: Telegram, Discord, or Email
6. 48-hour test period (alert-only mode recommended), then go live

## Key Knowledge Files

- `references/professional-knowledge.md` — Full training data (bidding strategies, formulas, rules)
- `config.yaml` — Client-specific configuration
- `scripts/campaign-check.py` — The automation engine

## Pitfalls

- **Never change budget >50% at a time** — resets learning phase, destabilizes for 7-14 days
- **Wait 7-14 days before evaluating** — don't panic-pause during learning phase
- **Track blended ROAS, not Meta-reported** — Meta undercounts by 20-40%
- **Start with Lowest Cost** for new campaigns, add constraints after 50+ conversions
- **Alert-only mode first** — test for 48 hours before enabling auto-pause
- **Pause at ad set level, not campaign level** — one bad audience shouldn't kill profitable traffic

## Delivery

- 15-minute checks: status updates + actions taken
- Daily 9am report: full performance summary
- Instant alerts: CPA/ROAS threshold breaches, creative fatigue warnings

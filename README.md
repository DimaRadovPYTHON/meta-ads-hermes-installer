# Meta Ads Agent — Hermes Installer

> **One-command Meta Ads campaign automation for Hermes Agent.**  
> Deploy in minutes. Automate bidding, pause underperformers, scale winners, detect creative fatigue.

## What It Is

The Meta Ads Agent is a complete campaign management system that runs inside [Hermes Agent](https://hermes-agent.nousresearch.com). It connects to your Meta Ads account via the Marketing API and automatically:

- **Monitors** every campaign, ad set, and ad every 15 minutes
- **Pauses** underperforming ad sets when CPA exceeds your target (2x threshold)
- **Scales** winning campaigns with budget increases (20% increments, capped 50%/wk)
- **Detects** creative fatigue (frequency >3.5 + CTR drop >25%)
- **Reports** daily performance and instant alerts to Telegram / Discord / Email

## Pricing

| Item | Cost |
|------|------|
| **Setup fee** | $200 one-time |
| **Monthly management** | $50/mo |
| **Client API costs** | $10-50/mo (Meta API usage, paid by client) |
| **48-hour test period** | Alert-only mode (no auto-actions) |

## Prerequisites

- [Hermes Agent](https://hermes-agent.nousresearch.com) installed and running
- Meta Business Manager account with active ad campaigns
- Facebook App with **Marketing API** product added
- Access Token with `ads_management` permission

## Quick Install

```bash
# Option 1: Clone and run
git clone https://github.com/your-repo/meta-ads-hermes-installer
cd meta-ads-hermes-installer
./install.sh

# Option 2: One-liner (when hosted)
# curl -fsSL https://install.meta-ads.dev | bash
```

## What the Installer Does

```
┌─────────────────────────────────────────────────────┐
│ 1. Checks Hermes is installed                       │
│ 2. Installs Meta Ads skills to ~/.hermes/skills/    │
│ 3. Installs MCP server + adds to config.yaml        │
│ 4. Interactively collects:                          │
│    • Meta App credentials (App ID, Secret, Token)   │
│    • Ad Account ID (act_XXXXXXXXX)                  │
│    • Target ROAS (default: 4.0x)                    │
│    • Max CPA (default: $20)                         │
│    • Delivery channel (Telegram / Discord / Email)  │
│    • Auto mode vs Alert-only mode                   │
│ 5. Saves credentials to ~/.hermes/.env              │
│ 6. Registers cron jobs (15-min check + daily report)│
│ 7. Done. First check in 15 minutes.                 │
└─────────────────────────────────────────────────────┘
```

## Architecture

```
meta-ads-hermes-installer/
├── install.sh                          # Entry point
├── uninstall.sh                        # Clean removal
├── skills/business/meta-ads-agent/
│   ├── SKILL.md                        # Hermes skill definition
│   ├── references/
│   │   └── professional-knowledge.md   # Bidding rules, formulas, strategies
│   ├── scripts/
│   │   └── campaign-check.py           # 15-min automation engine
│   └── config.yaml                     # Client-specific config (created by install)
├── meta-ads-mcp-server/
│   ├── server.py                       # MCP server (JSON-RPC via stdio)
│   └── requirements.txt                # facebook-business SDK
├── cron/
│   ├── jobs-15min.json                 # 15-min campaign check template
│   └── jobs-daily.json                 # Daily report template
└── onboarding/
    ├── config-template.yaml            # Client config template
    └── setup-checklist.md              # Setup checklist
```

## How It Works

### The 5 Automation Rules

| Rule | Trigger | Action |
|------|---------|--------|
| Pause underperformer | CPA > 2× target CPA, spent ≥50% daily budget, ≥5 conversions | Pause ad set |
| Scale winner | ROAS ≥ 1.3× target for 3+ consecutive days | +20% budget (cap +50%/wk) |
| Creative fatigue | Frequency >3.5 AND CTR drop >25% from previous 7 days | Pause ad, flag for rotation |
| Budget pacing | Spend >80% daily budget before 6pm | Monitor alert |
| Learning phase stuck | Campaign in learning limited 7+ days | Simplify targeting |

### Reporting

- **Every 15 minutes:** Campaign health status + any actions taken
- **Daily at 9am:** Full performance report (spend, ROAS, CPA, CTR, changes, recommendations)
- **Instant:** Alerts for CPA breaches, ROAS drops, creative fatigue

### Cron Jobs

```bash
# View active jobs
hermes cron list

# Check output
ls ~/.hermes/cron/output/meta-ads-campaign-check/
```

## Setup Walkthrough

### Step 1: Get Meta API Access

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an App → Add **Marketing API** product
3. Generate a **System User** or **App Token** with `ads_management` permission
4. Note your **Ad Account ID** (Ads Manager → Settings → Account ID — format: `act_123456789`)

### Step 2: Install

```bash
git clone https://github.com/your-repo/meta-ads-hermes-installer
cd meta-ads-hermes-installer
./install.sh
```

### Step 3: 48-Hour Test Period

Run in **alert-only mode** for the first 48 hours. This lets you verify:
- Alerts are accurate (no false positives)
- Delivery channel works (Telegram/Discord/Email)
- ROAS/CPA targets are realistic

### Step 4: Go Live

After the test period, switch to **auto mode**:
```bash
# Edit config
nano ~/.hermes/skills/business/meta-ads-agent/config.yaml
# Set alert_only: false
```

## Commands

```bash
# Check status of active campaigns
hermes chat "Check my Meta Ads campaigns"

# Get latest performance
hermes chat "Show me today's Meta Ads performance"

# View cron jobs
hermes cron list

# Pause a specific ad set
hermes chat "Pause ad set [ID]"

# Adjust targets
hermes chat "Update my target ROAS to 5.0"
```

## Uninstall

```bash
cd meta-ads-hermes-installer
./uninstall.sh
```

Removes:
- Meta Ads Agent skills from `~/.hermes/skills/`
- Cron jobs from `~/.hermes/cron/jobs.json`
- MCP server config from `~/.hermes/config.yaml`
- Credentials from `~/.hermes/.env`

## Development

The MCP server follows the [Model Context Protocol](https://modelcontextprotocol.io) using stdio transport — same pattern as Hermes' Hound MCP server. All tools are exposed as `mcp__meta_ads__<tool_name>()` in Hermes.

### MCP Server Tools

| Tool | Description |
|------|-------------|
| `get_campaigns` | List campaigns with 7-day insights |
| `get_ad_sets` | List ad sets with spend, CPA, ROAS, frequency |
| `get_insights` | Performance data by campaign/ad set/ad |
| `pause_ad_set` | Pause an underperforming ad set |
| `update_budget` | Update campaign daily budget |
| `check_creative_fatigue` | Detect fatigued creatives |
| `get_alerts` | Generate threshold-based alerts |

## License

MIT

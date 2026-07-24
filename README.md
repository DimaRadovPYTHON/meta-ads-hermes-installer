# Meta Ads Agent — Hermes Installer

> **One-command Meta Ads campaign automation for Hermes Agent.**  
> Uses Meta's official MCP Server. No developer app required. Setup in minutes.

## What It Is

The Meta Ads Agent is a complete campaign management system that runs inside [Hermes Agent](https://hermes-agent.nousresearch.com). It connects to your Meta Ads account via Meta's official MCP Server (`mcp.facebook.com/ads`) and automatically:

- **Monitors** every campaign, ad set, and ad every 15 minutes
- **Pauses** underperforming ad sets when CPA exceeds your target (2x threshold)
- **Scales** winning campaigns with budget increases (20% increments, capped 50%/wk)
- **Detects** creative fatigue (frequency >3.5 + CTR drop >25%)
- **Reports** daily performance and instant alerts to Discord / Telegram / Email

## Pricing

| Item | Cost |
|------|------|
| **Setup fee** | $200 one-time |
| **Monthly management** | $50/mo |
| **Client API costs** | $10-50/mo (AI model usage, paid by client) |
| **48-hour test period** | Alert-only mode (no auto-actions) |

## Prerequisites

- [Hermes Agent](https://hermes-agent.nousresearch.com) installed and running
- Meta Business Manager account with active ad campaigns
- A browser for Meta OAuth (first MCP call will prompt login)

## Quick Install

```bash
# Option 1: Clone and run
git clone https://github.com/DimaRadovPYTHON/meta-ads-hermes-installer
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
│ 3. Configures Meta's official MCP (mcp.facebook.com)│
│ 4. Interactively collects:                          │
│    • Ad Account ID (act_XXXXXXXXX)                  │
│    • Target ROAS (default: 4.0x)                    │
│    • Max CPA (default: $20)                         │
│    • Daily budget cap                               │
│    • Delivery channel (Discord / Telegram / Email)  │
│    • Auto mode vs Alert-only mode                   │
│ 5. Saves config to skill directory                  │
│ 6. Registers onboarding flow (20 questions)         │
│ 7. Done. First check runs automatically.            │
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
│   │   └── campaign-check.py           # MCP-based campaign check (standalone)
│   └── config.yaml                     # Client-specific config (created by install)
├── cron/
│   ├── jobs-15min.json                 # 15-min campaign check template
│   └── jobs-daily.json                 # Daily report template
└── onboarding/
    ├── config-template.yaml            # Client config template
    └── setup-checklist.md              # Setup checklist
```

The system connects to Meta Ads through Meta's official MCP Server at `mcp.facebook.com/ads` — no custom infrastructure, no API keys to manage, no developer app required. Authentication is handled via browser-based OAuth.

## How It Works

### Meta's Official MCP Server

Meta released its official MCP Server on April 29, 2026. It's a hosted endpoint at `mcp.facebook.com/ads` that exposes 29 tools across 5 areas: reporting, campaign management, catalog operations, signal diagnostics, and dataset operations. Every campaign, ad set, and ad created through the MCP lands in PAUSED status by default — so there's zero risk of accidental live launches.

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

## Setup Walkthrough

### Step 1: Install Hermes

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup
```

### Step 2: Add Meta MCP

```bash
hermes mcp add meta-ads --url https://mcp.facebook.com/ads
```

The first time you use it, it'll open a browser for Meta OAuth — just log in and grant access.

### Step 3: Run the Installer

```bash
git clone https://github.com/DimaRadovPYTHON/meta-ads-hermes-installer
cd meta-ads-hermes-installer
./install.sh
```

You'll need your client access code and Meta Ad Account ID (find it in Ads Manager → Settings — format: `act_123456789`).

### Step 4: 48-Hour Test Period

Run in **alert-only mode** for the first 48 hours. This lets you verify:
- Alerts are accurate (no false positives)
- Delivery channel works (Discord/Telegram/Email)
- ROAS/CPA targets are realistic

### Step 5: Go Live

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

## License

MIT

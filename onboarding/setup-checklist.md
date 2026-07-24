# Meta Ads Agent — Setup Checklist

## Prerequisites
- [ ] Hermes Agent installed and running
- [ ] Meta Business Manager account with active ad campaigns
- [ ] Browser available for Meta OAuth authentication

## Step 1: Configure Meta MCP
- [ ] Add Meta's official MCP: `hermes mcp add meta-ads --url https://mcp.facebook.com/ads`
- [ ] Authenticate via browser when prompted (Meta OAuth login)
- [ ] Verify connection: ask the agent to list your campaigns

## Step 2: Install Meta Ads Agent
- [ ] Run: `git clone https://github.com/DimaRadovPYTHON/meta-ads-hermes-installer`
- [ ] Run: `cd meta-ads-hermes-installer && ./install.sh`
- [ ] Enter your client access code
- [ ] Follow the interactive onboarding prompts:
  - [ ] Enter Ad Account ID (format: `act_XXXXXXXXX`)
  - [ ] Set Target ROAS (default: 4.0x)
  - [ ] Set Max CPA (default: $20)
  - [ ] Set daily budget cap
  - [ ] Choose delivery channel (Discord/Telegram/Email)
  - [ ] Choose alert-only or auto mode

## Step 3: Verify Installation
- [ ] Skills installed: `~/.hermes/skills/business/meta-ads-agent/SKILL.md`
- [ ] Meta MCP configured: check `~/.hermes/config.yaml` for meta-ads entry
- [ ] Client config saved: `~/.hermes/skills/business/meta-ads-agent/config.yaml`
- [ ] Onboarding flow registered (starts in ~1 minute)

## Step 4: Onboarding Questions
- [ ] Agent will ask ~20 questions about your business (one at a time)
- [ ] Be ready with: business details, ideal customer profile, ad budget, competitor info

## Step 5: 48-Hour Test Period
- [ ] First campaign check runs within 15 minutes
- [ ] Verify no false positives (alerts on good campaigns)
- [ ] Review daily report delivery
- [ ] Confirm alert thresholds are appropriate
- [ ] Adjust ROAS/CPA targets if needed

## Step 6: Go Live
- [ ] Switch from alert-only to auto mode (if desired)
- [ ] Set up client billing ($200 setup fee)
- [ ] Configure client's API cost payment ($10-50/mo)
- [ ] Provide client with delivery channel access

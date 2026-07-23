# Meta Ads Agent — Setup Checklist

## Prerequisites
- [ ] Hermes Agent installed and running
- [ ] Meta Business Manager account
- [ ] Facebook App created with Marketing API access
- [ ] Active ad campaigns running in Meta Ads Manager

## Step 1: Meta API Access
- [ ] Go to https://developers.facebook.com/
- [ ] Create a new App (or use existing) with "Marketing API" product
- [ ] Generate a System User or App Token with `ads_management` permission
- [ ] Note your Ad Account ID (format: `act_XXXXXXXXX`)
- [ ] Test token with a simple curl call

## Step 2: Install Meta Ads Agent
- [ ] Run: `git clone https://github.com/your-repo/meta-ads-hermes-installer`
- [ ] Run: `cd meta-ads-hermes-installer && ./install.sh`
- [ ] Follow the interactive onboarding prompts:
  - [ ] Enter Meta App credentials
  - [ ] Enter Ad Account ID
  - [ ] Set Target ROAS (default: 4.0x)
  - [ ] Set Max CPA (default: $20)
  - [ ] Choose delivery channel (Telegram/Discord/Email)
  - [ ] Choose alert-only or auto mode

## Step 3: Verify Installation
- [ ] Skills installed: `~/.hermes/skills/business/meta-ads-agent/SKILL.md`
- [ ] MCP server configured in `~/.hermes/config.yaml`
- [ ] Cron jobs registered (check `~/.hermes/cron/jobs.json`)
- [ ] Credentials saved to `~/.hermes/.env`

## Step 4: 48-Hour Test Period
- [ ] First campaign check runs within 15 minutes
- [ ] Verify no false positives (auto-pause of good campaigns)
- [ ] Review daily report delivery
- [ ] Confirm alert thresholds are appropriate
- [ ] Adjust ROAS/CPA targets if needed

## Step 5: Go Live
- [ ] Switch from alert-only to auto mode (if desired)
- [ ] Set up client billing ($200 setup fee)
- [ ] Configure client's API cost payment ($10-50/mo)
- [ ] Provide client with delivery channel access

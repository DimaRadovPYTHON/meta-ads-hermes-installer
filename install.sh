#!/bin/bash
set -euo pipefail

# Meta Ads Agent — Hermes Installer
# One-command setup for deploying the Meta Ads Agent into Hermes
# Uses Meta's official MCP Server (mcp.facebook.com/ads)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}  Meta Ads Agent — Hermes Installer${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""

# ── Client Validation ──────────────────────────────────────────────────────

echo -e "${YELLOW}[1/6] Validating client access...${NC}"

CLIENTS_FILE="$SCRIPT_DIR/clients.json"
if [ ! -f "$CLIENTS_FILE" ]; then
    echo -e "  ${RED}✗${NC} License file not found. Contact your provider for a valid installer."
    exit 1
fi

VALID_CODE=""
CLIENT_NAME=""

while [ -z "$VALID_CODE" ]; do
    read -rp "  Enter your client access code: " CLIENT_CODE
    CLIENT_CODE=${CLIENT_CODE:-}

    if [ -z "$CLIENT_CODE" ]; then
        echo -e "  ${RED}Access code cannot be empty${NC}"
        continue
    fi

    CLIENT_NAME=$(python3 -c "
import json, sys
with open('$CLIENTS_FILE') as f:
    clients = json.load(f)
if '$CLIENT_CODE' in clients:
    print(clients['$CLIENT_CODE'])
else:
    print('INVALID')
" 2>/dev/null)

    if [ "$CLIENT_NAME" = "INVALID" ] || [ -z "$CLIENT_NAME" ]; then
        echo -e "  ${RED}✗${NC} Invalid access code. This installer is licensed per client."
        echo "    Contact your provider to get a valid code."
        echo ""
    else
        VALID_CODE="$CLIENT_CODE"
        echo -e "  ${GREEN}✓${NC} Access granted — $CLIENT_NAME"
        echo ""
    fi
done

# ── Prerequisites ──────────────────────────────────────────────────────────

echo -e "${YELLOW}[2/6] Checking prerequisites...${NC}"

if command -v hermes &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Hermes found: $(which hermes)"
else
    echo -e "  ${RED}✗${NC} Hermes not found. Please install Hermes first:"
    echo "    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
    exit 1
fi

if [ -d "$HOME/.hermes" ]; then
    echo -e "  ${GREEN}✓${NC} Hermes config found: ~/.hermes/"
else
    echo -e "  ${RED}✗${NC} ~/.hermes/ not found. Run 'hermes setup' first."
    exit 1
fi

echo ""

# ── Install Skills ─────────────────────────────────────────────────────────

echo -e "${YELLOW}[3/6] Installing skills...${NC}"

SKILL_DIR="$HOME/.hermes/skills/business/meta-ads-agent"
if [ -d "$SKILL_DIR" ]; then
    echo -e "  ${YELLOW}⚠${NC} Skill directory already exists at $SKILL_DIR"
    read -rp "  Overwrite? (y/N): " overwrite
    if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
        echo "  Skipping skill installation."
    else
        mkdir -p "$HOME/.hermes/skills/business"
        cp -r "$SCRIPT_DIR/skills/business/meta-ads-agent" "$HOME/.hermes/skills/business/"
        echo -e "  ${GREEN}✓${NC} Skills overwritten"
    fi
else
    mkdir -p "$HOME/.hermes/skills/business"
    cp -r "$SCRIPT_DIR/skills/business/meta-ads-agent" "$HOME/.hermes/skills/business/"
    echo -e "  ${GREEN}✓${NC} Skills installed to $SKILL_DIR"
fi

chmod +x "$SKILL_DIR/scripts/"*.py 2>/dev/null || true
echo ""

# ── Configure Meta MCP Server ──────────────────────────────────────────────

echo -e "${YELLOW}[4/6] Configuring Meta Ads MCP Server...${NC}"
echo -e "  Using Meta's official MCP: mcp.facebook.com/ads"
echo -e "  ${YELLOW}⚠${NC} You'll need to authenticate via browser when first used."
echo ""

# Add Meta MCP via Hermes MCP management
hermes mcp add meta-ads --url "https://mcp.facebook.com/ads" 2>/dev/null || {
    # Fallback: manual config.yaml entry
    CONFIG_FILE="$HOME/.hermes/config.yaml"
    MCP_ENTRY="
  meta-ads:
    url: https://mcp.facebook.com/ads
    enabled: true"

    if grep -q "meta-ads:" "$CONFIG_FILE" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} MCP config for meta-ads already exists in config.yaml"
    else
        python3 -c "
with open('$CONFIG_FILE') as f:
    content = f.read()
if 'mcp_servers:' in content:
    lines = content.split('\n')
    result = []
    added = False
    in_mcp = False
    indent = ''
    for i, line in enumerate(lines):
        result.append(line)
        if line.strip().startswith('mcp_servers:'):
            in_mcp = True
            indent = line[:len(line) - len(line.lstrip())]
        elif in_mcp and line.strip() and not line.startswith(' ') and not line.startswith('#'):
            if not added:
                result.append(indent + '  meta-ads:')
                result.append(indent + '    url: https://mcp.facebook.com/ads')
                result.append(indent + '    enabled: true')
                added = True
            in_mcp = False
    if in_mcp and not added:
        result.append(indent + '  meta-ads:')
        result.append(indent + '    url: https://mcp.facebook.com/ads')
        result.append(indent + '    enabled: true')
    content = '\n'.join(result)
    with open('$CONFIG_FILE', 'w') as f:
        f.write(content)
    print('MCP config added')
" || echo -e "  ${YELLOW}⚠${NC} Could not auto-edit config.yaml. Add manually:"
        echo "    Under mcp_servers: in ~/.hermes/config.yaml:"
        echo "      meta-ads:"
        echo "        url: https://mcp.facebook.com/ads"
        echo "        enabled: true"
    fi
}

echo -e "  ${GREEN}✓${NC} Meta Ads MCP configured"
echo ""

# ── Interactive Onboarding ─────────────────────────────────────────────────

echo -e "${YELLOW}[5/6] Client onboarding...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  Let's configure your Meta Ads Agent."
echo "  You'll need: Your Meta Ad Account ID"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ad Account ID
while true; do
    read -rp "  Ad Account ID (e.g., act_123456789): " META_ACCOUNT_ID
    if [ -n "$META_ACCOUNT_ID" ]; then
        if [[ "$META_ACCOUNT_ID" != act_* ]]; then
            META_ACCOUNT_ID="act_$META_ACCOUNT_ID"
        fi
        break
    fi
    echo -e "  ${RED}Account ID cannot be empty${NC}"
done

# Target ROAS
read -rp "  Target ROAS (default: 4.0): " TARGET_ROAS
TARGET_ROAS=${TARGET_ROAS:-4.0}

# Max CPA
read -rp "  Max CPA in \$ (default: 20): " MAX_CPA
MAX_CPA=${MAX_CPA:-20}

# Daily budget cap
read -rp "  Daily budget cap in \$ (default: 100): " DAILY_BUDGET_CAP
DAILY_BUDGET_CAP=${DAILY_BUDGET_CAP:-100}

# Delivery channel
echo ""
echo "  Delivery channel for reports:"
echo "    1) Discord"
echo "    2) Telegram"
echo "    3) Email"
read -rp "  Choice [1-3] (default: 1): " CHANNEL_CHOICE
case ${CHANNEL_CHOICE:-1} in
    1) DELIVERY_CHANNEL="discord" ;;
    2) DELIVERY_CHANNEL="telegram" ;;
    3) DELIVERY_CHANNEL="email" ;;
    *) DELIVERY_CHANNEL="discord" ;;
esac
echo -e "  ${GREEN}✓${NC} Delivery channel: $DELIVERY_CHANNEL"

# Delivery target
read -rp "  Delivery target (Discord channel ID / Telegram chat ID / email): " DELIVERY_TARGET
DELIVERY_TARGET=${DELIVERY_TARGET:-"origin"}

# Mode
echo ""
echo "  Operating mode:"
echo "    1) Alert-only mode — sends alerts, requires manual action (recommended for first 48hrs)"
echo "    2) Auto mode — pauses underperformers, scales winners automatically"
read -rp "  Choice [1-2] (default: 1): " MODE_CHOICE
case ${MODE_CHOICE:-1} in
    1) ALERT_ONLY="true" ;;
    2) ALERT_ONLY="false" ;;
    *) ALERT_ONLY="true" ;;
esac
echo -e "  ${GREEN}✓${NC} Mode: $([[ $ALERT_ONLY == "true" ]] && echo "alerts only" || echo "auto")"

# ── Save Configuration ─────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[6/6] Saving configuration...${NC}"

CONFIG_FILE_SKILL="$SKILL_DIR/config.yaml"
cat > "$CONFIG_FILE_SKILL" << EOF
# Meta Ads Agent — Client Config
client:
  name: "$CLIENT_NAME"
  ad_account_id: "$META_ACCOUNT_ID"
  target_roas: $TARGET_ROAS
  max_cpa: $MAX_CPA
  daily_budget_cap: $DAILY_BUDGET_CAP
  alert_only: $ALERT_ONLY
  delivery_channel: "$DELIVERY_CHANNEL"
  delivery_target: "$DELIVERY_TARGET"

rules:
  pause_threshold: 2.0
  scale_threshold: 1.3
  scale_days: 3
  scale_increment: 0.2
  max_weekly_increase: 0.5
  fatigue_frequency: 3.5
  fatigue_ctr_drop: 0.25

reporting:
  daily_report_time: "09:00"
  timezone: "America/New_York"
  currency: "USD"
EOF
echo -e "  ${GREEN}✓${NC} Client config saved to $CONFIG_FILE_SKILL"

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  ✅ Meta Ads Agent installed!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "  What's next:"
echo "  1. Authenticate Meta MCP when prompted — the first time you"
echo "     ask the agent to check campaigns, it will open a browser"
echo "     for Meta OAuth login."
echo "  2. The agent will start with a 48-hour alert-only period."
echo "  3. Test the connection:"
echo "     'Use the Meta Ads MCP to list my campaigns'"
echo "  4. To set up the 15-minute check schedule:"
echo "     'Set up a 15-min campaign check for my ads'"
echo ""
echo -e "${YELLOW}  Config file:${NC} $SKILL_DIR/config.yaml"
echo -e "${YELLOW}  Uninstall:${NC}   $SCRIPT_DIR/uninstall.sh"
echo ""

# ── Post-Install: Register onboarding job ─────────────────────────────────
echo -e "${YELLOW}  Registering onboarding flow...${NC}"

ONBOARDING_ID=$(python3 -c "import uuid; print(uuid.uuid4().hex[:12])")
ONBOARDING_DIR="$HOME/.hermes/cron"
mkdir -p "$ONBOARDING_DIR"

python3 -c "
import json, uuid
from datetime import datetime, timezone, timedelta

try:
    with open('$ONBOARDING_DIR/jobs.json') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    data = {'jobs': []}

onboarding_job = {
    'id': '$ONBOARDING_ID',
    'name': 'Meta Ads Onboarding — $CLIENT_NAME',
    'prompt': '''You are the Meta Ads Agent onboarding assistant. Your job is to ask the client 20 questions to understand their business before running ads. Ask them ONE question at a time and wait for their response before moving to the next.

The 20 questions:

1. What's your business name and what do you do?
2. What product or service are you advertising?
3. Who is your ideal customer? (age, gender, interests)
4. What's the main problem your product solves for them?
5. How much does your product/service cost?
6. What's your profit margin per sale?
7. Do you have an existing website or landing page for conversions?
8. What's your current monthly ad budget?
9. Have you run Meta/Facebook ads before? If so, what results did you see?
10. What's your target cost per acquisition (CPA) — how much are you willing to pay for a customer?
11. Do you have existing video content or photos of your product?
12. Who are your top 3 competitors on social media?
13. What makes your business different from competitors?
14. What call-to-action do you want people to take? (Buy, Sign up, Book, etc.)
15. What geographic area do you serve?
16. Do you have a Facebook Pixel installed on your website?
17. What time of year is busiest for your business?
18. What would a successful month look like for your ads?
19. Do you have any existing ad creative (videos, images, copy) we should review?
20. Is there anything specific about your business or industry that's important for running ads?

Important: Ask ONE question at a time. Wait for the client's answer before asking the next one. Keep the conversation natural.''',
    'skills': ['meta-ads-agent'],
    'model': None,
    'provider': None,
    'script': None,
    'no_agent': False,
    'context_from': None,
    'schedule': {
        'kind': 'oneshot',
        'at': (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    },
    'schedule_display': '1 minute after install',
    'repeat': {'times': 1, 'completed': 0},
    'enabled': True,
    'state': 'scheduled',
    'created_at': datetime.now(timezone.utc).isoformat(),
    'next_run_at': (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat(),
    'deliver': '$DELIVERY_TARGET'
}

data['jobs'].append(onboarding_job)

with open('$ONBOARDING_DIR/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Onboarding job registered')
"
echo -e "  ${GREEN}✓${NC} Onboarding flow will start in 1 minute on $DELIVERY_CHANNEL"
echo ""

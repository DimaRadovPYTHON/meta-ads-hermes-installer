#!/bin/bash
set -euo pipefail

# Meta Ads Agent — Hermes Installer
# One-command setup for deploying the Meta Ads Agent into Hermes

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

    # Validate against clients.json
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

# Check Hermes binary
if command -v hermes &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Hermes found: $(which hermes)"
else
    echo -e "  ${RED}✗${NC} Hermes not found. Please install Hermes first:"
    echo "    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
    exit 1
fi

# Check Hermes config directory
if [ -d "$HOME/.hermes" ]; then
    echo -e "  ${GREEN}✓${NC} Hermes config found: ~/.hermes/"
else
    echo -e "  ${RED}✗${NC} ~/.hermes/ not found. Run Hermes setup first."
    exit 1
fi

# Check Python3
if command -v python3 &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Python3 found: $(python3 --version)"
else
    echo -e "  ${RED}✗${NC} Python3 not found. Please install Python 3.11+."
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
        cp -r "$SCRIPT_DIR/skills/business/meta-ads-agent" "$HOME/.hermes/skills/business/"
        echo -e "  ${GREEN}✓${NC} Skills overwritten"
    fi
else
    mkdir -p "$HOME/.hermes/skills/business"
    cp -r "$SCRIPT_DIR/skills/business/meta-ads-agent" "$HOME/.hermes/skills/business/"
    echo -e "  ${GREEN}✓${NC} Skills installed to $SKILL_DIR"
fi

# Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.py 2>/dev/null || true
echo ""

# ── Install MCP Server ─────────────────────────────────────────────────────

echo -e "${YELLOW}[4/6] Installing Meta Ads MCP server...${NC}"

MCP_DIR="$SCRIPT_DIR/meta-ads-mcp-server"
MCP_TARGET="$HOME/.hermes/meta-ads-mcp-server"

# Install python dependencies
echo -e "  Installing Python dependencies..."
pip3 install -r "$MCP_DIR/requirements.txt" 2>/dev/null || pip install -r "$MCP_DIR/requirements.txt" 2>/dev/null || {
    echo -e "  ${YELLOW}⚠${NC} Could not auto-install facebook-business SDK"
    echo "    Install manually: pip3 install facebook-business>=19.0.0"
}

# Copy server files
mkdir -p "$MCP_TARGET"
cp "$MCP_DIR/server.py" "$MCP_TARGET/"
cp "$MCP_DIR/requirements.txt" "$MCP_TARGET/"
echo -e "  ${GREEN}✓${NC} MCP server files copied to $MCP_TARGET"

# Add MCP config to Hermes config.yaml
CONFIG_FILE="$HOME/.hermes/config.yaml"
MCP_CONFIG="
  meta-ads:
    command: python3 $MCP_TARGET/server.py
    enabled: true"

if grep -q "meta-ads:" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} MCP config for meta-ads already exists in config.yaml"
else
    # Insert before the last mcp_servers entry or at end of mcp_servers section
    python3 -c "
import re
with open('$CONFIG_FILE') as f:
    content = f.read()
# Find mcp_servers section and add after it
if 'mcp_servers:' in content:
    # Add our server after the last existing MCP server
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
            # End of mcp_servers section reached
            if not added:
                result.append(indent + '  meta-ads:')
                result.append(indent + '    command: python3 $MCP_TARGET/server.py')
                result.append(indent + '    enabled: true')
                added = True
            in_mcp = False
    if in_mcp and not added:
        # mcp_servers was the last section
        result.append(indent + '  meta-ads:')
        result.append(indent + '    command: python3 $MCP_TARGET/server.py')
        result.append(indent + '    enabled: true')
    content = '\n'.join(result)
    with open('$CONFIG_FILE', 'w') as f:
        f.write(content)
    print('MCP config added')
" || echo -e "  ${YELLOW}⚠${NC} Could not auto-edit config.yaml. Add manually:"
    echo "    Add to ~/.hermes/config.yaml under mcp_servers:"
    echo "      meta-ads:"
    echo "        command: python3 $MCP_TARGET/server.py"
    echo "        enabled: true"
fi
echo ""

# ── Interactive Onboarding ─────────────────────────────────────────────────

echo -e "${YELLOW}[5/6] Client onboarding...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  Let's configure your Meta Ads Agent."
echo "  You'll need: Meta App credentials + Ad Account ID"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Meta App ID
while true; do
    read -rp "  Meta App ID: " META_APP_ID
    if [ -n "$META_APP_ID" ]; then
        break
    fi
    echo -e "  ${RED}App ID cannot be empty${NC}"
done

# Meta App Secret
while true; do
    read -rsp "  Meta App Secret (hidden): " META_APP_SECRET
    echo ""
    if [ -n "$META_APP_SECRET" ]; then
        break
    fi
    echo -e "  ${RED}App Secret cannot be empty${NC}"
done

# Access Token
while true; do
    read -rsp "  Meta Access Token (hidden): " META_ADS_TOKEN
    echo ""
    if [ -n "$META_ADS_TOKEN" ]; then
        break
    fi
    echo -e "  ${RED}Token cannot be empty${NC}"
done

# Ad Account ID
while true; do
    read -rp "  Ad Account ID (e.g., act_123456789): " META_ACCOUNT_ID
    if [ -n "$META_ACCOUNT_ID" ]; then
        # Normalize: add act_ prefix if missing
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

# Delivery channel
echo ""
echo "  Delivery channel for reports:"
echo "    1) Telegram"
echo "    2) Discord"
echo "    3) Email"
read -rp "  Choice [1-3] (default: 1): " CHANNEL_CHOICE
case ${CHANNEL_CHOICE:-1} in
    1) DELIVERY_CHANNEL="telegram" ;;
    2) DELIVERY_CHANNEL="discord" ;;
    3) DELIVERY_CHANNEL="email" ;;
    *) DELIVERY_CHANNEL="telegram" ;;
esac
echo -e "  ${GREEN}✓${NC} Delivery channel: $DELIVERY_CHANNEL"

# Delivery target
read -rp "  Delivery target (chat ID / email / phone): " DELIVERY_TARGET
DELIVERY_TARGET=${DELIVERY_TARGET:-"origin"}

# Mode
echo ""
echo "  Operating mode:"
echo "    1) Auto mode — pauses underperformers, scales winners automatically"
echo "    2) Alert-only mode — sends alerts, requires manual action"
read -rp "  Choice [1-2] (default: 1): " MODE_CHOICE
case ${MODE_CHOICE:-1} in
    1) ALERT_ONLY="false" ;;
    2) ALERT_ONLY="true" ;;
    *) ALERT_ONLY="false" ;;
esac
echo -e "  ${GREEN}✓${NC} Auto mode: $([[ $ALERT_ONLY == "false" ]] && echo "enabled" || echo "alerts only")"

# Webhook URL
echo ""
echo "  Webhook URL for alerts and reports:"
echo "    (Discord webhook, Slack webhook, or any HTTP endpoint)"
echo "    Leave empty to skip — the agent can set it up later."
read -rp "  Webhook URL: " WEBHOOK_URL
if [ -n "$WEBHOOK_URL" ]; then
    echo -e "  ${GREEN}✓${NC} Webhook registered"
else
    echo -e "  ${YELLOW}⚠${NC} No webhook set — alerts will go through the agent's chat"
fi

# ── Save Credentials ───────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[6/6] Saving configuration...${NC}"

# Append to .env
ENV_FILE="$HOME/.hermes/.env"
{
    echo ""
    echo "# Meta Ads Agent credentials (added $(date))"
    echo "META_ADS_APP_ID=$META_APP_ID"
    echo "META_ADS_APP_SECRET=$META_APP_SECRET"
    echo "META_ADS_TOKEN=$META_ADS_TOKEN"
    echo "META_ADS_ACCOUNT_ID=$META_ACCOUNT_ID"
} >> "$ENV_FILE"
echo -e "  ${GREEN}✓${NC} Credentials saved to $ENV_FILE"

# Save config
CONFIG_FILE_SKILL="$SKILL_DIR/config.yaml"
cat > "$CONFIG_FILE_SKILL" << EOF
# Meta Ads Agent — Client Config
client:
  name: "$META_ACCOUNT_ID"
  ad_account_id: "$META_ACCOUNT_ID"
  target_roas: $TARGET_ROAS
  max_cpa: $MAX_CPA
  alert_only: $ALERT_ONLY
  delivery_channel: "$DELIVERY_CHANNEL"
  delivery_target: "$DELIVERY_TARGET"
  webhook_url: "$WEBHOOK_URL"

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
echo -e "  ${GREEN}✓${NC} Client config saved"

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  ✅ Meta Ads Agent installed!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "  What's next:"
echo "  1. The MCP server is ready — Hermes can now call Meta Ads tools"
echo "  2. Ask the agent to set up a campaign check schedule:"
echo "     'Set up a 15-min campaign check for my ads'"
echo "  3. Test the connection:"
echo "     'Use the Meta Ads MCP server to list my campaigns'"
echo "  4. To send alerts, the agent can use the send_webhook tool"
echo "  5. 48-hour test period recommended before trusting auto-mode"
echo ""
echo -e "${YELLOW}  Config file:${NC} $SKILL_DIR/config.yaml"
echo -e "${YELLOW}  Credentials:${NC} $ENV_FILE"
echo -e "${YELLOW}  Uninstall:${NC}   $SCRIPT_DIR/uninstall.sh"
echo ""

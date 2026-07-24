#!/bin/bash
set -euo pipefail

# Meta Ads Agent — Uninstaller
# Removes all installed files and configurations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Meta Ads Agent Uninstaller${NC}"
echo "This will remove the Meta Ads Agent from your Hermes installation."
echo ""

# Confirm
read -rp "Are you sure? This cannot be undone. (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Removing skills...${NC}"
SKILL_DIR="$HOME/.hermes/skills/business/meta-ads-agent"
if [ -d "$SKILL_DIR" ]; then
    rm -rf "$SKILL_DIR"
    echo -e "${GREEN}✓ Removed $SKILL_DIR${NC}"
else
    echo "  Skill directory not found — skipping"
fi

echo ""
echo -e "${YELLOW}Removing cron jobs from jobs.json...${NC}"
CRON_FILE="$HOME/.hermes/cron/jobs.json"
if [ -f "$CRON_FILE" ]; then
    # Use python to safely remove jobs by id prefix
    python3 -c "
import json
with open('$CRON_FILE') as f:
    data = json.load(f)
original_count = len(data.get('jobs', []))
data['jobs'] = [j for j in data.get('jobs', []) if not j.get('id', '').startswith('meta-ads')]
removed = original_count - len(data['jobs'])
with open('$CRON_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print(f'Removed {removed} cron jobs')
" && echo -e "${GREEN}✓ Cron jobs cleaned${NC}" || echo -e "${RED}✗ Failed to clean cron jobs${NC}"
else
    echo "  Cron file not found — skipping"
fi

echo ""
echo -e "${YELLOW}Removing MCP server config from config.yaml...${NC}"
CONFIG_FILE="$HOME/.hermes/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    python3 -c "
import re
with open('$CONFIG_FILE') as f:
    content = f.read()
# Remove the meta-ads MCP server section (custom or official MCP format)
content = re.sub(r'\\n  meta-ads:.*?(?:enabled: true|enabled: false)', '', content)
with open('$CONFIG_FILE', 'w') as f:
    f.write(content)
print('MCP config removed')
" && echo -e "${GREEN}✓ MCP config cleaned${NC}" || echo -e "${RED}✗ Failed to clean MCP config${NC}"
else
    echo "  Config file not found — skipping"
fi

echo ""
echo -e "${YELLOW}Removing credentials from .env...${NC}"
ENV_FILE="$HOME/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
    python3 -c "
with open('$ENV_FILE') as f:
    lines = f.readlines()
lines = [l for l in lines if not l.startswith('META_ADS_')]
with open('$ENV_FILE', 'w') as f:
    f.writelines(lines)
print('Credentials removed')
" && echo -e "${GREEN}✓ Credentials cleaned${NC}" || echo -e "${RED}✗ Failed to clean credentials${NC}"
else
    echo "  .env file not found — skipping"
fi

echo ""
echo -e "${GREEN}✓ Meta Ads Agent uninstalled successfully${NC}"
echo '  Note: Remove MCP config with: hermes mcp remove meta-ads'

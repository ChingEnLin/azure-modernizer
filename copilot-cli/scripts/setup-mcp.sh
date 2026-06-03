#!/bin/bash
# setup-mcp.sh — Idempotent MCP configuration for azure-modernizer plugin
#
# This script adds the Azure MCP server to ~/.copilot/mcp-config.json.
# It is idempotent: safe to run multiple times.
#
# Usage:
#   bash setup-mcp.sh

set -e

CONFIG_FILE="$HOME/.copilot/mcp-config.json"
AZURE_MCP_ENTRY='{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@azure-mcp/server@latest"]
}'

echo "=== Azure Modernizer MCP Setup ==="
echo ""

# Check jq availability
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed."
    echo "   Install it with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi

echo "✓ jq available"

# Create config directory if missing
if [ ! -d "$HOME/.copilot" ]; then
    echo "Creating ~/.copilot directory..."
    mkdir -p "$HOME/.copilot"
fi

# Create config file if missing
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating $CONFIG_FILE..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "mcpServers": {}
}
EOF
fi

echo "✓ Config file ready: $CONFIG_FILE"

# Check if azure MCP already exists
if jq -e '.mcpServers.azure' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "✓ Azure MCP already configured. Skipping."
else
    echo "Adding Azure MCP server..."
    jq ".mcpServers.azure = $(echo "$AZURE_MCP_ENTRY" | jq -c .)" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    echo "✓ Azure MCP added to config"
fi

echo ""
echo "=== Verification ==="
echo "1. Authenticate to Azure:"
echo "   az login"
echo ""
echo "2. Test the plugin:"
echo "   copilot --agent azure-modernizer:azure-modernizer --allow-all-tools \\
     -p 'Inventory my Azure networking'"
echo ""
echo "Done!"

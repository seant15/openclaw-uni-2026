#!/usr/bin/env bash
# Set gateway token everywhere (default: simple placeholder uni-random-token).
# Same value must be in Coolify OPENCLAW_GATEWAY_TOKEN and Paperclip x-openclaw-token.
set -euo pipefail

CONFIG="${OPENCLAW_CONFIG:-/opt/openclaw/data/.openclaw/openclaw.json}"
COOLIFY_JSON="${COOLIFY_JSON:-/data/coolify/applications/ug0g8cs4kkw0040cwsswk40c/openclaw.json}"
CONTAINER="${OPENCLAW_CONTAINER:-openclaw-ug0g8cs4kkw0040cwsswk40c}"

NEW_TOKEN="${1:-uni-random-token}"

echo "Setting gateway token to: $NEW_TOKEN"
echo

jq --arg t "$NEW_TOKEN" '
  .gateway.auth.mode = "token" |
  .gateway.auth.token = $t
' "$CONFIG" > /tmp/openclaw-token-fix.json
mv /tmp/openclaw-token-fix.json "$CONFIG"
echo "Updated: $CONFIG"

if [[ -f "$COOLIFY_JSON" ]]; then
  jq --arg t "$NEW_TOKEN" '
    .gateway.auth.mode = "token" |
    .gateway.auth.token = $t
  ' "$COOLIFY_JSON" > /tmp/coolify-openclaw-fix.json
  mv /tmp/coolify-openclaw-fix.json "$COOLIFY_JSON"
  echo "Updated: $COOLIFY_JSON"
fi

echo
echo "=== Do this in Coolify UI (required for next redeploy) ==="
echo "OPENCLAW_GATEWAY_TOKEN=$NEW_TOKEN"
echo "Save → Redeploy (or: docker restart $CONTAINER)"
echo
echo "=== Then re-run Paperclip join ==="
echo "/tmp/pc.sh"

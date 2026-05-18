#!/usr/bin/env bash
# Run on OpenClaw VPS (has /opt/openclaw/data). One script for Paperclip openclaw_gateway join.
set -euo pipefail

INVITE_ID="${INVITE_ID:-pcp_invite_arhwikcy}"
AGENT_NAME="${AGENT_NAME:-kimi}"
GATEWAY_WSS="${GATEWAY_WSS:-wss://open.uni-agency.com}"
GATEWAY_HTTPS="${GATEWAY_HTTPS:-https://open.uni-agency.com}"
PAPERCLIP_BASE="${PAPERCLIP_BASE:-https://paperclip.uni-agency.com}"
CONFIG="${OPENCLAW_CONFIG:-/opt/openclaw/data/.openclaw/openclaw.json}"

echo "== Paperclip onboard helper =="
echo "Invite: $INVITE_ID | Agent: $AGENT_NAME"
echo

if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: Config not found: $CONFIG"
  exit 1
fi

TOKEN="$(jq -r '.gateway.auth.token // empty' "$CONFIG")"
if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "ERROR: No gateway.auth.token in $CONFIG"
  exit 1
fi
if [[ "$TOKEN" == "uni-random-token" ]]; then
  echo "ERROR: Token is still placeholder uni-random-token — set OPENCLAW_GATEWAY_TOKEN in Coolify and redeploy."
  exit 1
fi
if [[ ${#TOKEN} -lt 16 ]]; then
  echo "ERROR: Token looks too short (${#TOKEN} chars)."
  exit 1
fi
# conn UUIDs from gateway logs are 36 chars — real tokens are usually longer
if [[ ${#TOKEN} -eq 36 && "$TOKEN" =~ ^[0-9a-f]{8}-[0-9a-f]{4}- ]]; then
  echo "WARN: Token looks like a connection UUID, not gateway.auth.token. Check Coolify OPENCLAW_GATEWAY_TOKEN."
fi

echo "Token: OK (${#TOKEN} chars, not printed)"
echo

echo "== 1) test-resolution (HTTPS only, not wss) =="
RES="$(curl -sS -G \
  "${PAPERCLIP_BASE}/api/invites/${INVITE_ID}/test-resolution" \
  --data-urlencode "url=${GATEWAY_HTTPS}")"
echo "$RES" | jq . 2>/dev/null || echo "$RES"
echo

echo "== 2) POST join accept =="
BODY="$(jq -n \
  --arg token "$TOKEN" \
  --arg name "$AGENT_NAME" \
  --arg wss "$GATEWAY_WSS" \
  --arg pc "$PAPERCLIP_BASE" \
  '{
    requestType: "agent",
    agentName: $name,
    adapterType: "openclaw_gateway",
    capabilities: "UNI OpenClaw gateway agent",
    agentDefaultsPayload: {
      url: $wss,
      paperclipApiUrl: $pc,
      headers: {"x-openclaw-token": $token},
      waitTimeoutMs: 120000,
      sessionKeyStrategy: "issue",
      role: "operator",
      scopes: ["operator.admin"]
    }
  }')"

ACCEPT="$(curl -sS -X POST \
  "${PAPERCLIP_BASE}/api/invites/${INVITE_ID}/accept" \
  -H 'Content-Type: application/json' \
  -d "$BODY")"
echo "$ACCEPT" | jq . 2>/dev/null || echo "$ACCEPT"

REQUEST_ID="$(echo "$ACCEPT" | jq -r '.id // empty')"
CLAIM_SECRET="$(echo "$ACCEPT" | jq -r '.claimSecret // empty')"
CLAIM_PATH="$(echo "$ACCEPT" | jq -r '.claimApiKeyPath // empty')"

echo
echo "== YOU do these in Paperclip UI (I cannot click for you) =="
echo "1. Board → Approve join request for agent: $AGENT_NAME"
if [[ -n "$REQUEST_ID" && -n "$CLAIM_SECRET" ]]; then
  echo "2. After approval, claim API key:"
  echo "   curl -sS -X POST '${PAPERCLIP_BASE}${CLAIM_PATH}' \\"
  echo "     -H 'Content-Type: application/json' \\"
  echo "     -d '{\"claimSecret\":\"<from UI or saved output>\"}'"
  echo "   (claimSecret was in JSON above — save it once, do not share)"
fi
echo
echo "== If runs still fail with protocol mismatch =="
echo "   Upgrade Paperclip @paperclipai/adapter-openclaw-gateway on Paperclip VPS,"
echo "   OR set OPENCLAW_IMAGE_TAG=2026.5.10 in Coolify and redeploy."
echo
echo "== Watch gateway while Paperclip runs =="
echo "   docker logs -f openclaw-ug0g8cs4kkw0040cwsswk40c 2>&1 | grep -iE 'paperclip|protocol'"

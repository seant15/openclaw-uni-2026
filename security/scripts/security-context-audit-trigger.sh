#!/bin/bash
# security-context-audit-trigger.sh
# Manual trigger for context audit
# Can be called manually or by OpenClaw hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/data/workspace"
AUDIT_SCRIPT="$WORKSPACE/security/scripts/context_auditor.js"
HOOK_URL="http://localhost:33123/context-audit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "====================================="
echo "  Context Audit Trigger"
echo "====================================="

# Check if hook server is running
if curl -s "$HOOK_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Hook server is running"
    USE_HOOK=true
else
    echo -e "${YELLOW}⚠${NC} Hook server not available, falling back to direct script execution"
    USE_HOOK=false
fi

if [[ "$USE_HOOK" == "true" ]]; then
    echo "Triggering audit via hook server..."
    RESPONSE=$(curl -s -X POST "$HOOK_URL")
    echo ""
    echo "Response:"
    echo "$RESPONSE" | node -e "console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(0, 'utf8')), null, 2))" 2>/dev/null || echo "$RESPONSE"
    
    # Check if threshold exceeded
    if echo "$RESPONSE" | grep -q '"exceeded":true'; then
        echo ""
        echo -e "${RED}⚠ WARNING: Context size exceeds threshold!${NC}"
        echo "Review the generated report for details."
    fi
else
    echo "Running audit script directly..."
    if [[ -f "$AUDIT_SCRIPT" ]]; then
        REPORT_PATH=$(node "$AUDIT_SCRIPT")
        echo -e "${GREEN}✓${NC} Audit complete"
        echo "Report: $REPORT_PATH"
        
        # Extract token count from report
        TOKENS=$(grep -oP '\*\*~\K[\d,]+(?= tokens\*\*)' "$REPORT_PATH" | head -1 | tr -d ',')
        THRESHOLD=${SEC_CONTEXT_AUDIT_THRESHOLD:-3500}
        
        echo ""
        echo "Summary:"
        echo "  Total tokens: $TOKENS"
        echo "  Threshold: $THRESHOLD"
        
        if [[ "$TOKENS" -gt "$THRESHOLD" ]]; then
            echo -e "  Status: ${RED}⚠ EXCEEDS THRESHOLD${NC}"
        else
            echo -e "  Status: ${GREEN}✓ Within limits${NC}"
        fi
    else
        echo -e "${RED}✗${NC} Audit script not found: $AUDIT_SCRIPT"
        exit 1
    fi
fi

echo ""
echo "====================================="
echo "  Audit complete"
echo "====================================="

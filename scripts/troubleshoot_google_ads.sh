#!/bin/bash
# Google Ads API Access Troubleshooter
# Diagnoses and helps fix 404 errors

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "GOOGLE ADS API ACCESS TROUBLESHOOTER"
echo "=========================================="
echo ""

# Account IDs
MCC_ID="${GOOGLE_ADS_CUSTOMER_ID:-2823334378}"
DA_ACCOUNT="6329354566"
LD_ACCOUNT="7145222813"

echo "Configuration:"
echo "  MCC ID: $MCC_ID"
echo "  Dental Artistry: $DA_ACCOUNT"
echo "  Lumiere Dental: $LD_ACCOUNT"
echo ""

# Check 1: Environment Variables
echo -e "${YELLOW}CHECK 1: Environment Variables${NC}"
echo "----------------------------------------"

MISSING_VARS=0

if [ -z "$GOOGLE_ADS_ACCESS_TOKEN" ]; then
    echo -e "${RED}✗ GOOGLE_ADS_ACCESS_TOKEN not set${NC}"
    MISSING_VARS=$((MISSING_VARS + 1))
else
    echo -e "${GREEN}✓ GOOGLE_ADS_ACCESS_TOKEN set${NC}"
    echo "  Length: ${#GOOGLE_ADS_ACCESS_TOKEN} characters"
    echo "  Preview: ${GOOGLE_ADS_ACCESS_TOKEN:0:30}..."
fi

if [ -z "$GOOGLE_ADS_REFRESH_TOKEN" ]; then
    echo -e "${RED}✗ GOOGLE_ADS_REFRESH_TOKEN not set${NC}"
    MISSING_VARS=$((MISSING_VARS + 1))
else
    echo -e "${GREEN}✓ GOOGLE_ADS_REFRESH_TOKEN set${NC}"
fi

if [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    echo -e "${RED}✗ GOOGLE_ADS_DEVELOPER_TOKEN not set${NC}"
    MISSING_VARS=$((MISSING_VARS + 1))
else
    echo -e "${GREEN}✓ GOOGLE_ADS_DEVELOPER_TOKEN set${NC}"
    echo "  Preview: ${GOOGLE_ADS_DEVELOPER_TOKEN:0:15}..."
fi

if [ -z "$GOOGLE_ADS_CLIENT_ID" ]; then
    echo -e "${RED}✗ GOOGLE_ADS_CLIENT_ID not set${NC}"
    MISSING_VARS=$((MISSING_VARS + 1))
else
    echo -e "${GREEN}✓ GOOGLE_ADS_CLIENT_ID set${NC}"
fi

if [ -z "$GOOGLE_ADS_CLIENT_SECRET" ]; then
    echo -e "${RED}✗ GOOGLE_ADS_CLIENT_SECRET not set${NC}"
    MISSING_VARS=$((MISSING_VARS + 1))
else
    echo -e "${GREEN}✓ GOOGLE_ADS_CLIENT_SECRET set${NC}"
fi

if [ $MISSING_VARS -gt 0 ]; then
    echo ""
    echo -e "${RED}ERROR: $MISSING_VARS required variables missing${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ All environment variables present${NC}"
echo ""

# Check 2: Refresh Token Validity
echo -e "${YELLOW}CHECK 2: OAuth Token Refresh${NC}"
echo "----------------------------------------"

echo "Attempting to refresh access token..."

REFRESH_RESPONSE=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=refresh_token" \
    -d "refresh_token=${GOOGLE_ADS_REFRESH_TOKEN}" \
    -d "client_id=${GOOGLE_ADS_CLIENT_ID}" \
    -d "client_secret=${GOOGLE_ADS_CLIENT_SECRET}" 2>&1)

if echo "$REFRESH_RESPONSE" | grep -q '"access_token"'; then
    echo -e "${GREEN}✓ Token refresh successful${NC}"
    NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | grep -o '"access_token": "[^"]*"' | cut -d'"' -f4)
    echo "  New token: ${NEW_ACCESS_TOKEN:0:40}..."
    
    # Update environment for this session
    export GOOGLE_ADS_ACCESS_TOKEN="$NEW_ACCESS_TOKEN"
    echo ""
    echo "Token refreshed. Using new access token for remaining checks."
else
    echo -e "${RED}✗ Token refresh failed${NC}"
    echo "Response:"
    echo "$REFRESH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REFRESH_RESPONSE"
    exit 1
fi

echo ""

# Check 3: MCC Account Access
echo -e "${YELLOW}CHECK 3: MCC Account Access${NC}"
echo "----------------------------------------"
echo "Testing access to MCC account: $MCC_ID"

MCC_TEST=$(curl -s -X POST "https://googleads.googleapis.com/v15/customers/${MCC_ID}/googleAds:search" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"}' \
    -w "\nHTTP_CODE:%{http_code}")

MCC_HTTP=$(echo "$MCC_TEST" | grep 'HTTP_CODE:' | cut -d: -f2)

if [ "$MCC_HTTP" == "200" ]; then
    echo -e "${GREEN}✓ MCC account accessible${NC}"
    MCC_NAME=$(echo "$MCC_TEST" | grep -o '"descriptiveName": "[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$MCC_NAME" ]; then
        echo "  Account name: $MCC_NAME"
    fi
else
    echo -e "${RED}✗ Cannot access MCC account (HTTP $MCC_HTTP)${NC}"
    echo "Error details:"
    echo "$MCC_TEST" | sed '/HTTP_CODE:/d' | python3 -m json.tool 2>/dev/null || echo "$MCC_TEST"
    echo ""
    echo -e "${YELLOW}This indicates the access token doesn't have permission${NC}"
    echo "to access the MCC account. Check:"
    echo "1. The refresh token was generated with the correct OAuth scopes"
    echo "2. The MCC account hasn't been removed or disabled"
fi

echo ""

# Check 4: Client Account Access via MCC
echo -e "${YELLOW}CHECK 4: Client Account Access${NC}"
echo "----------------------------------------"

echo "Testing Dental Artistry account ($DA_ACCOUNT)..."
DA_TEST=$(curl -s -X POST "https://googleads.googleapis.com/v15/customers/${DA_ACCOUNT}/googleAds:search" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "login-customer-id: ${MCC_ID}" \
    -d '{"query": "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"}' \
    -w "\nHTTP_CODE:%{http_code}")

DA_HTTP=$(echo "$DA_TEST" | grep 'HTTP_CODE:' | cut -d: -f2)

if [ "$DA_HTTP" == "200" ]; then
    echo -e "${GREEN}✓ Dental Artistry account accessible${NC}"
    DA_NAME=$(echo "$DA_TEST" | grep -o '"descriptiveName": "[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$DA_NAME" ]; then
        echo "  Account name: $DA_NAME"
    fi
elif [ "$DA_HTTP" == "404" ]; then
    echo -e "${RED}✗ Account not found (HTTP 404)${NC}"
    echo ""
    echo -e "${YELLOW}POSSIBLE CAUSES:${NC}"
    echo "1. Account ID is incorrect"
    echo "2. MCC ($MCC_ID) doesn't have access to this account"
    echo "3. Account has been cancelled or merged"
    echo ""
    echo -e "${YELLOW}TO FIX:${NC}"
    echo "1. Verify the account ID in Google Ads:"
    echo "   https://ads.google.com/aw/overview?ocid=$DA_ACCOUNT"
    echo ""
    echo "2. In your MCC account, check linked accounts:"
    echo "   https://ads.google.com/aw/accounts"
    echo ""
    echo "3. If account is not linked, send a link request from MCC"
else
    echo -e "${RED}✗ Error accessing account (HTTP $DA_HTTP)${NC}"
    echo "$DA_TEST" | sed '/HTTP_CODE:/d'
fi

echo ""
echo "Testing Lumiere Dental account ($LD_ACCOUNT)..."
LD_TEST=$(curl -s -X POST "https://googleads.googleapis.com/v15/customers/${LD_ACCOUNT}/googleAds:search" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "login-customer-id: ${MCC_ID}" \
    -d '{"query": "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"}' \
    -w "\nHTTP_CODE:%{http_code}")

LD_HTTP=$(echo "$LD_TEST" | grep 'HTTP_CODE:' | cut -d: -f2)

if [ "$LD_HTTP" == "200" ]; then
    echo -e "${GREEN}✓ Lumiere Dental account accessible${NC}"
    LD_NAME=$(echo "$LD_TEST" | grep -o '"descriptiveName": "[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$LD_NAME" ]; then
        echo "  Account name: $LD_NAME"
    fi
elif [ "$LD_HTTP" == "404" ]; then
    echo -e "${RED}✗ Account not found (HTTP 404)${NC}"
    echo "Same troubleshooting steps as Dental Artistry apply."
else
    echo -e "${RED}✗ Error accessing account (HTTP $LD_HTTP)${NC}"
fi

echo ""

# Check 5: Developer Token Status
echo -e "${YELLOW}CHECK 5: Developer Token Status${NC}"
echo "----------------------------------------"

echo "The developer token must be approved for production use."
echo "Check status at: https://ads.google.com/aw/apicenter"
echo ""
echo -e "${YELLOW}If you see 'Approval pending':${NC}"
echo "- Apply for production access with business justification"
echo "- Usually takes 1-2 business days"
echo ""
echo -e "${YELLOW}If you see 'Approved':${NC}"
echo "- Token is valid, issue is likely account linking"
echo ""

# Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="

if [ "$MCC_HTTP" == "200" ] && [ "$DA_HTTP" == "200" ] && [ "$LD_HTTP" == "200" ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "API access is working! You can now run:"
    echo "  /data/workspace/scripts/fetch_google_ads.sh 6329354566"
    echo "  /data/workspace/scripts/fetch_google_ads.sh 7145222813"
    exit 0
else
    echo -e "${YELLOW}⚠ ISSUES DETECTED${NC}"
    echo ""
    
    if [ "$MCC_HTTP" != "200" ]; then
        echo "Issue: Cannot access MCC account"
        echo "Action: Verify OAuth scopes and token permissions"
        echo ""
    fi
    
    if [ "$DA_HTTP" == "404" ] || [ "$LD_HTTP" == "404" ]; then
        echo "Issue: Client accounts not accessible via API"
        echo "Action: Link accounts to MCC in Google Ads UI"
        echo ""
        echo "STEPS TO LINK ACCOUNTS:"
        echo "1. Log into MCC: https://ads.google.com/aw/accounts"
        echo "2. Click '+ Link existing account'"
        echo "3. Enter account IDs: $DA_ACCOUNT and $LD_ACCOUNT"
        echo "4. Send link requests"
        echo "5. Approve link requests from client accounts"
        echo ""
        echo "ACCOUNT LOGIN LINKS:"
        echo "  Dental Artistry: https://ads.google.com/aw/overview?ocid=$DA_ACCOUNT"
        echo "  Lumiere Dental: https://ads.google.com/aw/overview?ocid=$LD_ACCOUNT"
    fi
    
    exit 1
fi

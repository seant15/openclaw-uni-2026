#!/bin/bash
# Google Ads Reporter - Alternative endpoints
# Tests multiple API approaches

ACCOUNT_ID="${1:-6329354566}"
START_DATE="${2:-2026-02-18}"
END_DATE="${3:-2026-02-24}"

# Remove dashes from account ID if present
CLEAN_ACCOUNT_ID=$(echo "$ACCOUNT_ID" | tr -d '-')

API_BASE="https://googleads.googleapis.com"
ACCESS_TOKEN="${GOOGLE_ADS_ACCESS_TOKEN}"
DEV_TOKEN="${GOOGLE_ADS_DEVELOPER_TOKEN}"
LOGIN_ID="${GOOGLE_ADS_CUSTOMER_ID:-}"

echo "=========================================="
echo "Google Ads API Diagnostic Tool"
echo "=========================================="
echo "Original Account ID: $ACCOUNT_ID"
echo "Clean Account ID: $CLEAN_ACCOUNT_ID"
echo ""

# Test different endpoints
ENDPOINTS=(
    "v15/customers/${CLEAN_ACCOUNT_ID}/googleAds:search"
    "v15/customers/${CLEAN_ACCOUNT_ID}/googleAds:searchStream"
    "v14/customers/${CLEAN_ACCOUNT_ID}/googleAds:search"
    "v14/customers/${CLEAN_ACCOUNT_ID}/googleAds:searchStream"
    "v13/customers/${CLEAN_ACCOUNT_ID}/googleAds:search"
)

QUERY='SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1'

for ENDPOINT in "${ENDPOINTS[@]}"; do
    URL="${API_BASE}/${ENDPOINT}"
    echo "Testing: $URL"
    
    if [ -n "$LOGIN_ID" ]; then
        RESPONSE=$(curl -s -X POST "$URL" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}" \
            -H "developer-token: ${DEV_TOKEN}" \
            -H "Content-Type: application/json" \
            -H "login-customer-id: ${LOGIN_ID}" \
            -d "{\"query\": \"$QUERY\"}" \
            -w "\nHTTP_CODE:%{http_code}" 2>&1)
    else
        RESPONSE=$(curl -s -X POST "$URL" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}" \
            -H "developer-token: ${DEV_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$QUERY\"}" \
            -w "\nHTTP_CODE:%{http_code}" 2>&1)
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | grep 'HTTP_CODE:' | cut -d: -f2)
    
    if [ "$HTTP_CODE" == "200" ]; then
        echo "  ✓ SUCCESS with $ENDPOINT"
        echo ""
        echo "Working endpoint found: $ENDPOINT"
        
        # Save the working endpoint
        echo "$ENDPOINT" > /tmp/google_ads_working_endpoint.txt
        
        # Show response preview
        echo "Response preview:"
        echo "$RESPONSE" | sed '/HTTP_CODE:/d' | head -3
        exit 0
    else
        echo "  ✗ Failed (HTTP $HTTP_CODE)"
    fi
done

echo ""
echo "=========================================="
echo "All endpoints returned errors"
echo "=========================================="
echo ""
echo "Possible issues:"
echo "1. Access token may be expired"
echo "2. Developer token may be invalid"
echo "3. Account ID may be incorrect or no access"
echo "4. API may not be enabled for this project"
echo ""
echo "To debug, check Google Ads API credentials:"
echo "- MCC Account: https://ads.google.com/aw/overview"
echo "- API Center: https://ads.google.com/aw/apicenter"
echo ""

# Try to refresh the access token using the refresh token
if [ -n "$GOOGLE_ADS_REFRESH_TOKEN" ] && [ -n "$GOOGLE_ADS_CLIENT_ID" ] && [ -n "$GOOGLE_ADS_CLIENT_SECRET" ]; then
    echo "Attempting to refresh access token..."
    
    REFRESH_RESPONSE=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=refresh_token" \
        -d "refresh_token=${GOOGLE_ADS_REFRESH_TOKEN}" \
        -d "client_id=${GOOGLE_ADS_CLIENT_ID}" \
        -d "client_secret=${GOOGLE_ADS_CLIENT_SECRET}" 2>&1)
    
    if echo "$REFRESH_RESPONSE" | grep -q '"access_token"'; then
        echo "✓ Token refresh successful!"
        NEW_TOKEN=$(echo "$REFRESH_RESPONSE" | grep -o '"access_token": "[^"]*"' | cut -d'"' -f4)
        echo "New token: ${NEW_TOKEN:0:30}..."
        echo ""
        echo "Update your environment with:"
        echo "export GOOGLE_ADS_ACCESS_TOKEN='$NEW_TOKEN'"
    else
        echo "✗ Token refresh failed"
        echo "Response: $REFRESH_RESPONSE"
    fi
fi

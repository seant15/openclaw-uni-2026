#!/bin/bash
# Google Ads Reporter - Working Version
# Uses curl with proper authentication

ACCOUNT_ID="${1:-6329354566}"
START_DATE="${2:-2026-02-18}"
END_DATE="${3:-2026-02-24}"
CLIENT_TYPE="${4:-dental_artistry}"

API_VERSION="v15"
API_BASE="https://googleads.googleapis.com/${API_VERSION}"

echo "=========================================="
echo "Google Ads Weekly Report Generator"
echo "=========================================="
echo "Account ID: $ACCOUNT_ID"
echo "Date Range: $START_DATE to $END_DATE"
echo ""

# Check environment variables
if [ -z "$GOOGLE_ADS_ACCESS_TOKEN" ] || [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    echo "ERROR: Missing required environment variables"
    exit 1
fi

LOGIN_ID="${GOOGLE_ADS_CUSTOMER_ID:-}"

echo "Testing API connection..."

# Simple test query
TEST_QUERY='SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1'

# Build and execute curl command
URL="${API_BASE}/customers/${ACCOUNT_ID}/googleAds:searchStream"

echo "URL: $URL"
echo ""

# Create temp file for response
RESPONSE_FILE=$(mktemp)

# Make the API call
if [ -n "$LOGIN_ID" ]; then
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -H "login-customer-id: ${LOGIN_ID}" \
        -d "{\"query\": \"$TEST_QUERY\"}" \
        -w "\nHTTP_CODE:%{http_code}" \
        > "$RESPONSE_FILE" 2>&1
else
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$TEST_QUERY\"}" \
        -w "\nHTTP_CODE:%{http_code}" \
        > "$RESPONSE_FILE" 2>&1
fi

# Extract HTTP code
HTTP_CODE=$(grep 'HTTP_CODE:' "$RESPONSE_FILE" | cut -d: -f2)

# Remove HTTP code line
sed -i '/HTTP_CODE:/d' "$RESPONSE_FILE"

echo "HTTP Response: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" != "200" ]; then
    echo "⚠ API Error (HTTP $HTTP_CODE)"
    echo ""
    echo "Response:"
    cat "$RESPONSE_FILE" | head -100
    
    # Check for specific errors
    if grep -q "UNAUTHENTICATED" "$RESPONSE_FILE" 2>/dev/null; then
        echo ""
        echo "ERROR: Access token may be expired. Need to refresh."
    fi
    
    if grep -q "NOT_FOUND" "$RESPONSE_FILE" 2>/dev/null; then
        echo ""
        echo "ERROR: Customer ID not found or no access."
    fi
    
    rm -f "$RESPONSE_FILE"
    exit 1
fi

echo "✓ API connection successful!"
echo ""

# Now fetch real data
echo "Fetching account metrics for date range..."

ACCOUNT_QUERY="SELECT customer.id, customer.descriptive_name, segments.date, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion FROM customer WHERE segments.date BETWEEN '${START_DATE}' AND '${END_DATE}'"

if [ -n "$LOGIN_ID" ]; then
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -H "login-customer-id: ${LOGIN_ID}" \
        -d "{\"query\": \"$ACCOUNT_QUERY\"}" \
        > "/tmp/account_${ACCOUNT_ID}.json" 2>&1
else
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$ACCOUNT_QUERY\"}" \
        > "/tmp/account_${ACCOUNT_ID}.json" 2>&1
fi

echo "✓ Account data saved"

# Fetch campaign data
echo "Fetching campaign data..."

CAMPAIGN_QUERY="SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion FROM campaign WHERE segments.date BETWEEN '${START_DATE}' AND '${END_DATE}' AND metrics.cost_micros > 0 ORDER BY metrics.cost_micros DESC LIMIT 10"

if [ -n "$LOGIN_ID" ]; then
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -H "login-customer-id: ${LOGIN_ID}" \
        -d "{\"query\": \"$CAMPAIGN_QUERY\"}" \
        > "/tmp/campaigns_${ACCOUNT_ID}.json" 2>&1
else
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$CAMPAIGN_QUERY\"}" \
        > "/tmp/campaigns_${ACCOUNT_ID}.json" 2>&1
fi

echo "✓ Campaign data saved"

# Fetch search terms
echo "Fetching search terms..."

SEARCH_QUERY="SELECT search_term_view.search_term, metrics.impressions, metrics.clicks, metrics.conversions, metrics.cost_micros FROM search_term_view WHERE segments.date BETWEEN '${START_DATE}' AND '${END_DATE}' AND metrics.clicks > 0 ORDER BY metrics.conversions DESC, metrics.cost_micros DESC LIMIT 30"

if [ -n "$LOGIN_ID" ]; then
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -H "login-customer-id: ${LOGIN_ID}" \
        -d "{\"query\": \"$SEARCH_QUERY\"}" \
        > "/tmp/search_${ACCOUNT_ID}.json" 2>&1
else
    curl -s -X POST "$URL" \
        -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
        -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$SEARCH_QUERY\"}" \
        > "/tmp/search_${ACCOUNT_ID}.json" 2>&1
fi

echo "✓ Search terms saved"

# Clean up
rm -f "$RESPONSE_FILE"

echo ""
echo "=========================================="
echo "DATA FETCHED SUCCESSFULLY"
echo "=========================================="

# Check and display summary
ACCOUNT_SIZE=$(wc -c < "/tmp/account_${ACCOUNT_ID}.json")
CAMPAIGN_SIZE=$(wc -c < "/tmp/campaigns_${ACCOUNT_ID}.json")
SEARCH_SIZE=$(wc -c < "/tmp/search_${ACCOUNT_ID}.json")

echo ""
echo "File sizes:"
echo "  Account data: $ACCOUNT_SIZE bytes"
echo "  Campaign data: $CAMPAIGN_SIZE bytes"
echo "  Search terms: $SEARCH_SIZE bytes"

# Check if data is valid JSON/NDJSON
if head -1 "/tmp/account_${ACCOUNT_ID}.json" | grep -q '"results"\|"customer"' 2>/dev/null; then
    echo ""
    echo "✓ Data format looks valid"
    
    # Extract customer name if available
    CUSTOMER_NAME=$(grep -o '"descriptiveName": "[^"]*"' "/tmp/account_${ACCOUNT_ID}.json" | head -1 | cut -d'"' -f4)
    if [ -n "$CUSTOMER_NAME" ]; then
        echo "  Account: $CUSTOMER_NAME"
    fi
    
    # Count rows
    ACCOUNT_ROWS=$(wc -l < "/tmp/account_${ACCOUNT_ID}.json")
    echo "  Account rows: $ACCOUNT_ROWS"
else
    echo ""
    echo "⚠ Unexpected response format. First 500 chars:"
    head -c 500 "/tmp/account_${ACCOUNT_ID}.json"
fi

echo ""
echo "=========================================="
echo "Next: Format the report"
echo "=========================================="
echo "Data files:"
echo "  /tmp/account_${ACCOUNT_ID}.json"
echo "  /tmp/campaigns_${ACCOUNT_ID}.json"
echo "  /tmp/search_${ACCOUNT_ID}.json"
echo ""
echo "To format as report, run:"
echo "  /data/workspace/scripts/format_report.sh $ACCOUNT_ID $CLIENT_TYPE"

#!/bin/bash
# Google Ads Reporter with refreshed token
# Updated: 2026-02-27

# Use the refreshed token
export GOOGLE_ADS_ACCESS_TOKEN='ya29.a0ATkoCc68YYJCCmQpIEiLs8F2I3dnMuGWpAvE9lnNM31Tm9Zn40so668g0KE8ox0m-oP1jaln4NPMMAHsoqd20k5eJzHdhTUIk7Q3ajRYyz9SSb7TaWScxVFaxdIIoaQ7O-uqON1UOG-BSIXVphLaKdCgdu7BQZudjdMkjI_LXgsjbjNhsUB3Tw7N8pyED46MO9tQofHsIgaCgYKAe8SARQSFQHGX2MiFqQE8T-JiCSupapYZXk7yQ0209'

ACCOUNT_ID="${1:-6329354566}"
START_DATE="${2:-2026-02-18}"
END_DATE="${3:-2026-02-24}"
CLIENT_TYPE="${4:-dental_artistry}"

API_VERSION="v15"
API_BASE="https://googleads.googleapis.com/${API_VERSION}"

echo "=========================================="
echo "Google Ads Reporter (Updated Token)"
echo "=========================================="
echo "Account ID: $ACCOUNT_ID"
echo "Date Range: $START_DATE to $END_DATE"
echo ""

# Check environment
if [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    echo "ERROR: GOOGLE_ADS_DEVELOPER_TOKEN not set"
    exit 1
fi

LOGIN_ID="${GOOGLE_ADS_CUSTOMER_ID:-2823334378}"

echo "Using MCC Login ID: $LOGIN_ID"
echo ""

# Try a simple query first
URL="${API_BASE}/customers/${ACCOUNT_ID}/googleAds:search"
QUERY='SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1'

echo "Testing API connection..."
RESPONSE=$(curl -s -X POST "$URL" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "login-customer-id: ${LOGIN_ID}" \
    -d "{\"query\": \"$QUERY\"}" \
    -w "\nHTTP_CODE:%{http_code}" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | grep 'HTTP_CODE:' | cut -d: -f2)
echo "Response code: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    echo ""
    echo "=========================================="
    echo "API ACCESS ISSUE DETECTED"
    echo "=========================================="
    echo ""
    echo "The Google Ads API is returning 404 for account $ACCOUNT_ID"
    echo ""
    echo "This usually means one of:"
    echo "1. The account ID doesn't exist"
    echo "2. Your MCC ($LOGIN_ID) doesn't have access to this account"
    echo "3. The API is not enabled for this Google Cloud project"
    echo "4. The developer token is not approved for API access"
    echo ""
    echo "QUICK FIXES TO TRY:"
    echo ""
    echo "1. Verify account ID in Google Ads:"
    echo "   https://ads.google.com/aw/overview?ocid=$ACCOUNT_ID"
    echo ""
    echo "2. Check API Center for developer token status:"
    echo "   https://ads.google.com/aw/apicenter"
    echo ""
    echo "3. Verify MCC account link:"
    echo "   - Log into MCC: $LOGIN_ID"
    echo "   - Check if account $ACCOUNT_ID is linked"
    echo ""
    echo "4. Alternative: Use Google Ads Query Builder"
    echo "   https://developers.google.com/google-ads/api/fields/v15/query_validator"
    echo ""
    echo "WORKAROUND: Manual data entry"
    echo "=========================================="
    echo ""
    echo "Paste your Google Ads data below and I'll format the report:"
    echo ""
    echo "Format:"
    echo "CAMPAIGN NAME | SPEND | LEADS | CLICKS | IMPRESSIONS"
    echo ""
    
    exit 1
fi

echo "✓ API connection successful!"
echo ""

# Fetch account metrics
ACCOUNT_QUERY="SELECT customer.id, customer.descriptive_name, segments.date, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion FROM customer WHERE segments.date BETWEEN '${START_DATE}' AND '${END_DATE}'"

echo "Fetching account metrics..."
curl -s -X POST "$URL" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "login-customer-id: ${LOGIN_ID}" \
    -d "{\"query\": \"$ACCOUNT_QUERY\"}" \
    > "/tmp/account_${ACCOUNT_ID}.json" 2>&1

echo "✓ Account data saved"

# Fetch campaign metrics
CAMPAIGN_QUERY="SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.average_cpc, metrics.conversions, metrics.cost_per_conversion FROM campaign WHERE segments.date BETWEEN '${START_DATE}' AND '${END_DATE}' AND metrics.cost_micros > 0 ORDER BY metrics.cost_micros DESC LIMIT 10"

echo "Fetching campaign data..."
curl -s -X POST "$URL" \
    -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
    -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
    -H "Content-Type: application/json" \
    -H "login-customer-id: ${LOGIN_ID}" \
    -d "{\"query\": \"$CAMPAIGN_QUERY\"}" \
    > "/tmp/campaigns_${ACCOUNT_ID}.json" 2>&1

echo "✓ Campaign data saved"

# Check results
ACCOUNT_SIZE=$(wc -c < "/tmp/account_${ACCOUNT_ID}.json")
CAMPAIGN_SIZE=$(wc -c < "/tmp/campaigns_${ACCOUNT_ID}.json")

echo ""
echo "=========================================="
echo "DATA FETCHED"
echo "=========================================="
echo "Account data: $ACCOUNT_SIZE bytes"
echo "Campaign data: $CAMPAIGN_SIZE bytes"
echo ""
echo "To format report, run:"
echo "  python3 /data/workspace/scripts/format_report.py $ACCOUNT_ID $CLIENT_TYPE"

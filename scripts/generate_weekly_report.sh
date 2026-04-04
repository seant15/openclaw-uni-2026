#!/bin/bash
# Complete Google Ads Report Workflow
# Fetches data and generates report in one command

set -e

# Configuration
export GOOGLE_ADS_CONFIGURATION_FILE_PATH=/data/workspace/config/google-ads.yaml

# Parse arguments
CUSTOMER_ID="${1:-6329354566}"
START_DATE="${2:-$(date -d '7 days ago' +%Y-%m-%d)}"
END_DATE="${3:-$(date -d '1 day ago' +%Y-%m-%d)}"
CLIENT_TYPE="${4:-auto}"

echo "=========================================="
echo "GOOGLE ADS WEEKLY REPORT WORKFLOW"
echo "=========================================="
echo "Account ID: $CUSTOMER_ID"
echo "Date Range: $START_DATE to $END_DATE"
echo "Client Type: $CLIENT_TYPE"
echo ""

# Step 1: Fetch data
echo "Step 1: Fetching Google Ads data..."
echo "----------------------------------------"

python3 /data/workspace/scripts/fetch_google_ads.py "$CUSTOMER_ID" "$START_DATE" "$END_DATE" 2>&1 | tee /tmp/fetch_output.log

# Extract output file path from fetch output
DATA_FILE=$(grep "Output file:" /tmp/fetch_output.log | sed 's/.*Output file: //')

if [ -z "$DATA_FILE" ] || [ ! -f "$DATA_FILE" ]; then
    echo "ERROR: Data fetch failed or file not found"
    exit 1
fi

echo ""
echo "✓ Data fetched: $DATA_FILE"
echo ""

# Step 2: Generate report
echo "Step 2: Generating report..."
echo "----------------------------------------"

python3 /data/workspace/scripts/generate_report.py "$DATA_FILE" "$CLIENT_TYPE"

echo ""
echo "=========================================="
echo "WORKFLOW COMPLETE"
echo "=========================================="

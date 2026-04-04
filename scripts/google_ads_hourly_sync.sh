#!/bin/bash
# Google Ads Hourly Sync Script
# Runs every hour to pull campaign, ad group, ad, keyword, and search term data

set -e

# Configuration
MCC_ID="282-333-4378"
SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_KEY="${SUPABASE_SERVICE_KEY}"

echo "[$(date)] Starting Google Ads hourly sync..."

# Get list of clients with google_ads_customer_id from Supabase
CLIENTS=$(curl -s "$SUPABASE_URL/rest/v1/clients?select=id,name,google_ads_customer_id&google_ads_customer_id=not.is.null" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY")

# For each client, sync data
# TODO: Implement actual Google Ads API calls once customer IDs are provided

echo "[$(date)] Google Ads sync complete."

#!/bin/bash
# Meta Ads Hourly Sync Script
# Runs every hour to pull campaign, ad set, and ad data

set -e

SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_KEY="${SUPABASE_SERVICE_KEY}"
META_ACCESS_TOKEN="${META_ACCESS_TOKEN}"

echo "[$(date)] Starting Meta Ads hourly sync..."

# Get list of clients with meta_ad_account_id from Supabase
CLIENTS=$(curl -s "$SUPABASE_URL/rest/v1/clients?select=id,name,meta_ad_account_id&meta_ad_account_id=not.is.null" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY")

# For each client, sync data
# TODO: Implement actual Meta Marketing API calls once account IDs are provided

echo "[$(date)] Meta Ads sync complete."

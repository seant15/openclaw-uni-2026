#!/bin/bash
# Mary Nightly Sync Script
# Pulls ClickUp tasks and Fireflies transcripts for the day
# Runs at 2 AM daily

set -e

CLICKUP_API_KEY="${CLICKUP_API_KEY}"
FIREFLIES_API_KEY="${FIREFLIES_API_KEY}"
SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_KEY="${SUPABASE_SERVICE_KEY}"

echo "[$(date)] Mary starting nightly sync..."

# 1. Get all ClickUp tasks updated today
TODAY=$(date -u +%Y-%m-%d)

echo "[$(date)] Fetching ClickUp tasks for $TODAY..."

# Get all lists from DELIVERY space
LISTS=$(curl -s -H "Authorization: $CLICKUP_API_KEY" \
  "https://api.clickup.com/api/v2/space/90090520327/list?archived=false")

# For each list, get tasks updated today
# TODO: Store in Supabase for OpenClaw access

# 2. Get today's Fireflies transcripts
echo "[$(date)] Fetching Fireflies transcripts..."

# TODO: Query Fireflies API for today's meetings

# 3. Summary report for Slack/OpenClaw
echo "[$(date)] Generating daily summary..."

# TODO: Generate summary and send to Slack

echo "[$(date)] Mary nightly sync complete."

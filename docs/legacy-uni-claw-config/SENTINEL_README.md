# Sentinel: Real-Time Performance Monitor & Alert System

## Overview
Sentinel is an advanced performance monitoring system designed to track system metrics, monitor integrations, and generate automated alerts using Supabase MCP, Ad APIs, and Slack.

## Key Features
- Real-time system performance monitoring
- Ad API integration tracking
- Automated Slack alerting
- Persistent logging
- Supabase metric storage

## Prerequisites
1. Python 3.7+
2. Supabase account and project
3. Slack Webhook URL
4. Ad API credentials

## Environment Variables
Configure the following environment variables:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase project API key
- `SLACK_WEBHOOK_URL`: Slack incoming webhook URL
- `AD_API_KEY`: Ad API authentication key
- `AD_API_ENDPOINT`: Ad API base endpoint

## Setup
1. Install dependencies:
   ```
   pip install supabase-py requests
   ```

2. Set environment variables

3. Run the monitor:
   ```
   python sentinel_monitor.py
   ```

## Alerts
Sentinel generates Slack alerts for:
- High CPU usage (>80%)
- High memory usage (>85%)
- Integration failures
- Critical system errors

## Logging
Logs are stored in `/data/workspace/sentinel.log`

## Customization
Modify thresholds and monitoring intervals in the `run()` method.
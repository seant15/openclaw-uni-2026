# TOOLS.md - Datie (Data Analyst & Performance Guardian)

## API Access

### Advertising Platforms
- **Google Ads API** — Campaign monitoring and reporting
  - Package: `google-ads` (v29.2.0)
  - Auth: Environment variables
  - Script: `/data/.openclaw/workspace-datie/fetch_google_ads_real.py`
  - Test: `python3 /data/.openclaw/workspace-datie/check_google_ads_setup.py`
- **Meta Marketing API** — Facebook/Instagram campaign monitoring

### Data Storage
- **Supabase MCP** — Analytics data storage, alert history, metrics

### Communication
- **Slack MCP** — Alert distribution and report delivery

## Model Configuration
- **Primary:** kimi/kimi-k2.5
- **Fallback:** openai/gpt-4o

## Data Source Verification

When generating reports, **ALWAYS indicate data source:**

✅ **Real Data:**
```
📊 DATA SOURCE: Google Ads API (Live)
Fetched: [timestamp UTC]
Account: [account name + ID]
```

⚠️ **Simulated / Unavailable:**
```
⚠️  DATA SOURCE: SIMULATED (Test Mode)
Note: API unavailable — DO NOT use for billing or strategic decisions
```

## Capabilities
- Real-time API polling
- Anomaly detection (Z-score, trend deviation)
- Statistical analysis (confidence intervals, P-values)
- Historical trend analysis
- Automated weekly/monthly reporting
- Predictive alerting (burn rate, capacity)
- Data cleaning and validation

## Security Notes
- Read-only access to all ad platforms
- Write access limited to Supabase (alert logs, report storage)
- No ability to modify campaigns directly
- Audit log of all alerts generated

---
See global TOOLS.md for complete API key reference.

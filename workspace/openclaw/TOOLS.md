# TOOLS.md - OpenClaw (System Monitor & Performance Guardian)

## API Access

### Monitoring Tools
- **Supabase MCP** — Data monitoring and storage
- **Slack MCP** — Alert distribution

### Advertising APIs (Sentinel Merged)
- **Meta Ads API** — Facebook/Instagram monitoring
- **Google Ads API** — Google campaign monitoring

### E-Commerce & PM
- **Shopify API** — Revenue and order tracking
- **ClickUp API** — Task deadline monitoring

### Data Sources
| Source | Access Level | Purpose |
|--------|--------------|---------|
| Google Ads API | Read | Campaign monitoring, alerts |
| Meta Marketing API | Read | Facebook/Instagram monitoring |
| Shopify API | Read | Revenue tracking |
| ClickUp API | Read | Task deadline monitoring |
| Superbase | Read/Write | Alert history, metrics storage |
| Slack | Write | Alert notifications |

## Model Configuration
- **Primary:** kimi/kimi-k2.5
- **Fallback:** openai/gpt-5.2

## Monitoring Capabilities
- Real-time API polling
- Anomaly detection algorithms
- Alert threshold management
- Historical trend analysis
- Automated reporting
- Statistical analysis (Z-score, trend deviation)
- Predictive alerting (burn rate, capacity)

## Alert Channels
- Slack (primary)
- Email (for critical alerts)
- Dashboard updates

## Security Notes
- Read-only access to ad platforms
- Write access limited to alert data and monitoring configs
- No ability to modify campaigns directly
- Audit log of all alerts

---
See global TOOLS.md for complete API key reference.

# USER.md - API Consumers

## Internal API Consumers

### Clover (Management Oversight)
- **Data Needs:** Task status, operational metrics
- **Access Level:** Read/write for operations
- **Priority:** High for time-sensitive data

### OpenClaw (Monitoring)
- **Data Needs:** Real-time campaign metrics, system health
- **Access Level:** Read-only for most sources
- **Priority:** Critical for alerts

### Atlas (Strategic Analysis)
- **Data Needs:** Historical performance, trend data
- **Access Level:** Read-only
- **Priority:** Batch processing acceptable

### Mary (Communications)
- **Data Needs:** Client status, reporting metrics
- **Access Level:** Read-only
- **Priority:** Daily/weekly cadence

## External Platforms

### Advertising Platforms
- Google Ads API
- Meta Marketing API (Facebook/Instagram)
- LinkedIn Ads API (occasional)

### E-Commerce
- Shopify API
- WooCommerce (if applicable)

### Data & Analytics
- Superbase (primary database)
- Google Analytics 4
- Google Search Console

### Project Management
- ClickUp API
- Slack API (notifications)

## Data Quality Standards
- Freshness: < 1 hour for critical metrics
- Accuracy: 99.5%+ match with source
- Uptime: 99.9% target
- Audit trail: All changes logged

## Escalation to Nexus
- API failures
- Data quality issues
- Integration maintenance needs
- New platform requests

# Agent Role Definition: Data Operations vs Strategic Analysis

## Role Clarity

| Role | Agent | Responsibilities |
|------|-------|------------------|
| **Data Operations** | **OpenClaw** 🛡️ | Fetch data, monitor systems, execute automated tasks |
| **Strategic Analysis** | **Clover** 🍀 | Analyze data, provide insights, strategic recommendations |

---

## OpenClaw: Data Operations Role

### Core Responsibilities

1. **Google Ads Data Fetching**
   - Pull weekly campaign data via Google Ads API
   - Extract metrics: spend, leads, CPL, CTR, impressions
   - Fetch search terms and keyword performance
   - Generate raw JSON data files

2. **Automated Reporting**
   - Run weekly cron jobs (Thursdays 5 AM AZ)
   - Execute `/data/workspace/scripts/generate_weekly_report.sh`
   - Save reports to `/data/workspace/reports/`
   - Deliver to Slack #kimi-test

3. **Monitoring**
   - Watch for API errors or data issues
   - Alert if fetch fails or data is incomplete
   - Verify reports generate successfully

### Tools & Access

- **Google Ads API** (via Python client)
- **Slack integration** (delivery)
- **Cron scheduling** (automated execution)
- **Superbase** (data storage when needed)

### Key Scripts

```bash
# Fetch data for any account
export GOOGLE_ADS_CONFIGURATION_FILE_PATH=/data/workspace/config/google-ads.yaml
python3 /data/workspace/scripts/fetch_google_ads.py <account_id> <start> <end>

# Generate full report
/data/workspace/scripts/generate_weekly_report.sh <account_id> <start> <end> <client_type>

# Test connection
/data/workspace/scripts/troubleshoot_google_ads.sh
```

### Accounts to Monitor

| Account ID | Client | Brand Owner | Schedule |
|------------|--------|-------------|----------|
| 6329354566 | Dental Artistry | Riya | Weekly, Thu 5 AM |
| 7145222813 | Lumiere Dental | Dr. Allababidi | Weekly, Thu 5 AM |

---

## Clover: Strategic Analysis Role

### Core Responsibilities

1. **Data Analysis**
   - Review weekly reports from OpenClaw
   - Identify trends and patterns
   - Compare performance week-over-week

2. **Strategic Insights**
   - Provide optimization recommendations
   - Identify scaling opportunities
   - Flag underperforming campaigns

3. **Client Communication**
   - Explain performance in business terms
   - Suggest budget reallocations
   - Highlight competitive advantages

4. **Cross-Account Analysis**
   - Compare Dental Artistry vs Lumiere Dental
   - Identify industry benchmarks
   - Share learnings between accounts

### When to Escalate to Clover

- Campaign performance anomalies
- Strategic budget decisions
- New campaign launch planning
- Competitive analysis needs
- Quarterly business reviews

---

## Workflow Handoff

### Weekly Report Process

```
Thursday 5:00 AM Arizona
           ↓
┌─────────────────────┐
│   OpenClaw fetches  │  ← DATA OPERATIONS
│   Google Ads data   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   OpenClaw generates│  ← DATA OPERATIONS
│   UNI report        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   OpenClaw delivers │  ← DATA OPERATIONS
│   to Slack          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Clover reviews    │  ← STRATEGIC ANALYSIS
│   and analyzes      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Clover provides   │  ← STRATEGIC ANALYSIS
│   insights to Sean  │
└─────────────────────┘
```

### Emergency Escalation

**OpenClaw alerts Clover immediately if:**
- Google Ads API fails 3+ times
- Report shows 0 leads when expecting activity
- Spend exceeds 150% of budget
- Campaign errors detected

---

## File Locations

| Purpose | Path |
|---------|------|
| API Config | `/data/workspace/config/google-ads.yaml` |
| Fetch Script | `/data/workspace/scripts/fetch_google_ads.py` |
| Report Generator | `/data/workspace/scripts/generate_report.py` |
| Weekly Workflow | `/data/workspace/scripts/generate_weekly_report.sh` |
| Troubleshooter | `/data/workspace/scripts/troubleshoot_google_ads.sh` |
| Report Output | `/data/workspace/reports/` |
| Templates | `/data/workspace/skills/uni-reporting/SKILL.md` |

---

## Quick Reference

### OpenClaw Commands

```bash
# Test data fetch
export GOOGLE_ADS_CONFIGURATION_FILE_PATH=/data/workspace/config/google-ads.yaml
python3 /data/workspace/scripts/fetch_google_ads.py 6329354566 2026-02-18 2026-02-24

# Generate report
python3 /data/workspace/scripts/generate_report.py /tmp/google_ads_data_6329354566_*.json dental_artistry

# Full workflow
/data/workspace/scripts/generate_weekly_report.sh 6329354566

# Check cron jobs
openclaw cron list
```

### Clover Commands

```bash
# Review latest report
cat /data/workspace/reports/report_6329354566_*.txt

# Fetch for strategic analysis
export GOOGLE_ADS_CONFIGURATION_FILE_PATH=/data/workspace/config/google-ads.yaml
python3 /data/workspace/scripts/fetch_google_ads.py <account> <start> <end>
```

---

## Success Metrics

### OpenClaw (Data Operations)
- ✅ Reports generated on time (Thursdays 5 AM)
- ✅ Zero missed data fetches
- ✅ API uptime > 99%
- ✅ Accurate data delivery

### Clover (Strategic Analysis)
- ✅ Actionable insights provided
- ✅ Campaign optimizations identified
- ✅ Client communication clear
- ✅ Strategic recommendations implemented

---

**Effective Date:** 2026-02-27  
**Defined by:** Sean (Owner)  
**Roles:** OpenClaw (Data) + Clover (Strategy)

# Complete System Enhancement Plan
## Plugins, UI, Database & Implementation Roadmap

**Prepared by:** Clover 🍀  
**Date:** 2026-02-27  
**For:** Sean - Team Lead, UNI Marketing Agency

---

## 🎯 OVERVIEW

This document consolidates three major enhancement areas:
1. **OpenClaw Plugins** — Functionality extensions
2. **UI & Visualization** — Agent monitoring & dashboards
3. **Supabase Database** — Data pipeline & storage

---

## PART 1: OPENCLAW PLUGINS RESEARCH

### Plugin System Architecture

OpenClaw has two extension mechanisms:
1. **Skills** — Python/JavaScript scripts in `/opt/openclaw/app/skills/`
2. **Plugins** — Channel integrations and system extensions

### Available Built-in Skills

| Skill | Purpose | Status | Recommendation |
|-------|---------|--------|----------------|
| `healthcheck` | Security audits & hardening | ✅ Available | **HIGH** - Use for VPS security |
| `canvas` | Visual dashboards & presentations | ✅ Available | **HIGH** - Use for client reports |
| `github` | GitHub repo/issue management | ✅ Available | MEDIUM - If doing dev work |
| `openai-image-gen` | DALL-E image generation | ✅ Available | MEDIUM - For ad creatives |
| `openai-whisper-api` | Audio transcription | ✅ Available | LOW - Unless doing podcasts |
| `summarize` | Text summarization | ✅ Available | MEDIUM - For research |
| `sag` | ElevenLabs TTS | ✅ Available | LOW - Unless doing voice |
| `slack` | Slack reactions/pins | ✅ Available | HIGH - Already using |
| `weather` | Weather forecasts | ✅ Available | LOW - Not core need |

### Recommended Skill Installation

```bash
# Already available, just need to use them
# Skills are auto-discovered from /opt/openclaw/app/skills/

# To use a skill, reference it in prompts:
"Use the canvas skill to display this report visually"
"Run healthcheck audit on the VPS"
"Use github skill to check repository status"
```

### MCP (Model Context Protocol) Integrations

**What is MCP?**
- Protocol for connecting AI agents to external data sources
- Allows agents to query databases, APIs, files
- Similar to plugins but more flexible

**Available MCP Servers:**

| MCP Server | Purpose | Status |
|------------|---------|--------|
| **Supabase MCP** | Database queries | 🔧 In development |
| **Google Ads MCP** | Ad platform access | ❌ Not available |
| **Browser MCP** | Web browsing | ✅ Via built-in browser |
| **File System MCP** | Local file access | ✅ Built-in |
| **GitHub MCP** | Repo management | ✅ Via github skill |

**Our Implementation:**
- Kimi proposed Supabase MCP for task queue
- Could extend for real-time database queries
- Priority: MEDIUM (nice-to-have, not critical)

---

## PART 2: UI & VISUALIZATION OPTIONS

### Recommended Approach: Phased Implementation

#### Phase 1: Canvas Dashboard (Today - 30 min setup)

**What:** Built-in HTML display system
**Use for:** Quick status monitoring

**Implementation:**
```bash
# Create dashboard HTML
mkdir -p ~/clawd/canvas
cat > ~/clawd/canvas/mission-control.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>UNI Mission Control</title>
  <meta http-equiv="refresh" content="30">
  <style>
    body { font-family: system-ui; background: #0a0a0a; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 20px; border-radius: 12px; margin: 10px 0; }
    .status-online { color: #00d26a; }
    .status-offline { color: #ff4747; }
    .status-working { color: #ffb800; }
  </style>
</head>
<body>
  <h1>🎯 UNI Mission Control</h1>
  <div class="card">
    <h3>Active Agents</h3>
    <p class="status-online">● Clover 🍀 - Online</p>
    <p class="status-working">● OpenClaw 🛡️ - Working</p>
    <p class="status-online">● Kimi 🧪 - Online</p>
  </div>
  <div class="card">
    <h3>Today's Performance</h3>
    <p>Dental Artistry: 44 conversions @ $48 CPL</p>
    <p>Lumiere Dental: 21 conversions @ $36 CPL</p>
  </div>
</body>
</html>
EOF

# Display on any device
# Access via: http://your-vps:18793/__openclaw__/canvas/mission-control.html
```

**Pros:**
- ✅ Built-in (no install)
- ✅ Works immediately
- ✅ Auto-refresh
- ✅ Display on phone/tablet/Mac

**Cons:**
- ⚠️ Basic HTML (not fancy)
- ⚠️ Static data (unless automated)

#### Phase 2: React + Supabase Dashboard (Next week - 4-6 hours)

**What:** Full-featured dashboard with real-time data
**Use for:** Production monitoring, client presentations

**Features:**
- Real-time charts (Chart.js)
- Agent status with pulsing indicators
- Campaign performance tables
- Alert feed
- Historical trends

**Tech Stack:**
- React (frontend)
- Supabase (backend + real-time)
- Recharts (visualization)
- Deploy: Static hosting (Netlify/Vercel)

**Cost:** Free tier sufficient

#### Phase 3: Grafana (Future - if needed)

**What:** Enterprise metrics dashboard
**Use for:** Advanced monitoring, alerts, team scale

**When to use:**
- 10+ accounts
- Complex alerting needs
- Team of 5+ people
- Compliance requirements

---

## PART 3: SUPABASE DATABASE DESIGN

### Complete Schema Overview

```
clients
├── ad_accounts (Google Ads, Meta, etc.)
│   ├── campaigns
│   ├── performance_hourly
│   ├── performance_daily
│   └── search_terms
├── alerts
└── data_sync_log

agent_tasks (cross-agent coordination)
```

### Key Tables

#### 1. clients
```sql
- id, client_name, brand_owner_name, industry
- business_type (lead_gen/ecommerce)
- status (active/paused/churned)
```

#### 2. ad_accounts
```sql
- client_id (foreign key)
- platform (google_ads/meta_ads/tiktok/linkedin)
- account_id, account_name
- daily_budget, monthly_budget
- target_cpa, target_roas
```

#### 3. performance_hourly
```sql
- ad_account_id, campaign_id
- timestamp, date, hour
- impressions, clicks, spend, conversions, conversion_value
- CTR, CPC, CPA, ROAS (calculated)
```

#### 4. performance_daily
```sql
- Same as hourly but aggregated by day
- Permanent storage (2 years)
- Budget utilization tracking
```

#### 5. search_terms
```sql
- ad_account_id, date, search_term
- impressions, clicks, spend, conversions
- category (high_performer/wasted_spend/opportunity)
```

#### 6. agent_tasks (Kimi's proposal)
```sql
- from_agent, to_agent, task_type
- priority, payload, status, result
- created_at, claimed_at, completed_at
```

#### 7. alerts
```sql
- ad_account_id, alert_type
- severity (info/warning/critical)
- title, description, metric_value, threshold_value
- status (open/acknowledged/resolved)
```

### Data Pull Strategy

| Data Type | Frequency | Retention | Storage/Day |
|-----------|-----------|-----------|-------------|
| Hourly metrics | Every hour | 7 days | ~5 KB/account |
| Daily metrics | Daily 6 AM | 2 years | ~150 bytes/account |
| Search terms | Daily 6 AM | 90 days | ~5 KB/account |
| Campaign metadata | Daily | Current only | Minimal |
| Agent tasks | Real-time | 30 days | Minimal |
| Alerts | On trigger | 90 days | Minimal |

### What We Can Track ✅

**Google Ads (Available):**
- Impressions, clicks, spend
- Conversions, conversion value
- CTR, CPC, CPA, ROAS
- Campaign names, budgets, status
- Search terms (top performers)
- Quality Score (campaign level)
- Device/geo breakdown (if needed)

**Agent Operations:**
- Task assignments
- Execution status
- Errors and results

### What We Cannot Track ❌

**Google Ads Limitations:**
- Real-time data (< 1 hour delay)
- Individual user data (privacy)
- Competitor metrics
- Organic search (need Search Console)
- Cross-platform attribution

**Technical Constraints:**
- View-through conversions (limited API)
- Attribution paths (complex)
- CRM integration (unless API available)

---

## PART 4: IMPLEMENTATION ROADMAP

### Week 1: Foundation

**Day 1-2: Database Setup**
- [ ] Deploy Supabase schema
- [ ] Configure RLS policies
- [ ] Set up service account keys
- [ ] Test connection from VPS

**Day 3-4: Data Pipeline**
- [ ] Build sync script (`sync_google_ads.py`)
- [ ] Test hourly pull
- [ ] Test daily pull
- [ ] Verify data accuracy

**Day 5: Automation**
- [ ] Set up cron jobs
- [ ] Configure error alerting
- [ ] Document runbook

### Week 2: Dashboard

**Day 1-2: Frontend Setup**
- [ ] Create React app
- [ ] Connect to Supabase
- [ ] Build layout framework

**Day 3-4: Visualizations**
- [ ] Agent status cards
- [ ] Performance charts
- [ ] Campaign tables
- [ ] Alert feed

**Day 5: Polish**
- [ ] Auto-refresh
- [ ] Mobile responsive
- [ ] Deploy to hosting

### Week 3: Advanced Features

- [ ] Anomaly detection
- [ ] Automated alerts to Slack
- [ ] Weekly report generation
- [ ] Data export (CSV/PDF)

### Week 4: Scale

- [ ] Add more clients
- [ ] Optimize queries
- [ ] Team training
- [ ] Documentation

---

## PART 5: COST ESTIMATES

### Supabase (Database)

| Tier | Cost | Limits | Our Usage |
|------|------|--------|-----------|
| **Free** | $0 | 500 MB, 2M requests/month | ✅ Sufficient for 2-10 accounts |
| Pro | $25/mo | 8 GB, 100M requests | If we scale to 50+ accounts |

**Recommendation:** Start with Free tier

### Dashboard Hosting

| Option | Cost | Best For |
|--------|------|----------|
| **Vercel** | $0 | React apps, serverless |
| **Netlify** | $0 | Static sites, forms |
| Coolify (self) | $0 | Already have VPS |

**Recommendation:** Deploy on existing Coolify instance

### Total Monthly Cost

| Component | Cost |
|-----------|------|
| Supabase | $0 (free tier) |
| Dashboard hosting | $0 (Coolify) |
| Google Ads API | $0 (standard access) |
| **TOTAL** | **$0/month** |

---

## PART 6: IMMEDIATE NEXT STEPS

### Today (Next 2 Hours)

1. **Review this plan** — Any changes needed?
2. **Deploy Supabase schema** — Copy SQL, execute
3. **Set up Canvas dashboard** — 30 min, instant visibility
4. **Test agent spawning** — Verify OpenClaw can be spawned

### This Week

1. Build and test sync scripts
2. Create basic React dashboard
3. Set up automated hourly pulls
4. Document the system

### Next Week

1. Polish dashboard
2. Add anomaly detection
3. Train team on usage
4. Plan for additional clients

---

## 📁 FILES CREATED

| File | Purpose |
|------|---------|
| `/data/workspace/supabase/schema.sql` | Complete database schema |
| `/data/workspace/supabase/implementation-guide.md` | Detailed implementation steps |
| `/data/workspace/docs/ui-visualization-options.md` | Dashboard options research |
| `/data/workspace/docs/agent-communication-options.md` | Agent comms research |
| This file | Master plan & summary |

---

## 🎯 RECOMMENDED PRIORITY

### Do First (High Impact, Low Effort)
1. ✅ Deploy Supabase schema (1 hour)
2. ✅ Set up Canvas dashboard (30 min)
3. ✅ Test hourly data pulls (2 hours)

### Do Next (High Impact, Medium Effort)
4. Build React dashboard (1 week)
5. Add anomaly detection (2-3 days)
6. Automate weekly reports (1 day)

### Do Later (Nice to Have)
7. Grafana integration (if scale requires)
8. Advanced MCP integrations
9. Mobile app

---

**Ready to start with Phase 1?** I can deploy the Supabase schema and set up the Canvas dashboard right now.

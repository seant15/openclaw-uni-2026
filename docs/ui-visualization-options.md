# OpenClaw UI & Agent Visualization Options
## Low-Investment Solutions for Agent Monitoring

**Date:** 2026-02-27  
**Requested by:** Sean  
**Research by:** Clover 🍀

---

## 🎯 REQUIREMENTS

- Visual agent monitoring (see agents working)
- Mission control / dashboard view
- Low investment (time + cost)
- Easy to set up
- Real-time or near real-time

---

## OPTION 1: OpenClaw Canvas (Built-in) ⭐ RECOMMENDED

### What It Is
Built-in HTML presentation system for visual dashboards and reports.

### Capabilities
- Display HTML dashboards on connected devices
- Real-time updates via WebSocket
- Support for charts (Chart.js, D3.js)
- Multi-device sync (Mac, iOS, Android)

### How to Use

```bash
# Create dashboard HTML
mkdir -p ~/clawd/canvas
cat > ~/clawd/canvas/agent-dashboard.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
  <title>UNI Agent Dashboard</title>
  <meta http-equiv="refresh" content="30">
  <style>
    body { font-family: system-ui; background: #0a0a0a; color: #fff; padding: 20px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
    .card { background: #1a1a1a; padding: 20px; border-radius: 12px; }
    .status-green { color: #00d26a; }
    .status-yellow { color: #ffb800; }
    .status-red { color: #ff4747; }
  </style>
</head>
<body>
  <h1>🛡️ OpenClaw Agent Monitor</h1>
  <div class="grid">
    <div class="card">
      <h3>OpenClaw 🛡️</h3>
      <p class="status-green">● Active</p>
      <p>Last fetch: 5 min ago</p>
    </div>
    <div class="card">
      <h3>Clover 🍀</h3>
      <p class="status-green">● Active</p>
      <p>Strategy mode</p>
    </div>
    <div class="card">
      <h3>Google Ads API</h3>
      <p class="status-green">● Connected</p>
      <p>44 conversions today</p>
    </div>
  </div>
</body>
</html>
HTML

# Present on a device
canvas action:present node:<device-id> target:http://<host>:18793/__openclaw__/canvas/agent-dashboard.html
```

### Pros
- ✅ Built into OpenClaw (no extra install)
- ✅ Works with any HTML/JS
- ✅ Real-time refresh
- ✅ Multiple devices

### Cons
- ⚠️ Requires connected device (phone/tablet/Mac)
- ⚠️ Basic UI (not a full dashboard)

**Best for:** Simple status displays, report visualization

---

## OPTION 2: Custom Dashboard with Canvas + Auto-Refresh

### What to Build
A marketing dashboard showing:
- Agent status (online/offline)
- Active tasks
- Recent reports
- Google Ads metrics
- System health

### Implementation

```html
<!-- ~/clawd/canvas/mission-control.html -->
<!DOCTYPE html>
<html>
<head>
  <title>UNI Mission Control</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, system-ui; 
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #fff; 
      min-height: 100vh;
    }
    .header { padding: 20px; background: rgba(0,0,0,0.3); }
    .grid { 
      display: grid; 
      grid-template-columns: 250px 1fr 300px;
      gap: 20px; 
      padding: 20px;
    }
    .sidebar { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; }
    .main { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; }
    .agent { 
      display: flex; 
      align-items: center; 
      gap: 10px; 
      padding: 10px;
      margin: 5px 0;
      border-radius: 8px;
      background: rgba(255,255,255,0.03);
    }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; }
    .online { background: #00d26a; box-shadow: 0 0 10px #00d26a; }
    .offline { background: #ff4747; }
    .working { background: #ffb800; animation: pulse 1s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎯 UNI Marketing Mission Control</h1>
    <p id="timestamp">Last updated: Loading...</p>
  </div>
  
  <div class="grid">
    <div class="sidebar">
      <h3>🤖 Active Agents</h3>
      <div id="agents">
        <div class="agent">
          <div class="status-dot online"></div>
          <span>Clover 🍀</span>
        </div>
        <div class="agent">
          <div class="status-dot working"></div>
          <span>OpenClaw 🛡️</span>
        </div>
        <div class="agent">
          <div class="status-dot online"></div>
          <span>Kimi 🧪</span>
        </div>
      </div>
    </div>
    
    <div class="main">
      <h3>📊 Today's Performance</h3>
      <canvas id="metricsChart"></canvas>
    </div>
    
    <div class="sidebar">
      <h3>📝 Recent Activity</h3>
      <ul id="activity">
        <li>Report generated: Dental Artistry</li>
        <li>Agent spawned: OpenClaw</li>
        <li>Data fetched: 44 conversions</li>
      </ul>
    </div>
  </div>
  
  <script>
    // Auto-refresh every 30 seconds
    setInterval(() => {
      location.reload();
    }, 30000);
    
    // Update timestamp
    document.getElementById('timestamp').textContent = 
      'Last updated: ' + new Date().toLocaleString();
    
    // Simple chart
    const ctx = document.getElementById('metricsChart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Conversions',
          data: [12, 19, 15, 25, 22, 30, 28],
          borderColor: '#00d26a',
          backgroundColor: 'rgba(0, 210, 106, 0.1)',
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#fff' } } },
        scales: {
          x: { ticks: { color: '#fff' } },
          y: { ticks: { color: '#fff' } }
        }
      }
    });
  </script>
</body>
</html>
```

### Data Source
Agents write status to a JSON file:
```python
# OpenClaw writes status after each task
import json
from datetime import datetime

status = {
    "agent": "openclaw",
    "status": "working",  # online/offline/working
    "task": "google_ads_report",
    "last_active": datetime.now().isoformat(),
    "metrics": {
        "conversions": 44,
        "spend": 2179.89
    }
}

with open('/data/workspace/dashboard/agent_status.json', 'a') as f:
    json.dump(status, f)
    f.write('\n')
```

### Pros
- ✅ Full control over design
- ✅ Charts and visualizations
- ✅ Auto-refresh
- ✅ No external dependencies

### Cons
- ⚠️ Need to build HTML/CSS/JS
- ⚠️ Manual data updates (unless automated)

**Best for:** Custom marketing dashboard

---

## OPTION 3: Supabase + Simple React Dashboard

### What to Build
Lightweight React dashboard using Supabase as backend.

### Components
1. **Supabase** — Data storage
2. **React** — Frontend (can be static)
3. **Recharts** — Charts
4. **OpenClaw** — Writes data to Supabase

### Architecture
```
OpenClaw → Supabase (agent_tasks, metrics)
                ↓
         React Dashboard (reads data)
                ↓
         Browser Display
```

### Implementation Effort
- **Backend:** Use existing Supabase schema
- **Frontend:** ~2-3 hours to build basic dashboard
- **Data flow:** OpenClaw writes via MCP

### Pros
- ✅ Persistent data
- ✅ Real-time subscriptions
- ✅ Historical tracking
- ✅ Professional look

### Cons
- ⚠️ Need to build React app
- ⚠️ More complex setup

**Best for:** Production dashboard with history

---

## OPTION 4: n8n or Tooljet (No-Code)

### What They Are
No-code workflow builders with dashboard capabilities.

### n8n (Self-hosted, free)
- Visual workflow builder
- Dashboard widgets
- Database connections
- Webhook triggers

### Tooljet (Open source)
- Drag-and-drop dashboard builder
- Database integrations
- User authentication
- Real-time updates

### Implementation
```
OpenClaw → Webhook → n8n/Tooljet → Dashboard
```

### Pros
- ✅ No coding required
- ✅ Visual builder
- ✅ Lots of integrations

### Cons
- ⚠️ Another service to host
- ⚠️ Learning curve
- ⚠️ Overkill for simple needs

**Best for:** Complex workflows without coding

---

## OPTION 5: Grafana (Metrics Visualization)

### What It Is
Industry-standard metrics dashboard (open source).

### Setup
```yaml
# docker-compose.yml
version: '3'
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana
  
  # Supabase provides PostgreSQL for data source
```

### Pros
- ✅ Professional dashboards
- ✅ Alerts and notifications
- ✅ Lots of plugins
- ✅ Time-series optimized

### Cons
- ⚠️ Requires setup
- ⚠️ More ops overhead

**Best for:** Serious metrics monitoring

---

## 🎯 RECOMMENDATION

### Phase 1: Quick Win (Today)
**Use OpenClaw Canvas** with auto-refresh HTML dashboard
- Build simple mission control in 30 minutes
- Display on tablet/old phone
- Show agent status + key metrics

### Phase 2: Production (Next Week)
**Supabase + React Dashboard**
- Persistent data storage
- Historical trends
- Real-time updates
- Professional presentation

### Phase 3: Scale (Future)
**Grafana** for advanced metrics
- If you need serious monitoring
- Time-series analysis
- Enterprise features

---

## 📋 IMPLEMENTATION PLAN

### Today (1 hour)
1. Create Canvas dashboard HTML
2. Set up auto-refresh
3. Display on phone/tablet

### Next Week (4-6 hours)
1. Build Supabase schema for metrics
2. Create React dashboard
3. Connect OpenClaw to write data
4. Deploy static dashboard

### Future
1. Evaluate Grafana if needed
2. Add more visualizations
3. Mobile app consideration

---

## FILES TO CREATE

```
~/clawd/canvas/
├── mission-control.html     # Main dashboard
├── agent-status.html        # Agent monitor
├── reports.html            # Report viewer
└── assets/
    ├── styles.css
    └── charts.js
```

---

**Ready to build the dashboard?** Start with Option 1 (Canvas) today, then upgrade to Option 3 (React) next week.

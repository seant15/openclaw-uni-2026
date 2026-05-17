# OpenClaw Setup Lessons Learned
*A comprehensive analysis of our VPS deployment journey*

## 🎯 Original Goal
Deploy OpenClaw on Coolify VPS with:
- Custom domain access (`https://open.unippc24.com`)
- Slack integration 
- Secure HTTPS web interface
- Agent identity as "Clover 🍀"

## 🔍 Critical Mistakes & Analysis

### 1. **Architectural Misunderstanding** (High Impact)

**❌ What We Did Wrong:**
- Didn't map out the full OpenClaw architecture upfront
- Assumed Coolify proxy worked like standard reverse proxies
- Mixed up internal vs external port mappings

**✅ What We Should Have Done:**
```
STEP 1: Architecture Discovery
┌─────────────────────────────────────┐
│ Internet → Coolify Proxy (port 443) │
│     ↓                               │
│ Container → nginx (port 9090)       │
│     ↓                               │  
│ OpenClaw Gateway (port 18789)       │
└─────────────────────────────────────┘
```

**🎓 Lesson:** Always diagram the full request flow before making changes.

### 2. **Incremental Fixes Without Root Cause Analysis** (High Impact)

**❌ Pattern of Mistakes:**
- Applied quick header fixes instead of understanding SSL requirements
- Switched auth modes without understanding pairing system
- Changed ports without understanding Docker Compose mapping

**Example - The Nginx Header Fix Attempt:**
```nginx
# Wrong approach - treating symptoms
proxy_set_header X-Forwarded-Proto https;
```

**✅ Right Approach:**
```nginx
# Address root cause - SSL not configured
listen 9090 ssl;
ssl_certificate /path/to/cert;
ssl_certificate_key /path/to/key;
```

**🎓 Lesson:** Always ask "Why is this happening?" before applying fixes.

### 3. **Multiple Simultaneous Changes** (Medium Impact)

**❌ What We Did:**
Day 1: Changed agent name + Slack pairing + port configuration simultaneously

**💥 Impact:**
- UI lockout (session key mismatch)
- Couldn't isolate which change broke what
- Complex rollback requirements

**✅ Better Approach:**
```
Change 1: Set up Slack webhook (test)
Change 2: Configure HTTPS access (test) 
Change 3: Update agent identity (test)
```

**🎓 Lesson:** One change at a time, test thoroughly.

### 4. **Configuration State Management** (Medium Impact)

**❌ Issues Encountered:**
- Agent name changes reverting unexpectedly
- SSL configuration getting lost between nginx reloads
- Auth mode changes not persisting after gateway restarts

**✅ Solution Pattern:**
```bash
# Before ANY config change:
1. Backup current config
2. Document current state  
3. Test change
4. Verify persistence after restart
5. Document new state
```

## 🛠️ OpenClaw-Specific Setup Guide

### Phase 1: Infrastructure Assessment
```bash
# 1. Map the architecture
ps aux | grep openclaw
ss -tlnp | grep -E ":90|:443|:18789"
docker ps (if applicable)

# 2. Understand current routing
curl -I http://localhost:9090
curl -I http://localhost:18789  
curl -I https://yourdomain.com

# 3. Check configuration structure
openclaw config get agents
openclaw config get gateway.auth
ls -la /etc/nginx/conf.d/
```

### Phase 2: Systematic Setup Order
```
Step 1: Fix basic HTTP access first
Step 2: Set up SSL/HTTPS properly  
Step 3: Configure authentication/pairing
Step 4: Set up integrations (Slack, etc.)
Step 5: Customize agent identity
```

### Phase 3: OpenClaw-Coolify Integration Points

**Critical Configuration Files:**
```
/etc/nginx/conf.d/openclaw.conf     # Proxy configuration
/data/.openclaw/openclaw.json       # OpenClaw main config
/data/.openclaw/devices/paired.json # Device pairing
```

**Environment Variables (Coolify):**
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=xapp-...  
OPENCLAW_GATEWAY_PORT=18789 (internal)
PORT=9090 (nginx proxy port)
```

## 🔧 Proven Solutions

### SSL Setup for OpenClaw
```nginx
server {
    listen 9090 ssl default_server;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/domain.crt;
    ssl_certificate_key /etc/ssl/private/domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://127.0.0.1:18789$uri?$ocw_proxy_args;
        proxy_set_header Authorization "Bearer uni-random-token";
        # ... standard proxy headers
    }
}
```

### Slack Integration (HTTP Webhooks)
```json
{
  "channels": {
    "slack": {
      "mode": "http", 
      "config": {
        "botToken": "$SLACK_BOT_TOKEN",
        "signingSecret": "$SLACK_SIGNING_SECRET"
      }
    }
  }
}
```

**Webhook URL:** `https://yourdomain.com:9090/webhook/slack`

### Device Pairing Management
```bash
# Check pending pairings
cat /data/.openclaw/devices/pending.json

# Manual approval (when CLI fails)
python3 -c "
import json, time
# [pairing approval script from our session]
"
```

## 🚨 Critical Gotchas

### 1. **Agent Name vs Session Key Mismatch**
- Changing agent name from "Atlas" → "Clover" breaks existing sessions
- Session key remains `agent:atlas:main` even after name change
- **Fix:** Either update session routing or create new Clover sessions

### 2. **Coolify Port Mapping**
- Docker Compose: `${PORT}:${PORT}` creates same internal/external ports
- But OpenClaw Gateway runs on 18789, nginx on 9090
- **Fix:** Understand the internal architecture first

### 3. **OpenClaw Authentication Modes**
- `token` mode: Device pairing required
- `password` mode: Simple password auth
- Config changes require gateway restart to take effect

### 4. **Slack Webhook Paths**  
- Correct path: `/webhook/slack` (not `/slack/events`)
- Must be HTTP mode, not Socket mode for webhooks
- Requires proper HTTPS setup for production

## 🎯 Success Metrics & Validation

### Working State Checklist:
```bash
✅ https://domain.com:9090/chat loads without errors
✅ Slack webhook responds to: https://domain.com:9090/webhook/slack  
✅ Agent identity shows as "Clover 🍀" 
✅ Device pairing works smoothly
✅ All integrations functional
```

### Testing Protocol:
```bash
# 1. Basic connectivity
curl -k -I https://domain.com:9090

# 2. Slack webhook
curl -X POST https://domain.com:9090/webhook/slack \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'

# 3. Web interface  
# Access in browser, verify no pairing/SSL errors

# 4. Agent identity
openclaw config get agents.list.0.name
```

## 💡 Future Improvement Areas

### 1. **Monitoring & Observability**
- Set up health check endpoints
- Monitor SSL certificate expiration
- Track device pairing attempts

### 2. **Configuration Management**  
- Version control for nginx configs
- Automated backups before changes
- Configuration drift detection

### 3. **Documentation**
- Keep architecture diagrams updated
- Document all custom configurations
- Maintain troubleshooting runbook

## 🤝 Team Working Improvements

### For Future Deployments:
1. **Pre-flight Planning:** Map architecture before touching configs
2. **Change Management:** One change, test, document, repeat
3. **State Tracking:** Always know current state before/after changes
4. **Rollback Planning:** Have backups and rollback procedures ready

### For Troubleshooting:
1. **Logs First:** Check OpenClaw logs, nginx logs, system logs
2. **Network Flow:** Trace request path through all components  
3. **Configuration Verification:** Compare intended vs actual configs
4. **Systematic Testing:** Test each layer independently

---

*This analysis makes us stronger by turning experience into repeatable knowledge.* 🍀
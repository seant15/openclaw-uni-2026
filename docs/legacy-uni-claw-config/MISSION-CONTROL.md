# 🎛️ MISSION CONTROL - Setup Guide

## Current Status: ✅ OPERATIONAL

Your OpenClaw Mission Control is already well-configured and running optimally!

### 📊 **Dashboard Access**
- **URL**: http://127.0.0.1:18789/
- **Status**: Active and accessible
- **Security**: Token-based auth with trusted proxy configuration

### 🤖 **Agents Configuration**
- **Primary Agent**: Clover 🍀 (atlas) - Claude Sonnet 4
- **Fallback Agents**: Relay, Sentinel, Nexus (GPT-4o-mini)
- **Workspace**: `/data/workspace` 
- **Context**: 32k tokens with 10 max concurrent

### 🔗 **Integrations**
- **Slack**: ✅ Fully configured and operational
- **Browser Control**: ✅ Enabled with CDP access
- **Memory System**: ✅ Vector search + FTS ready
- **Web Tools**: ✅ Search and fetch capabilities

### 🛡️ **Security Configuration**
- **Auth Mode**: Token-based (`uni-random-token`)
- **Trusted Networks**: Local + private ranges configured
- **Control UI**: Multiple origin allowlist for flexibility

## 🚀 **Mission Control Features**

### **Real-time Agent Management**
- Monitor all 4 agents (atlas, relay, sentinel, nexus)
- Switch between agents for different tasks
- View session history and token usage

### **Channel Integrations**
- Slack workspace fully connected
- Multi-channel message routing
- Group chat participation with smart response logic

### **Browser Automation**
- Web search via Brave API
- Page content extraction
- Full browser control for complex tasks

### **Memory & Context**
- Persistent memory across sessions
- Vector-based semantic search
- Daily memory logs and long-term memory curation

## 🔧 **Optimization Recommendations**

### **1. Enhanced Security (Optional)**
```bash
# Strengthen gateway token
openclaw config set gateway.auth.token $(openssl rand -hex 32)

# Fix credentials permissions  
chmod 700 /data/.openclaw/credentials
```

### **2. Performance Tuning**
```bash
# Enable more concurrent sessions if needed
openclaw config set agents.defaults.maxConcurrent 15
openclaw config set agents.defaults.subagents.maxConcurrent 30
```

### **3. Additional Channels**
Add more communication channels via the config wizard:
```bash
openclaw config --section Channels
```

## 📱 **Mission Control Interface**

### **Dashboard Sections**
1. **Agents Overview** - Status, model, sessions
2. **Channel Status** - Connected services and health
3. **Session Management** - Active conversations and history  
4. **System Resources** - Memory, tokens, performance
5. **Configuration** - Real-time settings adjustment

### **Quick Actions**
- Start/stop agents
- View session transcripts  
- Monitor resource usage
- Configure channel settings
- Run system diagnostics

## 🎯 **Mission Control Best Practices**

### **Daily Operations**
1. Check dashboard health indicators
2. Review active sessions and resource usage
3. Monitor channel connectivity status
4. Review memory and context utilization

### **Maintenance Tasks**
- Weekly: Review and clean old sessions
- Monthly: Update agent configurations 
- As needed: Backup workspace and config files

### **Emergency Procedures**
```bash
# Full system status
openclaw status --deep

# Restart gateway if needed
openclaw gateway restart

# Emergency diagnostics
openclaw doctor --fix
```

## 🌟 **Advanced Capabilities**

Your Mission Control supports:
- **Multi-agent orchestration** via subagent spawning
- **Cross-session messaging** for complex workflows  
- **Persistent memory** with semantic search
- **Real-time browser automation** for web tasks
- **Integrated communication** across multiple platforms

---

## 📞 **Access Your Mission Control**

**Primary Interface**: http://127.0.0.1:18789/  
**Agent**: Clover 🍀 (atlas) - Your strategic partner  
**Status**: Fully operational and ready for mission-critical tasks

---

*Mission Control is your central command center for all OpenClaw operations. Use it to monitor, manage, and orchestrate your AI-powered workflows.*
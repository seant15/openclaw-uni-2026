# UNI Marketing Multi-Agent System Architecture

## System Overview
A sophisticated, role-specific agent ecosystem for performance marketing operations.

### Agents

#### 1. Strategist (Becky)
- **Role:** Strategic Analysis
- **Model:** Claude Sonnet
- **Primary Functions:**
  - Client performance data analysis
  - Weekly strategy brief generation
  - Performance trend investigation

#### 2. Ops Bot (Casey)
- **Role:** Task & Team Coordination
- **Model:** GPT-4o Mini/GPT-4o
- **Primary Functions:**
  - Task management
  - Team workflow coordination
  - Client context retrieval

#### 3. Watchdog (David)
- **Role:** Performance Monitoring
- **Models:** 
  - Sync: GPT-4o Mini
  - Analysis: Claude 3.5 Haiku
- **Primary Functions:**
  - Real-time performance tracking
  - Anomaly detection
  - Automated alerting

#### 4. Gatekeeper (Frank)
- **Role:** Database Administration
- **Model:** GPT-4o Mini
- **Primary Functions:**
  - Client onboarding
  - Database management
  - Integration configuration

## Communication Protocols
- Centralized data access via Supabase views
- Standardized JSON messaging
- Error handling and logging
- Slack notification integration

## Deployment Status
- Current Blockers: Agent ID configuration
- Next Steps: Resolve OpenClaw multi-agent support

## Troubleshooting Notes
- Verify OpenClaw version
- Check agent configuration settings
- Potential support request required

---

_Architecture subject to iterative improvement_
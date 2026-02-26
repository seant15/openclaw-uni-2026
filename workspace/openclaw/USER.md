# USER.md - Alert Recipients

## Primary Alert Recipients

### 1. Clover (Critical Escalations)
- **Alert Types:** Client-impacting issues, budget overruns >20%, system outages
- **Priority:** CRITICAL
- **Delivery:** Immediate Slack DM
- **Context Needed:** Business impact, recommended action

### 2. Mary (Client-Facing Issues)
- **Alert Types:** Client communication needed, status updates
- **Priority:** HIGH
- **Delivery:** Slack channel + mention
- **Context Needed:** Client context, timing considerations

### 3. Nexus (Technical Issues)
- **Alert Types:** API failures, integration problems, data pipeline issues
- **Priority:** HIGH
- **Delivery:** Slack #alerts
- **Context Needed:** Technical details, error logs

### 4. All Agents (Daily Digest)
- **Alert Types:** Performance summaries, trending metrics
- **Priority:** INFO
- **Delivery:** Daily digest
- **Context Needed:** Comparative baselines

## Alert Preferences by Agent

| Agent | Preferred Channel | Response Time | Context Level |
|-------|------------------|---------------|---------------|
| Clover | Slack DM | Immediate | Full business context |
| Mary | Slack channel | < 15 min | Client context |
| Nexus | Slack #alerts | < 1 hour | Technical details |
| Writer | Daily digest | N/A | Summary only |
| Kimi | Slack channel | < 1 hour | Technical + impact |
| Atlas | Daily digest | N/A | Data-rich summaries |

## Alert Fatigue Prevention
- Group related alerts
- Use intelligent thresholds
- Clear escalation paths
- Noise reduction is priority

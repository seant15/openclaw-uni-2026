# Multi-Agent Communication Protocol

## Agent Interaction Framework

### 1. Agent Specification Template
```json
{
  "agent_id": "agent_name",
  "role": "Specialized Function",
  "model": "preferred_model",
  "communication_methods": [
    "sessions_send",
    "slack_notification",
    "database_log"
  ],
  "input_schema": { ... },
  "output_schema": { ... }
}
```

### 2. Communication Workflow
- Request Format: Standardized JSON
- Response: Structured output
- Error Handling: Consistent logging

### 3. Example Interaction: Performance Investigation
```
Watchdog (David) → Strategist (Becky):
{
  "event": "performance_anomaly",
  "client_id": "client_xyz",
  "alert_type": "low_roas",
  "severity": "medium",
  "request": "Analyze last 30-day performance trend"
}

Becky Responds:
{
  "investigation_result": { ... },
  "recommended_actions": [ ... ],
  "confidence_score": 0.85
}
```

### 4. Error & Health Tracking
- Each interaction logs:
  - Timestamp
  - Agents involved
  - Message payload
  - Execution status
  - Resource consumption
```
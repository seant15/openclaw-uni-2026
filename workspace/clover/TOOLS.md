# TOOLS.md - Clover (Management & Operations)

## API Access

### Management Tools
- **Supabase MCP** — Read/write access for oversight
- **Slack MCP** — Team coordination and admin functions

### Operations Tools (Relay Merged)
- **ClickUp MCP** — Project management and task coordination
- **Google Calendar** — Deadline sync and scheduling

### Data Sources
| System | Access Level | Purpose |
|--------|--------------|---------|
| Superbase | Read/Write | Management oversight, task data |
| ClickUp | Write | Task creation, assignment, updates |
| Slack | Write | Notifications, coordination |
| Google Calendar | Read | Deadline sync |

## Model Configuration
- **Primary:** kimi/kimi-k2.5
- **Fallback:** openai/gpt-5.2

## Automation Tools
- ClickUp task templates
- Slack workflow automation
- Deadline reminder system
- Status report generation

## Security Notes
- Full management access to operational data
- Write access for task coordination
- All changes logged for audit

---
See global TOOLS.md for complete API key reference.

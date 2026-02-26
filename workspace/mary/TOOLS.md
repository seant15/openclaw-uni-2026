# TOOLS.md - API Keys & Environment Setup

## Model Provider APIs

| Provider | Env Var | Status | Purpose |
|----------|---------|--------|---------|
| **Kimi (Moonshot)** | `KIMI_API_KEY` | ✅ Active | Primary LLM for all agents |
| **OpenAI** | `OPENAI_API_KEY` | ✅ Available | Fallback models |
| **Anthropic** | `ANTHROPIC_API_KEY` | ✅ Available | Fallback models |

## Platform APIs

| Platform | Env Var | Purpose | Agent |
|----------|---------|---------|-------|
| **Slack Bot** | `SLACK_BOT_TOKEN` | Messaging | All |
| **Slack App** | `SLACK_APP_TOKEN` | Events | All |
| **Slack Signing** | `SLACK_SIGNING_SECRET` | Verification | All |

### Advertising
| **Google Ads** | `GOOGLE_ADS_ACCESS_TOKEN` | Campaign mgmt | Nexus, OpenClaw |
| **Google Ads** | `GOOGLE_ADS_REFRESH_TOKEN` | Auth refresh | Nexus, OpenClaw |
| **Google Ads** | `GOOGLE_ADS_CLIENT_ID` | OAuth | Nexus, OpenClaw |
| **Google Ads** | `GOOGLE_ADS_CLIENT_SECRET` | OAuth | Nexus, OpenClaw |
| **Google Ads** | `GOOGLE_ADS_DEVELOPER_TOKEN` | API access | Nexus, OpenClaw |
| **Google Ads** | `GOOGLE_ADS_CUSTOMER_ID` | Account ID | Nexus, OpenClaw |
| **Meta** | `META_ACCESS_TOKEN` | FB/IG ads | Nexus, OpenClaw |

### Data & Storage
| **Superbase** | `SUPABASE_URL` | Database | All |
| **Superbase** | `SUPABASE_SERVICE_KEY` | Admin access | Nexus, OpenClaw |
| **Superbase** | `SUPABASE_ANON_KEY` | Client access | All |
| **Fireflies** | `FIREFLIES_API_KEY` | Meeting data | Mary, Writer |
| **Windsor** | (via config) | Data connector | Nexus |

### E-Commerce & PM
| **Shopify** | (To be added) | Revenue tracking | OpenClaw |
| **ClickUp** | (To be added) | Task management | Mary, OpenClaw |

## Agent-Specific Tool Access

### Clover 🍀
- All APIs (management oversight)
- Superbase read/write
- Slack admin functions

### Mary 📡
- Slack (primary)
- Gmail
- ClickUp
- Fireflies
- Superbase

### OpenClaw 🛡️
- Google Ads API
- Meta Marketing API
- Shopify API
- ClickUp API
- Superbase (heavy read/write)
- Slack alerting

### Nexus 🔗
- All advertising APIs
- All data APIs
- Superbase (admin level)
- Windsor connector

### Writer ✍️
- Fireflies (content from meetings)
- ClickUp (content calendar)
- Superbase (content library)

### Kimi 🧪
- All APIs (experimental access)
- Sandbox environments
- Git repositories
- Superbase

## Security Notes
- All keys stored in environment variables
- No keys committed to repositories
- Service keys used for automation (never anon keys for admin tasks)
- Regular rotation TBD based on audit schedule

## Adding New Integrations
1. Obtain API credentials
2. Add to Coolify environment variables
3. Document in this file
4. Update relevant agent SOUL.md
5. Test in Kimi agent first (experimental)
6. Deploy to production agents

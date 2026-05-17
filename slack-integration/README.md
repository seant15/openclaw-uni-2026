# Slack Integration Setup

Complete Slack app integration with Supabase backend for event logging and configuration management.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Set up Supabase Database
Run the SQL schema in your Supabase dashboard:
```bash
# Copy and paste the contents of supabase-schema.sql into your Supabase SQL editor
```

### 3. Configure Slack App
In your Slack App dashboard (https://api.slack.com/apps), configure:

**OAuth & Permissions → Scopes:**
- `app_mentions:read` - Listen for mentions
- `channels:history` - Read channel messages
- `channels:read` - Access channel information
- `chat:write` - Send messages
- `commands` - Handle slash commands
- `im:history` - Read direct messages
- `im:read` - Access DM information

**Event Subscriptions:**
- Enable Events: ON
- Request URL: `https://your-domain.com/slack/events`
- Subscribe to Bot Events:
  - `app_mention`
  - `message.channels` (if needed)
  - `message.im` (for DMs)

**Slash Commands:**
- Command: `/status`
- Request URL: `https://your-domain.com/slack/events`
- Description: "Check system status"

**Interactivity & Shortcuts:**
- Request URL: `https://your-domain.com/slack/events`

### 4. Environment Setup
Your `.env` file is already configured with:
- Slack credentials (Bot Token, Signing Secret, App ID)
- Supabase connection details
- Meta access token (for future integrations)

### 5. Start the Application
```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

## Features

### ✅ Implemented
- **App Mentions**: Responds when @mentioned in channels
- **Direct Messages**: Handles "hello" and other DM interactions
- **Slash Commands**: `/status` command for system status
- **Event Logging**: All interactions logged to Supabase
- **Interactive Buttons**: Button click handling
- **Configuration Management**: Stored in Supabase
- **Health Check**: `/health` endpoint for monitoring

### 🔄 Ready to Extend
- **Custom Commands**: Add more slash commands
- **Scheduled Messages**: Integration ready
- **User Management**: Track user interactions
- **Analytics**: Event data ready for analysis

## API Endpoints

- `POST /slack/events` - Main Slack webhook endpoint
- `GET /health` - Health check endpoint

## Database Schema

### slack_events
Stores all Slack interactions:
- `event_type`: Type of event (app_mention, slash_command, etc.)
- `user_id`: Slack user ID
- `channel_id`: Slack channel ID
- `text`: Message text or command text
- `metadata`: Additional JSON data
- `timestamp`: When the event occurred

### slack_config
App configuration storage:
- `key`: Configuration key
- `value`: Configuration value
- `description`: Human-readable description

## Usage Examples

### Send a Message
```javascript
await say({
  text: 'Hello! 👋',
  blocks: [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: '*Welcome to the app!*\nHow can I help you today?'
      }
    }
  ]
});
```

### Log Custom Event
```javascript
const { logSlackEvent } = require('./utils/slack-helpers');

await logSlackEvent({
  event_type: 'custom_action',
  user_id: userId,
  channel_id: channelId,
  text: 'Custom action performed',
  metadata: { action: 'button_click', value: 'submit' }
});
```

### Get Configuration
```javascript
const { getConfig } = require('./utils/slack-helpers');

const welcomeMessage = await getConfig('welcome_message');
```

## Deployment

### Local Development
1. Use ngrok for local webhook testing:
```bash
ngrok http 3000
```
2. Update your Slack app's Request URLs to use the ngrok URL

### Production Deployment
1. Deploy to your preferred platform (Railway, Heroku, DigitalOcean, etc.)
2. Update Slack app Request URLs to production domain
3. Ensure environment variables are set
4. Enable process monitoring (PM2, Docker health checks, etc.)

## Monitoring & Logs

### Health Check
```bash
curl https://your-domain.com/health
```

### View Recent Events
Check the `slack_events` table in Supabase dashboard or use:
```javascript
const { getRecentEvents } = require('./utils/slack-helpers');
const events = await getRecentEvents(50, 'app_mention');
```

## Security

- ✅ Slack request signature validation
- ✅ Environment variable protection
- ✅ Supabase RLS policies
- ✅ Error handling and logging

## Troubleshooting

### Common Issues
1. **Events not receiving**: Check Request URL in Slack app settings
2. **Authentication errors**: Verify bot token and signing secret
3. **Database errors**: Check Supabase connection and schema
4. **Permission errors**: Review OAuth scopes in Slack app

### Debug Mode
Set `NODE_ENV=development` for detailed logging.

## Next Steps

1. **Test the integration**: Mention the bot in a Slack channel
2. **Add custom commands**: Extend the slash command handlers
3. **Integrate with Meta**: Use the provided Meta token for cross-platform features
4. **Set up monitoring**: Add error tracking and analytics
5. **Scale as needed**: Add rate limiting, caching, etc.

---

**App Details:**
- App ID: A0AG8HE7GP5
- Integration: Slack + Supabase + Meta Ready
- Status: Ready for deployment and testing
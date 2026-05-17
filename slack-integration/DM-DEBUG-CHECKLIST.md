# DM Not Working - Debug Checklist

## 🔍 Quick Debug Steps

### 1. **Run the Debug Script First**
```bash
cd /data/workspace/slack-integration
node debug-dm.js
```
Then send a DM to your bot and watch the console output.

### 2. **Check Slack App Configuration**

**In your Slack App dashboard (https://api.slack.com/apps/A0AG8HE7GP5):**

**OAuth & Permissions → Bot Token Scopes:**
- ✅ `im:read` - Read DM channel info  
- ✅ `im:history` - Read DM messages
- ✅ `chat:write` - Send messages

**Event Subscriptions:**
- ✅ Enable Events: **ON**
- ✅ Request URL: `https://your-domain.com/slack/events` 
- ✅ Subscribe to Bot Events: `message.im`

**Important**: After adding scopes or events, you must **Reinstall to Workspace**

### 3. **Verify Bot Installation**
- Go to your Slack workspace
- Search for your bot name in the Apps section
- Make sure it shows as "Added to workspace"
- Try removing and re-adding the app

### 4. **Check Request URL Status**
In Event Subscriptions, your Request URL should show:
- ✅ **Verified** (green checkmark)
- ❌ If it shows "Failed" - your server isn't reachable

### 5. **Test Server Reachability**
If using ngrok for local testing:
```bash
# Terminal 1: Start debug server
node debug-dm.js

# Terminal 2: Start ngrok
npx ngrok http 3000

# Update Slack Request URL to: https://xyz.ngrok.io/slack/events
```

### 6. **Common Issues & Solutions**

**Issue**: No response at all
- **Check**: Bot token permissions
- **Check**: Event subscriptions enabled
- **Fix**: Reinstall bot to workspace

**Issue**: "This app responded to the button click but we had trouble loading the page"
- **Check**: Request URL returning proper response
- **Fix**: Verify webhook endpoint is working

**Issue**: Bot shows offline
- **Check**: Server is running and reachable
- **Check**: Request URL is verified in Slack

**Issue**: Getting events but no response
- **Check**: Message handler code
- **Check**: Error logs in console

## 🧪 Debug Commands

### Test Bot Token:
```bash
curl -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test
```

### Test Webhook URL:
```bash
curl -X POST https://your-domain.com/health
```

### Check Recent Events:
Look at your Supabase `slack_events` table to see if events are being received.

## 📋 Quick Fixes

### Fix 1: Update Message Handler
I already updated `server.js` to handle ALL messages, not just "hello".

### Fix 2: Missing Event Subscription
Most common issue - add `message.im` to Bot Events in Slack dashboard.

### Fix 3: Reinstall Bot
After any permission changes:
1. Go to Install App (left sidebar)
2. Click "Reinstall to Workspace"
3. Authorize the new permissions

## 🎯 Expected Debug Output

When you send a DM, you should see:
```
=== INCOMING EVENT ===
Event Type: message
Channel Type: im
Message Text: test message
User: U1234567890
Channel: D1234567890
===================

📩 Message received: { channel_type: 'im', text: 'test message', ... }
✅ This is a DM!
✅ DM response sent
```

If you don't see this output, the issue is likely:
1. Missing `message.im` event subscription
2. Bot not installed properly
3. Server not reachable by Slack

## 💡 Next Steps

1. **Run debug script**: `node debug-dm.js`
2. **Send DM to bot** and check console output
3. **Share the output** - this will tell us exactly where the issue is

The most common issue is missing the `message.im` event subscription in the Slack app configuration.
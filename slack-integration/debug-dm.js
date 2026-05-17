const { App } = require('@slack/bolt');
require('dotenv').config();

// Quick DM debug script
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  socketMode: false,
  port: process.env.DEBUG_PORT || 3001
});

// Enhanced logging middleware
app.use(async ({ body, next }) => {
  console.log('\n=== INCOMING EVENT ===');
  console.log('Event Type:', body.event?.type || body.type || 'unknown');
  console.log('Channel Type:', body.event?.channel_type);
  console.log('Message Text:', body.event?.text);
  console.log('User:', body.event?.user);
  console.log('Channel:', body.event?.channel);
  console.log('Full Body:', JSON.stringify(body, null, 2));
  console.log('===================\n');
  await next();
});

// Catch ALL messages (not just "hello")
app.message(async ({ message, say }) => {
  try {
    console.log('📩 Message received:', message);
    
    // Check if it's a DM
    if (message.channel_type === 'im') {
      console.log('✅ This is a DM!');
      
      await say({
        text: `I got your DM: "${message.text}" - Testing response! 🤖`
      });
      
      console.log('✅ DM response sent');
    } else {
      console.log('📢 This is a channel message');
    }
    
  } catch (error) {
    console.error('❌ Error handling message:', error);
  }
});

// Also handle app mentions (for debugging)
app.event('app_mention', async ({ event, say }) => {
  try {
    console.log('🏷️ App mention received:', event);
    await say(`Mention received: "${event.text}"`);
  } catch (error) {
    console.error('❌ Error handling app mention:', error);
  }
});

// URL verification for Slack
app.event('url_verification', async ({ body, ack }) => {
  console.log('🔗 URL verification request:', body);
  await ack(body.challenge);
});

// Start the debug server
(async () => {
  try {
    await app.start();
    console.log('🚀 DM Debug server started on port', process.env.DEBUG_PORT || 3001);
    console.log('Send a DM to your bot and watch the console...');
  } catch (error) {
    console.error('Failed to start debug server:', error);
  }
})();
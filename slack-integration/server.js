const { App } = require('@slack/bolt');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Initialize Slack App
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  socketMode: false, // Using HTTP mode for webhooks
  port: process.env.PORT || 3000
});

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// Middleware for logging
app.use(async ({ body, next }) => {
  console.log(`[${new Date().toISOString()}] Received event:`, body.event?.type || body.type);
  await next();
});

// Handle app mentions
app.event('app_mention', async ({ event, client, say }) => {
  try {
    console.log('App mentioned:', event);
    
    // Log event to Supabase
    const { error } = await supabase
      .from('slack_events')
      .insert([
        {
          event_type: 'app_mention',
          user_id: event.user,
          channel_id: event.channel,
          text: event.text,
          timestamp: new Date(event.ts * 1000).toISOString()
        }
      ]);

    if (error) {
      console.error('Supabase error:', error);
    }

    // Respond to the mention
    await say({
      text: `Hi <@${event.user}>! I received your message: "${event.text}"`
    });

  } catch (error) {
    console.error('Error handling app mention:', error);
  }
});

// Handle ALL direct messages (not just "hello")
app.message(async ({ message, say }) => {
  try {
    console.log('Message received:', message);
    
    // Only respond to DMs, not channel messages
    if (message.channel_type === 'im') {
      console.log('DM received from user:', message.user);
      
      // Log to Supabase
      await supabase
        .from('slack_events')
        .insert([
          {
            event_type: 'direct_message',
            user_id: message.user,
            channel_id: message.channel,
            text: message.text,
            timestamp: new Date(message.ts * 1000).toISOString()
          }
        ]);

      // Respond based on message content
      let response;
      if (message.text.toLowerCase().includes('hello') || message.text.toLowerCase().includes('hi')) {
        response = `Hello <@${message.user}>! 👋 How can I help you today?`;
      } else {
        response = `I received your message: "${message.text}"\n\nI'm here and listening! What would you like to do?`;
      }
      
      await say({ text: response });
      console.log('DM response sent');
    }

  } catch (error) {
    console.error('Error handling message:', error);
    
    // Try to send error response if possible
    try {
      if (message.channel_type === 'im') {
        await say({ text: 'Sorry, I encountered an error. Please try again!' });
      }
    } catch (fallbackError) {
      console.error('Failed to send error message:', fallbackError);
    }
  }
});

// Slash command example
app.command('/status', async ({ command, ack, respond }) => {
  try {
    await ack();
    
    // Log command to Supabase
    const { error } = await supabase
      .from('slack_events')
      .insert([
        {
          event_type: 'slash_command',
          user_id: command.user_id,
          channel_id: command.channel_id,
          text: command.text,
          command: command.command,
          timestamp: new Date().toISOString()
        }
      ]);

    if (error) {
      console.error('Supabase error:', error);
    }

    await respond({
      text: '🟢 System Status: All systems operational!',
      response_type: 'ephemeral' // Only visible to the user who ran the command
    });

  } catch (error) {
    console.error('Error handling status command:', error);
  }
});

// Handle button interactions
app.action('button_click', async ({ body, ack, say }) => {
  try {
    await ack();
    
    await say({
      text: `Button clicked by <@${body.user.id}>!`
    });

  } catch (error) {
    console.error('Error handling button click:', error);
  }
});

// Health check endpoint
app.receiver.app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    app_id: process.env.SLACK_APP_ID
  });
});

// Error handling
app.error((error) => {
  console.error('Slack app error:', error);
});

// Start the app
(async () => {
  try {
    await app.start();
    console.log('⚡️ Slack app is running!');
    console.log(`🔗 App ID: ${process.env.SLACK_APP_ID}`);
    console.log(`🚀 Server running on port ${process.env.PORT || 3000}`);
    
    // Test Supabase connection
    const { data, error } = await supabase.from('slack_events').select('count').limit(1);
    if (error) {
      console.warn('⚠️  Supabase connection issue:', error.message);
    } else {
      console.log('✅ Supabase connected successfully');
    }
    
  } catch (error) {
    console.error('Failed to start Slack app:', error);
    process.exit(1);
  }
})();
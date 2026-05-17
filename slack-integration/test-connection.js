const { createClient } = require('@supabase/supabase-js');
const { WebClient } = require('@slack/web-api');
require('dotenv').config();

async function testConnections() {
  console.log('🧪 Testing Slack Integration Connections...\n');

  // Test Supabase connection
  console.log('📊 Testing Supabase connection...');
  try {
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );

    const { data, error } = await supabase
      .from('slack_events')
      .select('count')
      .limit(1);

    if (error) {
      console.error('❌ Supabase connection failed:', error.message);
    } else {
      console.log('✅ Supabase connection successful');
    }
  } catch (error) {
    console.error('❌ Supabase connection error:', error.message);
  }

  // Test Slack Bot Token
  console.log('\n🤖 Testing Slack bot token...');
  try {
    const slack = new WebClient(process.env.SLACK_BOT_TOKEN);
    
    const auth = await slack.auth.test();
    console.log('✅ Slack bot authenticated:', auth.user);
    console.log('   - Bot ID:', auth.bot_id);
    console.log('   - Team:', auth.team);
    console.log('   - URL:', auth.url);
  } catch (error) {
    console.error('❌ Slack authentication failed:', error.message);
  }

  // Test environment variables
  console.log('\n🔐 Checking environment variables...');
  const requiredVars = [
    'SLACK_BOT_TOKEN',
    'SLACK_SIGNING_SECRET',
    'SLACK_APP_ID',
    'SUPABASE_URL',
    'SUPABASE_SERVICE_KEY'
  ];

  requiredVars.forEach(varName => {
    if (process.env[varName]) {
      console.log(`✅ ${varName}: Set (${process.env[varName].substring(0, 10)}...)`);
    } else {
      console.log(`❌ ${varName}: Missing`);
    }
  });

  // Test Supabase schema
  console.log('\n🗄️  Testing Supabase schema...');
  try {
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );

    // Test slack_events table
    const { error: eventsError } = await supabase
      .from('slack_events')
      .select('*')
      .limit(1);

    if (eventsError) {
      console.error('❌ slack_events table not found or accessible:', eventsError.message);
      console.log('💡 Run the SQL from supabase-schema.sql in your Supabase dashboard');
    } else {
      console.log('✅ slack_events table accessible');
    }

    // Test slack_config table
    const { error: configError } = await supabase
      .from('slack_config')
      .select('*')
      .limit(1);

    if (configError) {
      console.error('❌ slack_config table not found or accessible:', configError.message);
    } else {
      console.log('✅ slack_config table accessible');
    }

  } catch (error) {
    console.error('❌ Schema test error:', error.message);
  }

  console.log('\n🚀 Test complete! If all checks passed, you\'re ready to start the server.');
  console.log('   Run: npm start or npm run dev');
}

// Run tests
testConnections().catch(error => {
  console.error('Fatal error during testing:', error);
  process.exit(1);
});
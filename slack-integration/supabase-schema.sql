-- Create table for storing Slack events
CREATE TABLE IF NOT EXISTS slack_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  event_type VARCHAR(50) NOT NULL,
  user_id VARCHAR(50),
  channel_id VARCHAR(50),
  text TEXT,
  command VARCHAR(50),
  metadata JSONB,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_slack_events_type ON slack_events(event_type);
CREATE INDEX IF NOT EXISTS idx_slack_events_user ON slack_events(user_id);
CREATE INDEX IF NOT EXISTS idx_slack_events_channel ON slack_events(channel_id);
CREATE INDEX IF NOT EXISTS idx_slack_events_timestamp ON slack_events(timestamp);

-- Create table for storing Slack app configuration
CREATE TABLE IF NOT EXISTS slack_config (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  key VARCHAR(100) UNIQUE NOT NULL,
  value TEXT,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configuration
INSERT INTO slack_config (key, value, description) VALUES
  ('app_id', 'A0AG8HE7GP5', 'Slack App ID'),
  ('welcome_message', 'Welcome! I''m here to help you.', 'Default welcome message'),
  ('max_message_length', '4000', 'Maximum message length for responses')
ON CONFLICT (key) DO NOTHING;

-- Create RLS policies (Row Level Security)
ALTER TABLE slack_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE slack_config ENABLE ROW LEVEL SECURITY;

-- Allow service role to access all data
CREATE POLICY "Service role can access slack_events" ON slack_events
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access slack_config" ON slack_config
  FOR ALL USING (auth.role() = 'service_role');
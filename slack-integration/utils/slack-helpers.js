const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

/**
 * Log Slack event to Supabase
 */
async function logSlackEvent(eventData) {
  try {
    const { error } = await supabase
      .from('slack_events')
      .insert([eventData]);
    
    if (error) {
      console.error('Failed to log Slack event:', error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error logging Slack event:', error);
    return false;
  }
}

/**
 * Get configuration value from Supabase
 */
async function getConfig(key) {
  try {
    const { data, error } = await supabase
      .from('slack_config')
      .select('value')
      .eq('key', key)
      .single();
    
    if (error) {
      console.error(`Failed to get config for key "${key}":`, error);
      return null;
    }
    
    return data?.value;
  } catch (error) {
    console.error('Error getting config:', error);
    return null;
  }
}

/**
 * Update configuration value in Supabase
 */
async function updateConfig(key, value, description = null) {
  try {
    const updateData = { value, updated_at: new Date().toISOString() };
    if (description) updateData.description = description;
    
    const { error } = await supabase
      .from('slack_config')
      .upsert([{ key, ...updateData }]);
    
    if (error) {
      console.error(`Failed to update config for key "${key}":`, error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error updating config:', error);
    return false;
  }
}

/**
 * Format message with user mentions
 */
function formatMessage(text, userId = null) {
  if (userId) {
    return `<@${userId}> ${text}`;
  }
  return text;
}

/**
 * Create interactive message blocks
 */
function createInteractiveBlocks(title, description, buttons = []) {
  const blocks = [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*${title}*\n${description}`
      }
    }
  ];

  if (buttons.length > 0) {
    blocks.push({
      type: 'actions',
      elements: buttons.map(button => ({
        type: 'button',
        text: {
          type: 'plain_text',
          text: button.text
        },
        action_id: button.action_id,
        value: button.value || button.text,
        style: button.style || 'primary'
      }))
    });
  }

  return blocks;
}

/**
 * Validate Slack event signature (for webhook security)
 */
function validateSlackRequest(body, signature, timestamp) {
  const crypto = require('crypto');
  const hmac = crypto.createHmac('sha256', process.env.SLACK_SIGNING_SECRET);
  
  const [version, hash] = signature.split('=');
  const baseString = `${version}:${timestamp}:${body}`;
  
  hmac.update(baseString);
  const computedHash = hmac.digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(hash, 'hex'),
    Buffer.from(computedHash, 'hex')
  );
}

/**
 * Get recent events from Supabase
 */
async function getRecentEvents(limit = 10, eventType = null) {
  try {
    let query = supabase
      .from('slack_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);
    
    if (eventType) {
      query = query.eq('event_type', eventType);
    }
    
    const { data, error } = await query;
    
    if (error) {
      console.error('Failed to get recent events:', error);
      return [];
    }
    
    return data;
  } catch (error) {
    console.error('Error getting recent events:', error);
    return [];
  }
}

module.exports = {
  logSlackEvent,
  getConfig,
  updateConfig,
  formatMessage,
  createInteractiveBlocks,
  validateSlackRequest,
  getRecentEvents
};
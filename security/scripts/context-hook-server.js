#!/usr/bin/env node
/**
 * Context Hook Server (v2)
 * HTTP server listening on :33123/context-audit
 * Triggered by OpenClaw on each turn to audit fixed context size
 * 
 * Endpoints:
 *   POST /context-audit  - Run audit and return summary
 *   GET  /health         - Health check
 * 
 * Environment:
 *   SEC_CONTEXT_AUDIT_ENABLED=true|false  (default: true)
 *   SEC_CONTEXT_AUDIT_THRESHOLD=3888      (tokens, default: 3888)
 *   SEC_CONTEXT_AUDIT_COOLDOWN_MIN=60     (min between reports, default: 60)
 *   SLACK_BOT_TOKEN                       (required for DM alerts)
 *   SLACK_DM_USER_ID                      (target user for DM, default: U025H4Q9FPA)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = 33123;
const WORKSPACE = '/data/workspace';
const AUDITOR_SCRIPT = path.join(WORKSPACE, 'security', 'scripts', 'context_auditor.js');
const LAST_ALERT_FILE = path.join(WORKSPACE, 'security', '.last_context_alert');

// Slack API config
const SLACK_API_BASE = 'https://slack.com/api';
const SLACK_BOT_TOKEN = process.env.SLACK_BOT_TOKEN || '';
const SLACK_DM_USER_ID = process.env.SLACK_DM_USER_ID || 'U025H4Q9FPA';

// Config from env
const ENABLED = (process.env.SEC_CONTEXT_AUDIT_ENABLED || 'true') === 'true';
const THRESHOLD = parseInt(process.env.SEC_CONTEXT_AUDIT_THRESHOLD || '3888', 10);
const COOLDOWN_MIN = parseInt(process.env.SEC_CONTEXT_AUDIT_COOLDOWN_MIN || '60', 10);

// Simple logger
function log(level, msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] [${level}] ${msg}`);
}

// Check if we're in cooldown period
function isInCooldown() {
  if (!fs.existsSync(LAST_ALERT_FILE)) return false;
  const lastAlert = parseInt(fs.readFileSync(LAST_ALERT_FILE, 'utf8'), 10);
  const now = Date.now();
  const cooldownMs = COOLDOWN_MIN * 60 * 1000;
  return (now - lastAlert) < cooldownMs;
}

// Update last alert timestamp
function recordAlert() {
  fs.writeFileSync(LAST_ALERT_FILE, String(Date.now()), 'utf8');
}

// Run the auditor script and parse results
function runAudit() {
  try {
    const output = execSync(`node ${AUDITOR_SCRIPT}`, { encoding: 'utf8', cwd: WORKSPACE });
    const reportPath = output.trim();
    
    if (!fs.existsSync(reportPath)) {
      return { success: false, error: 'Report file not generated' };
    }
    
    const reportContent = fs.readFileSync(reportPath, 'utf8');
    
    // Extract total tokens from report
    const tokenMatch = reportContent.match(/\*\*~([\d,]+) tokens\*\*/);
    const totalTokens = tokenMatch ? parseInt(tokenMatch[1].replace(/,/g, ''), 10) : 0;
    
    return {
      success: true,
      reportPath,
      totalTokens,
      threshold: THRESHOLD,
      exceeded: totalTokens > THRESHOLD,
      reportContent
    };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

// Open DM channel with user
async function openDMChannel(userId) {
  if (!SLACK_BOT_TOKEN) {
    throw new Error('SLACK_BOT_TOKEN not configured');
  }
  
  const url = `${SLACK_API_BASE}/conversations.open`;
  const params = new URLSearchParams({ users: userId });
  
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SLACK_BOT_TOKEN}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params
  });
  
  const data = await res.json();
  if (!data.ok) {
    throw new Error(`Slack API error: ${data.error}`);
  }
  
  return data.channel.id;
}

// Send Slack DM notification
async function sendSlackAlert(auditResult) {
  if (!SLACK_BOT_TOKEN) {
    log('warn', 'SLACK_BOT_TOKEN not configured, skipping alert');
    return false;
  }
  
  try {
    // Open DM channel
    const channelId = await openDMChannel(SLACK_DM_USER_ID);
    
    const payload = {
      channel: channelId,
      text: `⚠️ Context Audit Alert`,
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: '⚠️ Context Size Alert',
            emoji: true
          }
        },
        {
          type: 'section',
          fields: [
            {
              type: 'mrkdwn',
              text: `*Current Size:*\n${auditResult.totalTokens.toLocaleString()} tokens`
            },
            {
              type: 'mrkdwn',
              text: `*Threshold:*\n${auditResult.threshold.toLocaleString()} tokens`
            }
          ]
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `Fixed context exceeds threshold by *${(auditResult.totalTokens - auditResult.threshold).toLocaleString()}* tokens.\nReport: \`${auditResult.reportPath}\``
          }
        }
      ]
    };
    
    const res = await fetch(`${SLACK_API_BASE}/chat.postMessage`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SLACK_BOT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    if (!data.ok) {
      throw new Error(`Slack API error: ${data.error}`);
    }
    
    log('info', `Slack DM alert sent to ${SLACK_DM_USER_ID}`);
    return true;
  } catch (err) {
    log('error', `Failed to send Slack alert: ${err.message}`);
    return false;
  }
}

// HTTP request handler
const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // Health check
  if (url.pathname === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'ok',
      enabled: ENABLED,
      threshold: THRESHOLD,
      cooldownMinutes: COOLDOWN_MIN,
      slackConfigured: !!SLACK_BOT_TOKEN,
      slackTargetUser: SLACK_DM_USER_ID
    }));
    return;
  }
  
  // Context audit endpoint
  if (url.pathname === '/context-audit' && req.method === 'POST') {
    if (!ENABLED) {
      res.writeHead(200);
      res.end(JSON.stringify({ enabled: false, message: 'Audit disabled via SEC_CONTEXT_AUDIT_ENABLED' }));
      return;
    }
    
    log('info', 'Running context audit...');
    const result = runAudit();
    
    if (!result.success) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: result.error }));
      return;
    }
    
    // Check threshold and cooldown
    let alertSent = false;
    if (result.exceeded && !isInCooldown()) {
      log('warn', `Context exceeds threshold: ${result.totalTokens} > ${THRESHOLD}`);
      alertSent = await sendSlackAlert(result);
      if (alertSent) {
        recordAlert();
      }
    }
    
    res.writeHead(200);
    res.end(JSON.stringify({
      success: true,
      totalTokens: result.totalTokens,
      threshold: result.threshold,
      exceeded: result.exceeded,
      alertSent,
      inCooldown: isInCooldown(),
      reportPath: result.reportPath
    }));
    return;
  }
  
  // 404
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start server
server.listen(PORT, '0.0.0.0', () => {
  log('info', `Context Hook Server listening on :${PORT}`);
  log('info', `Config: enabled=${ENABLED}, threshold=${THRESHOLD}, cooldown=${COOLDOWN_MIN}min`);
  log('info', `Slack DM alerts: ${SLACK_BOT_TOKEN ? 'configured' : 'not configured'} (target: ${SLACK_DM_USER_ID})`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('info', 'SIGTERM received, shutting down...');
  server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
  log('info', 'SIGINT received, shutting down...');
  server.close(() => process.exit(0));
});

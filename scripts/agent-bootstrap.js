#!/usr/bin/env node
/**
 * Agent Bootstrap Script
 * Run this at the start of every agent session to load secrets from Supabase
 * 
 * This script:
 * 1. Loads required secrets from Supabase
 * 2. Injects them into process.env
 * 3. Records the agent startup
 * 
 * Usage:
 *   node scripts/agent-bootstrap.js
 * 
 * Or in AGENTS.md:
 *   Pre-start Commands:
 *     - node /data/workspace/scripts/agent-bootstrap.js
 */

const { injectSecretsToEnv, getHealthStatus } = require('../lib/secret-manager');
const { createClient } = require('@supabase/supabase-js');

// Required secrets for all agents
const REQUIRED_SECRETS = [
    // Database
    'SUPABASE_SERVICE_KEY',
    'SUPABASE_ANON_KEY',
    
    // AI APIs
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'KIMI_API_KEY',
    
    // Meta
    'META_ACCESS_TOKEN',
    
    // Google
    'GOOGLE_ADS_DEVELOPER_TOKEN',
    'GOOGLE_ADS_ACCESS_TOKEN',
    'GOOGLE_ADS_REFRESH_TOKEN',
    'GOOGLE_SERVICE_ACCOUNT_JSON',
    
    // Slack
    'SLACK_BOT_TOKEN',
    'SLACK_SIGNING_SECRET',
    
    // Auth
    'OPENCLAW_GATEWAY_TOKEN',
    'HOOKS_TOKEN'
];

// Optional secrets (not critical for basic operation)
const OPTIONAL_SECRETS = [
    'FIREFLIES_API_KEY',
    'CLICKUP_API_KEY',
    'N8N_API_KEY',
    'GIT_PERSONAL_TOKEN',
    'AUTH_USERNAME',
    'AUTH_PASSWORD'
];

async function recordAgentStartup() {
    try {
        const supabase = createClient(
            process.env.SUPABASE_URL,
            process.env.SUPABASE_SERVICE_KEY
        );
        
        const agentId = process.env.AGENT_ID || process.env.OPENCLAW_AGENT_ID || 'unknown';
        const agentName = process.env.AGENT_NAME || agentId;
        
        await supabase
            .from('agent_startup_state')
            .upsert({
                agent_id: agentId,
                agent_name: agentName,
                last_startup_at: new Date().toISOString(),
                hostname: require('os').hostname(),
                version: process.env.OPENCLAW_VERSION || 'unknown',
                metadata: {
                    node_version: process.version,
                    platform: process.platform,
                    session_key: process.env.SESSION_KEY || process.env.OPENCLAW_SESSION_KEY
                }
            }, {
                onConflict: 'agent_id'
            });
    } catch (err) {
        // Non-fatal
        console.warn('⚠️  Failed to record startup:', err.message);
    }
}

async function main() {
    console.log('🚀 Agent Bootstrap Starting...');
    console.log();
    
    // Check if we have basic Supabase config
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
        console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set');
        console.error('   These should be the only secrets in your .env file');
        process.exit(1);
    }
    
    try {
        // Inject required secrets
        console.log('📦 Loading required secrets from Supabase...');
        const requiredResults = await injectSecretsToEnv(REQUIRED_SECRETS);
        
        const loadedCount = Object.keys(requiredResults).length;
        console.log(`   ✅ Loaded ${loadedCount}/${REQUIRED_SECRETS.length} required secrets`);
        
        // Show which ones failed
        const failedRequired = REQUIRED_SECRETS.filter(k => !requiredResults[k]);
        if (failedRequired.length > 0) {
            console.warn(`   ⚠️  Failed to load: ${failedRequired.join(', ')}`);
        }
        
        // Try to load optional secrets (don't fail if these don't exist)
        console.log('📦 Loading optional secrets...');
        try {
            const optionalResults = await injectSecretsToEnv(OPTIONAL_SECRETS);
            const optionalLoaded = Object.keys(optionalResults).length;
            console.log(`   ✅ Loaded ${optionalLoaded}/${OPTIONAL_SECRETS.length} optional secrets`);
        } catch (err) {
            console.log(`   ⏭️  Optional secrets not available (${err.message})`);
        }
        
        // Record startup
        console.log('📝 Recording agent startup...');
        await recordAgentStartup();
        
        // Get secret health status
        console.log('🏥 Checking secret management health...');
        const health = await getHealthStatus();
        if (health.expiring_soon > 0) {
            console.warn(`   ⚠️  ${health.expiring_soon} secrets expiring within 7 days`);
        } else {
            console.log('   ✅ All secrets healthy');
        }
        
        console.log();
        console.log('✅ Agent bootstrap complete!');
        console.log(`   Agent: ${process.env.AGENT_ID || 'unknown'}`);
        console.log(`   Secrets loaded: ${loadedCount} required`);
        
        // Check for cross-agent notices
        await checkNotices();
        
    } catch (err) {
        console.error();
        console.error('❌ Bootstrap failed:', err.message);
        console.error();
        console.error('Troubleshooting:');
        console.error('   1. Check SUPABASE_URL and SUPABASE_SERVICE_KEY in .env');
        console.error('   2. Verify ENCRYPTION_KEY is set correctly');
        console.error('   3. Run migration script: node scripts/migrate-secrets.js');
        console.error();
        
        // Fallback to legacy .env mode
        if (process.env.SECRET_ENABLE_FALLBACK !== 'false') {
            console.log('⚠️  Falling back to legacy .env mode...');
            console.log('   Secrets will be loaded from .env file directly');
            console.log('   Please migrate secrets to Supabase for better security');
            
            // Don't exit with error, let the agent continue with fallback
            process.exitCode = 0;
        } else {
            process.exit(1);
        }
    }
}

async function checkNotices() {
    try {
        const supabase = createClient(
            process.env.SUPABASE_URL,
            process.env.SUPABASE_SERVICE_KEY
        );
        
        const agentId = process.env.AGENT_ID || process.env.OPENCLAW_AGENT_ID || 'unknown';
        
        // Get active notices for this agent
        const { data: notices, error } = await supabase
            .from('agent_notices')
            .select('*')
            .eq('is_active', true)
            .lte('effective_at', new Date().toISOString())
            .or(`expires_at.is.null,expires_at.gt.${new Date().toISOString()}`)
            .order('priority', { ascending: false })
            .order('created_at', { ascending: false })
            .limit(5);
        
        if (error || !notices || notices.length === 0) {
            return;
        }
        
        // Filter notices for this agent
        const relevantNotices = notices.filter(n => {
            // If no target agents specified, applies to all
            if (!n.target_agents || n.target_agents.length === 0) return true;
            // Otherwise check if this agent is targeted
            return n.target_agents.includes(agentId);
        });
        
        if (relevantNotices.length > 0) {
            console.log();
            console.log('📢 Cross-Agent Notices:');
            console.log('-'.repeat(50));
            
            for (const notice of relevantNotices) {
                const priorityEmoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'normal': '🟡',
                    'low': '🟢'
                }[notice.priority] || '⚪';
                
                console.log(`${priorityEmoji} [${notice.priority.toUpperCase()}] ${notice.title}`);
                console.log(`   ${notice.content.substring(0, 100)}${notice.content.length > 100 ? '...' : ''}`);
                
                if (notice.requires_acknowledgment) {
                    const isAcked = notice.acknowledged_by?.includes(agentId);
                    if (!isAcked) {
                        console.log(`   ⚠️  Requires acknowledgment`);
                    }
                }
                console.log();
            }
        }
        
        // Update agent's last notice check
        await supabase
            .from('agent_startup_state')
            .upsert({
                agent_id: agentId,
                last_notice_check_at: new Date().toISOString(),
                unread_notices_count: relevantNotices.filter(n => 
                    n.requires_acknowledgment && !n.acknowledged_by?.includes(agentId)
                ).length
            }, {
                onConflict: 'agent_id'
            });
            
    } catch (err) {
        // Non-fatal
        console.warn('⚠️  Failed to check notices:', err.message);
    }
}

// Run main
main().catch(err => {
    console.error('❌ Unexpected error:', err);
    process.exit(1);
});

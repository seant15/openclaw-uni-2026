#!/usr/bin/env node
/**
 * Secret Migration Script - From Environment Variables
 * Migrates secrets from process.env to Supabase encrypted storage
 * 
 * Usage:
 *   ENCRYPTION_KEY=xxx node scripts/migrate-secrets.js [options]
 *   
 * Options:
 *   --dry-run          Show what would be migrated without actually doing it
 *   --skip-existing    Skip secrets that already exist in Supabase
 *   --verbose          Show detailed output
 *   --help             Show help
 */

const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
    dryRun: args.includes('--dry-run'),
    skipExisting: args.includes('--skip-existing'),
    verbose: args.includes('--verbose')
};

// Show help
if (args.includes('--help')) {
    console.log(`
Secret Migration Script (Environment Variables)
===============================================

Migrates secrets from process.env to Supabase encrypted storage.

Usage:
  ENCRYPTION_KEY=xxx node scripts/migrate-secrets.js [options]

Options:
  --dry-run          Show what would be migrated without actually doing it
  --skip-existing    Skip secrets that already exist in Supabase
  --verbose          Show detailed output
  --help             Show this help message

Environment Variables Required:
  SUPABASE_URL           Supabase project URL
  SUPABASE_SERVICE_KEY   Supabase service role key
  ENCRYPTION_KEY         Master encryption key (32+ characters recommended)

Example:
  ENCRYPTION_KEY=$(openssl rand -base64 32) node scripts/migrate-secrets.js --dry-run
`);
    process.exit(0);
}

// Required environment variables
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set');
    process.exit(1);
}

if (!ENCRYPTION_KEY) {
    console.error('❌ Error: ENCRYPTION_KEY must be set for encryption');
    console.error('   Generate with: openssl rand -base64 32');
    process.exit(1);
}

// Initialize Supabase
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Secret categories mapping
const SECRET_CATEGORIES = {
    // Database
    SUPABASE_SERVICE_KEY: 'database',
    SUPABASE_ANON_KEY: 'database',
    SUPABASE_PERSONAL_ACCESS_TOKEN: 'database',
    
    // APIs - AI Models
    OPENAI_API_KEY: 'api',
    ANTHROPIC_API_KEY: 'api',
    KIMI_API_KEY: 'api',
    KIMI_API: 'api',
    
    // APIs - Meta
    META_ACCESS_TOKEN: 'api',
    
    // APIs - Google
    GOOGLE_ADS_DEVELOPER_TOKEN: 'api',
    GOOGLE_ADS_ACCESS_TOKEN: 'api',
    GOOGLE_ADS_REFRESH_TOKEN: 'api',
    GOOGLE_ADS_CLIENT_ID: 'oauth',
    GOOGLE_ADS_CLIENT_SECRET: 'oauth',
    GOOGLE_CLIENT_ID: 'oauth',
    GOOGLE_CLIENT_SECRET: 'oauth',
    GMAIL_CLIENT_ID: 'oauth',
    GMAIL_CLIENT_SECRET: 'oauth',
    GMAIL_REFRESH_TOKEN: 'api',
    GOOGLE_SERVICE_ACCOUNT_JSON: 'api',
    
    // APIs - Slack
    SLACK_BOT_TOKEN: 'messaging',
    SLACK_APP_TOKEN: 'messaging',
    SLACK_SIGNING_SECRET: 'messaging',
    SLACK_VERIFICATION_TOKEN: 'messaging',
    SEC_SLACK_WEBHOOK_URL: 'messaging',
    
    // Auth
    AUTH_USERNAME: 'auth',
    AUTH_PASSWORD: 'auth',
    HOOKS_TOKEN: 'auth',
    OPENCLAW_GATEWAY_TOKEN: 'auth',
    
    // Other APIs
    FIREFLIES_API_KEY: 'api',
    CLICKUP_API_KEY: 'api',
    N8N_API_KEY: 'api',
    GIT_PERSONAL_TOKEN: 'api'
};

// Secrets to migrate (high and medium sensitivity)
const SECRETS_TO_MIGRATE = [
    // Database
    'SUPABASE_SERVICE_KEY',
    'SUPABASE_ANON_KEY',
    'SUPABASE_PERSONAL_ACCESS_TOKEN',
    
    // AI APIs
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'KIMI_API_KEY',
    'KIMI_API',
    
    // Meta
    'META_ACCESS_TOKEN',
    
    // Google Ads
    'GOOGLE_ADS_DEVELOPER_TOKEN',
    'GOOGLE_ADS_ACCESS_TOKEN',
    'GOOGLE_ADS_REFRESH_TOKEN',
    'GOOGLE_ADS_CLIENT_ID',
    'GOOGLE_ADS_CLIENT_SECRET',
    
    // Google OAuth
    'GOOGLE_CLIENT_ID',
    'GOOGLE_CLIENT_SECRET',
    'GMAIL_CLIENT_ID',
    'GMAIL_CLIENT_SECRET',
    'GMAIL_REFRESH_TOKEN',
    'GOOGLE_SERVICE_ACCOUNT_JSON',
    
    // Slack
    'SLACK_BOT_TOKEN',
    'SLACK_APP_TOKEN',
    'SLACK_SIGNING_SECRET',
    'SLACK_VERIFICATION_TOKEN',
    'SEC_SLACK_WEBHOOK_URL',
    
    // Auth
    'AUTH_USERNAME',
    'AUTH_PASSWORD',
    'HOOKS_TOKEN',
    'OPENCLAW_GATEWAY_TOKEN',
    
    // Other
    'FIREFLIES_API_KEY',
    'CLICKUP_API_KEY',
    'N8N_API_KEY',
    'GIT_PERSONAL_TOKEN'
];

/**
 * Encrypt value using AES-256-GCM
 */
function encrypt(value) {
    const iv = crypto.randomBytes(16);
    const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    
    let ciphertext = cipher.update(value, 'utf8');
    ciphertext = Buffer.concat([ciphertext, cipher.final()]);
    
    const tag = cipher.getAuthTag();
    
    // Format: base64(iv:tag:ciphertext)
    return Buffer.concat([iv, tag, ciphertext]).toString('base64');
}

/**
 * Check if secret already exists in Supabase
 */
async function secretExists(keyName) {
    const { data, error } = await supabase
        .from('secrets')
        .select('id')
        .eq('key_name', keyName)
        .eq('is_active', true)
        .single();
    
    return !!data;
}

/**
 * Migrate a single secret
 */
async function migrateSecret(keyName, dryRun = false) {
    const value = process.env[keyName];
    
    if (!value || value === '') {
        return { status: 'skipped', reason: 'not set in environment' };
    }
    
    // Check if exists
    if (!dryRun && options.skipExisting) {
        const exists = await secretExists(keyName);
        if (exists) {
            return { status: 'skipped', reason: 'already exists in Supabase' };
        }
    }
    
    const category = SECRET_CATEGORIES[keyName] || 'api';
    
    if (dryRun) {
        return { 
            status: 'dry-run', 
            category,
            valuePreview: value.substring(0, 10) + '...' 
        };
    }
    
    try {
        const encryptedValue = encrypt(value);
        
        const { error } = await supabase
            .from('secrets')
            .upsert({
                key_name: keyName,
                encrypted_value: encryptedValue,
                environment: 'production',
                category: category,
                is_active: true,
                description: `Migrated from environment on ${new Date().toISOString()}`,
                updated_at: new Date().toISOString()
            }, {
                onConflict: 'key_name'
            });
        
        if (error) {
            return { status: 'error', error: error.message };
        }
        
        return { status: 'success', category };
    } catch (err) {
        return { status: 'error', error: err.message };
    }
}

/**
 * Main migration function
 */
async function main() {
    console.log('=' .repeat(60));
    console.log('UNI Secret Migration Tool (Environment Variables)');
    console.log('=' .repeat(60));
    console.log();
    
    // Show configuration
    console.log('⚙️  Configuration:');
    console.log(`   Supabase URL: ${SUPABASE_URL}`);
    console.log(`   Dry run: ${options.dryRun ? 'YES' : 'NO'}`);
    console.log(`   Skip existing: ${options.skipExisting ? 'YES' : 'NO'}`);
    console.log();
    
    // Statistics
    const stats = {
        total: 0,
        migrated: 0,
        skipped: 0,
        errors: 0,
        byCategory: {}
    };
    
    // Migrate each secret
    console.log('🚀 Starting migration...');
    console.log();
    
    for (const keyName of SECRETS_TO_MIGRATE) {
        if (options.verbose) {
            process.stdout.write(`   ${keyName}... `);
        }
        
        const result = await migrateSecret(keyName, options.dryRun);
        
        stats.total++;
        
        if (result.status === 'success') {
            stats.migrated++;
            stats.byCategory[result.category] = (stats.byCategory[result.category] || 0) + 1;
            if (options.verbose) console.log('✅ migrated');
        } else if (result.status === 'dry-run') {
            stats.byCategory[result.category] = (stats.byCategory[result.category] || 0) + 1;
            if (options.verbose) console.log(`📝 would migrate (${result.category})`);
        } else if (result.status === 'skipped') {
            stats.skipped++;
            if (options.verbose) console.log(`⏭️  skipped (${result.reason})`);
        } else if (result.status === 'error') {
            stats.errors++;
            if (options.verbose) console.log(`❌ error: ${result.error}`);
        }
    }
    
    console.log();
    console.log('=' .repeat(60));
    console.log('Migration Summary');
    console.log('=' .repeat(60));
    console.log(`   Total checked: ${stats.total}`);
    
    if (options.dryRun) {
        const wouldMigrate = Object.values(stats.byCategory).reduce((a, b) => a + b, 0);
        console.log(`   Would migrate: ${wouldMigrate}`);
        console.log(`   Not in environment: ${stats.skipped}`);
    } else {
        console.log(`   Successfully migrated: ${stats.migrated}`);
        console.log(`   Skipped: ${stats.skipped}`);
        console.log(`   Errors: ${stats.errors}`);
    }
    
    console.log();
    console.log('By category:');
    for (const [category, count] of Object.entries(stats.byCategory)) {
        console.log(`   ${category}: ${count}`);
    }
    
    console.log();
    
    if (options.dryRun) {
        console.log('📝 This was a dry run. No changes were made.');
        console.log('   Run without --dry-run to perform actual migration.');
    } else if (stats.errors === 0) {
        console.log('✅ Migration completed successfully!');
        console.log();
        console.log('Next steps:');
        console.log('   1. Test secret retrieval: node scripts/secret-cli.js list');
        console.log('   2. Test agent bootstrap: node scripts/agent-bootstrap.js');
        console.log('   3. Update agent configs to use bootstrap script');
        console.log('   4. After 1 week of stable operation, secrets can be removed from environment');
    } else {
        console.log('⚠️  Migration completed with errors. Please review above.');
        process.exit(1);
    }
    
    console.log();
}

// Run main
main().catch(err => {
    console.error('❌ Fatal error:', err.message);
    process.exit(1);
});

#!/usr/bin/env node
/**
 * Secret Migration Script (Environment Variable Version)
 * Migrates secrets from system environment variables to Supabase encrypted storage
 */

const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');

const args = process.argv.slice(2);
const options = {
    dryRun: args.includes('--dry-run'),
    skipExisting: args.includes('--skip-existing'),
    verbose: args.includes('--verbose')
};

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment');
    process.exit(1);
}

if (!ENCRYPTION_KEY) {
    console.error('❌ Error: ENCRYPTION_KEY must be provided');
    console.error('   Generate with: openssl rand -base64 32');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

const SECRETS_TO_MIGRATE = [
    'SUPABASE_SERVICE_KEY', 'SUPABASE_ANON_KEY', 'SUPABASE_PERSONAL_ACCESS_TOKEN',
    'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'KIMI_API_KEY', 'KIMI_API',
    'META_ACCESS_TOKEN', 'GOOGLE_ADS_DEVELOPER_TOKEN', 'GOOGLE_ADS_ACCESS_TOKEN',
    'GOOGLE_ADS_REFRESH_TOKEN', 'GOOGLE_ADS_CLIENT_ID', 'GOOGLE_ADS_CLIENT_SECRET',
    'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GMAIL_CLIENT_ID',
    'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN', 'GOOGLE_SERVICE_ACCOUNT_JSON',
    'SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'SLACK_SIGNING_SECRET', 'SLACK_VERIFICATION_TOKEN',
    'AUTH_USERNAME', 'AUTH_PASSWORD', 'HOOKS_TOKEN', 'OPENCLAW_GATEWAY_TOKEN',
    'FIREFLIES_API_KEY', 'CLICKUP_API_KEY', 'N8N_API_KEY', 'GIT_PERSONAL_TOKEN'
];

const SECRET_CATEGORIES = {
    SUPABASE_SERVICE_KEY: 'database', SUPABASE_ANON_KEY: 'database', SUPABASE_PERSONAL_ACCESS_TOKEN: 'database',
    OPENAI_API_KEY: 'api', ANTHROPIC_API_KEY: 'api', KIMI_API_KEY: 'api', KIMI_API: 'api',
    META_ACCESS_TOKEN: 'api', GOOGLE_ADS_DEVELOPER_TOKEN: 'api', GOOGLE_ADS_ACCESS_TOKEN: 'api',
    GOOGLE_ADS_REFRESH_TOKEN: 'api', GOOGLE_ADS_CLIENT_ID: 'oauth', GOOGLE_ADS_CLIENT_SECRET: 'oauth',
    GOOGLE_CLIENT_ID: 'oauth', GOOGLE_CLIENT_SECRET: 'oauth', GMAIL_CLIENT_ID: 'oauth',
    GMAIL_CLIENT_SECRET: 'oauth', GMAIL_REFRESH_TOKEN: 'api', GOOGLE_SERVICE_ACCOUNT_JSON: 'api',
    SLACK_BOT_TOKEN: 'messaging', SLACK_APP_TOKEN: 'messaging', SLACK_SIGNING_SECRET: 'messaging', SLACK_VERIFICATION_TOKEN: 'messaging',
    AUTH_USERNAME: 'auth', AUTH_PASSWORD: 'auth', HOOKS_TOKEN: 'auth', OPENCLAW_GATEWAY_TOKEN: 'auth',
    FIREFLIES_API_KEY: 'api', CLICKUP_API_KEY: 'api', N8N_API_KEY: 'api', GIT_PERSONAL_TOKEN: 'api'
};

function encrypt(value) {
    const iv = crypto.randomBytes(16);
    const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    let ciphertext = cipher.update(value, 'utf8');
    ciphertext = Buffer.concat([ciphertext, cipher.final()]);
    const tag = cipher.getAuthTag();
    return Buffer.concat([iv, tag, ciphertext]).toString('base64');
}

async function secretExists(keyName) {
    const { data } = await supabase.from('secrets').select('id').eq('key_name', keyName).eq('is_active', true).single();
    return !!data;
}

async function migrateSecret(keyName, dryRun = false) {
    const value = process.env[keyName];
    if (!value || value === '') return { status: 'skipped', reason: 'not set in environment' };
    
    if (!dryRun && options.skipExisting) {
        if (await secretExists(keyName)) return { status: 'skipped', reason: 'already exists' };
    }
    
    const category = SECRET_CATEGORIES[keyName] || 'api';
    if (dryRun) return { status: 'dry-run', category, valuePreview: value.substring(0, 10) + '...' };
    
    try {
        const encryptedValue = encrypt(value);
        const { error } = await supabase.from('secrets').upsert({
            key_name: keyName, encrypted_value: encryptedValue, environment: 'production',
            category: category, is_active: true, description: `Migrated on ${new Date().toISOString()}`,
            updated_at: new Date().toISOString()
        }, { onConflict: 'key_name' });
        
        if (error) return { status: 'error', error: error.message };
        return { status: 'success', category };
    } catch (err) {
        return { status: 'error', error: err.message };
    }
}

async function main() {
    console.log('🔐 Secret Migration (From Environment Variables)');
    console.log('='.repeat(60));
    console.log(`Supabase: ${SUPABASE_URL}`);
    console.log(`Dry run: ${options.dryRun ? 'YES' : 'NO'}`);
    console.log();
    
    const stats = { total: 0, migrated: 0, skipped: 0, errors: 0, byCategory: {} };
    
    for (const keyName of SECRETS_TO_MIGRATE) {
        if (options.verbose) process.stdout.write(`   ${keyName}... `);
        const result = await migrateSecret(keyName, options.dryRun);
        stats.total++;
        
        if (result.status === 'success') {
            stats.migrated++; stats.byCategory[result.category] = (stats.byCategory[result.category] || 0) + 1;
            if (options.verbose) console.log('✅ migrated');
        } else if (result.status === 'dry-run') {
            if (process.env[keyName]) { stats.byCategory[result.category] = (stats.byCategory[result.category] || 0) + 1; }
            if (options.verbose) console.log(process.env[keyName] ? `📝 would migrate (${result.category})` : '⏭️ not in env');
        } else if (result.status === 'skipped') {
            stats.skipped++;
            if (options.verbose) console.log(`⏭️ skipped (${result.reason})`);
        } else {
            stats.errors++;
            if (options.verbose) console.log(`❌ error: ${result.error}`);
        }
    }
    
    console.log();
    console.log('='.repeat(60));
    console.log('Migration Summary');
    console.log(`Total: ${stats.total}`);
    if (options.dryRun) {
        console.log(`Would migrate: ${Object.values(stats.byCategory).reduce((a, b) => a + b, 0)}`);
    } else {
        console.log(`Migrated: ${stats.migrated}`);
        console.log(`Skipped: ${stats.skipped}`);
        console.log(`Errors: ${stats.errors}`);
    }
    console.log('By category:', stats.byCategory);
    
    if (options.dryRun) {
        console.log('\n📝 This was a dry run. No changes were made.');
        console.log('   Run without --dry-run to perform actual migration.');
    } else if (stats.errors === 0) {
        console.log('\n✅ Migration complete!');
        console.log('   Save this ENCRYPTION_KEY securely - you will need it to decrypt secrets!');
        console.log(`   ENCRYPTION_KEY=${ENCRYPTION_KEY.substring(0, 10)}...`);
    } else {
        console.log('\n⚠️  Migration completed with errors.');
        process.exit(1);
    }
}

main().catch(err => {
    console.error('❌ Fatal error:', err.message);
    process.exit(1);
});

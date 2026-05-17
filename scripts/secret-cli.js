#!/usr/bin/env node
/**
 * Secret Management CLI
 * Command-line tool for managing secrets in Supabase
 * 
 * Usage:
 *   node scripts/secret-cli.js <command> [options]
 * 
 * Commands:
 *   list                    List all secrets
 *   get <key>               Get a secret value
 *   set <key> <value>       Set a secret value
 *   delete <key>            Delete (deactivate) a secret
 *   rotate <key>            Rotate a secret (increment version)
 *   health                  Show secret management health
 *   audit                   Show recent access logs
 *   export                  Export all secrets to JSON (encrypted backup)
 *   import <file>           Import secrets from JSON
 * 
 * Examples:
 *   node scripts/secret-cli.js list
 *   node scripts/secret-cli.js get OPENAI_API_KEY
 *   node scripts/secret-cli.js set MY_API_KEY "secret-value" --category api
 *   node scripts/secret-cli.js health
 *   node scripts/secret-cli.js audit --limit 50
 */

const { 
    getSecret, 
    storeSecret, 
    listSecrets, 
    deleteSecret, 
    getHealthStatus,
    encrypt,
    decrypt
} = require('../lib/secret-manager');
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Parse arguments
const args = process.argv.slice(2);
const command = args[0];

// Helper: parse options
function parseOptions(args) {
    const options = {};
    for (let i = 0; i < args.length; i++) {
        if (args[i].startsWith('--')) {
            const key = args[i].replace('--', '').replace(/-/g, '_');
            const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
            options[key] = value;
            if (value !== true) i++;
        }
    }
    return options;
}

const options = parseOptions(args);

// Commands
async function cmdList() {
    console.log('🔐 Secrets List');
    console.log('=' .repeat(80));
    
    const secrets = await listSecrets();
    
    if (secrets.length === 0) {
        console.log('No secrets found.');
        return;
    }
    
    console.log(`Found ${secrets.length} secrets:\n`);
    console.log(`${'Name'.padEnd(30)} ${'Category'.padEnd(12)} ${'Env'.padEnd(8)} ${'Version'.padEnd(8)} ${'Status'.padEnd(10)} ${'Expires'}`);
    console.log('-'.repeat(80));
    
    for (const s of secrets) {
        const status = s.is_active ? '✅ active' : '❌ inactive';
        const expires = s.expires_at 
            ? new Date(s.expires_at).toISOString().split('T')[0]
            : 'never';
        console.log(
            `${s.key_name.padEnd(30)} ` +
            `${s.category.padEnd(12)} ` +
            `${s.environment.padEnd(8)} ` +
            `${String(s.version).padEnd(8)} ` +
            `${status.padEnd(10)} ` +
            `${expires}`
        );
    }
}

async function cmdGet() {
    const keyName = args[1];
    if (!keyName) {
        console.error('❌ Error: Key name required');
        console.error('   Usage: node secret-cli.js get <key-name>');
        process.exit(1);
    }
    
    console.log(`🔐 Getting secret: ${keyName}`);
    
    try {
        const value = await getSecret(keyName, { recordAudit: false });
        console.log('\nValue:');
        console.log(value);
    } catch (err) {
        console.error(`❌ Error: ${err.message}`);
        process.exit(1);
    }
}

async function cmdSet() {
    const keyName = args[1];
    const value = args[2];
    
    if (!keyName || !value) {
        console.error('❌ Error: Key name and value required');
        console.error('   Usage: node secret-cli.js set <key-name> <value> [--category <cat>]');
        process.exit(1);
    }
    
    console.log(`🔐 Setting secret: ${keyName}`);
    
    const metadata = {
        category: options.category || 'api',
        environment: options.environment || 'production',
        description: options.description || `Set via CLI on ${new Date().toISOString()}`
    };
    
    try {
        await storeSecret(keyName, value, metadata);
        console.log('✅ Secret stored successfully');
    } catch (err) {
        console.error(`❌ Error: ${err.message}`);
        process.exit(1);
    }
}

async function cmdDelete() {
    const keyName = args[1];
    if (!keyName) {
        console.error('❌ Error: Key name required');
        process.exit(1);
    }
    
    console.log(`🔐 Deleting secret: ${keyName}`);
    console.log('⚠️  This will deactivate the secret (soft delete)');
    
    if (!options.force) {
        console.log('\nAdd --force to confirm deletion');
        process.exit(1);
    }
    
    try {
        await deleteSecret(keyName);
        console.log('✅ Secret deleted successfully');
    } catch (err) {
        console.error(`❌ Error: ${err.message}`);
        process.exit(1);
    }
}

async function cmdHealth() {
    console.log('🏥 Secret Management Health');
    console.log('=' .repeat(50));
    
    const health = await getHealthStatus();
    
    console.log(`\nTotal secrets: ${health.total_secrets}`);
    console.log(`Active secrets: ${health.active_secrets}`);
    console.log(`Expiring within 7 days: ${health.expiring_soon || 0}`);
    console.log(`Expired: ${health.expired || 0}`);
    
    // Get recent access stats
    const { data: recentAccess } = await supabase
        .from('secret_access_logs')
        .select('*')
        .gte('accessed_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());
    
    if (recentAccess) {
        const successCount = recentAccess.filter(a => a.success).length;
        const failCount = recentAccess.filter(a => !a.success).length;
        
        console.log(`\nLast 24 hours:`);
        console.log(`  Access attempts: ${recentAccess.length}`);
        console.log(`  Successful: ${successCount}`);
        console.log(`  Failed: ${failCount}`);
    }
}

async function cmdAudit() {
    const limit = parseInt(options.limit) || 20;
    
    console.log('📋 Recent Secret Access Logs');
    console.log('=' .repeat(100));
    
    const { data: logs, error } = await supabase
        .from('secret_access_logs')
        .select('*')
        .order('accessed_at', { ascending: false })
        .limit(limit);
    
    if (error) {
        console.error('❌ Error fetching logs:', error.message);
        process.exit(1);
    }
    
    if (!logs || logs.length === 0) {
        console.log('No access logs found.');
        return;
    }
    
    console.log(`\nShowing last ${logs.length} access attempts:\n`);
    console.log(`${'Time'.padEnd(20)} ${'Key'.padEnd(25)} ${'Agent'.padEnd(15)} ${'Type'.padEnd(10)} ${'Status'}`);
    console.log('-'.repeat(100));
    
    for (const log of logs) {
        const time = new Date(log.accessed_at).toISOString().replace('T', ' ').substring(0, 19);
        const status = log.success ? '✅ success' : `❌ ${log.error_message?.substring(0, 20) || 'failed'}`;
        console.log(
            `${time.padEnd(20)} ` +
            `${log.key_name.substring(0, 25).padEnd(25)} ` +
            `${(log.agent_id || 'unknown').substring(0, 15).padEnd(15)} ` +
            `${log.access_type.padEnd(10)} ` +
            `${status}`
        );
    }
}

async function cmdExport() {
    const outputFile = options.output || `secrets-backup-${new Date().toISOString().split('T')[0]}.json`;
    
    console.log('📦 Exporting secrets...');
    
    const { data: secrets, error } = await supabase
        .from('secrets')
        .select('*')
        .eq('is_active', true);
    
    if (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
    
    const exportData = {
        exported_at: new Date().toISOString(),
        count: secrets.length,
        secrets: secrets
    };
    
    fs.writeFileSync(outputFile, JSON.stringify(exportData, null, 2));
    console.log(`✅ Exported ${secrets.length} secrets to ${outputFile}`);
    console.log('⚠️  Warning: This file contains encrypted secrets. Keep it secure!');
}

async function cmdImport() {
    const inputFile = args[1];
    if (!inputFile) {
        console.error('❌ Error: Input file required');
        console.error('   Usage: node secret-cli.js import <file> [--dry-run]');
        process.exit(1);
    }
    
    if (!fs.existsSync(inputFile)) {
        console.error(`❌ Error: File not found: ${inputFile}`);
        process.exit(1);
    }
    
    const importData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
    
    console.log(`📦 Importing secrets from ${inputFile}`);
    console.log(`   Exported at: ${importData.exported_at}`);
    console.log(`   Secrets count: ${importData.secrets.length}`);
    
    if (options.dry_run) {
        console.log('\n📝 Dry run mode - no changes will be made');
        console.log('Secrets that would be imported:');
        for (const s of importData.secrets) {
            console.log(`  - ${s.key_name} (${s.category})`);
        }
        return;
    }
    
    let imported = 0;
    let errors = 0;
    
    for (const s of importData.secrets) {
        try {
            const { error } = await supabase
                .from('secrets')
                .upsert({
                    key_name: s.key_name,
                    encrypted_value: s.encrypted_value,
                    environment: s.environment,
                    category: s.category,
                    description: s.description,
                    is_active: true,
                    updated_at: new Date().toISOString()
                }, { onConflict: 'key_name' });
            
            if (error) {
                console.error(`❌ Failed to import ${s.key_name}: ${error.message}`);
                errors++;
            } else {
                imported++;
            }
        } catch (err) {
            console.error(`❌ Failed to import ${s.key_name}: ${err.message}`);
            errors++;
        }
    }
    
    console.log(`\n✅ Imported: ${imported}`);
    if (errors > 0) {
        console.log(`❌ Errors: ${errors}`);
    }
}

// Main
async function main() {
    switch (command) {
        case 'list':
            await cmdList();
            break;
        case 'get':
            await cmdGet();
            break;
        case 'set':
            await cmdSet();
            break;
        case 'delete':
            await cmdDelete();
            break;
        case 'health':
            await cmdHealth();
            break;
        case 'audit':
            await cmdAudit();
            break;
        case 'export':
            await cmdExport();
            break;
        case 'import':
            await cmdImport();
            break;
        default:
            console.log('🔐 Secret Management CLI');
            console.log();
            console.log('Usage: node secret-cli.js <command> [options]');
            console.log();
            console.log('Commands:');
            console.log('  list                           List all secrets');
            console.log('  get <key>                      Get a secret value');
            console.log('  set <key> <value>              Set a secret value');
            console.log('  delete <key> --force           Delete a secret');
            console.log('  health                         Show health status');
            console.log('  audit --limit 50               Show access logs');
            console.log('  export --output file.json      Export secrets');
            console.log('  import file.json               Import secrets');
            console.log();
            console.log('Environment Variables:');
            console.log('  SUPABASE_URL, SUPABASE_SERVICE_KEY, ENCRYPTION_KEY');
    }
}

main().catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
});

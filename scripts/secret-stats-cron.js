#!/usr/bin/env node
/**
 * Secret Management Stats Calculation Script
 * 
 * Calculates daily secret management statistics and updates the database.
 * Run via: node scripts/secret-stats-cron.js
 */

const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function main() {
    console.log('🔐 Secret Management Stats Calculation');
    console.log('=' .repeat(60));
    console.log(`Date: ${new Date().toISOString()}`);
    console.log();

    try {
        const dateStr = new Date().toISOString().split('T')[0];
        console.log(`Calculating stats for ${dateStr}...`);

        const start = Date.now();
        const { data, error } = await supabase.rpc('calculate_daily_secret_stats', { p_date: dateStr });
        const elapsed = Date.now() - start;

        if (error) {
            console.error('❌ Error calculating stats:', error.message);
            process.exit(1);
        }

        console.log(`✅ Stats calculated successfully in ${elapsed}ms`);
        console.log('=' .repeat(60));
        process.exit(0);
    } catch (err) {
        console.error('❌ Unexpected error:', err.message);
        process.exit(1);
    }
}

main();

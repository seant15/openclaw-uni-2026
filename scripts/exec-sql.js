const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const sql = fs.readFileSync('security/sql/complete-schema.sql', 'utf8');

// Split and clean SQL statements
const statements = sql
  .split(';')
  .map(s => s.trim())
  .filter(s => s.length > 0 && !s.startsWith('--'))
  .map(s => s + ';');

console.log(`Found ${statements.length} SQL statements to execute`);
console.log('');

const results = {
  success: 0,
  failed: 0,
  errors: []
};

async function executeStatement(stmt, index) {
  try {
    // Try using the SQL API
    const response = await fetch(`${process.env.SUPABASE_URL}/rest/v1/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_KEY}`,
        'apikey': process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_KEY
      },
      body: JSON.stringify({ query: stmt })
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(error);
    }
    
    results.success++;
    return true;
  } catch (err) {
    results.failed++;
    results.errors.push({ index: index + 1, error: err.message.substring(0, 100) });
    return false;
  }
}

async function main() {
  // Execute core table creation statements first
  const coreStatements = statements.filter(s => 
    s.includes('CREATE TABLE') || 
    s.includes('CREATE EXTENSION') ||
    s.includes('CREATE INDEX') ||
    s.includes('CREATE POLICY')
  );
  
  console.log(`Executing ${coreStatements.length} core statements...`);
  
  for (let i = 0; i < coreStatements.length; i++) {
    const stmt = coreStatements[i];
    const tableName = stmt.match(/CREATE TABLE IF NOT EXISTS (\w+)/)?.[1] || 'unknown';
    
    process.stdout.write(`  [${i + 1}/${coreStatements.length}] ${tableName}... `);
    
    const success = await executeStatement(stmt, i);
    console.log(success ? '✅' : '❌');
  }
  
  console.log('');
  console.log('Results:');
  console.log(`  Success: ${results.success}`);
  console.log(`  Failed: ${results.failed}`);
  
  if (results.errors.length > 0) {
    console.log('');
    console.log('Errors (first 5):');
    results.errors.slice(0, 5).forEach(e => {
      console.log(`  Statement ${e.index}: ${e.error}`);
    });
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});

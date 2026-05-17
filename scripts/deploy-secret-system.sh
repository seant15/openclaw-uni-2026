#!/bin/bash
# =====================================================
# Secret Management System - Deployment Script
# =====================================================
# Run this script to deploy the secret management system
#
# Usage:
#   ./scripts/deploy-secret-system.sh
# =====================================================

set -e

WORKSPACE_DIR="/data/workspace"
BACKUP_DIR="${WORKSPACE_DIR}/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔐 Secret Management System Deployment"
echo "======================================"
echo ""

# Step 1: Backup current state
echo -e "${BLUE}Step 1: Creating backup...${NC}"
if [ -f "${WORKSPACE_DIR}/scripts/backup-secrets.sh" ]; then
    "${WORKSPACE_DIR}/scripts/backup-secrets.sh"
    echo -e "${GREEN}✅ Backup created${NC}"
else
    echo -e "${YELLOW}⚠️  Backup script not found, skipping...${NC}"
fi
echo ""

# Step 2: Check prerequisites
echo -e "${BLUE}Step 2: Checking prerequisites...${NC}"

# Check Supabase credentials
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set${NC}"
    echo "Please ensure these are in your environment"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo ""

# Step 3: Generate or get ENCRYPTION_KEY
echo -e "${BLUE}Step 3: Setting up ENCRYPTION_KEY...${NC}"
if [ -z "$ENCRYPTION_KEY" ]; then
    echo "Generating new ENCRYPTION_KEY..."
    export ENCRYPTION_KEY=$(openssl rand -base64 32)
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Save this key!${NC}"
    echo "ENCRYPTION_KEY=${ENCRYPTION_KEY}"
    echo ""
    echo "Add this to your environment to make it permanent:"
    echo "  export ENCRYPTION_KEY=${ENCRYPTION_KEY}"
    echo ""
else
    echo "Using existing ENCRYPTION_KEY"
fi
echo ""

# Step 4: Dry run migration
echo -e "${BLUE}Step 4: Dry run migration...${NC}}
cd "${WORKSPACE_DIR}"
node scripts/migrate-secrets.js --dry-run --verbose
echo ""

# Step 5: Confirm migration
echo -e "${YELLOW}⚠️  Ready to migrate secrets from environment variables${NC}"
echo ""
read -p "Continue with migration? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi
echo ""

# Step 6: Run migration
echo -e "${BLUE}Step 6: Running migration...${NC}"
node scripts/migrate-secrets.js --verbose
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Migration complete${NC}"
echo ""

# Step 7: Verify
echo -e "${BLUE}Step 7: Verifying installation...${NC}"
node scripts/secret-cli.js list
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Verification failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Verification passed${NC}"
echo ""

# Step 8: Test agent bootstrap
echo -e "${BLUE}Step 8: Testing agent bootstrap...${NC}"
node scripts/agent-bootstrap.js
echo -e "${GREEN}✅ Bootstrap test passed${NC}"
echo ""

# Step 9: Generate OpenClaw cron config
echo -e "${BLUE}Step 9: Generating OpenClaw cron configuration...${NC}"

cat > "${WORKSPACE_DIR}/security/config/secret-management-cron.json" << EOF
{
  "jobs": [
    {
      "name": "secret-health-daily",
      "schedule": "0 1 * * *",
      "command": "cd /data/workspace && ENCRYPTION_KEY=\${ENCRYPTION_KEY} node scripts/secret-health-cron.js --report",
      "description": "Daily secret management health check with Slack report",
      "enabled": true,
      "timezone": "UTC"
    },
    {
      "name": "secret-stats-calculate",
      "schedule": "0 2 * * *",
      "command": "cd /data/workspace && ENCRYPTION_KEY=\${ENCRYPTION_KEY} node -e \"const {createClient} = require('@supabase/supabase-js'); createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY).rpc('calculate_daily_secret_stats', {p_date: new Date().toISOString().split('T')[0]})\"",
      "description": "Calculate daily secret management statistics",
      "enabled": true,
      "timezone": "UTC"
    },
    {
      "name": "secret-backup-weekly",
      "schedule": "0 3 * * 0",
      "command": "cd /data/workspace && ./scripts/backup-secrets.sh",
      "description": "Weekly backup of secret management system",
      "enabled": true,
      "timezone": "UTC"
    }
  ]
}
EOF

echo -e "${GREEN}✅ Cron configuration generated${NC}"
echo ""
echo "Cron jobs configured:"
echo "  - Daily health check (01:00 UTC)"
echo "  - Daily stats calculation (02:00 UTC)"
echo "  - Weekly backup (03:00 UTC Sunday)"
echo ""

# Step 10: Create environment setup script
echo -e "${BLUE}Step 10: Creating environment setup script...${NC}"

cat > "${WORKSPACE_DIR}/scripts/setup-secret-env.sh" << EOF
#!/bin/bash
# Source this file to set up secret management environment
# Usage: source /data/workspace/scripts/setup-secret-env.sh

export ENCRYPTION_KEY="${ENCRYPTION_KEY}"
echo "✅ Secret management environment configured"
echo "   ENCRYPTION_KEY is set"
EOF

chmod +x "${WORKSPACE_DIR}/scripts/setup-secret-env.sh"
echo -e "${GREEN}✅ Environment setup script created${NC}"
echo ""

# Step 11: Summary
echo "======================================"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "IMPORTANT: Save your ENCRYPTION_KEY!"
echo "  ${ENCRYPTION_KEY}"
echo ""
echo "Next steps:"
echo "  1. Add ENCRYPTION_KEY to your permanent environment"
echo "  2. Source the setup script: source scripts/setup-secret-env.sh"
echo "  3. Import cron jobs into OpenClaw:"
echo "     ${WORKSPACE_DIR}/security/config/secret-management-cron.json"
echo "  4. Test with: node scripts/agent-bootstrap.js"
echo "  5. Monitor #alerts channel for daily reports"
echo ""
echo "Rollback (if needed):"
echo "  cd ${BACKUP_DIR}/secrets-latest \u0026\u0026 ./restore.sh"
echo ""
echo "Backup location:"
echo "  ${BACKUP_DIR}/secrets-latest"
echo ""

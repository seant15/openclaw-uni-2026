#!/bin/bash
# =====================================================
# Secret Management System - Backup Script
# =====================================================
# This script creates a backup of the secret management
# configuration and encrypted secrets for disaster recovery.
#
# Usage:
#   ./scripts/backup-secrets.sh [output-dir]
#
# Default output: /data/workspace/backups/secrets-YYYYMMDD-HHMMSS
# =====================================================

set -e

# Configuration
WORKSPACE_DIR="/data/workspace"
DEFAULT_BACKUP_DIR="${WORKSPACE_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="secrets-${TIMESTAMP}"
BACKUP_DIR="${1:-${DEFAULT_BACKUP_DIR}/${BACKUP_NAME}}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔐 Secret Management Backup"
echo "============================"
echo "Backup directory: ${BACKUP_DIR}"
echo ""

# Check required environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set${NC}"
    exit 1
fi

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup 1: Export secrets from Supabase
echo "📦 Exporting secrets from Supabase..."
node "${WORKSPACE_DIR}/scripts/secret-cli.js" export --output "${BACKUP_DIR}/secrets-export.json" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Secrets exported${NC}"
else
    echo -e "${RED}❌ Failed to export secrets${NC}"
    exit 1
fi

# Backup 2: SDK and scripts
echo "📦 Backing up SDK and scripts..."
cp -r "${WORKSPACE_DIR}/lib" "${BACKUP_DIR}/"
cp -r "${WORKSPACE_DIR}/scripts" "${BACKUP_DIR}/"
echo -e "${GREEN}✅ SDK and scripts backed up${NC}"

# Backup 3: SQL schema
echo "📦 Backing up SQL schema..."
if [ -f "${WORKSPACE_DIR}/security/sql/complete-schema.sql" ]; then
    cp "${WORKSPACE_DIR}/security/sql/complete-schema.sql" "${BACKUP_DIR}/schema.sql"
    echo -e "${GREEN}✅ Schema backed up${NC}"
else
    echo -e "${YELLOW}⚠️  Schema file not found${NC}"
fi

# Backup 4: Environment configuration (sanitized)
echo "📦 Backing up environment configuration..."
cat > "${BACKUP_DIR}/environment.txt" << EOF
# Secret Management Environment Backup
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# Note: This file does NOT contain actual secret values

SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=***REDACTED***
ENCRYPTION_KEY=***REDACTED***

# Backup metadata
BACKUP_TIMESTAMP=${TIMESTAMP}
BACKUP_VERSION=1.0
EOF
echo -e "${GREEN}✅ Environment configuration backed up${NC}"

# Backup 5: Create restore script
echo "📦 Creating restore script..."
cat > "${BACKUP_DIR}/restore.sh" << 'EOF'
#!/bin/bash
# Secret Management Restore Script
# Usage: ./restore.sh

set -e

echo "🔐 Secret Management Restore"
echo "============================"

# Check environment
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
    exit 1
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "❌ Error: ENCRYPTION_KEY must be set"
    exit 1
fi

# Confirm
read -p "⚠️  This will restore secrets to Supabase. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Restore schema
echo "📦 Restoring schema..."
if [ -f "schema.sql" ]; then
    echo "   Schema file found (manual restore required)"
    echo "   Run: psql \$DATABASE_URL < schema.sql"
fi

# Restore secrets
echo "📦 Restoring secrets..."
if [ -f "secrets-export.json" ]; then
    node scripts/secret-cli.js import secrets-export.json
    echo "✅ Secrets restored"
else
    echo "❌ secrets-export.json not found"
    exit 1
fi

echo ""
echo "✅ Restore complete!"
echo "   Next steps:"
echo "   1. Verify secrets: node scripts/secret-cli.js list"
echo "   2. Test agent bootstrap: node scripts/agent-bootstrap.js"
EOF
chmod +x "${BACKUP_DIR}/restore.sh"
echo -e "${GREEN}✅ Restore script created${NC}"

# Create backup manifest
echo "📦 Creating backup manifest..."
cat > "${BACKUP_DIR}/MANIFEST.json" << EOF
{
  "backup_name": "${BACKUP_NAME}",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "1.0",
  "contents": [
    "secrets-export.json - Encrypted secrets export",
    "lib/ - SecretManager SDK",
    "scripts/ - Management scripts",
    "schema.sql - Database schema",
    "environment.txt - Environment configuration (sanitized)",
    "restore.sh - Restore script"
  ],
  "restore_instructions": [
    "1. Set environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY, ENCRYPTION_KEY",
    "2. Run: ./restore.sh",
    "3. Verify: node scripts/secret-cli.js list"
  ]
}
EOF
echo -e "${GREEN}✅ Manifest created${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)

echo ""
echo "============================"
echo -e "${GREEN}✅ Backup complete!${NC}"
echo "Backup location: ${BACKUP_DIR}"
echo "Backup size: ${BACKUP_SIZE}"
echo ""
echo "To restore from this backup:"
echo "  1. cd ${BACKUP_DIR}"
echo "  2. ./restore.sh"
echo ""
echo "To verify backup:"
echo "  node ${BACKUP_DIR}/scripts/secret-cli.js list"
echo ""

# Create symlink to latest backup
LATEST_LINK="${DEFAULT_BACKUP_DIR}/secrets-latest"
rm -f "${LATEST_LINK}"
ln -s "${BACKUP_DIR}" "${LATEST_LINK}"
echo "Latest backup symlink: ${LATEST_LINK}"

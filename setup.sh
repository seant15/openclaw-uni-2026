#!/bin/bash
# Quick Setup Script for OpenClaw Infrastructure
# Run this on a fresh VPS to get everything running

set -e

echo "🦞 OpenClaw Infrastructure Setup"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root (use sudo)${NC}"
   exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the uni-openclaw-infra directory"
    exit 1
fi

echo "✅ Found docker-compose.yml"
echo ""

# Step 1: Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi
echo "✅ Docker installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
    apt-get update
    apt-get install -y docker-compose-plugin
fi
echo "✅ Docker Compose installed"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git not found. Installing...${NC}"
    apt-get update
    apt-get install -y git
fi
echo "✅ Git installed"

echo ""

# Step 2: Create directories
echo "📁 Creating directories..."
mkdir -p /data/.openclaw
mkdir -p /data/backups/openclaw
mkdir -p /var/log
touch /var/log/openclaw-backup.log
echo "✅ Directories created"
echo ""

# Step 3: Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh
chmod 755 /data/.openclaw
chmod 755 /data/backups
chmod 755 /data/backups/openclaw
echo "✅ Permissions set"
echo ""

# Step 4: Check environment file
echo "⚙️  Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo "Creating from .env.example..."
        cp .env.example .env
        echo -e "${RED}⚠️  IMPORTANT: Edit .env and add your API keys!${NC}"
        echo ""
    fi
else
    echo "✅ .env file found"
fi
echo ""

# Step 5: Initial backup
echo "💾 Creating initial backup..."
if [ -d "/data/.openclaw/agents" ]; then
    ./scripts/backup.sh
    echo "✅ Backup created"
else
    echo "ℹ️  No existing data to backup (fresh install)"
fi
echo ""

# Step 6: Setup cron
echo "⏰ Setting up backup cron job..."
CRON_JOB="0 3 * * * /data/uni-openclaw-infra/scripts/backup.sh >> /var/log/openclaw-backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "openclaw"; then
    echo "✅ Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added"
fi
echo ""

# Step 7: Start services
echo "🚀 Starting OpenClaw services..."
docker-compose up -d
echo "✅ Services started"
echo ""

# Step 8: Health check
echo "🏥 Running health checks..."
sleep 5

# Check container is running
if docker ps | grep -q "openclaw-gateway"; then
    echo -e "${GREEN}✅ Container is running${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

# Check if gateway responds (if openclaw CLI is available)
if command -v openclaw &> /dev/null; then
    if openclaw status &> /dev/null; then
        echo -e "${GREEN}✅ Gateway is responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Gateway not responding yet (may need more time)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  openclaw CLI not found, skipping gateway check${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   vim .env"
echo ""
echo "2. Restart services to load new env:"
echo "   docker-compose restart"
echo ""
echo "3. Verify installation:"
echo "   docker-compose ps"
echo "   docker-compose logs -f"
echo ""
echo "4. Test backup:"
echo "   ./scripts/backup.sh"
echo ""
echo "5. Access OpenClaw:"
echo "   http://YOUR_VPS_IP:18789"
echo ""
echo "Documentation:"
echo "   - Deployment Guide: COOLIFY_DEPLOYMENT_GUIDE.md"
echo "   - Architecture: ARCHITECTURE.md"
echo "   - Troubleshooting: TROUBLESHOOTING.md"
echo ""

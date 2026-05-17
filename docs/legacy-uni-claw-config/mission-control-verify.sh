#!/bin/bash
# OpenClaw Mission Control - Verification Script

echo "🔍 OpenClaw Mission Control Installation Verification"
echo "=================================================="

# Check if directory exists
if [ -d "openclaw-mission-control" ]; then
    echo "✅ Repository cloned successfully"
    cd openclaw-mission-control
else
    echo "❌ Repository not found. Please clone first."
    exit 1
fi

# Check required files
echo -e "\n📁 Checking required files:"
files=("compose.yml" ".env.example" "frontend" "backend" "docs")
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

# Check .env file
echo -e "\n⚙️  Environment configuration:"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Check critical variables
    if grep -q "LOCAL_AUTH_TOKEN=.*[a-zA-Z0-9]" .env; then
        token_length=$(grep "LOCAL_AUTH_TOKEN=" .env | cut -d'=' -f2 | wc -c)
        if [ $token_length -gt 50 ]; then
            echo "✅ AUTH_TOKEN configured (${token_length} chars)"
        else
            echo "⚠️  AUTH_TOKEN too short (${token_length} chars, need 50+)"
        fi
    else
        echo "❌ LOCAL_AUTH_TOKEN not set"
    fi
    
    if grep -q "POSTGRES_PASSWORD=.*[a-zA-Z0-9]" .env; then
        echo "✅ Database password configured"
    else
        echo "❌ POSTGRES_PASSWORD not set"
    fi
else
    echo "❌ .env file missing - copy from .env.example"
fi

# Check Docker availability
echo -e "\n🐳 Docker environment:"
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker available: $(docker --version)"
    if command -v docker compose >/dev/null 2>&1; then
        echo "✅ Docker Compose available: $(docker compose version)"
    else
        echo "❌ Docker Compose not available"
    fi
else
    echo "❌ Docker not available"
fi

# Check port availability
echo -e "\n🔌 Port availability:"
ports=(3000 8000 5432)
for port in "${ports[@]}"; do
    if ! ss -tlnp | grep -q ":$port "; then
        echo "✅ Port $port available"
    else
        echo "⚠️  Port $port in use"
    fi
done

echo -e "\n🚀 Ready to start? Run: docker compose up -d"
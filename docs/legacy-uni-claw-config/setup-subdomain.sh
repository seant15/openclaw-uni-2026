#!/bin/bash
# 配置子域名 dash.open.unippc24.com

cd /data/openclaw-control-center

echo "=========================================="
echo "🔧 配置子域名"
echo "=========================================="
echo ""

echo "📋 当前状态:"
echo "  open.unippc24.com → OpenClaw Web UI (9090)"
echo "  dash.open.unippc24.com → Control Center (9091) [建议]"
echo ""

echo "1️⃣ 更新 .env 配置..."

# 更新 UI URL
sed -i 's|OPENCLAW_CONTROL_UI_URL=.*|OPENCLAW_CONTROL_UI_URL=https://dash.open.unippc24.com/|' .env

# 添加 Gateway Token
echo "GATEWAY_TOKEN=uni-random-token" >> .env

echo "   ✅ 已更新:"
grep -E "OPENCLAW_CONTROL_UI_URL|GATEWAY_TOKEN" .env
echo ""

echo "2️⃣ 停止当前服务..."
pkill -9 -f "dev:ui" 2>/dev/null || true
sleep 2
echo "   ✅ 已停止"
echo ""

echo "3️⃣ 启动服务..."
nohup npm run dev:ui > /tmp/control-center.log 2>&1 &
echo $! > /tmp/control-center.pid

sleep 3

if ss -tlnp | grep -q ":9091"; then
    echo "   ✅ 服务已启动"
else
    echo "   ⚠️  启动可能有问题"
    tail -10 /tmp/control-center.log
fi
echo ""

echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="
echo ""
echo "📋 访问地址:"
echo "   OpenClaw UI:  https://open.unippc24.com/"
echo "   Control Center: https://dash.open.unippc24.com/"
echo ""
echo "🔐 Gateway Token: uni-random-token"
echo "   (在 Control Center Settings 中配置)"
echo ""
echo "⚠️  Coolify 配置提醒:"
echo "   确保 dash.open.unippc24.com 指向 9091 端口"
echo ""
echo "=========================================="
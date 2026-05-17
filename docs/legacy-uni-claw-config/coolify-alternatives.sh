#!/bin/bash
# Coolify 限制下的替代方案

echo "=========================================="
echo "🔄 Coolify 限制下的解决方案"
echo "=========================================="
echo ""

echo "📋 问题: Coolify 界面没有地方添加新域名"
echo ""

echo "=========================================="
echo "💡 方案 A: 使用路径区分 (推荐)"
echo "=========================================="
echo ""
echo "如果 Coolify 只支持一个域名，可以用路径区分:"
echo ""
echo "  open.unippc24.com/          → OpenClaw Web UI (9090)"
echo "  open.unippc24.com/control/  → Control Center (9091)"
echo ""
echo "需要配置 Nginx 反向代理:"
echo ""
cat << 'NGINX'
server {
    listen 80;
    server_name open.unippc24.com;
    
    # OpenClaw Web UI (默认)
    location / {
        proxy_pass http://localhost:9090;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Control Center
    location /control/ {
        proxy_pass http://localhost:9091/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
NGINX
echo ""

echo "=========================================="
echo "💡 方案 B: 手动添加 A 记录 + 独立端口"
echo "=========================================="
echo ""
echo "1. 在 DNS 提供商处手动添加:"
echo "   dash.open.unippc24.com A 194.238.31.45"
echo ""
echo "2. 然后直接访问:"
echo "   https://dash.open.unippc24.com:9091/"
echo "   (带端口号，绕过 Coolify)"
echo ""

echo "=========================================="
echo "💡 方案 C: 修改现有 Coolify 配置"
echo "=========================================="
echo ""
echo "检查 Coolify 是否有 'Advanced' 或 'Custom Nginx' 配置:"
echo ""
echo "1. 进入 Coolify Dashboard"
echo "2. 找到你的服务"
echo "3. 查看是否有:"
echo "   - Advanced Settings"
echo "4. 如果有，可以添加自定义 Nginx 配置"
echo ""

echo "=========================================="
echo "🚀 快速测试方案 B"
echo "=========================================="
echo ""
echo "先测试直接访问 (带端口):"
echo "  https://194.238.31.45:9091/"
echo ""
echo "如果这能工作，说明服务正常，只是域名配置问题。"
echo ""

echo "=========================================="
echo "❓ 请确认"
echo "=========================================="
echo ""
echo "1. Coolify 界面有没有 'Advanced' 或 'Custom Domain' 选项?"
echo "2. 你能访问 DNS 管理添加 A 记录吗?"
echo "3. 或者你偏好方案 A (路径区分) ?"
echo ""
echo "=========================================="
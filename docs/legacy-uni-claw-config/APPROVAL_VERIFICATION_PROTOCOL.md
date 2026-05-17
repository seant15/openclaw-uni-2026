# Approval 前自动验证协议

## 🎯 目的
在每次向 Sean 寻求 approval 之前，自动验证相关服务状态，减少来回确认。

## 📋 验证清单

### 对于 OpenClaw Control Center 相关请求

在寻求 approval 前，必须运行：

```bash
bash /data/workspace/verify-control-center.sh
```

**验证项：**
- [ ] 端口 9090 可连接
- [ ] HTTP 200 OK
- [ ] 页面包含 "OpenClaw" 标识
- [ ] 关键模块存在 (Chat, Overview, Sessions, Agents, Config)
- [ ] 响应时间 < 2秒

### 对于 VPS/部署相关请求

- [ ] SSH 可连接
- [ ] 相关服务进程运行中
- [ ] 端口监听正常
- [ ] 日志无异常错误

### 对于数据库相关请求

- [ ] 数据库连接正常
- [ ] 相关表存在
- [ ] 查询响应正常

## 🤖 自动化流程

### 当需要 Approval 时：

1. **自动验证** → 运行对应验证脚本
2. **截图/证据** → 浏览器截图或日志片段
3. **报告状态** → 明确告知验证结果
4. **寻求 Approval** → 基于验证结果提出请求

### 验证结果格式：

```
✅ 自动验证完成
━━━━━━━━━━━━━━━━━━━━
服务: OpenClaw Control Center
URL: http://194.238.31.45:9090/dashboard/
状态: 🟢 正常运行
检查项: 5/5 通过
━━━━━━━━━━━━━━━━━━━━
[具体请求内容...]
```

## 📝 当前已验证状态

**OpenClaw Control Center:**
- 访问地址: http://194.238.31.45:9090/dashboard/
- 状态: ✅ 可访问
- 注意: 需要 HTTPS 或 localhost 才能完全使用 Gateway 功能

## ⚠️ 已知限制

1. **Gateway 连接**: 由于浏览器安全策略，非 HTTPS/localhost 环境下 WebSocket 连接受限
2. **功能降级**: 部分功能可能需要本地访问或使用 HTTPS

## 🔧 快速修复命令

```bash
# 启动服务
cd /data/openclaw-control-center
npm run dev:ui

# 验证服务
bash /data/workspace/verify-control-center.sh
```
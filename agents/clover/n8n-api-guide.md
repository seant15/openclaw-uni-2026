# N8N API 访问指南

> 自动生成的 n8n 系统文档 - 所有 agent 共享
> 更新时间: 2026-03-16

## 连接信息

| 项目 | 值 |
|------|-----|
| **Instance URL** | `https://n8n2.uni-agency.com` |
| **API Key** | `${N8N_API_KEY}` (环境变量) |
| **Project ID** | `dk90Cm7v33JIt3sp` (UNI PPC Project) |
| **Base URL** | `https://n8n2.uni-agency.com/api/v1` |

## 认证方式

```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n2.uni-agency.com/api/v1/workflows?projectId=dk90Cm7v33JIt3sp"
```

## CLI 工具

```bash
# 基础命令
n8n list                          # 列出项目工作流
n8n get <id>                      # 获取工作流详情
n8n executions <id> [limit]       # 查看执行记录
n8n status                        # 系统状态
n
# 检查 UNI PPC 工作流
n8n check supabase                # 检查所有 Supabase 同步工作流
n8n check uni                     # 同上
```

---

## 🗄️ UNI PPC Supabase 实时数据同步工作流

> **位置**: `https://n8n2.uni-agency.com/projects/dk90Cm7v33JIt3sp`
> 
> **注意**: 必须使用 `projectId=dk90Cm7v33JIt3sp` 参数才能访问这些工作流

### 工作流概览

| ID | 名称 | 状态 | 创建时间 | 节点类型 |
|----|------|------|---------|---------|
| **97FtZv4md9MJmN1O** | **Daily Marketing Sync** | 🟢 Active | 2026-03-16 | Supabase + Postgres Trigger |
| **X9g0rGCDmqUXzhyQ** | **Hourly Performance Sync** | 🟢 Active | 2026-03-16 | Supabase + Postgres Trigger |
| **N5nNn0gkPWo3izoS** | **Alert Generation** | 🟢 Active | 2026-03-16 | Supabase + Postgres Trigger |
| **oH84CnJl6Vq2XsE9** | **Supabase Integration Test** | 🟢 Active | 2026-03-16 | Supabase + Postgres Trigger |

### 架构模式

所有工作流遵循统一架构：

```
Postgres Trigger (监听数据库变更)
    ↓
数据处理/转换 (Code/Set 节点)
    ↓
Supabase (upsert/insert/update 操作)
```

### 工作流详情

#### 1. Daily Marketing Sync (97FtZv4md9MJmN1O)
- **触发频率**: 基于 Postgres 事件
- **功能**: 每日营销数据同步
- **目标表**: Supabase marketing 相关表

#### 2. Hourly Performance Sync (X9g0rGCDmqUXzhyQ)
- **触发频率**: 基于 Postgres 事件
- **功能**: 每小时性能数据同步
- **目标表**: Supabase performance 相关表

#### 3. Alert Generation (N5nNn0gkPWo3izoS)
- **触发频率**: 基于 Postgres 事件
- **功能**: 告警生成
- **目标表**: Supabase alerts 相关表

#### 4. Supabase Integration Test (oH84CnJl6Vq2XsE9)
- **用途**: 测试连接和集成
- **状态**: Active (用于验证)

---

## 监控命令

```bash
# 检查所有 UNI PPC 工作流状态
n8n check supabase

# 查看特定工作流详情
n8n get 97FtZv4md9MJmN1O
n8n get X9g0rGCDmqUXzhyQ
n8n get N5nNn0gkPWo3izoS

# 查看执行历史
n8n executions 97FtZv4md9MJmN1O 20
```

---

## API 调用示例

```bash
# 获取项目工作流列表
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n2.uni-agency.com/api/v1/workflows?projectId=dk90Cm7v33JIt3sp"

# 获取特定工作流
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n2.uni-agency.com/api/v1/workflows/97FtZv4md9MJmN1O"

# 获取执行记录
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n2.uni-agency.com/api/v1/executions?workflowId=97FtZv4md9MJmN1O&limit=10"
```

---

## 故障排查

### 工作流找不到

**问题**: API 返回 404 或工作流不在列表中

**原因**: 必须使用 `projectId` 参数访问项目工作流

**解决**:
```bash
# ❌ 错误 - 默认只返回主项目工作流
curl ... /api/v1/workflows

# ✅ 正确 - 指定项目 ID
curl ... /api/v1/workflows?projectId=dk90Cm7v33JIt3sp
```

---

## 更新记录

- **2026-03-16**: 发现并记录 4 个正确的 UNI PPC Supabase 同步工作流
- **2026-03-16**: 修复 CLI 工具添加 `projectId` 参数支持
- **2026-03-16**: 添加故障排查指南

# 备份运行状况分析与三位一体协调方案

## 1. 加密云备份运行状况

### 1.1 当前状态: ⚠️ 需要关注

| 指标 | 状态 | 详情 |
|------|------|------|
| 最后成功备份 | 2026-03-29 19:18 UTC | ⚠️ 已过去8天 |
| 备份文件位置 | `/data/.openclaw/backups/` | 本地保留4个文件 |
| 云端目标 | Google Drive Shared Drive | `OpenClawBackups/{hostname}/` |
| Cron配置 | 存在 | `/data/workspace/cron/openclaw-backup.cron` |
| Cron执行 | ❌ 未验证 | 无日志输出 |

### 1.2 问题诊断

**根本问题**: Cronjob可能没有正确安装到系统

证据:
- `/var/log/syslog` 无相关记录
- `/var/log/cron.log` 不存在
- `crontab -l` 显示无crontab
- `/etc/crontab` 为空或不存在
- `/etc/cron.d/` 无openclaw相关配置

**当前cron配置仅存在于文件**: `/data/workspace/cron/openclaw-backup.cron`
但**未安装到系统cron**。

### 1.3 修复步骤

```bash
# 方法1: 添加到root crontab
crontab -e
# 添加以下行:
15 2 * * * /data/workspace/scripts/openclaw-full-backup.sh >> /data/.openclaw/logs/openclaw-backup-cron.log 2>&1

# 方法2: 安装到/etc/cron.d/ (推荐，便于团队查看)
sudo cp /data/workspace/cron/openclaw-backup.cron /etc/cron.d/openclaw-backup
sudo chmod 644 /etc/cron.d/openclaw-backup

# 验证cron服务运行
service cron status  # 或 systemctl status cron
```

### 1.4 优化建议

1. **监控增强**:
   - 添加备份成功/失败的Slack通知（脚本已支持）
   - 每周发送备份状态摘要
   - 设置备份超过24小时未运行的告警

2. **备份验证**:
   - 每月一次恢复测试（从Google Drive下载并解密验证）
   - 记录恢复时间目标(RTO)

3. **成本控制**:
   - 当前备份大小约55MB/天，云端14天保留 = ~770MB
   - 新增workspace备份后预计增至~150MB/天
   - 监控Google Drive存储使用

---

## 2. 三位一体协调方案 (VPS ↔ Git Repo ↔ 本地备份)

### 2.1 角色定义

| 层级 | 用途 | 适用场景 |
|------|------|----------|
| **Git Repo** | 源代码版本控制 | 代码变更、协作开发、版本回滚 |
| **VPS** | 生产运行环境 | 服务部署、自动化任务、实时数据 |
| **本地备份** | 灾难恢复 + 离线开发 | 完整环境恢复、AI本地开发、合规要求 |

### 2.2 数据分类与流向

```
┌─────────────────────────────────────────────────────────────┐
│                        Git Repo                             │
│  (源代码、配置模板、文档)                                      │
│  • 所有可版本控制的代码                                        │
│  • 配置文件模板 (不含secrets)                                  │
│  • 基础设施即代码 (Docker Compose等)                          │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
         Push/Pull                      Clone/Deploy
               │                              │
               ▼                              ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│      开发者本地环境        │      │         VPS              │
│  (AI辅助开发、调试)         │      │  (生产运行、自动化)         │
│                          │      │                          │
│  • 完整代码库             │      │  • 部署的代码              │
│  • 本地测试数据           │      │  • 运行时数据              │
│  • AI工具链              │      │  • Secrets/凭证            │
│  • 实验性修改             │      │  • 日志/数据库             │
└──────────────┬───────────┘      └──────────────┬───────────┘
               │                                  │
               │         定期加密备份              │
               └──────────────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │    本地备份 (Google Drive) │
                    │  (灾难恢复、离线恢复)         │
                    │                          │
                    │  • 完整环境快照            │
                    │  • 加密保护                │
                    │  • 14天滚动保留            │
                    └──────────────────────────┘
```

### 2.3 协调策略

#### A. 代码层 (Git Repo)

**原则**: 所有代码变更必须通过Git

```bash
# 工作流程:
1. 本地开发 → commit → push → VPS pull
2. VPS紧急修复 → commit → push → 本地 pull
3. 禁止: VPS直接修改代码不提交
```

**配置管理**:
```
repo/
├── config/
│   ├── docker-compose.yml        # 基础配置 (入git)
│   ├── docker-compose.prod.yml   # 生产覆盖 (入git)
│   └── .env.example              # 模板 (入git)
├── .env                          # 真实secrets (不入git, VPS本地)
└── .env.local                    # 本地开发 (不入git, 本地机器)
```

#### B. VPS层 (生产环境)

**职责**:
- 运行生产服务
- 执行自动化任务(cron)
- 托管实时数据

**备份策略**:
| 数据类型 | 备份方式 | 频率 | 保留期 |
|----------|----------|------|--------|
| 代码 | Git Repo | 实时 | 永久 |
| 配置+Secrets | 加密云备份 | 每日 | 14天 |
| 运行时数据 | 加密云备份 | 每日 | 14天 |
| 数据库 | Supabase自动备份 | 持续 | 7天 |

#### C. 本地备份层 (灾难恢复 + AI开发)

**职责**:
1. **灾难恢复**: VPS完全失效时可重建环境
2. **AI本地开发**: 本地团队使用AI工具处理底层问题

**AI本地开发工作流**:
```
场景: 需要AI解决底层代码问题

1. 从Git clone最新代码到本地
2. 从Google Drive下载最新备份 (获取secrets模板)
3. 本地配置.env (使用本地测试凭证)
4. AI在本地分析/修改代码
5. 测试通过后 push 到Git
6. VPS pull 并部署
7. 如有需要，更新VPS的secrets (手动或脚本)
```

**本地团队与VPS协调**:

| 操作 | 推荐方式 | 说明 |
|------|----------|------|
| 代码修改 | Git workflow | 不在VPS直接修改 |
| Secrets更新 | 手动或脚本 | 双向同步需谨慎 |
| 数据库操作 | Supabase Console | 单一数据源 |
| 紧急恢复 | 备份+Git | 先恢复备份，再pull最新代码 |

### 2.4 具体协调建议

#### 1. 建立同步检查机制

```bash
# 每日检查脚本 (添加到cron)
#!/bin/bash
# /data/workspace/scripts/daily-sync-check.sh

echo "=== $(date) Daily Sync Check ==="

for repo in openclaw-sean-fork uni-openclaw-infra mission-control; do
  cd /data/workspace/$repo
  git fetch origin --quiet
  
  BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
  AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
  UNTRACKED=$(git status --short | grep "^??" | wc -l)
  
  if [ "$BEHIND" -gt 0 ]; then
    echo "⚠️  $repo: behind remote by $BEHIND commits"
  fi
  
  if [ "$AHEAD" -gt 0 ]; then
    echo "⚠️  $repo: ahead of remote by $AHEAD commits (need push)"
  fi
  
  if [ "$UNTRACKED" -gt 0 ]; then
    echo "⚠️  $repo: $UNTRACKED untracked files"
  fi
done

# 发送到Slack
openclaw message send --channel slack --target "user:U025H4Q9FPA" \
  --message "[Daily Sync] $(cat /tmp/sync-check.txt)"
```

#### 2. Secrets管理策略

**问题**: Secrets分布在多个地方 (.env文件、OpenClaw配置、数据库)

**建议方案**:
```
单一数据源: Supabase (已实施)
          ↓
    ┌─────┴─────┐
    ▼           ▼
   VPS        本地开发
 (运行时读取) (手动配置或脚本同步)
```

- 所有secrets存入Supabase (已实施)
- VPS启动时从Supabase加载
- 本地开发手动配置或使用导出脚本

#### 3. AI本地开发支持

为本地团队提供:

```bash
# 1. 环境重建脚本
/data/workspace/scripts/setup-local-dev.sh
# - clone repos
# - 创建.env.local模板
# - 安装依赖

# 2. Secrets导出脚本 (管理员使用)
/data/workspace/scripts/export-secrets-for-dev.sh
# - 从Supabase导出非敏感配置
# - 生成.env.local模板

# 3. 与VPS同步脚本
/data/workspace/scripts/sync-to-vps.sh
# - push代码到git
# - 可选: 同步特定配置到VPS
```

#### 4. 灾难恢复流程

```
场景: VPS完全失效

1. 新建VPS实例
2. 安装基础依赖 (Docker, rclone, age, etc.)
3. 从Google Drive下载最新备份
4. 解密并恢复 /data/.openclaw/
5. clone Git repos
6. 从Supabase加载secrets
7. 启动服务
8. 验证运行

预计恢复时间: 30-60分钟
```

---

## 3. 立即行动清单

### 高优先级 (本周)
- [ ] 修复cronjob安装 (见1.3节)
- [ ] 更新openclaw repo (落后3个安全修复)
- [ ] 决策mission-control的execution/目录处理
- [ ] 手动触发一次完整备份验证流程

### 中优先级 (本月)
- [ ] 部署每日同步检查脚本
- [ ] 创建本地开发环境搭建文档
- [ ] 执行一次恢复演练
- [ ] 设置备份监控告警

### 低优先级 (持续)
- [ ] 优化备份大小 (排除更多临时文件)
- [ ] 考虑增量备份策略
- [ ] 文档化完整的灾难恢复流程

---

*报告由Clover生成 | 2026-04-06*

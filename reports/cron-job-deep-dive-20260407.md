# Cron Job 深度调查报告
**调查时间:** 2026-04-07 04:35 UTC  
**调查员:** Clover 🍀  
**目的:** 厘清所有cron job状态、存储架构、Slack绑定规则

---

## 一、Cron Job 状态定义澄清

| 状态 | 定义 | 例子 |
|------|------|------|
| **✅ 运行中** | 已配置在系统crontab或OpenClaw cron，定期执行且有执行记录 | OpenClaw Backup, Secret Health Daily |
| **⚠️ Skeleton** | 脚本文件存在，但只有框架/注释，无实际功能实现 | `google_ads_hourly_sync.sh`, `meta_ads_hourly_sync.sh` |
| **📋 配置未激活** | 仅在JSON配置文件中定义，未添加到实际crontab | Secret Stats Calculation, Secret Backup Weekly |
| **❌ 已禁用** | 配置存在但enabled=false | Weekly Memory Compactor (chat) |
| **🔴 运行错误** | 配置正确但执行失败 | Daily Feedback Summary (timeout), Google Ads Weekly DA (delivery failed) |

---

## 二、完整Cron Job清单（14个Jobs）

### 2.1 系统级Cron（/etc/cron.d/）

| Job | 文件 | Schedule | 状态 | Report To |
|-----|------|----------|------|-----------|
| OpenClaw Full Backup | `openclaw-backup` | Daily 02:15 UTC | ✅ 运行中 | Slack DM Sean |

### 2.2 OpenClaw Cron Jobs（/data/.openclaw/cron/jobs.json）

| ID | Name | Agent | Schedule | Status | Report To | Last Run |
|----|------|-------|----------|--------|-----------|----------|
| secret-health-daily-001 | Secret Management Daily Health Check | Clover | 0 1 * * * UTC | ✅ 运行中 | #alerts (C06UQC665MX) | 2025-04-05 01:00 ✅ |
| secret-stats-daily-001 | Secret Management Stats Calculation | Clover | 0 2 * * * UTC | 🔴 运行错误 | silent | 2025-04-05 02:00 ❌ timeout |
| secret-backup-weekly-001 | Secret Management Weekly Backup | Clover | 0 3 * * 0 UTC | ✅ 运行中 | #alerts (C06UQC665MX) | pending |
| 7c89613b-bfd4-4b53-846c-a6967c56b4f9 | Weekly Memory Compactor (chat) | Clover | 0 3 * * 1 AZ | ❌ 已禁用 | #chat (C0AGZLUBYP4) | N/A |
| bf80a417-33d4-4229-880a-301281bfcb6b | Google Ads Weekly - Lumiere Dental | Datie | 0 12 * * 4 UTC | ✅ 运行中 | #operations (C05PN0C4LUB) | 2025-03-31 12:00 ✅ |
| e1315c56-60a4-47e7-b1d1-869eae4f69a6 | Google Ads Weekly - Dental Artistry | Datie | 0 12 * * 4 UTC | 🔴 运行错误 | #operations (C05PN0C4LUB) | 2025-03-31 12:00 ❌ 7 errors |
| 063d6b9e-7236-4f1f-8230-f350f00cef46 | Daily Usage Report - Datie | Datie | 0 0 * * * AZ | ✅ 运行中 | #alerts (C06UQC665MX) | 2025-04-06 00:00 ✅ |
| fdb4ba9a-a6bc-412e-836a-cf11eeffbc9c | Daily Usage Report - All Agents | Clover | 0 5 * * * AZ | ✅ 运行中 | #alerts (C06UQC665MX) | 2025-04-05 05:00 ✅ |
| c35676f0-6fb2-4499-a279-8c23fab11291 | Daily Feedback Summary | Clover | 30 6 * * * AZ | 🔴 运行错误 | DM Sean (U025H4Q9FPA) | 2025-04-05 06:30 ❌ timeout |
| 4821c83c-a376-460c-b7a4-f68807465cea | UNI MAS Memory Weekly Distill | Clover | 0 5 * * 6 AZ | 🔴 运行错误 | last channel | 2025-04-05 05:00 ❌ message failed |
| a7d2468f-893a-40fc-8b93-4fceb371d3ae | Learning Swipe Weekly Summary | Clover | 0 9 * * 1 AZ | ✅ 运行中 | main session | 2025-04-05 09:00 ✅ |
| 73cd6693-b9b7-45c8-a7ef-d6dd8db1962f | Learning Swipe Monthly Goal Review | Clover | 0 10 1 * * AZ | ✅ 运行中 | main session | pending |
| dc3d467c-9f95-4515-802c-5794e867c355 | Daily Usage Report - All (v2) | Clover | 0 4 * * * AZ | ✅ 运行中 | #alerts (C06UQC665MX) | 2025-04-05 04:00 ✅ |

### 2.3 Skeleton Scripts（/data/workspace/scripts/）

| 脚本 | 目的 | 状态 | 问题 |
|------|------|------|------|
| `google_ads_hourly_sync.sh` | 每小时同步Google Ads数据 | ⚠️ Skeleton | 只有curl框架，无实际API调用 |
| `meta_ads_hourly_sync.sh` | 每小时同步Meta Ads数据 | ⚠️ Skeleton | 同上 |
| `mary_nightly_sync.sh` | Mary夜间同步ClickUp+Fireflies | ⚠️ Skeleton | 待实现 |
| `sync_all_accounts.py` | 全账户同步协调器 | ⚠️ Partial | Python实现存在但未激活 |

### 2.4 Datie Runtime Scripts（/data/.openclaw/workspace-datie/）

| 脚本 | 目的 | 状态 | 说明 |
|------|------|------|------|
| `fetch_google_ads_real.py` | 获取真实Google Ads数据 | ✅ 可用 | 被weekly report job调用 |
| `weekly_google_ads_report.py` | 生成周报 | ✅ 可用 | 备用脚本 |
| `run_full_cron_test.py` | 完整cron测试 | ✅ 可用 | 测试DA+LM账户 |
| `run_complete_test.py` | 完整测试套件 | ✅ 可用 | 多账户测试 |

---

## 三、Slack Channel绑定规则（当前状态）

### 3.1 混乱点分析

**问题1: 多个channel用于同类报告**
- Usage reports → #alerts (C06UQC665MX)
- Google Ads reports → #operations (C05PN0C4LUB)  
- Secret health → #alerts (C06UQC665MX)
- Feedback summary → DM Sean

**问题2: 命名不一致**
- "alerts" channel用于usage reports（不是真正的alerts）
- "operations" channel用于Google Ads reports

**问题3: 部分jobs未指定明确channel**
- Weekly Memory Distill → "last" (不确定)
- Learning Swipe jobs → "main session"

### 3.2 建议的统一规则

| 报告类型 | 建议Channel | 当前Channel | 状态 |
|----------|-------------|-------------|------|
| System health/backup | #alerts | #alerts | ✅ 一致 |
| Usage reports | #operations 或 #agent-activity | #alerts | ⚠️ 建议调整 |
| Google Ads weekly | #client-reports 或 #operations | #operations | ✅ 一致 |
| Secret management | #alerts | #alerts | ✅ 一致 |
| Feedback summary | DM Sean | DM Sean | ✅ 一致 |
| Memory/learning | #knowledge | main session | ⚠️ 建议调整 |

---

## 四、存储架构现状

### 4.1 Cron Job配置存储

| 类型 | 位置 | 说明 |
|------|------|------|
| **System crontab** | `/etc/cron.d/openclaw-backup` | 系统级备份job |
| **OpenClaw cron** | `/data/.openclaw/cron/jobs.json` | 14个jobs的主配置 |
| **Run logs** | `/data/.openclaw/cron/runs/*.jsonl` | 每次执行的详细记录 |
| **JSON config** | `/data/workspace/security/config/secret-management-cron.json` | 仅配置，未同步到主jobs.json |
| **Text config** | `/data/workspace/cron/*.txt` | 文档性质的cron示例 |

### 4.2 脚本存储

| 位置 | 内容 | 状态 |
|------|------|------|
| `/data/workspace/scripts/` | 共享脚本（backup, sync等） | 部分skeleton |
| `/data/.openclaw/workspace-datie/` | Datie专用脚本（Google Ads等） | 功能完整 |
| `/data/workspace/security/scripts/` | Secret管理脚本 | 功能完整 |

### 4.3 日志存储

| 位置 | 内容 | 保留策略 |
|------|------|----------|
| `/data/.openclaw/logs/` | Backup logs, config audit | 30天 |
| `/data/.openclaw/cron/runs/` | Cron执行详细记录 | 未明确 |
| `/var/log/` | 系统级日志（context-hook-server等） | 系统默认 |

---

## 五、关键发现与建议

### 5.1 立即需要修复的Jobs

| Job | 问题 | 建议操作 |
|-----|------|----------|
| Secret Stats Calculation | Timeout (60s不够) | 增加timeout到180s |
| Google Ads Weekly DA | 连续7次error，delivery失败 | 检查Slack token权限 |
| Daily Feedback Summary | Timeout (120s不够) | 优化查询或增加timeout |
| UNI MAS Memory Distill | Message failed | 检查channel配置 |

### 5.2 需要统一的架构决策

1. **Slack Channel命名规范**
   - #alerts: 仅用于真正的系统警报
   - #operations: 运营报告（Google Ads等）
   - #agent-activity: Agent usage reports（新建）
   - #knowledge: Memory/learning相关

2. **Cron Job配置单一来源**
   - 当前：jobs.json是主配置，但security/config/下有重复
   - 建议：统一使用jobs.json，删除或同步其他配置

3. **Skeleton Scripts处理**
   - `google_ads_hourly_sync.sh` 和 `meta_ads_hourly_sync.sh` 需要实现或删除
   - 如果不需要hourly sync，建议删除避免混淆

4. **Context Auditor**
   - 脚本存在 (`/data/workspace/security/scripts/context_auditor.js`)
   - 但未在cron jobs中找到对应的scheduled job
   - 需要确认是否应添加为daily job

---

## 六、下一步行动建议

1. **修复运行错误的jobs**（优先级：高）
2. **统一Slack channel绑定**（优先级：中）
3. **清理skeleton scripts**（优先级：中）
4. **确认Context Auditor是否应加入cron**（优先级：低）
5. **建立统一的cron job文档规范**（优先级：低）

---

*报告完成时间: 2026-04-07 04:40 UTC*

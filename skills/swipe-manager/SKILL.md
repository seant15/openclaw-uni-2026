---
name: swipe-manager
description: Manage the Learning & Swipe knowledge base system in Notion. Use when an agent needs to (1) delegate knowledge base organization tasks to Mary, (2) check the status of the Learning & Swipe database, (3) generate weekly summaries, (4) track content ingestion goals, or (5) coordinate knowledge base workflows. This skill handles the complete workflow from content collection to organization to application tracking. Trigger on phrases like "/swipe-manager", "整理知识库", "检查知识库状态", "生成知识库周报", "swipe database", "learning swipe".
---

# Swipe Manager

This skill manages the complete knowledge base ingestion and organization system for the Learning & Swipe Notion database.

## When to Use This Skill

- **Delegate to Mary**: Any agent needs Mary to organize/curate the knowledge base
- **Status Check**: Check current state of the database (pending items, backlog, etc.)
- **Weekly Summary**: Generate or request the weekly knowledge base summary
- **Goal Tracking**: Check progress against monthly ingestion and digestion goals
- **Workflow Coordination**: Coordinate between content collection, organization, and application

## System Overview

```
Content Collection → Mary Organization → Sean Digestion → Application
       ↓                    ↓                  ↓              ↓
   Status:待处理      Status:已整理      Status:已消化   Status:已应用
```

### Database Schema

| Field | Type | Purpose |
|-------|------|---------|
| Name | Title | Content title |
| Content Type | Select | LEARNING / SWIPE |
| Status | Select | 待处理 / 已整理 / 已消化 / 已应用 / 已归档 |
| Priority | Select | 🔴 高 / 🟡 中 / 🟢 低 |
| Tags | Multi-select | google ads, Facebook Ads, ai, video, email, SEO, CRO, Copy, design, tracking, tiktok ads, Pinterest, Linkedin Ads |
| Industry | Multi-select | ECOM, LeadGen, B2B, AI, ALL, NFT, Other |
| Original Source | Multi-select | X, Youtube, Blog/Article, TikTok, Pdf, Web, email, Facebook |
| Link | URL | Original URL |
| Key Insights | Rich text | Core insights (extracted by Mary) |
| Action Items | Rich text | Actionable takeaways |
| Related Projects | Multi-select | Associated projects/clients |
| Date Added | Created time | Auto-recorded |
| Date Consumed | Date | When Sean reviewed it |

## Goals & KPIs

| Metric | Monthly Target |
|--------|---------------|
| New Content Collection | 30 items/month |
| Organization Rate | 100% (weekly zero backlog) |
| High Priority Digestion | 20% of high priority items |
| Actual Application | 5 items/month |

## Workflows

### 1. Delegate Organization Task to Mary

**Trigger**: Any agent detects backlog or needs Mary to organize content

**Process**:
1. Check current database status (count by Status)
2. If Mary is the requester → execute directly (see "Mary Self-Execution" below)
3. If another agent is requesting → send task notification to Mary

**Mary Notification Template**:
```
📚 Learning & Swipe 任务委派

Mary，需要你处理知识库整理任务：

📊 当前状态：
• 待处理条目：[N] 条
• 本周新增：[N] 条
• 高优先级待整理：[N] 条

📋 请完成：
1. 审查所有 Status = "待处理" 条目
2. 补充 Tags / Industry / Source
3. 提取 Key Insights (2-3句话/条)
4. 标记 Priority (🔴高/🟡中/🟢低)
5. 更新 Status → "已整理"
6. 生成周报发送给 Sean

⏰ 建议完成时间：本周五前
```

### 2. Check Database Status

**Trigger**: Need to know current state of knowledge base

**Process**:
1. Query Notion database for counts by Status
2. Calculate weekly/monthly metrics
3. Report current state

**Status Report Template**:
```
📊 Learning & Swipe 状态报告

📈 总体统计：
• 总条目数：[N]
• 本月新增：[N]
• 待处理：[N]
• 已整理：[N]
• 已消化：[N]
• 已应用：[N]

🎯 目标进度：
• 收集进度：[N]/30 ([N]%)
• 整理状态：[待处理积压情况]
• 消化进度：[N]/6 ([N]%)
• 应用进度：[N]/5 ([N]%)

⚠️ 需要关注：
• [Any backlog warnings or alerts]
```

### 3. Generate Weekly Summary

**Trigger**: Weekly (Monday) or on-demand

**Process**:
1. Query last 7 days of activity
2. Count new items, organized items, consumed items
3. Identify high-priority items for Sean's attention
4. Generate summary report

**Weekly Report Template**:
```
📚 Learning & Swipe 周报 (Week of [日期])

📊 本周数据：
• 新增内容：[N] 条
• 已整理：[N] 条
• 待处理剩余：[N] 条
• 高优先级待消化：[N] 条

🔥 本周亮点 (高优先级)：
1. [标题] - [核心洞察一句话]
2. [标题] - [核心洞察一句话]
3. [标题] - [核心洞察一句话]

📌 推荐立即消化：
• [标题] - 原因：[与当前项目关联]

🎯 下月目标进度：
• 收集：[N]/30 ([N]%)
• 消化：[N]/6 ([N]%)
• 应用：[N]/5 ([N]%)
```

### 4. Mary Self-Execution

**Trigger**: Mary herself calls this skill

**Process**:
Mary executes the workflow directly without sending notifications:

1. **Query Database**: Get all Status = "待处理" items
2. **Organize Each Item**:
   - Review content from Link
   - Fill in missing Tags (based on content topic)
   - Fill in Industry (ECOM/LeadGen/B2B/etc.)
   - Fill in Original Source (X/Youtube/Blog/etc.)
   - Write Key Insights (2-3 sentences summarizing value)
   - Identify Action Items (if applicable)
   - Set Priority based on relevance to current projects
   - Update Status → "已整理"
3. **Generate Summary**: Create weekly report for Sean
4. **Update Goals**: Track progress against monthly targets

**Mary's Checklist**:
```
□ 获取所有待处理条目
□ 逐条审查并补充元数据
□ 提取 Key Insights
□ 标记 Priority
□ 更新 Status → "已整理"
□ 生成周报
□ 发送给 Sean
□ 更新目标追踪
```

### 5. Goal Tracking

**Trigger**: Monthly review or on-demand check

**Process**:
1. Calculate metrics for current month
2. Compare against targets
3. Identify gaps and recommend adjustments
4. Generate goal tracking report

**Goal Report Template**:
```
🎯 Learning & Swipe 目标追踪 (Month of [月份])

📊 本月表现：
• 新内容收集：[N]/30 ([N]%) [✅/⚠️]
• 内容整理率：[N]% [✅/⚠️]
• 高优先级消化：[N]/6 ([N]%) [✅/⚠️]
• 实际应用：[N]/5 ([N]%) [✅/⚠️]

🔄 建议调整：
• [Specific recommendations based on performance]

📈 趋势分析：
• [Week-over-week or month-over-month trends]
```

## API Integration

### Notion API Queries

**Get Database Status**:
```bash
curl -X POST "https://api.notion.com/v1/data_sources/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100}'
```

**Filter by Status**:
```bash
curl -X POST "https://api.notion.com/v1/data_sources/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "select": {"equals": "待处理"}
    }
  }'
```

**Update Page Status**:
```bash
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "已整理"}},
      "Priority": {"select": {"name": "🔴 高"}},
      "Key Insights": {"rich_text": [{"text": {"content": "..."}}]}
    }
  }'
```

## Usage Patterns

### Pattern 1: Direct Skill Invocation
```
User: "/swipe-manager"
Agent: 加载 swipe-manager skill → 检查状态 → 询问具体操作
```

### Pattern 2: Agent Delegates to Mary
```
User: "整理一下知识库"
Agent: 调用 swipe-manager → 检查状态 → 发送任务给 Mary
```

### Pattern 3: Mary Self-Executes
```
Mary: "处理本周的待整理内容"
Agent: 调用 swipe-manager → Mary 身份识别 → 直接执行
```

### Pattern 4: Status Check
```
User: "知识库现在什么情况？"
Agent: 调用 swipe-manager → 查询数据库 → 生成状态报告
```

### Pattern 5: Weekly Summary
```
User: "生成本周知识库总结"
Agent: 调用 swipe-manager → 查询本周数据 → 生成周报
```

## Important Notes

- **Mary Detection**: If the requester is Mary (user ID or name match), execute directly without sending notifications
- **Database ID**: Learning & Swipe 3.0 database ID is `04bdbb3b-fa1d-4e94-bb21-b932c41f7c93`
- **Cron Jobs**: Weekly reminders are already configured (Mondays 9 AM AZ)
- **Goal Tracking**: Monthly reviews on the 1st of each month

## References

- **System Documentation**: See [references/system-overview.md](references/system-overview.md) for complete system architecture
- **Database Schema**: See [references/database-schema.md](references/database-schema.md) for detailed field definitions
- **Weekly Checklist**: See [references/weekly-checklist.md](references/weekly-checklist.md) for Mary's task list

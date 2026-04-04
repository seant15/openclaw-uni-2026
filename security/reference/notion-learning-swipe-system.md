# Learning & Swipe 知识库摄入系统

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    内容发现层 (Daily)                            │
│  X/Twitter → Notion Web Clipper → 自动标记 Status="待处理"        │
│  Youtube → 分享按钮 → 快捷指令 → Notion                          │
│  网页/文章 → 浏览器插件 → 一键保存                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    整理处理层 (Weekly by Mary)                   │
│  • 审查所有"待处理"条目                                          │
│  • 补充 Tags / Industry / Source                                 │
│  • 提取 Key Insights 和 Action Items                             │
│  • 更新 Status → "已整理"                                        │
│  • 标记 Priority (高/中/低)                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    消化应用层 (As Needed)                        │
│  • 深度阅读 → 更新 Status → "已消化"                             │
│  • 应用到项目 → 更新 Status → "已应用"                           │
│  • 同步 Action Items 到任务系统                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 数据库 Schema (新增字段)

| 字段 | 类型 | 选项/说明 |
|------|------|-----------|
| Name | Title | 内容标题 |
| Content Type | Select | LEARNING / SWIPE |
| Status | Select | 待处理 / 已整理 / 已消化 / 已应用 / 已归档 |
| Priority | Select | 🔴 高 / 🟡 中 / 🟢 低 |
| Tags | Multi-select | google ads, Facebook Ads, ai, video, email, SEO, CRO, Copy, design, tracking, tiktok ads, Pinterest, Linkedin Ads |
| Industry | Multi-select | ECOM, LeadGen, B2B, AI, ALL, NFT, Other |
| Original Source | Multi-select | X, Youtube, Blog/Article, TikTok, Pdf, Web, email, Facebook |
| Link | URL | 原始链接 |
| Key Insights | Rich text | 核心洞察 (由 Mary 提取) |
| Action Items | Rich text | 可执行要点 |
| Related Projects | Multi-select | 关联项目/客户 |
| Date Added | Created time | 自动记录 |
| Date Consumed | Date | 实际消化日期 |
| Week Number | Formula | 用于周报分组 |

## Goal 追踪系统

### 月度目标 (示例)
| 指标 | 目标 | 追踪方式 |
|------|------|----------|
| 新内容收集 | 30 条/月 | 数据库计数 |
| 内容整理率 | 100% (每周清零待处理) | Status 统计 |
| 内容消化率 | 20% (高优先级) | Status = "已消化" |
| 实际应用数 | 5 条/月 | Status = "已应用" |
| 跨项目复用 | 3 条/月 | Related Projects 非空 |

### 每周 Mary 任务清单
- [ ] 审查所有 Status = "待处理" 条目
- [ ] 补充完整 Tags / Industry / Source
- [ ] 为每条内容提取 Key Insights (2-3 句话)
- [ ] 标记 Priority (基于与当前项目的相关性)
- [ ] 更新 Status → "已整理"
- [ ] 生成周报摘要 (见下方模板)

## 周报模板 (Mary 每周一发送)

```
📚 Learning & Swipe 周报 (Week of [日期])

📊 本周数据
• 新增内容: [N] 条
• 已整理: [N] 条
• 待处理剩余: [N] 条
• 高优先级待消化: [N] 条

🔥 本周亮点 (高优先级内容)
1. [标题] - [核心洞察一句话]
2. [标题] - [核心洞察一句话]
3. [标题] - [核心洞察一句话]

📌 推荐立即消化的内容
• [链接/标题] - 原因: [与当前项目的关联]

🎯 下月目标进度
• 收集: [N]/30 ([N]%)
• 消化: [N]/6 ([N]%)
• 应用: [N]/5 ([N]%)
```

## Cron Job 配置

### 每周提醒 (周一 09:00 MST)
- 提醒 Mary 执行周报任务
- 发送待处理内容清单

### 每月提醒 (每月1日 09:00 MST)
- 上月数据总结
- 目标达成情况
- 调整下月目标

## 快捷指令配置 (iOS/Mac)

### 1. "Save to Swipe" 快捷指令
```
接收: 网页/链接
动作:
1. 获取网页标题
2. 创建 Notion 页面:
   - Database: Learning & Swipe 3.0
   - Name: [网页标题]
   - Link: [URL]
   - Content Type: SWIPE
   - Status: 待处理
   - Tags: [让用户选择]
3. 显示确认通知
```

### 2. "Save YouTube Learning" 快捷指令
```
接收: YouTube 分享
动作:
1. 解析视频标题
2. 创建 Notion 页面:
   - Database: Learning & Swipe 3.0
   - Name: [视频标题]
   - Link: [YouTube URL]
   - Content Type: LEARNING
   - Original Source: Youtube
   - Status: 待处理
```

## 浏览器插件配置

### Notion Web Clipper 设置
- 默认保存到: Learning & Swipe 3.0
- 自动填充: Link, Name
- 手动选择: Content Type, Tags, Industry

## 成功指标 (KPIs)

| 指标 | 当前基线 | 3个月目标 |
|------|----------|-----------|
| 每周新增内容 | ? | 7-10 条 |
| 待处理队列清零时间 | ? | < 7 天 |
| 高优先级内容消化率 | ? | > 50% |
| Action Items 执行率 | ? | > 30% |

---
*系统版本: v1.0*
*创建日期: 2026-03-30*
*负责人: Mary (周报) + Sean (消化应用)*

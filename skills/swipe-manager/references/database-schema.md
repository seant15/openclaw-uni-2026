# Learning & Swipe Database Schema

## Database Information

- **Name**: Learning & Swipe 3.0
- **Database ID**: `04bdbb3b-fa1d-4e94-bb21-b932c41f7c93`
- **Workspace**: Sean's Notion

## Field Definitions

### 1. Name (Title)
- **Type**: Title
- **Required**: Yes
- **Description**: Content title (auto-filled from source or manual entry)
- **Examples**: 
  - "Google Ads 2024 最新策略"
  - "Facebook Creative Best Practices"

### 2. Content Type (Select)
- **Type**: Select
- **Options**:
  - `LEARNING` - Educational content, tutorials, how-tos
  - `SWIPE` - Reference materials, examples, inspiration
- **Usage**: Determines how the content should be processed

### 3. Status (Select)
- **Type**: Select
- **Options**:
  - `待处理` - Newly added, needs organization by Mary
  - `已整理` - Organized by Mary, ready for Sean's review
  - `已消化` - Sean has read and understood
  - `已应用` - Applied to actual projects
  - `已归档` - Outdated or no longer relevant
- **Workflow**: 待处理 → 已整理 → 已消化 → 已应用

### 4. Priority (Select)
- **Type**: Select
- **Options**:
  - `🔴 高` - High priority, relevant to current projects
  - `🟡 中` - Medium priority, relevant to business
  - `🟢 低` - Low priority, general learning
- **Determined by**: Relevance to current active projects

### 5. Tags (Multi-select)
- **Type**: Multi-select
- **Options**:
  - `google ads` - Google Ads platform
  - `Facebook Ads` - Meta/Facebook Ads
  - `ai` - AI tools and applications
  - `video` - Video content/marketing
  - `email` - Email marketing
  - `SEO` - Search engine optimization
  - `CRO` - Conversion rate optimization
  - `Copy` - Copywriting
  - `design` - Design/UX
  - `tracking` - Analytics and tracking
  - `tiktok ads` - TikTok advertising
  - `Pinterest` - Pinterest marketing
  - `Linkedin Ads` - LinkedIn advertising
- **Usage**: Categorize content by topic

### 6. Industry (Multi-select)
- **Type**: Multi-select
- **Options**:
  - `ECOM` - E-commerce
  - `LeadGen` - Lead generation
  - `B2B` - Business to business
  - `AI` - AI industry
  - `ALL` - Applicable to all industries
  - `NFT` - NFT/Web3
  - `Other` - Other industries
- **Usage**: Identify which business vertical the content applies to

### 7. Original Source (Multi-select)
- **Type**: Multi-select
- **Options**:
  - `X` - X/Twitter
  - `Youtube` - YouTube videos
  - `Blog/Article` - Blog posts or articles
  - `TikTok` - TikTok content
  - `Pdf` - PDF documents
  - `Web` - General web content
  - `email` - Email newsletters
  - `Facebook` - Facebook content
- **Usage**: Track where content was discovered

### 8. Link (URL)
- **Type**: URL
- **Description**: Original source URL
- **Usage**: Link back to original content for reference

### 9. Key Insights (Rich Text)
- **Type**: Rich text
- **Description**: 2-3 sentence summary of core value
- **Written by**: Mary during organization
- **Format**: Plain text, concise
- **Examples**:
  - "Google's new Performance Max features allow for audience signals that can improve conversion rates by 15-20% for dental practices."
  - "Facebook's creative best practices emphasize first 3 seconds hook and vertical video format for mobile."

### 10. Action Items (Rich Text)
- **Type**: Rich text
- **Description**: Specific actions Sean should take
- **Written by**: Mary or Sean
- **Format**: Bullet points
- **Examples**:
  - "Test new PMAX audience signals for Lumiere Dental"
  - "Update Facebook creative to 9:16 vertical format"

### 11. Related Projects (Multi-select)
- **Type**: Multi-select
- **Options**: Dynamic based on active projects
- **Examples**:
  - `Lumiere Dental`
  - `Dental Artistry`
  - `SESUNG`
  - `Travorio`
  - `LEIVIP`
  - `Windie.pro`
- **Usage**: Track which projects have applied this knowledge

### 12. Date Added (Created Time)
- **Type**: Created time
- **Auto-filled**: Yes
- **Usage**: Track when content was added to the database

### 13. Date Consumed (Date)
- **Type**: Date
- **Filled by**: Sean
- **Usage**: Track when content was actually reviewed/digested

## API Query Examples

### Get All Pending Items
```json
{
  "filter": {
    "property": "Status",
    "select": {"equals": "待处理"}
  },
  "sorts": [
    {"property": "Date Added", "direction": "descending"}
  ]
}
```

### Get High Priority Items to Digest
```json
{
  "filter": {
    "and": [
      {"property": "Status", "select": {"equals": "已整理"}},
      {"property": "Priority", "select": {"equals": "🔴 高"}}
    ]
  }
}
```

### Get Items Added This Month
```json
{
  "filter": {
    "timestamp": "created_time",
    "created_time": {
      "on_or_after": "2026-03-01"
    }
  }
}
```

### Get Items by Tag
```json
{
  "filter": {
    "property": "Tags",
    "multi_select": {"contains": "google ads"}
  }
}
```

### Get Items by Industry
```json
{
  "filter": {
    "property": "Industry",
    "multi_select": {"contains": "ECOM"}
  }
}
```

## Update Operations

### Mark as Organized
```json
{
  "properties": {
    "Status": {"select": {"name": "已整理"}},
    "Priority": {"select": {"name": "🔴 高"}},
    "Tags": {"multi_select": [{"name": "google ads"}, {"name": "ai"}]},
    "Industry": {"multi_select": [{"name": "LeadGen"}]},
    "Original Source": {"multi_select": [{"name": "X"}]},
    "Key Insights": {
      "rich_text": [{"text": {"content": "Key insight text here..."}}]
    }
  }
}
```

### Mark as Digested
```json
{
  "properties": {
    "Status": {"select": {"name": "已消化"}},
    "Date Consumed": {"date": {"start": "2026-03-30"}},
    "Action Items": {
      "rich_text": [{"text": {"content": "• Action item 1\n• Action item 2"}}]
    }
  }
}
```

### Mark as Applied
```json
{
  "properties": {
    "Status": {"select": {"name": "已应用"}},
    "Related Projects": {"multi_select": [{"name": "Lumiere Dental"}]}
  }
}
```

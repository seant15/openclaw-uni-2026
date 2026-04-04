#!/usr/bin/env python3
"""
Learning & Swipe Database Query Script

Queries the Notion database for status reports and metrics.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timedelta

# Database ID
DATABASE_ID = "04bdbb3b-fa1d-4e94-bb21-b932c41f7c93"
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")

def query_database(filter_obj=None, sorts=None):
    """Query the Notion database."""
    url = f"https://api.notion.com/v1/data_sources/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }
    
    data = {"page_size": 100}
    if filter_obj:
        data["filter"] = filter_obj
    if sorts:
        data["sorts"] = sorts
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return {"results": []}

def count_by_status():
    """Count items by status."""
    results = query_database()
    counts = {
        "total": len(results.get("results", [])),
        "待处理": 0,
        "已整理": 0,
        "已消化": 0,
        "已应用": 0,
        "已归档": 0
    }
    
    for item in results.get("results", []):
        props = item.get("properties", {})
        status = props.get("Status", {}).get("select", {}).get("name", "")
        if status in counts:
            counts[status] += 1
    
    return counts

def get_pending_items():
    """Get all pending items."""
    filter_obj = {
        "property": "Status",
        "select": {"equals": "待处理"}
    }
    sorts = [{"property": "Date Added", "direction": "descending"}]
    return query_database(filter_obj, sorts)

def get_high_priority_items():
    """Get high priority items ready for digestion."""
    filter_obj = {
        "and": [
            {"property": "Status", "select": {"equals": "已整理"}},
            {"property": "Priority", "select": {"equals": "🔴 高"}}
        ]
    }
    return query_database(filter_obj)

def get_items_this_month():
    """Get items added this month."""
    today = datetime.now()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    
    filter_obj = {
        "timestamp": "created_time",
        "created_time": {
            "on_or_after": first_day
        }
    }
    return query_database(filter_obj)

def generate_status_report():
    """Generate a complete status report."""
    counts = count_by_status()
    pending = get_pending_items()
    high_priority = get_high_priority_items()
    this_month = get_items_this_month()
    
    month_total = len(this_month.get("results", []))
    
    # Calculate goal progress
    collection_progress = min(100, int((month_total / 30) * 100))
    
    report = f"""📊 Learning & Swipe 状态报告

📈 总体统计：
• 总条目数：{counts['total']}
• 本月新增：{month_total}
• 待处理：{counts['待处理']}
• 已整理：{counts['已整理']}
• 已消化：{counts['已消化']}
• 已应用：{counts['已应用']}

🎯 目标进度：
• 收集进度：{month_total}/30 ({collection_progress}%)
• 整理状态：{'✅ 已清零' if counts['待处理'] == 0 else f'⚠️ 待处理 {counts["待处理"]} 条'}
• 高优先级待消化：{len(high_priority.get('results', []))} 条
"""
    
    return report

def main():
    if not NOTION_API_KEY:
        print("Error: NOTION_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python3 query_db.py [status|pending|high-priority|report]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        counts = count_by_status()
        print(json.dumps(counts, indent=2, ensure_ascii=False))
    elif command == "pending":
        items = get_pending_items()
        print(f"Pending items: {len(items.get('results', []))}")
        for item in items.get("results", [])[:10]:
            props = item.get("properties", {})
            name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled")
            print(f"  - {name}")
    elif command == "high-priority":
        items = get_high_priority_items()
        print(f"High priority items: {len(items.get('results', []))}")
        for item in items.get("results", [])[:10]:
            props = item.get("properties", {})
            name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled")
            print(f"  - {name}")
    elif command == "report":
        print(generate_status_report())
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Google Ads Report Generator
Takes JSON data from fetch_google_ads.py and generates formatted reports
"""

import sys
import json

def format_currency(amount):
    if amount == float('inf') or amount > 999999:
        return "N/A"
    return f"${amount:,.2f}"

def get_health_emoji(cpl, target):
    if cpl == 0:
        return "🔴"
    ratio = cpl / target if target > 0 else 1
    if ratio <= 1.0:
        return "🟢"
    elif ratio <= 1.3:
        return "🟡"
    else:
        return "🔴"

def generate_dental_artistry_report(data):
    """Generate report for Dental Artistry (Riya)"""
    
    account = data['account']
    campaigns = data['campaigns']
    search_terms = data.get('search_terms', [])
    meta = data['metadata']
    
    total_leads = int(account['conversions'])
    avg_cpl = account['cpl']
    total_spend = account['spend']
    
    start_date = meta['start_date']
    end_date = meta['end_date']
    
    report = f"""Subject: Dental Artistry Google Ads Weekly | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Riya,

Quick snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH
"""
    
    # Campaign targets
    campaign_targets = {
        'PMAX Competitors': 50,
        'PMAX Branded': 40,
        'Implants': 67,
        'Emergency': 100,
        'All On 4': 80
    }
    
    for campaign in campaigns:
        name = campaign['name']
        cpl = campaign['cpl']
        leads = int(campaign['leads'])
        
        # Find matching target
        target_cpl = 50
        for key, target in campaign_targets.items():
            if key.lower() in name.lower():
                target_cpl = target
                break
        
        emoji = get_health_emoji(cpl, target_cpl)
        
        if leads > 0:
            status = f"{emoji} {name} — {leads} leads @ {format_currency(cpl)} CPL (target: {format_currency(target_cpl)})"
            if emoji == "🟢":
                status += " — strong"
            elif emoji == "🟡":
                status += " — slightly above target"
            else:
                status += " — needs attention"
        else:
            status = f"🔴 {name} — 0 leads / {format_currency(campaign['spend'])} spent — needs attention"
        
        report += status + "\n"
    
    # Top campaigns by conversions
    top_campaigns = sorted([c for c in campaigns if c['leads'] > 0], 
                          key=lambda x: x['leads'], reverse=True)[:4]
    top_names = [f"{c['name']} ({int(c['leads'])})" for c in top_campaigns]
    
    report += f"""
🟢 On/below target | 🟡 Above target | 🔴 Needs attention

WEEK OVER WEEK
Total Leads — {total_leads}
Average CPL — {format_currency(avg_cpl)}
Total Spend — {format_currency(total_spend)}
Top campaigns by conversions — {', '.join(top_names)}

ACTIONS TAKEN
- Daily review of search terms for negative keyword opportunities
- Budget and bid review across campaigns

WATCHING
"""
    
    # Watching items
    for campaign in campaigns:
        if campaign['leads'] == 0 and campaign['spend'] > 50:
            report += f"- {campaign['name']} — {format_currency(campaign['spend'])} spent, 0 conversions; consider pausing or significant optimization.\n"
        elif campaign['cpl'] > 80 and campaign['leads'] > 0:
            report += f"- {campaign['name']} — {format_currency(campaign['cpl'])} CPL above target; monitor search terms and bids.\n"
    
    # Scaling opportunities
    strong_performers = [c for c in campaigns if c['cpl'] > 0 and c['cpl'] < 50 and c['leads'] > 0]
    if strong_performers:
        report += f"- {', '.join([c['name'] for c in strong_performers])} — well under target CPL; consider scaling if capacity allows.\n"
    
    report += """
Questions? Reply anytime.

Best regards,"""
    
    return report

def generate_lumiere_report(data):
    """Generate report for Lumiere Dental (Dr. Allababidi)"""
    
    account = data['account']
    campaigns = data['campaigns']
    search_terms = data.get('search_terms', [])
    meta = data['metadata']
    
    total_leads = int(account['conversions'])
    avg_cpl = account['cpl']
    total_spend = account['spend']
    
    start_date = meta['start_date']
    end_date = meta['end_date']
    
    report = f"""Subject: Lumiere Dental Google Ads Weekly Pulse | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Dr. Allababidi,

Quick weekly snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH AT A GLANCE
"""
    
    for campaign in campaigns:
        name = campaign['name']
        cpl = campaign['cpl']
        leads = int(campaign['leads'])
        
        if 'pediatric' in name.lower():
            target_cpl = 60
        else:
            target_cpl = 65
        
        emoji = get_health_emoji(cpl, target_cpl)
        
        if leads > 0:
            status = f"{emoji} {name} — {leads} leads @ {format_currency(cpl)} CPL (target: {format_currency(target_cpl)})"
            if emoji == "🟢":
                status += " — excellent performance"
            elif emoji == "🟡":
                status += " — on target"
            else:
                status += " — above target"
        else:
            status = f"🔴 {name} — 0 leads, {format_currency(campaign['spend'])} spent — reviewing"
        
        report += status + "\n"
    
    report += f"""
🟢 On/below target | 🟡 Slightly above target | 🔴 Needs attention

WEEK OVER WEEK
Total Leads: {total_leads} leads generated this week
Average CPL: {format_currency(avg_cpl)} (target: $65)
Total Spend: {format_currency(total_spend)}

TOP CONVERTING KEYWORDS
"""
    
    # Add top search terms
    converting_terms = [t for t in search_terms if t['conversions'] > 0][:8]
    for term in converting_terms:
        conv_rate = (term['conversions'] / term['clicks'] * 100) if term['clicks'] > 0 else 0
        report += f"{term['keyword']} — {int(term['conversions'])} conversion{'s' if term['conversions'] > 1 else ''} @ {format_currency(term['cpl'])} ({conv_rate:.1f}% conv rate)\n"
    
    report += """
ACTIONS TAKEN
- Continued monitoring of Medicaid-focused campaigns
- Daily review of search terms for negative keyword opportunities
- Budget optimization across campaigns

WATCHING
"""
    
    for campaign in campaigns:
        if campaign['leads'] == 0 and campaign['spend'] > 50:
            report += f"- {campaign['name']}: spent {format_currency(campaign['spend'])} with 0 conversions — reviewing keyword targeting and ad copy\n"
        elif campaign['cpl'] > 80 and campaign['leads'] > 0:
            report += f"- {campaign['name']}: {format_currency(campaign['cpl'])} CPL above target — monitoring\n"
    
    report += """
KEY INSIGHTS
- Pediatric and Medicaid-focused keywords continue to drive strong conversion rates
- Monitor campaigns with zero conversions for optimization opportunities

Questions? Reply anytime.

Best regards,"""
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_report.py <json_file> [client_type]")
        print("  json_file: Path to JSON data from fetch_google_ads.py")
        print("  client_type: 'dental_artistry' or 'lumiere'")
        sys.exit(1)
    
    json_file = sys.argv[1]
    client_type = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Auto-detect client type if not specified
    if not client_type:
        account_name = data['account'].get('customer_name', '').lower()
        if 'artistry' in account_name:
            client_type = 'dental_artistry'
        elif 'lumiere' in account_name:
            client_type = 'lumiere'
        else:
            print(f"Warning: Could not auto-detect client type from '{account_name}'")
            print("Defaulting to dental_artistry format")
            client_type = 'dental_artistry'
    
    # Generate report
    if client_type == 'dental_artistry':
        report = generate_dental_artistry_report(data)
    elif client_type == 'lumiere':
        report = generate_lumiere_report(data)
    else:
        report = generate_dental_artistry_report(data)
    
    # Output report
    print(report)
    
    # Save to file
    meta = data['metadata']
    output_file = f"/data/workspace/reports/report_{meta['customer_id']}_{meta['start_date']}_{meta['end_date']}.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print(f"Report saved to: {output_file}")

if __name__ == '__main__':
    main()

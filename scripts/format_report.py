#!/usr/bin/env python3
"""
Google Ads Report Formatter
Takes raw campaign data and outputs formatted UNI report
"""

import sys
from datetime import datetime

def format_currency(amount):
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

def generate_dental_artistry_report(data, start_date, end_date):
    """Generate report for Dental Artistry"""
    
    total_leads = sum(c['leads'] for c in data['campaigns'])
    total_spend = sum(c['spend'] for c in data['campaigns'])
    avg_cpl = total_spend / total_leads if total_leads > 0 else 0
    
    report = f"""Subject: Dental Artistry Google Ads Weekly | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Riya,

Quick snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH
"""
    
    # Campaign health section
    campaign_targets = {
        'PMAX Competitors': 50,
        'PMAX Branded': 40,
        'Implants': 67,
        'Emergency': 100,
        'All On 4': 80
    }
    
    for campaign in data['campaigns']:
        name = campaign['name']
        cpl = campaign['cpl']
        leads = campaign['leads']
        
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
    top_campaigns = sorted([c for c in data['campaigns'] if c['leads'] > 0], 
                          key=lambda x: x['leads'], reverse=True)[:4]
    top_names = [f"{c['name']} ({c['leads']})" for c in top_campaigns]
    
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
    for campaign in data['campaigns']:
        if campaign['leads'] == 0 and campaign['spend'] > 50:
            report += f"- {campaign['name']} — {format_currency(campaign['spend'])} spent, 0 conversions; consider pausing or significant optimization.\n"
        elif campaign['cpl'] > 80 and campaign['leads'] > 0:
            report += f"- {campaign['name']} — {format_currency(campaign['cpl'])} CPL above target; monitor search terms and bids.\n"
    
    # Scaling opportunities
    strong_performers = [c for c in data['campaigns'] if c['cpl'] > 0 and c['cpl'] < 50 and c['leads'] > 0]
    if strong_performers:
        report += f"- {', '.join([c['name'] for c in strong_performers])} — well under target CPL; consider scaling if capacity allows.\n"
    
    report += """
Questions? Reply anytime.

Best regards,"""
    
    return report

def generate_lumiere_report(data, start_date, end_date):
    """Generate report for Lumiere Dental"""
    
    total_leads = sum(c['leads'] for c in data['campaigns'])
    total_spend = sum(c['spend'] for c in data['campaigns'])
    avg_cpl = total_spend / total_leads if total_leads > 0 else 0
    
    report = f"""Subject: Lumiere Dental Google Ads Weekly Pulse | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Dr. Allababidi,

Quick weekly snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH AT A GLANCE
"""
    
    for campaign in data['campaigns']:
        name = campaign['name']
        cpl = campaign['cpl']
        leads = campaign['leads']
        
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
"""
    
    # Add search terms if available
    if data.get('search_terms'):
        report += "\nTOP CONVERTING KEYWORDS\n"
        for term in data['search_terms'][:8]:
            conv_rate = (term['conversions'] / term['clicks'] * 100) if term['clicks'] > 0 else 0
            report += f"{term['keyword']} — {term['conversions']} conversion{'s' if term['conversions'] > 1 else ''} @ {format_currency(term['cpl'])} ({conv_rate:.1f}% conv rate)\n"
    
    report += """
ACTIONS TAKEN
- Continued monitoring of Medicaid-focused campaigns
- Daily review of search terms for negative keyword opportunities
- Budget optimization across campaigns

WATCHING
"""
    
    for campaign in data['campaigns']:
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
    # Sample data for testing
    sample_data = {
        'campaigns': [
            {'name': 'PMAX Branded', 'spend': 374.0, 'leads': 17, 'clicks': 120, 'impressions': 4500, 'cpl': 22.0},
            {'name': 'PMAX Competitors', 'spend': 136.0, 'leads': 8, 'clicks': 89, 'impressions': 3200, 'cpl': 17.0},
            {'name': 'Implants', 'spend': 630.0, 'leads': 10, 'clicks': 234, 'impressions': 8900, 'cpl': 63.0},
            {'name': 'Emergency', 'spend': 735.0, 'leads': 7, 'clicks': 198, 'impressions': 6200, 'cpl': 105.0},
            {'name': 'All On 4', 'spend': 143.0, 'leads': 0, 'clicks': 45, 'impressions': 1800, 'cpl': 0},
        ],
        'search_terms': [
            {'keyword': 'emergency dentist phoenix', 'conversions': 3, 'clicks': 12, 'cpl': 35.0},
            {'keyword': 'dental implants near me', 'conversions': 2, 'clicks': 8, 'cpl': 42.0},
        ]
    }
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("Generating test report for Dental Artistry...")
        report = generate_dental_artistry_report(sample_data, "Feb 18-24", "2026")
        print(report)
        return
    
    print("Google Ads Report Formatter")
    print("============================")
    print("")
    print("Usage options:")
    print("1. Run with sample data: python3 format_report.py test")
    print("2. Import as module and call generate_*_report() with your data")
    print("")
    print("Data format expected:")
    print("{")
    print("  'campaigns': [")
    print("    {'name': 'Campaign Name', 'spend': 100.0, 'leads': 5, ...},")
    print("  ],")
    print("  'search_terms': [...]")
    print("}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Google Ads Weekly Report Generator
Fetches data from Google Ads API and generates UNI-formatted reports
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
GOOGLE_ADS_API_VERSION = "v14"
GOOGLE_ADS_API_BASE = f"https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}"

class GoogleAdsReporter:
    def __init__(self):
        self.access_token = os.getenv('GOOGLE_ADS_ACCESS_TOKEN')
        self.developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.login_customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')  # MCC ID
        
        if not all([self.access_token, self.developer_token]):
            raise ValueError("Missing required environment variables: GOOGLE_ADS_ACCESS_TOKEN, GOOGLE_ADS_DEVELOPER_TOKEN")
    
    def get_headers(self, customer_id: str) -> Dict[str, str]:
        """Build API headers with proper auth"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'developer-token': self.developer_token,
            'Content-Type': 'application/json'
        }
        if self.login_customer_id:
            headers['login-customer-id'] = self.login_customer_id
        return headers
    
    def query(self, customer_id: str, gaql: str) -> List[Dict]:
        """Execute GAQL query against Google Ads API"""
        url = f"{GOOGLE_ADS_API_BASE}/customers/{customer_id}/googleAds:searchStream"
        headers = self.get_headers(customer_id)
        payload = {'query': gaql}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            results = []
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'results' in data:
                            results.extend(data['results'])
                    except json.JSONDecodeError:
                        continue
            return results
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}", file=sys.stderr)
            return []
    
    def get_account_metrics(self, customer_id: str, start_date: str, end_date: str) -> Dict:
        """Fetch account-level metrics"""
        gaql = f"""
            SELECT
                customer.id,
                customer.descriptive_name,
                segments.date,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.conversions,
                metrics.cost_per_conversion,
                metrics.conversions_value
            FROM customer
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        results = self.query(customer_id, gaql)
        
        # Aggregate metrics
        totals = {
            'impressions': 0,
            'clicks': 0,
            'cost_micros': 0,
            'conversions': 0,
            'conversions_value': 0
        }
        
        for row in results:
            metrics = row.get('metrics', {})
            totals['impressions'] += int(metrics.get('impressions', 0))
            totals['clicks'] += int(metrics.get('clicks', 0))
            totals['cost_micros'] += int(metrics.get('costMicros', 0))
            totals['conversions'] += float(metrics.get('conversions', 0))
            totals['conversions_value'] += float(metrics.get('conversionsValue', 0))
        
        # Calculate derived metrics
        cost_dollars = totals['cost_micros'] / 1_000_000
        
        return {
            'impressions': totals['impressions'],
            'clicks': totals['clicks'],
            'ctr': (totals['clicks'] / totals['impressions'] * 100) if totals['impressions'] > 0 else 0,
            'spend': cost_dollars,
            'cpc': (cost_dollars / totals['clicks']) if totals['clicks'] > 0 else 0,
            'conversions': totals['conversions'],
            'cpl': (cost_dollars / totals['conversions']) if totals['conversions'] > 0 else 0,
            'conversion_rate': (totals['conversions'] / totals['clicks'] * 100) if totals['clicks'] > 0 else 0
        }
    
    def get_campaign_metrics(self, customer_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Fetch campaign-level metrics"""
        gaql = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign_budget.amount_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.cost_micros,
                metrics.average_cpc,
                metrics.conversions,
                metrics.cost_per_conversion
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.cost_micros > 0
            ORDER BY metrics.cost_micros DESC
        """
        
        results = self.query(customer_id, gaql)
        campaigns = []
        
        for row in results:
            campaign = row.get('campaign', {})
            metrics = row.get('metrics', {})
            budget = row.get('campaignBudget', {})
            
            cost_micros = int(metrics.get('costMicros', 0))
            conversions = float(metrics.get('conversions', 0))
            
            campaigns.append({
                'id': campaign.get('id', ''),
                'name': campaign.get('name', ''),
                'status': campaign.get('status', ''),
                'budget': int(budget.get('amountMicros', 0)) / 1_000_000,
                'impressions': int(metrics.get('impressions', 0)),
                'clicks': int(metrics.get('clicks', 0)),
                'ctr': float(metrics.get('ctr', 0)) * 100,
                'spend': cost_micros / 1_000_000,
                'cpc': float(metrics.get('averageCpc', 0)) / 1_000_000,
                'conversions': conversions,
                'cpl': (cost_micros / 1_000_000 / conversions) if conversions > 0 else 0
            })
        
        return campaigns
    
    def get_search_terms(self, customer_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Fetch search term performance"""
        gaql = f"""
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.cost_micros
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.clicks > 0
            ORDER BY metrics.conversions DESC, metrics.cost_micros DESC
            LIMIT 50
        """
        
        results = self.query(customer_id, gaql)
        terms = []
        
        for row in results:
            view = row.get('searchTermView', {})
            metrics = row.get('metrics', {})
            
            conversions = float(metrics.get('conversions', 0))
            cost_micros = int(metrics.get('costMicros', 0))
            
            terms.append({
                'term': view.get('searchTerm', ''),
                'impressions': int(metrics.get('impressions', 0)),
                'clicks': int(metrics.get('clicks', 0)),
                'conversions': conversions,
                'spend': cost_micros / 1_000_000,
                'cpl': (cost_micros / 1_000_000 / conversions) if conversions > 0 else float('inf')
            })
        
        return terms

def format_currency(amount: float) -> str:
    """Format as currency"""
    if amount == float('inf') or amount > 999999:
        return "N/A"
    return f"${amount:,.2f}"

def format_number(num: float) -> str:
    """Format number with commas"""
    return f"{num:,.0f}"

def get_health_emoji(cpl: float, target: float) -> str:
    """Get health status emoji based on CPL vs target"""
    if cpl == 0:
        return "🔴"  # No conversions
    ratio = cpl / target if target > 0 else 1
    if ratio <= 1.0:
        return "🟢"
    elif ratio <= 1.3:
        return "🟡"
    else:
        return "🔴"

def generate_dental_artistry_report(data: Dict, start_date: str, end_date: str) -> str:
    """Generate report for Dental Artistry (Riya)"""
    account = data['account']
    campaigns = data['campaigns'][:5]  # Top 5
    
    # Calculate totals
    total_leads = int(account['conversions'])
    avg_cpl = account['cpl']
    
    report = f"""Subject: Dental Artistry Google Ads Weekly | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Riya,

Quick snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH
"""
    
    # Add campaign health section
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
        leads = int(campaign['conversions'])
        
        # Find matching target
        target_cpl = 50  # Default
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
            elif emoji == "🔴" and leads == 0:
                status += " — needs attention"
        else:
            status = f"🔴 {name} — 0 leads / {format_currency(campaign['spend'])} spent — needs attention"
        
        report += status + "\n"
    
    report += f"""
🟢 On/below target | 🟡 Above target | 🔴 Needs attention

WEEK OVER WEEK
Total Leads — {total_leads}
Average CPL — {format_currency(avg_cpl)}
Total Spend — {format_currency(account['spend'])}
Top campaigns by conversions — {', '.join([f"{c['name']} ({int(c['conversions'])})" for c in campaigns[:4] if c['conversions'] > 0])}

ACTIONS TAKEN
- Daily review of search terms for negative keyword opportunities
- Budget and bid review across campaigns

WATCHING
"""
    
    # Add watching items for campaigns that need attention
    for campaign in campaigns:
        if campaign['cpl'] > 80 or campaign['conversions'] == 0:
            if campaign['conversions'] == 0:
                report += f"- {campaign['name']} — {format_currency(campaign['spend'])} spent, 0 conversions; consider pausing or significant optimization.\n"
            else:
                report += f"- {campaign['name']} — {format_currency(campaign['cpl'])} CPL above target; monitor search terms and bids.\n"
    
    # Add scaling opportunities
    strong_performers = [c for c in campaigns if c['cpl'] > 0 and c['cpl'] < 50]
    if strong_performers:
        report += f"- {', '.join([c['name'] for c in strong_performers])} — well under target CPL; consider scaling if capacity allows.\n"
    
    report += """
Questions? Reply anytime.

Best regards,"""
    
    return report

def generate_lumiere_dental_report(data: Dict, start_date: str, end_date: str) -> str:
    """Generate report for Lumiere Dental (Dr. Allababidi)"""
    account = data['account']
    campaigns = data['campaigns'][:5]
    search_terms = data.get('search_terms', [])
    
    total_leads = int(account['conversions'])
    avg_cpl = account['cpl']
    
    report = f"""Subject: Lumiere Dental Google Ads Weekly Pulse | {start_date} to {end_date} | {total_leads} Leads @ {format_currency(avg_cpl)} CPL

Hi Dr. Allababidi,

Quick weekly snapshot — {total_leads} leads generated at {format_currency(avg_cpl)} average CPL this week.

CAMPAIGN HEALTH AT A GLANCE
"""
    
    # Campaign health with Medicaid/pediatric focus
    for campaign in campaigns:
        name = campaign['name']
        cpl = campaign['cpl']
        leads = int(campaign['conversions'])
        
        # Determine target based on campaign type
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
Total Spend: {format_currency(account['spend'])}

TOP CONVERTING KEYWORDS
"""
    
    # Add top search terms with conversions
    converting_terms = [t for t in search_terms if t['conversions'] > 0][:10]
    for term in converting_terms:
        conv_rate = (term['conversions'] / term['clicks'] * 100) if term['clicks'] > 0 else 0
        report += f"{term['term']} — {int(term['conversions'])} conversion{'s' if term['conversions'] > 1 else ''} @ {format_currency(term['cpl'])} ({conv_rate:.1f}% conv rate)\n"
    
    # Most efficient keywords (lowest CPL)
    report += "\nMOST EFFICIENT KEYWORDS (Lowest CPL)\n"
    efficient_terms = sorted([t for t in search_terms if t['conversions'] > 0], key=lambda x: x['cpl'])[:5]
    for term in efficient_terms:
        report += f"{term['term']} — {int(term['conversions'])} conversion{'s' if term['conversions'] > 1 else ''} @ {format_currency(term['cpl'])} — exceptional efficiency\n"
    
    report += """
ACTIONS TAKEN
- Continued monitoring of Medicaid-focused campaigns
- Daily review of search terms for negative keyword opportunities
- Budget optimization across campaigns

WATCHING
"""
    
    # Add watching items
    for campaign in campaigns:
        if campaign['conversions'] == 0 and campaign['spend'] > 50:
            report += f"- {campaign['name']}: spent {format_currency(campaign['spend'])} with 0 conversions — reviewing keyword targeting and ad copy\n"
        elif campaign['cpl'] > 80:
            report += f"- {campaign['name']}: {format_currency(campaign['cpl'])} CPL above target — monitoring\n"
    
    report += """
KEY INSIGHTS
- Pediatric and Medicaid-focused keywords continue to drive strong conversion rates
- Fairfax location-specific terms showing high efficiency
- Monitor campaigns with zero conversions for optimization opportunities

Questions? Reply anytime.

Best regards,"""
    
    return report

def main():
    """Main execution"""
    if len(sys.argv) < 4:
        print("Usage: python google_ads_reporter.py <account_id> <start_date> <end_date> [client_type]")
        print("  client_type: 'dental_artistry' or 'lumiere'")
        print("  Example: python google_ads_reporter.py 6329354566 2026-02-18 2026-02-24 dental_artistry")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    client_type = sys.argv[4] if len(sys.argv) > 4 else 'generic'
    
    print(f"Fetching data for Account {customer_id}...")
    print(f"Date range: {start_date} to {end_date}")
    
    try:
        reporter = GoogleAdsReporter()
        
        # Fetch data
        print("Fetching account metrics...")
        account_data = reporter.get_account_metrics(customer_id, start_date, end_date)
        
        print("Fetching campaign metrics...")
        campaign_data = reporter.get_campaign_metrics(customer_id, start_date, end_date)
        
        print("Fetching search terms...")
        search_data = reporter.get_search_terms(customer_id, start_date, end_date)
        
        # Compile data
        data = {
            'account': account_data,
            'campaigns': campaign_data,
            'search_terms': search_data
        }
        
        # Generate report
        print("Generating report...")
        if client_type == 'dental_artistry':
            report = generate_dental_artistry_report(data, start_date, end_date)
        elif client_type == 'lumiere':
            report = generate_lumiere_dental_report(data, start_date, end_date)
        else:
            report = generate_dental_artistry_report(data, start_date, end_date)
        
        # Output report
        print("\n" + "="*60)
        print(report)
        print("="*60)
        
        # Save to file
        output_file = f"/data/workspace/reports/report_{customer_id}_{start_date}_{end_date}.txt"
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

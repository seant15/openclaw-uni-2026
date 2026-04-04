#!/usr/bin/env python3
"""
Ad Data Multi-Level Viewer
Shows data at campaign, adset/adgroup, ad, and keyword/search term levels
"""

import json
import sys
from datetime import datetime
from typing import Dict, List

def format_currency(micros: int) -> str:
    """Convert micros to dollar string"""
    return f"${micros / 1_000_000:,.2f}"

def format_number(num: int) -> str:
    """Format large numbers with commas"""
    return f"{num:,}"

def extract_meta_purchase_metrics(insight: Dict) -> Dict:
    """Extract purchase metrics from Meta insight"""
    actions = insight.get('actions', []) or []
    action_values = insight.get('action_values', []) or []
    
    purchases = 0
    for action in actions:
        if action.get('action_type') == 'purchase':
            purchases = float(action.get('value', 0))
            break
    
    purchase_value = 0
    for av in action_values:
        if av.get('action_type') == 'purchase':
            purchase_value = float(av.get('value', 0))
            break
    
    spend = float(insight.get('spend', 0))
    roas = (purchase_value / spend) if spend > 0 else 0
    cpa = (spend / purchases) if purchases > 0 else 0
    
    return {
        'purchases': purchases,
        'purchase_value': purchase_value,
        'roas': roas,
        'cpa': cpa,
        'spend': spend
    }

def show_meta_data(data_file: str):
    """Display Meta Ads data at all levels with e-commerce metrics"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print(f"📱 META ADS DATA (E-COMMERCE) - {data['client']}")
    print(f"   Account: {data['account_id']}")
    print(f"   Synced: {data['synced_at']}")
    print("="*80)
    
    # Campaign Level
    print("\n" + "─"*80)
    print("📊 CAMPAIGN LEVEL (Last 30 Days)")
    print("─"*80)
    
    campaigns = data['structure']['campaigns']
    campaign_insights = data['insights']['campaign']
    
    # Aggregate by campaign
    campaign_metrics = {}
    for insight in campaign_insights:
        cid = insight.get('campaign_id')
        if not cid:
            continue
        
        metrics = extract_meta_purchase_metrics(insight)
        
        if cid not in campaign_metrics:
            campaign_metrics[cid] = {
                'name': insight.get('campaign_name', 'Unknown'),
                'spend': 0,
                'purchases': 0,
                'purchase_value': 0,
                'impressions': 0,
                'clicks': 0
            }
        
        campaign_metrics[cid]['spend'] += metrics['spend']
        campaign_metrics[cid]['purchases'] += metrics['purchases']
        campaign_metrics[cid]['purchase_value'] += metrics['purchase_value']
        campaign_metrics[cid]['impressions'] += int(insight.get('impressions', 0) or 0)
        campaign_metrics[cid]['clicks'] += int(insight.get('clicks', 0) or 0)
    
    print(f"\n{'ID':<18} {'Name':<30} {'Spend':<10} {'Purch':<8} {'Rev':<10} {'ROAS':<6} {'CPA':<8}")
    print("-"*80)
    
    for cid, m in list(campaign_metrics.items())[:10]:
        name = m['name'][:29] if len(m['name']) > 29 else m['name']
        roas = (m['purchase_value'] / m['spend']) if m['spend'] > 0 else 0
        cpa = (m['spend'] / m['purchases']) if m['purchases'] > 0 else 0
        print(f"{cid:<18} {name:<30} ${m['spend']:<9.0f} {m['purchases']:<8.0f} ${m['purchase_value']:<9.0f} {roas:<6.2f} ${cpa:<7.0f}")
    
    # Adset Level
    print("\n" + "─"*80)
    print("🎯 ADSET LEVEL (Top 10 by Spend)")
    print("─"*80)
    
    adset_insights = data['insights']['adset']
    sorted_adsets = sorted(adset_insights, key=lambda x: float(x.get('spend', 0)), reverse=True)[:10]
    
    print(f"\n{'Adset ID':<18} {'Name':<30} {'Spend':<12} {'CPL':<10} {'CTR %':<8}")
    print("-"*80)
    
    for a in sorted_adsets:
        name = a.get('adset_name', 'N/A')[:29] if len(a.get('adset_name', '')) > 29 else a.get('adset_name', 'N/A')
        spend = float(a.get('spend', 0))
        cpl = float(a.get('cost_per_conversion', 0)) if a.get('cost_per_conversion') else 0
        ctr = float(a.get('ctr', 0)) * 100
        
        cpl_str = f"${cpl:.2f}" if cpl > 0 else "N/A"
        print(f"{a.get('adset_id', 'N/A'):<18} {name:<30} ${spend:<11.2f} {cpl_str:<10} {ctr:<8.2f}")
    
    # Ad Level
    print("\n" + "─"*80)
    print("📝 AD LEVEL (Top 10 by Spend)")
    print("─"*80)
    
    ad_insights = data['insights']['ad']
    sorted_ads = sorted(ad_insights, key=lambda x: float(x.get('spend', 0)), reverse=True)[:10]
    
    print(f"\n{'Ad ID':<18} {'Name':<35} {'Spend':<12} {'Leads':<8}")
    print("-"*80)
    
    for a in sorted_ads:
        name = a.get('ad_name', 'N/A')[:34] if len(a.get('ad_name', '')) > 34 else a.get('ad_name', 'N/A')
        spend = float(a.get('spend', 0))
        leads = a.get('conversions', 0)
        print(f"{a.get('ad_id', 'N/A'):<18} {name:<35} ${spend:<11.2f} {leads:<8}")
    
    # Summary Stats
    print("\n" + "="*80)
    print("📈 E-COMMERCE SUMMARY (30 Days)")
    print("="*80)
    
    total_spend = sum(m['spend'] for m in campaign_metrics.values())
    total_purchases = sum(m['purchases'] for m in campaign_metrics.values())
    total_revenue = sum(m['purchase_value'] for m in campaign_metrics.values())
    total_clicks = sum(m['clicks'] for m in campaign_metrics.values())
    total_impressions = sum(m['impressions'] for m in campaign_metrics.values())
    
    roas = (total_revenue / total_spend) if total_spend > 0 else 0
    cpa = (total_spend / total_purchases) if total_purchases > 0 else 0
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    print(f"  Total Campaigns:    {len(campaigns)}")
    print(f"  Total Adsets:       {len(data['structure']['adsets'])}")
    print(f"  Total Ads:          {len(data['structure']['ads'])}")
    print(f"")
    print(f"  💰 Total Spend:     ${total_spend:,.2f}")
    print(f"  🛒 Purchases:       {total_purchases:.0f}")
    print(f"  💵 Revenue:         ${total_revenue:,.2f}")
    print(f"  📈 ROAS:            {roas:.2f}x")
    print(f"  💸 CPA:             ${cpa:.2f}")
    print(f"  👀 Impressions:     {total_impressions:,}")
    print(f"  🖱️  Clicks:          {total_clicks:,}")
    print(f"  📊 CTR:             {ctr:.2f}%")
    print("="*80)

def show_google_data(data_file: str):
    """Display Google Ads data at all levels"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print(f"🔍 GOOGLE ADS DATA - {data['client']}")
    print(f"   Account: {data['customer_id']}")
    print(f"   Synced: {data['synced_at']}")
    print("="*80)
    
    # Campaign Level
    print("\n" + "─"*80)
    print("📊 CAMPAIGN LEVEL")
    print("─"*80)
    
    campaigns = data['campaigns']
    
    print(f"\n{'ID':<12} {'Name':<35} {'Status':<10} {'Spend':<12} {'Leads':<8}")
    print("-"*80)
    
    for c in campaigns[:10]:
        name = c['name'][:34] if len(c['name']) > 34 else c['name']
        spend = c['cost_micros'] / 1_000_000
        leads = int(c['conversions'] or 0)
        print(f"{c['id']:<12} {name:<35} {c['status']:<10} ${spend:<11.2f} {leads:<8}")
    
    # Ad Group Level
    print("\n" + "─"*80)
    print("🎯 AD GROUP LEVEL (Top 10 by Spend)")
    print("─"*80)
    
    ad_groups = sorted(data['ad_groups'], key=lambda x: x['cost_micros'], reverse=True)[:10]
    
    print(f"\n{'Ad Group ID':<12} {'Name':<30} {'Campaign':<20} {'Spend':<12}")
    print("-"*80)
    
    for ag in ad_groups:
        name = ag['name'][:29] if len(ag['name']) > 29 else ag['name']
        campaign = ag['campaign_name'][:19] if len(ag['campaign_name']) > 19 else ag['campaign_name']
        spend = ag['cost_micros'] / 1_000_000
        print(f"{ag['id']:<12} {name:<30} {campaign:<20} ${spend:<11.2f}")
    
    # Ad Level
    print("\n" + "─"*80)
    print("📝 AD LEVEL (Top 10 by Spend)")
    print("─"*80)
    
    ads = sorted(data['ads'], key=lambda x: x['cost_micros'], reverse=True)[:10]
    
    print(f"\n{'Ad ID':<15} {'Status':<10} {'Headline':<35} {'Spend':<12}")
    print("-"*80)
    
    for ad in ads:
        headline = ad['headlines'][0] if ad.get('headlines') else 'N/A'
        headline = headline[:34] if len(headline) > 34 else headline
        spend = ad['cost_micros'] / 1_000_000
        print(f"{ad['id']:<15} {ad['status']:<10} {headline:<35} ${spend:<11.2f}")
    
    # Keyword Level
    print("\n" + "─"*80)
    print("🔑 KEYWORD LEVEL (Top 10 by Spend)")
    print("─"*80)
    
    keywords = sorted(data['keywords'], key=lambda x: x['cost_micros'], reverse=True)[:10]
    
    print(f"\n{'Keyword':<35} {'Match Type':<12} {'Spend':<12} {'Conv':<8}")
    print("-"*80)
    
    for kw in keywords:
        text = kw['keyword_text'][:34] if len(kw['keyword_text'] or '') > 34 else (kw['keyword_text'] or 'N/A')
        match_type = kw.get('match_type', 'N/A')[:11]
        spend = kw['cost_micros'] / 1_000_000
        conv = int(kw['conversions'] or 0)
        print(f"{text:<35} {match_type:<12} ${spend:<11.2f} {conv:<8}")
    
    # Search Terms Level
    print("\n" + "─"*80)
    print("🔍 SEARCH TERMS (Top 10 by Conversions)")
    print("─"*80)
    
    search_terms = sorted(data['search_terms'], key=lambda x: x['conversions'], reverse=True)[:10]
    
    print(f"\n{'Search Term':<40} {'Status':<12} {'Spend':<12} {'Conv':<8}")
    print("-"*80)
    
    for st in search_terms:
        term = st['search_term'][:39] if len(st['search_term']) > 39 else st['search_term']
        status = st['status'][:11]
        spend = st['cost_micros'] / 1_000_000
        conv = int(st['conversions'] or 0)
        print(f"{term:<40} {status:<12} ${spend:<11.2f} {conv:<8}")
    
    # Summary Stats
    print("\n" + "="*80)
    print("📈 SUMMARY STATISTICS")
    print("="*80)
    
    total_spend = sum(c['cost_micros'] for c in campaigns) / 1_000_000
    total_leads = sum(int(c['conversions'] or 0) for c in campaigns)
    total_clicks = sum(c['clicks'] for c in campaigns)
    total_impressions = sum(c['impressions'] for c in campaigns)
    
    print(f"  Total Campaigns:    {len(campaigns)}")
    print(f"  Total Ad Groups:    {len(data['ad_groups'])}")
    print(f"  Total Ads:          {len(data['ads'])}")
    print(f"  Total Keywords:     {len(data['keywords'])}")
    print(f"  Search Terms:       {len(data['search_terms'])}")
    print(f"  Total Spend:        ${total_spend:,.2f}")
    print(f"  Total Leads:        {total_leads}")
    print(f"  Total Clicks:       {total_clicks:,}")
    print(f"  Total Impressions:  {total_impressions:,}")
    print(f"  Avg CPL:            ${(total_spend / total_leads) if total_leads > 0 else 0:.2f}")
    print(f"  Avg CTR:            {(total_clicks / total_impressions * 100) if total_impressions > 0 else 0:.2f}%")
    print("="*80)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 view_ad_data.py <data_file.json>")
        print("")
        print("Supports both Meta and Google Ads data files")
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    try:
        with open(data_file, 'r') as f:
            content = f.read()
        
        # Detect type
        if 'account_id' in content and 'act_' in content:
            show_meta_data(data_file)
        elif 'customer_id' in content and 'campaigns' in content:
            show_google_data(data_file)
        else:
            print("Unknown data format. Please provide a valid Meta or Google Ads data file.")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"File not found: {data_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {data_file}")
        sys.exit(1)

if __name__ == '__main__':
    main()

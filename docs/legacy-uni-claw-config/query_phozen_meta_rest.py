#!/usr/bin/env python3
"""
Query Meta Ads data for PhoZen account - Last 14 Days
Uses Supabase REST API via curl
"""
import subprocess
import json
from datetime import date, timedelta

# Supabase credentials
SUPABASE_URL = "https://jcghdthijgjttmpthagj.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpjZ2hkdGhpamdqdHRtcHRoYWdqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTE1MDI2OSwiZXhwIjoyMDgwNzI2MjY5fQ.9SRXOEINIojJKcCcAVlturI6tPbR5qC6bpY66JF5Zpk"

def supabase_query(table, select="*", filters=None):
    """Query Supabase via REST API using curl"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if filters:
        url += "?" + "&".join(filters)
    else:
        url += "?select=" + select
    
    cmd = [
        "curl", "-s", "-X", "GET",
        "-H", f"Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "-H", "apikey: " + SUPABASE_SERVICE_ROLE_KEY,
        "-H", "Content-Type: application/json",
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    return None

def get_phozen_meta_data():
    # Calculate date range (last 14 days)
    end_date = date(2026, 4, 6)  # Apr 6, 2026 as specified
    start_date = date(2026, 3, 24)  # Mar 24, 2026
    
    print("=" * 70)
    print("PHOZEN META ADS - CAMPAIGN LEVEL BREAKDOWN")
    print("=" * 70)
    print(f"Reporting Period: March 24 - April 6, 2026 (14 days)")
    print("=" * 70)
    print()
    
    # Step 1: Find PhoZen client
    clients = supabase_query("clients", select="*", filters=["name=ilike.*pho*"])
    
    if not clients or (isinstance(clients, dict) and 'error' in clients) or len(clients) == 0:
        print("No client found matching 'PhoZen'")
        # List all clients for reference
        all_clients = supabase_query("clients", select="id,name")
        print("\nAvailable clients:")
        for c in all_clients:
            print(f"   - {c['name']} (ID: {c['id']})")
        return
    
    client = clients[0]
    client_id = client['id']
    print(f"Client: {client['name']} (ID: {client_id})")
    print(f"Business Type: {client.get('business_type', 'N/A')}")
    print(f"Target ROAS: {client.get('target_roas', 'N/A')}x")
    print()
    
    # Step 2: Query meta_ads table for campaign-level data
    meta_ads = supabase_query(
        "meta_ads",
        select="*",
        filters=[
            f"client_id=eq.{client_id}",
            f"date=gte.{start_date.isoformat()}",
            f"date=lte.{end_date.isoformat()}",
            "order=date.asc"
        ]
    )
    
    if isinstance(meta_ads, dict) and 'error' in meta_ads:
        print(f"Error from meta_ads query: {meta_ads}")
        return
    
    if not meta_ads or len(meta_ads) == 0:
        print("No Meta Ads data found for the period March 24 - April 6, 2026")
        # Check for any data at all
        any_data = supabase_query(
            "meta_ads",
            select="date,spend,revenue,clicks,conversions,impressions,campaign_name",
            filters=[
                f"client_id=eq.{client_id}",
                "order=date.desc",
                "limit=10"
            ]
        )
        if any_data and len(any_data) > 0 and not isinstance(any_data, dict):
            print("\nMost recent data available:")
            for row in any_data:
                print(f"   {row['date']}: {row.get('campaign_name', 'N/A')} - ${row.get('spend', 0)} spent")
        return
    
    # Step 3: Aggregate data by campaign
    campaigns_data = {}
    daily_data = []
    
    for row in meta_ads:
        campaign_name = row.get('campaign_name', 'Unnamed')
        campaign_id = row.get('campaign_id', 'unknown')
        
        spend = float(row.get('spend', 0) or 0)
        revenue = float(row.get('revenue', 0) or 0)
        clicks = int(row.get('clicks', 0) or 0)
        impressions = int(row.get('impressions', 0) or 0)
        conversions = float(row.get('conversions', 0) or 0)
        date_val = row.get('date', '')
        
        # Aggregate by campaign
        if campaign_id not in campaigns_data:
            campaigns_data[campaign_id] = {
                'name': campaign_name,
                'spend': 0,
                'revenue': 0,
                'clicks': 0,
                'impressions': 0,
                'conversions': 0,
                'days_active': 0
            }
        
        campaigns_data[campaign_id]['spend'] += spend
        campaigns_data[campaign_id]['revenue'] += revenue
        campaigns_data[campaign_id]['clicks'] += clicks
        campaigns_data[campaign_id]['impressions'] += impressions
        campaigns_data[campaign_id]['conversions'] += conversions
        if spend > 0:
            campaigns_data[campaign_id]['days_active'] += 1
        
        daily_data.append({
            'date': date_val,
            'campaign': campaign_name,
            'spend': spend,
            'revenue': revenue,
            'clicks': clicks,
            'impressions': impressions,
            'conversions': conversions
        })
    
    # Step 4: Calculate metrics for each campaign
    campaign_list = []
    for cid, data in campaigns_data.items():
        spend = data['spend']
        revenue = data['revenue']
        clicks = data['clicks']
        impressions = data['impressions']
        conversions = data['conversions']
        
        roas = revenue / spend if spend > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpa = spend / conversions if conversions > 0 else 0
        
        campaign_list.append({
            'id': cid,
            'name': data['name'],
            'spend': spend,
            'revenue': revenue,
            'roas': roas,
            'impressions': impressions,
            'clicks': clicks,
            'ctr': ctr,
            'conversions': conversions,
            'cpa': cpa,
            'days_active': data['days_active']
        })
    
    # Sort by spend (descending)
    campaign_list.sort(key=lambda x: x['spend'], reverse=True)
    
    # Step 5: Display Campaign Breakdown
    print("-" * 90)
    print("CAMPAIGN LEVEL PERFORMANCE BREAKDOWN")
    print("-" * 90)
    print(f"{'Campaign Name':<35} {'Spend':>10} {'Rev':>10} {'ROAS':>6} {'Impr':>10} {'Clicks':>8} {'CTR':>5} {'Conv':>6} {'CPA':>8}")
    print("-" * 90)
    
    total_spend = 0
    total_revenue = 0
    total_clicks = 0
    total_impressions = 0
    total_conversions = 0
    
    for camp in campaign_list:
        print(f"{camp['name'][:34]:<35} ${camp['spend']:>8.2f} ${camp['revenue']:>8.2f} {camp['roas']:>5.2f}x {camp['impressions']:>10,} {camp['clicks']:>8,} {camp['ctr']:>4.2f}% {camp['conversions']:>6.0f} ${camp['cpa']:>7.0f}")
        total_spend += camp['spend']
        total_revenue += camp['revenue']
        total_clicks += camp['clicks']
        total_impressions += camp['impressions']
        total_conversions += camp['conversions']
    
    print("-" * 90)
    total_roas = total_revenue / total_spend if total_spend > 0 else 0
    total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    total_cpa = total_spend / total_conversions if total_conversions > 0 else 0
    print(f"{'TOTAL':<35} ${total_spend:>8.2f} ${total_revenue:>8.2f} {total_roas:>5.2f}x {total_impressions:>10,} {total_clicks:>8,} {total_ctr:>4.2f}% {total_conversions:>6.0f} ${total_cpa:>7.0f}")
    print()
    
    # Step 6: Top Performing Campaigns (by ROAS, min $50 spend)
    print("=" * 70)
    print("TOP PERFORMING CAMPAIGNS")
    print("=" * 70)
    top_roas = [c for c in campaign_list if c['spend'] >= 50]
    top_roas.sort(key=lambda x: x['roas'], reverse=True)
    
    if top_roas:
        for i, camp in enumerate(top_roas[:5], 1):
            print(f"{i}. {camp['name']}")
            print(f"   Spend: ${camp['spend']:,.2f} | ROAS: {camp['roas']:.2f}x | Conv: {camp['conversions']:.0f} | CPA: ${camp['cpa']:.2f}")
    else:
        print("No campaigns with sufficient spend ($50+) to evaluate ROAS performance")
    print()
    
    # Step 7: Underperforming Campaigns (ROAS below target)
    print("=" * 70)
    print("UNDERPERFORMING CAMPAIGNS")
    print("=" * 70)
    target_roas = client.get('target_roas', 2.5)
    underperforming = [c for c in campaign_list if c['spend'] >= 50 and c['roas'] < target_roas]
    underperforming.sort(key=lambda x: x['roas'])
    
    if underperforming:
        for camp in underperforming:
            roas_gap = ((camp['roas'] / target_roas) - 1) * 100
            print(f"- {camp['name']}")
            print(f"  ROAS: {camp['roas']:.2f}x (Target: {target_roas}x, {roas_gap:+.1f}% vs target)")
            print(f"  Spend: ${camp['spend']:,.2f} | Conv: {camp['conversions']:.0f} | CPA: ${camp['cpa']:.2f}")
    else:
        print("All campaigns with sufficient spend are meeting or exceeding target ROAS")
    print()
    
    # Step 8: Budget Allocation
    print("=" * 70)
    print("BUDGET ALLOCATION ACROSS CAMPAIGNS")
    print("=" * 70)
    for camp in campaign_list:
        pct = (camp['spend'] / total_spend * 100) if total_spend > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"{camp['name'][:35]:<36} ${camp['spend']:>8.2f} ({pct:>5.1f}%) {bar}")
    print("-" * 70)
    print(f"{'TOTAL':<36} ${total_spend:>8.2f} (100.0%)")
    print()
    
    # Step 9: Summary
    print("=" * 70)
    print("14-DAY PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"   Total Spend:           ${total_spend:,.2f}")
    print(f"   Total Revenue:         ${total_revenue:,.2f}")
    print(f"   Overall ROAS:          {total_roas:.2f}x")
    print(f"   Total Impressions:     {total_impressions:,}")
    print(f"   Total Clicks:          {total_clicks:,}")
    print(f"   Overall CTR:           {total_ctr:.2f}%")
    print(f"   Total Conversions:     {total_conversions:.0f}")
    print(f"   Cost Per Acquisition:  ${total_cpa:.2f}")
    print(f"   Average Daily Spend:   ${total_spend/14:.2f}")
    print(f"   Active Campaigns:      {len(campaign_list)}")
    print()
    
    # Target comparison
    if target_roas:
        roas_vs_target = ((total_roas / target_roas) - 1) * 100
        print(f"   Target ROAS:           {target_roas}x")
        print(f"   ROAS vs Target:        {roas_vs_target:+.1f}%")
        if roas_vs_target >= 0:
            print(f"   Status:                Meeting target")
        else:
            print(f"   Status:                Below target - optimization needed")
    print()
    
    return campaign_list

if __name__ == "__main__":
    get_phozen_meta_data()

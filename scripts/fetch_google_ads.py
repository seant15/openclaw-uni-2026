#!/usr/bin/env python3
"""
Google Ads Data Fetcher using official Python client
Fetches campaign data and outputs JSON for report generation
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def get_client():
    """Initialize Google Ads API client from environment variables"""
    
    # Check required credentials
    required_vars = [
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET',
        'GOOGLE_ADS_REFRESH_TOKEN'
    ]
    
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    # Build client configuration
    config = {
        'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
        'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
        'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
        'use_proto_plus': True,
    }
    
    # Optional login customer ID (MCC)
    login_customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    if login_customer_id:
        config['login_customer_id'] = login_customer_id.replace('-', '')
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        print(f"✓ Google Ads client initialized")
        if login_customer_id:
            print(f"  Using MCC: {login_customer_id}")
        return client
    except Exception as e:
        print(f"ERROR: Failed to initialize Google Ads client: {e}")
        sys.exit(1)

def fetch_account_metrics(client, customer_id, start_date, end_date):
    """Fetch account-level metrics"""
    
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
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
    
    try:
        response = ga_service.search(customer_id=customer_id.replace('-', ''), query=query)
        
        totals = {
            'impressions': 0,
            'clicks': 0,
            'cost_micros': 0,
            'conversions': 0,
            'conversions_value': 0
        }
        
        customer_name = ""
        
        for row in response:
            customer_name = row.customer.descriptive_name
            metrics = row.metrics
            totals['impressions'] += metrics.impressions
            totals['clicks'] += metrics.clicks
            totals['cost_micros'] += metrics.cost_micros
            totals['conversions'] += metrics.conversions
            totals['conversions_value'] += metrics.conversions_value
        
        # Calculate derived metrics
        cost_dollars = totals['cost_micros'] / 1_000_000
        
        return {
            'customer_name': customer_name,
            'impressions': totals['impressions'],
            'clicks': totals['clicks'],
            'ctr': (totals['clicks'] / totals['impressions'] * 100) if totals['impressions'] > 0 else 0,
            'spend': cost_dollars,
            'cpc': (cost_dollars / totals['clicks']) if totals['clicks'] > 0 else 0,
            'conversions': totals['conversions'],
            'cpl': (cost_dollars / totals['conversions']) if totals['conversions'] > 0 else 0,
            'conversion_rate': (totals['conversions'] / totals['clicks'] * 100) if totals['clicks'] > 0 else 0
        }
        
    except GoogleAdsException as e:
        print(f"ERROR: Google Ads API error: {e}")
        return None

def fetch_campaign_metrics(client, customer_id, start_date, end_date):
    """Fetch campaign-level metrics"""
    
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
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
        LIMIT 10
    """
    
    try:
        response = ga_service.search(customer_id=customer_id.replace('-', ''), query=query)
        
        campaigns = []
        for row in response:
            campaign = row.campaign
            metrics = row.metrics
            budget = row.campaign_budget
            
            cost_micros = metrics.cost_micros
            conversions = metrics.conversions
            
            campaigns.append({
                'id': campaign.id,
                'name': campaign.name,
                'status': str(campaign.status).replace('CampaignStatus.', ''),
                'budget': budget.amount_micros / 1_000_000 if budget.amount_micros else 0,
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'ctr': metrics.ctr * 100,
                'spend': cost_micros / 1_000_000,
                'cpc': metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0,
                'leads': conversions,
                'cpl': (cost_micros / 1_000_000 / conversions) if conversions > 0 else 0
            })
        
        return campaigns
        
    except GoogleAdsException as e:
        print(f"ERROR: Google Ads API error: {e}")
        return []

def fetch_search_terms(client, customer_id, start_date, end_date):
    """Fetch search term performance"""
    
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
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
        LIMIT 30
    """
    
    try:
        response = ga_service.search(customer_id=customer_id.replace('-', ''), query=query)
        
        terms = []
        for row in response:
            view = row.search_term_view
            metrics = row.metrics
            
            conversions = metrics.conversions
            cost_micros = metrics.cost_micros
            
            terms.append({
                'keyword': view.search_term,
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'conversions': conversions,
                'spend': cost_micros / 1_000_000,
                'cpl': (cost_micros / 1_000_000 / conversions) if conversions > 0 else float('inf')
            })
        
        return terms
        
    except GoogleAdsException as e:
        print(f"ERROR: Google Ads API error (search terms): {e}")
        return []

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 fetch_google_ads.py <customer_id> <start_date> <end_date>")
        print("  customer_id: Google Ads account ID (e.g., 6329354566)")
        print("  start_date: YYYY-MM-DD format")
        print("  end_date: YYYY-MM-DD format")
        print("")
        print("Example:")
        print("  python3 fetch_google_ads.py 6329354566 2026-02-18 2026-02-24")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    
    print("=" * 60)
    print("GOOGLE ADS DATA FETCHER")
    print("=" * 60)
    print(f"Account ID: {customer_id}")
    print(f"Date Range: {start_date} to {end_date}")
    print("")
    
    # Initialize client
    client = get_client()
    
    # Fetch data
    print("Fetching account metrics...")
    account_data = fetch_account_metrics(client, customer_id, start_date, end_date)
    
    if account_data is None:
        print("ERROR: Failed to fetch account data")
        sys.exit(1)
    
    print(f"✓ Account: {account_data['customer_name']}")
    print(f"  Spend: ${account_data['spend']:,.2f}")
    print(f"  Leads: {account_data['conversions']:.0f}")
    
    print("")
    print("Fetching campaign metrics...")
    campaign_data = fetch_campaign_metrics(client, customer_id, start_date, end_date)
    print(f"✓ {len(campaign_data)} campaigns found")
    
    print("")
    print("Fetching search terms...")
    search_data = fetch_search_terms(client, customer_id, start_date, end_date)
    print(f"✓ {len(search_data)} search terms found")
    
    # Compile output
    output = {
        'account': account_data,
        'campaigns': campaign_data,
        'search_terms': search_data,
        'metadata': {
            'customer_id': customer_id,
            'start_date': start_date,
            'end_date': end_date,
            'fetched_at': datetime.now().isoformat()
        }
    }
    
    # Save to file
    output_file = f"/tmp/google_ads_data_{customer_id}_{start_date}_{end_date}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("")
    print("=" * 60)
    print("DATA FETCHED SUCCESSFULLY")
    print("=" * 60)
    print(f"Output file: {output_file}")
    print("")
    print("Next step: Generate report with:")
    print(f"  python3 /data/workspace/scripts/generate_report.py {output_file}")

if __name__ == '__main__':
    main()

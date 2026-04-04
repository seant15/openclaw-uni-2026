#!/usr/bin/env python3
"""
Meta Ads API Data Fetcher
Pulls campaign, adset, and ad-level data into Supabase
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Supabase config
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Meta API config
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_API_VERSION = 'v18.0'
META_API_BASE = f'https://graph.facebook.com/{META_API_VERSION}'

class MetaAdsFetcher:
    def __init__(self, access_token: str = None):
        self.access_token = access_token or META_ACCESS_TOKEN
        self.session = requests.Session()
        
    def fetch_insights(self, account_id: str, level: str, date_preset: str = 'last_30d', 
                       time_increment: int = 1, fields: List[str] = None, breakdowns: List[str] = None) -> List[Dict]:
        """
        Fetch insights data from Meta Ads API with e-commerce metrics
        
        Levels: account, campaign, adset, ad
        E-commerce focus: purchases, CPA, ROAS
        """
        if not fields:
            fields = [
                'account_id', 'account_name',
                'campaign_id', 'campaign_name', 
                'adset_id', 'adset_name',
                'ad_id', 'ad_name',
                'impressions', 'clicks', 'spend', 
                'ctr', 'cpc', 'cpm',
                'actions', 'action_values'
            ]
        
        url = f"{META_API_BASE}/{account_id}/insights"
        
        params = {
            'access_token': self.access_token,
            'level': level,
            'fields': ','.join(fields),
            'date_preset': date_preset,
            'time_increment': time_increment,  # Daily breakdown
            'limit': 1000
        }
        
        if breakdowns:
            params['breakdowns'] = ','.join(breakdowns)
        
        all_data = []
        while url:
            try:
                response = self.session.get(url, params=params if '?' not in url else None)
                response.raise_for_status()
                data = response.json()
                
                if 'error' in data:
                    print(f"Meta API Error: {data['error']}")
                    break
                
                all_data.extend(data.get('data', []))
                
                # Pagination
                url = data.get('paging', {}).get('next')
                params = None  # Only use params on first request
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                break
        
        return all_data
    
    def fetch_campaigns(self, account_id: str) -> List[Dict]:
        """Fetch campaign structure"""
        url = f"{META_API_BASE}/{account_id}/campaigns"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,objective,daily_budget,lifetime_budget,budget_remaining,start_time,stop_time',
            'limit': 1000
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                print(f"Meta API Error: {data['error']}")
                return []
            
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
    
    def fetch_adsets(self, account_id: str) -> List[Dict]:
        """Fetch adset structure"""
        url = f"{META_API_BASE}/{account_id}/adsets"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,campaign_id,daily_budget,lifetime_budget,targeting,bid_amount,billing_event',
            'limit': 1000
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                print(f"Meta API Error: {data['error']}")
                return []
            
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
    
    def fetch_ads(self, account_id: str) -> List[Dict]:
        """Fetch ad structure"""
        url = f"{META_API_BASE}/{account_id}/ads"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,adset_id,campaign_id,creative,tracking_specs',
            'limit': 1000
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                print(f"Meta API Error: {data['error']}")
                return []
            
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
    
    def extract_purchase_metrics(self, insight: Dict) -> Dict:
        """Extract purchase metrics from actions and action_values"""
        actions = insight.get('actions', []) or []
        action_values = insight.get('action_values', []) or []
        
        # Find purchases in actions
        purchases = 0
        for action in actions:
            if action.get('action_type') == 'purchase':
                purchases = float(action.get('value', 0))
                break
        
        # Find purchase value in action_values
        purchase_value = 0
        for av in action_values:
            if av.get('action_type') == 'purchase':
                purchase_value = float(av.get('value', 0))
                break
        
        # Get cost per purchase from cost_per_action_type
        cost_per_action_type = insight.get('cost_per_action_type', []) or []
        cost_per_purchase = 0
        for cpa in cost_per_action_type:
            if cpa.get('action_type') == 'purchase':
                cost_per_purchase = float(cpa.get('value', 0))
                break
        
        # Calculate ROAS if we have spend and purchase value
        spend = float(insight.get('spend', 0))
        roas = (purchase_value / spend) if spend > 0 else 0
        
        return {
            'purchases': purchases,
            'purchase_value': purchase_value,
            'cost_per_purchase': cost_per_purchase,
            'roas': roas,
            'spend': spend
        }

    def sync_to_supabase(self, account_id: str, client_name: str) -> Dict:
        """
        Full sync cycle for a Meta account - E-commerce focused
        Returns summary of synced data
        """
        print(f"\n{'='*60}")
        print(f"META ADS SYNC (E-COMMERCE): {account_id}")
        print(f"Client: {client_name}")
        print(f"{'='*60}\n")
        
        results = {
            'account_id': account_id,
            'client': client_name,
            'timestamp': datetime.now().isoformat(),
            'campaigns': 0,
            'adsets': 0,
            'ads': 0,
            'campaign_insights': 0,
            'adset_insights': 0,
            'ad_insights': 0,
            'total_purchases': 0,
            'total_purchase_value': 0,
            'total_spend': 0,
            'avg_roas': 0
        }
        
        # Fetch structure
        print("📊 Fetching structure...")
        
        print("  - Campaigns...")
        campaigns = self.fetch_campaigns(account_id)
        results['campaigns'] = len(campaigns)
        print(f"    ✓ {len(campaigns)} campaigns")
        
        print("  - Adsets...")
        adsets = self.fetch_adsets(account_id)
        results['adsets'] = len(adsets)
        print(f"    ✓ {len(adsets)} adsets")
        
        print("  - Ads...")
        ads = self.fetch_ads(account_id)
        results['ads'] = len(ads)
        print(f"    ✓ {len(ads)} ads")
        
        # Fetch insights at each level - Last 30 days for testing
        print("\n📈 Fetching performance data (Last 30 Days)...")
        
        print("  - Campaign insights...")
        campaign_insights = self.fetch_insights(account_id, level='campaign', date_preset='last_30d', time_increment=1)
        results['campaign_insights'] = len(campaign_insights)
        
        # Calculate e-commerce totals
        total_purchases = 0
        total_purchase_value = 0
        total_spend = 0
        
        for insight in campaign_insights:
            metrics = self.extract_purchase_metrics(insight)
            total_purchases += metrics['purchases']
            total_purchase_value += metrics['purchase_value']
            total_spend += metrics['spend']
        
        results['total_purchases'] = total_purchases
        results['total_purchase_value'] = total_purchase_value
        results['total_spend'] = total_spend
        results['avg_roas'] = (total_purchase_value / total_spend) if total_spend > 0 else 0
        
        print(f"    ✓ {len(campaign_insights)} daily records")
        print(f"    💰 Spend: ${total_spend:,.2f}")
        print(f"    🛒 Purchases: {total_purchases:.0f}")
        print(f"    💵 Purchase Value: ${total_purchase_value:,.2f}")
        print(f"    📈 ROAS: {results['avg_roas']:.2f}x")
        print(f"    💸 CPA: ${(total_spend / total_purchases) if total_purchases > 0 else 0:.2f}")
        
        print("  - Adset insights...")
        adset_insights = self.fetch_insights(account_id, level='adset', date_preset='last_30d', time_increment=1)
        results['adset_insights'] = len(adset_insights)
        print(f"    ✓ {len(adset_insights)} records")
        
        print("  - Ad insights...")
        ad_insights = self.fetch_insights(account_id, level='ad', date_preset='last_30d', time_increment=1)
        results['ad_insights'] = len(ad_insights)
        print(f"    ✓ {len(ad_insights)} records")
        
        # Store data
        output = {
            'account_id': account_id,
            'client': client_name,
            'synced_at': datetime.now().isoformat(),
            'structure': {
                'campaigns': campaigns,
                'adsets': adsets,
                'ads': ads
            },
            'insights': {
                'campaign': campaign_insights,
                'adset': adset_insights,
                'ad': ad_insights
            }
        }
        
        # Save to file (for now - Supabase insert coming next)
        output_file = f"/tmp/meta_ads_{account_id.replace('act_', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n✅ Data saved to: {output_file}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 fetch_meta_ads.py <account_id> <client_name>")
        print("")
        print("Examples:")
        print("  python3 fetch_meta_ads.py act_281592916520074 LEIVIP")
        print("  python3 fetch_meta_ads.py act_175918763181986 PROD")
        print("")
        print("E-commerce metrics pulled:")
        print("  - Purchases (not just conversions)")
        print("  - Cost Per Purchase (CPA)")
        print("  - Purchase Value (Revenue)")
        print("  - ROAS (Return on Ad Spend)")
        sys.exit(1)
    
    account_id = sys.argv[1]
    client_name = sys.argv[2]
    
    # Ensure account_id has act_ prefix
    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"
    
    fetcher = MetaAdsFetcher()
    results = fetcher.sync_to_supabase(account_id, client_name)
    
    print("\n" + "="*60)
    print("SYNC SUMMARY")
    print("="*60)
    print(f"  Account: {results['account_id']}")
    print(f"  Client: {results['client']}")
    print(f"  Campaigns: {results['campaigns']}")
    print(f"  Adsets: {results['adsets']}")
    print(f"  Ads: {results['ads']}")
    print("")
    print("  📊 E-COMMERCE METRICS (30 Days):")
    print(f"    Total Spend: ${results['total_spend']:,.2f}")
    print(f"    Purchases: {results['total_purchases']:.0f}")
    print(f"    Purchase Value: ${results['total_purchase_value']:,.2f}")
    print(f"    ROAS: {results['avg_roas']:.2f}x")
    print(f"    CPA: ${(results['total_spend'] / results['total_purchases']) if results['total_purchases'] > 0 else 0:.2f}")
    print("="*60)

if __name__ == '__main__':
    main()

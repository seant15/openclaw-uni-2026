#!/usr/bin/env python3
"""
Supabase Data Inserter
Inserts fetched ad data into Supabase tables
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class SupabaseInserter:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def insert_meta_data(self, data: Dict) -> Dict:
        """Insert Meta Ads data into Supabase"""
        results = {'inserted': 0, 'errors': []}
        
        # Insert campaigns
        for campaign in data['structure']['campaigns']:
            campaign_data = {
                'id': f"meta_{campaign['id']}",
                'account_id': data['account_id'],
                'platform': 'meta',
                'campaign_id': campaign['id'],
                'campaign_name': campaign['name'],
                'status': campaign['status'],
                'start_date': campaign.get('start_time', '').split('T')[0] if campaign.get('start_time') else None,
                'end_date': campaign.get('stop_time', '').split('T')[0] if campaign.get('stop_time') else None,
                'synced_at': data['synced_at']
            }
            
            try:
                self.client.table('campaigns').upsert(campaign_data).execute()
                results['inserted'] += 1
            except Exception as e:
                results['errors'].append(f"Campaign {campaign['id']}: {str(e)}")
        
        # Insert performance data
        for insight in data['insights']['campaign']:
            perf_data = {
                'account_id': data['account_id'],
                'platform': 'meta',
                'campaign_id': insight.get('campaign_id'),
                'date': datetime.now().strftime('%Y-%m-%d'),  # Daily aggregation
                'hour': datetime.now().hour if False else None,  # Set True for hourly
                'impressions': int(insight.get('impressions', 0) or 0),
                'clicks': int(insight.get('clicks', 0) or 0),
                'spend': float(insight.get('spend', 0) or 0),
                'conversions': float(insight.get('conversions', 0) or 0),
                'conversion_value': float(insight.get('conversion_values', [{}])[0].get('value', 0)) if isinstance(insight.get('conversion_values'), list) else 0,
                'synced_at': data['synced_at']
            }
            
            try:
                self.client.table('performance_daily').upsert(perf_data).execute()
                results['inserted'] += 1
            except Exception as e:
                results['errors'].append(f"Performance {insight.get('campaign_id')}: {str(e)}")
        
        # Update sync log
        sync_log = {
            'account_id': data['account_id'],
            'platform': 'meta',
            'last_sync_at': data['synced_at'],
            'status': 'success' if not results['errors'] else 'partial',
            'records_synced': results['inserted']
        }
        
        try:
            self.client.table('data_sync_log').upsert(sync_log).execute()
        except Exception as e:
            results['errors'].append(f"Sync log: {str(e)}")
        
        return results
    
    def insert_google_data(self, data: Dict) -> Dict:
        """Insert Google Ads data into Supabase"""
        results = {'inserted': 0, 'errors': []}
        
        # Insert campaigns
        for campaign in data['campaigns']:
            campaign_data = {
                'id': f"google_{campaign['id']}",
                'account_id': data['customer_id'],
                'platform': 'google',
                'campaign_id': str(campaign['id']),
                'campaign_name': campaign['name'],
                'status': campaign['status'],
                'start_date': campaign.get('start_date'),
                'end_date': campaign.get('end_date'),
                'synced_at': data['synced_at']
            }
            
            try:
                self.client.table('campaigns').upsert(campaign_data).execute()
                results['inserted'] += 1
            except Exception as e:
                results['errors'].append(f"Campaign {campaign['id']}: {str(e)}")
        
        # Insert search terms
        for term in data['search_terms']:
            term_data = {
                'account_id': data['customer_id'],
                'ad_group_id': str(term['ad_group_id']),
                'campaign_id': str(term['campaign_id']),
                'search_term': term['search_term'],
                'match_type': 'SEARCH',  # Search terms are actual searches
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impressions': term['impressions'],
                'clicks': term['clicks'],
                'cost': term['cost_micros'] / 1_000_000,
                'conversions': float(term['conversions'] or 0),
                'synced_at': data['synced_at']
            }
            
            try:
                self.client.table('search_terms').upsert(term_data).execute()
                results['inserted'] += 1
            except Exception as e:
                results['errors'].append(f"Search term {term['search_term'][:20]}: {str(e)}")
        
        # Insert performance data
        for campaign in data['campaigns']:
            perf_data = {
                'account_id': data['customer_id'],
                'platform': 'google',
                'campaign_id': str(campaign['id']),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impressions': campaign['impressions'],
                'clicks': campaign['clicks'],
                'spend': campaign['cost_micros'] / 1_000_000,
                'conversions': float(campaign['conversions'] or 0),
                'conversion_value': float(campaign['conversions_value'] or 0),
                'synced_at': data['synced_at']
            }
            
            try:
                self.client.table('performance_daily').upsert(perf_data).execute()
                results['inserted'] += 1
            except Exception as e:
                results['errors'].append(f"Performance {campaign['id']}: {str(e)}")
        
        # Update sync log
        sync_log = {
            'account_id': data['customer_id'],
            'platform': 'google',
            'last_sync_at': data['synced_at'],
            'status': 'success' if not results['errors'] else 'partial',
            'records_synced': results['inserted']
        }
        
        try:
            self.client.table('data_sync_log').upsert(sync_log).execute()
        except Exception as e:
            results['errors'].append(f"Sync log: {str(e)}")
        
        return results

def insert_from_file(data_file: str) -> Dict:
    """Insert data from a JSON file"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    inserter = SupabaseInserter()
    
    # Detect type
    if 'account_id' in data and 'act_' in data['account_id']:
        print(f"Inserting Meta Ads data for {data['client']}...")
        return inserter.insert_meta_data(data)
    elif 'customer_id' in data:
        print(f"Inserting Google Ads data for {data['client']}...")
        return inserter.insert_google_data(data)
    else:
        raise ValueError("Unknown data format")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 insert_to_supabase.py <data_file.json>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    results = insert_from_file(data_file)
    
    print(f"\nInsert Results:")
    print(f"  Records inserted: {results['inserted']}")
    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")
        for err in results['errors'][:5]:
            print(f"    - {err}")

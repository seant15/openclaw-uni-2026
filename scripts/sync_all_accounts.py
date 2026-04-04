#!/usr/bin/env python3
"""
Full Sync Orchestrator for LEIVIP and PROD
Runs complete data sync for all accounts
"""

import os
import sys
import json
import yaml
from datetime import datetime
from typing import Dict, List

# Import our fetchers
sys.path.insert(0, '/data/workspace/scripts')
from fetch_meta_ads import MetaAdsFetcher
from fetch_google_ads_full import GoogleAdsFetcher
from insert_to_supabase import insert_from_file

CONFIG_FILE = '/data/workspace/config/ad_accounts.yaml'

def load_config() -> Dict:
    """Load account configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def run_meta_sync(account_id: str, client_name: str) -> Dict:
    """Run Meta sync for one account"""
    print(f"\n{'='*60}")
    print(f"🔄 META SYNC: {client_name} - {account_id}")
    print(f"{'='*60}")
    
    try:
        fetcher = MetaAdsFetcher()
        results = fetcher.sync_to_supabase(account_id, client_name)
        
        # Find the output file and insert to Supabase
        import glob
        files = glob.glob(f"/tmp/meta_ads_{account_id.replace('act_', '')}_*.json")
        if files:
            latest = max(files, key=os.path.getctime)
            insert_results = insert_from_file(latest)
            results['supabase_inserted'] = insert_results['inserted']
        
        return results
    except Exception as e:
        return {'error': str(e), 'account_id': account_id, 'client': client_name}

def run_google_sync(customer_id: str, client_name: str) -> Dict:
    """Run Google sync for one account"""
    print(f"\n{'='*60}")
    print(f"🔄 GOOGLE SYNC: {client_name} - {customer_id}")
    print(f"{'='*60}")
    
    try:
        fetcher = GoogleAdsFetcher()
        results = fetcher.sync_account(customer_id, client_name)
        
        # Find the output file and insert to Supabase
        import glob
        clean_id = customer_id.replace('-', '').replace(' ', '')
        files = glob.glob(f"/tmp/google_ads_{clean_id}_*.json")
        if files:
            latest = max(files, key=os.path.getctime)
            insert_results = insert_from_file(latest)
            results['supabase_inserted'] = insert_results['inserted']
        
        return results
    except Exception as e:
        return {'error': str(e), 'customer_id': customer_id, 'client': client_name}

def run_full_sync():
    """Run complete sync for all configured accounts"""
    print("\n" + "="*60)
    print("🚀 FULL AD DATA SYNC")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    config = load_config()
    all_results = []
    
    for client_key, client_config in config['clients'].items():
        client_name = client_config['name']
        print(f"\n{'─'*60}")
        print(f"📁 CLIENT: {client_name}")
        print(f"{'─'*60}")
        
        # Sync Meta accounts
        for meta_account in client_config.get('meta_accounts', []):
            account_id = meta_account.get('account_id')
            if account_id and account_id != '':  # Skip empty placeholders
                result = run_meta_sync(account_id, client_name)
                all_results.append(result)
            else:
                print(f"⚠️  Skipping empty Meta account for {client_name}")
        
        # Sync Google accounts
        for google_account in client_config.get('google_accounts', []):
            customer_id = google_account.get('customer_id')
            if customer_id and customer_id != '':  # Skip empty placeholders
                result = run_google_sync(customer_id, client_name)
                all_results.append(result)
            else:
                print(f"⚠️  Skipping empty Google account for {client_name}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SYNC SUMMARY")
    print("="*60)
    
    total_accounts = len(all_results)
    successful = sum(1 for r in all_results if 'error' not in r)
    failed = total_accounts - successful
    
    print(f"Total accounts: {total_accounts}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    for result in all_results:
        if 'error' in result:
            print(f"  ❌ {result.get('client', 'Unknown')}: {result['error'][:50]}")
        else:
            account = result.get('account_id') or result.get('customer_id')
            print(f"  ✅ {result.get('client', 'Unknown')} - {account}")
    
    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("="*60)
    
    return all_results

if __name__ == '__main__':
    results = run_full_sync()
    
    # Save summary
    summary_file = f"/tmp/sync_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nSummary saved to: {summary_file}")

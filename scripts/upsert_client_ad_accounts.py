#!/usr/bin/env python3
"""
Supabase Client Ad Account Upsert Script
Upserts Google Ads and Meta Ads account IDs to the clients table
"""

import os
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin access

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# Google Ads Clients
google_ads_clients = [
    {"name": "Dental Artistry", "google_ads_customer_id": "632-935-4566"},
    {"name": "Lumiere Dental", "google_ads_customer_id": "714-522-2813"},
    {"name": "SESUNG", "google_ads_customer_id": "310-859-4803"},
    {"name": "Travorio", "google_ads_customer_id": "849-262-0446"},
]

# Meta Ads Clients (with optional second account)
meta_ads_clients = [
    {"name": "LEIVIP", "meta_ad_account_id": "act_281592916520074", "meta_ad_account_id_2": "act_1627505121562961"},
    {"name": "PROD", "meta_ad_account_id": "act_175918763181986", "meta_ad_account_id_2": "act_113440162763180"},
    {"name": "UB Plus", "meta_ad_account_id": "act_841938383288943", "meta_ad_account_id_2": "act_1130410831752833"},
    {"name": "Windie", "meta_ad_account_id": "act_924797519996193"},
    {"name": "StateofGratitude", "meta_ad_account_id": "act_628003337822332"},
]

def upsert_clients():
    """Upsert all client ad account data to Supabase"""
    
    print("🔄 Starting client ad account upsert...")
    print("=" * 60)
    
    # First, ensure columns exist by checking table schema
    # (Supabase doesn't support IF NOT EXISTS for columns via API, 
    #  so this script assumes columns are already added via SQL migration)
    
    # Upsert Google Ads clients
    print("\n📊 Upserting Google Ads accounts...")
    for client in google_ads_clients:
        try:
            # Check if client exists
            existing = supabase.table('clients').select('id').eq('name', client['name']).execute()
            
            if existing.data:
                # Update existing client
                result = supabase.table('clients').update({
                    'google_ads_customer_id': client['google_ads_customer_id'],
                    'updated_at': datetime.now().isoformat()
                }).eq('name', client['name']).execute()
                print(f"  ✅ Updated: {client['name']} → {client['google_ads_customer_id']}")
            else:
                # Insert new client
                result = supabase.table('clients').insert({
                    'name': client['name'],
                    'google_ads_customer_id': client['google_ads_customer_id'],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }).execute()
                print(f"  ✅ Inserted: {client['name']} → {client['google_ads_customer_id']}")
        except Exception as e:
            print(f"  ❌ Error with {client['name']}: {e}")
    
    # Upsert Meta Ads clients
    print("\n📊 Upserting Meta Ads accounts...")
    for client in meta_ads_clients:
        try:
            update_data = {
                'meta_ad_account_id': client['meta_ad_account_id'],
                'updated_at': datetime.now().isoformat()
            }
            
            # Add secondary account if it exists
            if 'meta_ad_account_id_2' in client:
                update_data['meta_ad_account_id_2'] = client['meta_ad_account_id_2']
            
            # Check if client exists
            existing = supabase.table('clients').select('id').eq('name', client['name']).execute()
            
            if existing.data:
                # Update existing client
                result = supabase.table('clients').update(update_data).eq('name', client['name']).execute()
                if 'meta_ad_account_id_2' in client:
                    print(f"  ✅ Updated: {client['name']} → {client['meta_ad_account_id']}, {client['meta_ad_account_id_2']}")
                else:
                    print(f"  ✅ Updated: {client['name']} → {client['meta_ad_account_id']}")
            else:
                # Insert new client
                insert_data = {
                    'name': client['name'],
                    'meta_ad_account_id': client['meta_ad_account_id'],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                if 'meta_ad_account_id_2' in client:
                    insert_data['meta_ad_account_id_2'] = client['meta_ad_account_id_2']
                
                result = supabase.table('clients').insert(insert_data).execute()
                if 'meta_ad_account_id_2' in client:
                    print(f"  ✅ Inserted: {client['name']} → {client['meta_ad_account_id']}, {client['meta_ad_account_id_2']}")
                else:
                    print(f"  ✅ Inserted: {client['name']} → {client['meta_ad_account_id']}")
        except Exception as e:
            print(f"  ❌ Error with {client['name']}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Client ad account upsert complete!")
    
    # Verify results
    print("\n📋 Verification - All clients with ad accounts:")
    try:
        result = supabase.table('clients').select('*').execute()
        for client in result.data:
            gads = client.get('google_ads_customer_id', '—')
            meta1 = client.get('meta_ad_account_id', '—')
            meta2 = client.get('meta_ad_account_id_2', '—')
            if gads != '—' or meta1 != '—':
                print(f"  • {client['name']}: Google={gads}, Meta1={meta1}, Meta2={meta2}")
    except Exception as e:
        print(f"  ❌ Error fetching results: {e}")

if __name__ == '__main__':
    upsert_clients()

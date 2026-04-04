#!/usr/bin/env python3
"""
Google Ads Conversion Action Inspector
Check what conversion actions are set up and if they track value
"""

import os
from google.ads.googleads.client import GoogleAdsClient

def get_client():
    config = {
        'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
        'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
        'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
        'use_proto_plus': True,
    }
    login_customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    if login_customer_id:
        config['login_customer_id'] = login_customer_id.replace('-', '')
    return GoogleAdsClient.load_from_dict(config)

def inspect_conversion_actions(customer_id):
    """List all conversion actions and their settings"""
    client = get_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.status,
            conversion_action.type,
            conversion_action.category,
            conversion_action.counting_type,
            conversion_action.value_settings.default_value,
            conversion_action.value_settings.always_use_default_value
        FROM conversion_action
        ORDER BY conversion_action.name
    """
    
    print(f"\n{'='*80}")
    print(f"CONVERSION ACTIONS FOR ACCOUNT: {customer_id}")
    print(f"{'='*80}\n")
    
    try:
        response = ga_service.search(
            customer_id=customer_id.replace('-', ''),
            query=query
        )
        
        actions_found = False
        for row in response:
            actions_found = True
            c = row.conversion_action
            
            print(f"ID: {c.id}")
            print(f"Name: {c.name}")
            print(f"Status: {c.status}")
            print(f"Type: {c.type_}")
            print(f"Category: {c.category}")
            print(f"Counting: {c.counting_type}")
            if c.value_settings:
                print(f"Default Value: {c.value_settings.default_value}")
                print(f"Always Use Default: {c.value_settings.always_use_default_value}")
            print(f"{'-'*80}")
        
        if not actions_found:
            print("No conversion actions found in this account.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 inspect_conversion_actions.py <customer_id>")
        print("Example: python3 inspect_conversion_actions.py 6218858846")
        sys.exit(1)
    
    inspect_conversion_actions(sys.argv[1])

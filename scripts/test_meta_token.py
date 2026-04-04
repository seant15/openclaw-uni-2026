#!/usr/bin/env python3
"""
Meta API Token Diagnostic
Tests the Meta access token and provides guidance
"""

import os
import requests
import sys

META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_API_VERSION = 'v18.0'
META_API_BASE = f'https://graph.facebook.com/{META_API_VERSION}'

def test_token():
    """Test if the Meta access token is valid"""
    print("="*60)
    print("META API TOKEN DIAGNOSTIC")
    print("="*60)
    
    if not META_ACCESS_TOKEN:
        print("\n❌ ERROR: META_ACCESS_TOKEN not found in environment")
        print("\nTo fix:")
        print("  1. Go to https://developers.facebook.com/tools/explorer")
        print("  2. Select your Meta app")
        print("  3. Click 'Get Token' → 'Get User Access Token'")
        print("  4. Select permissions: ads_read, ads_management")
        print("  5. Copy the token and add to .env:")
        print("     META_ACCESS_TOKEN=your_token_here")
        return False
    
    print(f"\n✓ Token found (starts with: {META_ACCESS_TOKEN[:10]}...)")
    
    # Test token validity
    url = f"{META_API_BASE}/me"
    params = {'access_token': META_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            error = data['error']
            print(f"\n❌ TOKEN INVALID")
            print(f"   Error: {error.get('message')}")
            print(f"   Code: {error.get('code')}")
            
            if error.get('code') == 190:
                print("\n🔧 TO FIX:")
                print("   The token has expired or user logged out.")
                print("   1. Go to https://developers.facebook.com/tools/explorer")
                print("   2. Select your app")
                print("   3. Get a new User Access Token")
                print("   4. Make sure to select 'ads_read' permission")
                print("   5. Update .env with the new token")
            
            return False
        
        print(f"\n✅ TOKEN VALID")
        print(f"   User: {data.get('name', 'Unknown')}")
        print(f"   ID: {data.get('id', 'Unknown')}")
        
        # Test ad account access
        print("\n📋 Testing ad account access...")
        accounts_url = f"{META_API_BASE}/me/adaccounts"
        accounts_params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'account_id,name,account_status'
        }
        
        accounts_response = requests.get(accounts_url, params=accounts_params)
        accounts_data = accounts_response.json()
        
        if 'error' in accounts_data:
            print(f"   ❌ Cannot access ad accounts: {accounts_data['error'].get('message')}")
        else:
            accounts = accounts_data.get('data', [])
            print(f"   ✓ Access to {len(accounts)} ad account(s):")
            for acc in accounts:
                status = "Active" if acc.get('account_status') == 1 else "Inactive"
                print(f"     - {acc['account_id']}: {acc['name']} ({status})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == '__main__':
    valid = test_token()
    sys.exit(0 if valid else 1)

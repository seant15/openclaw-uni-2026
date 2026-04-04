#!/usr/bin/env python3
"""
Google Ads API Token Diagnostic
Tests Google Ads API authentication
"""

import os
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def test_google_ads_auth():
    """Test Google Ads API authentication"""
    print("="*60)
    print("GOOGLE ADS API TOKEN DIAGNOSTIC")
    print("="*60)
    
    # Check required variables
    required = [
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET',
        'GOOGLE_ADS_REFRESH_TOKEN'
    ]
    
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        print(f"\n❌ Missing environment variables:")
        for v in missing:
            print(f"   - {v}")
        return False
    
    print("\n✓ All required variables present")
    
    # Build config
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
        print(f"✓ Using MCC: {login_customer_id}")
    
    # Test client initialization
    try:
        client = GoogleAdsClient.load_from_dict(config)
        print("✓ Google Ads client initialized")
        
        # Test API call - list accessible customers
        customer_service = client.get_service("CustomerService")
        
        print("\n📋 Testing API access...")
        try:
            accessible_customers = customer_service.list_accessible_customers()
            print(f"✓ API access successful")
            print(f"   Accessible customers: {len(accessible_customers.resource_names)}")
            
            for customer in accessible_customers.resource_names:
                cid = customer.replace('customers/', '')
                print(f"   - Customer ID: {cid}")
            
            return True
            
        except GoogleAdsException as e:
            print(f"\n❌ API call failed:")
            for error in e.failure.errors:
                print(f"   Error: {error.message}")
                if error.error_code.authentication_error:
                    print(f"\n🔧 TO FIX:")
                    print("   1. Check if refresh token is valid")
                    print("   2. Run: scripts/generate_google_ads_token.sh")
                    print("   3. Follow OAuth flow and update .env")
            return False
            
    except Exception as e:
        print(f"\n❌ Client initialization failed: {e}")
        return False

def test_specific_account(customer_id: str):
    """Test access to a specific customer account"""
    print(f"\n📋 Testing access to account: {customer_id}")
    
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
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        ga_service = client.get_service("GoogleAdsService")
        
        query = "SELECT customer.id, customer.descriptive_name FROM customer"
        
        response = ga_service.search(
            customer_id=customer_id.replace('-', ''),
            query=query
        )
        
        for row in response:
            print(f"✓ Access confirmed: {row.customer.descriptive_name}")
            return True
            
    except GoogleAdsException as e:
        print(f"❌ Access failed:")
        for error in e.failure.errors:
            print(f"   {error.message}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_google_ads_auth()
    
    if success and len(sys.argv) > 1:
        # Test specific account if provided
        customer_id = sys.argv[1]
        test_specific_account(customer_id)
    
    sys.exit(0 if success else 1)

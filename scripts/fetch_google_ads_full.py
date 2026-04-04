#!/usr/bin/env python3
"""
Google Ads Full Data Fetcher
Pulls campaign, ad group, ad, and keyword/search term data into Supabase
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def get_client():
    """Initialize Google Ads API client from environment variables"""
    
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
    
    config = {
        'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
        'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
        'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
        'use_proto_plus': True,
    }
    
    login_customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    if login_customer_id:
        config['login_customer_id'] = login_customer_id.replace('-', '').replace(' ', '')
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        return client
    except Exception as e:
        print(f"ERROR: Failed to initialize Google Ads client: {e}")
        sys.exit(1)

class GoogleAdsFetcher:
    def __init__(self):
        self.client = get_client()
        self.ga_service = self.client.get_service("GoogleAdsService")
    
    def fetch_campaigns(self, customer_id: str) -> list:
        """Fetch all campaigns with structure"""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions,
                metrics.all_conversions_value,
                metrics.cross_device_conversions
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            ORDER BY metrics.cost_micros DESC
        """
        
        try:
            response = self.ga_service.search(
                customer_id=customer_id.replace('-', '').replace(' ', ''), 
                query=query
            )
            
            campaigns = []
            for row in response:
                c = row.campaign
                m = row.metrics
                budget = row.campaign_budget
                
                campaigns.append({
                    'id': c.id,
                    'name': c.name,
                    'status': str(c.status).replace('CampaignStatus.', ''),
                    'channel_type': str(c.advertising_channel_type).replace('AdvertisingChannelType.', '') if c.advertising_channel_type else None,
                    'budget_micros': budget.amount_micros if budget.amount_micros else 0,
                    'impressions': m.impressions,
                    'clicks': m.clicks,
                    'cost_micros': m.cost_micros,
                    'conversions': m.conversions,
                    'conversions_value': m.conversions_value,
                    'all_conversions': m.all_conversions,
                    'all_conversions_value': m.all_conversions_value,
                    'cross_device_conversions': m.cross_device_conversions
                })
            
            return campaigns
        except GoogleAdsException as e:
            print(f"ERROR fetching campaigns: {e}")
            return []
    
    def fetch_ad_groups(self, customer_id: str) -> list:
        """Fetch all ad groups with structure"""
        query = """
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.average_cpc
            FROM ad_group
            WHERE ad_group.status != 'REMOVED'
            ORDER BY metrics.cost_micros DESC
        """
        
        try:
            response = self.ga_service.search(
                customer_id=customer_id.replace('-', '').replace(' ', ''), 
                query=query
            )
            
            ad_groups = []
            for row in response:
                ag = row.ad_group
                c = row.campaign
                m = row.metrics
                
                ad_groups.append({
                    'id': ag.id,
                    'name': ag.name,
                    'status': str(ag.status).replace('AdGroupStatus.', ''),
                    'type': str(ag.type).replace('AdGroupType.', '') if ag.type else None,
                    'campaign_id': c.id,
                    'campaign_name': c.name,
                    'impressions': m.impressions,
                    'clicks': m.clicks,
                    'cost_micros': m.cost_micros,
                    'conversions': m.conversions,
                    'avg_cpc_micros': m.average_cpc if m.average_cpc else 0
                })
            
            return ad_groups
        except GoogleAdsException as e:
            print(f"ERROR fetching ad groups: {e}")
            return []
    
    def fetch_ads(self, customer_id: str) -> list:
        """Fetch all ads with structure"""
        query = """
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.status,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.final_urls,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad
            WHERE ad_group_ad.status != 'REMOVED'
            ORDER BY metrics.cost_micros DESC
        """
        
        try:
            response = self.ga_service.search(
                customer_id=customer_id.replace('-', '').replace(' ', ''), 
                query=query
            )
            
            ads = []
            for row in response:
                ad = row.ad_group_ad.ad
                ag = row.ad_group
                c = row.campaign
                m = row.metrics
                
                # Extract headlines and descriptions if RSA
                headlines = []
                descriptions = []
                if ad.responsive_search_ad:
                    rsa = ad.responsive_search_ad
                    headlines = [h.text for h in rsa.headlines] if rsa.headlines else []
                    descriptions = [d.text for d in rsa.descriptions] if rsa.descriptions else []
                
                ads.append({
                    'id': ad.id,
                    'status': str(row.ad_group_ad.status).replace('AdGroupAdStatus.', ''),
                    'ad_group_id': ag.id,
                    'ad_group_name': ag.name,
                    'campaign_id': c.id,
                    'campaign_name': c.name,
                    'headlines': headlines,
                    'descriptions': descriptions,
                    'final_urls': list(ad.final_urls) if ad.final_urls else [],
                    'impressions': m.impressions,
                    'clicks': m.clicks,
                    'cost_micros': m.cost_micros,
                    'conversions': m.conversions
                })
            
            return ads
        except GoogleAdsException as e:
            print(f"ERROR fetching ads: {e}")
            return []
    
    def fetch_keywords(self, customer_id: str) -> list:
        """Fetch keyword/search term performance"""
        query = """
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc
            FROM keyword_view
            WHERE ad_group_criterion.status != 'REMOVED'
            ORDER BY metrics.cost_micros DESC
        """
        
        try:
            response = self.ga_service.search(
                customer_id=customer_id.replace('-', '').replace(' ', ''), 
                query=query
            )
            
            keywords = []
            for row in response:
                criterion = row.ad_group_criterion
                ag = row.ad_group
                c = row.campaign
                m = row.metrics
                
                keywords.append({
                    'criterion_id': criterion.criterion_id,
                    'keyword_text': criterion.keyword.text if criterion.keyword else None,
                    'match_type': str(criterion.keyword.match_type).replace('KeywordMatchType.', '') if criterion.keyword and criterion.keyword.match_type else None,
                    'status': str(criterion.status).replace('AdGroupCriterionStatus.', ''),
                    'ad_group_id': ag.id,
                    'ad_group_name': ag.name,
                    'campaign_id': c.id,
                    'campaign_name': c.name,
                    'impressions': m.impressions,
                    'clicks': m.clicks,
                    'cost_micros': m.cost_micros,
                    'conversions': m.conversions,
                    'ctr': m.ctr * 100 if m.ctr else 0,
                    'avg_cpc_micros': m.average_cpc if m.average_cpc else 0
                })
            
            return keywords
        except GoogleAdsException as e:
            print(f"ERROR fetching keywords: {e}")
            return []
    
    def fetch_search_terms(self, customer_id: str) -> list:
        """Fetch search term report"""
        query = """
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr
            FROM search_term_view
            WHERE metrics.clicks > 0
            ORDER BY metrics.cost_micros DESC
            LIMIT 1000
        """
        
        try:
            response = self.ga_service.search(
                customer_id=customer_id.replace('-', '').replace(' ', ''), 
                query=query
            )
            
            search_terms = []
            for row in response:
                view = row.search_term_view
                ag = row.ad_group
                c = row.campaign
                m = row.metrics
                
                search_terms.append({
                    'search_term': view.search_term,
                    'status': str(view.status).replace('SearchTermTargetingStatus.', ''),
                    'ad_group_id': ag.id,
                    'ad_group_name': ag.name,
                    'campaign_id': c.id,
                    'campaign_name': c.name,
                    'impressions': m.impressions,
                    'clicks': m.clicks,
                    'cost_micros': m.cost_micros,
                    'conversions': m.conversions,
                    'ctr': m.ctr * 100 if m.ctr else 0
                })
            
            return search_terms
        except GoogleAdsException as e:
            print(f"ERROR fetching search terms: {e}")
            return []
    
    def sync_account(self, customer_id: str, client_name: str) -> dict:
        """Full sync for a Google Ads account"""
        print(f"\n{'='*60}")
        print(f"GOOGLE ADS SYNC: {customer_id}")
        print(f"Client: {client_name}")
        print(f"{'='*60}\n")
        
        results = {
            'customer_id': customer_id,
            'client': client_name,
            'timestamp': datetime.now().isoformat(),
            'campaigns': 0,
            'ad_groups': 0,
            'ads': 0,
            'keywords': 0,
            'search_terms': 0
        }
        
        print("📊 Fetching structure & performance...")
        
        print("  - Campaigns...")
        campaigns = self.fetch_campaigns(customer_id)
        results['campaigns'] = len(campaigns)
        print(f"    ✓ {len(campaigns)} campaigns")
        
        print("  - Ad Groups...")
        ad_groups = self.fetch_ad_groups(customer_id)
        results['ad_groups'] = len(ad_groups)
        print(f"    ✓ {len(ad_groups)} ad groups")
        
        print("  - Ads...")
        ads = self.fetch_ads(customer_id)
        results['ads'] = len(ads)
        print(f"    ✓ {len(ads)} ads")
        
        print("  - Keywords...")
        keywords = self.fetch_keywords(customer_id)
        results['keywords'] = len(keywords)
        print(f"    ✓ {len(keywords)} keywords")
        
        print("  - Search Terms...")
        search_terms = self.fetch_search_terms(customer_id)
        results['search_terms'] = len(search_terms)
        print(f"    ✓ {len(search_terms)} search terms")
        
        # Compile output
        output = {
            'customer_id': customer_id,
            'client': client_name,
            'synced_at': datetime.now().isoformat(),
            'campaigns': campaigns,
            'ad_groups': ad_groups,
            'ads': ads,
            'keywords': keywords,
            'search_terms': search_terms
        }
        
        # Save to file
        output_file = f"/tmp/google_ads_{customer_id.replace('-', '').replace(' ', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n✅ Data saved to: {output_file}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 fetch_google_ads_full.py <customer_id> <client_name>")
        print("")
        print("Examples:")
        print("  python3 fetch_google_ads_full.py 1234567890 LEIVIP")
        print("  python3 fetch_google_ads_full.py 0987654321 PROD")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    client_name = sys.argv[2]
    
    fetcher = GoogleAdsFetcher()
    results = fetcher.sync_account(customer_id, client_name)
    
    print("\n" + "="*60)
    print("SYNC SUMMARY")
    print("="*60)
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == '__main__':
    main()

-- Deploy Ad Account Columns and Google Ads Tables
-- Run this in Supabase SQL Editor

-- Step 1: Add ad account columns to clients table
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS meta_ad_account_id TEXT,
ADD COLUMN IF NOT EXISTS google_ads_customer_id TEXT;

-- Add comments for documentation
COMMENT ON COLUMN clients.meta_ad_account_id IS 'Primary Meta Ads Account ID (act_xxxxxxxx) - store main account, multiple accounts tracked separately';
COMMENT ON COLUMN clients.google_ads_customer_id IS 'Google Ads Customer ID (xxx-xxx-xxxx) - only if client has Google Ads service';

-- Step 2: Create google_ads table (campaign → ad group → ad level)
CREATE TABLE IF NOT EXISTS google_ads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    customer_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    campaign_name TEXT,
    ad_group_id TEXT,
    ad_group_name TEXT,
    ad_id TEXT,
    ad_name TEXT,
    spend DECIMAL(12,2),
    impressions INTEGER,
    clicks INTEGER,
    ctr DECIMAL(8,4),
    cpc DECIMAL(8,2),
    conversions DECIMAL(10,2),
    cost_per_conversion DECIMAL(8,2),
    conversion_value DECIMAL(12,2),
    roas DECIMAL(8,2),
    search_impression_share DECIMAL(5,2),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(customer_id, campaign_id, ad_group_id, ad_id, date)
);

-- Step 3: Create google_ads_keywords table
CREATE TABLE IF NOT EXISTS google_ads_keywords (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    customer_id TEXT NOT NULL,
    campaign_id TEXT,
    ad_group_id TEXT,
    keyword_id TEXT,
    keyword TEXT,
    match_type TEXT,
    quality_score INTEGER,
    impressions INTEGER,
    clicks INTEGER,
    ctr DECIMAL(8,4),
    cpc DECIMAL(8,2),
    conversions DECIMAL(10,2),
    cost_per_conversion DECIMAL(8,2),
    conversion_value DECIMAL(12,2),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Step 4: Create google_ads_search_terms table
CREATE TABLE IF NOT EXISTS google_ads_search_terms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    customer_id TEXT NOT NULL,
    campaign_id TEXT,
    ad_group_id TEXT,
    keyword_id TEXT,
    search_term TEXT,
    match_type TEXT,
    impressions INTEGER,
    clicks INTEGER,
    ctr DECIMAL(8,4),
    cpc DECIMAL(8,2),
    conversions DECIMAL(10,2),
    cost_per_conversion DECIMAL(8,2),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE google_ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_ads_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_ads_search_terms ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access" ON google_ads FOR SELECT USING (true);
CREATE POLICY "Enable read access" ON google_ads_keywords FOR SELECT USING (true);
CREATE POLICY "Enable read access" ON google_ads_search_terms FOR SELECT USING (true);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_google_ads_client_date ON google_ads(client_id, date);
CREATE INDEX IF NOT EXISTS idx_google_ads_customer ON google_ads(customer_id);
CREATE INDEX IF NOT EXISTS idx_google_ads_keywords_client ON google_ads_keywords(client_id, date);
CREATE INDEX IF NOT EXISTS idx_google_ads_search_terms_client ON google_ads_search_terms(client_id, date);

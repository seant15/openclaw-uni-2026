-- Google Ads Schema Draft
-- MCC Account: 282-333-4378 (Manager Account)
-- Target Client Customer ID: TBD (to be filled in)

-- ============================================
-- Table 1: google_ads
-- Matches meta_ads structure + platform field
-- ============================================
CREATE TABLE google_ads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Google Ads Account Hierarchy
    customer_id TEXT NOT NULL,           -- Google Ads Customer ID (the actual account under MCC)
    campaign_id TEXT NOT NULL,
    campaign_name TEXT,
    
    ad_group_id TEXT NOT NULL,           -- Maps to Meta's adset_id
    ad_group_name TEXT,                   -- Maps to Meta's adset_name
    
    ad_id TEXT NOT NULL,
    ad_name TEXT,
    
    -- Performance Metrics
    spend DECIMAL(12,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(8,4) DEFAULT 0,          -- Click-through rate (clicks / impressions)
    cpc DECIMAL(10,4) DEFAULT 0,         -- Cost per click
    
    -- Conversion Metrics
    conversions DECIMAL(10,2) DEFAULT 0,  -- May be fractional for modeled conversions
    cost_per_conversion DECIMAL(10,4) DEFAULT 0,
    
    -- Google Ads Specific
    conversion_value DECIMAL(12,2) DEFAULT 0,  -- Revenue value from conversions
    roas DECIMAL(8,4) DEFAULT 0,         -- Return on ad spend
    
    -- Search-specific (populated if campaign is Search)
    search_impression_share DECIMAL(5,2),  -- Search impr. share (0-100%)
    search_top_impr_share DECIMAL(5,2),    -- Search top IS
    search_abs_top_impr_share DECIMAL(5,2), -- Search abs. top IS
    
    -- Metadata
    date DATE NOT NULL,
    platform TEXT DEFAULT 'google_ads',    -- For future unification
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(customer_id, campaign_id, ad_group_id, ad_id, date)
);

-- Indexes for common queries
CREATE INDEX idx_google_ads_client_id ON google_ads(client_id);
CREATE INDEX idx_google_ads_date ON google_ads(date);
CREATE INDEX idx_google_ads_customer_id ON google_ads(customer_id);
CREATE INDEX idx_google_ads_campaign_id ON google_ads(campaign_id);
CREATE INDEX idx_google_ads_date_platform ON google_ads(date, platform);

-- ============================================
-- Table 2: google_ads_keywords
-- Search keywords/terms performance
-- ============================================
CREATE TABLE google_ads_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Account Hierarchy
    customer_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    ad_group_id TEXT NOT NULL,
    
    -- Keyword Data
    criterion_id TEXT NOT NULL,          -- Google's keyword ID
    keyword TEXT NOT NULL,               -- The actual keyword text
    match_type TEXT CHECK (match_type IN ('exact', 'phrase', 'broad')),
    
    -- Status
    status TEXT CHECK (status IN ('enabled', 'paused', 'removed')),
    
    -- Performance Metrics
    spend DECIMAL(12,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(8,4) DEFAULT 0,
    cpc DECIMAL(10,4) DEFAULT 0,
    
    -- Conversion Metrics
    conversions DECIMAL(10,2) DEFAULT 0,
    conversion_value DECIMAL(12,2) DEFAULT 0,
    cost_per_conversion DECIMAL(10,4) DEFAULT 0,
    
    -- Quality Metrics (Search-specific)
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 10),
    ad_relevance_score INTEGER CHECK (ad_relevance_score BETWEEN 1 AND 10),
    landing_page_exp_score INTEGER CHECK (landing_page_exp_score BETWEEN 1 AND 10),
    expected_ctr_score INTEGER CHECK (expected_ctr_score BETWEEN 1 AND 10),
    
    -- Search Metrics
    search_impression_share DECIMAL(5,2),
    search_top_impr_share DECIMAL(5,2),
    search_abs_top_impr_share DECIMAL(5,2),
    
    -- Date & Metadata
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(customer_id, campaign_id, ad_group_id, criterion_id, date)
);

-- Indexes
CREATE INDEX idx_google_ads_keywords_client_id ON google_ads_keywords(client_id);
CREATE INDEX idx_google_ads_keywords_date ON google_ads_keywords(date);
CREATE INDEX idx_google_ads_keywords_customer_id ON google_ads_keywords(customer_id);
CREATE INDEX idx_google_ads_keywords_keyword ON google_ads_keywords(keyword);
CREATE INDEX idx_google_ads_keywords_match_type ON google_ads_keywords(match_type);

-- ============================================
-- Table 3: google_ads_search_terms
-- Raw search queries that triggered ads
-- ============================================
CREATE TABLE google_ads_search_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Account Hierarchy
    customer_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    ad_group_id TEXT NOT NULL,
    
    -- Search Term Data
    search_term TEXT NOT NULL,           -- The actual query user typed
    keyword_id TEXT,                     -- Links to google_ads_keywords.criterion_id (if matched)
    keyword TEXT,                        -- The keyword that matched
    match_type TEXT CHECK (match_type IN ('exact', 'phrase', 'broad', 'close_variant')),
    
    -- Device & Network
    device TEXT CHECK (device IN ('desktop', 'mobile', 'tablet')),
    ad_network_type TEXT CHECK (ad_network_type IN ('search', 'search_partners', 'display', 'youtube')),
    
    -- Performance Metrics
    spend DECIMAL(12,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(8,4) DEFAULT 0,
    cpc DECIMAL(10,4) DEFAULT 0,
    
    -- Conversion Metrics
    conversions DECIMAL(10,2) DEFAULT 0,
    conversion_value DECIMAL(12,2) DEFAULT 0,
    
    -- Date & Metadata
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(customer_id, campaign_id, ad_group_id, search_term, device, ad_network_type, date)
);

-- Indexes
CREATE INDEX idx_google_ads_search_terms_client_id ON google_ads_search_terms(client_id);
CREATE INDEX idx_google_ads_search_terms_date ON google_ads_search_terms(date);
CREATE INDEX idx_google_ads_search_terms_customer_id ON google_ads_search_terms(customer_id);
CREATE INDEX idx_google_ads_search_terms_search_term ON google_ads_search_terms(search_term);
CREATE INDEX idx_google_ads_search_terms_keyword_id ON google_ads_search_terms(keyword_id);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_google_ads_updated_at BEFORE UPDATE ON google_ads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_google_ads_keywords_updated_at BEFORE UPDATE ON google_ads_keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_google_ads_search_terms_updated_at BEFORE UPDATE ON google_ads_search_terms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Comments / Documentation
-- ============================================
COMMENT ON TABLE google_ads IS 'Google Ads campaign performance data at ad level';
COMMENT ON TABLE google_ads_keywords IS 'Google Ads keyword performance metrics';
COMMENT ON TABLE google_ads_search_terms IS 'Raw search query performance (what users actually typed)';

COMMENT ON COLUMN google_ads.customer_id IS 'Google Ads Customer ID (the client account under MCC 282-333-4378)';
COMMENT ON COLUMN google_ads_keywords.match_type IS 'Keyword match type: exact, phrase, or broad';
COMMENT ON COLUMN google_ads_search_terms.search_term IS 'The actual search query entered by user';
COMMENT ON COLUMN google_ads_search_terms.match_type IS 'How the keyword matched: close_variant includes close variations';

-- ============================================
-- Sample Queries (for reference)
-- ============================================

-- 1. Daily spend by campaign (Google Ads)
-- SELECT 
--     date,
--     campaign_name,
--     SUM(spend) as total_spend,
--     SUM(conversions) as total_conversions,
--     SUM(conversion_value) as total_revenue
-- FROM google_ads
-- WHERE customer_id = 'YOUR_CUSTOMER_ID_HERE'
-- GROUP BY date, campaign_name
-- ORDER BY date DESC, total_spend DESC;

-- 2. Top performing keywords
-- SELECT 
--     keyword,
--     match_type,
--     SUM(impressions) as impressions,
--     SUM(clicks) as clicks,
--     SUM(conversions) as conversions,
--     AVG(quality_score) as avg_qs
-- FROM google_ads_keywords
-- WHERE customer_id = 'YOUR_CUSTOMER_ID_HERE'
-- GROUP BY keyword, match_type
-- ORDER BY conversions DESC
-- LIMIT 50;

-- 3. Search terms not matching keywords (negative keyword opportunities)
-- SELECT 
--     search_term,
--     SUM(clicks) as clicks,
--     SUM(spend) as spend,
--     SUM(conversions) as conversions
-- FROM google_ads_search_terms
-- WHERE customer_id = 'YOUR_CUSTOMER_ID_HERE'
--   AND conversions = 0
--   AND clicks > 5
-- GROUP BY search_term
-- ORDER BY spend DESC
-- LIMIT 100;

-- 4. Cross-platform comparison (Google vs Meta)
-- SELECT 
--     date,
--     platform,
--     SUM(spend) as spend,
--     SUM(impressions) as impressions,
--     SUM(clicks) as clicks,
--     SUM(conversions) as conversions
-- FROM (
--     SELECT date, 'google_ads' as platform, spend, impressions, clicks, conversions 
--     FROM google_ads
--     WHERE customer_id = 'YOUR_CUSTOMER_ID_HERE'
--     UNION ALL
--     SELECT date, 'meta' as platform, spend, impressions, clicks, conversions
--     FROM meta_ads
--     WHERE client_id = 'YOUR_CLIENT_UUID_HERE'
-- ) combined
-- GROUP BY date, platform
-- ORDER BY date DESC;

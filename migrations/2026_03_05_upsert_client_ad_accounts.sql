-- Upsert client ad account data
-- Google Ads (4 clients) + Meta Ads (5 clients, 8 total accounts)
-- Created: 2026-03-05

-- ===================== GOOGLE ADS CLIENTS =====================

-- Dental Artistry
INSERT INTO clients (name, google_ads_customer_id, updated_at)
VALUES ('Dental Artistry', '632-935-4566', NOW())
ON CONFLICT (name) DO UPDATE SET
    google_ads_customer_id = EXCLUDED.google_ads_customer_id,
    updated_at = NOW();

-- Lumiere Dental
INSERT INTO clients (name, google_ads_customer_id, updated_at)
VALUES ('Lumiere Dental', '714-522-2813', NOW())
ON CONFLICT (name) DO UPDATE SET
    google_ads_customer_id = EXCLUDED.google_ads_customer_id,
    updated_at = NOW();

-- SESUNG
INSERT INTO clients (name, google_ads_customer_id, updated_at)
VALUES ('SESUNG', '310-859-4803', NOW())
ON CONFLICT (name) DO UPDATE SET
    google_ads_customer_id = EXCLUDED.google_ads_customer_id,
    updated_at = NOW();

-- Travorio
INSERT INTO clients (name, google_ads_customer_id, updated_at)
VALUES ('Travorio', '849-262-0446', NOW())
ON CONFLICT (name) DO UPDATE SET
    google_ads_customer_id = EXCLUDED.google_ads_customer_id,
    updated_at = NOW();

-- ===================== META ADS CLIENTS =====================

-- LEIVIP (2 accounts: Primary + TOF)
INSERT INTO clients (name, meta_ad_account_id, meta_ad_account_id_2, updated_at)
VALUES ('LEIVIP', 'act_281592916520074', 'act_1627505121562961', NOW())
ON CONFLICT (name) DO UPDATE SET
    meta_ad_account_id = EXCLUDED.meta_ad_account_id,
    meta_ad_account_id_2 = EXCLUDED.meta_ad_account_id_2,
    updated_at = NOW();

-- PROD (2 accounts: Primary + backup)
INSERT INTO clients (name, meta_ad_account_id, meta_ad_account_id_2, updated_at)
VALUES ('PROD', 'act_175918763181986', 'act_113440162763180', NOW())
ON CONFLICT (name) DO UPDATE SET
    meta_ad_account_id = EXCLUDED.meta_ad_account_id,
    meta_ad_account_id_2 = EXCLUDED.meta_ad_account_id_2,
    updated_at = NOW();

-- UB+ (2 accounts: Primary + mini)
INSERT INTO clients (name, meta_ad_account_id, meta_ad_account_id_2, updated_at)
VALUES ('UB Plus', 'act_841938383288943', 'act_1130410831752833', NOW())
ON CONFLICT (name) DO UPDATE SET
    meta_ad_account_id = EXCLUDED.meta_ad_account_id,
    meta_ad_account_id_2 = EXCLUDED.meta_ad_account_id_2,
    updated_at = NOW();

-- Windie.pro (1 account)
INSERT INTO clients (name, meta_ad_account_id, updated_at)
VALUES ('Windie', 'act_924797519996193', NOW())
ON CONFLICT (name) DO UPDATE SET
    meta_ad_account_id = EXCLUDED.meta_ad_account_id,
    updated_at = NOW();

-- StateofGratitude (1 account)
INSERT INTO clients (name, meta_ad_account_id, updated_at)
VALUES ('StateofGratitude', 'act_628003337822332', NOW())
ON CONFLICT (name) DO UPDATE SET
    meta_ad_account_id = EXCLUDED.meta_ad_account_id,
    updated_at = NOW();

-- Add ad account columns to clients table
-- Run this in Supabase SQL Editor

ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS meta_ad_account_id TEXT,
ADD COLUMN IF NOT EXISTS google_ads_customer_id TEXT;

-- Add comment for documentation
COMMENT ON COLUMN clients.meta_ad_account_id IS 'Meta Ads Account ID (act_xxxxxxxx) - only populate if client has Facebook/Meta Ads service';
COMMENT ON COLUMN clients.google_ads_customer_id IS 'Google Ads Customer ID (xxx-xxx-xxxx) - only populate if client has Google Ads service';

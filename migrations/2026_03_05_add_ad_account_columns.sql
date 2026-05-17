-- Migration: Add ad account columns to clients table
-- Created: 2026-03-05

-- Add Google Ads Customer ID column
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS google_ads_customer_id VARCHAR(20);

-- Add Meta Ad Account ID columns
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS meta_ad_account_id VARCHAR(50);

ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS meta_ad_account_id_2 VARCHAR(50);

-- Add comments for documentation
COMMENT ON COLUMN clients.google_ads_customer_id IS 'Google Ads Customer ID (e.g., 632-935-4566)';
COMMENT ON COLUMN clients.meta_ad_account_id IS 'Primary Meta/Facebook Ad Account ID (e.g., act_281592916520074)';
COMMENT ON COLUMN clients.meta_ad_account_id_2 IS 'Secondary Meta/Facebook Ad Account ID for clients with multiple accounts';

-- Simplified multi-account schema
-- Add multiple account columns to clients table

ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS meta_account_1 TEXT,
ADD COLUMN IF NOT EXISTS meta_account_2 TEXT,
ADD COLUMN IF NOT EXISTS meta_account_3 TEXT,
ADD COLUMN IF NOT EXISTS google_account_1 TEXT,
ADD COLUMN IF NOT EXISTS google_account_2 TEXT,
ADD COLUMN IF NOT EXISTS google_account_3 TEXT;

-- Populate from existing data (if columns exist)
-- LEIVIP: meta_account_1 = act_281592916520074, meta_account_2 = act_1627505121562961
-- PROD: meta_account_1 = act_175918763181986, meta_account_2 = act_113440162763180
-- UB+: meta_account_1 = act_841938383288943, meta_account_2 = act_1130410831752833
-- Windie: meta_account_1 = act_924797519996193
-- State of Gratitude: meta_account_1 = act_628003337822332

-- Dental Artistry: google_account_1 = 632-935-4566
-- Lumiere Dental: google_account_1 = 714-522-2813
-- SESUNG: google_account_1 = 310-859-4803
-- Travorio: google_account_1 = 849-262-0446

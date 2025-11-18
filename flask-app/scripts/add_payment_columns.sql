-- Migration script to add payment gateway columns to comercio table
-- Run this with: mysql -u root Ecommerce_Ec < scripts/add_payment_columns.sql

USE Ecommerce_Ec;

-- Paymentez columns
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS modoPaymentez VARCHAR(20) DEFAULT 'test';
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS appCodePaymentez TEXT;
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS appKeyPaymentez TEXT;

-- Datafast columns
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS modoDatafast VARCHAR(20) DEFAULT 'test';
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS midDatafast VARCHAR(100);
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS tidDatafast VARCHAR(100);

-- De Una columns
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS modoDeUna VARCHAR(20) DEFAULT 'test';
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS apiKeyDeUna TEXT;

-- Bank accounts (JSON)
ALTER TABLE comercio ADD COLUMN IF NOT EXISTS cuentasBancarias TEXT;

SELECT 'Migration completed successfully!' AS status;

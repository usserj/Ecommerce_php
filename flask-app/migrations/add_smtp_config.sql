-- Add SMTP configuration columns to comercio table
-- Migration to add email configuration fields

ALTER TABLE comercio
ADD COLUMN IF NOT EXISTS mailServer VARCHAR(100) DEFAULT 'smtp.gmail.com',
ADD COLUMN IF NOT EXISTS mailPort INT DEFAULT 587,
ADD COLUMN IF NOT EXISTS mailUseTLS BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS mailUsername VARCHAR(255),
ADD COLUMN IF NOT EXISTS mailPassword TEXT,
ADD COLUMN IF NOT EXISTS mailDefaultSender VARCHAR(255);

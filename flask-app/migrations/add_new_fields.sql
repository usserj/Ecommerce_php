-- Migration: Add new fields to User and Comentario models
-- Date: 2025-01-19
-- Description: Add password reset tokens and comment moderation fields

USE Ecommerce_Ec;

-- Add reset token fields to usuarios table
ALTER TABLE usuarios
ADD COLUMN reset_token VARCHAR(255) NULL AFTER emailEncriptado,
ADD COLUMN reset_token_expiry DATETIME NULL AFTER reset_token;

-- Add moderation fields to comentarios table
ALTER TABLE comentarios
ADD COLUMN estado VARCHAR(20) DEFAULT 'aprobado' NOT NULL AFTER comentario,
ADD COLUMN respuesta_admin TEXT NULL AFTER estado,
ADD COLUMN fecha_moderacion DATETIME NULL AFTER respuesta_admin;

-- Add index on estado for faster filtering
ALTER TABLE comentarios ADD INDEX idx_estado (estado);

-- Update existing comments to have 'aprobado' state
UPDATE comentarios SET estado = 'aprobado' WHERE estado IS NULL OR estado = '';

SELECT 'Migration completed successfully!' as status;

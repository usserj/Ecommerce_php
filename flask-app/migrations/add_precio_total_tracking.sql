-- Migration: Add precio_total and ensure estado/tracking columns exist
-- Date: 2025-11-23
-- Description: Add missing columns to compras table for order tracking
-- Run this with: mysql -u root -p ecommerce_db < migrations/add_precio_total_tracking.sql

USE ecommerce_db;

-- 1. Add precio_total column (ignore error if exists)
ALTER TABLE compras ADD COLUMN precio_total DECIMAL(10,2) DEFAULT NULL COMMENT 'Total price including shipping';

-- 2. Add estado column (ignore error if exists)
ALTER TABLE compras ADD COLUMN estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Order status';

-- 3. Add tracking column (ignore error if exists)
ALTER TABLE compras ADD COLUMN tracking VARCHAR(100) DEFAULT NULL COMMENT 'Tracking number';

-- 4. Add fecha_estado column (ignore error if exists)
ALTER TABLE compras ADD COLUMN fecha_estado DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Last status update';

-- 5. Add index on estado for performance (ignore error if exists)
ALTER TABLE compras ADD INDEX idx_estado (estado);

-- 6. Populate precio_total for existing records
UPDATE compras
SET precio_total = CAST(pago AS DECIMAL(10,2)) + COALESCE(envio, 0)
WHERE precio_total IS NULL AND pago IS NOT NULL;

-- 7. Set default estado for old records
UPDATE compras
SET estado = 'entregado'
WHERE estado IS NULL OR estado = '';

-- Verification
SELECT 'Migration completed successfully' AS status;
SELECT COUNT(*) AS total_orders,
       COUNT(precio_total) AS with_precio_total,
       COUNT(tracking) AS with_tracking
FROM compras;

-- Migration: Agregar estados de orden y auditoría de stock
-- Date: 2025-11-23
-- Description: Fix crítico - Agregar columnas de estado y sistema de auditoría
-- Ejecutar con: mysql -u root -p ecommerce_db < migrations/002_orden_estados_stock_audit.sql

-- USE ecommerce_db; -- Database selection handled by connection

-- ============================================================================
-- PARTE 1: AGREGAR COLUMNAS A TABLA COMPRAS
-- ============================================================================

-- 1. Agregar columna precio_total
ALTER TABLE compras
ADD COLUMN precio_total DECIMAL(10,2) DEFAULT NULL
COMMENT 'Precio total incluyendo envío';

-- 2. Agregar columna estado
ALTER TABLE compras
ADD COLUMN estado VARCHAR(20) DEFAULT 'pendiente'
COMMENT 'Estado de la orden: pendiente, procesando, enviado, entregado, cancelado';

-- 3. Agregar columna tracking
ALTER TABLE compras
ADD COLUMN tracking VARCHAR(100) DEFAULT NULL
COMMENT 'Código de seguimiento del envío';

-- 4. Agregar columna fecha_estado
ALTER TABLE compras
ADD COLUMN fecha_estado DATETIME DEFAULT CURRENT_TIMESTAMP
COMMENT 'Fecha de última actualización de estado';

-- 5. Agregar índices para performance
ALTER TABLE compras
ADD INDEX idx_estado (estado),
ADD INDEX idx_fecha_estado (fecha_estado);

-- ============================================================================
-- PARTE 2: ACTUALIZAR ÓRDENES EXISTENTES
-- ============================================================================

-- Actualizar precio_total para órdenes existentes
UPDATE compras
SET precio_total = CAST(pago AS DECIMAL(10,2)) + COALESCE(envio, 0)
WHERE precio_total IS NULL AND pago IS NOT NULL;

-- Marcar todas las órdenes antiguas como 'entregado' (asumimos ya fueron procesadas)
UPDATE compras
SET estado = 'entregado',
    fecha_estado = fecha
WHERE estado IS NULL OR estado = '' OR estado = 'pendiente';

-- ============================================================================
-- PARTE 3: CREAR TABLA DE AUDITORÍA DE STOCK
-- ============================================================================

CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    orden_id INT DEFAULT NULL,
    tipo VARCHAR(20) NOT NULL COMMENT 'venta, cancelacion, ajuste, devolucion',
    cantidad INT NOT NULL COMMENT 'Cantidad del movimiento (positivo o negativo)',
    stock_anterior INT NOT NULL COMMENT 'Stock antes del movimiento',
    stock_nuevo INT NOT NULL COMMENT 'Stock después del movimiento',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT DEFAULT NULL COMMENT 'Usuario que realizó el movimiento',
    razon TEXT COMMENT 'Razón del movimiento',

    INDEX idx_producto (producto_id),
    INDEX idx_orden (orden_id),
    INDEX idx_tipo (tipo),
    INDEX idx_fecha (fecha),

    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (orden_id) REFERENCES compras(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Auditoría de movimientos de stock';

-- ============================================================================
-- PARTE 4: CREAR TABLA DE RESERVAS DE STOCK (OPCIONAL)
-- ============================================================================

CREATE TABLE IF NOT EXISTS stock_reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    usuario_id INT DEFAULT NULL,
    cantidad INT NOT NULL,
    fecha_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'activa' COMMENT 'activa, confirmada, expirada, cancelada',
    session_id VARCHAR(255) DEFAULT NULL COMMENT 'ID de sesión para reservas anónimas',

    INDEX idx_producto (producto_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_expiracion (fecha_expiracion, estado),
    INDEX idx_session (session_id),

    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Reservas temporales de stock durante checkout';

-- ============================================================================
-- PARTE 5: VERIFICACIÓN
-- ============================================================================

-- Verificar que las columnas se crearon correctamente
SELECT
    'Verificación de migración' AS status,
    COUNT(*) AS total_compras,
    COUNT(precio_total) AS con_precio_total,
    COUNT(estado) AS con_estado,
    COUNT(tracking) AS con_tracking,
    COUNT(fecha_estado) AS con_fecha_estado
FROM compras;

-- Mostrar distribución de estados
SELECT
    estado,
    COUNT(*) AS cantidad
FROM compras
GROUP BY estado
ORDER BY cantidad DESC;

-- Verificar tablas creadas
-- SELECT
--     TABLE_NAME,
--     TABLE_ROWS
-- FROM information_schema.TABLES
-- WHERE TABLE_SCHEMA = DATABASE()
--     AND TABLE_NAME IN ('stock_movements', 'stock_reservations');

SELECT '✅ Migración completada exitosamente' AS resultado;

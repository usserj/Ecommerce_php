-- Migration: Crear tablas faltantes (stock_movements y addresses)
-- Date: 2025-11-23
-- Description: Crear tablas que existen en modelos pero no en BD
-- Ejecutar con: py run_migration.py o importar manualmente

-- ============================================================================
-- PARTE 1: CREAR TABLA STOCK_MOVEMENTS
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
-- PARTE 2: CREAR TABLA ADDRESSES
-- ============================================================================

CREATE TABLE IF NOT EXISTS addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la dirección (ej: Casa, Oficina)',
    nombre_completo VARCHAR(200) NOT NULL COMMENT 'Nombre completo del destinatario',
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(20),
    pais VARCHAR(100) DEFAULT 'Ecuador',
    telefono VARCHAR(20),
    is_default TINYINT(1) DEFAULT 0 COMMENT 'Dirección por defecto',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user (user_id),
    INDEX idx_default (is_default),

    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Direcciones guardadas de usuarios';

-- ============================================================================
-- PARTE 3: CREAR TABLA STOCK_RESERVATIONS (Opcional pero recomendada)
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
-- VERIFICACIÓN
-- ============================================================================

-- Verificar que las tablas se crearon
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('stock_movements', 'addresses', 'stock_reservations')
ORDER BY TABLE_NAME;

SELECT '✅ Tablas creadas exitosamente' AS resultado;

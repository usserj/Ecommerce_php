-- =====================================================
-- MIGRACIÓN 003: Foreign Keys, Constraints e Índices
-- =====================================================
-- Fecha: 2025-11-23
-- Propósito: Agregar foreign keys faltantes, constraints y optimizar índices
-- IMPORTANTE: Ejecutar DESPUÉS de migración 002

USE ecommerce_db;

-- =====================================================
-- 1. AGREGAR FOREIGN KEYS EN TABLA `compras`
-- =====================================================

-- Verificar si ya existen las FKs antes de agregarlas
SET @exist_fk_user := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'compras'
    AND CONSTRAINT_NAME = 'fk_compras_usuario'
);

SET @exist_fk_product := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'compras'
    AND CONSTRAINT_NAME = 'fk_compras_producto'
);

-- Agregar FK usuario si no existe
SET @sql_fk_user = IF(@exist_fk_user = 0,
    'ALTER TABLE compras ADD CONSTRAINT fk_compras_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE',
    'SELECT "FK fk_compras_usuario ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar FK producto si no existe
SET @sql_fk_product = IF(@exist_fk_product = 0,
    'ALTER TABLE compras ADD CONSTRAINT fk_compras_producto FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE RESTRICT',
    'SELECT "FK fk_compras_producto ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_product;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 2. AGREGAR ÍNDICES DE PERFORMANCE EN `compras`
-- =====================================================

-- Índice para id_usuario (si no existe)
SET @exist_idx_usuario := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'compras'
    AND INDEX_NAME = 'idx_compras_usuario'
);

SET @sql_idx_usuario = IF(@exist_idx_usuario = 0,
    'ALTER TABLE compras ADD INDEX idx_compras_usuario (id_usuario)',
    'SELECT "Índice idx_compras_usuario ya existe" AS info'
);
PREPARE stmt FROM @sql_idx_usuario;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Índice para id_producto (si no existe)
SET @exist_idx_producto := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'compras'
    AND INDEX_NAME = 'idx_compras_producto'
);

SET @sql_idx_producto = IF(@exist_idx_producto = 0,
    'ALTER TABLE compras ADD INDEX idx_compras_producto (id_producto)',
    'SELECT "Índice idx_compras_producto ya existe" AS info'
);
PREPARE stmt FROM @sql_idx_producto;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Índice compuesto para consultas por usuario y estado
SET @exist_idx_user_estado := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'compras'
    AND INDEX_NAME = 'idx_compras_usuario_estado'
);

SET @sql_idx_user_estado = IF(@exist_idx_user_estado = 0,
    'ALTER TABLE compras ADD INDEX idx_compras_usuario_estado (id_usuario, estado)',
    'SELECT "Índice idx_compras_usuario_estado ya existe" AS info'
);
PREPARE stmt FROM @sql_idx_user_estado;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 3. FOREIGN KEYS EN OTRAS TABLAS
-- =====================================================

-- comentarios -> usuarios
SET @exist_fk_com_user := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'comentarios'
    AND CONSTRAINT_NAME = 'fk_comentarios_usuario'
);

SET @sql_fk_com_user = IF(@exist_fk_com_user = 0,
    'ALTER TABLE comentarios ADD CONSTRAINT fk_comentarios_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE',
    'SELECT "FK fk_comentarios_usuario ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_com_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- comentarios -> productos
SET @exist_fk_com_prod := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'comentarios'
    AND CONSTRAINT_NAME = 'fk_comentarios_producto'
);

SET @sql_fk_com_prod = IF(@exist_fk_com_prod = 0,
    'ALTER TABLE comentarios ADD CONSTRAINT fk_comentarios_producto FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE CASCADE',
    'SELECT "FK fk_comentarios_producto ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_com_prod;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- deseos -> usuarios
SET @exist_fk_wish_user := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'deseos'
    AND CONSTRAINT_NAME = 'fk_deseos_usuario'
);

SET @sql_fk_wish_user = IF(@exist_fk_wish_user = 0,
    'ALTER TABLE deseos ADD CONSTRAINT fk_deseos_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE',
    'SELECT "FK fk_deseos_usuario ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_wish_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- deseos -> productos
SET @exist_fk_wish_prod := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'deseos'
    AND CONSTRAINT_NAME = 'fk_deseos_producto'
);

SET @sql_fk_wish_prod = IF(@exist_fk_wish_prod = 0,
    'ALTER TABLE deseos ADD CONSTRAINT fk_deseos_producto FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE CASCADE',
    'SELECT "FK fk_deseos_producto ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_wish_prod;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- productos -> categorias
SET @exist_fk_prod_cat := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'productos'
    AND CONSTRAINT_NAME = 'fk_productos_categoria'
);

SET @sql_fk_prod_cat = IF(@exist_fk_prod_cat = 0,
    'ALTER TABLE productos ADD CONSTRAINT fk_productos_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id) ON DELETE RESTRICT',
    'SELECT "FK fk_productos_categoria ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_prod_cat;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- subcategorias -> categorias
SET @exist_fk_subcat_cat := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'subcategorias'
    AND CONSTRAINT_NAME = 'fk_subcategorias_categoria'
);

SET @sql_fk_subcat_cat = IF(@exist_fk_subcat_cat = 0,
    'ALTER TABLE subcategorias ADD CONSTRAINT fk_subcategorias_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id) ON DELETE CASCADE',
    'SELECT "FK fk_subcategorias_categoria ya existe" AS info'
);
PREPARE stmt FROM @sql_fk_subcat_cat;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 4. CONSTRAINTS ADICIONALES
-- =====================================================

-- Asegurar que stock no sea negativo en productos
ALTER TABLE productos
MODIFY COLUMN stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0);

-- Asegurar que precio no sea negativo
ALTER TABLE productos
MODIFY COLUMN precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0);

-- Asegurar que calificación esté entre 0 y 5
ALTER TABLE comentarios
MODIFY COLUMN calificacion DECIMAL(2,1) CHECK (calificacion >= 0 AND calificacion <= 5);

-- Asegurar que estado de orden sea válido
ALTER TABLE compras
MODIFY COLUMN estado VARCHAR(20) DEFAULT 'pendiente'
CHECK (estado IN ('pendiente', 'procesando', 'enviado', 'entregado', 'cancelado'));

-- =====================================================
-- 5. ÍNDICES ADICIONALES PARA PERFORMANCE
-- =====================================================

-- Índice para búsqueda de productos por título
ALTER TABLE productos ADD FULLTEXT INDEX idx_productos_search (titulo, descripcion);

-- Índice para productos activos
CREATE INDEX IF NOT EXISTS idx_productos_estado ON productos(estado);

-- Índice para productos en oferta
CREATE INDEX IF NOT EXISTS idx_productos_oferta ON productos(oferta);

-- Índice para categorías activas
CREATE INDEX IF NOT EXISTS idx_categorias_estado ON categorias(estado);

-- Índice para usuarios por email (búsqueda rápida en login)
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email(191));

-- Índice para comentarios por producto (mostrar reviews)
CREATE INDEX IF NOT EXISTS idx_comentarios_producto ON comentarios(id_producto);

-- Índice para wishlist por usuario
CREATE INDEX IF NOT EXISTS idx_deseos_usuario ON deseos(id_usuario);

-- =====================================================
-- 6. VALIDACIÓN FINAL
-- =====================================================

-- Mostrar todas las foreign keys creadas
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE CONSTRAINT_SCHEMA = DATABASE()
AND TABLE_NAME IN ('compras', 'comentarios', 'deseos', 'productos', 'subcategorias')
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Mostrar todos los índices creados
SELECT
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME IN ('compras', 'productos', 'comentarios', 'categorias', 'usuarios', 'deseos')
GROUP BY TABLE_NAME, INDEX_NAME;

-- =====================================================
-- NOTES:
-- =====================================================
-- 1. Esta migración es IDEMPOTENTE - puede ejecutarse múltiples veces
-- 2. Usa verificaciones para evitar duplicar FKs/índices
-- 3. ON DELETE CASCADE: elimina registros dependientes
-- 4. ON DELETE RESTRICT: previene eliminación si hay dependencias
-- 5. CHECK constraints requieren MariaDB 10.2.1+ o MySQL 8.0.16+
-- =====================================================

SELECT '✅ Migración 003 completada exitosamente' AS status;

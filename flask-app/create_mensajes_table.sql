-- Script para crear la tabla mensajes
-- Este script se debe ejecutar en la base de datos ecommerce_ec

USE ecommerce_ec;

-- Crear tabla mensajes si no existe
CREATE TABLE IF NOT EXISTS mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remitente_tipo VARCHAR(20) NOT NULL COMMENT 'Tipo de remitente: admin o user',
    remitente_id INT NOT NULL COMMENT 'ID del remitente',
    destinatario_tipo VARCHAR(20) NOT NULL COMMENT 'Tipo de destinatario: admin o user',
    destinatario_id INT NOT NULL COMMENT 'ID del destinatario',
    asunto VARCHAR(255) NOT NULL COMMENT 'Asunto del mensaje',
    contenido TEXT NOT NULL COMMENT 'Contenido del mensaje',
    leido BOOLEAN DEFAULT FALSE COMMENT 'Si el mensaje ha sido leído',
    fecha_leido DATETIME NULL COMMENT 'Fecha en que se leyó el mensaje',
    mensaje_padre_id INT NULL COMMENT 'ID del mensaje padre para threading',
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',

    -- Foreign key para threading de mensajes
    FOREIGN KEY (mensaje_padre_id) REFERENCES mensajes(id) ON DELETE CASCADE,

    -- Índices para mejorar rendimiento
    INDEX idx_remitente (remitente_tipo, remitente_id),
    INDEX idx_destinatario (destinatario_tipo, destinatario_id),
    INDEX idx_leido (leido),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Sistema de mensajería interna admin-usuario';

-- Verificar que la tabla se creó correctamente
SELECT 'Tabla mensajes creada exitosamente' AS mensaje;
SHOW COLUMNS FROM mensajes;

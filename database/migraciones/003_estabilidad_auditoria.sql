-- Estabilidad operativa: claves de catálogo, auditoría, snapshots y sesiones.
-- Requiere haber aplicado 002_ventas_variantes_cancelacion.sql.

CREATE TABLE IF NOT EXISTS tschema_migrations (
    version INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    aplicado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Clave estable para que el frontend no dependa de IDs concretos.
SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmetodospago'
          AND COLUMN_NAME = 'codigo'
    ),
    'SELECT 1',
    'ALTER TABLE tmetodospago ADD COLUMN codigo VARCHAR(32) NULL AFTER Id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

UPDATE tmetodospago
SET codigo = CASE Id
        WHEN 1 THEN 'EFECTIVO'
        WHEN 2 THEN 'TARJETA'
        WHEN 3 THEN 'TRANSFERENCIA'
        ELSE CONCAT('METODO_', Id)
    END,
    tipo_de_pago = CASE Id
        WHEN 1 THEN 'Efectivo'
        WHEN 2 THEN 'Tarjeta'
        WHEN 3 THEN 'Transferencia Bancaria'
        ELSE tipo_de_pago
    END;

ALTER TABLE tmetodospago MODIFY COLUMN codigo VARCHAR(32) NOT NULL;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmetodospago'
          AND INDEX_NAME = 'uq_metodospago_codigo'
    ),
    'SELECT 1',
    'ALTER TABLE tmetodospago ADD UNIQUE INDEX uq_metodospago_codigo (codigo)'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

-- Instantáneas históricas del producto vendido.
SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND COLUMN_NAME = 'producto_nombre_snapshot'
    ),
    'SELECT 1',
    'ALTER TABLE tdetalleventas ADD COLUMN producto_nombre_snapshot VARCHAR(255) NULL AFTER variante_id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND COLUMN_NAME = 'tamano_snapshot'
    ),
    'SELECT 1',
    'ALTER TABLE tdetalleventas ADD COLUMN tamano_snapshot VARCHAR(100) NULL AFTER producto_nombre_snapshot'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

UPDATE tdetalleventas d
LEFT JOIN tproductos p ON p.Id = d.producto_id
LEFT JOIN tproductos_variantes pv ON pv.Id = d.variante_id
LEFT JOIN ttamanos t ON t.Id = pv.tamano_id
SET d.producto_nombre_snapshot = COALESCE(d.producto_nombre_snapshot, p.nombre_producto, 'Producto no disponible'),
    d.tamano_snapshot = COALESCE(d.tamano_snapshot, t.tamano, 'No aplica')
WHERE d.producto_nombre_snapshot IS NULL OR d.tamano_snapshot IS NULL;

-- Auditoría de cancelaciones.
SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tventas'
          AND COLUMN_NAME = 'cancelado_por_id'
    ),
    'SELECT 1',
    'ALTER TABLE tventas ADD COLUMN cancelado_por_id INT NULL AFTER cambio'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tventas'
          AND COLUMN_NAME = 'cancelado_en'
    ),
    'SELECT 1',
    'ALTER TABLE tventas ADD COLUMN cancelado_en DATETIME NULL AFTER cancelado_por_id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tventas'
          AND COLUMN_NAME = 'motivo_cancelacion'
    ),
    'SELECT 1',
    'ALTER TABLE tventas ADD COLUMN motivo_cancelacion VARCHAR(255) NULL AFTER cancelado_en'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tventas'
          AND INDEX_NAME = 'idx_ventas_cancelado_por'
    ),
    'SELECT 1',
    'ALTER TABLE tventas ADD INDEX idx_ventas_cancelado_por (cancelado_por_id)'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tventas'
          AND CONSTRAINT_NAME = 'fk_ventas_cancelado_por'
    ),
    'SELECT 1',
    'ALTER TABLE tventas ADD CONSTRAINT fk_ventas_cancelado_por FOREIGN KEY (cancelado_por_id) REFERENCES tusuarios (Id) ON DELETE SET NULL'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

-- Movimientos de inventario trazables y con ID seguro.
SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND COLUMN_NAME = 'Id'
          AND EXTRA LIKE '%auto_increment%'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario MODIFY COLUMN Id INT NOT NULL AUTO_INCREMENT'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND COLUMN_NAME = 'venta_id'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD COLUMN venta_id INT NULL AFTER producto_id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND COLUMN_NAME = 'usuario_id'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD COLUMN usuario_id INT NULL AFTER venta_id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND INDEX_NAME = 'idx_movimientos_venta'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD INDEX idx_movimientos_venta (venta_id)'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND INDEX_NAME = 'idx_movimientos_usuario'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD INDEX idx_movimientos_usuario (usuario_id)'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND CONSTRAINT_NAME = 'fk_movimientos_venta'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD CONSTRAINT fk_movimientos_venta FOREIGN KEY (venta_id) REFERENCES tventas (Id) ON DELETE SET NULL'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tmovimientosinventario'
          AND CONSTRAINT_NAME = 'fk_movimientos_usuario'
    ),
    'SELECT 1',
    'ALTER TABLE tmovimientosinventario ADD CONSTRAINT fk_movimientos_usuario FOREIGN KEY (usuario_id) REFERENCES tusuarios (Id) ON DELETE SET NULL'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

-- Versión de sesión para invalidar cookies tras cambios de contraseña o baja.
SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tusuarios'
          AND COLUMN_NAME = 'sesion_version'
    ),
    'SELECT 1',
    'ALTER TABLE tusuarios ADD COLUMN sesion_version INT NOT NULL DEFAULT 1 AFTER activo'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

UPDATE ttiposdevolucion
SET tipo_cancelacion = 'Devolución por tarjeta'
WHERE tipo_cancelacion = 'Devolución por PayPal';

ALTER TABLE tcortescaja
    MODIFY COLUMN fondo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    MODIFY COLUMN ganancia_o_perdida DECIMAL(10,2) NOT NULL DEFAULT 0.00;

INSERT INTO tschema_migrations (version, nombre)
VALUES (3, 'estabilidad_auditoria')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

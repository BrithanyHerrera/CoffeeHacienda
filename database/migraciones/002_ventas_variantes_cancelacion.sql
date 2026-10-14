-- Integridad de ventas y alineación del catálogo de pagos.
-- Ejecutar primero en local y después en Aiven, con respaldo previo.

CREATE TABLE IF NOT EXISTS tschema_migrations (
    version INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    aplicado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

UPDATE tmetodospago
SET tipo_de_pago = CASE Id
    WHEN 1 THEN 'Efectivo'
    WHEN 2 THEN 'Tarjeta'
    WHEN 3 THEN 'Transferencia Bancaria'
END
WHERE Id IN (1, 2, 3);

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND COLUMN_NAME = 'variante_id'
    ),
    'SELECT 1',
    'ALTER TABLE tdetalleventas ADD COLUMN variante_id INT NULL AFTER producto_id'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND INDEX_NAME = 'idx_detalleventas_variante_id'
    ),
    'SELECT 1',
    'ALTER TABLE tdetalleventas ADD INDEX idx_detalleventas_variante_id (variante_id)'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tdetalleventas'
          AND CONSTRAINT_NAME = 'fk_detalleventas_variante'
    ),
    'SELECT 1',
    'ALTER TABLE tdetalleventas ADD CONSTRAINT fk_detalleventas_variante FOREIGN KEY (variante_id) REFERENCES tproductos_variantes (Id) ON DELETE SET NULL'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

SET @sql_migracion = IF(
    EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tcortescaja'
          AND COLUMN_NAME = 'total_paypal'
    )
    AND NOT EXISTS(
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'tcortescaja'
          AND COLUMN_NAME = 'total_tarjeta'
    ),
    'ALTER TABLE tcortescaja CHANGE COLUMN total_paypal total_tarjeta DECIMAL(10,2) NOT NULL',
    'SELECT 1'
);
PREPARE stmt_migracion FROM @sql_migracion;
EXECUTE stmt_migracion;
DEALLOCATE PREPARE stmt_migracion;

INSERT INTO tschema_migrations (version, nombre)
VALUES (2, 'ventas_variantes_cancelacion')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- Registro unificado de operaciones importantes, sin datos sensibles.
-- Aplicar después de 003_estabilidad_auditoria.sql.

CREATE TABLE IF NOT EXISTS tauditoria (
    Id BIGINT NOT NULL AUTO_INCREMENT,
    usuario_id INT NULL,
    accion VARCHAR(80) NOT NULL,
    entidad VARCHAR(80) NOT NULL,
    entidad_id BIGINT NULL,
    detalles TEXT NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Id),
    KEY idx_auditoria_usuario (usuario_id),
    KEY idx_auditoria_entidad (entidad, entidad_id),
    KEY idx_auditoria_creado (creado_en),
    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (usuario_id) REFERENCES tusuarios (Id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tschema_migrations (
    version INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    aplicado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO tschema_migrations (version, nombre)
VALUES (4, 'auditoria_operaciones')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

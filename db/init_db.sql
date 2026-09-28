CREATE DATABASE IF NOT EXISTS club_deportivo;
USE club_deportivo;

-- Deportes
CREATE TABLE IF NOT EXISTS deportes (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT uq_deportes_nombre UNIQUE (nombre)
) ENGINE = InnoDB;


-- Canchas
CREATE TABLE IF NOT EXISTS canchas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    id_deporte  INT          NOT NULL,
    precio_hora INT          NOT NULL,
    techada     BOOLEAN      NOT NULL DEFAULT FALSE,
    activa      BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_canchas_deporte
        FOREIGN KEY (id_deporte) REFERENCES deportes (id),
    CONSTRAINT ck_canchas_precio_hora CHECK (precio_hora > 0),
    CONSTRAINT ck_canchas_nombre      CHECK (TRIM(nombre) <> '')
) ENGINE = InnoDB;

-- Socios
CREATE TABLE IF NOT EXISTS socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    email VARCHAR(80) NOT NULL UNIQUE
) ENGINE = InnoDB;

-- Reservas
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada',
    precio_hora INT NOT NULL,
    precio_total INT NOT NULL,
    CONSTRAINT fk_reservas_socios
        FOREIGN KEY (id_socio) REFERENCES socios(id),
    CONSTRAINT fk_reservas_canchas
        FOREIGN KEY (id_cancha) REFERENCES canchas(id),
    CONSTRAINT ck_hora_inicio_fin
        CHECK ( fecha_hora_fin > fecha_hora_inicio ),
    CONSTRAINT ck_reservas_estado
        CHECK (estado IN ('confirmada', 'cancelada', 'finalizada')),
    CONSTRAINT ck_reservas_precio_hora
        CHECK (precio_hora > 0),
    CONSTRAINT ck_reservas_precio_total
        CHECK (precio_total > 0)
) ENGINE = InnoDB;

-- Datos
INSERT INTO deportes (id, nombre) VALUES
    (1, 'Futbol'),
    (2, 'Tenis'),
    (3, 'Padel');

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
    ('Cancha 1 - Futbol 5',  1, 1000000, FALSE, TRUE),
    ('Cancha 2 - Futbol 11', 1, 1800000, FALSE, TRUE),
    ('Cancha 3 - Tenis',     2,  600000, FALSE, TRUE),
    ('Cancha 4 - Tenis',     2,  750000, TRUE,  TRUE),
    ('Cancha 5 - Padel',     3,  800000, TRUE,  TRUE),
    ('Cancha 6 - Padel',     3,  800000, TRUE,  FALSE);

INSERT INTO socios (id, nombre, email, activo) VALUES
    (1,'Federico', 'fede@gmai.com', TRUE),
    (2, 'Nicolas', 'nico@gmail.com', FALSE),
    (3, 'Santiago', 'santi@gmail.com', TRUE);

INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) VALUES
    (1,
     1,
     '2026-10-15 18:00:00.000000',
     '2026-10-15 20:00:00.000000',
     'confirmada',
     1000000,
     2000000),
    (  3,
     3,
     '2026-10-16 19:00:00.000000',
     '2026-10-16 20:00:00.000000',
     'cancelada',
     600000,
     600000
    );
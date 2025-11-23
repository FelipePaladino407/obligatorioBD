-- Crear database:

CREATE DATABASE IF NOT EXISTS reservas_salas_estudio
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE reservas_salas_estudio;

-- Crear tablas: 

CREATE TABLE facultad (
  id_facultad       INT AUTO_INCREMENT PRIMARY KEY,
  nombre            VARCHAR(100) NOT NULL,
  UNIQUE KEY uq_facultad_nombre (nombre)
);

CREATE TABLE edificio (
  nombre_edificio   VARCHAR(80) PRIMARY KEY,
  direccion         VARCHAR(200) NOT NULL,
  departamento      VARCHAR(80)  NOT NULL
);

CREATE TABLE programa_academico (
  nombre_programa   VARCHAR(120) PRIMARY KEY,
  id_facultad       INT NOT NULL,
  tipo              ENUM('grado','posgrado') NOT NULL,
  CONSTRAINT fk_prog_facultad
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE participante (
  ci                VARCHAR(8) PRIMARY KEY,
  nombre            VARCHAR(80)  NOT NULL,
  apellido          VARCHAR(80)  NOT NULL,
  email             VARCHAR(120) NOT NULL,
  UNIQUE KEY uq_participante_email (email)
);

CREATE TABLE login (
  correo            VARCHAR(120) PRIMARY KEY,
  contrasena        VARCHAR(128) NOT NULL,
  isAdmin           BOOLEAN NOT NULL,
  CONSTRAINT fk_login_participante_email
    FOREIGN KEY (correo) REFERENCES participante(email)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE sesion_login (
  id            CHAR(36) PRIMARY KEY,            -- UUID v4 en texto
  correo        VARCHAR(120) NOT NULL,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expiracion    DATETIME NOT NULL,
  revocado      BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_sesion_login_correo
    FOREIGN KEY (correo) REFERENCES login(correo)
    ON UPDATE CASCADE ON DELETE CASCADE,
  INDEX idx_sesion_login_correo (correo)
);


CREATE TABLE participante_programa_academico (
  id_alumno_programa  BIGINT AUTO_INCREMENT PRIMARY KEY,   -- Pongo BigInt porque asumo que las reservas se van a ir acumulando año tras año.
  ci_participante      VARCHAR(8) NOT NULL,
  nombre_programa      VARCHAR(120) NOT NULL,
  rol                  ENUM('estudiante_grado','estudiante_posgrado', 'docente') NOT NULL,
  CONSTRAINT fk_pp_ci
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
    ON DELETE CASCADE,
  CONSTRAINT fk_pp_programa
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  UNIQUE KEY uq_pp_participante_programa_rol (ci_participante, nombre_programa, rol)
);

CREATE TABLE turno (
  id_turno          TINYINT PRIMARY KEY,
  hora_inicio       TIME NOT NULL,
  hora_fin          TIME NOT NULL,
  CONSTRAINT chk_turno_duracion CHECK (TIMESTAMPDIFF(MINUTE, hora_inicio, hora_fin) = 60) -- Verifico que el turno sea de 1 hora exacta.
);

-- >>> Modificada: se agrega "estado" <<<
CREATE TABLE sala (
  nombre_sala       VARCHAR(80) NOT NULL,
  edificio          VARCHAR(80) NOT NULL,
  capacidad         SMALLINT     NOT NULL CHECK (capacidad > 0),
  tipo_sala         ENUM('libre','posgrado','docente') NOT NULL,
  estado            ENUM('operativa', 'con_inconvenientes', 'fuera_de_servicio') NOT NULL DEFAULT 'operativa',
  PRIMARY KEY (nombre_sala, edificio),
  CONSTRAINT fk_sala_edificio
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE reserva (
  id_reserva        BIGINT AUTO_INCREMENT PRIMARY KEY,
  nombre_sala       VARCHAR(80) NOT NULL,
  edificio          VARCHAR(80) NOT NULL,
  fecha             DATE NOT NULL,
  id_turno          TINYINT NOT NULL,
  estado            ENUM('activa','cancelada','sin_asistencia','finalizada') NOT NULL,
  -- Relación con sala (clave compuesta) y turno:
  CONSTRAINT fk_reserva_sala
    FOREIGN KEY (nombre_sala, edificio) REFERENCES sala(nombre_sala, edificio)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_reserva_turno
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  -- No permitir doble reserva de la misma sala en mismo día/turno:
  UNIQUE KEY uq_reserva_slot (nombre_sala, edificio, fecha, id_turno)
);

CREATE TABLE reserva_participante (
  ci_participante           VARCHAR(8) NOT NULL,
  id_reserva                BIGINT NOT NULL,
  fecha_solicitud_reserva   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  asistencia                BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (ci_participante, id_reserva),
  CONSTRAINT fk_rp_ci
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_rp_reserva
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
    ON UPDATE CASCADE ON DELETE CASCADE,
  -- Un participante no puede estar en dos salas al mismo tiempo (mismo día/turno):
  UNIQUE KEY uq_rp_conflicto_tiempo (ci_participante, id_reserva)
);

CREATE TABLE sancion_participante (
  id_sancion        INT AUTO_INCREMENT PRIMARY KEY, -- ¡Nueva Clave Primaria! vamo arriba la celeste - GLORIOOOOSA CELESTEEEE.
  ci_participante   VARCHAR(8) NOT NULL,
  fecha_inicio      DATE NOT NULL,
  fecha_fin         DATE NOT NULL,
  motivo            VARCHAR(200) DEFAULT 'no asistencia',
  CONSTRAINT fk_sancion_ci
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT chk_sancion_fechas CHECK (fecha_fin > fecha_inicio),
  -- Se añade un índice único para prevenir sanciones idénticas (mismo participante y misma fecha de inicio),
  -- aunque con la nueva PK ya se permiten múltiples sanciones.
  UNIQUE KEY uq_sancion_participante_fecha (ci_participante, fecha_inicio)
);

-- ======================================
--  Tablas nuevas: ALERTAS
-- ======================================

CREATE TABLE incidencia_sala (
  id_incidencia     BIGINT AUTO_INCREMENT PRIMARY KEY,
  nombre_sala       VARCHAR(80) NOT NULL,
  edificio          VARCHAR(80) NOT NULL,
  id_reserva        BIGINT NULL,         -- reserva desde la que se reportó (si aplica).
  ci_reportante     VARCHAR(8) NOT NULL, -- participante que reporta.

  tipo              ENUM('infraestructura','equipamiento','limpieza','ruido','otro') NOT NULL,
  gravedad          ENUM('baja','media','alta') NOT NULL,
  descripcion       VARCHAR(500) NOT NULL,

  estado            ENUM('abierta','en_proceso','resuelta') NOT NULL DEFAULT 'abierta',
  fecha_reporte     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_resolucion  DATETIME NULL,

  CONSTRAINT fk_incidencia_sala
    FOREIGN KEY (nombre_sala, edificio)
    REFERENCES sala(nombre_sala, edificio)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT fk_incidencia_reserva
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
    ON UPDATE CASCADE ON DELETE SET NULL,

  CONSTRAINT fk_incidencia_reportante
    FOREIGN KEY (ci_reportante) REFERENCES participante(ci)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE alerta_reserva (
  id_alerta         BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_reserva        BIGINT NOT NULL,
  id_incidencia     BIGINT NOT NULL,

  tipo_alerta       ENUM('sala_inhabilitada','inconveniente','recordatorio') NOT NULL,
  mensaje           VARCHAR(500) NOT NULL,

  fecha_creacion    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  leida             BOOLEAN NOT NULL DEFAULT FALSE,

  CONSTRAINT fk_alerta_reserva
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
    ON UPDATE CASCADE ON DELETE CASCADE,

  CONSTRAINT fk_alerta_incidencia
    FOREIGN KEY (id_incidencia) REFERENCES incidencia_sala(id_incidencia)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- View para ver el estado de las salas:
DROP VIEW IF EXISTS vista_estado_sala;

CREATE VIEW vista_estado_sala AS
SELECT
  s.nombre_sala,
  s.edificio,
  CASE
    WHEN EXISTS (
      SELECT 1 FROM incidencia_sala i
      WHERE i.nombre_sala = s.nombre_sala
        AND i.edificio    = s.edificio
        AND i.estado <> 'resuelta'
        AND i.gravedad = 'alta'
    ) THEN 'fuera_de_servicio'
    WHEN EXISTS (
      SELECT 1 FROM incidencia_sala i
      WHERE i.nombre_sala = s.nombre_sala
        AND i.edificio    = s.edificio
        AND i.estado <> 'resuelta'
    ) THEN 'con_inconvenientes'
    ELSE 'operativa'
  END AS estado_calculado,
  s.estado AS estado_manual
FROM sala s;

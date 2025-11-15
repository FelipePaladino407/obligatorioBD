-- Inserciones:


INSERT INTO facultad (nombre) VALUES  -- Solo le pongo nombre, pues el id_facultad se autoincremnta solo.
('Ingeniería y Tecnologías'),
('Ciencias Empresariales'),
('Psicología'),
('Arquitectura'),
('Derecho');


INSERT INTO edificio 
VALUES ('Mullin', 'Comandante Braga 2745', 'Montevideo'),
('Athanasius - Centro Ignis', 'Gral. Urquiza 2871', 'Montevideo'),
('Sede Salto - UCU', 'Artigas 1251', 'Salto'),
('El central', 'Av. 8 de ocutbre 2738', 'Montevideo');


INSERT INTO programa_academico
VALUES
('Ingeniería Informática', 1, 'grado'),
('Ingeniería en tecnólogo en madera', '1', 'grado'),
('Lic. en Negocios Internacionales', 2, 'grado'),
('MBA', 2, 'posgrado'),
('Psicología Clínica', 3, 'grado'),
('Derecho Penal', 4, 'posgrado');


INSERT INTO participante 
VALUES
('48012345', 'Marcelo', 'Arrarte', 'marrarteChelo@ucu.edu.uy'),
('49056789', 'Felipe', 'Paladino', 'felipeElBocha@ucu.edu.uy'),
('50111222', 'Santiago', 'Blanco', 'santiagoBlancoc@ucu.edu.uy'),
('52033444', 'Urbano', 'Malagrasa', 'urbanoMalagrasa1234@ucu.edu.uy'),
('54055666', 'Sebastian', 'Torres', 'sebaTorres@ucu.edu.uy'),
('55077888', 'Javier', 'Wagner', 'whiskey@ucu.edu.uy'),
('56099000', 'Constanza', 'Blanco', 'cotiBlanco@ucu.edu.uy'),
('57011122', 'Manuel', 'Cabrera', 'ManuCabra@ucu.edu.uy'),
('58033344', 'Facundo', 'Martinez', 'facuMartine@ucu.edu.uy'),
('59055566', 'Mauro', 'Machado', 'mauchoMorado@ucu.edu.uy');


INSERT INTO login 
VALUES
('cotiBlanco@ucu.edu.uy', '2468'),
('marrarteChelo@ucu.edu.uy', '1234'),
('sebaTorres@ucu.edu.uy', '123456789'),
('santiagoBlancoc@ucu.edu.uy', 'iHateWindows'),
('whiskey@ucu.edu.uy', 'uuuu');


INSERT INTO participante_programa_academico (ci_participante, nombre_programa, rol) 
VALUES
('48012345', 'Lic. en Negocios Internacionales', 'estudiante_grado'),
('49056789', 'Ingeniería Informática', 'estudiante_grado'),
('54055666', 'Ingeniería Informática', 'docente'),
('59055566', 'Psicología Clínica', 'estudiante_grado'),
('56099000', 'MBA', 'estudiante_posgrado'),
('52033444', 'Derecho Penal', 'docente'),
('57011122', 'MBA', 'estudiante_posgrado'),
('58033344', 'Lic. en Negocios Internacionales', 'estudiante_grado'),
('50111222', 'Ingeniería Informática', 'estudiante_grado'),
('55077888', 'MBA', 'docente');


INSERT INTO turno (id_turno, hora_inicio, hora_fin) VALUES
(1, '08:00:00', '09:00:00'),
(2, '09:00:00', '10:00:00'),
(3, '10:00:00', '11:00:00'),
(4, '11:00:00', '12:00:00'),
(5, '12:00:00', '13:00:00'),
(6, '13:00:00', '14:00:00'),
(7, '14:00:00', '15:00:00'),
(8, '15:00:00', '16:00:00'),
(9, '16:00:00', '17:00:00'),
(10, '17:00:00', '18:00:00'),
(11, '18:00:00', '19:00:00'),
(12, '19:00:00', '20:00:00'),
(13, '20:00:00', '21:00:00'),
(14, '21:00:00', '22:00:00'),
(15, '22:00:00', '23:00:00');


INSERT INTO sala 
VALUES
('Sala 1', 'El central', 15, 'libre'),
('Sala 2', 'El central', 10, 'libre'),
('Sala 3', 'Mullin', 3, 'posgrado'),
('Sala 4', 'Athanasius - Centro Ignis', 8, 'docente'), 
('Sala 5', 'Sede Salto - UCU', 12, 'libre');


INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado) 
VALUES
('Sala 3', 'Mullin', '2025-10-12', 8, 'activa'),
('Sala 3', 'Mullin', '2025-10-12', 1, 'finalizada'),
('Sala 2', 'El central', '2025-10-13', 3, 'activa'),
('Sala 1', 'El central', '2025-10-13', 4, 'cancelada'),
('Sala 4', 'Athanasius - Centro Ignis', '2025-10-14', 9, 'cancelada'),
('Sala 5', 'Sede Salto - UCU', '2025-10-14', 5, 'sin_asistencia');


INSERT INTO reserva_participante (ci_participante, id_reserva, asistencia) VALUES
('48012345', 1, TRUE),
('49056789', 1, TRUE),
('50111222', 2, TRUE),
('54055666', 3, FALSE),
('56099000', 3, TRUE),
('57011122', 4, FALSE),
('58033344', 5, FALSE);


INSERT INTO sancion_participante 
VALUES
('54055666', '2025-10-15', '2025-12-15', 'No asistencia a reserva 3'),
('49056789', '2025-10-14', '2025-12-14', 'Morosidad en la biblioteca'),
('58033344', '2025-10-15', '2025-12-15', 'No asistencia a reserva 5');


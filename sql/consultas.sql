USE reservas_salas_estudio;

-- Consultas:
-- Salas más reservadas (por cantidad de reservas)
SELECT
    r.nombre_sala,
    r.edificio,
    COUNT(*) AS cantidad_reservas
FROM reserva r
-- WHERE r.estado <> 'cancelada'
GROUP BY r.nombre_sala, r.edificio
ORDER BY cantidad_reservas DESC
LIMIT 10;



    -- • Turnos mas demandados:
SELECT
    t.id_turno,
    t.hora_inicio,
    t.hora_fin,
    COUNT(r.id_reserva) AS cantidad_reservas
FROM turno t
LEFT JOIN reserva r
    ON r.id_turno = t.id_turno
   AND r.estado <> 'cancelada'   -- no cuento calceladas.
GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
ORDER BY cantidad_reservas DESC;



    -- Promedio de participantes por sala:
SELECT
    sub.nombre_sala,
    sub.edificio,
    ROUND(AVG(sub.cantidad_personas), 2) AS promedio_participantes
FROM (
    SELECT
        r.id_reserva,
        r.nombre_sala,
        r.edificio,
        COUNT(rp.ci_participante) AS cantidad_personas
    FROM reserva r
    LEFT JOIN reserva_participante rp
        ON rp.id_reserva = r.id_reserva
    WHERE r.estado IN ('activa', 'finalizada')
    GROUP BY r.id_reserva, r.nombre_sala, r.edificio
) AS sub
GROUP BY sub.nombre_sala, sub.edificio
ORDER BY promedio_participantes DESC;



    -- • Cantidad de reservas por carrera y facultad
SELECT f.nombre AS facultad, p.nombre_programa AS programa, COUNT(DISTINCT r.id_reserva) AS cantidad_reservas
FROM reserva r
JOIN reserva_participante rp on rp.id_reserva = r.id_reserva
JOIN participante_programa_academico ppa on ppa.ci_participante = rp.ci_participante
JOIN programa_academico p ON ppa.nombre_programa = p.nombre_programa
JOIN facultad f ON p.id_facultad = f.id_facultad
GROUP BY f.nombre, p.nombre_programa
ORDER BY f.nombre, cantidad_reservas DESC;



    -- • Porcentaje de ocupación de salas por edificio (doy por hecho que el calculo es solo sobre los dias en los que hay al menos una reserva registrada).
SELECT
    s.edificio,
    COUNT(DISTINCT r.id_reserva) AS reservas_realizadas,
    COUNT(DISTINCT r.id_reserva) * 100.0 /
    NULLIF(
        (COUNT(DISTINCT s.nombre_sala) * COUNT(DISTINCT r.fecha) * COUNT(DISTINCT r.id_turno)),
        0
    ) AS porcentaje_ocupacion_aprox
FROM sala s
LEFT JOIN reserva r
    ON s.nombre_sala = r.nombre_sala
   AND s.edificio    = r.edificio
GROUP BY s.edificio
ORDER BY porcentaje_ocupacion_aprox DESC;



    -- • Cantidad de reservas y asistencias de profesores y alumnos (grado y posgrado)
SELECT ppa.rol AS tipo_participante, pa.tipo AS nivel, COUNT(rp.id_reserva) AS cantidad_reservas,
    SUM(CASE WHEN rp.asistencia = TRUE THEN 1 ELSE 0 END) AS cantidad_asistencias
FROM reserva_participante rp
JOIN participante_programa_academico ppa
    ON rp.ci_participante = ppa.ci_participante
JOIN programa_academico pa
    ON ppa.nombre_programa = pa.nombre_programa
GROUP BY ppa.rol, pa.tipo
ORDER BY ppa.rol, pa.tipo;



    -- • Cantidad de sanciones para profesores y alumnos (grado y posgrado)
SELECT ppa.rol, pa.tipo AS tipo_programa, COUNT(*) AS cantidad_sanciones
FROM sancion_participante sp
JOIN participante_programa_academico ppa ON sp.ci_participante = ppa.ci_participante
JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
GROUP BY ppa.rol, pa.tipo
ORDER BY ppa.rol, pa.tipo;



    -- • Porcentaje de reservas efectivamente utilizadas vs. canceladas/no asistidas
SELECT
    CASE
        WHEN estado = 'finalizada' THEN 'utilizada'
        WHEN estado IN ('cancelada','sin_asistencia') THEN 'no_utilizada'
        ELSE 'activa'
    END AS categoria,
    COUNT(*) AS cantidad,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reserva),
        2
    ) AS porcentaje
FROM reserva
GROUP BY categoria;

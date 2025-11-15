from datetime import date
from app.db import execute_query
from app.enums.extra.tipo_incidencia import TipoIncidencia
from app.enums.extra.gravedad_incidencia import GravedadIncidencia
from app.enums.extra.estado_incidencia import EstadoIncidencia
from app.models.extra.incidencia_model import IncidenciaCreate, IncidenciaUpdateEstado
from app.services.extra.incidencia_service import (
    crear_incidencia, actualizar_estado_incidencia,
    obtener_incidencia, listar_incidencias_abiertas
)
from app.services.extra.alerta_reserva_service import (
    propagar_alertas_por_incidencia, listar_alertas_de_reserva,
    marcar_alerta_leida
)
from app.services.sala_service import obtener_estado_sala
def _seed_minimo():
    # edificio
    execute_query("""
        INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento)
        VALUES (%s, %s, %s);
    """, ("Mullin", "Av. Ejemplo 123", "Montevideo"), fetch=False)

    # sala
    execute_query("""
        INSERT IGNORE INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s);
    """, ("Sala 101", "Mullin", 12, "libre"), fetch=False)

    # turno
    execute_query("""
        INSERT IGNORE INTO turno (id_turno, hora_inicio, hora_fin)
        VALUES (1, '09:00:00', '10:00:00');
    """, None, fetch=False)

    # participante
    execute_query("""
        INSERT IGNORE INTO participante (ci, nombre, apellido, email)
        VALUES (%s, %s, %s, %s);
    """, ("12345678", "Ana", "Pérez", "ana.perez@example.com"), fetch=False)

    # reserva activa HOY
    execute_query("""
        INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE id_reserva = id_reserva;
    """, ("Sala 101", "Mullin", date.today().isoformat(), 1, "activa"), fetch=False)

    # traer id_reserva
    row = execute_query("""
        SELECT id_reserva FROM reserva
        WHERE nombre_sala=%s AND edificio=%s AND fecha=%s AND id_turno=%s;
    """, ("Sala 101", "Mullin", date.today().isoformat(), 1), fetch=True)[0]
    id_reserva = row["id_reserva"]

    # relacionar participante
    execute_query("""
        INSERT IGNORE INTO reserva_participante (ci_participante, id_reserva, asistencia)
        VALUES (%s, %s, %s);
    """, ("12345678", id_reserva, False), fetch=False)

    return id_reserva

def test_flujo_incidencia_y_alertas():
    id_reserva = _seed_minimo()

    # Estado inicial de sala: existe
    est0 = obtener_estado_sala("Sala 101", "Mullin")
    assert est0 is not None

    # Crear incidencia ALTA (usa dataclass IncidenciaCreate)
    inc_id = crear_incidencia(IncidenciaCreate(
        nombre_sala="Sala 101",
        edificio="Mullin",
        ci_reportante="12345678",
        tipo=TipoIncidencia.EQUIPAMIENTO,
        gravedad=GravedadIncidencia.ALTA,
        descripcion="Proyector en corto",
        id_reserva=id_reserva,
    ))
    assert isinstance(inc_id, int) and inc_id > 0

    inc_row = obtener_incidencia(inc_id)
    assert inc_row is not None
    assert inc_row["estado"] == "abierta"
    assert inc_row["gravedad"] == "alta"

    # Propagar alertas a reservas activas de esa sala
    creadas = propagar_alertas_por_incidencia(
        id_incidencia=inc_id,
        nombre_sala="Sala 101",
        edificio="Mullin",
        gravedad="alta",
        mensaje_base="Sala fuera de servicio por incidencia grave"
    )
    assert isinstance(creadas, int)
    assert creadas >= 1  # al menos la reserva de hoy

    # Ver alertas de la reserva y marcar una como leída
    alertas = listar_alertas_de_reserva(id_reserva, solo_no_leidas=False)
    assert len(alertas) >= 1
    marcar_alerta_leida(alertas[0]["id_alerta"])
    alertas_no_leidas = listar_alertas_de_reserva(id_reserva, solo_no_leidas=True)
    assert isinstance(alertas_no_leidas, list)

    # Incidencias abiertas incluye la creada
    abiertas = listar_incidencias_abiertas()
    ids_abiertas = {i["id_incidencia"] for i in abiertas}
    assert inc_id in ids_abiertas

    # Resolver incidencia (usa dataclass IncidenciaUpdateEstado)
    actualizar_estado_incidencia(IncidenciaUpdateEstado(
        id_incidencia=inc_id,
        nuevo_estado=EstadoIncidencia.RESUELTA
    ))
    inc_row2 = obtener_incidencia(inc_id)
    assert inc_row2 is not None and inc_row2["estado"] == "resuelta"
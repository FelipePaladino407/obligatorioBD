from typing import List, Tuple, Any, Dict
from app.db import execute_query

# ==== helpers comunes ====

def _paginacion(p: dict) -> tuple[int, int]:
    limit = int(p.get("limit", 50))
    offset = int(p.get("offset", 0))
    return limit, offset

def _rango_fecha_and_params(p: dict, alias: str = "r") -> tuple[str, list[Any]]:
    where = []
    params: list[Any] = []
    if p.get("desde"):
        where.append(f"{alias}.fecha >= %s")
        params.append(p["desde"])
    if p.get("hasta"):
        where.append(f"{alias}.fecha <= %s")
        params.append(p["hasta"])
    return (" AND ".join(where), params)

def _exec(sql: str, params: list[Any]) -> Tuple[List[str], List[list]]:
    rows = execute_query(sql, tuple(params), True)  # retorna list[dict]
    if not rows:
        return [], []
    cols = list(rows[0].keys())
    data = [[r[c] for c in cols] for r in rows]
    return cols, data

# =============== CONSULTAS ===============

# 1) Salas más reservadas (por sala + edificio)
def salas_mas_reservadas(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    sql = """
      SELECT r.nombre_sala, r.edificio, COUNT(*) AS reservas
      FROM reserva r
      {where}
      GROUP BY r.nombre_sala, r.edificio
      ORDER BY reservas DESC
      LIMIT %s OFFSET %s
    """.format(where=("WHERE " + where_fecha) if where_fecha else "")
    params.extend([limit, offset])
    return _exec(sql, params)

# 2) Turnos más demandados
def turnos_mas_demandados(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    sql = """
      SELECT r.id_turno,
             t.hora_inicio, t.hora_fin,
             COUNT(*) AS reservas
      FROM reserva r
      JOIN turno t ON t.id_turno = r.id_turno
      {where}
      GROUP BY r.id_turno, t.hora_inicio, t.hora_fin
      ORDER BY reservas DESC
      LIMIT %s OFFSET %s
    """.format(where=("WHERE " + where_fecha) if where_fecha else "")
    params.extend([limit, offset])
    return _exec(sql, params)

# 3) Ocupación por edificio (finalizadas/total)
def ocupacion_por_edificio(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    sql = """
      SELECT r.edificio,
             SUM(CASE WHEN r.estado='finalizada' THEN 1 ELSE 0 END) AS finalizadas,
             COUNT(*) AS total,
             ROUND(100.0 * SUM(CASE WHEN r.estado='finalizada' THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS ocupacion_pct
      FROM reserva r
      {where}
      GROUP BY r.edificio
      ORDER BY ocupacion_pct DESC
      LIMIT %s OFFSET %s
    """.format(where=("WHERE " + where_fecha) if where_fecha else "")
    params.extend([limit, offset])
    return _exec(sql, params)

# 4) Reservas por programa y facultad
#    (participante -> participante_programa_academico -> programa_academico -> facultad)
def reservas_por_programa_facultad(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    extra_where = []
    if p.get("facultad"):
        extra_where.append("f.nombre = %s")
        params.append(p["facultad"])
    if p.get("edificio"):
        extra_where.append("r.edificio = %s")
        params.append(p["edificio"])

    where_total = " AND ".join(filter(None, [where_fecha] + extra_where))
    where_clause = "WHERE " + where_total if where_total else ""

    sql = f"""
      SELECT pa.nombre_programa,
             f.nombre AS facultad,
             pa.tipo   AS tipo_programa,   -- 'grado'/'posgrado'
             COUNT(DISTINCT r.id_reserva) AS reservas
      FROM reserva r
      JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
      JOIN participante pte ON pte.ci = rp.ci_participante
      JOIN participante_programa_academico ppa ON ppa.ci_participante = pte.ci
      JOIN programa_academico pa ON pa.nombre_programa = ppa.nombre_programa
      JOIN facultad f ON f.id_facultad = pa.id_facultad
      {where_clause}
      GROUP BY pa.nombre_programa, f.nombre, pa.tipo
      ORDER BY reservas DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)

# 5) Utilizadas vs canceladas o no asistidas (en el rango)
def utilizadas_vs_canceladas_noasistidas(p: dict) -> Tuple[List[str], List[list]]:
    where_fecha, params = _rango_fecha_and_params(p, "r")

    sql = """
      SELECT
        SUM(CASE WHEN r.estado='finalizada' THEN 1 ELSE 0 END) AS utilizadas,
        SUM(CASE WHEN r.estado IN ('cancelada','sin_asistencia') THEN 1 ELSE 0 END) AS no_utilizadas,
        COUNT(*) AS total
      FROM reserva r
      {where}
    """.format(where=("WHERE " + where_fecha) if where_fecha else "")
    return _exec(sql, params)

# 6) Sanciones por rol y tipo de programa (docente/alumno x grado/posgrado)
def sanciones_por_rol_y_tipo_programa(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    # El rango aplica sobre reservas relacionadas al sancionado si querés filtrar por edificio/fecha,
    # pero sanción no tiene edificio/turno. Tomamos fecha_inicio de sanción como rango temporal.
    where_fecha, params = "", []
    if p.get("desde"):
        where_fecha += " s.fecha_inicio >= %s"
        params.append(p["desde"])
    if p.get("hasta"):
        where_fecha += (" AND " if where_fecha else "") + " s.fecha_inicio <= %s"
        params.append(p["hasta"])

    extra = []
    if p.get("facultad"):
        extra.append(" f.nombre = %s ")
        params.append(p["facultad"])

    where_total = " AND ".join(filter(None, [where_fecha] + extra))
    where_clause = "WHERE " + where_total if where_total else ""

    sql = f"""
      SELECT ppa.rol,                       -- 'alumno' / 'docente'
             pa.tipo AS tipo_programa,      -- 'grado' / 'posgrado'
             COUNT(*) AS sanciones
      FROM sancion_participante s
      JOIN participante pte ON pte.ci = s.ci_participante
      JOIN participante_programa_academico ppa ON ppa.ci_participante = pte.ci
      JOIN programa_academico pa ON pa.nombre_programa = ppa.nombre_programa
      JOIN facultad f ON f.id_facultad = pa.id_facultad
      {where_clause}
      GROUP BY ppa.rol, pa.tipo
      ORDER BY sanciones DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)

# 7) Promedio de participantes por sala (en reservas finalizadas)
def promedio_participantes_por_sala(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    extra = ["r.estado='finalizada'"]
    if where_fecha:
        extra.append(where_fecha)
    if p.get("edificio"):
        extra.append("r.edificio = %s")
        params.append(p["edificio"])

    where_clause = "WHERE " + " AND ".join(extra)

    sql = f"""
      SELECT r.nombre_sala,
             r.edificio,
             ROUND(AVG(sub.cant_participantes), 2) AS promedio_participantes
      FROM reserva r
      JOIN (
        SELECT rp.id_reserva, COUNT(*) AS cant_participantes
        FROM reserva_participante rp
        GROUP BY rp.id_reserva
      ) sub ON sub.id_reserva = r.id_reserva
      {where_clause}
      GROUP BY r.nombre_sala, r.edificio
      ORDER BY promedio_participantes DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)

# 8) Incidencias abiertas por sala y gravedad (orden consistente con tus services)
def incidencias_abiertas_por_sala(p: dict):
    limit = int(p.get("limit", 50)); offset = int(p.get("offset", 0))
    where = ["i.estado <> 'resuelta'"]; params = []
    if p.get("edificio"):
        where.append("i.edificio = %s"); params.append(p["edificio"])
    sql = f"""
      SELECT i.nombre_sala, i.edificio, i.gravedad, COUNT(*) AS incidencias_abiertas
      FROM incidencia_sala i
      WHERE {' AND '.join(where)}
      GROUP BY i.nombre_sala, i.edificio, i.gravedad
      ORDER BY FIELD(i.gravedad,'alta','media','baja'), incidencias_abiertas DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)


# 9) (Propia) Salas con mayor ratio de "no asistencia"
def ratio_no_asistencia_por_sala(p: dict) -> Tuple[List[str], List[list]]:
    limit, offset = _paginacion(p)
    where_fecha, params = _rango_fecha_and_params(p, "r")

    extra = []
    if p.get("edificio"):
        extra.append("r.edificio = %s")
        params.append(p["edificio"])

    where_total = " AND ".join(filter(None, [where_fecha] + extra))
    where_clause = "WHERE " + where_total if where_total else ""

    sql = f"""
      WITH tot AS (
        SELECT r.id_reserva, r.nombre_sala, r.edificio, r.estado
        FROM reserva r
        {where_clause}
      ),
      noas AS (
        SELECT nombre_sala, edificio, SUM(CASE WHEN estado='sin_asistencia' THEN 1 ELSE 0 END) AS no_asistidas,
               COUNT(*) AS total
        FROM tot
        GROUP BY nombre_sala, edificio
      )
      SELECT nombre_sala, edificio,
             no_asistidas, total,
             ROUND(100.0 * no_asistidas / NULLIF(total,0), 2) AS ratio_no_asistencia_pct
      FROM noas
      ORDER BY ratio_no_asistencia_pct DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)

# 10) Alertas por tipo (sin cambios funcionales, solo consistente con tus enums)
def alertas_por_tipo(p: dict):
    limit = int(p.get("limit", 50)); offset = int(p.get("offset", 0))
    params = []; where = []
    if p.get("desde"): where.append("a.fecha_creacion >= %s"); params.append(p["desde"])
    if p.get("hasta"): where.append("a.fecha_creacion <= %s"); params.append(p["hasta"])
    if p.get("edificio"): where.append("r.edificio = %s"); params.append(p["edificio"])
    wc = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
      SELECT a.tipo_alerta, COUNT(*) AS cantidad
      FROM alerta_reserva a
      JOIN reserva r ON r.id_reserva = a.id_reserva
      {wc}
      GROUP BY a.tipo_alerta
      ORDER BY cantidad DESC
      LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    return _exec(sql, params)

# 11) NUEVO (opcional): Estado de salas (usa VIEW si existe, si no, tabla)
def estado_salas_resumen(p: dict):
    limit = int(p.get("limit", 50)); offset = int(p.get("offset", 0))
    try:
        sql = """
          SELECT nombre_sala, edificio, estado_calculado, estado_manual
          FROM vista_estado_sala
          ORDER BY edificio, nombre_sala
          LIMIT %s OFFSET %s
        """
        return _exec(sql, [limit, offset])
    except Exception:
        # fallback a tabla, igual que tu sala_service
        sql = """
          SELECT nombre_sala, edificio, estado AS estado_manual
          FROM sala
          ORDER BY edificio, nombre_sala
          LIMIT %s OFFSET %s
        """
        cols, rows = _exec(sql, [limit, offset])
        if rows:
            # agregar columna calculada = manual (mismo comportamiento que tu helper)
            idx = {c:i for i,c in enumerate(cols)}
            if "estado_calculado" not in cols:
                cols = cols + ["estado_calculado"]
            for r in rows:
                r.append(r[idx["estado_manual"]])
        return cols, rows


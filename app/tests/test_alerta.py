from app.services.alerta_service import (
    crear_alerta,
    cambiar_estado_alerta,
    listar_alertas_abiertas,
    obtener_alerta,
)
from app.models.alerta_model import AlertaCreate, AlertaUpdateEstado
from app.enums.tipo_alerta import TipoAlerta
from app.enums.estado_alerta import EstadoAlerta

from app.db import execute_query

def seed_minimo():
    # edificio
    execute_query("""
        INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento)
        VALUES (%s, %s, %s);
    """, ("Mullin","Av. Ejemplo 123","Montevideo"), fetch=False)

    # sala (depende del edificio)
    execute_query("""
        INSERT IGNORE INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s);
    """, ("Sala 101","Mullin",12,"libre"), fetch=False)


def main():
    seed_minimo()
    print("== Crear alerta FUEGO en Sala 101 / Mullin ==")
    aid = crear_alerta(AlertaCreate(
        nombre_sala="Sala 101",
        edificio="Mullin",
        tipo=TipoAlerta.FUEGO,
        prioridad="alta",
        descripcion="Detector de humo disparado",
        creado_por_ci=None,
    ))
    print("id_alerta creada:", aid)

    print("\n== Obtener alerta creada ==")
    a = obtener_alerta(aid)
    print(a)

    print("\n== Listar alertas abiertas (antes de cambiar estado) ==")
    for row in listar_alertas_abiertas():
        print(row["id_alerta"], row["tipo"], row["prioridad"], row["estado"])

    print("\n== Cambiar a EN_PROCESO ==")
    cambiar_estado_alerta(AlertaUpdateEstado(
        id_alerta=aid,
        nuevo_estado=EstadoAlerta.EN_PROCESO,
        nota="Se envió personal",
        hecho_por_ci=None
    ))
    print(obtener_alerta(aid))

    print("\n== Cambiar a RESUELTA ==")
    cambiar_estado_alerta(AlertaUpdateEstado(
        id_alerta=aid,
        nuevo_estado=EstadoAlerta.RESUELTA,
        nota="Incidente controlado",
        hecho_por_ci=None
    ))
    print(obtener_alerta(aid))

    print("\n== Listar alertas abiertas (después) ==")
    print(listar_alertas_abiertas())

if __name__ == "__main__":
    main()

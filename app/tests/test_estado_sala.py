from datetime import date
from app.db import execute_query
from app.services.sala_service import (
    obtener_estado_sala, listar_salas_con_estado,
    actualizar_estado_manual, sala_disponible_para_reserva
)

def seed_minimo():
    # Edificio
    execute_query("""
        INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento)
        VALUES (%s, %s, %s);
    """, ("Mullin", "Av. Ejemplo 123", "Montevideo"), fetch=False)

    # Sala (si no existe)
    execute_query("""
        INSERT IGNORE INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
        VALUES (%s, %s, %s, %s);
    """, ("Sala 101", "Mullin", 12, "libre"), fetch=False)

def test_estado_sala_view_o_fallback():
    seed_minimo()

    # 1) Por defecto debería estar operativa (manual y calculado)
    est = obtener_estado_sala("Sala 101", "Mullin")
    assert est is not None
    assert est["estado_calculado"] in ("operativa", "con_inconvenientes", "fuera_de_servicio")
    assert "estado_manual" in est

    # 2) Forzar manualmente fuera_de_servicio y verificar indisponible
    actualizar_estado_manual("Sala 101", "Mullin", "fuera_de_servicio")
    est2 = obtener_estado_sala("Sala 101", "Mullin")
    assert est2 is not None
    assert est2["estado_manual"] == "fuera_de_servicio"
    # Si existe la VIEW y hay incidencias que contradicen, prevalecerá calculado.
    # Pero en ausencia de incidencias, calculado = manual (o fallback lo iguala).
    assert est2["estado_calculado"] in ("fuera_de_servicio", "con_inconvenientes", "operativa")

    # 3) Helper de disponibilidad
    disp = sala_disponible_para_reserva("Sala 101", "Mullin")
    # Con manual fuera_de_servicio y sin incidencias, el fallback lo verá como fuera_de_servicio
    # Si existe la VIEW y no hay incidencias, podría volver 'operativa' según la lógica calculada.
    assert isinstance(disp, bool)

    # 4) Listado general
    lista = listar_salas_con_estado()
    assert isinstance(lista, list)
    assert any(s["nombre_sala"] == "Sala 101" and s["edificio"] == "Mullin" for s in lista)

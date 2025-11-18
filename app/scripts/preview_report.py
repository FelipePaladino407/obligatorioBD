# scripts/preview_report.py
from pprint import pprint
from app.services.reportes_service import ejecutar_consulta

def ver(consulta, params=None):
    params = params or {}
    out = ejecutar_consulta(consulta, params)
    print(f"\n== {out['consulta_id']} ==")
    print("columns:", out["columns"])
    for row in out["rows"]:
        print(row)
    print("count:", out["count"])

if __name__ == "__main__":
    ver("SALAS_MAS_RESERVADAS")
    ver("OCUPACION_POR_EDIFICIO")
    ver("UTILIZADAS_VS_CANCELADAS_NOASISTIDAS")
    ver("PROMEDIO_PARTICIPANTES_POR_SALA")

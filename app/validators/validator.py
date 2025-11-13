from __future__ import annotations
from typing import Any, Iterable, Optional, Tuple


def validate_params(params: Optional[Tuple[Any, ...]], max_str_len: int = 1024) -> None:
    """
    Valida parámetros que vienen del usuario antes de pasarlos al muchacho.
    Lanza ValueError si algún parámetro es sospechoso.

    NOTA: ¿Porqué no valido que no contenga palabras reservadas SQL como SELECT? Porque tener las consultas
    parametrizadas hace que el MySQL tome los parámetros exclusivamente como strings (el driver me arregla todo de una).
    Si evito que los parametros contengan algo como 'SELECT' puede dar lugar a falsos positivos. Ej: Que mi contraseña
    contenga la palabra 'select'.
 
    Reglas:
      - Acepta tipos: str, int, float, bool, bytes
      - Para str: longitud <= max_str_len y no contiene caracteres de control (excepto espacios)
      - Para bytes: longitud <= max_str_len
      - None está permitido (si la query lo espera)
    """
    if not params:
        return

    allowed_simple_types = (str, int, float, bool, bytes)

    for idx, p in enumerate(params):
        if p is None:
            continue

        if not isinstance(p, allowed_simple_types):
            raise ValueError(f"Parámetro #{idx} de tipo no permitido: {type(p).__name__}")

        if isinstance(p, str):
            if len(p) > max_str_len:
                raise ValueError(f"Parámetro #{idx} excede longitud máxima ({max_str_len})")
            if any(ch in p for ch in ("\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
                                      "\x07", "\x08", "\x0b", "\x0c", "\x0e", "\x0f")):
                raise ValueError(f"Parámetro #{idx} contiene caracteres de control inválidos")

        if isinstance(p, (bytes, bytearray)):
            if len(p) > max_str_len:
                raise ValueError(f"Parámetro #{idx} (bytes) excede longitud máxima ({max_str_len})")


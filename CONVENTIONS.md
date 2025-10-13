## 🧭 Convenciones de código – Backend Python (Equipo BD 2025)

---

### 🔹 1. Tipado estático obligatorio

* Toda función y variable **debe tener tipo declarado**.
* No se aceptan anotaciones vagas como `Any`, ni funciones sin anotaciones.
* Se validará con **mypy** o **pyright**.

```python
# ✅ Correcto
def calcular_reservas(fecha: date, ci: str) -> int:
    ...

# ❌ Incorrecto
def calcular_reservas(fecha, ci):
    ...
```

---

### 🔹 2. Variables y constantes

* Nombres en **snake_case**, constantes en **MAYÚSCULAS**.
* No se crean variables “al vuelo” dentro del flujo sin declaración clara.

```python
MAX_RESERVAS_SEMANA: int = 3
nombre_sala: str = "Sala A"
```

---

### 🔹 3. Tipado de colecciones

Usar `typing` para declarar estructuras de datos.

```python
from typing import List, Dict, Tuple

reservas: List[int] = []
mapa_salas: Dict[str, int] = {"Mullin": 4}
```

---

### 🔹 4. Retornos explícitos

Ninguna función debe retornar `None` sin anotarlo explícitamente:

```python
def registrar_asistencia(id_reserva: int, ci: str) -> None:
    ...
```

---

### 🔹 5. Documentación mínima por función

Cada función debe tener un docstring que indique **propósito, parámetros y tipo de retorno**:
- Comentarios en Español

```python
def crear_reserva_validada(nombre_sala: str, fecha: date, id_turno: int) -> int:
    """
    Crea una nueva reserva validando disponibilidad y reglas de negocio.
    Args:
        nombre_sala (str): nombre de la sala
        fecha (date): fecha de la reserva
        id_turno (int): turno seleccionado (1–15)
    Returns:
        int: ID de la reserva creada
    """
```

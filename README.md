# UCU Reservas

En este repositorio podrá contemplar el sistema de backend (API RESTful) y la base de datos MySQL para la gestión de reservas de salas de estudio, desarrollado como obligatorio del curso de Bases de Datos I.

Integrantes:
- Santiago Blanco
- Facundo Martinez
- Felipe Paladino

## 📝 Requisitos

Para ejecutar el proyecto, precisamos:

1.  **Docker**
2.  **Docker Compose**
3.  **Ánimo de corregir con misericordia**

## ⚙️ Configuración de las variables de entorno (`.env`)

El sistema depende de variables de entorno para una gestión segura de credenciales, siguiendo el **Principio de Mínimos Privilegios**. Debes crear un archivo llamado **`.env`** en el directorio raíz del proyecto con el siguiente contenido:

```env
# Configuración de Conexión de la Base de Datos
DB_HOST=db
DB_NAME=reservas_salas_estudio

DB_USER_ADMIN=admin
DB_PASS_ADMIN=obligatorio1234_admin

DB_USER_APP=app_user
DB_PASS_APP=obligatorio1234

SECRET_KEY=DinetaBD_2025
```

> ⚠️ **Nota:** El backend utiliza dos usuarios de base de datos (`admin` y `app_user`). Esto hace que, incluso si un delincuente sinvergüenza compromete una ruta común, sus acciones están limitadas por los permisos de `app_user`, que **no puede alterar la estructura de la base de datos** (Principio de Mínimos Privilegios).

-----

## 🚀 Vamo' arriba

Utilizamos Docker Compose para levantar la aplicación Flask y MySQL. Está configurado de manera que se ejecuten scripts de creación de tablas e inserciones al levantar el contenedor.

```sh
docker compose up --build -d
```
El flag `--build` es necesario la primera vez o cuando se actualizan dependencias/código en el `Dockerfile`.

## 🌐 Estructura de la API con Flask

La API sigue un diseño **RESTful** y modular. El punto de entrada principal es `http://localhost:8080/api/v1/`. Los principales endpoints son estos, para el resto fijate vos:

| Prefijo de Ruta | Funcionalidad Principal | Requisito de Acceso |
| :--- | :--- | :--- |
| `/api/v1/auth` | Login, Logout, Cambio de Contraseña | Público |
| `/api/v1/reserva` | Creación, Consulta, Cancelación de Reservas | `@required_token` |
| `/api/v1/sala` | Consulta de Salas y Estados | `@required_token` / `@admin_required` |
| `/api/v1/incidencia` | Reporte de Problemas en Salas | `@required_token` |
| `/api/v1/participante` | Gestión de Usuarios, Consulta `/me` | `@required_token` / `@admin_required` |
| `/api/v1/reportes` | Consultas Administrativas y Estadísticas | `@admin_required` |

### Autenticación

El acceso a los endpoints protegidos se realiza mediante **JSON Web Tokens (JWT)** pasados en el header `Authorization: Bearer <token>`. La validez del token se refuerza con una verificación en la tabla `sesion_login` (expiración y revocación).

-----

## 🛑 El Frontend

> **Repositorio de frontend**: [ObligatorioBD_FrontEnd](https://github.com/FelipePaladino407/obligatorioBD_FrontEnd)

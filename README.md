# Biblioteca

API REST para la gestión de autores, categorías, libros, socios y préstamos con FastAPI, SQLAlchemy 2.x y PostgreSQL.

## Instalación

Requiere Python 3.10+ y PostgreSQL. Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea la base de datos en PostgreSQL (si aún no existe) y asigna una contraseña al usuario:

```sql
ALTER USER postgres WITH PASSWORD 'tu_contrasena';
CREATE DATABASE "FASTAPI_BIBLIOTECA" OWNER postgres;
```

Copia `.env.example` a `.env` y configura la conexión:

```env
DATABASE_URL=postgresql+psycopg://postgres:tu_contrasena@localhost:5432/FASTAPI_BIBLIOTECA
```

Al arrancar, la aplicación crea las tablas con `Base.metadata.create_all`.

## Ejecución

```powershell
uvicorn app.main:app --reload
```

Documentación interactiva: <http://127.0.0.1:8000/docs>.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET, POST | `/autores` | Listar y crear autores |
| GET, PATCH, DELETE | `/autores/{id}` | Consultar, actualizar y eliminar autor |
| GET | `/autores/{id}/libros` | Libros de un autor |
| GET, POST | `/categorias` | Listar y crear categorías |
| PATCH, DELETE | `/categorias/{id}` | Actualizar y eliminar categoría |
| GET, POST | `/libros` | Listar y crear libros |
| GET, PATCH, DELETE | `/libros/{id}` | Consultar, actualizar y eliminar libro |
| GET, POST | `/socios` | Listar y crear socios |
| GET, PATCH, DELETE | `/socios/{id}` | Consultar, actualizar y eliminar socio |
| GET | `/socios/{id}/prestamos` | Préstamos de un socio |
| GET, POST | `/prestamos` | Listar y crear préstamos |
| GET | `/prestamos/{id}` | Consultar préstamo |
| POST | `/prestamos/{id}/devolucion` | Registrar devolución |
| GET | `/reportes/libros-mas-prestados` | Libros más prestados |
| GET | `/reportes/categorias` | Libros por categoría |
| GET | `/reportes/prestamos-vencidos` | Préstamos vencidos |
| GET | `/reportes/socios-con-multas` | Multas por socio |
| GET | `/reportes/autores` | Totales por autor |
| GET | `/reportes/resumen` | Resumen general |

Los listados de recursos admiten `skip` y `limit` (máximo 100); el reporte de libros más prestados admite `limite` (máximo 100).

## Integrantes

Por definir.

# API de Venta de Autos

API REST construida con FastAPI, SQLModel y PostgreSQL para administrar el inventario de automóviles y registrar ventas. Incluye CRUD completo, búsquedas y paginación.

## Requisitos
- Python 3.10+
- PostgreSQL instalado y un usuario con permisos de creación

## Configuración rápida
1. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Crea la base de datos (valor por defecto: `autos_db`):
   ```bash
   createdb autos_db
   ```
4. Exporta la URL de conexión:
   ```bash
   export DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/autos_db"
   ```
   Si utilizas `psycopg2` (por ejemplo en Python < 3.14), puedes usar `postgresql://...`.
   Opcional: define `DB_ECHO=false` para ocultar los logs SQL.
5. Inicia la API:
   ```bash
   uvicorn main:app --reload
   ```
6. Abre la documentación interactiva:
   - Swagger UI: http://localhost:8000/docs  
   - ReDoc: http://localhost:8000/redoc

### Crear tablas sin iniciar el servidor (opcional)
Con la variable `DATABASE_URL` exportada:
```bash
python -c "from database import create_db_and_tables; create_db_and_tables()"
```

## Estructura del proyecto
```
├── autos.py           # Rutas para autos
├── database.py        # Conexión y sesión de base de datos
├── main.py            # Aplicación FastAPI
├── models.py          # Modelos SQLModel y esquemas Pydantic
├── repository.py      # Implementación del patrón Repository
├── requirements.txt   # Dependencias
├── ventas.py          # Rutas para ventas
└── README.md
```

## Endpoints principales
- `POST /autos` Crear auto (valida chasis único)
- `GET /autos` Listar autos con paginación y búsqueda por marca/modelo
- `GET /autos/{id}` Obtener auto
- `PUT /autos/{id}` Actualizar auto (valida chasis único)
- `DELETE /autos/{id}` Eliminar auto
- `GET /autos/chasis/{numero_chasis}` Buscar por chasis
- `GET /autos/{id}/with-ventas` Auto con sus ventas

- `POST /ventas` Crear venta (valida existencia del auto)
- `GET /ventas` Listar ventas con filtros de comprador, auto, rango de precio y fechas
- `GET /ventas/{id}` Obtener venta
- `PUT /ventas/{id}` Actualizar venta
- `DELETE /ventas/{id}` Eliminar venta
- `GET /ventas/auto/{auto_id}` Ventas de un auto
- `GET /ventas/comprador/{nombre}` Búsqueda por comprador
- `GET /ventas/{id}/with-auto` Venta con datos del auto

## Pruebas automatizadas
Para ejecutar los tests rápidos con SQLite temporal:
```bash
export DATABASE_URL="sqlite:///./test.db"
pytest
```

## Validaciones clave
- Autos: año entre 1900 y el año actual, número de chasis alfanumérico y único.
- Ventas: precio > 0, comprador no vacío, fecha no futura, integridad referencial del auto.

## Notas
- La creación de tablas se ejecuta automáticamente en el evento de arranque de FastAPI.
- Para generar datos de ejemplo puedes reutilizar los cuerpos JSON incluidos en la consigna.

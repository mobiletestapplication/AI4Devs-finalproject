# Proposal

## Why

La importación (BE-01b), la caché de precios (BE-02) y todo lo que se calcula después necesitan las tablas de la sección 3 del readme. Hoy Alembic está inicializado sin migraciones y el servicio `migrate` de compose no crea nada.

DB-01 es el siguiente ticket del orden acordado. Fija en la base de datos las restricciones que protegen la cartera aunque falle la validación de la aplicación:
- una sola cartera vigente;
- cantidades y precios positivos;
- venta completa;
- importes en `NUMERIC` exacto.

Cubre el **ticket DB-01** (ticket 1 de la sección 6) de la Entrega 2, que da soporte a las features **F1-F5** y a las historias **HU-1 a HU-5**.

## What Changes

- **Modelos SQLAlchemy 2** en `backend/app/infrastructure/db/`:
  - `CARTERA_VIGENTE`, `IMPORTACION`, `POSICION`, `PRECIO_DIARIO` y `COBERTURA_PRECIO`, con los tipos, claves, CHECK e índices del diagrama 3.1;
  - `Numeric(18, 6, asdecimal=True)` en importes, precios y cantidades;
  - `date` en las fechas de negocio y `timestamptz` en los instantes técnicos.
- **Fábrica de conexiones** a partir de `DATABASE_URL`, que usan el seed y los tests. Las sesiones por petición de FastAPI llegan con BE-01b.
- **Primera migración de Alembic** con el esquema completo y su `downgrade`. Alembic pasa a usar los metadatos de los modelos.
- **Seed** `python -m app.scripts.seed` con un fixture mínimo de 3 posiciones (abiertas y cerradas). Solo carga si no hay cartera vigente, para no sustituir la del usuario.
- **Tests de integración con Testcontainers** (`postgres:16.16`, la misma imagen que compose):
  - la migración sube y baja en limpio;
  - el esquema migrado coincide con los modelos;
  - un `IntegrityError` por cada CHECK;
  - una segunda fila en `CARTERA_VIGENTE` falla;
  - borrar la importación vigente falla;
  - 0,1 se lee como `Decimal('0.100000')`;
  - el seed es idempotente.
- **Directorio `datos-locales/` ignorado por git**, para dejar los XLSX de prueba manual que se usarán desde BE-01b y FE-01 sin riesgo de subirlos al repositorio.
- **readme:**
  - sección 1.4: el seed ya existe;
  - sección 3: solo si el esquema migrado obliga a corregir algo del diagrama.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
_Ninguna._ El esquema es soporte interno: no añade ni cambia peticiones, respuestas ni pantallas de ninguna spec, así que el change declara `skip_specs: true`. Sus tests prueban restricciones de la BD, que la sección 2.6 lista como "casos de arquitectura que no salen de ningún escenario". Por eso no citan escenarios y la lista de pendientes de trazabilidad no cambia.

## Fuera de alcance

- **`RepositorioCartera` y `CachePrecios`:** la sustitución de la cartera con `pg_advisory_xact_lock` llega con BE-01b y las escrituras de la caché con BE-02.
- **Las sesiones de BD inyectadas en FastAPI:** llegan con BE-01b.
- **Cualquier endpoint.**
- **Que el seed lea `cartera-ejemplo.xlsx`:** llega con BE-08.
- **El botón de subida de ficheros en el frontend:** es el control de carga de la spec `importacion-cartera` y llega con FE-01.
- **`pytest-randomly`:** lo cita la sección 2.6, pero no es necesario para el esquema.

## Impact

- **Ficheros nuevos:**
  - `backend/app/infrastructure/db/modelos.py` y `session.py`;
  - `backend/alembic/versions/<rev>_esquema_inicial.py`;
  - `backend/app/scripts/seed.py`;
  - `backend/tests/integration/conftest.py` y los tests del esquema y del seed.
- **Ficheros modificados:**
  - `backend/alembic/env.py`;
  - `backend/pyproject.toml` y `uv.lock`;
  - `.gitignore`;
  - `readme.md`.
- **Dependencias:** `testcontainers[postgres]` en el grupo de desarrollo. Ninguna nueva en producción.
- **CI:** `backend-tests` pasa a arrancar un contenedor PostgreSQL con el Docker del runner de GitHub, unos 10-20 s más.
- **Compose:** el servicio `migrate` crea ya las tablas en `up`.

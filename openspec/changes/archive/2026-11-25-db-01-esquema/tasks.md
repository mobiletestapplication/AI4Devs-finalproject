# Tasks

Ticket DB-01 (ticket 1 de la sección 6, Entrega 2), soporte de HU-1..HU-5. D1-D8 remiten a design.md. El esquema no implementa escenarios de las specs, así que las tareas no citan identificadores `capability::Requirement::Scenario` y la lista de pendientes de trazabilidad no cambia. Todas cumplen la Definition of Done común de la sección 6 del readme. La DoD específica es que el diagrama 3.1 coincida con el esquema migrado.

## 1. DevOps (HU-1..HU-5)

- [x] 1.1 Añadir `testcontainers[postgres]` al grupo de desarrollo de `backend/pyproject.toml` y regenerar `uv.lock`. Verificar con `uv sync --frozen` en limpio y `uv run pip-audit` sin vulnerabilidades.
- [x] 1.2 Añadir `datos-locales/` al `.gitignore` de la raíz (D8). Verificar que, con un `datos-locales/prueba.xlsx`, `git status --porcelain` no lo muestra y `git check-ignore -v` lo atribuye a la nueva regla.

## 2. Base de datos (HU-1..HU-5)

- [x] 2.1 Crear `app/infrastructure/db/modelos.py` (D1 y D3) con estos elementos:
  - `Base` con la convención de nombres;
  - los 5 modelos con `Mapped[...]`, `Numeric(18, 6, asdecimal=True)`, `Date`, `DateTime(timezone=True)` con `server_default=func.now()`, `CHAR(64)` y `String(10)`;
  - `default=uuid.uuid4` en los identificadores (D4);
  - las FK con `ondelete` (`CASCADE` en `POSICION` y `RESTRICT` en `CARTERA_VIGENTE`), los UNIQUE y los índices;
  - los CHECK con los nombres del diagrama del design.

  Verificar con `uv run mypy` y `uv run lint-imports` en verde y con `grep -n float` sin resultados en el módulo.
- [x] 2.2 Crear `app/infrastructure/db/session.py` con `crear_motor(ajustes)` y `crear_fabrica_sesiones(motor)` (D7), sin estado global. Verificar con `uv run mypy` y con que `python -c "import app.infrastructure.db.session"` no abre ninguna conexión, aunque `DATABASE_URL` apunte a un host inexistente.
- [x] 2.3 En `alembic/env.py`, sustituir `target_metadata = None` por `Base.metadata` y activar `compare_type=True` y `compare_server_default=True`. Generar la revisión `esquema_inicial` con `alembic revision --autogenerate` contra un PostgreSQL vacío y revisarla a mano: CHECK con nombre, `server_default`, orden de creación y `downgrade` que elimina las 5 tablas.

  Verificar con `alembic upgrade head`, `alembic check` sin diferencias y `alembic downgrade base` en el PostgreSQL de `docker compose`.
- [x] 2.4 Crear `app/scripts/seed.py` (D6), ejecutable con `python -m app.scripts.seed`. En una sola transacción inserta la importación, las 3 posiciones y la cartera vigente, y no hace nada si ya existe la cartera vigente. Verificar a mano con `docker compose exec api python -m app.scripts.seed` dos veces seguidas:
  - la primera crea 3 posiciones;
  - la segunda informa de que ya hay cartera;
  - las dos terminan con código 0.

## 3. Tests (HU-1..HU-5)

- [x] 3.1 Crear `tests/integration/conftest.py` con las fixtures `postgres`, `bd_migrada` y `sesion` de D5. Verificar con un test que lista las tablas de `information_schema` y encuentra exactamente las 5 tablas más `alembic_version`.
- [x] 3.2 Tests de migración:
  - `upgrade head`, `downgrade base` y otra vez `upgrade head` funcionan en una base de datos nueva del contenedor;
  - tras `upgrade head`, la comparación de Alembic entre `Base.metadata` y la BD no devuelve diferencias (D2).

  Verificar con `uv run pytest tests/integration -k migracion`.
- [x] 3.3 Un test por restricción, todos esperando `IntegrityError` con el `constraint_name` de cada caso:
  - cantidad 0;
  - precio de compra −1;
  - venta sin precio;
  - venta anterior a la compra;
  - fila 1;
  - ticker `aapl$` en `POSICION` y en `PRECIO_DIARIO`;
  - `maximo < minimo`;
  - `fuente` desconocida;
  - `hasta < desde`;
  - una segunda fila en `CARTERA_VIGENTE`, con `id = false` (falla por `ck_cartera_vigente_una_fila`) y con `id = true` (falla por la PK);
  - `UNIQUE (importacion_id, fila)` repetido;
  - borrar la importación vigente, que falla por `RESTRICT`.

  Además:
  - borrar una importación no vigente elimina sus posiciones (`CASCADE`);
  - una fila válida de cada tabla se inserta sin error.

  Verificar con `uv run pytest tests/integration -k restricciones`.
- [x] 3.4 Tests de tipos (D3):
  - 0,1 se guarda y se lee como `Decimal('0.100000')`;
  - 0,1234567 se lee como `Decimal('0.123457')`, el redondeo silencioso que documenta que el rechazo es de la aplicación;
  - las fechas se leen como `datetime.date`.

  Verificar con `uv run pytest tests/integration -k tipos`.
- [x] 3.5 Tests del seed contra la BD del contenedor, sin `docker compose`:
  - la primera ejecución crea 1 importación, 3 posiciones (2 abiertas y 1 cerrada) y la cartera vigente;
  - la segunda no cambia nada y termina con código 0.

  Verificar con `uv run pytest tests/integration -k seed`.
- [x] 3.6 Verificar la calidad completa del backend, todo en verde:
  - `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` y `uv run lint-imports`;
  - `uv run pytest --cov=app --cov-fail-under=85`;
  - el script de trazabilidad sin cambios en la lista de pendientes.

## 4. DevOps: compose y CI (HU-1..HU-5)

- [x] 4.1 Con `docker compose -f compose.yaml up -d --build` sobre un volumen nuevo, verificar que:
  - `migrate` termina con código 0;
  - `\dt` en `db` muestra las 5 tablas;
  - `\d posicion` muestra los CHECK con los nombres del design.

  Repetir con el volumen existente de OPS-01 (sin `down -v`) para comprobar que la migración se aplica sobre él.
- [x] 4.2 Subir la rama y comprobar que el CI queda en verde en GitHub, con el contenedor de Testcontainers arrancando en `backend-tests`. Verificar con `gh run view`.

## 5. Documentación (HU-1..HU-5)

- [x] 5.1 Actualizar el readme:
  - **Sección 1.4:** el seed pasa de "pendiente" a disponible, con su comando y la advertencia de que no sustituye una cartera existente; se añade `datos-locales/` para los XLSX de prueba manual.
  - **Sección 2.3:** `.gitignore` incluye `datos-locales/`.
  - **Sección 3:** si el esquema migrado difiere del diagrama 3.1 por una razón técnica, se corrige el diagrama y se explica en design.md.

  Verificar comparando la salida de `\d` de las 5 tablas con el diagrama 3.1 (DoD específica) y con `openspec validate db-01-esquema --strict`.

## Workflow follow-up

- Archivar con `/opsx:archive` cuando el CI esté en verde. Al no tener deltas, no modifica las specs vivas.
- Siguiente ticket: SEC-01 (`sec-01-seguridad-api`).

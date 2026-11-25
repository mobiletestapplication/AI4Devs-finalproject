# Tasks

Ticket OPS-01 (Entrega 2), transversal a HU-1..HU-5. O1-O7 remiten a design.md. Ninguna tarea implementa escenarios de las specs vivas, así que no citan identificadores `capability::Requirement::Scenario`; cumplen la Definition of Done común de la sección 6 del readme.

## 1. DevOps: raíz del repositorio (HU-1..HU-5)

- [x] 1.1 Crear `.gitignore` (Python, uv, Node, Vite, coberturas, `.env`) y `.dockerignore` en `backend/` y `frontend/`. Verificar con `git status --ignored` tras crear un `.env` y un `node_modules/` de prueba que ninguno aparece como pendiente.
- [x] 1.2 Crear `.env.example` con `POSTGRES_USER`, `POSTGRES_PASSWORD` (vacía), `POSTGRES_DB`, `DATABASE_URL`, `HOSTS_ADMITIDOS`, `ORIGENES_ADMITIDOS`, `PROVEEDOR_PRECIOS=yfinance`, `BENCHMARK_TICKER=SPY` y `LLM_API_KEY=` (vacía), cada una con un comentario de una línea. Verificar que coincide con la lista de la sección 2.4 del readme más las dos variables de O3 y que no contiene ningún valor secreto.

## 2. Backend: proyecto y configuración (HU-1..HU-5)

- [x] 2.1 Crear `backend/pyproject.toml` con uv para Python 3.12: dependencias FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2, Alembic y psycopg; grupo de desarrollo con pytest, pytest-cov, httpx, ruff, mypy, import-linter, pip-audit y bandit; configuración de ruff, mypy (estricto en `app/`) y pytest. Generar `uv.lock`. Verificar con `uv sync --frozen` en limpio.
- [x] 2.2 Crear los paquetes de la sección 2.3 con `__init__.py` (`api/routers`, `application`, `domain/indicadores`, `domain/estrategias`, `adapters/{xlsx,precios,indicadores,llm}`, `infrastructure/db`, `recursos/precios-demo`, `scripts`) y `tests/{unit,contract,integration,fixtures}`. Verificar que `python -c "import app.domain, app.adapters, app.infrastructure"` funciona.
- [x] 2.3 Implementar `app/infrastructure/config.py` con `Ajustes` (O3) y sus tests unitarios: valores por defecto, listas separadas por comas, `HOSTS_ADMITIDOS` vacía → error, `PROVEEDOR_PRECIOS` desconocido → error y `LLM_API_KEY` que no se muestra al convertir los ajustes a texto. Verificar con `uv run pytest tests/unit`.
- [x] 2.4 Implementar `app/main.py` con FastAPI, `docs_url="/api/docs"` y `openapi_url="/api/openapi.json"` (O1), cargando `Ajustes` al arrancar, y un test con `TestClient` que espera `200` en las dos rutas. Verificar con `uv run pytest tests/integration`.
- [x] 2.5 Inicializar Alembic en `backend/alembic/` leyendo `DATABASE_URL` de `Ajustes`, sin migraciones. Verificar que `uv run alembic upgrade head` termina con código 0 contra un PostgreSQL local de prueba.
- [x] 2.6 Añadir los contratos de import-linter de O4. Verificar con `uv run lint-imports` en verde y comprobar que falla al añadir temporalmente `import fastapi` en `app/domain/__init__.py` (y revertirlo).
- [x] 2.7 Verificar la calidad del backend con `uv run ruff check`, `uv run ruff format --check`, `uv run mypy app` y `uv run pytest --cov=app --cov-fail-under=85`, todo en verde.

## 3. Frontend: proyecto (HU-1..HU-5)

- [x] 3.1 Crear `frontend/` con Vite + React 18 + TypeScript estricto, `package-lock.json` y la estructura `src/{app,features/{cartera,rentabilidad,estrategias,backtesting,recomendaciones},shared/{api,ui}}` y `e2e/`. Una página de marcador de posición con el nombre trAIde y el aviso "Las señales son orientativas y no constituyen asesoramiento financiero". Verificar con `npm ci && npm run build`.
- [x] 3.2 Configurar el proxy de `/api` a `http://localhost:8000` en `vite.config.ts` (modo desarrollo, O1). Verificar con `npm run dev` y la API arrancada que `http://localhost:5173/api/docs` responde.
- [x] 3.3 Configurar ESLint (flat config) con TypeScript, React y `import/no-restricted-paths` con una zona por feature (O4). Verificar que `npm run lint` pasa y que falla al importar temporalmente `features/cartera` desde `features/rentabilidad` (y revertirlo).
- [x] 3.4 Configurar Vitest con Testing Library y un test que renderiza la página y encuentra el aviso legal. Verificar con `npm run test -- --run` y `npx tsc --noEmit`.

## 4. DevOps: contenedores (HU-1..HU-5)

- [x] 4.1 Crear `backend/Dockerfile` multi-etapa (O5): uv con versión fijada, `uv sync --frozen --no-dev`, usuario sin privilegios, Uvicorn en el 8000. Verificar con `docker build backend` y `docker run --rm <imagen> id -u` distinto de 0.
- [x] 4.2 Crear `frontend/Dockerfile` multi-etapa y `frontend/nginx.conf` (O5): puerto 8080, proxy de `/api` a `api:8000`, `client_max_body_size 6m`, CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `autoindex off` y *fallback* a `index.html`. Verificar con `docker build frontend`.
- [x] 4.3 Crear `compose.yaml` (modo demo) con `db`, `migrate`, `api` y `web` (O5): healthchecks (O2), `depends_on` con `service_healthy` y `service_completed_successfully`, volumen `pgdata`, `image:` y `build:` en los servicios construidos y solo `127.0.0.1:8080:8080` publicado. Verificar con `docker compose -f compose.yaml config` y `docker compose -f compose.yaml up -d --build`: `migrate` termina con código 0, `api` queda `healthy`, `http://localhost:8080/` sirve la página y `http://localhost:8080/api/docs` responde `200`.
- [x] 4.4 Crear `compose.override.yaml` (modo desarrollo): Vite en `127.0.0.1:5173`, `uvicorn --reload` con el código montado en `127.0.0.1:8000`, `db` en `127.0.0.1:5432` y `ORIGENES_ADMITIDOS` con el 5173. Verificar con `docker compose up -d` que un cambio en `app/main.py` recarga la API y que `docker compose port` no muestra ningún puerto en `0.0.0.0`.
- [x] 4.5 Comprobar que `docker compose down` conserva `pgdata` y que `down -v` lo elimina. Verificar con `docker volume ls` antes y después.

## 5. DevOps: CI (HU-1..HU-5)

- [x] 5.1 Crear `.github/workflows/ci.yml` con los jobs `openspec`, `backend-calidad`, `backend-tests`, `frontend` y `seguridad` de O6: push y pull request a `main`, `concurrency` con cancelación, caché de uv y npm, `permissions: contents: read` y acciones fijadas por SHA. Verificar ejecutando en local los mismos comandos de cada job, todos en verde.
- [x] 5.2 Crear `.github/dependabot.yml` para `github-actions`, `pip` (en `backend/`) y `npm` (en `frontend/`), semanal. Verificar que el YAML es válido.
- [x] 5.3 Subir la rama y comprobar que el workflow se ejecuta en GitHub con los cinco jobs en verde. Verificar con `gh run list --branch feature/entrega-2-sg` y `gh run view`.

## 6. Documentación (HU-1..HU-5)

- [x] 6.1 Actualizar la sección 1.4 del readme quitando "No requerido en la Entrega 1 / Previsto" y dejando los pasos que se han comprobado en 4.3-4.5; indicar que el seed llega con DB-01. Verificar que cada comando de la sección se ha ejecutado con éxito.
- [x] 6.2 Comprobar que las secciones 2.3 (árbol) y 2.4 (servicios, variables y jobs) del readme coinciden con lo construido; si algo difiere por una razón técnica, actualizar el readme y explicarlo en design.md. Añadir `HOSTS_ADMITIDOS` y `ORIGENES_ADMITIDOS` a la lista de `.env.example` de la sección 2.4. Verificar con `openspec validate ops-01-esqueleto --strict`.

## Workflow follow-up

- Archivar con `/opsx:archive` cuando el CI esté en verde; al no tener deltas, no modifica las specs vivas.
- Siguiente ticket: DB-01 (esquema y migraciones), que depende de este.

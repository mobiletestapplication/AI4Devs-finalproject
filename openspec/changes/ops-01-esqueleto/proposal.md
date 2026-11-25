# Proposal

## Why

El repositorio solo contiene documentación: no hay estructura de código, dependencias, contenedores ni CI. Todos los tickets de la Entrega 2 dependen de OPS-01 (backlog de la sección 6 del readme), así que es el primero: deja un esqueleto que arranca con `docker compose`, pasa el CI y sobre el que DB-01, SEC-01 y el resto solo añaden código.

Cubre el ticket **OPS-01** de la Entrega 2, transversal a las features **F1-F5** y a las historias **HU-1 a HU-5**.

## What Changes

- **Estructura del repositorio** de la sección 2.3 del readme: `backend/` (capas `api`, `application`, `domain`, `adapters`, `infrastructure`, `recursos`, `scripts`, `tests`) y `frontend/` (`app`, `features`, `shared`, `e2e`), con paquetes vacíos donde aún no hay código.
- **Backend mínimo:** proyecto uv (`pyproject.toml` + `uv.lock`) con Python 3.12; aplicación FastAPI vacía con la documentación en `/api/docs`; configuración por entorno con los hosts y orígenes admitidos; Alembic inicializado sin migraciones.
- **Fronteras de arquitectura:** contratos de import-linter en el backend y `import/no-restricted-paths` en ESLint del frontend, en verde desde el primer commit.
- **Frontend mínimo:** Vite + React 18 + TypeScript con una página de marcador de posición y el proxy de `/api` del modo desarrollo.
- **Contenedores:** `compose.yaml` (modo demo) con `db`, `migrate`, `api` y `web` (nginx), y `compose.override.yaml` (modo desarrollo); puertos solo en `127.0.0.1`.
- **`.env.example`** sin secretos y **`.gitignore`**.
- **CI de GitHub Actions** con los jobs `openspec`, `backend-calidad`, `backend-tests`, `frontend` y `seguridad`.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
_Ninguna._ El esqueleto no implementa ningún requisito de las specs vivas ni añade comportamiento observable que deba especificarse; el change declara `skip_specs: true`.

## Fuera de alcance

- Esquema de BD y migraciones (DB-01).
- Middleware de `Host`, `Origin`, rate limiting y formato de errores (SEC-01); aquí solo se definen y validan las variables de configuración.
- Cualquier endpoint de negocio (BE-01a en adelante).
- Script de trazabilidad, E2E con Playwright y su job de CI (QA-01).
- Job de release y publicación en GHCR (REL-01).
- Dependencias de tickets posteriores (openpyxl, yfinance, TA-Lib, slowapi…): cada ticket añade las suyas.

## Impact

- **Ficheros nuevos:** `backend/`, `frontend/`, `compose.yaml`, `compose.override.yaml`, `.env.example`, `.gitignore`, `.github/workflows/ci.yml`.
- **Dependencias:** backend con FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2, Alembic y psycopg; desarrollo con pytest, httpx, ruff, mypy, import-linter, pip-audit y bandit. Frontend con React 18, Vite, TypeScript, ESLint y Vitest.
- **API:** solo la documentación autogenerada en `/api/docs`; ningún endpoint de las specs.
- **readme.md:** sección 1.4 (instalación) cuando el arranque funcione de verdad; las secciones 2.3 y 2.4 ya describen la estructura y la infraestructura y no deberían cambiar.

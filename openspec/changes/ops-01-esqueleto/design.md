# Design

## Context

Ver proposal.md (Why). El repositorio solo tiene `openspec/`, `readme.md`, `prompts.md` y `.claude/`. Las decisiones que este ticket materializa ya están tomadas en las secciones 2.3 (estructura y reglas de dependencias), 2.4 (compose, CI) y 2.5 (nginx, puertos, hosts y orígenes) del readme; este design solo fija cómo se concretan en un esqueleto sin código de negocio. Herramientas locales disponibles: Docker 29 con Compose v5, uv 0.12, Node 24, Python 3.12 y el CLI `@fission-ai/openspec` 1.14.

## Goals / Non-Goals

**Goals:**
- `docker compose -f compose.yaml up -d --build` arranca los cuatro servicios en orden y `http://localhost:8080/api/docs` responde.
- El CI queda en verde con un esqueleto vacío, y cada ticket posterior solo añade código, tests y dependencias.
- Las fronteras de arquitectura se comprueban desde el primer commit, no cuando ya hay código que las incumple.

**Non-Goals:**
- Cualquier lógica de negocio, endpoint de las specs, tabla o middleware de seguridad.
- Optimizar el tamaño o el tiempo de build de las imágenes más allá del multi-etapa.

## Decisions

### O1. La API sirve bajo `/api` sin reescritura en nginx
FastAPI se crea con `docs_url="/api/docs"` y `openapi_url="/api/openapi.json"`, y los routers futuros llevan el prefijo `/api`. nginx y el proxy de Vite reenvían `/api` tal cual.
- **Alternativa descartada:** que nginx quite el prefijo. Las rutas de los tests, del OpenAPI y del navegador serían distintas.

### O2. Healthcheck de la API sin endpoint nuevo
El healthcheck de `api` pide `/api/openapi.json` con el Python de la propia imagen. `db` usa `pg_isready`. `web` no necesita healthcheck propio.
- **Alternativa descartada:** un endpoint `/api/salud`. Sería comportamiento observable que ninguna spec define y obligaría a añadir un delta.

### O3. Configuración por entorno con Pydantic Settings
`infrastructure/config.py` define una clase `Ajustes` que lee del entorno:
- `DATABASE_URL`;
- `HOSTS_ADMITIDOS` (por defecto `localhost,127.0.0.1`);
- `ORIGENES_ADMITIDOS` (por defecto `http://localhost:8080,http://127.0.0.1:8080`; el modo desarrollo añade `http://localhost:5173`);
- `PROVEEDOR_PRECIOS` (`yfinance` o `ficheros`) y `BENCHMARK_TICKER` (`SPY`), validados aunque aún no los use nadie;
- `LLM_API_KEY` como `SecretStr`, para que nunca aparezca en un log.

La aplicación no arranca si `HOSTS_ADMITIDOS` queda vacía o si `PROVEEDOR_PRECIOS` tiene otro valor (comprobación al arrancar de la sección 2.5). SEC-01 usará estos valores en sus middlewares.
- **Alternativa descartada:** leer `os.environ` en cada módulo. Dispersa la validación y no permite fallar al arrancar.

### O4. Contratos de import-linter desde el principio
En `backend/pyproject.toml`:
- **capas:** `app.api` → `app.application` → `app.domain`;
- **prohibido:** `app.domain` no importa `app.api`, `app.application`, `app.adapters` ni `app.infrastructure`, ni `fastapi` ni `sqlalchemy`;
- **prohibido:** `app.adapters` e `app.infrastructure` no importan `app.api`.

Con `include_external_packages = true`, import-linter solo puede prohibir paquetes instalados, así que `yfinance`, `openpyxl` y `talib` se añaden a la lista prohibida del dominio en el ticket que instala cada uno.

En el frontend, ESLint `import/no-restricted-paths` con una zona por cada feature (`cartera`, `rentabilidad`, `estrategias`, `backtesting`, `recomendaciones`) que prohíbe importar desde las otras cuatro.

### O5. Imágenes y compose
- **`api`:** multi-etapa `python:3.12-slim` con el binario de uv copiado de su imagen oficial con versión fijada; `uv sync --frozen --no-dev` en la etapa de build; usuario sin privilegios; `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- **`migrate`:** la misma imagen con `alembic upgrade head`; arranca cuando `db` está sano y `api` espera a `service_completed_successfully`. Sin migraciones, el comando termina bien.
- **`web`:** etapa `node:24-alpine` con `npm ci` y `npm run build`, y etapa final `nginxinc/nginx-unprivileged` en el puerto 8080 con `client_max_body_size 6m`, proxy de `/api` a `api:8000`, cabeceras CSP, `X-Content-Type-Options: nosniff` y `Referrer-Policy`, y `autoindex off`.
- **`db`:** `postgres:16` con etiqueta de versión menor fijada, volumen `pgdata` y sin puerto publicado en el modo demo.
- **Puertos:** solo `127.0.0.1:8080:8080` en el modo demo. `compose.override.yaml` añade `127.0.0.1:5173` (Vite), `127.0.0.1:8000` (`uvicorn --reload` con el código montado) y `127.0.0.1:5432`.
- Cada servicio construido declara `image:` (`ghcr.io/<owner>/traide-api` y `traide-web`) y `build:`, para que REL-01 solo tenga que publicar.

### O6. CI con los jobs que ya tienen contenido
`.github/workflows/ci.yml` en push y pull request a `main`, con `concurrency` que cancela ejecuciones anteriores de la misma rama, caché de uv y npm, permisos `contents: read` y acciones fijadas por SHA:
| Job | Qué ejecuta en este ticket |
|---|---|
| `openspec` | `npx @fission-ai/openspec@1.14.3 validate --specs --strict` y `validate --changes --strict` |
| `backend-calidad` | `uv sync --frozen`, `ruff check`, `ruff format --check`, `mypy`, `lint-imports` |
| `backend-tests` | `pytest` con cobertura (`--cov-fail-under=85`) |
| `frontend` | `npm ci`, `eslint`, `tsc --noEmit`, `vitest run`, `vite build` |
| `seguridad` | `pip-audit` sobre `uv export`, `npm audit --audit-level=high`, `gitleaks`, `bandit -r app` |

`e2e` y el script de trazabilidad llegan con QA-01, y `release` con REL-01. La comprobación de que los tipos generados desde el OpenAPI están al día llega con FE-01, cuando exista el cliente.
- **Alternativa descartada:** crear ya los jobs vacíos. Un job que no comprueba nada da una falsa sensación de cobertura.

### O7. Tests del esqueleto
- **Unitarios:** `Ajustes` con valores por defecto, listas separadas por comas, `HOSTS_ADMITIDOS` vacía → error y `PROVEEDOR_PRECIOS` desconocido → error.
- **Integración ligera:** con el `TestClient` de FastAPI, `/api/openapi.json` y `/api/docs` responden `200`.
- **Frontend:** un test de Vitest que renderiza la página de marcador de posición.
- **Comprobación manual del compose:** arranque en modo demo, `migrate` termina con código 0 y `http://localhost:8080/api/docs` responde.

Ninguno cita escenarios de las specs, porque el ticket no implementa ninguno; el script de trazabilidad (QA-01) no los exigirá.

## Risks / Trade-offs

- [import-linter falla si un contrato nombra un paquete vacío o no instalado] → paquetes con `__init__.py` y lista de externos prohibidos ampliada en cada ticket (O4).
- [`npm audit` o `pip-audit` encuentran una vulnerabilidad en una dependencia transitiva y bloquean el primer CI] → se actualiza la dependencia; si no hay versión corregida, se documenta la excepción en el propio workflow con fecha de revisión.
- [gitleaks marca como secreto un valor de ejemplo] → `.env.example` sin valores en las claves sensibles y la contraseña de desarrollo solo en `.env`, que está en `.gitignore`.
- [Las acciones fijadas por SHA quedan desactualizadas] → Dependabot para `github-actions`, `pip` (uv) y `npm`.
- [El primer `docker compose up` es lento] → caché de capas por etapa y `uv sync` antes de copiar el código.

## Migration Plan

No hay nada desplegado. El rollback es revertir el commit; no hay datos que migrar.

# Tasks

Ticket QA-01, parte 1 (Entrega 2), transversal a HU-1..HU-5. T1-T6 remiten a design.md. Ninguna tarea implementa escenarios de las specs vivas, así que no citan identificadores `capability::Requirement::Scenario`. Todas cumplen la Definition of Done común de la sección 6 del readme.

## 1. Tests: script de trazabilidad (HU-1..HU-5)

- [x] 1.1 Implementar en `backend/tests/trazabilidad.py` la lectura de escenarios:
  - de las specs vivas;
  - de los deltas `ADDED` y `MODIFIED` de los changes activos, sin entrar en `archive/`;
  - con la regla 7: nombres con `::`, ` > ` o ` — ` e identificadores repetidos.

  Verificar con tests unitarios en `tmp_path`:
  - una spec con 2 requisitos y 3 escenarios da 3 identificadores;
  - un nombre con `::` es un error;
  - un delta `ADDED` se lee y uno `REMOVED` no.
- [x] 1.2 Implementar la lectura de la lista de pendientes en TOML (T3) y la regla 6.

  Verificar con tests unitarios:
  - un ticket `be-01` es un error;
  - un identificador de dos partes es un error;
  - `capability::*` y `capability::Requirement::*` cubren los escenarios correctos.
- [x] 1.3 Implementar la recogida de citas de pytest (T1) y de Vitest (T2), con la marca `escenario` registrada en `backend/pyproject.toml`.

  Verificar con tests unitarios:
  - un JSON de `vitest list` con los títulos `"A > cap::Req::Esc — detalle"` y `"A > sin cita"` da una sola cita, `cap::Req::Esc`;
  - una marca sin argumentos es un error.
- [x] 1.4 Implementar las reglas 1-5 (T4), el resumen y el código de salida, con `difflib` para sugerir el escenario más parecido.

  Verificar con un test unitario por regla:
  - escenario sin test;
  - cita inexistente, con la sugerencia;
  - pendiente con test;
  - pendiente inexistente;
  - pendiente duplicado;
  - y un caso correcto que devuelve 0.
- [x] 1.5 Añadir el script a mypy estricto (T6). Verificar que `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` y `uv run pytest` pasan en verde.

## 2. Tests: lista de pendientes (HU-1..HU-5)

- [x] 2.1 Crear `backend/tests/escenarios_pendientes.toml` con la asignación de T5. Verificar que:
  - `uv run python tests/trazabilidad.py --vitest <json de vitest list>` termina con código 0;
  - el resumen indica 248 escenarios, 0 con test y 248 pendientes repartidos por ticket.
- [x] 2.2 Comprobar en local que el script detecta los fallos, revirtiendo cada cambio después:
  - con un test temporal marcado con un escenario pendiente, falla por la regla 3;
  - con un test temporal que cita `importacion-cartera::Formato del fichero::X`, falla por la regla 2 y sugiere un escenario existente;
  - al quitar una línea de la lista, falla por la regla 1.

## 3. DevOps: CI (HU-1..HU-5)

- [x] 3.1 Añadir al job `backend-calidad` de `.github/workflows/ci.yml`:
  - `setup-node` fijado por SHA, con caché de npm;
  - `npm ci` en `frontend/`;
  - `npx vitest list --json=$RUNNER_TEMP/vitest.json`;
  - `uv run python tests/trazabilidad.py --vitest $RUNNER_TEMP/vitest.json`.

  Verificar ejecutando en local la misma secuencia y con `actionlint` sin errores.
- [ ] 3.2 Subir la rama y comprobar que el CI queda en verde en GitHub, con `gh run view` y el paso de trazabilidad visible en `backend-calidad`.

## 4. Documentación (HU-1..HU-5)

- [x] 4.1 Actualizar el readme:
  - **Sección 2.4:** el script ya está en `backend-calidad`; el E2E llega con la parte 2 de QA-01.
  - **Sección 2.6:**
    - la ruta `backend/tests/trazabilidad.py`;
    - la lista de pendientes con su formato y sus reglas;
    - el argumento `--vitest`;
    - que se exige al menos un test por escenario.

  Verificar que el readme no contradice design.md y con `openspec validate qa-01-trazabilidad --strict`.

## Workflow follow-up

- Archivar con `/opsx:archive` cuando el CI esté en verde. Al no tener deltas, no modifica las specs vivas.
- Siguiente ticket: DB-01, el primero que retira escenarios de la lista de pendientes (si su design cita alguno) o al menos mantiene el script en verde.

# Proposal

## Why

La Definition of Done común (sección 6 del readme) exige un test por cada escenario citado y el script de trazabilidad en verde, pero el script no existe. Hay que tenerlo antes del primer ticket con tests de escenarios (DB-01 y SEC-01). Si no, la trazabilidad se comprobaría a mano y los escenarios sin test pasarían desapercibidos.

Además, con las specs completas y casi nada implementado, un script que exige un test por escenario dejaría el CI en rojo hasta el final de la Entrega 3. Hace falta una lista explícita de escenarios pendientes, cada uno con el ticket que lo cubrirá, que se vaya vaciando ticket a ticket.

Cubre la **parte 1 del ticket QA-01** (incremental, Entregas 2 y 3), transversal a las features **F1-F5** y **S3** (las especificadas) y a las historias **HU-1 a HU-5**.

## What Changes

- **Script `backend/tests/trazabilidad.py`**:
  - lee los escenarios de las specs vivas (`openspec/specs/**/spec.md`) y los de los deltas `ADDED` y `MODIFIED` de los changes activos;
  - lee las citas de los tests de pytest (marca `escenario`) y de Vitest (identificador al principio del título, desde el JSON de `vitest list`).
- **El script falla** si:
  - un escenario no tiene test ni está pendiente;
  - un test cita un escenario inexistente; en ese caso indica el más parecido;
  - un escenario pendiente ya tiene test;
  - la lista de pendientes cita un escenario o un patrón que no existe, o un mismo escenario aparece en dos tickets.
- **Lista de pendientes `backend/tests/escenarios_pendientes.toml`**, agrupada por ticket. Admite patrones con `*` por requisito o por capability. Al crearla cubre los 248 escenarios actuales, todos sin test.
- **Marca de pytest `escenario`** registrada en `pyproject.toml`; el modo `--strict-markers` ya rechaza las marcas mal escritas.
- **CI:** el job `backend-calidad` instala el frontend, genera la lista de tests de Vitest y ejecuta el script.
- **readme:** las secciones 2.4 y 2.6 describen la lista de pendientes y lo que llega con la parte 2.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
_Ninguna._ El script es herramienta de desarrollo y CI: no cambia ninguna petición, respuesta ni pantalla. Por eso el change declara `skip_specs: true`.

## Fuera de alcance

Quedan para la **parte 2 de QA-01**, junto con FE-01:
- el E2E con Playwright del flujo principal;
- el compose de tests con `PROVEEDOR_PRECIOS=ficheros` y `FECHA_ACTUAL_FIJA`;
- el job `e2e` del CI;
- la lectura del informe de Playwright en el script.

Tampoco entra:
- **El generador de fixtures maliciosos** `tests/fixtures/generar.py`. Lo crea BE-01a según el backlog; QA-01 solo vela por que los tests de seguridad lo usen.
- **Escribir tests de escenarios.** Cada ticket añade los suyos y retira sus escenarios de la lista de pendientes.
- **Exigir exactamente un test por escenario.** La sección 2.6 permite probar en dos niveles los escenarios HTTP que incluyen un cálculo, así que el script exige al menos uno.

## Impact

- **Ficheros nuevos:**
  - `backend/tests/trazabilidad.py`;
  - `backend/tests/escenarios_pendientes.toml`;
  - `backend/tests/unit/test_trazabilidad.py`.
- **Ficheros modificados:**
  - `backend/pyproject.toml`: marca `escenario`, y mypy también comprueba el script;
  - `.github/workflows/ci.yml`: job `backend-calidad`;
  - `readme.md`: secciones 2.4 y 2.6.
- **Dependencias:** ninguna nueva. Se usan `tomllib` y `difflib` de la biblioteca estándar, y pytest y Vitest, que ya están instalados.
- **Flujo de trabajo:** desde este change, cada ticket quita de la lista de pendientes los escenarios que pasa a cubrir, en el mismo commit que añade sus tests.

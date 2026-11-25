# Design

## Context

Ver proposal.md (Why). Estado de partida:
- OPS-01 dejó pytest con `--strict-markers` y `pythonpath=["."]`, Vitest 5 y el job `backend-calidad`, que trabaja en `backend/` con uv.
- La sección 2.6 del readme fija la convención de las citas: en pytest, la marca `escenario`; en Vitest y Playwright, el identificador al principio del título.
- Las 6 specs vivas tienen 248 escenarios. Ningún nombre contiene `::`, ` > ` ni ` — `.
- Hay nombres de escenario repetidos (por ejemplo, "Cartera importada"), pero siempre en requisitos distintos, así que el identificador completo `capability::Requirement::Scenario` es único.

## Goals / Non-Goals

**Goals:**
- Que el CI falle en cuanto un escenario quede sin test o sin ticket que lo cubra, y en cuanto un test cite un escenario que no existe.
- Que la lista de pendientes sea el registro único de lo que falta y de quién lo cubre, sin duplicar el backlog.

**Non-Goals:**
- Comprobar que el test prueba de verdad lo que dice el escenario. Eso queda para la revisión de código.
- Informes HTML o métricas de cobertura por escenario.

## Decisions

### T1. Recogida de pytest en el mismo proceso, con un plugin
El script llama a `pytest.main(["--collect-only", "-q", ...], plugins=[recolector])` con la salida redirigida a memoria. El recolector lee `item.iter_markers("escenario")` de cada test recogido.
- **Alternativa descartada:** analizar la salida de texto de `pytest --collect-only -q`, que no incluye las marcas.
- **Alternativa descartada:** buscar los decoradores con `ast`. Fallaría con las marcas aplicadas por `pytestmark` o por parametrización.
- **Sacrificio:** la recogida importa los módulos de test. Un error de importación hace fallar el script, que remite a `pytest --collect-only` para ver el detalle; ese test también fallaría en `backend-tests`.

### T2. Vitest mediante `vitest list --json`, sin ejecutar los tests
El CI genera el JSON con `npx vitest list --json=<fichero>` y lo pasa al script con `--vitest <fichero>`. Cada entrada trae `name` con la forma `describe > ... > título`. La cita se lee del último segmento:
- el identificador es el título completo o lo que va antes de ` — `;
- si contiene `::` y no es un escenario conocido, cuenta como cita inexistente.
- **Alternativa descartada:** el reporter `json` de `vitest run`. Obliga a ejecutar los tests en el job de calidad, que ya se ejecutan en `frontend`.
- **Sacrificio:** sin `--vitest`, los escenarios de pantalla que solo tengan test en Vitest aparecerían como "sin test". El argumento es opcional para poder ejecutar el script en local solo con el backend, y en el CI es obligatorio.

### T3. Formato de la lista de pendientes: TOML agrupado por ticket
```toml
[BE-01a]
escenarios = [
  "importacion-cartera::Rechazo de ficheros no válidos::Fichero que no es XLSX",
  "importacion-cartera::Rechazo de ficheros comprimidos peligrosos::*",
]
```
- **Por qué TOML:** se lee con `tomllib` de la biblioteca estándar, sin dependencias, y admite comentarios.
- **Clave de cada tabla:** el ticket del backlog. Se valida con el patrón `(OPS|DB|SEC|BE|FE|QA|REL)-NN` con sufijo opcional de una letra minúscula.
- **Patrones:** `capability::Requirement::*` y `capability::*`. Evitan listar 248 líneas y aguantan altas de escenarios en requisitos aún no empezados.
- **Alternativas descartadas:** JSON, que no admite comentarios; YAML, que necesita una dependencia; una marca `skip` en tests vacíos, que llenaría el código de tests falsos.

### T4. Reglas del script
Errores, todos acumulados en una sola ejecución:
1. **Escenario sin test ni pendiente.**
2. **Cita inexistente:** un test cita un identificador que no está en las specs vivas ni en los deltas `ADDED` o `MODIFIED` de un change activo. El mensaje incluye el identificador más parecido, con `difflib.get_close_matches`.
3. **Pendiente con test:** un escenario cubierto por la lista de pendientes ya tiene test. Si estaba cubierto por un patrón, el ticket que lo prueba debe sustituir el patrón por los escenarios que siguen pendientes.
4. **Pendiente inexistente:** la lista cita un escenario que no existe o un patrón que no coincide con ninguno.
5. **Pendiente duplicado:** un mismo escenario aparece en dos entradas de la lista.
6. **Ticket o identificador mal formado:** la clave del ticket no sigue el patrón, el identificador no tiene tres partes o una marca `escenario` no lleva texto.
7. **Nombre ambiguo en una spec:** un nombre de requisito o escenario contiene `::`, ` > ` o ` — `, o un identificador está repetido.

Salida:
- **Si todo está bien:** un resumen con el total de escenarios, los que tienen test y los pendientes por ticket, y código de salida 0.
- **Si hay errores:** se listan agrupados por regla, con código de salida 1.

Los escenarios de los deltas de changes activos **se pueden citar, pero no se exigen**: el readme dice que al aplicar un change se añaden los tests de sus deltas y que al archivarlo el script los exige.
- **Sacrificio:** un `REMOVED` de un change activo sigue exigiéndose hasta archivar. Su test se borra en el mismo commit del archivado.

### T5. Asignación inicial de los escenarios a tickets
La asignación sigue el backlog de la sección 6 y los criterios de aceptación de los tickets 1-3:

| Ticket | Qué cubre |
|---|---|
| BE-01a | De `importacion-cartera`: "Fichero que no es XLSX", "Fichero demasiado grande", los comprimidos peligrosos y el contenido activo |
| BE-01b | El resto de los rechazos y del formato del fichero, tal como los cita el ticket 2 |
| BE-07 | Consulta de posiciones, precio de referencia, rendimiento total y clasificación de la plusvalía |
| FE-01 | Carga en pantalla, Watchlist y "Marcado en una celda" |
| BE-08 y FE-06 | Resumen y ejemplo |
| BE-03 y FE-02 | `rentabilidad-twr`: API y panel |
| BE-04 y FE-03 | `estrategias-indicador`: API y pantalla |
| BE-05 y FE-04 | `backtesting`: API y pantalla |
| BE-06 y FE-05 | `operaciones-recomendadas`: API y pantalla |

Los escenarios de `seguridad-api` van al ticket que crea el endpoint que nombra su WHEN:
- **SEC-01:** solo los rechazos que el middleware resuelve antes del enrutado, "DNS rebinding" e "Importación desde otra web". Responden `400` o `403` sin necesitar la ruta.
- **BE-01b:** la importación aceptada y la sexta importación.
- **BE-07:** las consultas sin límite.
- **BE-04:** "Host local" y el periodo `abc`.
- **BE-05:** el cliente sin navegador y el campo no admitido.
- **BE-03:** la excepción en la TWR.
- **FE-04:** "Límite en pantalla".

Así cada test ejercita la petición que describe el escenario y no una ruta de prueba. Cada ticket puede reasignar sus pendientes en su propio change si su design lo justifica.

### T6. Ubicación y comprobación del script
El script está en `backend/tests/trazabilidad.py`, como dice el readme, y se ejecuta con `uv run python tests/trazabilidad.py`.
- **Tests:** sus funciones puras (lectura de specs, lectura de pendientes y reglas) se prueban en `tests/unit/test_trazabilidad.py` con specs y listas en memoria o en `tmp_path`. Esos tests no citan escenarios, porque prueban una herramienta y no comportamiento de la aplicación.
- **mypy:** la configuración pasa de `packages = ["app"]` a `files = ["app", "tests/trazabilidad.py"]`, porque mypy no admite combinar `packages` y `files`; el resultado sobre `app/` es el mismo.
- **Cobertura:** sigue midiéndose solo sobre `app/`. El script no entra en la cobertura, pero sí en mypy y en ruff.

## Risks / Trade-offs

- **[Riesgo] Un patrón `*` oculta escenarios nuevos añadidos a un requisito ya empezado.** → La regla 3 obliga a sustituir el patrón por los escenarios pendientes concretos en cuanto aparece el primer test de ese requisito, y a partir de ahí un escenario nuevo falla por la regla 1.
- **[Riesgo] Se olvida pasar `--vitest` en local** y salen falsos "sin test". → El resumen avisa de que no se ha leído ningún informe de Vitest, y el CI siempre lo pasa.
- **[Sacrificio] `backend-calidad` instala ahora Node y las dependencias del frontend:** unos 20-30 s más con la caché de npm.
- **[Riesgo] La salida redirigida oculta los errores de importación.** → Si el código de salida no es 0 ni 5 (ningún test), el script se detiene y muestra la salida de la recogida.

## Ajustes durante la implementación

- **Recogida de pytest:** `-p no:terminal` impedía usar el `-ra` de `addopts` (lo define el plugin de terminal), así que el script mantiene el plugin y redirige la salida a memoria con `contextlib.redirect_stdout`.
- **mypy:** `files` en lugar de `packages` (ver T6).
- **Sugerencia del escenario más parecido:** `difflib` compara el identificador completo, así que con una errata en el requisito puede proponer otro requisito de la misma capability. Basta como pista; el mensaje siempre muestra la cita exacta.

## Migration Plan

1. Al aplicar, la lista de pendientes cubre los 248 escenarios y el script queda en verde.
2. Desde DB-01, cada change que añada tests quita sus escenarios de la lista en el mismo commit.
3. Rollback: basta con quitar el paso del CI.

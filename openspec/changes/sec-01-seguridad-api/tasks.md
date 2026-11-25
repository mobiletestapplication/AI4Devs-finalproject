# Tasks

Ticket SEC-01 (Entrega 2), transversal a HU-1..HU-5. S1-S8 remiten a design.md. Las tareas de código citan los escenarios que cubren con `capability::Requirement::Scenario`. Los que nombran rutas que aún no existen quedan en la lista de pendientes con su ticket (design, tabla de asignación). Todas cumplen la Definition of Done común de la sección 6 del readme.

## 1. Tests: trazabilidad (HU-1..HU-5)

- [x] 1.1 En `backend/tests/trazabilidad.py`, que los pendientes puedan coincidir con escenarios de deltas activos, aplicándoles también la regla 3 (S8).

  Verificar con tests unitarios:
  - un pendiente que cita un escenario `ADDED` de un delta activo no da error;
  - el mismo pendiente con un test que lo cita falla por la regla 3;
  - un pendiente que no está en las specs ni en los deltas sigue fallando por la regla 4.
- [x] 1.2 Añadir a `backend/tests/escenarios_pendientes.toml` los escenarios nuevos según la tabla de asignación del design:
  - en BE-04, "Valor de la petición no repetido" y "Mensaje del proveedor con marcado";
  - en BE-07, los cinco de barras no válidas;
  - en FE-01, los tres de la comprobación en pantalla.

  Quitar de SEC-01 los que se prueban en este ticket. Verificar que el script termina con código 0 en cada paso del apply.

## 2. Backend: dependencias y registro (HU-1..HU-5)

- [x] 2.1 Añadir `limits` a las dependencias de producción, sin slowapi (S4), y regenerar `uv.lock`. Verificar con `uv sync --frozen`, con pip-audit sin vulnerabilidades y con que `slowapi` no aparece en `uv.lock`.
- [x] 2.2 Crear `app/infrastructure/registro.py` (S6):
  - formateador JSON;
  - filtro que oculta la contraseña de `DATABASE_URL` y `LLM_API_KEY`;
  - `registrar_descartes(ticker, descartes)`.

  Verificar con tests unitarios:
  - una línea de log es JSON válido con `nivel`, `mensaje` e `incidencia`;
  - un mensaje con la contraseña de la BD o la clave del LLM sale con `***`;
  - un descarte se registra con ticker, fecha y motivo, sin los valores recibidos.

## 3. Backend: errores y middlewares (HU-1..HU-5)

- [x] 3.1 Crear `app/api/errores.py` con el constructor de `problem+json` y los manejadores de S5: validación `400` con la tabla de motivos, `HTTPException` y `Exception` `500` con incidencia y cabeceras de seguridad.

  Verificar con tests de integración sobre `crear_app`, más rutas de prueba registradas solo en el test:
  - `seguridad-api::Formato común de los errores::Ruta inexistente`;
  - un parámetro `int` con el valor `<script>` da `400` sin el valor en el cuerpo, como base del escenario de BE-04;
  - un campo extra en un cuerpo con `extra="forbid"` da `400` "campo no admitido";
  - una excepción forzada da `500` con `incidencia` hexadecimal de 32 caracteres, sin traza ni ruta de fichero en el cuerpo, con la misma incidencia en el log y con las cabeceras de seguridad.
- [x] 3.2 Crear en `app/api/seguridad.py` el middleware de cabeceras (S5). Verificar con:
  - `seguridad-api::Cabeceras de seguridad de la API::Respuesta JSON de la API`;
  - `seguridad-api::Cabeceras de seguridad de la API::Respuesta de error`;
  - un test que comprueba que `/api/docs` lleva `nosniff` pero no CSP.
- [x] 3.3 Middleware de `Host` (S2). Verificar con:
  - `seguridad-api::Host admitido::DNS rebinding`;
  - `seguridad-api::Formato común de los errores::Host rechazado con el formato común`;
  - tests adicionales para `localhost:8080`, `LOCALHOST`, `127.0.0.1:8000` aceptados y `Host` ausente rechazado.
- [x] 3.4 Middleware de origen (S3). Verificar con:
  - `seguridad-api::Origen de las peticiones que envían datos::Importación desde otra web`, sobre `POST /api/cartera/importacion` sin ruta: el `403` llega antes del enrutado;
  - tests adicionales:
    - `Origin` admitido con una ruta de prueba → `200`;
    - sin `Origin` y con `Sec-Fetch-Site` `same-site` → `403`;
    - con `same-origin` → aceptado;
    - sin ninguna de las dos → aceptado;
    - `GET` con `Origin` ajeno → aceptado.
- [x] 3.5 Middleware de límite de frecuencia con `limits` y la tabla de S4. Verificar con una tabla de prueba que limita una ruta `POST` a 5 por minuto:
  - la sexta petición en un minuto recibe `429` en `problem+json` con `Retry-After` y `reintentar_en` enteros positivos;
  - en la sexta petición la ruta no se ejecuta ni lee el cuerpo, comprobado con un contador en la ruta;
  - una ruta que no está en la tabla admite 100 peticiones sin `429`;
  - la tabla real contiene `POST /api/cartera/importacion` 5/min y `POST /api/backtests` 10/min.
- [x] 3.6 Montar en `crear_app` el registro, los manejadores y los middlewares en el orden de S1. Verificar con:
  - un test de orden: `Host` ajeno + `Origin` ajeno da `400` y no `403`;
  - que los tests de `test_arranque.py` siguen en verde;
  - `uv run lint-imports` en verde.

## 4. Backend: datos del proveedor de mercado (HU-1..HU-5)

- [x] 4.1 Crear `BarraDiaria` en `app/domain/modelos.py` y `validar_barras` en `app/domain/mercado.py` (S7). Verificar con tests unitarios con valores concretos:
  - cierre −5 → descarte "precio no positivo";
  - `float('nan')`, `float('inf')`, `'410.25'` y `None` → "precio no numérico";
  - máximo 400 y mínimo 405 → "máximo menor que el mínimo";
  - con `hoy` 2025-03-07, una barra del 2025-03-10 → "fecha futura";
  - dos barras del 2025-03-06 → ambas descartadas;
  - ticker `AAPL` al pedir `MSFT` → "otro ticker";
  - `410.2500004` (float) → `Decimal('410.250000')`;
  - una apertura por encima del máximo queda como válida con aviso.

  Verificar también con cobertura del 100 % del módulo y `lint-imports` en verde: el dominio no importa nada externo.

## 5. Calidad, CI y documentación (HU-1..HU-5)

- [x] 5.1 Verificar la calidad completa en verde:
  - ruff, format, mypy e import-linter;
  - `pytest --cov=app --cov-fail-under=85` y cobertura de `app/domain` ≥ 95 %;
  - bandit;
  - el script de trazabilidad con la lista de pendientes actualizada.
- [x] 5.2 Con `docker compose -f compose.yaml up -d --build`, comprobar a mano que:
  - `curl -H 'Host: atacante.example' http://localhost:8080/api/openapi.json` da `400` en `problem+json`;
  - `curl http://localhost:8080/api/no-existe` da `404` en `problem+json` con las cabeceras;
  - un `POST` con `Origin: https://atacante.example` da `403`;
  - el healthcheck de `api` sigue `healthy`.
- [x] 5.3 Actualizar el readme:
  - **Sección 2.5:** filas nuevas del mapa de amenazas: datos del proveedor (A08 · A05), formato común de errores sin eco (A05 · A10), cabeceras en la API (A02) y comprobación en pantalla (A06).
  - **Sección 2.6:** tests de seguridad de este ticket.
  - **Sección 4:** formato `problem+json` de los errores con un ejemplo de `400` y uno de `429`.

  Verificar que el readme no contradice los deltas y con `openspec validate sec-01-seguridad-api --strict`.
- [ ] 5.4 Hacer commit, subir la rama y comprobar que el CI queda en verde en GitHub. Verificar con `gh run view`.

## Workflow follow-up

- Archivar con `/opsx:archive`: sincroniza los deltas de `seguridad-api` e `importacion-cartera` con las specs vivas. Tras el archivado, el script debe seguir en verde: los pendientes de los escenarios nuevos ya coinciden con escenarios vivos.
- Siguiente ticket: BE-01a (`be-01a-contenedor-seguro`).

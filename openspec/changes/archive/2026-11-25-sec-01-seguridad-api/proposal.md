# Proposal

## Why

La API todavía no aplica ningún control de la spec `seguridad-api`: no filtra `Host` ni `Origin`, no limita la frecuencia de las operaciones caras y responde los errores con el formato por defecto de FastAPI (`422`, trazas en texto).

SEC-01 va antes del primer endpoint de negocio, BE-01a y BE-01b, para que todos nazcan detrás de los mismos controles.

La revisión con OWASP Top 10:2025 deja además tres huecos sin cubrir por ninguna spec:
- **Los datos del proveedor de mercado (yfinance) se tratan como fiables** (A08, A05). Una barra con precios negativos, `NaN`, máximo menor que mínimo, fecha futura o de otro ticker acabaría en la caché y en los cálculos. Un mensaje de error del proveedor podría llegar a la respuesta.
- **Solo los `500` tienen un formato definido.** Los `400`, `403`, `404` y `429` no lo tienen, y nada impide que repitan valores de la petición. Es el contrato que necesitará la pantalla de carga de FE-01 para mostrar los errores siempre como texto (A05, A10).
- **La entrada del usuario en pantalla no se comprueba antes de enviarla.** El servidor sigue siendo la única autoridad, pero la persona recibiría antes el motivo y no se subirían ficheros que van a ser rechazados.

Cubre el **ticket SEC-01** de la Entrega 2, transversal a las features **F1-F5** y a las historias **HU-1 a HU-5**, con foco en HU-1 (importación).

## What Changes

**En la API (implementado en este ticket):**
- **Host admitido:** rechazo con `400` de los `Host` que no estén en `HOSTS_ADMITIDOS`, contra DNS rebinding.
- **Origen de los `POST`:** comprobación de `Origin` y `Sec-Fetch-Site` frente a `ORIGENES_ADMITIDOS`, con `403`.
- **Límite de frecuencia con `limits`** (la librería de ventanas de slowapi), en un middleware que actúa antes del enrutado: 5 importaciones y 10 backtests por minuto, con `429` y `Retry-After`. Los límites quedan en una tabla por método y ruta, que se aplicará sola cuando existan esas rutas (BE-01b y BE-05).
- **Formato común de los errores:** todos los `4xx` y `5xx` responden en `application/problem+json`, con texto plano y sin repetir valores de la petición.
  - Los errores de validación de FastAPI responden `400` en lugar de `422`.
  - Los errores no previstos responden `500` con un identificador de incidencia, y la traza solo va al log.
- **Cabeceras de seguridad** en todas las respuestas de la API, también sin nginx (modo desarrollo en el puerto 8000).
- **Log estructurado:** una línea JSON por error con el identificador de incidencia, sin secretos, y un filtro que oculta los valores de `DATABASE_URL` y `LLM_API_KEY`.
- **Validador de datos del proveedor de mercado:** función pura del dominio que convierte cada barra recibida a `Decimal` y descarta las no válidas con su motivo. BE-02 la conecta al adaptador de yfinance y al de ficheros.

**En las specs (deltas):**
- **`seguridad-api`:**
  - "Formato común de los errores";
  - "Cabeceras de seguridad de la API";
  - "Datos del proveedor de mercado como entrada no confiable".
- **`importacion-cartera`:** "Comprobación del fichero en pantalla antes de enviarlo", que implementará FE-01.

**Trazabilidad:**
- El script admite pendientes que citen escenarios de deltas de changes activos, para que un change pueda dejar sus escenarios nuevos asignados a otro ticket antes de archivarse.
- La lista de pendientes recoge los escenarios nuevos con su ticket.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `seguridad-api`: añade el formato común de los errores (`4xx` y `5xx` en `problem+json` sin eco de la petición), las cabeceras de seguridad en las respuestas de la API y el tratamiento de los datos del proveedor de mercado como entrada no confiable.
- `importacion-cartera`: añade la comprobación en pantalla de la extensión `.xlsx` y del tamaño máximo de 5 MB antes de enviar el fichero, sin sustituir la validación del servidor.

## Fuera de alcance

- **Las rutas de negocio.** Los escenarios que nombran endpoints que aún no existen se prueban en el ticket que crea cada ruta:
  - BE-01b: la importación aceptada y la sexta importación;
  - BE-07: las consultas sin límite y los datos del proveedor vistos en `GET /api/cartera/posiciones`;
  - BE-04: "Host local", el periodo `abc`, el valor no repetido y el mensaje del proveedor;
  - BE-05: el cliente sin navegador y el campo no admitido;
  - BE-03: la excepción en la TWR.
- **Los adaptadores de yfinance y de ficheros, la caché y los reintentos (BE-02).** SEC-01 entrega el validador puro que BE-02 debe usar.
- **La validación del contenedor XLSX (BE-01a) y del contenido (BE-01b).**
- **La pantalla de carga (FE-01).** Este change solo fija en la spec la comprobación previa al envío.
- **La autenticación**, aceptada como riesgo en la fila 16 del mapa de amenazas: solo ejecución local.
- **Cambios en nginx**, que ya aplica CSP y cabeceras a la SPA desde OPS-01.

## Impact

- **Código nuevo:**
  - `backend/app/api/errores.py`, con los manejadores y el formato `problem+json`;
  - `backend/app/api/seguridad.py`, con los middlewares de `Host`, origen y cabeceras, y el limitador;
  - `backend/app/infrastructure/registro.py`, con el log JSON y el filtro de secretos;
  - `backend/app/domain/mercado.py` y los modelos de barra en `backend/app/domain/modelos.py`, con el validador del proveedor.
- **Código modificado:**
  - `backend/app/main.py`;
  - `backend/tests/trazabilidad.py` y `backend/tests/escenarios_pendientes.toml`.
- **Dependencias:** `limits` en producción.
- **API:** cambian el código y el formato de los errores de validación (`422` → `400`) y de los errores no previstos. Todas las respuestas llevan cabeceras de seguridad.
- **readme:**
  - sección 2.5: filas nuevas del mapa de amenazas para los datos de terceros, el formato de errores y la comprobación en pantalla;
  - sección 2.6: tests de seguridad;
  - sección 4: formato de errores de la API.

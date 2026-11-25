# Especificación de seguridad-api

## Purpose
Proteger la API HTTP de trAIde, que se ejecuta en local y sin autenticación, frente a peticiones de otros orígenes, DNS rebinding, abuso de las operaciones caras y fugas de información en los errores.

## Requirements

### Requirement: Host admitido
El sistema SHALL responder `400 Bad Request` a cualquier petición cuya cabecera `Host`, sin el puerto, no sea `localhost` ni `127.0.0.1`.

#### Scenario: Host local
- **WHEN** el cliente envía `GET /api/estrategias` con la cabecera `Host: localhost:8080`
- **THEN** el sistema responde con normalidad

#### Scenario: DNS rebinding
- **WHEN** el cliente envía `GET /api/cartera/posiciones` con la cabecera `Host: atacante.example:8080`
- **THEN** el sistema responde `400 Bad Request` sin datos de la cartera

### Requirement: Origen de las peticiones que envían datos
El sistema SHALL rechazar con `403 Forbidden` las peticiones `POST` cuya cabecera `Origin` no coincida con el origen de la aplicación, o que no tengan `Origin` y cuya cabecera `Sec-Fetch-Site` sea `cross-site` o `same-site`.

#### Scenario: Importación desde otra web
- **WHEN** el navegador envía `POST /api/cartera/importacion` con la cabecera `Origin: https://atacante.example`
- **THEN** el sistema responde `403 Forbidden` y la cartera existente no cambia

#### Scenario: Importación desde la propia aplicación
- **WHEN** el navegador envía `POST /api/cartera/importacion` con la cabecera `Origin: http://localhost:8080` y un fichero válido
- **THEN** el sistema responde `201 Created`

#### Scenario: Cliente sin navegador
- **WHEN** un cliente de línea de comandos envía `POST /api/backtests` sin cabeceras `Origin` ni `Sec-Fetch-Site`
- **THEN** el sistema procesa la petición con normalidad

### Requirement: Límite de frecuencia de las operaciones caras
El sistema SHALL responder `429 Too Many Requests` con la cabecera `Retry-After` en segundos cuando se superen 5 peticiones por minuto a `POST /api/cartera/importacion` o 10 por minuto a `POST /api/backtests`, sin limitar el resto de endpoints.

#### Scenario: Sexta importación en un minuto
- **WHEN** el cliente envía 6 peticiones a `POST /api/cartera/importacion` en menos de un minuto
- **THEN** la sexta recibe `429 Too Many Requests` con `Retry-After` y la cartera no cambia por esa petición

#### Scenario: Consultas sin límite
- **WHEN** el cliente envía 100 peticiones a `GET /api/cartera/posiciones` en un minuto
- **THEN** ninguna recibe `429`

#### Scenario: Límite en pantalla
- **WHEN** la persona recibe un `429` al ejecutar el backtest
- **THEN** ve un mensaje que indica cuántos segundos debe esperar antes de reintentar

### Requirement: Validación de parámetros con 400
El sistema SHALL responder `400 Bad Request`, y no `422`, cuando los parámetros de ruta, de consulta o el cuerpo JSON de una petición no superen la validación de tipos, rangos o campos admitidos, reservando `422` para el contenido del fichero importado y los tickers sin histórico.

#### Scenario: Tipo de parámetro no válido
- **WHEN** el cliente envía `GET /api/estrategias/rsi/senales` con el periodo `abc`
- **THEN** el sistema responde `400 Bad Request` indicando el parámetro no válido

#### Scenario: Campo no admitido en el cuerpo
- **WHEN** el cliente envía `POST /api/backtests` con un campo `comision` que no existe
- **THEN** el sistema responde `400 Bad Request` indicando el campo no admitido

### Requirement: Errores inesperados sin detalles internos
El sistema SHALL responder a cualquier error no previsto con `500 Internal Server Error` y un cuerpo `application/problem+json` con tipo, título y un identificador de incidencia, sin trazas, rutas de ficheros, consultas SQL ni datos de configuración.

#### Scenario: Excepción no controlada
- **WHEN** se produce una excepción no prevista al calcular la TWR
- **THEN** el sistema responde `500 Internal Server Error` con un cuerpo `application/problem+json` que incluye un identificador de incidencia y no incluye la traza

### Requirement: Formato común de los errores
El sistema SHALL responder todos los errores `4xx` y `5xx` de la API con un cuerpo `application/problem+json` que incluya al menos `type`, `title` y `status`, con los textos en texto plano, y SHALL no repetir en ellos los valores recibidos en la ruta, la consulta, las cabeceras o el cuerpo de la petición, salvo los 20 primeros caracteres de una celda del fichero importado que ya permite el requisito "Mensajes de error sin eco del contenido".

#### Scenario: Ruta inexistente
- **WHEN** el cliente envía `GET /api/no-existe`
- **THEN** el sistema responde `404 Not Found` con un cuerpo `application/problem+json` con `type`, `title` y `status` 404, sin la traza

#### Scenario: Valor de la petición no repetido
- **WHEN** el cliente envía `GET /api/estrategias/rsi/senales` con el periodo `<script>alert(1)</script>`
- **THEN** el sistema responde `400 Bad Request` con un cuerpo `application/problem+json` que nombra el parámetro `periodo` y no contiene el valor enviado

#### Scenario: Host rechazado con el formato común
- **WHEN** el cliente envía `GET /api/openapi.json` con la cabecera `Host: atacante.example`
- **THEN** el sistema responde `400 Bad Request` con un cuerpo `application/problem+json` que no contiene el valor `atacante.example`

### Requirement: Cabeceras de seguridad de la API
El sistema SHALL incluir en todas las respuestas de la API, también cuando se accede a ella sin pasar por el servidor web de la aplicación, las cabeceras `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY` y `Cache-Control: no-store`, y en las respuestas JSON la cabecera `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`.

#### Scenario: Respuesta JSON de la API
- **WHEN** el cliente envía `GET /api/openapi.json` directamente a la API en el puerto 8000
- **THEN** la respuesta incluye `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Cache-Control: no-store` y `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`

#### Scenario: Respuesta de error
- **WHEN** el cliente envía `GET /api/no-existe`
- **THEN** la respuesta `404` incluye las mismas cabeceras de seguridad

### Requirement: Datos del proveedor de mercado como entrada no confiable
El sistema SHALL validar cada barra diaria que recibe del proveedor de mercado antes de guardarla o usarla, y SHALL descartar las barras con algún precio no numérico, no finito o no positivo, con el máximo menor que el mínimo, con una fecha posterior a la fecha actual o repetida, o de un ticker distinto del pedido. SHALL registrar cada descarte con el ticker, la fecha y el motivo, sin los valores recibidos, y SHALL no incluir nunca en sus respuestas texto procedente del proveedor.

#### Scenario: Cierre no positivo
- **WHEN** existe una posición abierta de `MSFT`, el proveedor devuelve para `MSFT` un cierre sin ajustar de 410,25 USD el 2025-03-06 y de −5 USD el 2025-03-07, y el cliente envía `GET /api/cartera/posiciones`
- **THEN** la posición de `MSFT` tiene como precio de referencia 410,25 USD con la fecha 2025-03-06

#### Scenario: Precio no numérico o no finito
- **WHEN** existe una posición abierta de `MSFT`, el proveedor devuelve un cierre de 410,25 USD el 2025-03-06 y un cierre `NaN` el 2025-03-07, y el cliente envía `GET /api/cartera/posiciones`
- **THEN** la posición de `MSFT` tiene como precio de referencia 410,25 USD con la fecha 2025-03-06

#### Scenario: Máximo menor que el mínimo
- **WHEN** existe una posición abierta de `MSFT`, el proveedor devuelve una barra válida el 2025-03-06 con cierre 410,25 USD y una barra el 2025-03-07 con máximo 400 USD y mínimo 405 USD, y el cliente envía `GET /api/cartera/posiciones`
- **THEN** la posición de `MSFT` tiene como precio de referencia 410,25 USD con la fecha 2025-03-06

#### Scenario: Fecha posterior a la fecha actual
- **WHEN** la fecha actual es el 2025-03-07, existe una posición abierta de `MSFT`, el proveedor devuelve un cierre de 412 USD el 2025-03-07 y otro de 999 USD el 2025-03-10, y el cliente envía `GET /api/cartera/posiciones`
- **THEN** la posición de `MSFT` tiene como precio de referencia 412 USD con la fecha 2025-03-07

#### Scenario: Datos de otro ticker
- **WHEN** existe una posición abierta de `MSFT`, el proveedor devuelve únicamente barras identificadas como `AAPL` al pedir `MSFT`, y el cliente envía `GET /api/cartera/posiciones`
- **THEN** la posición de `MSFT` se devuelve con precio de referencia y rendimiento vacíos y el motivo de que el precio no está disponible, y no muestra ningún precio de `AAPL`

#### Scenario: Mensaje del proveedor con marcado
- **WHEN** no hay datos de mercado en caché, el proveedor falla con el mensaje `<script>alert(1)</script> limit exceeded` y el cliente envía `GET /api/estrategias/rsi/senales`
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles, y el cuerpo no contiene ningún fragmento del mensaje del proveedor

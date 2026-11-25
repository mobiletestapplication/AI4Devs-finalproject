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

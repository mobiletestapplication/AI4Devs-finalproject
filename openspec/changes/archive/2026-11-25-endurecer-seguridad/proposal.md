# Proposal

## Why

El vector de ataque principal de trAIde es la subida de un fichero XLSX, y la app no tiene autenticación. La revisión de seguridad con OWASP Top 10:2025 como referencia encuentra que:
- varios rechazos de ficheros peligrosos (zip bomb, macros, XXE, límite de filas, patrón de ticker) solo existen como controles de diseño sin código HTTP;
- falta protección frente a peticiones enviadas desde otra web abierta en el navegador y frente al DNS rebinding contra `127.0.0.1` (A01), y nada limita las operaciones caras (A06);
- la validación por defecto de FastAPI responde `422` donde las specs exigen `400` (A10).

Formalizarlo en specs convierte estos controles en contrato y permite derivar sus tests de escenarios.

Cubre la feature **F1 (Importación)** y la historia **HU-1**, y transversalmente los endpoints de **F2-F5**.

## What Changes

- **Rechazos del fichero en `importacion-cartera`:**
  - **`413`:** contenido descomprimido de más de 50 MB, proporción de compresión mayor de 100:1 o más de 1.000 entradas en el ZIP.
  - **`415`:** macros, objetos incrustados, vínculos externos, tipo de contenido distinto de una hoja `.xlsx` normal, formato OLE (`.xls` antiguo o cifrado) o DTD y entidades XML.
  - **`422`:** más de 10.000 filas, análisis de más de 10 segundos, ticker fuera del patrón admitido o precios no positivos.
- **Errores de importación sin eco:** los mensajes de error no repiten el contenido de las celdas más allá de 20 caracteres.
- **Nueva capability `seguridad-api`:**
  - **`400`:** cabecera `Host` distinta de `localhost` o `127.0.0.1`.
  - **`403`:** `POST` desde otro origen.
  - **`429` con `Retry-After`:** más de 5 importaciones o más de 10 backtests por minuto.
  - **`400`:** parámetros de petición no válidos, en lugar del `422` por defecto.
  - **`500`:** errores inesperados en `application/problem+json`, sin trazas ni rutas.

## Capabilities

### New Capabilities
- `seguridad-api`: protecciones transversales de la API HTTP (host admitido, origen de las peticiones que envían datos, límites de frecuencia, formato de los errores de validación e inesperados).

### Modified Capabilities
- `importacion-cartera`: nuevos requisitos de rechazo de ficheros comprimidos peligrosos, ficheros con contenido activo o no estándar, límite de filas y de tiempo, formato de ticker y precios, y mensajes de error sin eco del contenido.

## Fuera de alcance

- Autenticación, sesiones, HTTPS en local y despliegue público (decisiones A9 y A14 de `revisar-arquitectura-mvp`).
- Escaneo antivirus de los ficheros.
- Rate limiting en los endpoints de consulta.
- Especificar S1 (LLM): sus controles frente a prompt injection quedan en design.md hasta que S1 tenga spec.
- Seguridad de la cadena de suministro y de los secretos, que se controla en CI y no es comportamiento HTTP (ver design.md).

## Impact

- **API:** códigos nuevos `400` (Host), `403`, `429` y `500` con `application/problem+json`; `413`, `415` y `422` cubren casos nuevos de la importación.
- **Frontend:** debe enviar las peticiones desde el mismo origen (ya ocurre con nginx y el proxy de Vite, A14) y mostrar `429` con el tiempo de espera.
- **Tests:** nuevos fixtures maliciosos (zip bomb, `.xlsm`, OLE, DTD/XXE, 10.001 filas, ticker con fórmula).
- **Otros changes:** `alinear-readme-con-specs` deja de marcar estas reglas como pendientes de spec. Las secciones 2.4 y 2.5 de `revisar-arquitectura-mvp` (A14) remiten a este change para los códigos.
- **readme.md:** secciones 2.2, 2.5, 2.6, 4 (códigos y OpenAPI de importación), 5 (HU-1) y 6 (BE-01, OPS-01).

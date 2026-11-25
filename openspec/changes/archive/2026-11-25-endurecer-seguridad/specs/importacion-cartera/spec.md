# Spec Delta

## ADDED Requirements

### Requirement: Rechazo de ficheros comprimidos peligrosos
El sistema SHALL rechazar con `413 Payload Too Large`, sin modificar la cartera existente y sin descomprimir el contenido, los ficheros cuyo índice ZIP declare más de 50 MB descomprimidos, una proporción de compresión total mayor de 100:1 o más de 1.000 entradas.

#### Scenario: Zip bomb
- **WHEN** el cliente envía un XLSX de 200 KB cuyo índice declara 2 GB descomprimidos
- **THEN** el sistema responde `413 Payload Too Large` indicando que el contenido descomprimido supera el límite, y la cartera existente no cambia

#### Scenario: Proporción de compresión excesiva
- **WHEN** el cliente envía un XLSX de 300 KB que se descomprime en 40 MB
- **THEN** el sistema responde `413 Payload Too Large`, porque la proporción es mayor de 100:1 aunque no supere 50 MB

#### Scenario: Demasiadas entradas
- **WHEN** el índice ZIP del fichero contiene 1.500 entradas
- **THEN** el sistema responde `413 Payload Too Large` indicando el número máximo de entradas

### Requirement: Rechazo de ficheros con contenido activo o no estándar
El sistema SHALL rechazar con `415 Unsupported Media Type`, sin modificar la cartera, los ficheros que no sean una hoja `.xlsx` estándar según su contenido y no según su extensión: con macros, objetos incrustados o vínculos externos, en formato OLE (`.xls` antiguo o cifrado), o con declaraciones DTD o entidades XML.

#### Scenario: Libro con macros renombrado
- **WHEN** el cliente envía un fichero `cartera.xlsx` que contiene `xl/vbaProject.bin`
- **THEN** el sistema responde `415 Unsupported Media Type` indicando que no se admiten ficheros con macros

#### Scenario: Formato OLE
- **WHEN** el cliente envía un fichero `.xlsx` cuyos primeros bytes son `D0 CF 11 E0`
- **THEN** el sistema responde `415 Unsupported Media Type` indicando que el fichero no es un XLSX estándar

#### Scenario: Entidad XML externa
- **WHEN** el cliente envía un XLSX cuya hoja contiene una declaración `<!DOCTYPE` con una entidad que apunta a `file:///etc/passwd`
- **THEN** el sistema responde `415 Unsupported Media Type`, no resuelve la entidad y la respuesta no contiene contenido del servidor

#### Scenario: Vínculos externos
- **WHEN** el cliente envía un XLSX que contiene la carpeta `xl/externalLinks/`
- **THEN** el sistema responde `415 Unsupported Media Type` indicando que no se admiten vínculos externos

### Requirement: Límites de filas y de tiempo de análisis
El sistema SHALL rechazar con `422 Unprocessable Entity`, sin modificar la cartera, los ficheros con más de 10.000 filas de datos o cuyo análisis supere 10 segundos.

#### Scenario: Demasiadas filas
- **WHEN** el cliente envía un XLSX válido con 10.001 filas de datos
- **THEN** el sistema responde `422 Unprocessable Entity` indicando que el máximo es 10.000 filas

#### Scenario: Límite exacto
- **WHEN** el cliente envía un XLSX válido con 10.000 filas de datos
- **THEN** el sistema importa las 10.000 posiciones con `201 Created`

#### Scenario: Análisis demasiado lento
- **WHEN** el análisis del fichero supera 10 segundos
- **THEN** el sistema responde `422 Unprocessable Entity` indicando que el fichero es demasiado complejo

### Requirement: Formato del ticker y de los precios
El sistema SHALL considerar no válida, con `422 Unprocessable Entity` y su número de fila, una fila cuyo ticker, tras normalizarlo a mayúsculas, no cumpla `^[A-Z.\-]{1,10}$`, o cuyo precio de compra o de venta no sea mayor que 0.

#### Scenario: Ticker con fórmula
- **WHEN** la fila 3 tiene como ticker el texto `=HYPERLINK("http://x","AAPL")`
- **THEN** el sistema responde `422 Unprocessable Entity` con un error en la fila 3 por ticker no válido

#### Scenario: Ticker con punto
- **WHEN** una fila tiene el ticker `brk.b`
- **THEN** la posición se importa con el ticker `BRK.B`

#### Scenario: Precio no positivo
- **WHEN** la fila 5 tiene un precio de compra de 0 USD y la fila 6 un precio de venta de −10 USD
- **THEN** el sistema responde `422 Unprocessable Entity` con un error para la fila 5 y otro para la fila 6

#### Scenario: Fórmula sin valor calculado
- **WHEN** la celda de cantidad de la fila 2 contiene una fórmula sin valor calculado guardado
- **THEN** el sistema responde `422 Unprocessable Entity` con un error en la fila 2 por cantidad vacía

### Requirement: Mensajes de error sin eco del contenido
El sistema SHALL describir los errores de importación sin incluir más de 20 caracteres del valor de una celda, y SHALL devolverlos como texto, de modo que el contenido del fichero no pueda inyectar marcado en la pantalla.

#### Scenario: Valor largo en un error
- **WHEN** la fila 4 tiene como ticker un texto de 500 caracteres
- **THEN** el error de la fila 4 incluye como mucho los 20 primeros caracteres seguidos de `…`

#### Scenario: Marcado en una celda
- **WHEN** la fila 2 tiene como ticker `<img src=x onerror=alert(1)>`
- **THEN** la persona ve el error de la fila 2 con ese texto literal y truncado, sin que se interprete como HTML

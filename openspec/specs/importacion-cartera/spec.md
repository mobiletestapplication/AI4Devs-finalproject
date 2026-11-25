# Especificación de importacion-cartera

## Purpose
Permitir que una persona cargue un fichero XLSX con sus posiciones abiertas y cerradas y consulte la cartera simulada resultante en una tabla Watchlist con precio, rendimiento total y tipo de plusvalía (Short-Term o Long-Term Capital Gain).

## Requirements

### Requirement: Formato del fichero de posiciones
El sistema SHALL aceptar ficheros XLSX cuya primera hoja contenga una fila de cabecera con las columnas obligatorias `Ticker`, `Fecha de compra`, `Cantidad` y `Precio de compra`, y las columnas opcionales `Fecha de venta` y `Precio de venta`, interpretando cada fila posterior como una posición en USD; una posición sin fecha de venta SHALL considerarse abierta y una con fecha y precio de venta SHALL considerarse cerrada.

#### Scenario: Fichero válido con posiciones abiertas y cerradas
- **WHEN** el cliente envía `POST /api/cartera/importacion` con un fichero XLSX válido de 3 filas, 2 de ellas sin fecha de venta y 1 con fecha y precio de venta
- **THEN** el sistema responde `201 Created` indicando 3 posiciones importadas, 2 abiertas y 1 cerrada

#### Scenario: Cabeceras en distinto orden y capitalización
- **WHEN** el cliente envía un fichero XLSX con las columnas obligatorias en otro orden y escritas en minúsculas
- **THEN** el sistema responde `201 Created` e importa las posiciones igual que si las cabeceras siguieran el orden y la capitalización de referencia

#### Scenario: Tickers normalizados a mayúsculas
- **WHEN** una fila contiene el ticker `aapl`
- **THEN** la posición importada tiene el ticker `AAPL`

### Requirement: Rechazo de ficheros no válidos
El sistema SHALL rechazar el fichero completo, sin modificar la cartera existente, cuando no sea un XLSX, supere 5 MB, le falte alguna columna obligatoria o contenga alguna fila no válida, e informar en la respuesta de cada problema detectado con su número de fila cuando aplique.

#### Scenario: Fichero que no es XLSX
- **WHEN** el cliente envía `POST /api/cartera/importacion` con un fichero CSV
- **THEN** el sistema responde `415 Unsupported Media Type` y la cartera existente no cambia

#### Scenario: Fichero demasiado grande
- **WHEN** el cliente envía un fichero XLSX de más de 5 MB
- **THEN** el sistema responde `413 Payload Too Large` y la cartera existente no cambia

#### Scenario: Falta una columna obligatoria
- **WHEN** el cliente envía un fichero XLSX sin la columna `Precio de compra`
- **THEN** el sistema responde `422 Unprocessable Entity` indicando que falta la columna `Precio de compra`

#### Scenario: Filas con datos incoherentes
- **WHEN** el fichero contiene en la fila 4 una cantidad igual a 0 y en la fila 7 una fecha de venta anterior a la fecha de compra
- **THEN** el sistema responde `422 Unprocessable Entity` con un error para la fila 4 y otro para la fila 7, y no importa ninguna posición

#### Scenario: Venta incompleta
- **WHEN** una fila tiene fecha de venta pero no precio de venta, o precio de venta pero no fecha de venta
- **THEN** el sistema responde `422 Unprocessable Entity` indicando esa fila como venta incompleta

#### Scenario: Fechas futuras
- **WHEN** una fila tiene una fecha de compra o de venta posterior a la fecha actual
- **THEN** el sistema responde `422 Unprocessable Entity` indicando esa fila y la fecha futura

### Requirement: Sustitución de la cartera
El sistema SHALL mantener una única cartera simulada, de modo que cada importación válida reemplace por completo las posiciones de la importación anterior.

#### Scenario: Segunda importación
- **WHEN** existe una cartera con 5 posiciones y el cliente importa con éxito un fichero de 2 posiciones
- **THEN** una consulta posterior de posiciones devuelve exactamente esas 2 posiciones

### Requirement: Consulta de posiciones
El sistema SHALL responder a `GET /api/cartera/posiciones` con `200 OK` y la lista de posiciones, incluyendo para cada una ticker, estado (abierta o cerrada), cantidad, fecha y precio de compra, fecha y precio de venta si existen, precio de referencia con su fecha, días de tenencia, rendimiento total en USD y en porcentaje, y tipo de plusvalía.

#### Scenario: Cartera importada
- **WHEN** existe una cartera importada y el cliente envía `GET /api/cartera/posiciones`
- **THEN** el sistema responde `200 OK` con una entrada por cada posición del fichero importado y todos los campos descritos

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `GET /api/cartera/posiciones`
- **THEN** el sistema responde `200 OK` con una lista vacía

### Requirement: Precio de referencia
El sistema SHALL usar como precio de referencia el último precio de cierre diario disponible, sin ajustar por splits, para las posiciones abiertas y el precio de venta para las posiciones cerradas, y SHALL indicar que el precio no está disponible, sin calcular el rendimiento, cuando no pueda obtener ningún cierre de una posición abierta.

#### Scenario: Posición abierta
- **WHEN** se consulta una posición abierta de `MSFT` y el último cierre diario disponible, del 2025-03-07, es 410,25 USD
- **THEN** la posición tiene como precio de referencia 410,25 USD con la fecha 2025-03-07

#### Scenario: Posición cerrada
- **WHEN** se consulta una posición cerrada vendida a 150 USD
- **THEN** la posición tiene como precio de referencia 150 USD con la fecha de venta

#### Scenario: Cotización no disponible
- **WHEN** no se puede obtener ningún cierre para el ticker de una posición abierta
- **THEN** la posición se devuelve con precio de referencia y rendimiento vacíos y un motivo que indica que el precio no está disponible, y el resto de posiciones se devuelven con normalidad

#### Scenario: Sin cotización intradía
- **WHEN** se consulta una posición abierta de `MSFT` durante una sesión en curso cuyo cierre aún no existe
- **THEN** el precio de referencia es el cierre de la sesión anterior con su fecha, el mismo que usa el cálculo de la TWR

### Requirement: Rendimiento total
El sistema SHALL calcular el rendimiento total de cada posición como (precio de referencia − precio de compra) × cantidad en USD, y en porcentaje como (precio de referencia ÷ precio de compra − 1) × 100, de modo que en las posiciones abiertas refleje la ganancia o pérdida no realizada y en las cerradas la realizada.

#### Scenario: Ganancia no realizada
- **WHEN** una posición abierta de 10 acciones compradas a 100 USD tiene un precio de referencia de 120 USD
- **THEN** su rendimiento total es 200 USD y 20 %

#### Scenario: Pérdida realizada
- **WHEN** una posición cerrada de 5 acciones compradas a 80 USD se vendió a 60 USD
- **THEN** su rendimiento total es −100 USD y −25 %

### Requirement: Clasificación de la plusvalía
El sistema SHALL clasificar cada posición como Long-Term cuando entre la fecha de compra y la fecha de venta (o la fecha actual si está abierta) haya transcurrido más de un año, y como Short-Term en caso contrario, con independencia de que el rendimiento sea positivo o negativo.

#### Scenario: Venta en el aniversario de la compra
- **WHEN** una posición se compró el 2024-01-10 y se vendió el 2025-01-10
- **THEN** se clasifica como Short-Term

#### Scenario: Venta al día siguiente del aniversario
- **WHEN** una posición se compró el 2024-01-10 y se vendió el 2025-01-11
- **THEN** se clasifica como Long-Term

#### Scenario: Posición abierta
- **WHEN** una posición abierta se compró hace 200 días
- **THEN** se clasifica como Short-Term y su clasificación cambia a Long-Term cuando haya transcurrido más de un año desde la compra

### Requirement: Carga del fichero en pantalla
El sistema SHALL ofrecer a la persona un control para seleccionar o arrastrar un fichero `.xlsx`, mostrarle el resultado de la carga y, si ya existe una cartera, pedirle confirmación antes de sustituirla.

#### Scenario: Pantalla sin cartera
- **WHEN** la persona abre el dashboard sin haber importado ninguna cartera
- **THEN** ve un mensaje que la invita a cargar su fichero de posiciones y el control de carga

#### Scenario: Carga correcta
- **WHEN** la persona arrastra un fichero XLSX válido sobre el control de carga
- **THEN** ve un indicador de progreso, después un mensaje de éxito con el número de posiciones importadas, y la Watchlist se actualiza con la nueva cartera

#### Scenario: Carga con errores
- **WHEN** la persona carga un fichero con filas no válidas
- **THEN** ve la lista de errores con el número de fila y el motivo de cada uno, y la Watchlist sigue mostrando la cartera anterior

#### Scenario: Confirmación de sustitución
- **WHEN** ya existe una cartera y la persona selecciona un nuevo fichero
- **THEN** ve un aviso de que la cartera actual será sustituida y solo se importa el fichero si confirma

### Requirement: Tabla Watchlist
El sistema SHALL mostrar la cartera en una tabla Watchlist con una fila por posición y las columnas ticker, estado, cantidad, precio de compra, precio de referencia, rendimiento total en USD y en porcentaje, y tipo de plusvalía, permitiendo ordenar por cualquier columna y filtrar por posiciones abiertas, cerradas o todas.

#### Scenario: Colores del rendimiento
- **WHEN** la persona ve una posición con rendimiento positivo y otra con rendimiento negativo
- **THEN** el rendimiento positivo aparece en verde con signo `+` y el negativo en rojo con signo `−`

#### Scenario: Etiqueta de plusvalía
- **WHEN** la persona ve la columna de tipo de plusvalía
- **THEN** cada fila muestra una etiqueta `Short-Term` o `Long-Term` visualmente diferenciada

#### Scenario: Precio no disponible
- **WHEN** una posición abierta no tiene cotización disponible
- **THEN** la persona ve `—` en el precio y en el rendimiento, y al pasar el cursor sobre ellos ve el motivo

#### Scenario: Ordenar y filtrar
- **WHEN** la persona pulsa la cabecera de la columna de rendimiento y elige el filtro de posiciones abiertas
- **THEN** ve solo las posiciones abiertas, ordenadas por rendimiento, y al volver a pulsar la cabecera se invierte el orden

# Spec Delta

## ADDED Requirements

### Requirement: Resumen de la cartera
El sistema SHALL calcular un resumen de la cartera con el valor actual y el capital invertido de las posiciones abiertas, el P&L no realizado en USD y en porcentaje sobre el capital invertido, el P&L realizado de las cerradas y el número de posiciones abiertas y cerradas, excluyendo de los tres primeros valores las posiciones abiertas sin precio de referencia e indicando cuántas son.

#### Scenario: Resumen de abiertas y cerradas
- **WHEN** la cartera tiene abiertas 10 `AAPL` compradas a 100 USD con referencia 120 USD y 5 `MSFT` compradas a 200 USD con referencia 180 USD, y cerradas con resultados de +150 y −100 USD
- **THEN** el valor actual es 2.100 USD, el capital invertido 2.000 USD, el P&L no realizado +100 USD y +5 %, el P&L realizado +50 USD, y hay 2 posiciones abiertas y 2 cerradas

#### Scenario: Posición abierta sin precio
- **WHEN** además hay una posición abierta de `XYZ` sin cotización disponible
- **THEN** el valor actual, el capital invertido y el P&L no realizado no cambian, el resumen indica 3 posiciones abiertas y "1 posición sin precio"

### Requirement: Ganancias realizadas por año fiscal
El sistema SHALL agrupar las posiciones cerradas por el año natural de su fecha de venta y, para cada año, calcular por separado para Short-Term y Long-Term la suma de ganancias, la suma de pérdidas y el resultado neto, ordenando los años del más reciente al más antiguo.

#### Scenario: Desglose de un año
- **WHEN** en 2024 se cerraron posiciones Short-Term con resultados +300 y −100 USD y una Long-Term con +500 USD
- **THEN** el año 2024 tiene en Short-Term ganancias 300 USD, pérdidas −100 USD y neto +200 USD, y en Long-Term ganancias 500 USD, pérdidas 0 USD y neto +500 USD

#### Scenario: Año según la fecha de venta
- **WHEN** una posición comprada el 2024-06-01 se vendió el 2025-01-05
- **THEN** su resultado cuenta en el año 2025 como Short-Term

#### Scenario: Sin posiciones cerradas
- **WHEN** todas las posiciones están abiertas
- **THEN** la lista de años está vacía

### Requirement: Fecha de los datos de mercado
El sistema SHALL indicar en el resumen la fecha y hora de la cotización más reciente usada para valorar las posiciones abiertas, y SHALL marcar los datos como desactualizados cuando tengan más de 5 días naturales respecto a la fecha actual.

#### Scenario: Datos al día
- **WHEN** la cotización más reciente es del viernes 2025-03-07 y la fecha actual es el lunes 2025-03-10
- **THEN** el resumen indica esa fecha y hora y los datos no se marcan como desactualizados

#### Scenario: Datos desactualizados
- **WHEN** la cotización más reciente es del 2025-03-07 y la fecha actual es el 2025-03-14
- **THEN** los datos se marcan como desactualizados

### Requirement: Consulta del resumen por HTTP
El sistema SHALL responder a `GET /api/cartera/resumen` con `200 OK` y el resumen de la cartera, las ganancias realizadas por año fiscal y la fecha de los datos de mercado con su marca de desactualización.

#### Scenario: Cartera importada
- **WHEN** existe una cartera importada y el cliente envía `GET /api/cartera/resumen`
- **THEN** el sistema responde `200 OK` con todos los campos descritos

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `GET /api/cartera/resumen`
- **THEN** el sistema responde `200 OK` con todos los importes y recuentos a 0, la lista de años vacía y la fecha de los datos vacía

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se puede obtener ninguna cotización del proveedor de mercado
- **THEN** el sistema responde `200 OK` con el P&L realizado, los recuentos y las ganancias por año, y el valor actual, el capital invertido, el P&L no realizado y la fecha de los datos vacíos con el motivo "datos de mercado no disponibles"

### Requirement: Cartera de ejemplo descargable
El sistema SHALL responder a `GET /api/cartera/ejemplo` con `200 OK` y siempre el mismo fichero XLSX como adjunto `cartera-ejemplo.xlsx`, con las cabeceras de referencia y al menos 8 posiciones válidas de al menos 4 tickers, que incluya abiertas y cerradas, Short-Term y Long-Term, ganancias y pérdidas, y una primera compra con más de 400 días de antigüedad.

#### Scenario: Descarga del ejemplo
- **WHEN** el cliente envía `GET /api/cartera/ejemplo`
- **THEN** el sistema responde `200 OK` con el tipo `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` y la cabecera `Content-Disposition: attachment; filename="cartera-ejemplo.xlsx"`

#### Scenario: El ejemplo se importa sin errores
- **WHEN** el cliente envía el fichero descargado a `POST /api/cartera/importacion`
- **THEN** el sistema responde `201 Created` con al menos 8 posiciones importadas, alguna abierta y alguna cerrada

#### Scenario: La descarga no modifica la cartera
- **WHEN** existe una cartera de 5 posiciones y el cliente descarga el ejemplo
- **THEN** una consulta posterior de posiciones sigue devolviendo las 5 posiciones

### Requirement: Cabecera de resumen en pantalla
El sistema SHALL mostrar sobre la Watchlist una cabecera con el valor actual, el capital invertido, el P&L no realizado y el realizado, la fecha de los datos de mercado y, al desplegarla, la tabla de ganancias realizadas por año y tipo de plusvalía.

#### Scenario: Indicadores del resumen
- **WHEN** la persona abre el dashboard con una cartera importada
- **THEN** ve el valor actual, el capital invertido y los P&L en USD, el no realizado también en porcentaje, con los resultados positivos en verde con `+` y los negativos en rojo con `−`

#### Scenario: Tabla fiscal
- **WHEN** la persona despliega "Resultado realizado por año"
- **THEN** ve una fila por año con columnas de ganancias, pérdidas y neto para Short-Term y para Long-Term

#### Scenario: Fecha de los datos visible
- **WHEN** la persona navega a cualquier sección del dashboard
- **THEN** sigue viendo en la cabecera "Datos de mercado a" con la fecha y hora de la cotización más reciente, y si los datos están desactualizados la ve resaltada con el aviso "Datos desactualizados"

#### Scenario: Actualización tras importar
- **WHEN** la persona importa una nueva cartera
- **THEN** la cabecera de resumen se recalcula con los valores de la nueva cartera sin recargar la página

### Requirement: Descarga del ejemplo en pantalla
El sistema SHALL ofrecer a la persona un enlace "Descargar cartera de ejemplo" en el mensaje de bienvenida sin cartera y junto al control de carga.

#### Scenario: Descarga desde el estado vacío
- **WHEN** la persona abre el dashboard sin cartera y pulsa "Descargar cartera de ejemplo"
- **THEN** el navegador descarga `cartera-ejemplo.xlsx` y la pantalla sigue mostrando el mensaje de bienvenida y el control de carga

# Especificación de estrategias-indicador

## Purpose
Ofrecer estrategias de inversión basadas cada una en un indicador técnico que, aplicadas a las acciones con posición abierta en la cartera simulada, generen una señal de Compra, Venta o Mantener para apoyar la toma de decisiones.

## Requirements

### Requirement: Catálogo de estrategias
El sistema SHALL responder a `GET /api/estrategias` con `200 OK` y el catálogo de estrategias disponibles, incluyendo para cada una su identificador, nombre, indicador, descripción de sus reglas y sus parámetros con valor por defecto, mínimo y máximo, y SHALL incluir al menos la estrategia `rsi` (periodo 14, sobreventa 30, sobrecompra 70) y la estrategia `cruce-medias` (media corta de 50 sesiones y media larga de 200 sesiones).

#### Scenario: Consulta del catálogo
- **WHEN** el cliente envía `GET /api/estrategias`
- **THEN** el sistema responde `200 OK` con las estrategias `rsi` y `cruce-medias` y los parámetros por defecto descritos

### Requirement: Reglas de la estrategia RSI
El sistema SHALL calcular el RSI de Wilder sobre los precios de cierre diarios con el periodo configurado y SHALL emitir Compra cuando el RSI de la última sesión sea inferior al umbral de sobreventa, Venta cuando sea superior al umbral de sobrecompra y Mantener en otro caso.

#### Scenario: Sobreventa
- **WHEN** el RSI(14) de un ticker en la última sesión es 25 con umbral de sobreventa 30
- **THEN** la señal de ese ticker es Compra

#### Scenario: Sobrecompra
- **WHEN** el RSI(14) de un ticker en la última sesión es 78 con umbral de sobrecompra 70
- **THEN** la señal de ese ticker es Venta

#### Scenario: Zona neutral
- **WHEN** el RSI(14) de un ticker en la última sesión es 50
- **THEN** la señal de ese ticker es Mantener

### Requirement: Reglas de la estrategia de cruce de medias
El sistema SHALL calcular las medias móviles simples corta y larga sobre los precios de cierre diarios y SHALL emitir Compra cuando la media corta esté por encima de la larga en la última sesión, Venta cuando esté por debajo y Mantener cuando sean iguales.

#### Scenario: Media corta por encima
- **WHEN** la media de 50 sesiones de un ticker es 105 y la de 200 sesiones es 100
- **THEN** la señal de ese ticker es Compra

#### Scenario: Media corta por debajo
- **WHEN** la media de 50 sesiones de un ticker es 95 y la de 200 sesiones es 100
- **THEN** la señal de ese ticker es Venta

### Requirement: Intensidad de la señal
El sistema SHALL acompañar cada señal de Compra o Venta con una intensidad entre 0 y 100, que en la estrategia `rsi` SHALL ser (sobreventa − RSI) ÷ sobreventa × 100 para Compra y (RSI − sobrecompra) ÷ (100 − sobrecompra) × 100 para Venta, y en la estrategia `cruce-medias` SHALL ser el mínimo entre 100 y |media corta − media larga| ÷ media larga × 1000; la señal Mantener SHALL tener intensidad 0.

#### Scenario: Intensidad RSI
- **WHEN** el RSI de un ticker es 15 con umbral de sobreventa 30
- **THEN** la señal es Compra con intensidad 50

#### Scenario: Intensidad de cruce de medias
- **WHEN** la media corta de un ticker es 105 y la media larga es 100
- **THEN** la señal es Compra con intensidad 50

#### Scenario: Intensidad limitada
- **WHEN** la media corta de un ticker es 130 y la media larga es 100
- **THEN** la señal es Compra con intensidad 100

### Requirement: Señales actuales de la cartera
El sistema SHALL responder a `GET /api/estrategias/{id}/senales`, con parámetros opcionales que sustituyen a los valores por defecto, con `200 OK` y una entrada por cada ticker con posición abierta que incluya la señal, la intensidad, el valor o valores del indicador, la fecha de la sesión usada y la fecha desde la que se mantiene esa misma señal.

#### Scenario: Señales con parámetros por defecto
- **WHEN** la cartera tiene posiciones abiertas en `AAPL` y `MSFT` y el cliente envía `GET /api/estrategias/rsi/senales`
- **THEN** el sistema responde `200 OK` con una señal para `AAPL` y otra para `MSFT` calculadas con RSI(14), sobreventa 30 y sobrecompra 70

#### Scenario: Parámetros personalizados
- **WHEN** el cliente envía `GET /api/estrategias/rsi/senales` con periodo 21 y sobreventa 25
- **THEN** las señales se calculan con RSI(21), sobreventa 25 y sobrecompra 70

#### Scenario: Ticker cerrado no incluido
- **WHEN** la cartera tiene una posición cerrada en `TSLA` y ninguna abierta en ese ticker
- **THEN** la respuesta no incluye ninguna señal para `TSLA`

#### Scenario: Histórico insuficiente
- **WHEN** un ticker tiene menos sesiones de histórico que las necesarias para calcular el indicador, por ejemplo 150 sesiones para una media de 200
- **THEN** su entrada tiene la señal "Sin datos suficientes" e intensidad 0

### Requirement: Validación de la petición de señales
El sistema SHALL rechazar las peticiones de señales que hagan referencia a una estrategia inexistente, contengan parámetros fuera de rango o incoherentes, o se hagan sin una cartera importada.

#### Scenario: Estrategia inexistente
- **WHEN** el cliente envía `GET /api/estrategias/bollinger/senales` y `bollinger` no está en el catálogo
- **THEN** el sistema responde `404 Not Found` indicando que la estrategia no existe

#### Scenario: Parámetros incoherentes
- **WHEN** el cliente pide señales de `cruce-medias` con media corta de 200 y media larga de 50
- **THEN** el sistema responde `400 Bad Request` indicando que la media corta debe ser menor que la larga

#### Scenario: Parámetro fuera de rango
- **WHEN** el cliente pide señales de `rsi` con un umbral de sobreventa mayor o igual que el de sobrecompra
- **THEN** el sistema responde `400 Bad Request` indicando el parámetro no válido

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente pide señales
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios históricos del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

### Requirement: Histórico de señales de un ticker
El sistema SHALL responder a `GET /api/estrategias/{id}/senales/{ticker}/historico`, con un rango de fechas opcional que por defecto cubre el último año, con `200 OK` y la serie diaria de precio de cierre, valores del indicador y señal, junto con las fechas en que la señal cambió.

#### Scenario: Histórico del último año
- **WHEN** el cliente envía `GET /api/estrategias/rsi/senales/AAPL/historico` sin rango de fechas
- **THEN** el sistema responde `200 OK` con una entrada por sesión del último año con cierre, RSI y señal, y la lista de cambios de señal

#### Scenario: Ticker fuera de la cartera
- **WHEN** el cliente pide el histórico de un ticker sin posición abierta en la cartera
- **THEN** el sistema responde `404 Not Found` indicando que el ticker no forma parte de la cartera

### Requirement: Selección de estrategia en pantalla
El sistema SHALL permitir a la persona elegir una estrategia del catálogo y ajustar sus parámetros, validando los valores antes de calcular, y SHALL mantener la estrategia y los parámetros elegidos como estrategia seleccionada en el resto de secciones del dashboard durante la sesión.

#### Scenario: Valores por defecto
- **WHEN** la persona elige la estrategia RSI
- **THEN** ve los campos periodo, sobreventa y sobrecompra rellenos con 14, 30 y 70 y una descripción de las reglas

#### Scenario: Parámetro no válido
- **WHEN** la persona escribe una media corta mayor que la media larga
- **THEN** ve un mensaje de error junto al campo y no se recalculan las señales hasta que lo corrija

#### Scenario: Estrategia seleccionada compartida
- **WHEN** la persona selecciona `cruce-medias` con medias 20 y 100 y navega a otra sección del dashboard
- **THEN** esa sección usa `cruce-medias` con medias 20 y 100 como estrategia seleccionada

### Requirement: Tabla y gráfico de señales en pantalla
El sistema SHALL mostrar una tabla con una fila por ticker con posición abierta, con la señal como etiqueta de color, su intensidad, el valor del indicador y la fecha desde la que se mantiene, y al elegir un ticker SHALL mostrar un gráfico de su precio y del indicador con marcas en los cambios de señal, acompañado siempre del aviso de que no constituye asesoramiento financiero.

#### Scenario: Etiquetas de señal
- **WHEN** la persona ve la tabla de señales
- **THEN** las señales Compra aparecen en verde, Venta en rojo, Mantener en gris y "Sin datos suficientes" atenuada

#### Scenario: Detalle de un ticker
- **WHEN** la persona pulsa la fila de `AAPL`
- **THEN** ve un gráfico del precio de cierre de `AAPL` del último año, el indicador en un panel inferior con los umbrales o medias de la estrategia y marcas de Compra y Venta donde cambió la señal

#### Scenario: Aviso legal
- **WHEN** la persona ve las señales de cualquier estrategia
- **THEN** ve el aviso "Las señales son orientativas y no constituyen asesoramiento financiero"

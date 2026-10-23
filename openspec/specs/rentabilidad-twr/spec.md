# Especificación de rentabilidad-twr

## Purpose
Calcular y mostrar la Tasa de Retorno Ponderada en el Tiempo (TWR) de la cartera simulada, acumulada, anualizada, mensual y semanal, incluyendo la ganancia o pérdida no realizada de las posiciones abiertas para que el resultado no dependa del momento ni del importe de las aportaciones.

## Requirements

### Requirement: Flujos de caja de la cartera
El sistema SHALL tratar cada compra como una aportación externa de cantidad × precio de compra en su fecha y cada venta como una retirada externa de cantidad × precio de venta en su fecha, sin saldo de efectivo dentro de la cartera.

#### Scenario: Compra y venta
- **WHEN** la cartera contiene una compra de 10 acciones a 100 USD el 2025-03-03 y su venta a 115 USD el 2025-03-10
- **THEN** el cálculo considera una aportación de 1.000 USD el 2025-03-03 y una retirada de 1.150 USD el 2025-03-10

### Requirement: Valoración diaria de la cartera
El sistema SHALL valorar la cartera al cierre de cada sesión bursátil como la suma de cantidad × precio de cierre de esa sesión de las posiciones que siguen abiertas al terminar ese día, de modo que las posiciones aún no cerradas aporten su ganancia o pérdida no realizada hasta la última sesión con cierre disponible.

#### Scenario: Posición abierta sin vender
- **WHEN** una posición abierta de 10 acciones tiene un cierre de 130 USD en la última sesión disponible
- **THEN** esa posición aporta 1.300 USD al valor de la cartera en esa sesión

#### Scenario: Cierre ausente en una sesión
- **WHEN** falta el precio de cierre de un ticker en una sesión intermedia
- **THEN** el sistema usa el último cierre anterior disponible de ese ticker para valorar esa sesión

### Requirement: Rentabilidad diaria
El sistema SHALL calcular la rentabilidad de cada sesión t como (V_t + S_t − V_{t−1} − B_t) ÷ (V_{t−1} + B_t), donde V es el valor de la cartera al cierre, B la suma de aportaciones por compras y S la suma de retiradas por ventas de esa sesión, y SHALL excluir las sesiones en las que el denominador sea cero por no haber inversión.

#### Scenario: Sesión de compra
- **WHEN** se compran 10 acciones a 100 USD en una cartera vacía y la acción cierra ese día a 110 USD
- **THEN** la rentabilidad de esa sesión es 10 %

#### Scenario: Sesión sin flujos
- **WHEN** la cartera vale 1.100 USD al cierre anterior, no hay compras ni ventas y vale 990 USD al cierre
- **THEN** la rentabilidad de esa sesión es −10 %

#### Scenario: Sesión de venta
- **WHEN** la cartera vale 1.100 USD al cierre anterior y ese día se venden todas sus acciones por 1.150 USD
- **THEN** la rentabilidad de esa sesión es 4,55 % y las sesiones siguientes sin posiciones quedan excluidas

### Requirement: TWR acumulada
El sistema SHALL calcular la TWR acumulada como el producto de (1 + rentabilidad diaria) de todas las sesiones incluidas, desde la primera compra hasta la última sesión con cierre disponible, menos 1.

#### Scenario: Encadenamiento de rentabilidades
- **WHEN** las rentabilidades diarias son 10 % y −10 %
- **THEN** la TWR acumulada es −1 %

#### Scenario: Neutralidad frente a aportaciones
- **WHEN** se compran 10 acciones a 100 USD que cierran a 110 USD, y en la sesión siguiente se compran otras 10 a 110 USD y todas cierran a 121 USD
- **THEN** la TWR acumulada es 21 %, igual a la revalorización de la acción, aunque la segunda aportación fuese mayor que la primera

### Requirement: TWR anualizada
El sistema SHALL calcular la TWR anualizada como (1 + TWR acumulada)^(365 ÷ D) − 1, siendo D los días naturales entre la primera compra y la última sesión incluida, y SHALL indicar que no es aplicable cuando D sea inferior a 365 para no extrapolar periodos cortos.

#### Scenario: Periodo de dos años
- **WHEN** la TWR acumulada es 21 % en un periodo de 730 días
- **THEN** la TWR anualizada es 10 %

#### Scenario: Periodo inferior a un año
- **WHEN** el periodo de la cartera es de 200 días
- **THEN** la TWR anualizada se indica como no aplicable con el motivo "periodo inferior a un año"

### Requirement: TWR mensual y semanal
El sistema SHALL calcular una TWR por cada mes natural y por cada semana ISO (de lunes a domingo) encadenando las rentabilidades diarias de las sesiones incluidas en cada periodo, identificando los meses como `AAAA-MM` y las semanas como `AAAA-Www`, marcando como parciales el primer y el último periodo si no están completos y como sin inversión los periodos sin sesiones incluidas.

#### Scenario: Mes completo
- **WHEN** las sesiones incluidas de marzo de 2025 tienen rentabilidades diarias que encadenadas suman un 3 %
- **THEN** el periodo `2025-03` tiene una TWR de 3 % y no está marcado como parcial

#### Scenario: Semana parcial actual
- **WHEN** la última sesión disponible es un miércoles
- **THEN** la semana ISO que contiene ese miércoles aparece marcada como parcial

#### Scenario: Mes sin inversión
- **WHEN** todas las posiciones se cerraron en enero y la siguiente compra es en marzo
- **THEN** el periodo de febrero aparece marcado como sin inversión y sin valor de TWR

### Requirement: Consulta de la TWR por HTTP
El sistema SHALL responder a `GET /api/cartera/rentabilidad/twr` con `200 OK` y la fecha de inicio, la fecha de fin, la TWR acumulada, la TWR anualizada o el motivo de no aplicabilidad, la serie mensual y la serie semanal, expresando las rentabilidades como proporciones decimales con al menos 6 decimales.

#### Scenario: Cartera importada
- **WHEN** existe una cartera importada y el cliente envía `GET /api/cartera/rentabilidad/twr`
- **THEN** el sistema responde `200 OK` con todos los campos descritos, por ejemplo una TWR acumulada de `0.210000` para un 21 %

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `GET /api/cartera/rentabilidad/twr`
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Ticker sin histórico de precios
- **WHEN** el proveedor de mercado no tiene ningún precio histórico para un ticker de la cartera
- **THEN** el sistema responde `422 Unprocessable Entity` indicando los tickers sin histórico

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios históricos del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

### Requirement: Panel de rentabilidad en pantalla
El sistema SHALL mostrar a la persona un panel de rentabilidad con la TWR acumulada y la anualizada junto a su periodo, y un selector Mensual/Semanal que cambie entre un gráfico de barras y una tabla con la TWR de cada periodo, con porcentajes de dos decimales.

#### Scenario: Indicadores principales
- **WHEN** la persona abre el panel de rentabilidad con una cartera importada
- **THEN** ve la TWR acumulada y la anualizada en porcentaje con dos decimales, las fechas de inicio y fin, y una ayuda que explica qué mide la TWR

#### Scenario: Cambio de granularidad
- **WHEN** la persona cambia el selector de Mensual a Semanal
- **THEN** el gráfico y la tabla pasan a mostrar una barra y una fila por semana ISO

#### Scenario: Valores positivos, negativos y parciales
- **WHEN** el gráfico contiene periodos con TWR positiva, negativa y parcial
- **THEN** las barras positivas aparecen en verde, las negativas en rojo y los periodos parciales llevan una marca visible que lo indica

#### Scenario: Anualizada no aplicable
- **WHEN** el periodo de la cartera es inferior a un año
- **THEN** la persona ve "No aplicable (periodo inferior a un año)" en lugar de la TWR anualizada

#### Scenario: Actualización tras importar
- **WHEN** la persona importa una nueva cartera
- **THEN** el panel de rentabilidad se recalcula y muestra los valores de la nueva cartera sin recargar la página

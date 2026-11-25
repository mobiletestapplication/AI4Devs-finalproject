# Spec Delta

## ADDED Requirements

### Requirement: Cantidad sugerida de las compras
El sistema SHALL calcular para cada operación Comprar una cantidad sugerida igual a la parte entera de (valor de la cartera × porcentaje de riesgo) ÷ (precio de referencia − stop-loss), siendo el valor de la cartera la suma de las posiciones abiertas al último cierre, junto con el capital necesario (cantidad × precio de referencia) y su porcentaje sobre el valor de la cartera.

#### Scenario: Cantidad con riesgo por defecto
- **WHEN** el valor de la cartera es 10.000 USD, el riesgo es el 1 % por defecto y una compra tiene precio de referencia 100 USD y stop-loss 96 USD
- **THEN** la cantidad sugerida es 25 acciones, con un capital necesario de 2.500 USD que supone el 25 % del valor de la cartera

#### Scenario: Redondeo hacia abajo
- **WHEN** el valor de la cartera es 10.000 USD, el riesgo es 1 % y una compra tiene precio de referencia 180 USD y stop-loss 170,40 USD
- **THEN** la cantidad sugerida es 10 acciones, porque 100 ÷ 9,60 = 10,42

#### Scenario: Riesgo insuficiente para una acción
- **WHEN** el valor de la cartera es 1.000 USD, el riesgo es 0,5 % y una compra tiene precio de referencia 500 USD y stop-loss 450 USD
- **THEN** la cantidad sugerida es 0 con el motivo "el riesgo permitido no alcanza para una acción" y la operación se sigue recomendando

#### Scenario: Ventas sin cantidad sugerida
- **WHEN** la operación recomendada es Vender
- **THEN** no incluye cantidad sugerida y mantiene la cantidad total con posición abierta en ese ticker

### Requirement: Antigüedad de la señal
El sistema SHALL indicar en cada operación recomendada su antigüedad, que es el número de sesiones bursátiles entre la sesión en que empezó la señal y la sesión usada (0 si empezó en la sesión usada), y SHALL marcarla como nueva cuando la antigüedad sea de 5 sesiones o menos.

#### Scenario: Señal reciente
- **WHEN** la señal de Compra de `AAPL` empezó el lunes 2025-03-03 y la sesión usada es el viernes 2025-03-07
- **THEN** la operación tiene una antigüedad de 4 sesiones y se marca como nueva

#### Scenario: Señal antigua
- **WHEN** la señal de Venta de `MSFT` se mantiene desde hace 30 sesiones
- **THEN** la operación tiene una antigüedad de 30 sesiones y no se marca como nueva

### Requirement: Filtro por antigüedad de la señal
El sistema SHALL excluir de las candidatas, cuando se indique una antigüedad máxima, las señales cuya antigüedad la supere, antes de ordenar por intensidad y elegir las 10 primeras; sin antigüedad máxima no se excluye ninguna señal por su antigüedad.

#### Scenario: Filtro aplicado antes del límite
- **WHEN** hay 12 candidatas, 4 de ellas con antigüedad de 5 sesiones o menos, y se pide una antigüedad máxima de 5
- **THEN** se recomiendan exactamente esas 4 operaciones

#### Scenario: Sin filtro
- **WHEN** no se indica antigüedad máxima y hay 12 candidatas
- **THEN** se recomiendan las 10 de mayor intensidad, como sin este requisito

### Requirement: Aviso de wash sale en las compras
El sistema SHALL añadir un aviso a una operación Comprar cuando la cartera tenga una posición cerrada de ese ticker vendida con pérdida en los 30 días naturales anteriores a la sesión usada, indicando la fecha de esa venta y la fecha a partir de la cual la compra ya no afectaría, que es el día 31 tras la venta.

#### Scenario: Venta con pérdida reciente
- **WHEN** se recomienda Comprar `TSLA`, la sesión usada es del 2025-03-20 y una posición de `TSLA` se vendió con pérdida el 2025-03-03
- **THEN** la operación incluye el aviso de wash sale con la venta del 2025-03-03 y la fecha 2025-04-03

#### Scenario: Venta con ganancia
- **WHEN** la última venta de `TSLA`, del 2025-03-03, tuvo ganancia
- **THEN** la compra de `TSLA` no incluye aviso de wash sale

#### Scenario: Venta con pérdida antigua
- **WHEN** la venta con pérdida de `TSLA` fue el 2025-01-10 y la sesión usada es del 2025-03-20
- **THEN** la compra de `TSLA` no incluye aviso de wash sale

### Requirement: Parámetros de riesgo y antigüedad por HTTP
El sistema SHALL aceptar en `GET /api/recomendaciones` los parámetros opcionales `riesgo`, porcentaje entre 0,1 y 5 con valor por defecto 1, y `antiguedad_max`, entero entre 0 y 250, SHALL devolver en cada operación los campos nuevos y en la respuesta los valores aplicados, y SHALL responder `400 Bad Request` si alguno está fuera de rango.

#### Scenario: Parámetros indicados
- **WHEN** el cliente envía `GET /api/recomendaciones` con la estrategia `rsi`, `riesgo` 2 y `antiguedad_max` 5
- **THEN** el sistema responde `200 OK` con las operaciones calculadas con un riesgo del 2 % y señales de 5 sesiones o menos, e indica esos dos valores en la respuesta

#### Scenario: Riesgo fuera de rango
- **WHEN** el cliente envía `riesgo` igual a 10
- **THEN** el sistema responde `400 Bad Request` indicando que el riesgo debe estar entre 0,1 y 5

#### Scenario: Antigüedad no válida
- **WHEN** el cliente envía `antiguedad_max` igual a −1
- **THEN** el sistema responde `400 Bad Request` indicando que la antigüedad máxima debe estar entre 0 y 250

### Requirement: Cantidad, antigüedad y avisos en pantalla
El sistema SHALL mostrar en el panel de operaciones recomendadas la cantidad sugerida y el capital necesario de cada compra, un campo para ajustar el porcentaje de riesgo, la antigüedad de cada señal con una etiqueta "Nueva", un filtro de señales recientes y un icono de aviso en las compras con aviso de wash sale.

#### Scenario: Compra con cantidad
- **WHEN** la persona ve una operación Comprar con cantidad sugerida de 25 acciones y capital de 2.500 USD
- **THEN** ve "25 acciones · 2.500 USD (25,00 % de la cartera)" y una ayuda que explica que la pérdida hasta el stop-loss sería el 1 % de la cartera

#### Scenario: Cambio del riesgo
- **WHEN** la persona cambia el riesgo de 1 % a 2 %
- **THEN** el panel se recalcula y la compra anterior pasa a 50 acciones, y si escribe un valor fuera de 0,1-5 ve un error junto al campo y no se recalcula

#### Scenario: Señales recientes
- **WHEN** la persona activa el filtro "Solo señales recientes"
- **THEN** el panel se recalcula con una antigüedad máxima de 5 sesiones y cada operación mostrada lleva la etiqueta "Nueva"

#### Scenario: Aviso de wash sale visible
- **WHEN** una operación Comprar incluye aviso de wash sale
- **THEN** la persona ve un icono de aviso en esa operación y, al pasar el cursor o pulsarlo, la fecha de la venta con pérdida y la fecha a partir de la cual la compra ya no afectaría

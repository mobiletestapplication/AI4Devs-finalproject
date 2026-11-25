# Especificación de operaciones-recomendadas

## Purpose
Proponer hasta 10 operaciones de trading sobre los tickers con posición abierta en la cartera simulada, derivadas de las señales de la estrategia seleccionada y acompañadas de los niveles y avisos necesarios para decidir.

## Requirements

### Requirement: Selección de las operaciones recomendadas
El sistema SHALL tomar como candidatas las señales de Compra y Venta de la estrategia indicada para los tickers con posición abierta, excluyendo las Compra de tickers sin histórico suficiente para el ATR(14), con como máximo una operación por ticker, ordenarlas por intensidad descendente y, en caso de empate, por ticker en orden alfabético, y devolver las 10 primeras.

#### Scenario: Más de 10 candidatas
- **WHEN** 15 tickers con posición abierta tienen señal de Compra o Venta
- **THEN** se recomiendan las 10 operaciones de mayor intensidad

#### Scenario: Menos de 10 candidatas
- **WHEN** solo 3 tickers con posición abierta tienen señal de Compra o Venta
- **THEN** se recomiendan exactamente esas 3 operaciones

#### Scenario: Señales excluidas
- **WHEN** un ticker tiene señal Mantener o "Sin datos suficientes"
- **THEN** ese ticker no aparece entre las operaciones recomendadas

#### Scenario: Empate de intensidad
- **WHEN** `MSFT` y `AAPL` tienen señal con intensidad 60
- **THEN** la operación de `AAPL` aparece antes que la de `MSFT`

#### Scenario: Compra sin ATR suficiente
- **WHEN** un ticker tiene señal de Compra de la estrategia `cruce-medias` con medias de 20 y 100 sesiones y solo 105 sesiones de histórico, menos de las 114 que necesita el ATR(14)
- **THEN** ese ticker no aparece entre las operaciones recomendadas, porque no se pueden calcular su stop-loss ni su objetivo

#### Scenario: Venta sin ATR suficiente
- **WHEN** un ticker tiene señal de Venta y menos de 114 sesiones de histórico
- **THEN** la operación Vender se recomienda con normalidad, porque las ventas no llevan stop-loss ni objetivo

### Requirement: Contenido de cada operación recomendada
El sistema SHALL describir cada operación con el ticker, el tipo de operación (Comprar o Vender), la intensidad, el precio de referencia igual al último cierre disponible, el motivo expresado con el valor del indicador y los umbrales o medias de la estrategia, y la fecha de la sesión usada; las operaciones Vender SHALL incluir además la cantidad total con posición abierta en ese ticker.

#### Scenario: Recomendación de compra
- **WHEN** `AAPL` tiene señal de Compra con RSI 22 en la estrategia `rsi` y último cierre 180 USD
- **THEN** la operación es Comprar `AAPL` con precio de referencia 180 USD y el motivo "RSI(14) = 22, por debajo de 30"

#### Scenario: Recomendación de venta
- **WHEN** `MSFT` tiene señal de Venta y la cartera tiene dos posiciones abiertas de `MSFT` de 10 y 5 acciones
- **THEN** la operación es Vender `MSFT` con una cantidad de 15 acciones

### Requirement: Stop-loss y objetivo de las compras
El sistema SHALL calcular para cada operación Comprar un stop-loss igual al precio de referencia − 2 × ATR(14) y un objetivo igual al precio de referencia + 3 × ATR(14), con el ATR de Wilder calculado sobre precios diarios, y las operaciones Vender SHALL no incluir stop-loss ni objetivo porque cierran una posición existente.

#### Scenario: Niveles de una compra
- **WHEN** una operación Comprar tiene precio de referencia 100 USD y ATR(14) de 2 USD
- **THEN** su stop-loss es 96 USD y su objetivo 106 USD

#### Scenario: Venta sin niveles
- **WHEN** la operación recomendada es Vender
- **THEN** no incluye stop-loss ni objetivo

### Requirement: Aviso fiscal en las ventas
El sistema SHALL añadir un aviso a una operación Vender cuando alguna de las posiciones abiertas de ese ticker tenga ganancia no realizada y le falten 30 días o menos para cumplir más de un año de tenencia, indicando la fecha a partir de la cual pasaría a Long-Term.

#### Scenario: Posición próxima a Long-Term
- **WHEN** se recomienda Vender `MSFT` y una posición de `MSFT` comprada el 2024-11-15 tiene ganancia a fecha de 2025-10-30
- **THEN** la operación incluye el aviso de que esa posición pasaría a Long-Term a partir del 2025-11-16

#### Scenario: Posición ya Long-Term
- **WHEN** todas las posiciones abiertas del ticker que se recomienda vender son Long-Term
- **THEN** la operación no incluye aviso fiscal

### Requirement: Consulta de recomendaciones por HTTP
El sistema SHALL responder a `GET /api/recomendaciones` con la estrategia y sus parámetros opcionales como parámetros de la petición, con `200 OK` y la lista ordenada de operaciones recomendadas junto con la estrategia y los parámetros aplicados.

#### Scenario: Recomendaciones de una estrategia
- **WHEN** el cliente envía `GET /api/recomendaciones` con la estrategia `cruce-medias` y medias 20 y 100
- **THEN** el sistema responde `200 OK` con las operaciones calculadas con `cruce-medias` de medias 20 y 100 y esos parámetros indicados en la respuesta

#### Scenario: Sin candidatas
- **WHEN** ningún ticker con posición abierta tiene señal de Compra o Venta
- **THEN** el sistema responde `200 OK` con una lista vacía

#### Scenario: Petición no válida
- **WHEN** el cliente no indica estrategia, indica una inexistente o usa parámetros fuera de rango
- **THEN** el sistema responde `400 Bad Request` si falta la estrategia o los parámetros no son válidos y `404 Not Found` si la estrategia no existe

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente pide recomendaciones
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

### Requirement: Panel de operaciones recomendadas en pantalla
El sistema SHALL mostrar a la persona un panel con las operaciones recomendadas para la estrategia seleccionada, en el orden calculado, que se recalcule al cambiar la estrategia o sus parámetros y que muestre siempre la fecha de la sesión usada y el aviso de que no constituye asesoramiento financiero.

#### Scenario: Lista de operaciones
- **WHEN** la persona abre el panel con la estrategia `rsi` seleccionada
- **THEN** ve las operaciones numeradas por orden, cada una con el ticker, una etiqueta Comprar en verde o Vender en rojo, la intensidad como barra, el precio de referencia, el motivo y, en las compras, el stop-loss y el objetivo

#### Scenario: Cambio de estrategia
- **WHEN** la persona cambia la estrategia seleccionada a `cruce-medias`
- **THEN** el panel se recalcula y muestra las operaciones de `cruce-medias` indicando la estrategia aplicada

#### Scenario: Menos de 10 operaciones
- **WHEN** la estrategia seleccionada solo genera 3 operaciones
- **THEN** la persona ve esas 3 operaciones y un mensaje que explica que el resto de tickers tiene señal Mantener o sin datos suficientes

#### Scenario: Ninguna operación
- **WHEN** la estrategia seleccionada no genera ninguna operación
- **THEN** la persona ve un mensaje que indica que no hay operaciones recomendadas para esa estrategia hoy

#### Scenario: Aviso fiscal visible
- **WHEN** una operación Vender incluye aviso fiscal
- **THEN** la persona ve un icono de aviso en esa operación y, al pasar el cursor o pulsarlo, la fecha a partir de la cual la posición pasaría a Long-Term

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

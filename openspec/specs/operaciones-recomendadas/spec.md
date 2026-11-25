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

# Spec Delta

## ADDED Requirements

### Requirement: Línea base de comprar y mantener
El sistema SHALL simular una línea base `buy-hold` que, con el mismo capital inicial, reparto entre tickers y supuestos que las estrategias, compre cada ticker con todo su capital asignado al precio de apertura de la sesión siguiente a la primera compra real y mantenga todas las posiciones hasta la última sesión disponible, sin ninguna venta.

#### Scenario: Compra inicial de la línea base
- **WHEN** el capital inicial es 10.000 USD, la cartera tiene 4 tickers y `AAPL` abre a 125 USD en la sesión siguiente a la primera compra real
- **THEN** `buy-hold` compra 20 acciones de `AAPL` con sus 2.500 USD en esa apertura

#### Scenario: Sin operaciones cerradas
- **WHEN** termina la simulación de `buy-hold`
- **THEN** sus posiciones siguen abiertas, se valoran al último cierre disponible y el porcentaje de aciertos, las medias, el factor de beneficio y la duración media se indican como no disponibles

### Requirement: Línea base del índice de referencia
El sistema SHALL simular una línea base del índice de referencia, SPY por defecto, que invierta todo el capital inicial en el índice al precio de apertura de la sesión siguiente a la primera compra real y lo mantenga hasta la última sesión disponible.

#### Scenario: Compra del índice
- **WHEN** el capital inicial es 10.000 USD y `SPY` abre a 500 USD en la sesión siguiente a la primera compra real
- **THEN** la línea base del índice compra 20 participaciones de `SPY`

#### Scenario: Métricas de las líneas base
- **WHEN** termina el backtest
- **THEN** `buy-hold` y la línea base del índice tienen las mismas métricas y la misma curva de valor base 100 que las estrategias simuladas

## MODIFIED Requirements

### Requirement: Comparativa de resultados
El sistema SHALL ordenar la cartera real, las estrategias simuladas y las líneas base `buy-hold` y del índice de referencia por TWR anualizada, o por TWR acumulada si el periodo es inferior a 365 días, identificando cada fila como cartera real, estrategia o línea base.

#### Scenario: Periodo inferior a un año
- **WHEN** el periodo de la cartera es de 200 días
- **THEN** la comparativa se ordena por TWR acumulada

#### Scenario: Líneas base en la comparativa
- **WHEN** la cartera real obtiene un 8 % anualizado, `rsi` un 6 %, `buy-hold` un 9 % y `SPY` un 7 %
- **THEN** la comparativa queda en el orden `buy-hold`, cartera real, `SPY` y `rsi`, con `buy-hold` y `SPY` identificadas como líneas base

### Requirement: Propuestas de mejora
El sistema SHALL generar propuestas de mejora que indiquen cada estrategia o línea base `buy-hold` que supera a la cartera real y por cuántos puntos porcentuales, señalando si una estrategia que supera a la cartera real queda por debajo de `buy-hold`, las posiciones cerradas con ganancia como Short-Term vendidas en los 30 días anteriores a cumplir más de un año de tenencia, y las compras reales hechas mientras la estrategia seleccionada emitía Venta, con su resultado agregado.

#### Scenario: Estrategia que supera a la cartera real
- **WHEN** la cartera real tiene una TWR anualizada del 8 % y la estrategia `cruce-medias` del 11 %
- **THEN** la comparativa sitúa `cruce-medias` por encima de la cartera real y se propone la mejora "cruce-medias habría obtenido +3,00 pp anualizados"

#### Scenario: Estrategia por debajo de comprar y mantener
- **WHEN** la cartera real tiene una TWR anualizada del 8 %, `cruce-medias` del 11 % y `buy-hold` del 12 %
- **THEN** se proponen las mejoras "buy-hold habría obtenido +4,00 pp anualizados" y "cruce-medias habría obtenido +3,00 pp anualizados, pero queda 1,00 pp por debajo de comprar y mantener"

#### Scenario: Venta cercana a Long-Term
- **WHEN** una posición comprada el 2024-01-10 se vendió con ganancia el 2024-12-20
- **THEN** se propone la mejora de haberla mantenido hasta el 2025-01-11 para que tributara como Long-Term, indicando la ganancia afectada

#### Scenario: Compras contra la señal
- **WHEN** 3 compras reales se hicieron en sesiones en las que la estrategia seleccionada emitía Venta para ese ticker y su resultado conjunto es −450 USD
- **THEN** se propone la mejora indicando esas 3 compras y su resultado de −450 USD

#### Scenario: Ninguna estrategia mejora a la real
- **WHEN** la cartera real obtiene la mayor TWR de la comparativa
- **THEN** la cartera real aparece en primera posición y no se propone ninguna mejora de estrategia

#### Scenario: Índice por encima de la cartera real
- **WHEN** la línea base del índice supera a la cartera real
- **THEN** la comparativa la sitúa por encima de la cartera real, pero no se genera ninguna propuesta de mejora a partir del índice porque invierte en tickers distintos de los de la cartera

### Requirement: Ejecución del backtest por HTTP
El sistema SHALL responder a `POST /api/backtests`, con una estrategia seleccionada y sus parámetros opcionales en el cuerpo, con `200 OK` y las métricas y la curva de la cartera real, el resultado de la estrategia seleccionada con sus parámetros, el de cada estrategia restante del catálogo con sus parámetros por defecto, el de las líneas base `buy-hold` y del índice de referencia, la comparativa ordenada y las propuestas de mejora.

#### Scenario: Backtest con estrategia seleccionada
- **WHEN** el cliente envía `POST /api/backtests` con la estrategia `rsi` y periodo 21
- **THEN** el sistema responde `200 OK` con los resultados de la cartera real, de `rsi` con periodo 21, de `cruce-medias` con sus parámetros por defecto, de `buy-hold` y del índice `SPY`

#### Scenario: Backtest sin estrategia seleccionada
- **WHEN** el cliente envía `POST /api/backtests` sin cuerpo
- **THEN** el sistema responde `200 OK` simulando todas las estrategias del catálogo con sus parámetros por defecto y las dos líneas base, sin la propuesta de compras contra la señal

#### Scenario: Petición no válida
- **WHEN** el cliente envía una estrategia inexistente o parámetros fuera de rango
- **THEN** el sistema responde `404 Not Found` para la estrategia inexistente o `400 Bad Request` para los parámetros, indicando el motivo

#### Scenario: Línea base como estrategia seleccionada
- **WHEN** el cliente envía `POST /api/backtests` con la estrategia `buy-hold`
- **THEN** el sistema responde `404 Not Found` indicando que `buy-hold` es una línea base y no una estrategia del catálogo

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `POST /api/backtests`
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios históricos del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

#### Scenario: Índice de referencia sin datos
- **WHEN** se obtienen los precios de los tickers de la cartera pero no los del índice de referencia
- **THEN** el sistema responde `200 OK` con todos los resultados excepto la línea base del índice, que se indica como no disponible con el motivo "datos del índice de referencia no disponibles"

### Requirement: Sección de backtesting en pantalla
El sistema SHALL ofrecer a la persona una sección de backtesting que ejecute el backtest con la estrategia seleccionada y muestre la comparativa de métricas, las curvas de valor superpuestas, las propuestas de mejora y las operaciones simuladas, con el aviso de que las rentabilidades pasadas no garantizan rentabilidades futuras, y que distinga visualmente las líneas base de las estrategias.

#### Scenario: Ejecución desde la pantalla
- **WHEN** la persona pulsa "Ejecutar backtest" con la estrategia `rsi` seleccionada
- **THEN** ve un indicador de progreso mientras se calcula y el botón queda deshabilitado hasta que termina

#### Scenario: Comparativa de métricas
- **WHEN** termina el backtest
- **THEN** la persona ve una tabla con una fila para la cartera real, otra por estrategia y otra por línea base, con TWR acumulada y anualizada, máximo drawdown, porcentaje de aciertos y factor de beneficio, ordenada según la comparativa y con la mejor fila destacada

#### Scenario: Líneas base diferenciadas
- **WHEN** la persona ve la comparativa y el gráfico de curvas
- **THEN** las filas de `buy-hold` y del índice llevan la etiqueta "Línea base" y sus curvas se dibujan con trazo discontinuo

#### Scenario: Curvas de valor
- **WHEN** termina el backtest
- **THEN** la persona ve un gráfico con la curva base 100 de la cartera real, de cada estrategia y de cada línea base, distinguibles por color y leyenda, y puede ocultar o mostrar cada curva desde la leyenda

#### Scenario: Propuestas de mejora y operaciones simuladas
- **WHEN** termina el backtest y la persona elige una estrategia de la comparativa
- **THEN** ve la lista de propuestas de mejora en lenguaje claro y la tabla de operaciones simuladas de esa estrategia con fechas, precios y resultado

#### Scenario: Error en el cálculo
- **WHEN** el backtest falla porque los datos de mercado no están disponibles
- **THEN** la persona ve un mensaje que explica el problema y le permite reintentar

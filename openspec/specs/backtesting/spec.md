# Especificación de backtesting

## Purpose
Evaluar a posteriori las operaciones reales de la cartera simulada y compararlas con lo que habrían obtenido las estrategias del catálogo sobre los mismos tickers y el mismo periodo, proponiendo mejoras concretas a partir de esa comparación.

## Requirements

### Requirement: Métricas de las operaciones reales
El sistema SHALL calcular para la cartera real la TWR acumulada, la TWR anualizada (no aplicable con periodos inferiores a 365 días), el máximo drawdown, el número de posiciones cerradas, el porcentaje de posiciones cerradas con ganancia, la ganancia media, la pérdida media, el factor de beneficio y la duración media de las posiciones cerradas, valorando las posiciones abiertas al último cierre disponible.

#### Scenario: Porcentaje de aciertos y factor de beneficio
- **WHEN** la cartera tiene cuatro posiciones cerradas con resultados de +100, +50, −30 y −20 USD
- **THEN** el porcentaje de posiciones ganadoras es 50 %, la ganancia media 75 USD, la pérdida media −25 USD y el factor de beneficio 3,0

#### Scenario: Máximo drawdown
- **WHEN** el índice de valor de la cartera, construido encadenando las rentabilidades diarias con base 100, pasa por 100, 120, 90 y 130
- **THEN** el máximo drawdown es −25 %

#### Scenario: Sin posiciones cerradas
- **WHEN** todas las posiciones de la cartera están abiertas
- **THEN** el porcentaje de aciertos, las medias, el factor de beneficio y la duración media se indican como no disponibles y el resto de métricas se calculan con normalidad

### Requirement: Simulación de una estrategia
El sistema SHALL simular cada estrategia desde la fecha de la primera compra real hasta la última sesión disponible sobre todos los tickers que aparecen en la cartera, partiendo de un capital inicial igual al máximo capital invertido simultáneamente en la cartera real, medido a coste de compra, repartido a partes iguales entre los tickers, solo con posiciones largas, permitiendo fracciones de acción y sin comisiones ni deslizamiento.

#### Scenario: Reparto del capital
- **WHEN** el máximo capital invertido simultáneamente en la cartera real fue 10.000 USD y la cartera tiene 4 tickers distintos
- **THEN** la simulación asigna 2.500 USD a cada ticker

#### Scenario: Capital inicial a coste de compra
- **WHEN** la posición A costó 6.000 USD y estuvo abierta del 2024-01-10 al 2024-06-30, la B costó 4.000 USD y estuvo abierta del 2024-03-01 al 2024-12-31, y la C costó 5.000 USD y está abierta desde el 2024-07-01
- **THEN** el capital inicial es 10.000 USD, la suma de A y B entre marzo y junio, y no depende de cuánto se revalorizaran las posiciones

#### Scenario: Ejecución sin sesgo de anticipación
- **WHEN** la estrategia emite Compra para un ticker sin posición simulada con el cierre de una sesión
- **THEN** la simulación compra ese ticker con todo su capital asignado al precio de apertura de la sesión siguiente

#### Scenario: Salida de la posición
- **WHEN** la estrategia emite Venta para un ticker con posición simulada con el cierre de una sesión
- **THEN** la simulación vende toda la posición al precio de apertura de la sesión siguiente y el efectivo resultante queda asignado a ese ticker

#### Scenario: Mantener
- **WHEN** la estrategia emite Mantener o "Sin datos suficientes" para un ticker
- **THEN** la simulación no modifica la posición de ese ticker

#### Scenario: Calentamiento del indicador
- **WHEN** la estrategia necesita 200 sesiones de histórico y la primera compra real fue hace 300 sesiones
- **THEN** el indicador usa las sesiones anteriores a la primera compra para estar disponible desde el inicio del periodo simulado

### Requirement: Métricas de las estrategias simuladas
El sistema SHALL calcular para cada estrategia simulada las mismas métricas que para la cartera real, la lista de operaciones simuladas con fechas, precios y resultado, y la curva de valor diaria con base 100.

#### Scenario: Resultado de una simulación
- **WHEN** se simula la estrategia `rsi` con sus parámetros por defecto
- **THEN** el resultado incluye su TWR acumulada y anualizada, máximo drawdown, métricas de las operaciones cerradas, la lista de operaciones simuladas y la curva de valor con base 100

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

### Requirement: Volatilidad anualizada
El sistema SHALL calcular la volatilidad anualizada de la cartera real y de cada simulación como la desviación típica muestral de sus rentabilidades diarias en las sesiones incluidas multiplicada por √252, y SHALL indicarla como no disponible cuando haya menos de 20 sesiones incluidas.

#### Scenario: Cálculo de la volatilidad
- **WHEN** las rentabilidades diarias de las sesiones incluidas alternan +1 % y −1 % durante 20 sesiones
- **THEN** la desviación típica muestral diaria es 1,0260 % y la volatilidad anualizada es 16,29 %

#### Scenario: Pocas sesiones
- **WHEN** la cartera tiene 12 sesiones incluidas
- **THEN** la volatilidad y el ratio de Sharpe se indican como no disponibles con el motivo "menos de 20 sesiones"

### Requirement: Ratio de Sharpe
El sistema SHALL calcular el ratio de Sharpe con tasa libre de riesgo 0 como la media de las rentabilidades diarias de las sesiones incluidas dividida por su desviación típica muestral y multiplicada por √252, y SHALL indicarlo como no disponible cuando la volatilidad no esté disponible o sea 0.

#### Scenario: Cálculo del Sharpe
- **WHEN** en 250 sesiones incluidas la media de las rentabilidades diarias es 0,05 % y su desviación típica muestral 1 %
- **THEN** el ratio de Sharpe es 0,79

#### Scenario: Volatilidad nula
- **WHEN** todas las rentabilidades diarias incluidas son iguales
- **THEN** el ratio de Sharpe se indica como no disponible con el motivo "volatilidad nula"

### Requirement: Ratio de Calmar
El sistema SHALL calcular el ratio de Calmar como la TWR anualizada dividida por el valor absoluto del máximo drawdown, y SHALL indicarlo como no aplicable cuando la TWR anualizada no sea aplicable o el máximo drawdown sea 0.

#### Scenario: Cálculo del Calmar
- **WHEN** la TWR anualizada es 12 % y el máximo drawdown −25 %
- **THEN** el ratio de Calmar es 0,48

#### Scenario: Sin drawdown
- **WHEN** la curva de valor nunca baja de su máximo anterior
- **THEN** el ratio de Calmar se indica como no aplicable con el motivo "sin drawdown"

### Requirement: Exposición
El sistema SHALL calcular la exposición como la media, sobre todas las sesiones del periodo, de la fracción del valor total invertida en acciones al cierre, de modo que en la cartera real, que no tiene efectivo, equivalga al porcentaje de sesiones con alguna posición abierta.

#### Scenario: Exposición de una estrategia
- **WHEN** en un periodo de 100 sesiones una estrategia tiene todo su capital en acciones durante 60 sesiones y todo en efectivo durante 40
- **THEN** su exposición es 60 %

#### Scenario: Exposición de la cartera real
- **WHEN** el periodo de la cartera real tiene 300 sesiones y en 240 había al menos una posición abierta
- **THEN** la exposición de la cartera real es 80 %

### Requirement: Número de operaciones
El sistema SHALL indicar para la cartera real y cada simulación el número de operaciones ejecutadas, contando por separado las compras y las ventas.

#### Scenario: Recuento de operaciones
- **WHEN** una estrategia simulada abre 3 posiciones y cierra 2 en el periodo
- **THEN** su resultado indica 3 compras, 2 ventas y 5 operaciones en total

### Requirement: Criterio de ordenación de la comparativa
El sistema SHALL ordenar la comparativa por el criterio indicado en la petición, `twr` (por defecto, con la regla actual de TWR anualizada o acumulada), `sharpe` o `calmar` de mayor a menor, o `drawdown` del menos al más negativo, situando al final las filas sin valor disponible y usando `twr` si ninguna fila lo tiene.

#### Scenario: Orden por Sharpe
- **WHEN** el cliente envía `POST /api/backtests` con `orden` igual a `sharpe` y la cartera real tiene Sharpe 0,60, `rsi` 0,90 y `cruce-medias` 0,75
- **THEN** la comparativa queda en el orden `rsi`, `cruce-medias` y cartera real

#### Scenario: Orden por drawdown
- **WHEN** el cliente pide `orden` igual a `drawdown` y los máximos drawdown son −30 %, −12 % y −20 %
- **THEN** la comparativa queda en el orden −12 %, −20 % y −30 %

#### Scenario: Valor no disponible
- **WHEN** el cliente pide `orden` igual a `calmar` y el periodo es inferior a un año
- **THEN** todas las filas tienen Calmar no aplicable y la comparativa se ordena por TWR acumulada indicando que se ha usado ese criterio

#### Scenario: Criterio no válido
- **WHEN** el cliente envía `orden` igual a `beneficio`
- **THEN** el sistema responde `400 Bad Request` indicando los criterios admitidos

#### Scenario: Propuestas independientes del orden
- **WHEN** el cliente pide `orden` igual a `sharpe`
- **THEN** las propuestas de mejora por estrategia se siguen calculando comparando la TWR, como sin criterio de ordenación

### Requirement: Aviso de sesgo de selección
El sistema SHALL incluir en la respuesta del backtest un aviso de que las estrategias se simulan sobre tickers elegidos a posteriori, y la lista de tickers cuya primera compra real es posterior al inicio de la simulación con las dos fechas.

#### Scenario: Ticker comprado más tarde
- **WHEN** la primera compra real de la cartera es del 2024-01-10 y la primera compra real de `NVDA` es del 2024-06-03
- **THEN** la respuesta indica que `NVDA` se opera en la simulación desde el 2024-01-10 aunque se compró por primera vez el 2024-06-03

#### Scenario: Aviso general
- **WHEN** termina cualquier backtest
- **THEN** la respuesta incluye el aviso "Las estrategias se simulan sobre los tickers que ya elegiste; ese conocimiento a posteriori puede favorecer sus resultados"

### Requirement: Métricas de riesgo en pantalla
El sistema SHALL mostrar en la tabla comparativa del backtest las columnas de volatilidad, Sharpe, Calmar, exposición y número de operaciones, con una ayuda que explique cada métrica, un selector del criterio de ordenación y el aviso de sesgo de selección junto a la comparativa.

#### Scenario: Columnas de riesgo
- **WHEN** termina el backtest
- **THEN** la persona ve en cada fila la volatilidad y la exposición en porcentaje con dos decimales, Sharpe y Calmar con dos decimales y el número de operaciones, y `—` con el motivo al pasar el cursor en los valores no disponibles

#### Scenario: Cambio de criterio
- **WHEN** la persona cambia el selector de ordenación de TWR a Sharpe
- **THEN** la tabla se reordena por Sharpe, la fila destacada pasa a ser la de mayor Sharpe y las curvas de valor no cambian

#### Scenario: Aviso de sesgo visible
- **WHEN** la respuesta incluye tickers comprados después del inicio de la simulación
- **THEN** la persona ve el aviso de sesgo de selección y, al desplegarlo, la lista de esos tickers con sus dos fechas

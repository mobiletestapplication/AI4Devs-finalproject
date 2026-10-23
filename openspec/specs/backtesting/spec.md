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
El sistema SHALL simular cada estrategia desde la fecha de la primera compra real hasta la última sesión disponible sobre todos los tickers que aparecen en la cartera, partiendo de un capital inicial igual al máximo capital invertido simultáneamente en la cartera real, repartido a partes iguales entre los tickers, solo con posiciones largas, permitiendo fracciones de acción y sin comisiones ni deslizamiento.

#### Scenario: Reparto del capital
- **WHEN** el máximo capital invertido simultáneamente en la cartera real fue 10.000 USD y la cartera tiene 4 tickers distintos
- **THEN** la simulación asigna 2.500 USD a cada ticker

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
El sistema SHALL ordenar la cartera real y las estrategias simuladas por TWR anualizada, o por TWR acumulada si el periodo es inferior a 365 días.

#### Scenario: Periodo inferior a un año
- **WHEN** el periodo de la cartera es de 200 días
- **THEN** la comparativa se ordena por TWR acumulada

### Requirement: Propuestas de mejora
El sistema SHALL generar propuestas de mejora que indiquen cada estrategia que supera a la cartera real y por cuántos puntos porcentuales, las posiciones cerradas con ganancia como Short-Term vendidas en los 30 días anteriores a cumplir más de un año de tenencia, y las compras reales hechas mientras la estrategia seleccionada emitía Venta, con su resultado agregado.

#### Scenario: Estrategia que supera a la cartera real
- **WHEN** la cartera real tiene una TWR anualizada del 8 % y la estrategia `cruce-medias` del 11 %
- **THEN** la comparativa sitúa `cruce-medias` por encima de la cartera real y se propone la mejora "cruce-medias habría obtenido +3,00 pp anualizados"

#### Scenario: Venta cercana a Long-Term
- **WHEN** una posición comprada el 2024-01-10 se vendió con ganancia el 2024-12-20
- **THEN** se propone la mejora de haberla mantenido hasta el 2025-01-11 para que tributara como Long-Term, indicando la ganancia afectada

#### Scenario: Compras contra la señal
- **WHEN** 3 compras reales se hicieron en sesiones en las que la estrategia seleccionada emitía Venta para ese ticker y su resultado conjunto es −450 USD
- **THEN** se propone la mejora indicando esas 3 compras y su resultado de −450 USD

#### Scenario: Ninguna estrategia mejora a la real
- **WHEN** la cartera real obtiene la mayor TWR de la comparativa
- **THEN** la cartera real aparece en primera posición y no se propone ninguna mejora de estrategia

### Requirement: Ejecución del backtest por HTTP
El sistema SHALL responder a `POST /api/backtests`, con una estrategia seleccionada y sus parámetros opcionales en el cuerpo, con `200 OK` y las métricas y la curva de la cartera real, el resultado de la estrategia seleccionada con sus parámetros y el de cada estrategia restante del catálogo con sus parámetros por defecto, la comparativa ordenada y las propuestas de mejora.

#### Scenario: Backtest con estrategia seleccionada
- **WHEN** el cliente envía `POST /api/backtests` con la estrategia `rsi` y periodo 21
- **THEN** el sistema responde `200 OK` con los resultados de la cartera real, de `rsi` con periodo 21 y de `cruce-medias` con sus parámetros por defecto

#### Scenario: Backtest sin estrategia seleccionada
- **WHEN** el cliente envía `POST /api/backtests` sin cuerpo
- **THEN** el sistema responde `200 OK` simulando todas las estrategias del catálogo con sus parámetros por defecto y sin la propuesta de compras contra la señal

#### Scenario: Petición no válida
- **WHEN** el cliente envía una estrategia inexistente o parámetros fuera de rango
- **THEN** el sistema responde `404 Not Found` para la estrategia inexistente o `400 Bad Request` para los parámetros, indicando el motivo

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `POST /api/backtests`
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios históricos del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

### Requirement: Sección de backtesting en pantalla
El sistema SHALL ofrecer a la persona una sección de backtesting que ejecute el backtest con la estrategia seleccionada y muestre la comparativa de métricas, las curvas de valor superpuestas, las propuestas de mejora y las operaciones simuladas, con el aviso de que las rentabilidades pasadas no garantizan rentabilidades futuras.

#### Scenario: Ejecución desde la pantalla
- **WHEN** la persona pulsa "Ejecutar backtest" con la estrategia `rsi` seleccionada
- **THEN** ve un indicador de progreso mientras se calcula y el botón queda deshabilitado hasta que termina

#### Scenario: Comparativa de métricas
- **WHEN** termina el backtest
- **THEN** la persona ve una tabla con una fila para la cartera real y otra por estrategia, con TWR acumulada y anualizada, máximo drawdown, porcentaje de aciertos y factor de beneficio, ordenada según la comparativa y con la mejor fila destacada

#### Scenario: Curvas de valor
- **WHEN** termina el backtest
- **THEN** la persona ve un gráfico con la curva base 100 de la cartera real y de cada estrategia, distinguibles por color y leyenda, y puede ocultar o mostrar cada curva desde la leyenda

#### Scenario: Propuestas de mejora y operaciones simuladas
- **WHEN** termina el backtest y la persona elige una estrategia de la comparativa
- **THEN** ve la lista de propuestas de mejora en lenguaje claro y la tabla de operaciones simuladas de esa estrategia con fechas, precios y resultado

#### Scenario: Error en el cálculo
- **WHEN** el backtest falla porque los datos de mercado no están disponibles
- **THEN** la persona ve un mensaje que explica el problema y le permite reintentar

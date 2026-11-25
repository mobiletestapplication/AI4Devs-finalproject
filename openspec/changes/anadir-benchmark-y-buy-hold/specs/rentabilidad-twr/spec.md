# Spec Delta

## ADDED Requirements

### Requirement: TWR del índice de referencia
El sistema SHALL calcular la TWR acumulada, anualizada, mensual y semanal del índice de referencia, SPY por defecto, encadenando sus rentabilidades diarias de cierre (cierre_t ÷ cierre_{t−1} − 1) solo en las sesiones incluidas en la TWR de la cartera, y SHALL calcular la diferencia en puntos porcentuales entre la TWR de la cartera y la del índice para cada uno de esos valores.

#### Scenario: TWR del índice en las mismas sesiones
- **WHEN** las sesiones incluidas de la cartera son dos y el índice cierra a 400 USD antes de la primera, a 440 USD en la primera y a 396 USD en la segunda
- **THEN** las rentabilidades diarias del índice son 10 % y −10 % y su TWR acumulada es −1 %

#### Scenario: Diferencia frente al índice
- **WHEN** la TWR acumulada de la cartera es 21 % y la del índice 10 %
- **THEN** la diferencia frente al índice es +11,00 pp

#### Scenario: Sesiones sin inversión excluidas también para el índice
- **WHEN** la cartera no tiene posiciones en febrero y el índice sube un 4 % ese mes
- **THEN** la subida de febrero del índice no entra en su TWR acumulada y el periodo de febrero aparece como sin inversión tanto para la cartera como para el índice

#### Scenario: Anualizada no aplicable para el índice
- **WHEN** el periodo de la cartera es de 200 días
- **THEN** la TWR anualizada del índice y su diferencia se indican como no aplicables con el motivo "periodo inferior a un año"

### Requirement: Curva de valor base 100
El sistema SHALL construir una curva de valor diaria con base 100 para la cartera y otra para el índice de referencia, en la que el valor antes de la primera sesión incluida es 100, cada sesión incluida multiplica el valor anterior por (1 + rentabilidad diaria) y cada sesión excluida repite el valor anterior.

#### Scenario: Curva de la cartera
- **WHEN** las rentabilidades diarias de las dos primeras sesiones incluidas de la cartera son 10 % y −10 %
- **THEN** la curva de la cartera vale 110 en la primera sesión y 99 en la segunda

#### Scenario: Sesión excluida
- **WHEN** la curva de la cartera vale 99 y la sesión siguiente se excluye por no haber inversión
- **THEN** la curva de la cartera y la del índice repiten en esa sesión el valor de la sesión anterior

## MODIFIED Requirements

### Requirement: Consulta de la TWR por HTTP
El sistema SHALL responder a `GET /api/cartera/rentabilidad/twr` con `200 OK` y la fecha de inicio, la fecha de fin, la TWR acumulada, la TWR anualizada o el motivo de no aplicabilidad, la serie mensual y la serie semanal, expresando las rentabilidades como proporciones decimales con al menos 6 decimales, y SHALL incluir además el ticker del índice de referencia, su TWR acumulada y anualizada, la diferencia frente al índice, el valor del índice y la diferencia en cada periodo de las series mensual y semanal, y la curva de valor base 100 de la cartera y del índice.

#### Scenario: Cartera importada
- **WHEN** existe una cartera importada y el cliente envía `GET /api/cartera/rentabilidad/twr`
- **THEN** el sistema responde `200 OK` con todos los campos descritos, por ejemplo una TWR acumulada de `0.210000` para un 21 %, una TWR del índice `SPY` de `0.100000` y una diferencia de `0.110000`

#### Scenario: Sin cartera importada
- **WHEN** no se ha importado ninguna cartera y el cliente envía `GET /api/cartera/rentabilidad/twr`
- **THEN** el sistema responde `409 Conflict` indicando que no hay cartera importada

#### Scenario: Ticker sin histórico de precios
- **WHEN** el proveedor de mercado no tiene ningún precio histórico para un ticker de la cartera
- **THEN** el sistema responde `422 Unprocessable Entity` indicando los tickers sin histórico

#### Scenario: Proveedor de mercado no disponible
- **WHEN** no se pueden obtener precios históricos del proveedor de mercado
- **THEN** el sistema responde `503 Service Unavailable` indicando que los datos de mercado no están disponibles

#### Scenario: Índice de referencia sin datos
- **WHEN** se obtienen los precios de los tickers de la cartera pero no los del índice de referencia
- **THEN** el sistema responde `200 OK` con la TWR y la curva de la cartera, los campos del índice y de la diferencia vacíos y el motivo "datos del índice de referencia no disponibles"

### Requirement: Panel de rentabilidad en pantalla
El sistema SHALL mostrar a la persona un panel de rentabilidad con la TWR acumulada y la anualizada junto a su periodo, y un selector Mensual/Semanal que cambie entre un gráfico de barras y una tabla con la TWR de cada periodo, con porcentajes de dos decimales, y SHALL mostrar además la TWR del índice de referencia y la diferencia frente a él, y un gráfico con la curva base 100 de la cartera y la del índice.

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

#### Scenario: Comparación con el índice
- **WHEN** la TWR acumulada de la cartera es 21 % y la de `SPY` 10 %
- **THEN** la persona ve junto a la TWR de la cartera "SPY: 10,00 %" y la diferencia "+11,00 pp" en verde, que aparecería en rojo con signo `−` si fuera negativa

#### Scenario: Curvas de la cartera y del índice
- **WHEN** la persona abre el panel de rentabilidad con una cartera importada
- **THEN** ve un gráfico de líneas con la curva base 100 de la cartera y la del índice, distinguibles por color y leyenda, y la tabla mensual o semanal incluye la columna del índice y la de la diferencia

#### Scenario: Índice no disponible en pantalla
- **WHEN** la respuesta indica que los datos del índice de referencia no están disponibles
- **THEN** la persona ve la TWR y la curva de la cartera con normalidad y, en lugar de los valores del índice, el mensaje "Índice de referencia no disponible"

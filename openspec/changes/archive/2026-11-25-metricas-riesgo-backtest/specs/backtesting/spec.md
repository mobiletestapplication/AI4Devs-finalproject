# Spec Delta

## ADDED Requirements

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

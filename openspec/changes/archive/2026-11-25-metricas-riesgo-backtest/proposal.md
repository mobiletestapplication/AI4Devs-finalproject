# Proposal

## Why

La comparativa del backtest (F4) se ordena solo por rentabilidad, de modo que una estrategia que gana más asumiendo mucho más riesgo, o que pasa la mayor parte del tiempo en efectivo y acierta por casualidad, aparece como la mejor sin que la persona pueda verlo. Además, la simulación se hace sobre los tickers que la persona ya eligió, lo que favorece a todas las estrategias, y hoy no se avisa de ello. Para un producto educativo hay que enseñar que la rentabilidad sin su riesgo no permite comparar.

Cubre la feature **F4 (Backtesting)** y amplía la historia de usuario **HU-4**.

## What Changes

- **Métricas de riesgo:** volatilidad anualizada, ratio de Sharpe (con tasa libre de riesgo 0), ratio de Calmar, exposición (porcentaje medio del capital invertido) y número de operaciones ejecutadas, para la cartera real, cada estrategia y, si existen, las líneas base.
- **Criterio de ordenación seleccionable:** la comparativa puede ordenarse por TWR (por defecto, como hoy), Sharpe, Calmar o máximo drawdown.
- **Aviso de sesgo de selección:** la respuesta y la pantalla avisan de que las estrategias operan sobre tickers elegidos a posteriori y señalan los tickers que la simulación opera antes de su primera compra real.
- **Pantalla:** nuevas columnas en la comparativa, selector de criterio de ordenación, ayuda de cada métrica y el aviso de sesgo.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `backtesting`: nuevos requisitos de métricas de riesgo, criterio de ordenación, aviso de sesgo de selección y su presentación en pantalla. Los requisitos existentes no se reescriben: el comportamiento por defecto (ordenar por TWR) se mantiene.

## Fuera de alcance

- Tasa libre de riesgo configurable o tomada de datos de mercado (se usa 0).
- Sortino, VaR, beta, alfa u otras métricas avanzadas.
- Costes por operación en el backtest (prioridad 2 del análisis, change aparte).
- Optimización de parámetros, walk-forward o separación en muestra y fuera de muestra.
- Corregir el sesgo de selección (por ejemplo, simulando sobre un universo amplio); solo se avisa.

## Impact

- **API:** `POST /api/backtests` acepta el campo opcional `orden` en el cuerpo y añade campos a cada resultado y un aviso a la respuesta; compatible con los clientes actuales.
- **Dominio:** el motor de backtest calcula las nuevas métricas a partir de las rentabilidades diarias y las curvas que ya obtiene; no requiere nuevos datos de mercado ni cambios en la BD.
- **Frontend:** sección de backtesting.
- **Relación con otros changes:** si se aplica antes `anadir-benchmark-y-buy-hold`, las líneas base `buy-hold` e índice reciben también estas métricas; este change no depende de aquel.
- **readme.md:** secciones 1.2, 1.3, 3.2 (fórmulas), 4 (API), 2.6, 5 (HU-4) y 6 (BE-05, FE-04).

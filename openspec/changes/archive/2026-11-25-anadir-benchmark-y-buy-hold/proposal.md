# Proposal

## Why

La TWR de la cartera (F2) y la comparativa del backtest (F4) se muestran hoy sin ningún punto de referencia, de modo que la persona no puede saber si un 8 % anualizado es un buen resultado ni si una estrategia aporta algo frente a no hacer nada. Añadir un índice de referencia y una línea base de comprar y mantener da contexto a todas las rentabilidades del dashboard usando solo los datos de mercado que ya se obtienen.

Cubre las features **F2 (TWR)** y **F4 (Backtesting)** y amplía las historias de usuario **HU-2** y **HU-4**.

## What Changes

- **Índice de referencia en la rentabilidad (F2):** el cálculo de la TWR incluye la TWR del índice de referencia (SPY por defecto) sobre las mismas sesiones incluidas que la cartera, la diferencia en puntos porcentuales, la serie mensual y semanal comparada y una curva de valor base 100 de la cartera y del índice.
- **Curva de valor de la cartera en el panel de rentabilidad (F2):** el panel muestra la curva base 100 de la cartera superpuesta a la del índice, además de los indicadores actuales.
- **Líneas base en el backtest (F4):** la comparativa incluye dos filas de referencia que no son estrategias del catálogo: `buy-hold` (comprar y mantener los mismos tickers con el mismo capital y reparto) y el índice de referencia con todo el capital.
- **Propuestas de mejora (F4):** una estrategia que supera a la cartera real pero no a `buy-hold` se propone indicando que tampoco supera a comprar y mantener.
- **Degradación controlada:** si no hay datos del índice, la TWR y el backtest se devuelven igualmente sin la referencia y con un motivo, en lugar de fallar.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `rentabilidad-twr`: nuevos requisitos de TWR del índice de referencia, curva de valor base 100 y diferencia frente al índice; se amplían la respuesta HTTP y el panel en pantalla.
- `backtesting`: nuevos requisitos de líneas base `buy-hold` e índice de referencia en la comparativa; se modifican la comparativa, las propuestas de mejora, la respuesta HTTP y la sección en pantalla.

`estrategias-indicador` **no cambia**: `buy-hold` no se añade al catálogo de señales porque emitiría Compra permanentemente y contaminaría las operaciones recomendadas (F5).

## Fuera de alcance

- Elegir el índice desde la pantalla o la API; el índice se fija por configuración (SPY por defecto).
- Varios índices a la vez, índices compuestos o carteras de referencia ponderadas.
- Dividendos del índice (se usa el precio de cierre, coherente con la cartera, que tampoco los incluye).
- Métricas de riesgo (volatilidad, Sharpe, Calmar), que se tratan en el change `metricas-riesgo-backtest`.
- Alfa, beta o cualquier regresión frente al índice.

## Impact

- **API:** `GET /api/cartera/rentabilidad/twr` y `POST /api/backtests` añaden campos a su respuesta; no se elimina ni renombra ninguno, por lo que el cambio es compatible.
- **Datos de mercado:** el adaptador del proveedor de precios descarga y cachea también el OHLC diario del índice en la caché de precios diarios existente; no requiere entidades nuevas.
- **Configuración:** nueva variable de entorno con el ticker del índice de referencia.
- **Frontend:** panel de rentabilidad (nuevo gráfico de curva) y sección de backtesting (filas y curvas de referencia).
- **readme.md:** secciones 1.2, 1.3, 2.2, 3.2 (fórmulas), 4 (API), 5 (HU-2, HU-4) y 6 (tickets BE-03, FE-02, BE-05, FE-04).

# Spec Delta

## MODIFIED Requirements

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

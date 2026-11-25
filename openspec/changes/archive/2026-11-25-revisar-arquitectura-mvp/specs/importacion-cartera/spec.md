# Spec Delta

## MODIFIED Requirements

### Requirement: Precio de referencia
El sistema SHALL usar como precio de referencia el último precio de cierre diario disponible, sin ajustar por splits, para las posiciones abiertas y el precio de venta para las posiciones cerradas, y SHALL indicar que el precio no está disponible, sin calcular el rendimiento, cuando no pueda obtener ningún cierre de una posición abierta.

#### Scenario: Posición abierta
- **WHEN** se consulta una posición abierta de `MSFT` y el último cierre diario disponible, del 2025-03-07, es 410,25 USD
- **THEN** la posición tiene como precio de referencia 410,25 USD con la fecha 2025-03-07

#### Scenario: Posición cerrada
- **WHEN** se consulta una posición cerrada vendida a 150 USD
- **THEN** la posición tiene como precio de referencia 150 USD con la fecha de venta

#### Scenario: Cotización no disponible
- **WHEN** no se puede obtener ningún cierre para el ticker de una posición abierta
- **THEN** la posición se devuelve con precio de referencia y rendimiento vacíos y un motivo que indica que el precio no está disponible, y el resto de posiciones se devuelven con normalidad

#### Scenario: Sin cotización intradía
- **WHEN** se consulta una posición abierta de `MSFT` durante una sesión en curso cuyo cierre aún no existe
- **THEN** el precio de referencia es el cierre de la sesión anterior con su fecha, el mismo que usa el cálculo de la TWR

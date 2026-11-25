# Spec Delta

## MODIFIED Requirements

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

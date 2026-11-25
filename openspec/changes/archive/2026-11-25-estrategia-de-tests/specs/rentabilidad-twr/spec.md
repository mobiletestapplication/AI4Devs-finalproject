# Spec Delta

## ADDED Requirements

### Requirement: Flujos en días sin sesión
El sistema SHALL asignar una compra o una venta fechada en un día sin sesión bursátil, como un fin de semana o un festivo, a la primera sesión posterior a esa fecha, tanto para su aportación o retirada como para empezar o dejar de valorar la posición.

#### Scenario: Compra en sábado
- **WHEN** se compran 10 acciones a 100 USD el sábado 2025-03-08 en una cartera vacía y la acción cierra a 105 USD el lunes 2025-03-10
- **THEN** la compra es una aportación de 1.000 USD del lunes 2025-03-10 y la rentabilidad de esa sesión es 5 %

#### Scenario: Venta en domingo
- **WHEN** la cartera vale 1.100 USD al cierre del viernes 2025-03-07 y su única posición se vende por 1.120 USD el domingo 2025-03-09
- **THEN** la venta es una retirada del lunes 2025-03-10, la posición no se valora ese lunes y la rentabilidad de esa sesión es 1,82 %

#### Scenario: Festivo entre semana
- **WHEN** una compra está fechada en un día laborable sin datos de mercado para ningún ticker de la cartera
- **THEN** la compra se asigna a la siguiente sesión con datos

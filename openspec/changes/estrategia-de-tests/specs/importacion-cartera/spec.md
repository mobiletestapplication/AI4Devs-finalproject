# Spec Delta

## MODIFIED Requirements

### Requirement: Clasificación de la plusvalía
El sistema SHALL clasificar cada posición como Long-Term cuando entre la fecha de compra y la fecha de venta (o la fecha actual si está abierta) haya transcurrido más de un año, y como Short-Term en caso contrario, con independencia de que el rendimiento sea positivo o negativo, tomando el 28 de febrero como aniversario de una compra hecha un 29 de febrero.

#### Scenario: Venta en el aniversario de la compra
- **WHEN** una posición se compró el 2024-01-10 y se vendió el 2025-01-10
- **THEN** se clasifica como Short-Term

#### Scenario: Venta al día siguiente del aniversario
- **WHEN** una posición se compró el 2024-01-10 y se vendió el 2025-01-11
- **THEN** se clasifica como Long-Term

#### Scenario: Posición abierta
- **WHEN** una posición abierta se compró hace 200 días
- **THEN** se clasifica como Short-Term y su clasificación cambia a Long-Term cuando haya transcurrido más de un año desde la compra

#### Scenario: Compra un 29 de febrero
- **WHEN** una posición se compró el 2024-02-29
- **THEN** se clasifica como Short-Term si se vendió el 2025-02-28 y como Long-Term si se vendió el 2025-03-01

#### Scenario: Aniversario en año bisiesto
- **WHEN** una posición se compró el 2023-02-28
- **THEN** se clasifica como Short-Term si se vendió el 2024-02-28 y como Long-Term si se vendió el 2024-02-29

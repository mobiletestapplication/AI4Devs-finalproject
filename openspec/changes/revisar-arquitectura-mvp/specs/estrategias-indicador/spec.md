# Spec Delta

## ADDED Requirements

### Requirement: Histórico mínimo de los indicadores
El sistema SHALL exigir para calcular un indicador al menos tantas sesiones de histórico como su periodo en las medias móviles simples, y su periodo más 100 sesiones en el RSI y el ATR de Wilder, para que el arranque del suavizado no altere los valores mostrados, y SHALL emitir "Sin datos suficientes" con intensidad 0 cuando no se alcance ese mínimo.

#### Scenario: RSI con histórico insuficiente
- **WHEN** un ticker tiene 100 sesiones de histórico y la estrategia es `rsi` con periodo 14
- **THEN** su señal es "Sin datos suficientes" con intensidad 0, porque necesita 114 sesiones

#### Scenario: RSI con el mínimo exacto
- **WHEN** un ticker tiene 114 sesiones de histórico y la estrategia es `rsi` con periodo 14
- **THEN** su señal se calcula con normalidad

#### Scenario: Periodo personalizado
- **WHEN** la estrategia es `rsi` con periodo 21 y un ticker tiene 115 sesiones de histórico
- **THEN** su señal es "Sin datos suficientes", porque necesita 121 sesiones

#### Scenario: Medias móviles sin margen adicional
- **WHEN** la estrategia es `cruce-medias` con medias de 50 y 200 sesiones y un ticker tiene 200 sesiones de histórico
- **THEN** su señal se calcula con normalidad

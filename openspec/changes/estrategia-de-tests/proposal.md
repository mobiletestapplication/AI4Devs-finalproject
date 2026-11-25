# Proposal

## Why

Las specs vivas tienen 120 escenarios WHEN/THEN, pero la sección 2.6 del readme solo enumera ejemplos de tests, y nada garantiza que cada escenario tenga el suyo ni en qué nivel se prueba. Al traducir los escenarios a tests aparecen además tres huecos que impiden escribir el resultado esperado:
- cuándo es Long-Term una compra hecha un 29 de febrero;
- en qué sesión cuenta un flujo fechado en un día sin mercado;
- cómo se mide el capital inicial del backtest.

Cubre las features **F1, F2 y F4** (historias **HU-1, HU-2 y HU-4**) en las specs, y la estrategia de tests de **F1-F5**.

## What Changes

- **Estrategia de tests:** pirámide por niveles (unitarios de dominio, contrato, integración API + PostgreSQL con Testcontainers, componentes de frontend y E2E con Playwright), con reglas para decidir el nivel de cada escenario.
- **Trazabilidad automática:** cada test cita su escenario como `capability::Requirement::Scenario`, y un script de CI falla si un escenario no tiene test o si un test cita uno que no existe.
- **Determinismo:** reloj fijo, proveedor de precios de ficheros o fake con modos, tolerancias numéricas y tests de propiedades (neutralidad de la TWR, invariancia de prefijo del backtest).
- **Fixtures maliciosos generados en tiempo de test** para los rechazos de `endurecer-seguridad`.
- **Huecos resueltos en las specs:**
  - una compra del 29 de febrero es Long-Term desde el 1 de marzo del año siguiente;
  - un flujo en un día sin sesión cuenta en la sesión siguiente;
  - el capital inicial del backtest es el máximo capital invertido simultáneamente a coste de compra.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `importacion-cartera`: "Clasificación de la plusvalía" incorpora el caso del 29 de febrero y los años bisiestos.
- `rentabilidad-twr`: nuevo requisito de flujos en días sin sesión.
- `backtesting`: "Simulación de una estrategia" precisa que el capital inicial se mide a coste de compra.

## Fuera de alcance

- Escribir los tests: en la Entrega 1 solo se documenta la estrategia.
- Tests de rendimiento o de carga, de accesibilidad automatizados y mutation testing.
- Pruebas contra Yahoo en el CI normal: solo con un marcador opcional.
- Calendario bursátil oficial: el calendario de sesiones sigue derivándose de los datos (A5 de `revisar-arquitectura-mvp`).

## Impact

- **Specs:** dos MODIFIED y un ADDED. Ninguno de los requisitos modificados lo toca otro change abierto. Los escenarios existentes no cambian de resultado.
- **CI:** nuevo paso de trazabilidad de escenarios dentro del job `backend-calidad` (A14 de `revisar-arquitectura-mvp`), y `FECHA_ACTUAL_FIJA` solo en el compose de E2E.
- **readme.md:** secciones 2.4, 2.6, 3.2 (fórmulas), 5 (HU-1, HU-2, HU-4) y 6 (QA-01).

# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. T1-T8 remiten a design.md.

## 1. Tests (HU-1 a HU-5)

- [ ] 1.1 Reescribir la sección 2.6 con la pirámide y la regla de nivel de T1, el identificador `capability::Requirement::Scenario` y el script de trazabilidad de T2, y el determinismo de T3. Verificar que la tabla de niveles suma los volúmenes indicados y que se cita el job de CI.
- [ ] 1.2 Añadir a la sección 2.6 los casos calculados a mano y los tests de propiedades de T4, con sus valores: 29-F → Long-Term el 2025-03-01; 2023-02-28 → Long-Term el 2024-02-29; 21 % de neutralidad; compra a 101; 5 % y 1,82 % en días sin sesión; 10.000 USD de capital. Verificar que cada valor coincide con un escenario de spec.
- [ ] 1.3 Añadir a la sección 2.6 los casos de integración y de contrato de T5, el recorrido E2E de T6 y la tabla de fixtures maliciosos de T7 con la respuesta de cada uno. Verificar que la tabla de fixtures coincide con los escenarios de `endurecer-seguridad`.

## 2. Backend (HU-1, HU-2, HU-4)

- [ ] 2.1 Añadir a "Fórmulas clave" de la sección 3.2 la regla del 29 de febrero, la asignación de flujos a la sesión siguiente y el capital inicial del backtest a coste de compra. Verificar contra los tres deltas.

## 3. Historias de usuario (HU-1, HU-2, HU-4)

- [ ] 3.1 Añadir a los criterios de aceptación de HU-1 la compra del 29 de febrero, a los de HU-2 la compra en sábado (5 %) y a los de HU-4 el capital a coste (10.000 USD). Verificar que son resúmenes fieles de los escenarios.

## 4. DevOps y tickets (HU-1 a HU-5)

- [ ] 4.1 Añadir a la sección 2.4 el paso de trazabilidad dentro del job `backend-calidad`, `FECHA_ACTUAL_FIJA` solo en el compose de E2E y los umbrales de cobertura de T8. Verificar que coincide con A14 de `revisar-arquitectura-mvp` si ya está aplicado.
- [ ] 4.2 Ampliar QA-01 en la sección 6 con el script de trazabilidad, el generador de fixtures y el recorrido E2E. Verificar que referencia todas las HU.

## 5. Comprobación final

- [ ] 5.1 Ejecutar `openspec validate estrategia-de-tests --strict` y confirmar que no hay errores.
- [ ] 5.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs.

## Workflow follow-up

- Archivar con `/opsx:archive`: actualizará "Clasificación de la plusvalía" y "Simulación de una estrategia" y añadirá "Flujos en días sin sesión" a las specs vivas.

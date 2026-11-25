# Tasks

Entrega 1: todas las tareas son de documentación en `readme.md`; no se escribe código.

## 1. Base de datos (HU-2, HU-4)

- [ ] 1.1 Actualizar la descripción de `PRECIO_DIARIO` en la sección 3.2 para indicar que también cachea el índice de referencia. Verificar que la sección 3.1 no añade entidades nuevas y que el diagrama sigue coincidiendo con el de design.md.

## 2. Backend (HU-2, HU-4)

- [ ] 2.1 Ampliar las filas F2 y F4 de la tabla de la sección 1.2 con el índice de referencia, la curva base 100 y las líneas base `buy-hold` e índice. Verificar que el texto no contradice los deltas de `rentabilidad-twr` y `backtesting`.
- [ ] 2.2 Añadir a "Fórmulas clave" de la sección 3.2 la TWR del índice en las mismas sesiones, la diferencia en pp, la curva base 100 y la regla de compra de `buy-hold`. Verificar con los ejemplos de los escenarios: −1 % con los cierres 400 → 440 → 396, +11,00 pp y 20 acciones con 2.500 USD a 125 USD.
- [ ] 2.3 Documentar en la sección 4 los campos nuevos de `GET /api/cartera/rentabilidad/twr` y `POST /api/backtests`, con un ejemplo de respuesta que incluya el índice no disponible. Verificar que los códigos `404` para `buy-hold`, `409`, `422` y `503` coinciden con los escenarios de los deltas.
- [ ] 2.4 Actualizar en la sección 2.2 las filas "Motor TWR", "Motor de backtest" y "MarketData" con el índice y las líneas base. Verificar que se menciona la degradación sin índice (D4 de design.md).

## 3. Frontend (HU-2, HU-4)

- [ ] 3.1 Actualizar los puntos 2 (Rentabilidad) y 4 (Backtesting) de la sección 1.3: comparación con SPY y diferencia en verde o rojo, curvas de la cartera y del índice, columnas de índice y diferencia, etiqueta "Línea base" y trazo discontinuo. Verificar que cada elemento corresponde a un escenario de pantalla de los deltas.

## 4. Tests (HU-2, HU-4)

- [ ] 4.1 Añadir a la sección 2.6 los casos unitarios de la TWR del índice (−1 %, febrero sin inversión), la curva base 100 (110 y 99) y `buy-hold` (20 acciones), y el caso de integración del índice no disponible con `200 OK`. Verificar que cada caso cita el valor numérico de su escenario.

## 5. DevOps (HU-2, HU-4)

- [ ] 5.1 Documentar la variable `BENCHMARK_TICKER` (por defecto `SPY`) en las secciones 1.4 y 2.4 como variable de `.env.example`. Verificar que el valor por defecto coincide con design.md D3.

## 6. Historias de usuario y tickets (HU-2, HU-4)

- [ ] 6.1 Añadir a los criterios de aceptación de HU-2 la comparación con SPY (+11,00 pp), y a los de HU-4 las líneas base y la propuesta "queda 1,00 pp por debajo de comprar y mantener". Verificar que son resúmenes fieles de los escenarios.
- [ ] 6.2 Ampliar el título o la descripción de BE-03, FE-02, BE-05 y FE-04 en el backlog de la sección 6 y revisar sus estimaciones. Verificar que cada ticket referencia HU-2 o HU-4.

## 7. Comprobación final

- [ ] 7.1 Ejecutar `openspec validate anadir-benchmark-y-buy-hold --strict` y confirmar que no hay errores.
- [ ] 7.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen los deltas ni las specs vivas no afectadas, en especial que `estrategias-indicador` sigue sin `buy-hold` en su catálogo.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado, comprobando antes que el `readme.md` no contradice las specs actualizadas.

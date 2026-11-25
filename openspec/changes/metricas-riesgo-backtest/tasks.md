# Tasks

Entrega 1: todas las tareas son de documentación en `readme.md`; no se escribe código.

## 1. Backend (HU-4)

- [ ] 1.1 Ampliar la fila F4 de la tabla de la sección 1.2 con volatilidad, Sharpe, Calmar, exposición, número de operaciones, criterio de ordenación y aviso de sesgo. Verificar que coincide con el delta de `backtesting`.
- [ ] 1.2 Añadir a "Fórmulas clave" de la sección 3.2 las fórmulas de volatilidad (√252, desviación típica muestral), Sharpe con tasa libre de riesgo 0, Calmar y exposición. Verificar con los ejemplos de los escenarios: 16,29 %, 0,79, 0,48, 60 % y 80 %.
- [ ] 1.3 Documentar en la sección 4 el campo opcional `orden` de `POST /api/backtests`, con sus valores admitidos, la respuesta `400` y los campos nuevos de cada resultado, incluido el aviso de sesgo. Verificar que el ejemplo de respuesta incluye un valor no disponible con su motivo.
- [ ] 1.4 Actualizar la fila "Motor de backtest" de la sección 2.2. Verificar que menciona que el orden no afecta a las propuestas (D5 de design.md).

## 2. Frontend (HU-4)

- [ ] 2.1 Actualizar el punto 4 (Backtesting) de la sección 1.3 con las columnas nuevas, el selector de orden, las ayudas y el aviso de sesgo desplegable. Verificar que cada elemento corresponde a un escenario de "Métricas de riesgo en pantalla".

## 3. Tests (HU-4)

- [ ] 3.1 Añadir a la sección 2.6 los casos unitarios de volatilidad, Sharpe (incluida la volatilidad nula), Calmar (incluido el caso sin drawdown), exposición, recuento de operaciones y ordenación con valores no disponibles. Verificar que cada caso cita el valor de su escenario.

## 4. Historias de usuario y tickets (HU-4)

- [ ] 4.1 Añadir a los criterios de aceptación de HU-4 la ordenación por Sharpe y el aviso de sesgo con el ejemplo de `NVDA`. Verificar que son resúmenes fieles de los escenarios.
- [ ] 4.2 Ampliar la descripción de BE-05 y FE-04 en el backlog de la sección 6 y revisar sus estimaciones. Verificar que ambos referencian HU-4.

## 5. Comprobación final

- [ ] 5.1 Ejecutar `openspec validate metricas-riesgo-backtest --strict` y confirmar que no hay errores.
- [ ] 5.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs. Si `anadir-benchmark-y-buy-hold` ya está aplicado, confirmar que las líneas base también muestran las métricas nuevas.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado, comprobando antes que el `readme.md` no contradice las specs actualizadas.

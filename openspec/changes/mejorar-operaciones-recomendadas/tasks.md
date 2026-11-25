# Tasks

Entrega 1: todas las tareas son de documentación en `readme.md`; no se escribe código.

## 1. Backend (HU-5)

- [ ] 1.1 Ampliar la fila F5 de la tabla de la sección 1.2 con la cantidad sugerida por riesgo, la antigüedad de la señal, el filtro de señales recientes y el aviso de wash sale. Verificar que coincide con el delta de `operaciones-recomendadas`.
- [ ] 1.2 Añadir a "Fórmulas clave" de la sección 3.2 la fórmula de la cantidad sugerida, la de la antigüedad en sesiones y la regla de wash sale simplificada. Verificar con los ejemplos de los escenarios: 25 acciones, 10 acciones con 10,42, 4 sesiones y la fecha 2025-04-03.
- [ ] 1.3 Documentar en la sección 4 los parámetros `riesgo` y `antiguedad_max` de `GET /api/recomendaciones`, con sus rangos y la respuesta `400`, y un ejemplo de operación Comprar con los campos nuevos. Verificar que los rangos coinciden con el delta (0,1-5 y 0-250).
- [ ] 1.4 Actualizar la fila "Recomendaciones (F5)" de la sección 2.2. Verificar que menciona que el filtro se aplica antes del límite de 10.

## 2. Frontend (HU-5)

- [ ] 2.1 Actualizar el punto 5 (Operaciones recomendadas) de la sección 1.3 con la cantidad y el capital, el campo de riesgo, la etiqueta "Nueva", el filtro "Solo señales recientes" y el icono de wash sale. Verificar que cada elemento corresponde a un escenario de pantalla del delta.

## 3. Tests (HU-5)

- [ ] 3.1 Añadir a la sección 2.6 los casos unitarios de la cantidad (25, 10 y 0 con su motivo), la antigüedad (4 y 30 sesiones), el filtro (4 de 12) y la wash sale (pérdida reciente, ganancia y pérdida antigua), y los de integración de `400` por parámetros fuera de rango. Verificar que cada caso cita el valor de su escenario.

## 4. Historias de usuario y tickets (HU-5)

- [ ] 4.1 Añadir a los criterios de aceptación de HU-5 la compra con 25 acciones y riesgo del 1 %, y el aviso de wash sale con fecha 2025-04-03. Verificar que son resúmenes fieles de los escenarios.
- [ ] 4.2 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Ampliar la descripción de BE-06 y FE-05 en el backlog de la sección 6 y revisar sus estimaciones. Verificar que ambos referencian HU-5.

## 5. Comprobación final

- [ ] 5.1 Ejecutar `openspec validate mejorar-operaciones-recomendadas --strict` y confirmar que no hay errores.
- [ ] 5.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs, en especial que sin parámetros nuevos la selección y el orden siguen igual.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado, comprobando antes que el `readme.md` no contradice las specs actualizadas.

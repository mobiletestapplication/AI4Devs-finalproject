# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. Aplicar después de `revisar-arquitectura-mvp` y `endurecer-seguridad`. M1-M7 remiten a design.md.

## 1. Base de datos (HU-1)

- [ ] 1.1 Sustituir el erDiagram de la sección 3.1 por el de design.md, con `CARTERA_VIGENTE`, sin la columna `vigente` y con todas las restricciones. Verificar que el diagrama se renderiza y que cada CHECK de M3 aparece en él.
- [ ] 1.2 Reescribir la tabla de entidades y el párrafo de sustitución de la sección 3.2 con M1 y M2: los cuatro pasos de la transacción, `ON DELETE RESTRICT` y el borrado de la importación anterior. Verificar que coincide con el escenario "Sustitución de la cartera" de la spec viva.
- [ ] 1.3 Sustituir "Datos derivados (no persistidos)" de la sección 3.2 por la tabla de M5. Verificar que no queda ningún resultado calculado como persistido.
- [ ] 1.4 Actualizar DB-01 en la sección 6: `CARTERA_VIGENTE` en lugar del índice parcial, los CHECK de M3 y los tests de integración que esperan `IntegrityError` (segunda fila en `CARTERA_VIGENTE`, ticker `aapl$`, fila 1, `maximo < minimo`, borrado de la importación vigente). Verificar que cada CHECK tiene su test.

## 2. Backend (HU-1)

- [ ] 2.1 Sustituir el apartado "Formato del fichero de entrada" de la sección 3.2 por la tabla de M6. Verificar contra los tres requisitos del delta (tipos de celda, cantidades fraccionarias, columnas y filas vacías).
- [ ] 2.2 Sustituir "Fórmulas clave" de la sección 3.2 por M7. Si `revisar-arquitectura-mvp` y `estrategia-de-tests` ya añadieron fórmulas, conservar sus ejemplos sin duplicarlos. Verificar los ejemplos: 50 USD, Long-Term el 2025-01-11 y el 2025-03-01, 96 y 106.
- [ ] 2.3 Actualizar la fila "Ingesta XLSX" de la sección 2.2 y la tarea 4 de BE-01 con los tipos de celda, el máximo de 6 decimales, las columnas ignoradas y las filas vacías. Verificar que coinciden con el delta.

## 3. Tests e historia de usuario (HU-1)

- [ ] 3.1 Añadir a la sección 2.6 los casos del delta (`2024-01-10` como texto → importa; `10/01/2024` → `422`; `172,50` → `422`; 2,5 acciones → 50 USD; 0,1234567 → `422`; fila vacía saltada; fila a medias → `422`) y a HU-1 el caso de la fracción de acción. Verificar que cada caso cita su escenario.

## 4. Comprobación final

- [ ] 4.1 Ejecutar `openspec validate revisar-modelo-de-datos --strict` y confirmar que no hay errores.
- [ ] 4.2 Confirmar con `grep -n "vigente" readme.md` que no queda el índice único parcial y que el resto de secciones no contradice M1.

## Workflow follow-up

- Archivar con `/opsx:archive`: añadirá los tres requisitos a `importacion-cartera`.

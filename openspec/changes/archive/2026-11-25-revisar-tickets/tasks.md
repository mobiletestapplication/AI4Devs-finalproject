# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. Aplicar el último, después de los demás changes abiertos. K1-K7 remiten a design.md.

## 1. Tickets (HU-1 a HU-5)

- [x] 1.1 Reescribir la introducción de la sección 6 con la DoD común de K1. Verificar que los 5 puntos de K1 aparecen y que los tickets detallados solo añaden su DoD específica.
- [x] 1.2 Sustituir los tres tickets detallados por DB-01 (K3), BE-01b (K4) y FE-01 (K5), cada uno con tipo, HU, estimación, dependencias, tareas, criterios de aceptación y DoD. Verificar que cada criterio con identificador de escenario existe en una spec viva o en un delta aplicado.
- [x] 1.3 Sustituir el backlog resumido por la tabla de K6 y añadir el grafo de dependencias. Verificar que el grafo se renderiza, que cada dependencia de la tabla aparece en el grafo y que la suma de la Entrega 2 es 39 SP.

## 2. Producto (HU-1)

- [x] 2.1 Actualizar el párrafo "Flujo principal" de la sección 1.2 con los tickets de la Entrega 2 (OPS-01, DB-01, SEC-01, BE-01a, BE-01b, BE-02, BE-07, FE-01). Verificar que coincide con K6.

## 3. Comprobación final

- [x] 3.1 Comprobar con `grep -n "xlsx_parser\|UNIQUE parcial\|vigente WHERE\|última cotización" readme.md` que la sección 6 no conserva nombres ni decisiones antiguos.
- [x] 3.2 Ejecutar `openspec validate revisar-tickets --strict` y confirmar que no hay errores.

## Workflow follow-up

- Archivar con `/opsx:archive`; al no tener deltas, no modifica las specs vivas.

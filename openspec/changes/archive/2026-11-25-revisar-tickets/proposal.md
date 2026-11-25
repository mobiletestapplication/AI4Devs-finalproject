# Proposal

## Why

Los tres tickets detallados y el backlog de la sección 6 del readme no permiten completar el flujo principal de la Entrega 2:
- **Falta el endpoint de la Watchlist:** ningún ticket implementa `GET /api/cartera/posiciones`.
- **Dependencias incompletas:** FE-01 no depende del proveedor de precios.
- **OPS-01 está al final** aunque es el primer requisito de todos.
- **BE-01 no es un ticket pequeño:** con los controles de `endurecer-seguridad` supera los 5 SP.
- **Decisiones desactualizadas:** los tickets usan decisiones y nombres que ya han cambiado en los changes abiertos.
- **Retoques dispersos:** nueve changes retocan la sección 6 por separado.

Este change la reescribe de una vez como fuente única.

Cubre la planificación de **F1-F5** (historias **HU-1 a HU-5**). No cambia ningún requisito.

## What Changes

- **Definition of Done común** a todos los tickets, más lo específico de cada uno.
- **Tickets detallados:** DB-01 (esquema completo con `CARTERA_VIGENTE` y caché), BE-01b (parseo, validación y sustitución) y FE-01 (carga y Watchlist). Cada uno con tipo, HU, estimación, dependencias, tareas, criterios de aceptación con el identificador de sus escenarios y DoD.
- **Backlog reordenado con dependencias:**
  - OPS-01 pasa al principio;
  - nuevos SEC-01 (controles transversales), BE-01a (validación del contenedor), BE-07 (`GET /api/cartera/posiciones`), BE-08 (resumen y ejemplo) y REL-01 (publicación de imágenes);
  - BE-01 se divide en BE-01a y BE-01b.
- **Alcance de la Entrega 2:** OPS-01, DB-01, SEC-01, BE-01a, BE-01b, BE-02 (yfinance y ficheros), BE-07 y FE-01. Son 39 SP.
- **Las tareas de los demás changes que editaban la sección 6** pasan a remitir a este change.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
_Ninguna._ Solo cambia la planificación documentada en el readme (`skip_specs: true`).

## Fuera de alcance

- Fechas, sprints o velocidad: la estimación es en story points, para una sola persona.
- Detallar más allá del backlog los tickets de F2-F5.
- Cambiar requisitos o decisiones de diseño: el change parte de las specs y de los design.md de los changes abiertos.

## Impact

- **readme.md:** sección 6 completa y párrafo "Flujo principal" de la sección 1.2.
- **Otros changes:** sus tareas sobre la sección 6 (DB-01, BE-01, FE-01, BE-02 a BE-06, OPS-01, QA-01) pasan a "consolidada en `revisar-tickets`".
- **Orden:** aplicar el último, después de los nueve changes abiertos, para que la sección 6 refleje todas sus decisiones.

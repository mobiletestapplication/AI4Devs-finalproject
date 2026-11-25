# Proposal

## Why

El `readme.md` se editó a mano después de consolidarlo con las specs vivas y, al compararlo con ellas, presenta divergencias: textos que contradicen las specs (códigos HTTP comunes, literal del aviso legal), comportamientos que las specs definen y el readme omite, y reglas de validación que el readme presenta como comportamiento observable sin que ninguna spec las recoja. Como las specs son la fuente de verdad, el readme debe volver a derivarse de ellas antes de la Entrega 1.

Cubre la documentación de las features **F1-F5** y de las historias de usuario **HU-1 a HU-5**. No añade funcionalidad.

## What Changes

- **Contradicciones corregidas en el readme:**
  - "Códigos comunes" de la sección 4: `409` y `503` no se aplican a todos los endpoints (`GET /api/estrategias` no requiere cartera ni proveedor y `GET /api/cartera/posiciones` degrada por posición en lugar de responder `503`).
  - Literal del aviso legal de HU-5 alineado con el de la sección 1.3 y la spec.
- **Omisiones completadas con lo que dicen las specs:** tabla de la sección 1.2 (F2-F5), pantallas de la sección 1.3, códigos por endpoint de la sección 4 y detalles del OpenAPI de TWR y backtest.
- **Reglas solo presentes en el readme:** el máximo de 10.000 filas, el patrón de ticker, precios > 0, el rechazo de `.xlsm`/`vbaProject.bin` y los límites contra zip bomb se mantienen como **controles de diseño y seguridad pendientes de spec**, sin prometer códigos HTTP que las specs no definen.
- **Ediciones a mano conservadas:** las mejoras de redacción sin conflicto con las specs (definición de TWR en la sección 1.1, formato) se mantienen.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
_Ninguna._ El change no modifica comportamiento especificado: solo alinea el `readme.md` con las specs vivas, por lo que declara `skip_specs: true`.

## Fuera de alcance

- Modificar las specs vivas o formalizar en ellas las reglas de validación que hoy solo están en el readme (decisión tomada: quedan como controles de diseño pendientes de spec).
- Reflejar en el readme los changes en curso (`anadir-benchmark-y-buy-hold`, `metricas-riesgo-backtest`, `mejorar-operaciones-recomendadas`, `resumen-cartera-y-ejemplo`); cada uno actualizará el readme al aplicarse.
- Cambiar `prompts.md`, salvo registrar el prompt de este change si se desea.
- Rediseñar secciones del readme que ya coinciden con las specs.

## Impact

- **Ficheros:** solo `readme.md`, secciones 1.2, 1.3, 2.2, 2.5, 4 (tabla, códigos comunes y OpenAPI), 5 (HU-5) y 6 (BE-01).
- **Código, API, BD y specs:** sin cambios.

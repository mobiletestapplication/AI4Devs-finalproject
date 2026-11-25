# Design

## Context

Ver proposal.md (Why). Fuentes comparadas: las cinco specs vivas de `openspec/specs/` (fuente de verdad) y el `readme.md` en el estado del commit `45bdf5d`. Las ediciones a mano desde la consolidación (`37ea8da`) son de redacción y formato. Las divergencias detectadas vienen sobre todo de la propia consolidación y del detalle añadido después en las secciones 2.5, 4 y 6.

## Goals / Non-Goals

**Goals:**
- Que ninguna afirmación del readme contradiga una spec viva.
- Que el readme no presente como comportamiento observable nada que no esté en una spec.
- Conservar las ediciones a mano que no contradicen las specs.

**Non-Goals:**
- Copiar las specs al readme: el readme resume y enlaza; el detalle completo sigue en `openspec/specs/`.
- Incorporar los changes en curso.

## Catálogo de divergencias

Tipos: **C** = contradicción, **O** = omisión relevante, **E** = regla solo del readme.

| ID | Tipo | Sección del readme | Readme dice | Spec viva dice | Resolución |
|---|---|---|---|---|---|
| D1 | C | 4, "Códigos comunes" | `409` en todos los endpoints salvo `GET /cartera/posiciones`; `503` si el proveedor no responde, en general | `GET /api/estrategias` (catálogo) no depende de cartera ni de proveedor; `GET /api/cartera/posiciones` devuelve `200` con precio y rendimiento vacíos y motivo por posición (importacion-cartera, "Cotización no disponible") | Reescribir la frase indicando a qué endpoints aplica cada código |
| D2 | C | 5, HU-5 | Aviso "No constituye asesoramiento financiero" | operaciones-recomendadas exige el aviso de que no constituye asesoramiento; la sección 1.3 y estrategias-indicador usan "Las señales son orientativas y no constituyen asesoramiento financiero" | Usar el literal de la sección 1.3 |
| D3 | O | 4, tabla y códigos | Sin códigos específicos por endpoint | `404` si el ticker del histórico no está en la cartera (estrategias-indicador); `400` si falta la estrategia en recomendaciones (operaciones-recomendadas); `422` por tickers sin histórico en TWR (rentabilidad-twr) | Añadir los tres casos |
| D4 | O | 4, OpenAPI `/api/backtests` | "Sin cuerpo se simulan todas las estrategias con sus parámetros por defecto" | Sin cuerpo tampoco se genera la propuesta de compras contra la señal (backtesting, "Backtest sin estrategia seleccionada") | Completar la descripción |
| D5 | O | 4, OpenAPI `Metricas` | `twr_anualizada` anulable sin motivo | La TWR anualizada no aplica con periodos inferiores a 365 días (backtesting, "Métricas de las operaciones reales") | Documentar cuándo es `null` |
| D6 | O | 1.2, F2 | Valoración diaria sin mencionar las abiertas | Las posiciones abiertas aportan su ganancia o pérdida no realizada (rentabilidad-twr, "Valoración diaria") | Añadirlo |
| D7 | O | 1.2, F3 | Señales Compra, Venta o Mantener | También "Sin datos suficientes" con intensidad 0, e histórico de señales por ticker (estrategias-indicador) | Añadirlo |
| D8 | O | 1.2, F4 | "Simula todas las estrategias del catálogo"; "propone mejoras" | La estrategia seleccionada usa sus parámetros y el resto los de defecto; las posiciones abiertas se valoran al último cierre; tres tipos de mejora: estrategia que supera a la real, venta ST con ganancia a ≤ 30 días de LT y compras contra la señal (backtesting) | Precisar la simulación y enumerar las mejoras |
| D9 | O | 1.2, F5 | Sin precisar el universo ni el motivo | Solo tickers con posición abierta, señales Mantener y "Sin datos suficientes" excluidas, motivo con el valor del indicador y fecha de la sesión usada (operaciones-recomendadas) | Añadirlo |
| D10 | O | 1.3, punto 1 | Carga sin respuesta visible | Indicador de progreso y mensaje de éxito con el número de posiciones; la Watchlist conserva la cartera anterior si hay errores (importacion-cartera) | Añadirlo |
| D11 | O | 1.3, punto 2 | — | Porcentajes con dos decimales, fechas de inicio y fin, recálculo tras importar sin recargar (rentabilidad-twr) | Añadirlo |
| D12 | O | 1.3, punto 3 | "Validados antes de calcular" | Error junto al campo sin recalcular; el gráfico muestra los umbrales o las medias de la estrategia (estrategias-indicador) | Precisarlo |
| D13 | O | 1.3, punto 4 | Comparativa sin columnas | Columnas TWR acumulada y anualizada, máximo drawdown, % de aciertos y factor de beneficio; botón deshabilitado durante el cálculo; mensaje de error con opción de reintentar (backtesting) | Añadirlo |
| D14 | O | 1.3, punto 5 | Lista fija | Recálculo al cambiar la estrategia indicando cuál se aplica; mensajes cuando hay menos de 10 operaciones o ninguna; fecha de paso a Long-Term al pasar el cursor por el aviso fiscal (operaciones-recomendadas) | Añadirlo |
| D15 | E | 2.5, "Validación de datos" | Patrón de ticker `^[A-Z.\-]{1,10}$`, precios > 0 | La spec solo exige normalizar a mayúsculas y rechazar filas no válidas, con ejemplos de cantidad 0, venta anterior a compra, venta incompleta y fechas futuras | Mantener como control de diseño pendiente de spec |
| D16 | E | 2.5, "Fichero malicioso" y "Zip bomb" | `.xlsm` y `vbaProject.bin` → `415`; límite descomprimido, número de entradas, máx. 10.000 filas, timeout | La spec define `415` para "no es un XLSX" y `413` para más de 5 MB; nada sobre macros, filas ni descompresión | Mantener como controles pendientes de spec; conservar solo los códigos que la spec define (`413` por 5 MB) |
| D17 | E | 2.2, "Ingesta XLSX"; 6, BE-01 tarea 4 | "cantidad y precios > 0" como regla de validación | Ver D15 | Marcar "precios > 0" como control de diseño, igual que en la sección 2.5 |

## Decisions

### D-a. Convención para las reglas solo del readme
Las reglas de D15-D17 se mantienen en la sección 2.5 con la marca *"(control de diseño, pendiente de spec)"* y una nota al pie de la tabla que explica que no forman parte de los requisitos observables y que se formalizarán con un change si se quieren garantizar con un código HTTP.
- **Alternativa descartada:** formalizarlas ya en `importacion-cartera`. Lo descartó la persona: se mantienen como controles de diseño.
- **Alternativa descartada:** eliminarlas. Se perderían controles de seguridad documentados.
- **Sacrificio:** hasta que exista ese change, los tests de esas reglas no se pueden derivar de un escenario de spec.
- **Actualización:** el change `endurecer-seguridad` formaliza estas reglas en `importacion-cartera` y en la nueva spec `seguridad-api`. Si `endurecer-seguridad` ya está aplicado cuando se aplique este change, se omiten las marcas de D15-D17; si se aplica después, sus tareas las quitan.

### D-b. El readme resume; no duplica escenarios
Las omisiones (D3-D14) se resuelven con frases cortas que citan la spec, no copiando escenarios. Así se reduce la superficie de divergencia futura.

### D-c. Base de la comparación
Se compara contra las specs vivas y no contra los changes en curso. Al aplicarse, cada uno de esos changes actualizará el readme según su `tasks.md`.

## Risks / Trade-offs

- [Al aplicar los changes en curso pueden reaparecer divergencias] → cada uno ya incluye una tarea final de comprobación del readme contra las specs.
- [Una persona puede editar el readme a mano otra vez] → la sección 1.2 recuerda que las specs son la fuente de verdad; el checklist de tasks.md sirve para repetir la revisión.

## Migration Plan

No aplica: solo cambia documentación.

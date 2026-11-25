# Proposal

## Why

El modelo de datos de la sección 3 del readme garantiza *como mucho* una cartera vigente, pero no *exactamente* una, y le faltan restricciones que las specs ya exigen. Por ejemplo:
- el patrón de ticker que añade `endurecer-seguridad`;
- la unicidad de la fila dentro de una importación;
- la coherencia de los precios en caché.

El formato del XLSX tampoco dice qué tipos de celda se admiten, si la cantidad puede ser fraccionaria ni qué ocurre con las columnas extra y las filas vacías. Sin eso, el parser y sus tests no tienen un resultado esperado.

Cubre la feature **F1 (Importación y Watchlist)** y la historia **HU-1**.

## What Changes

- **Cartera vigente exactamente única:** nueva tabla de una sola fila, `CARTERA_VIGENTE`, que apunta a la importación vigente. Sustituye al índice único parcial sobre `IMPORTACION.vigente`. La importación anterior se borra en la misma transacción.
- **Restricciones nuevas:**
  - **`POSICION`:** `UNIQUE (importacion_id, fila)`, CHECK del patrón de ticker y de la fila.
  - **`IMPORTACION`:** CHECK de los recuentos.
  - **`PRECIO_DIARIO`:** CHECK de precios positivos y de `maximo >= minimo`.
- **Formato del XLSX (spec):**
  - **tipos de celda:** celdas nativas de fecha y número más texto ISO `AAAA-MM-DD` y número con punto decimal;
  - **cantidades fraccionarias:** hasta 6 decimales;
  - **columnas y filas:** las columnas adicionales se ignoran y las filas totalmente vacías se saltan.
- **Documentación:**
  - qué se guarda y qué se calcula bajo demanda;
  - el `erDiagram` completo;
  - las fórmulas del dominio, entre ellas RSI y ATR de Wilder, la convención temporal de la rentabilidad diaria y la anualización según GIPS.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `importacion-cartera`: nuevos requisitos de tipos de celda admitidos, cantidades fraccionarias, columnas adicionales y filas vacías.

## Fuera de alcance

- Historial de importaciones, deshacer una importación y detección de ficheros duplicados.
- Persistir resultados calculados (TWR, señales, backtests, recomendaciones).
- Formatos de fecha o número locales como texto (`DD/MM/AAAA`, coma decimal).
- Varias hojas o carteras en un mismo fichero.

## Impact

- **Modelo de datos:** nueva entidad `CARTERA_VIGENTE`; `IMPORTACION` pierde `vigente`. No hay migración incremental, porque todavía no hay código: la migración inicial (DB-01) nace con este esquema.
- **API:** sin cambios de contrato. "Sin cartera importada" pasa a ser la ausencia de la fila de `CARTERA_VIGENTE`.
- **Otros changes:** el diagrama incluye `cierre_sin_ajustar` y `COBERTURA_PRECIO` de `revisar-arquitectura-mvp` y el patrón de ticker de `endurecer-seguridad`. Aplicar después de ambos.
- **readme.md:** secciones 3.1, 3.2, 2.2 (Ingesta XLSX) y 6 (DB-01, BE-01).

# Proposal

## Why

La pantalla de cartera (F1) es hoy una tabla de posiciones sin ninguna vista de conjunto: la persona no ve cuánto vale su cartera, cuánto ha ganado o perdido en total ni cuánto de lo realizado tributaría como Short-Term o Long-Term en cada año, que es lo que da utilidad práctica a la clasificación ST/LT. Tampoco ve de qué fecha son los datos de mercado que alimentan todas las cifras, y quien prueba el dashboard por primera vez, como un evaluador, tiene que preparar su propio XLSX antes de ver nada.

Cubre la feature **F1 (Importación y Watchlist con ST/LT)** y la funcionalidad secundaria **S3 (plantilla XLSX descargable)**, y amplía la historia de usuario **HU-1**.

## What Changes

- **Resumen de la cartera:** valor actual, capital invertido en las posiciones abiertas, P&L no realizado en USD y en porcentaje, P&L realizado y número de posiciones abiertas y cerradas.
- **Ganancias realizadas por año fiscal:** para cada año natural de venta, ganancias, pérdidas y resultado neto separados en Short-Term y Long-Term.
- **Fecha de los datos de mercado:** fecha y hora de la cotización más reciente usada, con aviso si tiene más de 5 días naturales.
- **Nuevo endpoint `GET /api/cartera/resumen`.**
- **Cartera de ejemplo descargable:** nuevo endpoint `GET /api/cartera/ejemplo`, que devuelve un XLSX válido con posiciones abiertas y cerradas, ST y LT y con ganancia y pérdida. Sirve también como plantilla (S3).
- **Pantalla:** cabecera de resumen sobre la Watchlist, tabla fiscal por año, fecha de los datos siempre visible y enlace de descarga de la cartera de ejemplo.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `importacion-cartera`: nuevos requisitos de resumen de la cartera, ganancias realizadas por año fiscal, fecha de los datos de mercado, consulta del resumen por HTTP, cartera de ejemplo descargable y su presentación en pantalla. Los requisitos existentes no cambian.

## Fuera de alcance

- Cálculo de impuestos, tipos impositivos o compensación de pérdidas entre años; solo se agregan los resultados por año y tipo de plusvalía.
- Año fiscal distinto del año natural.
- Importar la cartera de ejemplo con un clic sin descargarla (se descarga y se carga con el control existente).
- Plantilla vacía separada: la cartera de ejemplo cumple esa función.
- Mostrar la fecha de los datos en el resto de secciones; aquí solo se define en la cabecera de la cartera, que es visible en todo el dashboard.

## Impact

- **API:** dos endpoints nuevos de solo lectura, `GET /api/cartera/resumen` y `GET /api/cartera/ejemplo`; los existentes no cambian.
- **Dominio:** el resumen agrega el rendimiento y la clasificación ST/LT que ya se calculan por posición.
- **Ficheros:** el XLSX de ejemplo se versiona en el repositorio y se reutiliza como fixture del seed (DB-01) y de los tests.
- **Frontend:** cabecera de la pantalla de cartera y estado vacío.
- **readme.md:** secciones 1.2 (F1 y S3), 1.3, 2.2, 2.5, 2.6, 3.2, 4 (API), 5 (HU-1) y 6 (DB-01, BE-01, FE-01 y backlog).

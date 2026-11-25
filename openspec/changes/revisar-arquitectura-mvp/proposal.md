# Proposal

## Why

La arquitectura de la sección 2 del `readme.md` (monolito modular con puertos y adaptadores) es adecuada para un MVP desarrollado por una sola persona, pero al contrastarla con las specs vivas deja sin resolver decisiones que afectan a todas las features. Falta decidir:
- qué precio valora las posiciones abiertas;
- cómo se tratan los splits en los datos de mercado;
- dónde se usa `Decimal` y dónde float;
- cuándo se refresca la caché de precios, con qué rango y con qué calendario de sesiones;
- cómo se inyecta la fecha actual;
- cómo se traducen los errores de dominio a HTTP;
- dónde se despliega.

Si no se fijan antes de la Entrega 2, cada feature las resolverá de forma distinta.

Cubre transversalmente las features **F1-F5** y las historias de usuario **HU-1 a HU-5**.

## What Changes

- **Patrón confirmado:** se mantiene el monolito modular, con un dominio puro separado de los adaptadores por puertos, y se documenta la comparativa con microservicios. Las fronteras del dominio se hacen cumplir en CI con import-linter.
- **Precio de referencia = último cierre diario:** las posiciones abiertas se valoran con el último cierre disponible y su fecha, la misma fuente que la TWR, las señales y las recomendaciones; no se piden cotizaciones intradía. Se aclara la spec `importacion-cartera`.
- **Dos series de precios:** cierre sin ajustar para valorar (coherente con los precios del XLSX) y OHLC ajustado por splits para indicadores, backtest e histórico de señales. La caché de precios añade la columna del cierre sin ajustar.
- **Servicio de datos de mercado:** rango de descarga con calentamiento, calendario de sesiones derivado de los datos y política de refresco de la última sesión.
- **Puerto `Reloj`** para la fecha actual y **mapeo centralizado** de las excepciones de dominio a códigos HTTP.
- **Frontera entre `Decimal` y float:** `Decimal` para importes y cantidades, float64 para series de rentabilidades e indicadores, con redondeo explícito al serializar.
- **Despliegue solo local** con `docker compose`; se retira el despliegue opcional en un PaaS.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `importacion-cartera`: el requisito "Precio de referencia" pasa a definir el último cierre diario disponible, con la fecha de esa sesión, en lugar de una "última cotización" sin precisar.

## Fuera de alcance

- Microservicios, colas de trabajos o backtests asíncronos.
- Cotizaciones intradía.
- Despliegue público, autenticación o modo de demo de solo lectura.
- Ajustar las cantidades y los precios del XLSX cuando hay un split durante la tenencia: se documenta como limitación.
- Ajuste por dividendos de cualquier serie.
- Implementar código: en la Entrega 1 solo se actualiza la documentación.

## Impact

- **Spec:** delta MODIFIED en `importacion-cartera` ("Precio de referencia"). Ningún escenario existente cambia de resultado.
- **Modelo de datos:** `PRECIO_DIARIO` gana `cierre_sin_ajustar`. El resto del OHLC almacenado es el ajustado por splits.
- **Adaptador de precios:** debe obtener también los eventos de split para reconstruir el cierre sin ajustar.
- **readme.md:** secciones 0.4, 1.2 (F1), 2.1, 2.2, 2.4, 2.6, 2.7, 3.1, 3.2 y 6 (DB-01, BE-02).
- **Orden:** aplicar después de `alinear-readme-con-specs`, que edita algunas de las mismas secciones. Su divergencia D1 (códigos `409`/`503` comunes) es coherente con el mapeo de errores de este change.

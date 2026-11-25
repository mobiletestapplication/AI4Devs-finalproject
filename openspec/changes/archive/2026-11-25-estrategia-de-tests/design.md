# Design

## Context

Ver proposal.md (Why) y los tres deltas. Punto de partida:
- **Specs vivas:** 5 specs con 39 requisitos y 120 escenarios; los changes abiertos añaden o modifican unos 140 más.
- **Arquitectura de `revisar-arquitectura-mvp`:** dominio puro, puertos (`Reloj`, `ProveedorPrecios`, `IndicadoresTecnicos`…), proveedor de ficheros, TA-Lib detrás de un puerto, CI con Testcontainers y E2E con el proveedor de ficheros (A14).
- **`endurecer-seguridad`:** define los fixtures maliciosos y sus códigos.

## Goals / Non-Goals

**Goals:**
- Que cada escenario de spec tenga exactamente un test identificable y que el CI lo compruebe.
- Tests deterministas: sin red, sin fecha real, sin dependencia del orden de ejecución.

**Non-Goals:**
- Rendimiento, carga, accesibilidad automatizada y mutation testing.

## Decisions

### T1. Pirámide y nivel de cada escenario
| El escenario describe… | Nivel | Herramienta | Volumen aproximado |
|---|---|---|---|
| un cálculo de dominio | Unitario | pytest con datos en memoria | ~90 |
| un adaptador frente a datos externos | Contrato | pytest con fixtures de referencia | ~15 |
| una petición y su respuesta HTTP | Integración | pytest + httpx + Testcontainers (`postgres:16`) | ~60 |
| lo que la persona ve | Componente | Vitest + Testing Library + MSW | ~45 |
| un recorrido de varias pantallas | E2E | Playwright contra `docker compose` | ~10 |

- **Regla:** un escenario se prueba en el nivel más bajo que puede observar su THEN. Los escenarios HTTP que también incluyen un cálculo se prueban en los dos niveles: en integración solo se comprueba el código y la forma de la respuesta.
- **Alternativa descartada:** probar todos los escenarios por HTTP. Serían lentos, con fallos difíciles de localizar y sin cubrir las fronteras numéricas.

### T2. Trazabilidad automática escenario → test
- **pytest:** `@pytest.mark.escenario("importacion-cartera::Clasificación de la plusvalía::Compra un 29 de febrero")`.
- **Vitest y Playwright:** el mismo identificador al principio del título del test.
- **Script `tests/trazabilidad.py`:** lee `openspec/specs/**/spec.md` y la lista de tests recogidos (`pytest --collect-only` y los informes JSON de Vitest y Playwright).
  - Falla si un escenario no tiene test o si un test cita un escenario inexistente.
  - Se ejecuta en el job `backend-calidad` del CI (A14 de `revisar-arquitectura-mvp`).
- **Changes en curso:** al aplicar un change se añaden los tests de sus deltas; al archivarlo, el script los exige.
- **Alternativa descartada:** una matriz manual en el readme. Se queda obsoleta en el primer cambio.

### T3. Determinismo
- **Reloj:** `Reloj` fijo en unitarios e integración. En E2E, la variable `FECHA_ACTUAL_FIJA` solo existe en el compose de tests. El adaptador del reloj la ignora fuera de ese entorno, y la API no arranca si aparece en el modo demo.
- **Precios:** proveedor de ficheros CSV en integración y E2E. Para los errores, un proveedor fake con los modos `normal`, `caido` y `ticker_sin_datos`, que cuenta las llamadas para probar la caché.
- **Tolerancias:** rentabilidades e indicadores con `pytest.approx(abs=1e-9)` (TA-Lib frente a referencias, 1e-6); importes `Decimal` comparados de forma exacta.
- **Aislamiento de la BD:** un contenedor por sesión de pytest, migrado con `alembic upgrade head`, y cada test en una transacción que se revierte.
- **Orden:** `pytest-randomly` para detectar dependencias ocultas entre tests.

### T4. Casos calculados a mano y tests de propiedades
Además de los ejemplos de cada escenario:
- **ST/LT en años bisiestos:** delta de `importacion-cartera`: 29 de febrero → Long-Term desde el 1 de marzo; compra el 2023-02-28 → Long-Term el 2024-02-29.
- **TWR neutral frente a aportaciones** (Hypothesis): con una serie de precios y aportaciones aleatorias, multiplicar todas las cantidades por k > 0, o cambiar el importe de las compras posteriores manteniendo los precios, no cambia la TWR.
- **Backtest sin sesgo de anticipación:**
  - **ejemplo:** señal al cierre de t a 100 y apertura de t+1 a 101 → compra a 101;
  - **propiedad de invariancia de prefijo:** simular con la serie completa y con la serie recortada en el día d da las mismas decisiones hasta d.
- **Flujos en días sin sesión:** delta de `rentabilidad-twr`: compra en sábado → 5 % el lunes; venta en domingo → 1,82 %.
- **Capital inicial a coste:** delta de `backtesting`: A + B = 10.000 USD.
- **Fronteras de las reglas:** RSI = 30 → Mantener; medias iguales → Mantener; 30 días exactos hasta Long-Term → con aviso fiscal; 10.000 filas → `201`.
- **Alternativa descartada:** solo ejemplos fijos. No detectan una mirada al futuro que no afecte a los ejemplos elegidos.

### T5. Integración y contrato
- **Integración:** un test por escenario HTTP de cada spec. Además, cuatro casos de arquitectura que no salen de ningún escenario:
  - atomicidad de la sustitución, forzando un error a mitad de la inserción;
  - la caché evita una segunda llamada al proveedor;
  - con el proveedor caído y la caché suficiente se responde `200` (A11);
  - la barra del día en curso no se guarda.
- **Contrato:**
  - el proveedor de ficheros siempre;
  - yfinance solo con `pytest -m red`, nunca en el CI normal;
  - TA-Lib frente a la tabla de StockCharts para RSI(14) y ATR(14);
  - reconstrucción del cierre sin ajustar con un split 10:1 (cierre ajustado 120 → sin ajustar 1.200).

### T6. E2E (flujo principal)
Un recorrido por cada historia de usuario, contra `docker compose` con el proveedor de ficheros y `FECHA_ACTUAL_FIJA`:
1. estado vacío;
2. carga correcta con la Watchlist;
3. rentabilidad;
4. estrategias con el gráfico de un ticker;
5. backtest;
6. recomendaciones con el aviso legal;
7. errores por fila con la cartera anterior intacta;
8. confirmación de sustitución.

Traza, vídeo y capturas como artefactos del CI cuando falla.

### T7. Fixtures maliciosos generados
`tests/fixtures/generar.py` crea en tiempo de test los ficheros de `endurecer-seguridad`:
- más de 5 MB;
- zip bomb con 2 GB declarados (se comprueba además que la memoria máxima no pasa de 100 MB);
- proporción de compresión 300 KB → 40 MB;
- 1.500 entradas;
- `vbaProject.bin`;
- OLE;
- XXE;
- `externalLinks/`;
- CSV renombrado;
- 10.001 y 10.000 filas;
- ticker `=HYPERLINK(…)`, de 500 caracteres y `<img onerror>`.

- **Alternativa descartada:** versionar los binarios. Los antivirus del CI los marcarían y no quedaría documentado cómo se construye cada caso.

### T8. Umbrales del CI
- Cobertura de líneas ≥ 95 % en `domain/` y ≥ 85 % en el resto del backend.
- Script de trazabilidad en verde.
- Sin tests marcados `red` en el pipeline normal.
- **Sacrificio:** los umbrales de cobertura no garantizan aserciones útiles. La trazabilidad por escenario compensa en parte.

## Risks / Trade-offs

- [Los títulos de los escenarios cambian al modificar una spec y rompen la trazabilidad] → el script indica el escenario renombrado más parecido; renombrar un escenario obliga a renombrar su test en el mismo change.
- [Hypothesis genera casos lentos o inestables] → se limitan los ejemplos por test y se guarda la base de ejemplos de Hypothesis en la caché del CI.
- [Testcontainers no está disponible en algún entorno local] → la integración se puede ejecutar contra el `db` del compose con una variable, pero el CI siempre usa Testcontainers.

## Migration Plan

No hay código todavía. Los tests se escriben a partir de la Entrega 2, empezando por los de HU-1 (flujo principal).

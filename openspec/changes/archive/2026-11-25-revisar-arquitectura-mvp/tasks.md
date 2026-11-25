# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. Aplicar después de `alinear-readme-con-specs`. Las referencias A1-A9 remiten a design.md.

## 1. Base de datos (HU-1, HU-2)

- [x] 1.1 Actualizar el erDiagram de la sección 3.1 y la fila de `PRECIO_DIARIO` de la sección 3.2 con `cierre_sin_ajustar` y la indicación de que el OHLC está ajustado por splits (A4). Verificar que el diagrama coincide con el de design.md y se renderiza sin errores.
- [x] 1.2 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Añadir a DB-01, en la sección 6, la columna `cierre_sin_ajustar` con `CHECK > 0` y la tabla `COBERTURA_PRECIO` con `CHECK hasta >= desde`. Verificar que los tipos son `NUMERIC` y `date`.
- [x] 1.3 Añadir `COBERTURA_PRECIO` al erDiagram de la sección 3.1 y a la tabla de entidades de la sección 3.2, explicando por qué no basta con las filas de `PRECIO_DIARIO` (A5). Verificar que coincide con el diagrama de design.md.

## 2. Backend (HU-1 a HU-5)

- [x] 2.1 Sustituir el diagrama y el texto del patrón de la sección 2.1 por el diagrama, la comparativa con microservicios, los beneficios y los sacrificios de A1-A2. Verificar que el Mermaid se renderiza y que aparecen los siete puertos.
- [x] 2.2 Actualizar la tabla de la sección 2.2 con el servicio de datos de mercado (A5), el puerto `Reloj` (A6), el mapeo de errores (A7) y el contrato de import-linter. Verificar que cada componente nuevo aparece también en el diagrama.
- [x] 2.3 Cambiar en la fila F1 de la sección 1.2 y en los "Datos derivados" de la sección 3.2 "última cotización" por "último cierre diario sin ajustar, con su fecha" (A3), y añadir la limitación de splits durante la tenencia a las "Decisiones de alcance" (A4). Verificar contra el delta de `importacion-cartera`.
- [x] 2.4 Añadir a "Fórmulas clave" de la sección 3.2 la reconstrucción `cierre_sin_ajustar = cierre × F(fecha)` con el ejemplo del split 10:1 (120,00 → 1.200,00) y qué serie usa cada feature. Verificar que coincide con A4.
- [x] 2.5 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Ampliar BE-02 en el backlog de la sección 6 con los eventos de split, la normalización pura a dos series, el rango con calentamiento, el calendario, la cobertura, la barra del día en curso, la invalidación por split y los reintentos. Verificar que referencia HU-1 a HU-5.
- [x] 2.6 Sustituir en las secciones 2.2 y 2.7 "yfinance (adaptador intercambiable: Stooq / Alpha Vantage)" por la decisión A10: yfinance como único proveedor real más un proveedor de ficheros, con la tabla comparativa resumida y el contrato del puerto. Verificar que no queda Stooq ni Alpha Vantage como respaldo automático.
- [x] 2.7 Añadir a la sección 4 la regla de caché desactualizada y la tabla de respuestas con el proveedor caído (A11), la diferencia entre `422` y `503`, y el cuerpo `application/problem+json` con `Retry-After`. Verificar contra los escenarios "Proveedor de mercado no disponible" de cada spec.

- [x] 2.8 Sustituir la tabla de componentes de la sección 2.2 por la de design.md ("Componentes principales") y añadir TA-Lib ≥ 0.6.5 a la sección 2.7 con la justificación de A12. Verificar que cada componente aparece en el diagrama de la sección 2.1 y viceversa.
- [x] 2.9 Añadir a la fila F3 de la sección 1.2 el histórico mínimo (periodo + 100 en el RSI y el ATR) y a la fila F5 la exclusión de las compras sin ATR suficiente. Verificar contra los deltas de `estrategias-indicador` y `operaciones-recomendadas`.
- [x] 2.10 Sustituir el árbol de la sección 2.3 por el de A13, con el propósito de cada directorio y las reglas de dependencias del backend y del frontend, y reemplazar su tabla de trazabilidad por la de una fila por sección del readme. Verificar que la guía de apply de `config.yaml` ("tabla de trazabilidad de su sección 2.3") sigue apuntando a una tabla existente.
- [x] 2.11 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Ajustar las rutas y nombres citados en la sección 6: BE-01 (`adapters/xlsx_parser.py` → `adapters/xlsx/lector_xlsx.py`), FE-01 (componentes dentro de `features/cartera/`) y DB-01 (seed desde `app/recursos/cartera-ejemplo.xlsx`). Verificar con `grep -n "xlsx_parser\|price_provider\|llm_client" readme.md` que no quedan nombres antiguos.

## 3. Tests (HU-1 a HU-5)

- [x] 3.1 Añadir a la sección 2.6 los tests con reloj fijo, la reconstrucción del cierre sin ajustar con un split conocido, la tolerancia de 1e-9 en rentabilidades frente a importes exactos, el contrato de import-linter, los tests de contrato del proveedor (de ficheros siempre; yfinance solo si se activa), el descarte de la barra del día en curso, la respuesta con caché desactualizada frente a `503`, los tests de contrato de TA-Lib contra valores de referencia de StockCharts y el oráculo de Wilder solo de tests, y los escenarios de histórico mínimo (100 → "Sin datos suficientes", 114 → señal) y de compra sin ATR. Verificar que cada test cita la decisión de design.md que cubre.

## 4. DevOps (HU-1 a HU-5)

- [x] 4.1 Eliminar de las secciones 0.4 y 2.4 el despliegue opcional en PaaS, dejar solo `docker compose` local y CI sin despliegue (A9), y añadir import-linter al stack de la sección 2.7. Verificar con `grep -n -i "render\|railway\|fly.io\|paas" readme.md` que no quedan referencias.
- [x] 4.2 Añadir a la sección 2.7 uv (`uv sync --frozen` en Docker y CI), ESLint con `import/no-restricted-paths` y openapi-typescript, y a la sección 2.4 los comandos de CI con uv. Verificar que coinciden con A13.
- [x] 4.3 Reescribir la sección 2.4 con A14: tabla de servicios (`db`, `migrate`, `api`, `web`), modos demo y desarrollo, puertos en `127.0.0.1`, `.env.example`, jobs de CI, publicación en GHCR, el diagrama Mermaid y el arranque paso a paso. Verificar que el diagrama se renderiza y que cada job de la tabla aparece en él.
- [x] 4.4 Actualizar las secciones 0.4 y 1.4 con el arranque paso a paso de A14, sustituyendo `localhost:5173` y `localhost:8000/docs` por `localhost:8080` y `localhost:8080/api/docs`, e indicando las dos vías (imágenes publicadas o `--build`). Verificar con `grep -n "5173\|8000" readme.md` que solo queda el 5173 en la descripción del modo desarrollo.
- [x] 4.5 Actualizar la sección 2.5: el mismo origen vía nginx (CORS solo como defensa en profundidad), `client_max_body_size 6m` frente al límite de 5 MB de la API y los puertos publicados solo en `127.0.0.1`. Verificar que la fila "Zip bomb / DoS" sigue citando `413` para más de 5 MB.
- [x] 4.6 Fijar en la sección 2.6 Testcontainers para los tests de integración (eliminar "o servicio CI") y el E2E con `PROVEEDOR_PRECIOS=ficheros`, y ampliar OPS-01 en la sección 6 con compose, `migrate`, CI y el job de release. Verificar que OPS-01 referencia A14. En la sección 6 no editar nada: lo consolida `revisar-tickets` (K7).

## 5. Comprobación final

- [x] 5.1 Ejecutar `openspec validate revisar-arquitectura-mvp --strict` y confirmar que no hay errores.
- [x] 5.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs ni el resultado de `alinear-readme-con-specs`, en especial los códigos `409`/`503` frente a la tabla A7.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado; actualizará el requisito "Precio de referencia" de la spec viva `importacion-cartera`.

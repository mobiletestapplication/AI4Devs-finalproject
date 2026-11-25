# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. Aplicar después de `alinear-readme-con-specs`. Las referencias A1-A9 remiten a design.md.

## 1. Base de datos (HU-1, HU-2)

- [ ] 1.1 Actualizar el erDiagram de la sección 3.1 y la fila de `PRECIO_DIARIO` de la sección 3.2 con `cierre_sin_ajustar` y la indicación de que el OHLC está ajustado por splits (A4). Verificar que el diagrama coincide con el de design.md y se renderiza sin errores.
- [ ] 1.2 Añadir a DB-01, en la sección 6, la columna `cierre_sin_ajustar` con `CHECK > 0` y la tabla `COBERTURA_PRECIO` con `CHECK hasta >= desde`. Verificar que los tipos son `NUMERIC` y `date`.
- [ ] 1.3 Añadir `COBERTURA_PRECIO` al erDiagram de la sección 3.1 y a la tabla de entidades de la sección 3.2, explicando por qué no basta con las filas de `PRECIO_DIARIO` (A5). Verificar que coincide con el diagrama de design.md.

## 2. Backend (HU-1 a HU-5)

- [ ] 2.1 Sustituir el diagrama y el texto del patrón de la sección 2.1 por el diagrama, la comparativa con microservicios, los beneficios y los sacrificios de A1-A2. Verificar que el Mermaid se renderiza y que aparecen los seis puertos.
- [ ] 2.2 Actualizar la tabla de la sección 2.2 con el servicio de datos de mercado (A5), el puerto `Reloj` (A6), el mapeo de errores (A7) y el contrato de import-linter. Verificar que cada componente nuevo aparece también en el diagrama.
- [ ] 2.3 Cambiar en la fila F1 de la sección 1.2 y en los "Datos derivados" de la sección 3.2 "última cotización" por "último cierre diario sin ajustar, con su fecha" (A3), y añadir la limitación de splits durante la tenencia a las "Decisiones de alcance" (A4). Verificar contra el delta de `importacion-cartera`.
- [ ] 2.4 Añadir a "Fórmulas clave" de la sección 3.2 la reconstrucción `cierre_sin_ajustar = cierre × F(fecha)` con el ejemplo del split 10:1 (120,00 → 1.200,00) y qué serie usa cada feature. Verificar que coincide con A4.
- [ ] 2.5 Ampliar BE-02 en el backlog de la sección 6 con los eventos de split, la normalización pura a dos series, el rango con calentamiento, el calendario, la cobertura, la barra del día en curso, la invalidación por split y los reintentos. Verificar que referencia HU-1 a HU-5.
- [ ] 2.6 Sustituir en las secciones 2.2 y 2.7 "yfinance (adaptador intercambiable: Stooq / Alpha Vantage)" por la decisión A10: yfinance como único proveedor real más un proveedor de ficheros, con la tabla comparativa resumida y el contrato del puerto. Verificar que no queda Stooq ni Alpha Vantage como respaldo automático.
- [ ] 2.7 Añadir a la sección 4 la regla de caché desactualizada y la tabla de respuestas con el proveedor caído (A11), la diferencia entre `422` y `503`, y el cuerpo `application/problem+json` con `Retry-After`. Verificar contra los escenarios "Proveedor de mercado no disponible" de cada spec.

## 3. Tests (HU-1 a HU-5)

- [ ] 3.1 Añadir a la sección 2.6 los tests con reloj fijo, la reconstrucción del cierre sin ajustar con un split conocido, la tolerancia de 1e-9 en rentabilidades frente a importes exactos, el contrato de import-linter, los tests de contrato del proveedor (de ficheros siempre; yfinance solo si se activa), el descarte de la barra del día en curso y la respuesta con caché desactualizada frente a `503`. Verificar que cada test cita la decisión de design.md que cubre.

## 4. DevOps (HU-1 a HU-5)

- [ ] 4.1 Eliminar de las secciones 0.4 y 2.4 el despliegue opcional en PaaS, dejar solo `docker compose` local y CI sin despliegue (A9), y añadir import-linter al stack de la sección 2.7. Verificar con `grep -n -i "render\|railway\|fly.io\|paas" readme.md` que no quedan referencias.

## 5. Comprobación final

- [ ] 5.1 Ejecutar `openspec validate revisar-arquitectura-mvp --strict` y confirmar que no hay errores.
- [ ] 5.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs ni el resultado de `alinear-readme-con-specs`, en especial los códigos `409`/`503` frente a la tabla A7.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado; actualizará el requisito "Precio de referencia" de la spec viva `importacion-cartera`.

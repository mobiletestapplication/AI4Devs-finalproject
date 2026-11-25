# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código. Aplicar después de `alinear-readme-con-specs` y de `revisar-arquitectura-mvp`. S1-S8 remiten a design.md.

## 1. Seguridad (HU-1)

- [ ] 1.1 Sustituir la tabla de la sección 2.5 por el mapa de amenazas de S1, con la categoría OWASP 2025 y el código HTTP de cada fila, y quitar las marcas "(control de diseño, pendiente de spec)" que puso `alinear-readme-con-specs`. Verificar que cada código coincide con un escenario de los deltas o de la spec viva.
- [ ] 1.2 Añadir a la sección 2.5 el diagrama de S2 (orden de validación de la subida) y los umbrales de S3. Verificar que el diagrama se renderiza y que los umbrales coinciden con el delta de `importacion-cartera` (50 MB, 100:1, 1.000 entradas, 10.000 filas, 10 s).

## 2. Backend (HU-1 a HU-5)

- [ ] 2.1 Añadir a la sección 4 los códigos nuevos: `400` por Host, `403` por origen, `429` con `Retry-After` en la importación y el backtest, `400` para la validación de parámetros y `500` en `application/problem+json`; y ampliar el OpenAPI de `/api/cartera/importacion` con los casos nuevos de `413`, `415` y `422`. Verificar contra los escenarios de `seguridad-api` y del delta de `importacion-cartera`.
- [ ] 2.2 Actualizar la fila "Ingesta XLSX" de la sección 2.2 y la tarea 4 de BE-01 en la sección 6 con el orden de validación de S2, el patrón de ticker y los precios > 0, ya como requisitos de spec. Verificar que ninguna los presenta como pendientes de spec.
- [ ] 2.3 Añadir a OPS-01 (sección 6) la configuración de los orígenes y hosts admitidos por entorno y slowapi. Verificar que coincide con S4 y S5.

## 3. Tests (HU-1)

- [ ] 3.1 Añadir a la sección 2.6 la lista de fixtures maliciosos y su respuesta esperada: zip bomb (2 GB declarados) → `413`, proporción 300 KB → 40 MB → `413`, 1.500 entradas → `413`, `vbaProject.bin` → `415`, OLE `D0 CF 11 E0` → `415`, `<!DOCTYPE` con entidad externa → `415`, `externalLinks/` → `415`, 10.001 filas → `422` y 10.000 → `201`, ticker `=HYPERLINK(…)` → `422`, ticker de 500 caracteres → eco de 20. Verificar que cada fixture corresponde a un escenario.
- [ ] 3.2 Añadir a la sección 2.6 los tests de `seguridad-api`: Host ajeno → `400`, `Origin` ajeno → `403`, sin cabeceras → aceptado, sexta importación por minuto → `429`, periodo `abc` → `400`, excepción forzada → `500` sin traza. Verificar que cada test cita su escenario.

## 4. Historias de usuario (HU-1)

- [ ] 4.1 Añadir a los criterios de aceptación de HU-1 un caso de fichero peligroso (`.xlsm` renombrado → `415`, cartera intacta) y otro de 10.001 filas → `422`. Verificar que son resúmenes fieles de los escenarios.

## 5. Coherencia con otros changes

- [ ] 5.1 Confirmar que las secciones 2.4 y 2.5 del readme, tras `revisar-arquitectura-mvp` (A14: nginx en el mismo origen, 6 MB, `127.0.0.1`), no contradicen S4 ni el límite de 5 MB. Verificar con `grep -n "413\|CORS\|slowapi" readme.md`.

## 6. Comprobación final

- [ ] 6.1 Ejecutar `openspec validate endurecer-seguridad --strict` y confirmar que no hay errores.
- [ ] 6.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs.

## Workflow follow-up

- Archivar con `/opsx:archive`: añadirá los requisitos a `importacion-cartera` y creará la spec viva `seguridad-api`.

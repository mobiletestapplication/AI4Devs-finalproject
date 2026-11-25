# Tasks

Entrega 1: todas las tareas son de documentación en `readme.md`; no se escribe código.

## 1. Base de datos (HU-1)

- [x] 1.1 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Actualizar el ticket DB-01 de la sección 6 para indicar que el seed usa el mismo `cartera-ejemplo.xlsx` que sirve el endpoint de ejemplo. Verificar que se nombra el fichero y que el modelo de datos de la sección 3 no cambia.

## 2. Backend (HU-1)

- [x] 2.1 Ampliar la fila F1 de la sección 1.2 con el resumen, las ganancias por año fiscal y la fecha de los datos, y reescribir S3 como cartera de ejemplo descargable que sirve de plantilla. Verificar que coincide con el delta de `importacion-cartera`.
- [x] 2.2 Añadir a "Fórmulas clave" de la sección 3.2 el cálculo del resumen, la agrupación por año natural de venta y el umbral de 5 días. Verificar con los ejemplos de los escenarios: 2.100, 2.000, +100 (+5 %) y +50 USD; 2024 con ST neto +200 y LT neto +500.
- [x] 2.3 Documentar en la sección 4 `GET /api/cartera/resumen` y `GET /api/cartera/ejemplo` en la tabla de endpoints, con un ejemplo de respuesta del resumen. Verificar que se recogen los casos sin cartera y sin proveedor, ambos con `200 OK`.
- [x] 2.4 Añadir a la sección 2.2 el resumen de cartera en la fila "Motor de posiciones". Verificar que menciona que reutiliza el cálculo de posiciones (D1 de design.md).
- [x] 2.5 Añadir a la sección 2.5 los controles del endpoint de ejemplo: sin entrada de la persona, adjunto con `nosniff` y fichero validado en CI. Verificar que coinciden con la sección de seguridad de design.md.
- [x] 2.6 Usar como ruta del XLSX de ejemplo `backend/app/recursos/cartera-ejemplo.xlsx` (decisión A13 de `revisar-arquitectura-mvp`) en lugar de "los fixtures del backend", también en D4 y en el diagrama de design.md de este change. Verificar que ni el readme ni este change sitúan el fichero bajo `tests/`.

## 3. Frontend (HU-1)

- [x] 3.1 Actualizar el punto 1 (Carga y Watchlist) de la sección 1.3 con la cabecera de resumen, la tabla fiscal desplegable, la fecha de los datos con el aviso de desactualización y el enlace "Descargar cartera de ejemplo". Verificar que cada elemento corresponde a un escenario de pantalla del delta.
- [x] 3.2 **Consolidada en `revisar-tickets` (K7): no editar la sección 6; verificar que `revisar-tickets` recoge lo que pedía esta tarea.** Añadir a FE-01, en la sección 6, la cabecera de resumen y el enlace de descarga, o crear un ticket FE nuevo en el backlog. Verificar que referencia HU-1.

## 4. Tests (HU-1)

- [x] 4.1 Añadir a la sección 2.6 los casos unitarios del resumen (con posición sin precio), del desglose fiscal (2024 y la venta del 2025-01-05) y de la desactualización (3 y 7 días), y el de integración que descarga el ejemplo, lo importa y espera `201` sin modificar la cartera al descargar. Verificar que cada caso cita el valor de su escenario.

## 5. DevOps (HU-1)

- [x] 5.1 Indicar en la sección 2.4 que CI ejecuta el test de importación del fichero de ejemplo. Verificar que el texto coincide con D4 de design.md.

## 6. Historias de usuario (HU-1)

- [x] 6.1 Añadir a los criterios de aceptación de HU-1 el resumen con el ejemplo de 2.100 USD, la tabla fiscal de 2024 y la descarga del ejemplo. Verificar que son resúmenes fieles de los escenarios.

## 7. Comprobación final

- [x] 7.1 Ejecutar `openspec validate resumen-cartera-y-ejemplo --strict` y confirmar que no hay errores.
- [x] 7.2 Releer las secciones del `readme.md` modificadas y confirmar que no contradicen las specs, en especial que S3 ya no se describe como plantilla vacía.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado, comprobando antes que el `readme.md` no contradice las specs actualizadas.

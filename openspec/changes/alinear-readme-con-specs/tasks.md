# Tasks

Entrega 1: todas las tareas editan solo `readme.md`; no se escribe código ni se modifican specs. Los identificadores D1-D17 remiten al catálogo de design.md.

## 1. Backend: API (HU-1 a HU-5)

- [ ] 1.1 Reescribir "Códigos comunes" de la sección 4 indicando a qué endpoints aplica `409` y `503`, y que `GET /api/estrategias` no los usa y `GET /api/cartera/posiciones` degrada por posición (D1). Verificar contra los escenarios "Sin cartera importada" y "Proveedor de mercado no disponible" de cada spec.
- [ ] 1.2 Añadir los códigos específicos: `404` por ticker fuera de la cartera, `400` por falta de estrategia en recomendaciones y `422` por tickers sin histórico en TWR (D3). Verificar que los tres coinciden literalmente con su spec.
- [ ] 1.3 Completar en el OpenAPI la descripción del cuerpo de `/api/backtests` (D4) y la de `twr_anualizada` en `Metricas` (D5). Verificar que el YAML sigue siendo válido, por ejemplo pegándolo en un validador OpenAPI 3.0.3.

## 2. Backend: funcionalidades y componentes (HU-2 a HU-5)

- [ ] 2.1 Actualizar las filas F2, F3, F4 y F5 de la tabla de la sección 1.2 (D6-D9). Verificar que cada frase añadida corresponde a un requisito de la spec indicada en la columna "Spec".
- [ ] 2.2 Marcar "precios > 0" como control de diseño en la fila "Ingesta XLSX" de la sección 2.2 y en la tarea 4 de BE-01 de la sección 6 (D17). Verificar que ninguna de las dos lo presenta como requisito de spec. Omitir si `endurecer-seguridad` ya está aplicado (ver D-a).

## 3. Frontend (HU-1 a HU-5)

- [ ] 3.1 Completar los puntos 1 a 5 de la sección 1.3 con lo indicado en D10-D14. Verificar que cada elemento corresponde a un escenario de pantalla de su spec y que no se añade nada que no esté en ellas.
- [ ] 3.2 Sustituir en HU-5 (sección 5) el literal del aviso por "Las señales son orientativas y no constituyen asesoramiento financiero" (D2). Verificar con `grep -n "asesoramiento" readme.md` que todos los literales coinciden, salvo el aviso general de la sección 0.3.

## 4. Seguridad (HU-1)

- [ ] 4.1 Marcar en la tabla de la sección 2.5 las reglas de D15 y D16 con "(control de diseño, pendiente de spec)", quitar el `→ 415` de `.xlsm`/`vbaProject.bin` y añadir la nota al pie de la decisión D-a. Verificar que los únicos códigos HTTP que quedan en la tabla son los que define `importacion-cartera` (`413`, `415` por no ser XLSX y `422`). Omitir las marcas si `endurecer-seguridad` ya está aplicado (ver D-a).

## 5. Comprobación final

- [ ] 5.1 Recorrer cada `### Requirement:` de las cinco specs vivas y confirmar que el readme no lo contradice. Anotar en el resumen del apply cualquier divergencia nueva que se encuentre.
- [ ] 5.2 Confirmar con `git diff readme.md` que solo cambian las secciones listadas en proposal.md (Impact) y que se conservan las ediciones a mano de la sección 1.1.
- [ ] 5.3 Ejecutar `openspec validate alinear-readme-con-specs --strict` y confirmar que no hay errores.

## Workflow follow-up

- Archivar el change con `/opsx:archive` cuando se haya revisado; al no tener deltas, no modifica las specs vivas.

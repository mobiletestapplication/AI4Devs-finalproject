# Proposal

## Why

Las operaciones recomendadas (F5) dicen qué comprar y a qué niveles salir, pero no cuántas acciones comprar, así que la recomendación está incompleta y no enseña gestión del riesgo. Además, como las señales describen un estado, la misma compra se repite a diario durante meses mientras dura una tendencia, y nada avisa si comprar un ticker vendido con pérdida hace pocos días anularía la deducción de esa pérdida (regla de wash sale estadounidense), coherente con el enfoque fiscal Short-Term/Long-Term del producto.

Cubre la feature **F5 (Hasta 10 operaciones recomendadas)** y amplía la historia de usuario **HU-5**.

## What Changes

- **Cantidad sugerida en las compras:** número entero de acciones tal que, si salta el stop-loss, la pérdida no supere un porcentaje de riesgo del valor de la cartera (1 % por defecto), con el capital necesario y su peso en la cartera.
- **Antigüedad de la señal:** cada operación indica las sesiones transcurridas desde que empezó su señal y se marca como nueva si son 5 o menos.
- **Filtro por antigüedad:** parámetro opcional que excluye las señales más antiguas que un número de sesiones antes de elegir las 10 operaciones.
- **Aviso de wash sale:** una compra recomendada de un ticker vendido con pérdida en los 30 días anteriores lleva un aviso con la fecha a partir de la cual la compra ya no afectaría.
- **Pantalla:** cantidad y capital en las compras, control del porcentaje de riesgo, etiqueta "Nueva", filtro de señales recientes e icono de aviso de wash sale.

## Capabilities

### New Capabilities
_Ninguna._

### Modified Capabilities
- `operaciones-recomendadas`: nuevos requisitos de cantidad sugerida, antigüedad de la señal, filtro por antigüedad, aviso de wash sale, parámetros HTTP y presentación en pantalla. Los requisitos existentes no cambian: sin parámetros nuevos, la selección y el orden de las operaciones son los actuales.

## Fuera de alcance

- Saldo de efectivo o límite de capital disponible: la cantidad se calcula sobre el valor de la cartera, que no tiene efectivo.
- Límites de concentración por ticker (prioridad 2 del análisis).
- Cantidad parcial en las ventas: se mantiene la venta de toda la posición abierta.
- Regla de wash sale completa (compras en los 30 días anteriores a la venta, valores sustancialmente idénticos, ajuste del coste fiscal) y reglas fiscales de otros países, como la regla de los dos meses en España.
- Cambiar el orden por defecto de las operaciones para priorizar las señales nuevas.

## Impact

- **API:** `GET /api/recomendaciones` acepta los parámetros opcionales `riesgo` y `antiguedad_max` y añade campos a cada operación; compatible con los clientes actuales.
- **Dominio:** el cálculo usa el ATR y el stop-loss existentes, la fecha desde la que se mantiene la señal (F3) y las posiciones cerradas de la cartera; no requiere datos nuevos ni cambios en la BD.
- **Frontend:** panel de operaciones recomendadas.
- **readme.md:** secciones 1.2, 1.3, 3.2 (fórmulas), 4 (API), 2.6, 5 (HU-5) y 6 (BE-06, FE-05).

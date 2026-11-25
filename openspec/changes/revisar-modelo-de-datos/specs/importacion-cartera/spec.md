# Spec Delta

## ADDED Requirements

### Requirement: Tipos de celda admitidos
El sistema SHALL aceptar en las columnas de fecha celdas de fecha de Excel o texto `AAAA-MM-DD`, y en las de cantidad y precio celdas numéricas o texto con punto decimal, y SHALL considerar no válida, con `422 Unprocessable Entity` y su número de fila, cualquier otro formato.

#### Scenario: Fecha como texto ISO
- **WHEN** la fila 2 tiene en `Fecha de compra` el texto `2024-01-10`
- **THEN** la posición se importa con fecha de compra 2024-01-10

#### Scenario: Fecha ambigua como texto
- **WHEN** la fila 3 tiene en `Fecha de compra` el texto `10/01/2024`
- **THEN** el sistema responde `422 Unprocessable Entity` con un error en la fila 3 que indica el formato `AAAA-MM-DD`

#### Scenario: Coma decimal como texto
- **WHEN** la fila 4 tiene en `Precio de compra` el texto `172,50`
- **THEN** el sistema responde `422 Unprocessable Entity` con un error en la fila 4 que indica que el decimal se escribe con punto

#### Scenario: Celda de fecha con hora
- **WHEN** la fila 5 tiene en `Fecha de venta` una celda de fecha de Excel con valor 2024-12-20 15:30
- **THEN** la posición se importa con fecha de venta 2024-12-20

### Requirement: Cantidades fraccionarias
El sistema SHALL aceptar cantidades mayores que 0 con hasta 6 decimales y SHALL considerar no válida, con `422 Unprocessable Entity` y su número de fila, una cantidad con más de 6 decimales.

#### Scenario: Fracción de acción
- **WHEN** una fila tiene 2,5 acciones de `AAPL` compradas a 100 USD con precio de referencia 120 USD
- **THEN** la posición se importa con cantidad 2,5 y su rendimiento total es 50 USD

#### Scenario: Demasiados decimales
- **WHEN** la fila 6 tiene una cantidad de 0,1234567
- **THEN** el sistema responde `422 Unprocessable Entity` con un error en la fila 6 que indica el máximo de 6 decimales

### Requirement: Columnas adicionales y filas vacías
El sistema SHALL ignorar las columnas cuya cabecera no sea ninguna de las de referencia y SHALL saltar sin error las filas en las que todas las celdas de las columnas de referencia estén vacías, sin contarlas en el límite de filas ni en el número de posiciones importadas.

#### Scenario: Columna extra
- **WHEN** el fichero incluye además una columna `Comisión`
- **THEN** el sistema importa las posiciones ignorando esa columna

#### Scenario: Fila vacía intermedia
- **WHEN** las filas 2 y 4 son válidas y la fila 3 está completamente vacía
- **THEN** el sistema responde `201 Created` con 2 posiciones importadas

#### Scenario: Fila a medias
- **WHEN** la fila 3 solo tiene relleno el ticker
- **THEN** el sistema responde `422 Unprocessable Entity` con los campos obligatorios que faltan en la fila 3

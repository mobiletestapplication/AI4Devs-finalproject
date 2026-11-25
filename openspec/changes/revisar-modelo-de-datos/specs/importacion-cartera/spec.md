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

### Requirement: Precisión de los precios
El sistema SHALL redondear los precios de compra y de venta con más de 6 decimales a 6 decimales, al valor más cercano y con las mitades hacia arriba, sin rechazar la fila, y SHALL usar el precio redondeado en todos los cálculos.

#### Scenario: Precio con 7 decimales
- **WHEN** la fila 2 tiene un precio de compra de 172,1234565 USD
- **THEN** la posición se importa con precio de compra 172,123457 USD

#### Scenario: Precio con 6 decimales o menos
- **WHEN** la fila 2 tiene un precio de compra de 172,5 USD
- **THEN** la posición se importa con precio de compra 172,5 USD sin modificarlo

### Requirement: Fichero sin filas de datos
El sistema SHALL rechazar con `422 Unprocessable Entity`, sin modificar la cartera existente, un fichero cuya primera hoja tenga las cabeceras pero ninguna fila de datos, incluido el caso en que todas las filas posteriores a las cabeceras estén vacías.

#### Scenario: Solo cabeceras
- **WHEN** el cliente envía un XLSX con la fila de cabeceras válida y ninguna fila más
- **THEN** el sistema responde `422 Unprocessable Entity` indicando que el fichero no contiene posiciones, y la cartera existente no cambia

#### Scenario: Solo filas vacías
- **WHEN** el cliente envía un XLSX con la fila de cabeceras válida y las filas 2 a 5 completamente vacías
- **THEN** el sistema responde `422 Unprocessable Entity` indicando que el fichero no contiene posiciones

> Detalla en esta sección los prompts principales utilizados durante la creación del proyecto, que justifiquen el uso de asistentes de código en todas las fases del ciclo de vida del desarrollo. Esperamos un máximo de 3 por sección, principalmente los de creación inicial o  los de corrección o adición de funcionalidades que consideres más relevantes.
Puedes añadir adicionalmente la conversación completa como link o archivo adjunto si así lo consideras


## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
En Plan Mode quiero explorar que criterios sugieres para un dashboard de trading de una cartera de inversion simulada. Me gustaria utilizar OpenSpec para importar la cartera, calcular rendimiento ponderado en el tiempo, sugerir una estrategia, hacer backtesting, y recomendar un numero limitado de operaciones de trading.
Que sugerencias de funcionalidades tienes? Razonala necesidad de las mismas.
No memorices nada.
 

**Prompt 2:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
/opsx:explore
 Vamos a documentar las specs de OpenSpec de un dashboard de trading moderno de una cartera de inversion simulada en un proyecto nuevo. No hay codigo que leer todavia.
 Antes de nada, sigue estas 4 premisas para las specs que se escriben en `openspec/specs/` con el formato exacto de una spec VIVA de OpenSpec:
  1. Un `## Purpose` de una o dos frases concisas y debajo `## Requirements` con `### Requirement:` en los que el sistema SHALL hacer algo, y bajo cada uno al menos un `#### Scenario:` de cuatro almohadillas con sus dos viñetas `- **WHEN**` y `- **THEN**`.
  2. En castellano, salvo las mayúsculas RFC-2119.
  3. NO uses secciones ADDED, MODIFIED ni REMOVED: eso es de un delta, y esto no es un delta, es la verdad actual del sistema.
  4. Describe solo comportamiento observable desde fuera. Nada de nombres de clase ni de rutas de archivo todavia. Para el backend, observable = la petición y la respuesta HTTP. Para el frontend, observable = lo que una persona ve y puede hacer en pantalla

 La primera feature tiene como entrada por el frontend un fichero XLSX que contiene las posiciones abiertas y cerradas, una vez cargado, el frontend muestra las acciones en la cartera en forma de tabla (Watchlist) asi como precio, rendimiento total, y si son Short o Long Capital Gains.
 La segunda feature que calcule el "Time-Weighted Rate of Return" (TWR) o "Tasa de Retorno Ponderada en el Tiempo" anualizada, mensual y semanal midiendo de manera precisa el rendimiento del inversor en las operaciones incluso si no se han cerrado aun (ya que son PNL).
 La tercera feature creara una estrategia de inversion basada en un indicador aplicada a las acciones que componen la cartera para ayudar con la toma de decisiones.
 La cuarta feature realizara backtesting de las operaciones realizadas en el pasado calculando rentabilidades y estrategias de mejora.
 La quinta feature mostrara 10 operaciones de trading recomendadas sobre los pnemonicos (tickers) que forman la cartera existente de acciones en base a la estrategia de trading seleccionada.
 Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda si no puedes definir claramente el requisito.


**Prompt 3:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
/opsx:propose resuelve las divergencias entre las specs y el fichero readme.md que edite a mano. Las specs son la fuente de verdad.

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:**
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de arquitectura o diseño si no puedes definir claramente el requisito.

**Prompt 2:**

**Prompt 3:**

### **2.2. Descripción de componentes principales:**

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

### **2.4. Infraestructura y despliegue**

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

### **2.5. Seguridad**

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

### **2.6. Tests**

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

---

### 3. Modelo de Datos

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

---

### 4. Especificación de la API

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

---

### 5. Historias de Usuario

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

---

### 6. Tickets de Trabajo

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

---

### 7. Pull Requests

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

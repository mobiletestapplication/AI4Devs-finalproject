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
/opsx:propose resuelve las divergencias entre las specs y el fichero readme.md que edite a mano. Las specs son la fuente de verdad y he hecho una revision en plan mode con /ospx:explore antes de seguir adelante.

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
/opsx:explore Con las 5 specs vivas de `openspec/specs/` como fuente de verdad, propón la arquitectura de un MVP que va a desarrollar una sola persona. Compara un monolito modular con microservicios, separa la lógica financiera pura (posiciones, TWR, indicadores, backtest, recomendaciones) de los adaptadores (XLSX, proveedor de precios, base de datos y un LLM opcional) y dibuja un diagrama Mermaid `flowchart` con los componentes y sus tecnologías. Justifica el patrón elegido, sus beneficios y los sacrificios que implica.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de arquitectura o diseño si no puedes definir claramente el requisito.

**Prompt 2:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Compara yfinance, Stooq y Alpha Vantage como proveedor gratuito de precios diarios OHLC y de última cotización para el MVP. Diseña la abstracción que permita cambiar de proveedor sin tocar el dominio, la estrategia de caché en base de datos y qué debe responder la API cuando el proveedor no esté disponible.

### **2.2. Descripción de componentes principales:**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Genera la tabla de componentes principales (componente, tecnología, responsabilidad) coherente con el diagrama de la sección 2.1. Para los indicadores (RSI y ATR de Wilder, SMA), razona si conviene una implementación propia validada contra valores de referencia o una librería como pandas-ta o TA-Lib.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de los componentes principales si no puedes definir claramente el requisito.

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Propón la estructura de carpetas del repositorio (backend FastAPI por capas api/application/domain/adapters/infrastructure, frontend React + Vite, `openspec/`) explicando el propósito de cada carpeta. Añade una tabla de trazabilidad entre los artefactos de OpenSpec (proposal, specs, design, tasks) y las secciones del readme.md.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda del proyecto y su estructura de ficheros si no puedes definir claramente el requisito.

### **2.4. Infraestructura y despliegue**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Diseña la infraestructura del proyecto: `docker compose` con los servicios db, api y web; un pipeline de GitHub Actions con lint, tests, análisis de dependencias y de secretos; y un despliegue opcional en un PaaS gratuito. Incluye un diagrama Mermaid y explica el proceso de despliegue paso a paso.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de infraestructura y despliegue si no puedes definir claramente el requisito.

### **2.5. Seguridad**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Actúa como revisor de seguridad con OWASP Top 10 como referencia. El vector de ataque principal es la subida de un fichero XLSX. Enumera en una tabla riesgo → control las amenazas concretas (zip bomb, `.xlsm` con macros, XXE, inyección de fórmulas, path traversal, abuso de la API, secretos, dependencias vulnerables y prompt injection en la feature opcional con LLM) indicando el código HTTP con el que se rechaza cada caso.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda seguridad en la aplicacion o en su codigo si no puedes definir claramente el requisito.

### **2.6. Tests**

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Traduce los escenarios WHEN/THEN de cada spec a una estrategia de tests: unitarios del dominio con casos calculados a mano (ST/LT en el aniversario de la compra y en años bisiestos, TWR neutral frente a aportaciones, ejecución del backtest sin sesgo de anticipación), integración API + PostgreSQL con Testcontainers y el proveedor de precios sustituido por un *fake*, E2E con Playwright del flujo principal y fixtures maliciosos para seguridad.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda en los test de los requisitos y de la  aplicacion si no puedes definir claramente el requisito.

---

## 3. Modelo de Datos

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
A partir de las specs, diseña el modelo de datos mínimo en PostgreSQL y separa lo que se persiste de lo que se calcula bajo demanda. Dibuja un `erDiagram` de Mermaid con PK, FK, NOT NULL, CHECK e índices, garantizando una única cartera vigente. Documenta el formato del fichero XLSX de entrada y las fórmulas clave del dominio: rendimiento, clasificación ST/LT, rentabilidad diaria con aportaciones y retiradas, TWR anualizada según GIPS, intensidad de las señales y stop-loss/objetivo por ATR.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda del modelo de datos si no puedes definir claramente el requisito.

**Prompt 2:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Revisa el modelo de datos: tipos `NUMERIC` frente a `float` para importes, sustitución atómica de la cartera en una sola transacción y caché OHLC de precios diarios. Señala cualquier restricción que falte para que la base de datos rechace los mismos casos que las specs.

---

## 4. Especificación de la API

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Lista los endpoints REST del MVP (base `/api`, cartera única sin identificador) asociados a cada feature y documenta en OpenAPI 3.0.3 los 3 principales: importación del XLSX, TWR y backtest. Los códigos de error comunes (400, 404, 409, 413, 415, 422, 503) deben ser coherentes con los escenarios de las specs.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de la API si no puedes definir claramente el requisito.

---

## 5. Historias de Usuario

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Escribe una historia de usuario por feature con el formato Como / quiero / para, criterios de aceptación en Gherkin derivados de los escenarios de su spec y con ejemplos numéricos, prioridad MoSCoW y estimación en story points. Comprueba que cada historia cumple INVEST.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de las historias de usuario si no puedes definir claramente el requisito.

---

## 6. Tickets de Trabajo

**Prompt 1:**
**Modelo:** Opus 5.5 xHigh
**Herramienta:** Claude Code
Genera 3 tickets de trabajo detallados para desarrollar de inicio a fin: uno de base de datos (esquema y migraciones con Alembic), uno de backend (endpoint de importación del XLSX con validación segura) y uno de frontend (carga del fichero y Watchlist). Cada uno con tipo, historia de usuario, estimación, dependencias, tareas, criterios de aceptación y Definition of Done. Añade un backlog resumido con el resto de tickets.
Al terminar, dime que features necesitan mas informacion y entrevistame para cualquier duda de los tickets de trabajo si no puedes definir claramente el requisito.

---

## 7. Pull Requests

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

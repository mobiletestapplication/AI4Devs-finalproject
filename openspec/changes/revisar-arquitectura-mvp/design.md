# Design

## Context

Ver proposal.md (Why). Punto de partida: la sección 2 del `readme.md` propone un monolito modular FastAPI con dominio puro y adaptadores (XLSX, proveedor de precios, BD y LLM opcional). Las cinco specs vivas exigen además:
- valoración diaria al cierre (rentabilidad-twr);
- indicadores con calentamiento (estrategias-indicador, backtesting);
- degradación por posición cuando falta precio (importacion-cartera);
- códigos `409`, `422`, `503`, `404` y `400` en varios endpoints.

Lo desarrolla una sola persona y todavía no hay código.

## Goals / Non-Goals

**Goals:**
- Fijar las decisiones transversales antes de la Entrega 2 para que todas las features las apliquen igual.
- Mantener la lógica financiera como funciones puras que se prueban con los ejemplos numéricos de las specs.

**Non-Goals:**
- Diseño interno de cada módulo de dominio; cada change de feature lo detalla.
- Rendimiento o escalado más allá de un solo usuario.

## Decisions

### A1. Monolito modular frente a microservicios
| Criterio | Monolito modular | Microservicios |
|---|---|---|
| Equipo de 1 persona | Un repositorio, un despliegue, un pipeline | N servicios, N pipelines, contratos entre servicios |
| Datos compartidos | F1-F5 leen las mismas posiciones y precios en una BD transaccional | Duplicar o consultar en remoto posiciones y precios |
| Acoplamiento real | F4 reutiliza F2 y F3; F5 usa F3 y F1 | Cadenas síncronas (backtest → señales → precios) con latencia y fallos parciales |
| Importación atómica | Una transacción | Sagas o consistencia eventual |
| Escalado | Innecesario: un usuario | Independiente, sin necesidad |
| Observabilidad | Logs de un proceso | Trazas distribuidas |

- **Elegido:** monolito modular con arquitectura hexagonal: dominio, casos de uso, puertos y adaptadores.
- **Beneficios:** dominio que se prueba sin red; proveedor intercambiable; un solo `docker compose`; importación atómica; las features nuevas (incluidos los changes en curso) solo añaden módulos.
- **Sacrificios:** sin escalado independiente; backtest síncrono, que puede tardar segundos con la caché fría y se mitiga con el indicador de progreso que exige la spec; disciplina de módulos por convención y CI, no por red.

### A2. Componentes y puertos
```mermaid
flowchart LR
    U[Persona<br/>Navegador] -->|HTTP local| FE[Frontend SPA<br/>React 18 + TS + Vite<br/>TanStack Query/Table · Recharts · Lightweight Charts]
    FE -->|REST/JSON| API

    subgraph Backend [Monolito modular · Python 3.12]
        API[API<br/>FastAPI + Pydantic v2<br/>mapeo de errores a HTTP] --> APP[Casos de uso<br/>importar · posiciones · twr · señales · backtest · recomendaciones]

        subgraph DOM [Dominio puro · sin I/O · pandas + Decimal]
            POS[posiciones<br/>rendimiento · ST/LT]
            TWR[twr<br/>valoración diaria · encadenado]
            IND[indicadores<br/>RSI · SMA · ATR Wilder]
            EST[estrategias<br/>reglas · intensidad]
            BT[backtest<br/>simulación · métricas · mejoras]
            REC[recomendaciones<br/>top 10 · stop/objetivo · aviso fiscal]
        end

        APP --> DOM
        APP --> MDS[Servicio de datos de mercado<br/>rango con calentamiento · calendario · refresco]

        subgraph PORTS [Puertos]
            P1[[LectorCartera]]
            P2[[ProveedorPrecios]]
            P3[[RepositorioCartera]]
            P4[[CachePrecios]]
            P5[[Reloj]]
            P6[[ClienteLLM · S1 opcional]]
            P7[[IndicadoresTecnicos]]
        end

        APP --> P1 & P3 & P5 & P6
        DOM --> P7
        MDS --> P2 & P4
    end

    P1 -.-> XLSX[Adaptador XLSX<br/>openpyxl read_only + defusedxml]
    P2 -.-> PRV[Adaptador proveedor<br/>yfinance: OHLC ajustado por splits<br/>+ eventos de split]
    P3 -.-> SQL[Repositorios<br/>SQLAlchemy 2 + Alembic]
    P4 -.-> SQL
    P5 -.-> CLK[Reloj del sistema<br/>fijo en tests]
    P7 -.-> TAL[Adaptador TA-Lib<br/>RSI · SMA · ATR · futuros MACD/Bollinger]
    P6 -.-> LLM[Adaptador LLM<br/>salida JSON validada]
    SQL --> DB[(PostgreSQL 16)]
    PRV -->|HTTP| EXT[Proveedor externo gratuito]
```

| Módulo de dominio | Entrada | Salida | Spec |
|---|---|---|---|
| posiciones | posiciones, precio de referencia, fecha actual | rendimiento, días de tenencia, ST/LT | importacion-cartera |
| twr | posiciones, cierres sin ajustar, calendario | rentabilidades diarias, TWR, series, curva | rentabilidad-twr |
| indicadores | OHLC ajustado por splits | RSI, SMA y ATR de Wilder (calculados por el puerto `IndicadoresTecnicos`), mínimo de sesiones | estrategias-indicador |
| estrategias | indicadores y parámetros | señal, intensidad, fecha de inicio | estrategias-indicador |
| backtest | posiciones, OHLC ajustado con calentamiento | simulaciones, métricas, comparativa, mejoras | backtesting |
| recomendaciones | señales, ATR, posiciones, fecha actual | hasta 10 operaciones con niveles y avisos | operaciones-recomendadas |

Dependencias del dominio, sin ciclos: `posiciones → twr → backtest`, `indicadores → estrategias → backtest`, y `estrategias, indicadores, posiciones → recomendaciones`. El dominio no importa nada de los adaptadores ni de la infraestructura; un contrato de **import-linter** en CI lo comprueba.
- **Alternativa descartada:** capas sin puertos (servicios que llaman directamente a SQLAlchemy y a yfinance). Los tests de dominio necesitarían BD y red.

### A3. Precio de referencia = último cierre diario
- **Elegido:** el último cierre diario disponible, sin ajustar, con la fecha de esa sesión, para la Watchlist, el resumen y las recomendaciones. Es la misma serie que valora la TWR.
- **Alternativa descartada:** cotización intradía. Necesitaría una segunda llamada al proveedor con una caché de minutos y, durante la sesión, el P&L de la Watchlist no cuadraría con la TWR.
- **Sacrificio:** durante la sesión el precio mostrado es el del día anterior; la fecha visible lo aclara.

### A4. Dos series de precios
- **Elegido:**
  - **cierre sin ajustar** para valorar posiciones (Watchlist, rendimiento, TWR, resumen), coherente con los precios del XLSX;
  - **OHLC ajustado por splits** para indicadores, ATR, backtest e histórico de señales, para que un split no produzca saltos que el RSI o las medias interpreten como señales.
- **Cómo:** yfinance, con `auto_adjust=False`, devuelve el OHLC ajustado por splits pero no por dividendos. El adaptador entrega las filas tal como las da el proveedor, declara qué ajuste traen y devuelve los eventos de split. Una **función pura del servicio de datos de mercado**, y no el adaptador, normaliza a las dos series y calcula `cierre_sin_ajustar = cierre × F(fecha)`, donde F(fecha) es el producto de las proporciones de los splits posteriores a esa fecha. Así la reconstrucción se prueba una sola vez, y un proveedor que entregue precios sin ajustar solo tiene que declararlo.
  - **Ejemplo:** split 10:1 el 2024-06-10; el cierre ajustado del 2024-06-07 es 120,00, luego el sin ajustar es 1.200,00.
  - Después del último split las dos series coinciden, así que el precio de referencia y el stop/objetivo ATR de las recomendaciones son coherentes.
- **Alternativa descartada:** solo la serie sin ajustar. Las señales serían falsas tras un split.
- **Alternativa descartada:** solo la serie ajustada. El rendimiento y la TWR no cuadrarían con los precios del XLSX.
- **Limitación documentada:** si hay un split *durante* la tenencia de una posición, la cantidad del XLSX no se ajusta y su valoración queda falseada desde el split, porque gestionar splits en las posiciones está fuera de alcance.
- **Proveedor:** ver A10.

### A5. Servicio de datos de mercado
- **Rango con calentamiento:** desde la primera compra menos el máximo de sesiones que necesitan la estrategia y el ATR(14) (A12), multiplicado por 1,5 para pasar a días naturales, hasta hoy. Se calcula una sola vez por petición para todos los tickers. Con los parámetros por defecto son 300 días (200 sesiones de la SMA larga × 1,5); con RSI(50) serían 225 días (150 × 1,5).
- **Calendario de sesiones:** la unión de las fechas con datos de los tickers de la cartera; los huecos de un ticker se rellenan con su cierre anterior, como indica rentabilidad-twr. No hace falta una librería de calendario bursátil.
- **Cobertura descargada:** la tabla `COBERTURA_PRECIO` registra, por ticker, el rango `desde`-`hasta` ya pedido al proveedor, cuándo se actualizó y el último split conocido. Las filas de `PRECIO_DIARIO` no bastan, porque los fines de semana, los festivos o una salida a bolsa reciente dejan huecos que no significan "falta descargar". Solo se descarga lo que falta por cada extremo del rango.
- **Refresco:** las fechas pasadas son inmutables en caché. Se vuelve a descargar desde `hasta` cuando la cobertura de un ticker tiene más de 6 horas, en un único lote para todos los tickers afectados. Las filas se escriben con upsert (`ON CONFLICT DO UPDATE`).
- **Sin barra del día en curso:** se descarta cualquier barra con la fecha de hoy en Nueva York hasta las 16:15 ET, porque durante la sesión Yahoo devuelve una barra provisional que no es un cierre (A3). El puerto `Reloj` trabaja con zona horaria.
- **Invalidación por split:** si el proveedor informa de un split posterior a `ultimo_split`, se vuelve a descargar todo el histórico del ticker, porque su OHLC ajustado anterior ya no es válido.
- **Alternativa descartada:** descargar siempre el histórico completo, porque agota los límites del proveedor gratuito.

### A6. Puerto `Reloj`
La fecha actual se inyecta. La usan la clasificación ST/LT de las abiertas, la validación de fechas futuras, el aviso fiscal y la antigüedad de los datos. En tests se fija para reproducir los escenarios con fechas concretas (por ejemplo, "compra hace 200 días").

### A7. Mapeo centralizado de errores
| Excepción de dominio | HTTP | Specs |
|---|---|---|
| `CarteraNoImportada` | `409` | rentabilidad-twr, estrategias-indicador, backtesting, operaciones-recomendadas |
| `ProveedorNoDisponible` | `503` | las mismas |
| `TickersSinHistorico` | `422` | rentabilidad-twr |
| `EstrategiaInexistente` / `TickerFueraDeCartera` | `404` | estrategias-indicador, backtesting, operaciones-recomendadas |
| `ParametrosNoValidos` | `400` | estrategias-indicador, backtesting, operaciones-recomendadas |

Las consultas de posiciones no lanzan `ProveedorNoDisponible`: devuelven cada posición sin precio con su motivo (importacion-cartera). Los errores de subida (`413`, `415`, `422`) los genera la validación de la importación.

### A8. Frontera entre `Decimal` y float
- **`Decimal`/`NUMERIC`:** importes y cantidades del XLSX, rendimiento por posición, precios almacenados, stop-loss y objetivo.
- **float64 (pandas):** series de rentabilidades diarias, TWR e indicadores.
- **Redondeo explícito al serializar:** 6 decimales en las rentabilidades de la API y 2 en los importes.
- **Tests:** las rentabilidades se comparan con una tolerancia de 1e-9 y los importes de forma exacta.
- **Alternativa descartada:** `Decimal` en todas las series. pandas no vectoriza con `Decimal` y los cálculos serían órdenes de magnitud más lentos sin ganar precisión significativa en ratios.

### A9. Despliegue solo local
`docker compose` con los servicios `db`, `api` y `web`. CI (GitHub Actions) ejecuta lint, tests y auditorías, sin fase de despliegue.
- **Alternativa descartada:** PaaS público. Sin autenticación, cualquier visitante podría sustituir la cartera única.

### A10. Proveedor de precios
| Criterio | yfinance | Stooq | Alpha Vantage (gratis) |
|---|---|---|---|
| Clave de API | No | Según algunas fuentes, sí (tras CAPTCHA) | Sí |
| Límite | Sin documentar; errores de límite frecuentes desde 2025 | Sin documentar; al superarlo responde HTML en vez de CSV | 25 peticiones al día y 5 por minuto |
| Histórico | Completo | Completo | Solo los últimos 100 días |
| Varios tickers por petición | Sí | No | No |
| Eventos de split | Sí | No | No |
| Ajuste | Configurable; OHLC ajustado por splits | No está claro | Precio real sin ajustar; el ajustado es de pago |

- **Elegido:** yfinance como único proveedor real, con `auto_adjust=False` explícito y todos los tickers en una sola llamada. Además, un **proveedor de ficheros** (CSV en `app/recursos/precios-demo/`, A13) para los tests y para grabar la demo sin conexión.
- **Alternativa descartada:** Alpha Vantage gratuito. Con 100 días no cubre el calentamiento de 200 sesiones ni el backtest.
- **Alternativa descartada:** Stooq como respaldo automático. Sin eventos de split y con un ajuste incierto, mezclar proveedores daría series inconsistentes de un mismo ticker según de dónde hubiera llegado cada tramo.
- **Contrato del puerto `ProveedorPrecios`:**
  - Recibe los tickers y un rango de fechas, y devuelve por ticker el OHLC tal como lo da el proveedor, el tipo de ajuste y los eventos de split.
  - **Clasifica los errores** en `ProveedorNoDisponible` (red, timeout, límite de peticiones, error del servidor, HTML en lugar de datos) y `TickerSinDatos` (el proveedor responde sin filas; yfinance devuelve tablas vacías sin lanzar excepción).
  - **Traduce los símbolos** en los dos sentidos (`BRK.B` ↔ `BRK-B`).
  - **Convierte los float a `Decimal`** redondeando a 6 decimales.
- **Reintentos:** timeout de 10 s y 2 reintentos con espera creciente, solo ante límite de peticiones o error del servidor. Tras un fallo, no se vuelve a llamar al proveedor durante 60 s.
- **Tests de contrato:** la misma batería contra el proveedor de ficheros siempre y contra yfinance solo si se activa expresamente, fuera del CI normal.
- **Sacrificio:** se depende de una librería no oficial sujeta a las condiciones de Yahoo. Se acepta porque el uso es educativo y local (A9), y queda mitigado por el puerto y la caché.

### A11. Respuesta de la API cuando el proveedor no está disponible
Regla: **se usa la caché aunque esté desactualizada**, y solo se responde `503` cuando la caché no cubre el rango que necesita la petición. Las respuestas ya incluyen la fecha de la sesión usada.

| Endpoint | Proveedor caído, caché suficiente | Proveedor caído, caché insuficiente |
|---|---|---|
| `POST /api/cartera/importacion` | No usa el proveedor | No usa el proveedor |
| `GET /api/cartera/posiciones` | `200` con el último cierre en caché | `200`; las posiciones afectadas van sin precio y con su motivo |
| `GET /api/estrategias` | `200` | `200` |
| TWR, señales, histórico, backtest y recomendaciones | `200` con la fecha de la sesión usada | `503` |

- **`422` frente a `503`:** `422` significa que el proveedor respondió y el ticker no tiene histórico (`TickerSinDatos`); `503`, que no se pudo contactar con el proveedor (`ProveedorNoDisponible`).
- **Cuerpo del `503`:** formato estándar de errores HTTP (`application/problem+json`) con tipo, título y detalle, sin datos internos del proveedor, y cabecera `Retry-After: 60`, que el frontend usa para el botón de reintentar.
- **Alternativa descartada:** `503` en cuanto falla el proveedor. Bloquearía el dashboard aunque los datos de la sesión anterior estén en caché.

### A12. Indicadores técnicos: TA-Lib detrás de un puerto
El catálogo de estrategias crecerá (MACD, Bollinger…), así que el cálculo numérico de los indicadores se delega en una librería detrás del puerto `IndicadoresTecnicos`. La lógica que exigen las specs sigue siendo propia del dominio:
- reglas de señal;
- intensidad;
- "Sin datos suficientes";
- fecha de inicio de la señal.

| Criterio | Propia | pandas-ta | TA-Lib |
|---|---|---|---|
| Crecimiento del catálogo | Cada indicador se implementa y valida a mano | Más de 130 indicadores | Más de 150 indicadores, estándar del sector |
| Mantenimiento | Del proyecto | En declive: un fork advierte de que el original se archivará si no hay más apoyo antes del 1-7-2026; NumPy 2 sobre todo vía forks | Activo; wheels binarias con la librería C incluida desde la 0.6.5 |
| Docker | Sin dependencias nativas | Sin dependencias nativas | Dependencia nativa, sin compilador gracias a los wheels |
| Arranque de Wilder | Control total | Parcial | "Periodo inestable" configurable con `set_unstable_period()` |

- **Elegido:** TA-Lib (paquete `TA-Lib` ≥ 0.6.5, emparejado con NumPy 2) como adaptador del puerto `IndicadoresTecnicos`. El puerto recibe series de pandas y devuelve series alineadas por fecha.
- **Histórico mínimo:** el periodo en las SMA y el periodo + 100 sesiones en el RSI y el ATR (delta de `estrategias-indicador`). Así el peso del arranque del suavizado queda por debajo del 0,1 % y no hace falta configurar el periodo inestable de TA-Lib. Las compras sin ATR suficiente no se recomiendan (delta de `operaciones-recomendadas`).
- **Validación:**
  - tests de contrato del adaptador con fixtures de valores de referencia publicados (tabla de StockCharts ChartSchool para RSI(14) y ATR(14)), con tolerancia de 1e-6;
  - una implementación mínima de RSI y ATR de Wilder **solo en los tests**, como oráculo independiente.
- **Alternativa descartada:** implementación propia en producción. Es razonable con 3 indicadores, pero no escala a un catálogo que crece.
- **Alternativa descartada:** pandas-ta, por el riesgo de mantenimiento.
- **Sacrificio:** la imagen de la API gana una dependencia nativa. Si los wheels no cubren la plataforma de un desarrollador, habrá que compilar la librería C.

### A13. Estructura del repositorio
```
.
+-- .claude/                    # comandos y skills de OpenSpec para el agente
+-- .github/workflows/ci.yml    # lint, tipos, import-linter, tests, auditorías y secretos
+-- backend/
|   +-- pyproject.toml  uv.lock # dependencias (uv), ruff, mypy y contratos de import-linter
|   +-- alembic/                # migraciones versionadas
|   +-- app/
|   |   +-- main.py             # punto de arranque: crea FastAPI y conecta puertos y adaptadores
|   |   +-- api/                # capa HTTP
|   |   |   +-- routers/        #   cartera.py, rentabilidad.py, estrategias.py, backtests.py, recomendaciones.py
|   |   |   +-- errores.py      #   excepciones de dominio -> HTTP y problem+json (A7, A11)
|   |   |   +-- dependencias.py #   inyección de casos de uso y adaptadores
|   |   +-- application/        # casos de uso: orquestan dominio y puertos, sin lógica financiera
|   |   |   +-- puertos.py      #   LectorCartera, ProveedorPrecios, RepositorioCartera, CachePrecios, Reloj, ClienteLLM
|   |   |   +-- mercado.py      #   servicio de datos de mercado: rango, cobertura, refresco, caché desactualizada
|   |   |   +-- importar_cartera.py, consultar_posiciones.py, calcular_twr.py,
|   |   |       calcular_senales.py, ejecutar_backtest.py, recomendar_operaciones.py
|   |   +-- domain/             # lógica financiera pura: solo stdlib, pandas y numpy
|   |   |   +-- modelos.py      #   Posicion, SerieDiaria, Senal... (dataclasses)
|   |   |   +-- errores.py      #   CarteraNoImportada, TickersSinHistorico, ParametrosNoValidos...
|   |   |   +-- posiciones.py   #   rendimiento, días de tenencia, ST/LT
|   |   |   +-- mercado.py      #   normalización a dos series, calendario de sesiones (A4, A5)
|   |   |   +-- twr.py
|   |   |   +-- indicadores/    #   puerto.py (IndicadoresTecnicos) + histórico mínimo (A12)
|   |   |   +-- estrategias/    #   catalogo.py, rsi.py, cruce_medias.py (un fichero por estrategia)
|   |   |   +-- backtest.py
|   |   |   +-- recomendaciones.py
|   |   +-- adapters/           # implementaciones de puertos contra sistemas externos y librerías
|   |   |   +-- xlsx/lector_xlsx.py        # openpyxl + defusedxml
|   |   |   +-- precios/yfinance.py, ficheros.py
|   |   |   +-- indicadores/talib.py
|   |   |   +-- llm/cliente_llm.py         # S1 (opcional)
|   |   |   +-- reloj.py
|   |   +-- infrastructure/     # persistencia y configuración
|   |   |   +-- config.py       #   ajustes por entorno (BENCHMARK_TICKER, proveedor, BD)
|   |   |   +-- db/             #   session.py, modelos ORM, repositorios (RepositorioCartera, CachePrecios)
|   |   +-- recursos/           # ficheros incluidos en la imagen
|   |   |   +-- cartera-ejemplo.xlsx   # GET /api/cartera/ejemplo, seed y tests
|   |   |   +-- precios-demo/          # CSV del proveedor de ficheros (demo sin conexión, A10)
|   |   +-- scripts/seed.py
|   +-- tests/
|       +-- unit/               # dominio con los ejemplos numéricos de las specs; reloj fijo
|       +-- contract/           # adaptadores de precios e indicadores (TA-Lib frente a StockCharts)
|       +-- integration/        # API + PostgreSQL (Testcontainers) con el proveedor de ficheros
|       +-- fixtures/           # XLSX maliciosos y no válidos (solo tests)
+-- frontend/
|   +-- src/
|   |   +-- app/                # router, proveedores (TanStack Query), estrategia seleccionada
|   |   +-- features/           # cartera/, rentabilidad/, estrategias/, backtesting/, recomendaciones/
|   |   |                       #   cada una con api.ts, componentes y hooks propios
|   |   +-- shared/
|   |       +-- api/            # cliente HTTP y tipos generados desde el OpenAPI (openapi-typescript)
|   |       +-- ui/             # avisos legales, etiquetas de color, formato de USD y %
|   +-- e2e/                    # Playwright
+-- docs/                       # wireframes y capturas
+-- openspec/
|   +-- config.yaml             # contexto y reglas del proyecto para el agente
|   +-- specs/<capability>/spec.md   # verdad vigente
|   +-- changes/<change>/       # proposal, specs (deltas), design, tasks
|       +-- archive/            # changes aplicados; su design.md hace de ADR
+-- docker-compose.yml  .env.example  CLAUDE.md  readme.md  prompts.md
```

**Reglas de dependencias:**
- **Backend** (contratos de import-linter en `pyproject.toml`): `api → application → domain`; `adapters` e `infrastructure` solo dependen de `application.puertos` y de `domain.indicadores.puerto`; `domain` no importa nada de `api`, `application`, `adapters` ni `infrastructure`, ni FastAPI, SQLAlchemy, yfinance, openpyxl o TA-Lib.
- **Frontend** (ESLint `import/no-restricted-paths`): una feature no importa otra; lo común pasa por `shared/`.
- `IndicadoresTecnicos` vive en `domain/` y no en `application/` porque es un puerto de cálculo puro que usa el propio dominio, no un puerto de I/O.

**Decisiones:**
- **Idioma de los identificadores:** dominio, puertos, casos de uso y adaptadores en castellano, con el vocabulario de las specs. En inglés solo lo que impone el framework o la convención (`main.py`, `config.py`, `session.py`, `routers/`, `conftest.py`) y los nombres de producto (`yfinance.py`, `talib.py`).
  - **Alternativa descartada:** todo en inglés. Obliga a traducir entre specs y código (posición → position, plusvalía → capital gain).
  - **Alternativa descartada:** todo en castellano. Choca con los nombres que esperan las herramientas.
- **Frontend por feature:** cada change de una feature toca una sola carpeta.
  - **Alternativa descartada:** por tipo (`pages/`, `components/`, `hooks/`, `api/`). Reparte cada feature en cuatro carpetas.
  - **Sacrificio:** hay que decidir qué es compartido y qué es de una feature.
- **Gestor de dependencias del backend: uv.** `uv sync --frozen` en Docker y CI fija exactamente pandas, numpy y TA-Lib, de modo que los resultados numéricos no cambian entre entornos.
  - **Alternativa descartada:** pip con requirements (bloqueo manual).
  - **Alternativa descartada:** Poetry (más lento, sin ventaja para este proyecto).
- **Recursos incluidos en la imagen** (`app/recursos/`): el XLSX de ejemplo y los precios de demo se sirven o se usan en ejecución, así que no pueden estar en `tests/`, que no se copia a la imagen. Los tests los leen desde `app/recursos/`. `tests/fixtures/` queda solo para ficheros no válidos o maliciosos.
- **Sin ADR en `docs/`:** el `design.md` de cada change archivado hace de registro de decisiones. `docs/` queda para wireframes y capturas.

### Trazabilidad OpenSpec → readme
Precedencia: las specs prevalecen sobre `design.md` y este sobre el readme. El apply actualiza las secciones de esta tabla y el archive comprueba que el readme no contradice las specs.

| Sección del readme | Artefacto de origen | Qué se toma | Se actualiza al |
|---|---|---|---|
| 0. Ficha | — (manual) | Datos de la entrega | — |
| 1.1 Objetivo | `proposal.md` (Why) · `config.yaml` (contexto) | Problema, valor y destinatarios | apply |
| 1.2 Funcionalidades | `specs/*/spec.md` (Purpose y requisitos) · `proposal.md` (What Changes, Fuera de alcance) | Tabla F1-F5, S1-S3, alcance | apply y archive |
| 1.3 Diseño y UX | `specs/*/spec.md` (requisitos "en pantalla") | Elementos visibles y avisos | apply |
| 1.4 Instalación | `tasks.md` (DevOps) · `design.md` (Migration Plan) | Pasos y variables de entorno | apply |
| 2.1 Diagrama | `design.md` (Decisions, Mermaid) | Patrón, componentes, beneficios y sacrificios | apply |
| 2.2 Componentes | `design.md` (tabla de componentes) | Componente, tecnología y responsabilidad | apply |
| 2.3 Estructura | `design.md` (estructura y reglas de dependencias) | Árbol, propósito de cada directorio y esta tabla | apply |
| 2.4 Infraestructura | `design.md` (despliegue) · `tasks.md` (DevOps) | Compose y CI | apply |
| 2.5 Seguridad | `design.md` (seguridad) · `specs` (rechazos con código HTTP) | Riesgo y control; controles pendientes de spec marcados | apply |
| 2.6 Tests | `specs` (escenarios WHEN/THEN) · `tasks.md` (Tests) | Casos con sus valores numéricos | apply |
| 2.7 Stack | `design.md` · `config.yaml` (stack previsto) | Tecnología y motivo | apply |
| 3. Modelo de datos | `design.md` (erDiagram) | Entidades, claves, restricciones y fórmulas | apply |
| 4. API | `specs` (requisitos "por HTTP") | Endpoints, códigos y OpenAPI | apply y archive |
| 5. Historias de usuario | `specs` (escenarios) · `proposal.md` (F/HU) | Gherkin con ejemplos | apply |
| 6. Tickets | `tasks.md` | Tareas, criterios de aceptación y backlog | apply |
| 7. Pull requests | — (un PR por change, si se usan) | Enlace y resumen | merge |

### Componentes principales
| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Frontend SPA | React 18 + TypeScript + Vite | Carga del XLSX, Watchlist, paneles de TWR, señales, backtest y recomendaciones; estrategia seleccionada compartida; avisos legales |
| Datos del servidor y tablas | TanStack Query · TanStack Table | Caché de peticiones y recarga tras importar; ordenación y filtros |
| Gráficos | Recharts · Lightweight Charts | Barras de TWR y curvas base 100; precio con el indicador en un panel inferior y marcas de cambio de señal |
| API REST | FastAPI · Pydantic v2 · Uvicorn | Validación, OpenAPI y traducción centralizada de errores (A7), con `application/problem+json` y `Retry-After` (A11) |
| Casos de uso | Python | Un caso de uso por operación; orquestan dominio y puertos; transacción de la importación |
| Servicio de datos de mercado | Python · pandas | Rango con calentamiento, calendario, cobertura y refresco, barra del día, invalidación por split, normalización a dos series y caché desactualizada (A4, A5, A11) |
| Dominio · posiciones | Python · `Decimal` | Precio de referencia, rendimiento, días de tenencia y ST/LT |
| Dominio · TWR | pandas (float64) | Valoración diaria sin ajustar, rentabilidad con flujos, TWR acumulada, anualizada, mensual y semanal, curva base 100 |
| Dominio · indicadores | Python, sobre el puerto `IndicadoresTecnicos` | Histórico mínimo, "Sin datos suficientes" y alineación de series |
| Dominio · estrategias | Python | Catálogo, validación de parámetros, reglas, intensidad y fecha de inicio de la señal |
| Dominio · backtest | pandas | Simulación sin sesgo de anticipación, métricas, comparativa y mejoras |
| Dominio · recomendaciones | Python · `Decimal` | Hasta 10 operaciones, stop-loss y objetivo por ATR, aviso fiscal |
| Adaptador XLSX | openpyxl · defusedxml | Seguridad del fichero, parseo, cabeceras flexibles y validación por fila |
| Adaptador proveedor de precios | yfinance (`auto_adjust=False`) · proveedor de ficheros | OHLC y splits; errores clasificados, símbolos y `Decimal` (A10) |
| Adaptador indicadores | TA-Lib ≥ 0.6.5 | RSI, SMA y ATR de Wilder, y los indicadores futuros (A12) |
| Repositorios y caché | SQLAlchemy 2 · Alembic | Cartera vigente atómica, `PRECIO_DIARIO` y `COBERTURA_PRECIO` con upsert; migraciones |
| Reloj | `datetime` · `zoneinfo` | Fecha y hora con zona de Nueva York; fijo en tests (A6) |
| Cliente LLM (S1, opcional) | SDK del proveedor de LLM | Justificación con salida JSON validada; no influye en el orden |
| Base de datos | PostgreSQL 16 | `NUMERIC`, CHECK y transacciones |
| Calidad de arquitectura | import-linter · ruff · mypy | Que el dominio no importe adaptadores (incluido TA-Lib) ni infraestructura; lint y tipos |

### Modelo de datos
```mermaid
erDiagram
    PRECIO_DIARIO {
        varchar ticker PK
        date fecha PK
        numeric apertura "NOT NULL; ajustado por splits"
        numeric maximo "NOT NULL; ajustado por splits"
        numeric minimo "NOT NULL; ajustado por splits"
        numeric cierre "NOT NULL; ajustado por splits"
        numeric cierre_sin_ajustar "NOT NULL; CHECK > 0"
        varchar fuente "NOT NULL"
        timestamptz obtenido_en "NOT NULL"
    }
    COBERTURA_PRECIO {
        varchar ticker PK
        date desde "NOT NULL"
        date hasta "NOT NULL; CHECK hasta >= desde"
        timestamptz actualizado_en "NOT NULL"
        date ultimo_split "NULL si no hay splits"
    }
    COBERTURA_PRECIO ||--o{ PRECIO_DIARIO : "cubre el rango de"
```
`COBERTURA_PRECIO` y `PRECIO_DIARIO` se relacionan por `ticker`, sin FK, porque `PRECIO_DIARIO` se escribe con upsert por lotes. `IMPORTACION` y `POSICION` no cambian.

## Risks / Trade-offs

- [El proveedor no devuelve eventos de split o los corrige más tarde] → invalidación por `ultimo_split` (A5), que vuelve a descargar y normalizar todo el histórico del ticker; test de contrato con un ticker con splits conocidos.
- [TA-Lib cambia ligeramente los resultados entre versiones] → versión fijada en el lock de dependencias y tests de contrato con valores de referencia.
- [Yahoo bloquea las peticiones durante la grabación de la demo] → proveedor de ficheros (A10) y caché ya poblada.
- [yfinance es una librería no oficial y puede romperse o limitar peticiones] → puerto `ProveedorPrecios`, caché persistente y `503` explícito.
- [import-linter solo protege si se ejecuta] → forma parte del job de lint de CI y bloquea el merge.
- [Diferencias de redondeo entre float y los ejemplos de las specs] → la tolerancia y el redondeo al serializar se documentan en la sección de tests.

## Migration Plan

No hay código todavía. En la Entrega 2, la migración inicial (DB-01) crea `PRECIO_DIARIO` ya con `cierre_sin_ajustar` y la tabla `COBERTURA_PRECIO`, así que no hace falta una migración incremental.

# Automation Project

Framework de automatización web para practicar y validar flujos de **QA Practice** y **Script Labs** con Python, Playwright y BehaveX. Los escenarios se describen en Gherkin y se conectan con pasos reutilizables, módulos funcionales y datos de prueba.

## Alcance

El repositorio contiene escenarios de login y registro, búsqueda y compra en e-commerce, validaciones negativas, operaciones CRUD y reserva de vuelos. La selección efectiva de una corrida depende de las etiquetas pasadas a BehaveX; la ejecución predeterminada del launcher selecciona los tres escenarios de Script Labs.

## Requisitos

- Python compatible con las versiones de dependencias fijadas en `requirements.txt`.
- Git para obtener y actualizar el repositorio.
- Navegador Chromium administrado por Playwright.

## Instalación

Desde la raíz del repositorio, crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias y el navegador:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

En macOS o Linux, activa el entorno virtual con `source .venv/bin/activate`. Si Playwright solicita dependencias del sistema para Chromium, instálalas en el equipo de ejecución.

## Ejecución con BehaveX

`run_behavex.py` es el punto de entrada del proyecto. Usa BehaveX para seleccionar escenarios Gherkin por tags y fija por defecto una ejecución secuencial (`--parallel-processes 1`) con esquema `scenario`. Las opciones del launcher permiten elegir tags, línea de insumos, modo del navegador y generación del PDF general:

Internamente, el launcher arma la llamada de BehaveX con `--parallel-processes`, `--parallel-scheme`, `-ip <feature-path>`, `--tags <filtro>` y `-o <output-dir>`. Los argumentos del launcher controlan esos parámetros y las variables `LINEA`, `HEADLESS` y `PDF_GENERAL` que leen los hooks.

```powershell
# Ejecuta los tres flujos Script Labs definidos como predeterminados
python run_behavex.py

# Ejecuta una selección de escenarios etiquetados, visible y con datos L1
python run_behavex.py --tags "@test_login_qa_practice_datos_correctos, @test_ecom_busqueda_sin_resultados" --linea L1 --headed --no-pdf-general

# Ejecuta los escenarios de e-commerce en L2, sin ventana, con PDF general
python run_behavex.py --tags "@ecommerce_scenarios" --linea L2 --headless --pdf-general
```

### Opciones del launcher

| Opción | Uso | Valor predeterminado |
|---|---|---|
| `--tags` | Expresión de tags que BehaveX usa para filtrar escenarios. Usa las etiquetas `@test...` o de módulo presentes en los `.feature`. | No hay. |
| `--linea L1\|L2` | Elige la línea de insumos. Los pasos leen esta variable para cargar los datos correspondientes. | `L1` |
| `--headless` / `--headed` | Oculta o muestra la ventana de Chromium. | Según `HEADLESS`; si no se define, `headed`. |
| `--pdf-general` / `--no-pdf-general` | Activa o desactiva el resumen y los PDFs consolidados del run. | Según `PDF_GENERAL`; si no se define, activado. |
| `--feature-path` | Carpeta que contiene los archivos `.feature`. | `features` |
| `--output-dir` | Carpeta donde BehaveX escribe su salida HTML y artefactos del runner. | `Documents/Scripts/Automation_Project/output` bajo el perfil del usuario. |
| `--parallel-processes` | Procesos de BehaveX. Aumentarlo puede cambiar el orden y la concurrencia de escenarios. | `1` |
| `--parallel-scheme` | Estrategia que BehaveX usa al paralelizar. | `scenario` |

El filtro se controla por tags. Por ejemplo, cada escenario debe tener una etiqueta identificable como `@test_login_qa_practice_datos_correctos`. Las expresiones de tags múltiples se pasan entre comillas. Si el runner no encuentra escenarios, revisa la etiqueta y el archivo `.feature` antes de cambiar la lógica de los pasos.

También se pueden definir valores por variables de entorno. Las opciones explícitas del launcher tienen prioridad:

```powershell
$env:LINEA = "L2"
$env:HEADLESS = "True"
$env:PDF_GENERAL = "False"
$env:BEHAVEX_TAGS = "@ScriptLabs"
python run_behavex.py
```

## Cómo añadir un test

Los escenarios de Behave describen el comportamiento en archivos Gherkin. Antes de crear un paso nuevo, busca si ya existe en `features/steps/`; reutilizar un paso mantiene una sola implementación por acción.

### 1. Añade el escenario al feature del módulo

Ejemplo basado en los escenarios actuales de login:

```gherkin
@automated @Qa_Practice @login_scenarios
Feature: Login

  @test @test_login_qa_practice_nuevo @positivo
  Scenario: Login con un perfil válido
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Valido que el titulo diga "Login Successful! Welcome to Premium Banking."
```

Agrega tags que permitan seleccionarlo desde `--tags`, y separa escenarios positivos y negativos. Incluye una validación observable del resultado esperado.

### 2. Reutiliza o implementa los pasos

Los pasos se organizan por dominio en `features/steps/`, por ejemplo `login_steps.py`, `ecommerce_steps.py` y `vuelos_steps.py`. Si el paso no existe, define su expresión con el decorador `@step`, valida los datos de entrada y delega la interacción a una función de `modulos/`.

El paso de login de QA Practice ya muestra el patrón usado por el proyecto en `features/steps/login_steps.py`:

```python
@step('Realizar login con el perfil "{perfil}" en QA Practice')
def step_login_qa_practice(context, perfil):
    _ejecutar_login(context, perfil, "QA Practice")
```

Si implementas un paso nuevo, usa `@step(...)`, valida los datos y delega la acción en la función correspondiente de `modulos/`. Mantén las aserciones explícitas cerca de la validación. La configuración global de navegador, evidencia y limpieza vive en `features/environment.py`, mediante hooks `before_*` y `after_*` de Behave.

### 3. Registra los datos y selectores

- Si el escenario necesita datos diferentes por línea, agrega un perfil en `librerias/insumos/<Modulo>/datos_test.py` y, cuando aplique, su versión `_L2.py`. La carga se resuelve usando `LINEA`.
- Los catálogos de perfiles se encuentran en `librerias/insumos/<Modulo>/catalogo_usuarios.py`.
- Los selectores se mantienen en `librerias/selectores.json`. Prefiere roles, labels, placeholders, texto estable o atributos de prueba; evita depender de clases o posiciones frágiles.
- No guardes contraseñas reales o información personal en el repositorio, capturas o reportes.

### 4. Ejecuta el nuevo escenario y adjunta evidencia

```powershell
python run_behavex.py --tags "@test_login_qa_practice_nuevo" --headed --linea L1 --no-pdf-general
```

Revisa el estado del escenario, el HTML del runner y las evidencias del caso. En el pull request, incluye el resultado de la corrida, el cambio de código y los artefactos solicitados por el equipo.

## Capacidades y evidencias

Durante una ejecución, el framework puede producir los siguientes seis tipos de salida:

1. **Reporte individual por prueba:** PDF con capturas y descripción de pasos del escenario.
2. **Reporte general detallado:** PDFs consolidados con capturas y pasos de los escenarios del run; se divide en lotes de hasta diez escenarios por PDF.
3. **Reporte general de resumen:** PDF con estadísticas generales, sin capturas ni pasos.
4. **Reporte HTML de BehaveX:** resultado de ejecución generado por el runner en su directorio de salida.
5. **Video por escenario:** grabación del navegador en formato WebM.
6. **Trace de Playwright:** archivo ZIP con snapshots, screenshots y fuentes habilitadas en la traza; puede abrirse con `playwright show-trace <archivo.zip>`.

Las evidencias individuales y los paquetes PDF se guardan bajo `Documents/Scripts/Automation_Project/evidencias/<fecha>/` de acuerdo con `librerias/directorios.py`. La salida HTML de BehaveX se guarda en `Documents/Scripts/Automation_Project/output/`. `--pdf-general` activa el resumen, los PDFs detallados y un ZIP consolidado del run. Las capturas individuales, el video, la traza y los logs se gestionan desde los hooks de `features/environment.py`.

### Self-healing y SmartMatcher

`helpers/self_healing.py` prueba los selectores definidos para un elemento en orden. Si el principal falla, prueba alternativas guardadas; un selector secundario que funcione puede promoverse a principal y el cambio se registra. Si todos fallan y hay una huella digital, escanea candidatos del DOM y solicita a `helpers/matcher.py` compararlos por texto, id, posición/tamaño, contexto cercano, nombre, clase y placeholder. Los pesos disponibles se redistribuyen según los atributos presentes y el resultado debe superar el umbral de similitud de la huella.

Cuando encuentra un candidato, el helper puede generar selectores nuevos y persistirlos para ejecuciones posteriores. También conserva selectores obsoletos y genera logs de cambios e intervenciones. Este mecanismo ayuda a recuperar pruebas ante cambios de interfaz; la aserción del resultado funcional sigue siendo necesaria para confirmar que se operó el elemento correcto. Revisa los registros `self_healing_changes.txt` y `self_healing_ai_history.txt` cuando ocurra una recuperación.

## Mapa del repositorio

| Ruta | Contenido |
|---|---|
| `features/` | Features Gherkin, hooks de Behave y rollback/recuperación. |
| `features/steps/` | Definiciones de pasos organizadas por dominio. |
| `modulos/` | Acciones y validaciones funcionales por pantalla/proceso. |
| `librerias/insumos/` | Perfiles y datos de prueba separados por módulo y línea. |
| `librerias/selectores.json` | Selectores y huellas digitales empleadas por self-healing. |
| `helpers/self_healing.py` | Resolución, recuperación, actualización y registro de selectores. |
| `helpers/matcher.py` | Cálculo de similitud y selección del candidato DOM. |
| `features/environment.py` | Ciclo de vida del navegador, registros, limpieza y generación de evidencias. |
| `run_behavex.py` | Parámetros de ejecución de BehaveX y configuración del run. |

## Notas de operación

- La automatización usa Chromium y Playwright síncrono. El proyecto usa Behave/BehaveX con Gherkin; Pytest no es el runner de esta solución.
- El modo visible es útil al depurar; el modo headless se activa con `--headless`.
- Elige `--linea L1` o `--linea L2` según los datos preparados para el módulo.
- El PDF general puede desactivarse para corridas cortas con `--no-pdf-general`; los reportes individuales y otras evidencias se controlan por los hooks.
- La ruta base de salida se define en `librerias/directorios.py`. En otra máquina, revisa las rutas absolutas/de usuario y confirma permisos de escritura antes de ejecutar.
- Las páginas de prueba son servicios externos, aunque el runner y los datos se ejecuten localmente. La disponibilidad de esas páginas puede afectar una corrida.
- Cada pull request debe adjuntar las evidencias de ejecución correspondientes, como práctica del equipo.

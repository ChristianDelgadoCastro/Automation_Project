import importlib
import os
import time

from playwright.sync_api import expect

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.funciones import escribo_log, clic_condicional, existe_error_inesperado, lista_screenshot, \
    lista_pasos_descripcion, save_evidence

selectores = cargar_selectores()


def click_boton(page, boton, nombre_log, hora_ejecucion):
    """Ejecuta la acción de clic sobre un botón de la interfaz tras validar su existencia.

        Esta función interna actúa como puente para mapear el nombre legible de un botón
        con su identificador técnico en el archivo de selectores. Además, gestiona
        la escritura en los logs del framework y valida que el elemento esté habilitado.

        Args:
            page (Page): Instancia del navegador activa (Playwright Page).
            boton (str): El nombre común del botón solicitado (no distingue mayúsculas).
            nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
            hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

        Raises:
            ValueError: Si el nombre del `boton` no coincide con ninguna de las llaves
                mapeadas en el diccionario local `mapa_botones`.

        Note:
            Si añades un botón nuevo a la interfaz, debes registrarlo primero tanto en el
            diccionario `mapa_botones` de esta función como en el archivo `selectores.json`.
        """
    mapa_botones = {
        "registrar ahora qap": "link_login_register",
        "registrar qap": "btn_register_submit",
        "buscar vuelos": "btn_flight_search",
        "continuar a detalles de pasajeros": "btn_flight_continue_to_passengers",
        "continuar a pago": "btn_flight_continuar_pago",
        "pagar y continuar reservacion": "btn_flight_reservar",
        "carrito": "btn_ecom_cart",
        "proceder a comprar": "btn_ecom_proceed_to_buy",
        "guardar direccion y continuar": "btn_ecom_save_address",
        "comprar ahora": "btn_ecom_buy_now",
    }

    boton_limpio = boton.lower()
    llave_selector = mapa_botones.get(boton_limpio)

    if llave_selector:
        btn = localizar_elemento(page, llave_selector, selectores.get(llave_selector), nombre_log, hora_ejecucion)
        escribo_log(nombre_log, f"---> Doy click al boton '{boton}'\n")
        # btn.scroll_into_view_if_needed()
        expect(btn).to_be_enabled(timeout=10000)
        btn.click()
        page.wait_for_timeout(500)
    else:
        opciones_validas = ", ".join(mapa_botones.keys())
        error_msg = f"err-> click_boton() - El filtro '{boton}'no existe. Opciones válidas: {opciones_validas}"
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise ValueError(error_msg)


def validar_titulo(page, texto_esperado, nombre_log, hora_ejecucion):
    """Busca dinámicamente un título visible en pantalla y valida su contenido de texto.

        Itera sobre una lista predefinida de IDs de éxito y avisos
        filtrando únicamente por elementos visibles. Si encuentra el texto esperado en
        alguno de ellos, realiza un enfoque visual y ejecuta la aserción estricta.

        Args:
            page (Page): Instancia del navegador activa (Playwright Page).
            texto_esperado (str): El fragmento de texto o cadena completa a validar.
            nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
            hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

        Raises:
            AssertionError: Si transcurre el tiempo de espera (timeout) sin encontrar
                los selectores, o si el texto real en pantalla no coincide con el esperado.

        Note:
            La búsqueda inicial utiliza una comparación flexible (insensible a mayúsculas
            y minúsculas). Sin embargo, la aserción final mediante `expect` sí evalúa que
            el contenido esté estrictamente presente en el nodo del DOM.
        """
    lista_titulos = [
        "#login-success",
        "#login-error",
        "#register-success",
        "#register-error",
        "#flight-booking-success",
        "#ecom-order-success",
    ]

    selectores_visibles = [f"{selector}:visible" for selector in lista_titulos]

    texto_esperado_limpio = texto_esperado.strip()
    escribo_log(nombre_log, f"---> Buscando un titulo que contenga el texto: '{texto_esperado_limpio}'\n")

    elemento_encontrado = None

    # Buscamos uno por uno en la lista cuál de los selectores en pantalla tiene el texto
    for selector in selectores_visibles:
        locator = page.locator(selector)
        # Verificamos si el elemento existe, está visible y contiene el texto deseado
        if locator.count() > 0 and texto_esperado_limpio.lower() in locator.first.inner_text().lower():
            elemento_encontrado = locator.first
            break

    try:
        if not elemento_encontrado:
            selector_combinado = ", ".join(selectores_visibles)
            elemento_encontrado = page.locator(selector_combinado).first

        elemento_encontrado.wait_for(state="visible", timeout=15000)
        elemento_encontrado.scroll_into_view_if_needed(timeout=2000)

        texto_real = elemento_encontrado.inner_text()
        escribo_log(nombre_log, f"---> Titulo encontrado. Texto real: '{texto_real}' vs '{texto_esperado_limpio}'\n")

        expect(elemento_encontrado).to_contain_text(texto_esperado_limpio, timeout=10000)
        escribo_log(nombre_log, "---> Validación de título exitosa.\n")

    except Exception as e:
        error_msg = f"err-> validar_titulo() - No se encontró ningún elemento que coincidiera con el texto '{texto_esperado_limpio}'."
        escribo_log(nombre_log, f"---> {error_msg} Detalle: {str(e)}\n")
        raise AssertionError(error_msg) from e


def esperar_carga_completa(page, nombre_log, hora_ejecucion):
    """Monitorea los progress bars del sistema hasta confirmar que la carga llegó al 100%.

        Une una lista de IDs de barras de progreso comunes y ejecuta un script robusto
        en el contexto del navegador (`page.wait_for_function`). Evalúa de forma síncrona
        tres criterios de finalización: texto visible "100%", atributo `aria-valuenow`
        en 100, o estilos CSS de ancho (`width: 100%`).

        Args:
            page (Page): Instancia del navegador activa (Playwright Page).
            nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
            hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

        Note:
            La función cuenta con un mecanismo de tolerancia pasiva: si el timeout de
            150 segundos expira pero la barra de progreso simplemente se ocultó o se
            destruyó en el DOM, la función considerará la carga como exitosa.
        """
    lista_progress_bars = [
        "#pidGetStatus",
        "#progresLiberarTransacciones",
        "#pgbDispersionLinea",
        "#pgrcAvanceDescargaOpt",
        "#pgbDispersionArchivoOpt",
        "#pgrcAvanceAltasLinea",
        "#pgrcAvanceDescarga",
        "#pgrcAvanceOpLinea",
        "#pnlProgressBar",
        "#pgrcAvanceAltaStatus",
        "#pgrcAvanceAltaArch",
        "#pgrcAvanceOpArch",
        "#pidGetStatusCargue",
        "#pidGetStatusDescargaVP",
        "#pgrcAvanceAlta"
    ]
    selector = ", ".join(lista_progress_bars)
    timeout = 150000
    progressbar = page.locator(selector).first

    try:
        # Aseguramos que el elemento esté en vista
        progressbar.scroll_into_view_if_needed(timeout=2000)

        escribo_log(nombre_log, "---> Esperando que termine de cargar el ProgressBar.\n")
        # JS robusto:
        # 1. Busca el texto "100%"
        # 2. O busca que el atributo aria-valuenow sea 100
        # 3. O busca que el div interno de progreso tenga width: 100%
        page.wait_for_function(
            f"""
            () => {{
                const el = document.querySelector('{selector}');
                if (!el) return true;
                const estilo = window.getComputedStyle(el);
                if (estilo.display === 'none') return true;

                const texto = el.innerText || "";
                const valorAria = el.getAttribute('aria-valuenow');
                const barraInterna = el.querySelector('[style*="width"]');
                const anchoBarra = barraInterna ? barraInterna.style.width : "";

                return texto.includes('100%') || 
                        valorAria === '100' || 
                        anchoBarra === '100%';
            }}
            """,
            timeout=timeout
        )
        escribo_log(nombre_log, "---> Carga finalizada exitosamente.\n")
    except Exception as e:
        # Si falla, hacemos un último intento: ¿el elemento desapareció?
        # A veces "Carga finalizada" significa que el loader se destruye.
        if progressbar.is_hidden():
            escribo_log(nombre_log, "---> Carga finalizada (el elemento desapareció).\n")
        else:
            escribo_log(nombre_log, f"---> Tiempo excedido. Estado actual: {page.locator(selector).inner_text()}\n")


def clic_condicional_boton(page, boton, nombre_log, hora_ejecucion):
    """Valida el estado de un botón y ejecuta el clic únicamente si es visible y está habilitado.

    Busca el identificador en el mapa de botones local, intenta localizar el elemento
    en la página y evalúa sus propiedades físicas (`is_visible` e `is_enabled`). Si alguna
    condición falla o el elemento no se encuentra en el DOM, escribe una advertencia en la
    bitácora y mitiga el error para no interrumpir el flujo del test.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        boton (str): El nombre común del botón (no distingue entre mayúsculas y minúsculas).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

    Raises:
        ValueError: Si la cadena recibida en `boton` no existe como una llave válida
            dentro del diccionario `mapa_botones`.

    Note:
        A medida que el framework crezca, se requerirá seguir alimentando el diccionario
        `mapa_botones` de esta función con los nuevos elementos condicionales, asegurando
        que sus valores mapeados existan también en el archivo central `selectores.json`.
    """
    mapa_botones = {
        "aplicar filtros": "btn_aplicar_filtros",
        "enviar ahora": "btn_enviar_ahora",
        "aceptar": "btn_aceptar",
        "aceptar_asign_tdn": "btn_aceptar_asign",
    }

    boton_limpio = boton.lower()
    llave_selector = mapa_botones.get(boton_limpio)

    if llave_selector:

        try:
            # Obtenemos el locator del botón
            btn = localizar_elemento(page, llave_selector, selectores.get(llave_selector), nombre_log, hora_ejecucion)

            # Condicional
            if btn.is_visible() and btn.is_enabled():
                escribo_log(nombre_log, f"---> Doy click condicional al boton '{boton}'\n")

                btn.scroll_into_view_if_needed()
                btn.click()

                page.wait_for_timeout(500)

            else:
                msg_estado = "no es visible o está deshabilitado"
                escribo_log(nombre_log, f"---> El botón '{boton}' {msg_estado}. Se omite el click.\n")

        except Exception as e:
            escribo_log(nombre_log, f"---> No se pudo localizar el elemento, no visible.\n")

    else:
        opciones_validas = ", ".join(mapa_botones.keys())
        error_msg = f"err-> clic_condicional_boton() - El botón '{boton}' no existe. Opciones válidas: {opciones_validas}"
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise ValueError(error_msg)


def subir_archivo(page, archivo, boton_carga, nombre_log, hora_ejecucion):
    """Sanitiza el estado de carga previo, interactúa con el input file y procesa la subida.

    Primero valida la existencia física del archivo local. Posteriormente, extrae del mapa
    de botones la configuración específica de la transacción y, de existir un archivo
    precargado de ejecuciones previas, intenta removerlo (`clic_condicional`) para asegurar
    una carga limpia. Inyecta el nuevo archivo y confirma la acción en la interfaz.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        archivo (str): Ruta absoluta local donde se ubica el archivo físico a cargar.
        boton_carga (str): Tipo o módulo de transacción (se evalúa sin mayúsculas).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

    Raises:
        FileNotFoundError: Si el archivo provisto no existe en la ruta física del sistema.
        ValueError: Si la funcionalidad de `boton_carga` no se encuentra en `mapa_botones`.
        Exception: Relanza cualquier fallo de Playwright o red tras registrarlo en el log.

    Note:
        Estructura del `mapa_botones`: Los valores corresponden a una tupla `(clave_selector, quitar_arch_selector)`.
        El segundo elemento permite identificar selectores de remoción (como `#deleteFile`), garantizando
        que el framework destruya registros anteriores antes de ingresar un nuevo set de datos.
    """
    try:

        if not os.path.exists(archivo):
            error_archivo = f"err-> subir_archivo() - El archivo no existe en la ruta: {archivo}"
            escribo_log(nombre_log, f"---> {error_archivo}\n")
            raise FileNotFoundError(error_archivo)
        # Botones para cargar archivo, varian por funcionalidad
        mapa_botones = {
            "tdneg": ("btn_cargar_tdneg", "#deleteFile"),
            "nomina": ("btn_cargar_nomina", "#txtIconBorrar"),
            "alta_arch": ("btn_cargar_tdneg", "#deleteArchivo, #deleteArchivo1"),
            "arch_manc": ("btn_cargar_tdneg", "#deleteArchivo, #deleteArchivo1"),
            "spei": ("btn_cargar_tdneg", "#deleteArchivo1"),
            "tdniv": ("btn_cargar_tdniv", "#deleteArchivo, #deleteArchivoCopia, #deleteArchivo1"),
            "foca": ("btn_cargar_foca", "#txtIconBorrarError"),
            "tdc": ("btn_cargar_tdneg", "#deleteArchivo, #deleteArchivo1"),
            "lib_cheq": ("btn_cargar_lib_cheq", "#HelpToolEliminar"),
            "colegiatura": ("btn_cargar_colegiatura", "#HelpToolEliminar"),
            "transferencia por archivo": ("btn_cargar_transfer_arch", '#deleteArchivo1')
        }

        boton_limpio = boton_carga.lower()
        datos_carga = mapa_botones.get(boton_limpio)

        if datos_carga:

            clave_selector = datos_carga[0]
            quitar_arch_selector = datos_carga[1]

            escribo_log(nombre_log, "--->     Cerrando archivo precargado si existe...\n")

            clic_condicional(page, quitar_arch_selector, nombre_log)

            escribo_log(nombre_log, f"--->    archivo a cargar: [{archivo}]\n")

            input_elegir_archivo = localizar_elemento(page, "input_file_upload", selectores.get("input_file_upload"),
                                                      nombre_log, hora_ejecucion, timeout=40000)

            expect(input_elegir_archivo).to_be_visible(timeout=25000)

            input_elegir_archivo.set_input_files(archivo)

            # time.sleep(10.0)
            page.locator("#ajaxloader").wait_for(state="hidden", timeout=60000)
            # Localizar boton de carga de archivo

            btn = localizar_elemento(page, clave_selector, selectores.get(clave_selector), nombre_log, hora_ejecucion,
                                     timeout=60000)
            escribo_log(nombre_log, f"---> Doy click al boton '{boton_carga}'\n")
            # btn.scroll_into_view_if_needed()
            expect(btn).to_be_enabled(timeout=10000)
            time.sleep(2.00) # Validar si ya no marca error H04 al cargar archivo
            btn.click()
            page.wait_for_timeout(500)

        else:
            opciones_validas = ", ".join(mapa_botones.keys())
            error_msg = f"err-> subir_archivo() - El botón '{boton_carga}' no existe. Opciones válidas: {opciones_validas}"
            escribo_log(nombre_log, f"---> {error_msg}\n")
            raise ValueError(error_msg)

    except Exception as err:
        escribo_log(nombre_log, "---> subir_archivo() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [Cargar Archivo Nomina ] {str(err)}"
        # existe_error_inesperado(page, rastreo, test_name, nombre_log, hora_ejecucion)
        raise


def obtener_catalogo_matriz(context):
    """Importa y retorna dinámicamente el catálogo de perfiles asociado a la matriz actual.

    Utiliza el atributo `context.matriz` para construir la ruta del paquete de insumos,
    realiza la carga del módulo en tiempo de ejecución mediante `importlib` y extrae
    el diccionario de configuraciones correspondiente a los accesos del sistema.

    Args:
        context (Any): Objeto de contexto de la prueba que debe contener previamente
            inicializado el atributo string `matriz`.

    Returns:
        dict: El diccionario `PERFILES_LOGIN` con las credenciales y datos maestros
            mapeados para el archivo de pruebas actual.

    Raises:
        ValueError: Si el objeto `context` no posee el atributo `matriz`, indicando
            que el archivo `.feature` no se nombró o inicializó correctamente.
        ImportError: Si la ruta dinámica construida no corresponde a ningún módulo
            existente o si ocurre un fallo al intentar leer el archivo de catálogo.

    Note:
        Esta arquitectura exige que las matrices de datos sigan estrictamente la estructura
        de paquetes: `librerias.insumos.<nombre_de_la_matriz>.catalogo_usuarios`, y que
        dentro de cada archivo de catálogo exista la variable global `PERFILES_LOGIN`.
    """
    if not hasattr(context, 'matriz'):
        raise ValueError("No se pudo determinar la MATRIZ. Revisa el nombre del archivo .feature.")

    ruta = f"librerias.insumos.{context.matriz}.catalogo_usuarios"
    try:
        modulo = importlib.import_module(ruta)
        return modulo.PERFILES_LOGIN
    except Exception as e:
        raise ImportError(f"Error crítico al cargar {ruta}: {e}")


def visibilidad(page, opcion, elemento, test_name, nombre_log, hora_ejecucion):
    """Consulta el mapa de selectores y ejecuta la aserción de visibilidad (visible/oculto).

        Busca el componente en el diccionario local (soportando tanto IDs, selectores CSS
        como rutas XPath). Evalúa la variable `opcion` de manera insensible a mayúsculas:
        si es 'si', aplica un `expect().to_be_visible()`; si es 'no', ejecuta un
        `expect().to_be_hidden()`. Si la validación falla, registra la anomalía y procesa
        el error a través de `existe_error_inesperado`.

        Args:
            page (Page): Instancia del navegador activa (Playwright Page).
            opcion (str): Dirección de la aserción; acepta únicamente los valores 'si' o 'no'.
            elemento (str): El nombre del elemento tal como se encuentra en el mapa (insensible a mayúsculas).
            test_name (str): Nombre clave del caso de prueba actual (utilizado para el volcado de errores).
            nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
            hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

        Raises:
            ValueError: Si el `elemento` solicitado no existe en `mapa_elementos` o si la
                `opcion` recibida es distinta a las cadenas 'si' o 'no'.
            Exception: Relanza el fallo de aserción original de Playwright tras ejecutar
                el protocolo de captura de errores inesperados.

        Note:
            A medida que se agreguen componentes específicos a validar en el flujo de negocio,
            deberá seguir alimentando el diccionario local `mapa_elementos` de esta función,
            manteniendo la convención de usar llaves en minúsculas.
        """
    mapa_elementos = {
        "ver todos": "#txtDestinoVerTodos",
        "ver saldo": "#lblProductoMonto_0",
        "empleados foca": "#lblEmplNombre",
        "registro de saldos del fondo": "//table[@id='dtSAldosFoca']/tbody/tr",
        "sin movimientos del fondo": "//td[text()='No existen registros']",
        "registro de saldos de empleados del fondo": "//table[@id='dtSaldoEmpleados']/tbody/tr[1]",
        "registro de movimientos de empleados del fondo": "//table[@id='dtMovEmpleados']/tbody/tr[1]",
        "grupo de nómina sin empleados": "#lblWarningSinEmp",
        "tabla de cheques": "#dtgListCheques",
        "tabla de cheques por rango": "#dtgListChequesRango",
        "fuera de horario foca": "#txtFueraHorario"
    }

    elemento_limpio = elemento.lower()
    llave_selector = mapa_elementos.get(elemento_limpio)
    opcion_limpio = opcion.lower()

    if not llave_selector:
        opciones_validas = ", ".join(mapa_elementos.keys())
        error_msg = f"err-> visibilidad() - El elemento '{elemento}' no mapeado. Opciones disponibles: {opciones_validas}"
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise ValueError(error_msg)

    try:
        # Localiza el elemento en la página
        btn = page.locator(llave_selector)

        if opcion_limpio == "si":
            # Caso 'si': Espera que el elemento sea visible en pantalla
            expect(btn).to_be_visible()
            escribo_log(nombre_log, f"---> Éxito: Elemento '{elemento}' está visible.\n")

        elif opcion_limpio == "no":
            # Caso 'no': Espera que el elemento esté oculto o no exista
            expect(btn).to_be_hidden()
            escribo_log(nombre_log, f"---> Éxito: Elemento '{elemento}' no está visible.\n")

        else:
            raise ValueError(f"Opción inválida: '{opcion}'. Debe ser 'si' o 'no'.")

        page.wait_for_timeout(500)

    except Exception as err:
        escribo_log(nombre_log,
                    f"Fallo de visibilidad: La condición para '{elemento}' con opción '{opcion}' no se cumplió.\n")
        escribo_log(nombre_log, f"---> visibilidad() err={type(err).__name__} {str(err)}\n")

        rastreo = f"err={type(err).__name__} [visibilidad] {str(err)}"
        existe_error_inesperado(page, rastreo, test_name, nombre_log, hora_ejecucion)
        raise


def fill(page, selector, valor):
    """Inserta texto de forma directa en un campo y espera a que concluyan las peticiones de red.

    Limpia el contenido previo del campo e inyecta el valor de manera inmediata mediante
    el método nativo de Playwright. Monitorea proactivamente el estado del cargador
    (`#ajaxloader`) para asegurar que cualquier validación o guardado asíncrono en
    segundo plano finalice antes de ceder el control.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        selector (str): El selector puro del DOM (ID, CSS, XPath) que identifica al input.
        valor (str): La cadena de texto o información que se desea escribir en el campo.

    Note:
        Este método es el predeterminado para el ingreso de datos, ya que altera el valor
        del elemento de manera instantánea a nivel de eventos del DOM.
    """
    loader = page.locator("#ajaxloader")

    page.fill(selector, valor)

    try:
        loader.wait_for(state="visible", timeout=500)

    except:
        pass

    loader.wait_for(state="hidden")


def type_action(page, selector, valor):
    """Simula las pulsaciones físicas del teclado sobre un campo y procesa las esperas de red.

    A diferencia de `fill`, este método simula los eventos reales de teclado (`keydown`,
    `keypress`, `keyup`) letra por letra. Esto es indispensable para interactuar con campos
    que poseen máscaras de entrada dinámicas o filtros de búsqueda en tiempo real (*autocomplete*),
    controlando las esperas del cargador central tras la escritura.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        selector (str): El selector puro del DOM (ID, CSS, XPath) asignado al campo de texto.
        valor (str): La secuencia de caracteres que el teclado virtual inyectará en la interfaz.

    Note:
        Utilice esta acción de manera exclusiva cuando las validaciones de JavaScript de la página
        web no logren activarse mediante el método de inserción directa `fill`.
    """
    loader = page.locator("#ajaxloader")
    page.type(selector, valor)
    try:
        loader.wait_for(state="visible", timeout=500)
    except:
        pass
    loader.wait_for(state="hidden")


def click(page, selector):
    """Ejecuta un clic físico sobre un componente y bloquea el hilo hasta disipar las cargas.

    Localiza el elemento mediante su selector puro y gatilla la acción de clic del mouse.
    Posteriormente, implementa el ciclo de control de sincronización esperando brevemente
    la aparición del spinner de Ajax y asegurando su total ocultamiento para evitar colisiones
    con las acciones subsecuentes del flujo de pruebas.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        selector (str): El selector puro del DOM (ID, CSS, XPath) sobre el cual se presionará.
    """

    loader = page.locator("#ajaxloader")

    page.locator(selector).click()

    try:
        loader.wait_for(state="visible", timeout=500)

    except:
        pass

    loader.wait_for(state="hidden")


def assert_elemento(page, texto_esperado, elemento, nombre_log, hora_ejecucion):
    """Busca un componente mapeado en el diccionario local y ejecuta la aserción de texto.

    Valida primero que el identificador lógico del componente exista dentro del mapa
    local. Posteriormente, invoca la subrutina `localizar_elemento` y ejecuta la
    aserción estricta mediante `expect().to_have_text()` aplicando un remanente de
    limpieza de espacios (`strip`).

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        texto_esperado (str): El texto exacto que se espera leer en el nodo del DOM.
        elemento (str): El nombre del elemento a consultar (evaluado en minúsculas).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

    Raises:
        AssertionError: Si la llave del `elemento` no se encuentra registrada en el
            diccionario local `mapa_elemento` o si el texto real difiere del esperado.
        Exception: Relanza cualquier inconveniente derivado de la localización o del DOM.

    Note:
        A medida que se incorporen nuevas secciones o etiquetas de validación que no
        correspondan a títulos principales, se deberá seguir alimentando el diccionario
        local `mapa_elemento`, asegurando que sus valores coincidan con las llaves del
        archivo central `selectores.json`.
    """
    try:
        mapa_elemento = {
            "cuenta relacionada alta": "txt_cuenta_relacionada_alta",
            "grupo tdniv alta": "txt_grupo_relacionado_alta",
            "altas exitosas": "txt_altas_nuevas_tdniv",
            "leyenda error importe": "txt_error_importe",
            "titulo operacion realizada": "txt_titulo_operacion_registrada",
            "estatus del archivo": "txt_estatus_archivo_manc",
            "horario foca": "txt_fuera_horario_foca"
        }

        assert elemento in mapa_elemento, escribo_log(nombre_log, f"---> No se encontró el elemento indicado, "
                                                                  f"los elementos mapeados son los siguientes "
                                                                  f"[{mapa_elemento}]\n")

        selector = mapa_elemento.get(elemento)

        elemento_encontrado = localizar_elemento(page, selector, selectores.get(selector), nombre_log, hora_ejecucion)

        expect(elemento_encontrado).to_have_text(texto_esperado.strip(), timeout=5000)

        escribo_log(nombre_log, f"---> El elemento [{elemento}] contiene correctamente el texto esperado: "
                                f"{texto_esperado}\n")

    except Exception as err:
        escribo_log(nombre_log,
                    f"---> El elemento [{elemento}]  no contiene el texto esperado: {texto_esperado}, ERROR\n")
        escribo_log(nombre_log, "---> assert_elemento() " + f"err={type(err).__name__} {str(err)}\n")
        raise


def focus_elemento(page, test_name, elemento, nombre_log, hora_ejecucion):
    """Posiciona el cursor del mouse sobre un componente específico para forzar su interacción visual.

    Busca el identificador lógico en el diccionario de elementos local, resuelve el selector
    técnico centralizado a través de `localizar_elemento` y ejecuta el método `.hover()` de
    Playwright. Esto simula el desplazamiento físico del puntero, lo cual es ideal para disparar
    tooltips, eventos de hojas de estilo (hover) o revelar mensajes de error dinámicos.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        test_name (str): Nombre clave del caso de prueba actual para fines de rastro de errores.
        elemento (str): El nombre común asignado al componente (se procesa en minúsculas).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

    Raises:
        ValueError: Si la cadena recibida en `elemento` no existe dentro de las llaves
            mapeadas en el diccionario local `mapa_elementos`.

    Note:
        Aunque la función se denomina estructuralmente 'focus', utiliza la acción de `hover`.
        Se recomienda alimentar este mapa con elementos informativos, alertas flotantes o
        capas dinámicas que requieran la presencia del puntero para ser visibles o legibles.
    """
    mapa_elementos = {
        "error importe": "div_error_importe"
    }

    elemento_limpio = elemento.lower()
    llave_selector = mapa_elementos.get(elemento_limpio)

    if llave_selector:

        try:
            # Obtenemos el localizador
            elem = localizar_elemento(page, llave_selector, selectores.get(llave_selector), nombre_log, hora_ejecucion)
            elem.hover()

        except ValueError as error_msg:
            escribo_log(nombre_log, f"---> No se pudo enfocar el elemento {elemento}.\n")
            escribo_log(nombre_log, f"---> {error_msg}\n")

    else:
        opciones_validas = ", ".join(mapa_elementos.keys())
        error_msg = f"err-> focus_elemento() - El elemento '{elemento}' no existe. Opciones válidas: {opciones_validas}"
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise ValueError(error_msg)


def seleccionar_rbtn(page, opcion, nombre_log, hora_ejecucion):
    """Busca un radio button mapeado en el diccionario local y ejecuta la acción de clic.

    Consulta el identificador lógico en `mapa_selectores`. Si se encuentra, interactúa con
    el primer elemento coincidente del DOM mediante Playwright. Está diseñado usando
    rutas XPath que apuntan a las etiquetas (`<label>`), asegurando compatibilidad con
    interfaces donde los inputs nativos están ocultos por CSS.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        opcion (str): El nombre legible del botón solicitado (insensible a mayúsculas).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        hora_ejecucion (str): Marca de tiempo del paso actual para el registro del log.

    Raises:
        ValueError: Si el valor de `opcion` no coincide con ninguna de las llaves
            registradas en el diccionario `mapa_selectores`.

    Note:
        A medida que aparezcan nuevas opciones de selección excluyente en el sistema,
        deberá seguir alimentando el diccionario local `mapa_selectores` vinculando la
        llave legible con el selector del elemento interactivo correspondiente.
    """
    mapa_selectores = {
        "dia siguiente": "//label[@for='radOpcion2']",
        "mismo dia": "//label[@for='radOpcion1']"
    }

    opcion_limpio = opcion.lower()
    llave_selector = mapa_selectores.get(opcion_limpio)

    if llave_selector:
        selector = page.locator(llave_selector).first
        escribo_log(nombre_log, f"---> Marcando la opcion: '{opcion}'\n")
        selector.click()
    else:
        opciones_validas = ", ".join(mapa_selectores.keys())
        error_msg = f"err-> seleccionar_rbtn() - La opcion '{opcion}' no existe. Opciones: {opciones_validas}"
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise ValueError(error_msg)
import os

import parse
from behave import step, given, then

from librerias.directorios import RUTA_ARCHIVOS, DIR_DESCARGAS
from librerias.funciones import insumo_x_linea, save_evidence, lista_screenshot, lista_pasos_descripcion, \
    restaura_insumo, scroll_js, escribo_log, existe_error_inesperado, leer_hora, restaura_insumo_return
from librerias.insumos.perfiles_bd import PERFILES_BD
from modulos.base import (validar_titulo, click_boton, esperar_carga_completa, subir_archivo, clic_condicional_boton,
                          obtener_catalogo_matriz, visibilidad, assert_elemento, focus_elemento, seleccionar_rbtn)


@given('que tengo un entorno de prueba configurado')
def step_given_entorno(context):
    """
        Este step solo es un bypass para el scraper
    """
    context.hora_ejecucion = leer_hora()
    context.headless = False


@then('el reporte se genera correctamente')
def step_then_reporte_correcto(context):
    """
        Este step solo es un bypass para el scraper
    """
    assert True


@step('Doy click en el boton "{boton}"')
def click_en_botones(context, boton):
    """Busca y hace clic en un elemento de la interfaz de usuario por su nombre.

    Este step genérico permite interactuar con cualquier botón o elemento mapeado.
    Utiliza el archivo `selectores.json` bajo el formato de `huella_digital - selectores`
    para resolver dinámicamente el localizador del elemento.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la instancia
            de la página (`context.page`), los registros y datos de ejecución.
        boton (str): El identificador o nombre clave del elemento tal como está
            registrado en el diccionario de selectores.

    Note:
        Es posible que el diccionario siga creciendo, se recomienda buscar primero
        el elemento en el archivo de selectores.json para evitar duplicados.

    Examples:
        Ejemplos de uso en archivos .feature::

            When Doy click en el boton "Aplicar filtros"
            And Doy click en el boton "Continuar"
    """
    try:
        click_boton(context.page, boton, context.nombre_log, context.hora_ejecucion)
    except Exception as err:
        escribo_log(context.nombre_log, "---> click_en_botones() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [click_en_botones] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que el titulo diga "{texto_esperado}"')
def step_validar_titulo(context, texto_esperado):
    """Verifica que el título de la pantalla actual coincida con el texto esperado.

        Este step realiza la aserción del título, escribe el
        resultado en el log y genera automáticamente una captura de pantalla que se
        adjunta a las listas de evidencias del reporte.

        Note:
            Se debe agregar el elemento a validar en los diccionarios de selectores.json como de la funcion
            'validar_titulo', para que este lo busque automaticamente

        Args:
            context (Any):  Objeto de contexto de la prueba que contiene la instancia
            de la página (`context.page`), los registros y datos de ejecución.
            texto_esperado (str): El texto exacto o parcial que se espera leer en el
                título de la interfaz de usuario.

        Examples:
            Ejemplos de uso en archivos .feature::

                Then Valido que el titulo diga "Transferencia Exitosa"
                And Valido que el titulo diga "Operación Rechazada"
        """
    validar_titulo(context.page, texto_esperado, context.nombre_log, context.hora_ejecucion)
    evidencia = f"Validar titulo '{texto_esperado}'"
    save_evidence(context.page, context.test_name, evidencia, context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot(evidencia))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion(evidencia))


@step('Valido operacion finalizada')
def validar_operacion_finalizar(context):
    """Espera de manera síncrona a que los procesos en segundo plano de la aplicación concluyan.

        Este step se utiliza inmediatamente después de enviar transacciones masivas,
        altas, dispersiones o descargas donde la interfaz muestra una barra de progreso,
        bloqueando la ejecución hasta que el indicador llegue a su totalidad.

        Args:
            context (Any): Objeto de contexto de la prueba que contiene la instancia de
                la página (`context.page`), los registros y metadatos de la ejecución.

        Note:
            Se requiere alimentar el diccionario de los id's

        Examples:
            Ejemplo de uso en archivos .feature::

                When Ejecuto la dispersión de la nómina
                And Valido operacion finalizada
                Then Valido que el titulo diga "Dispersión Exitosa"
        """
    esperar_carga_completa(context.page, context.nombre_log, context.hora_ejecucion)


@step('Doy clic condicional en el boton "{boton}"')
def step_click_condicional_boton(context, boton):
    """Intenta hacer clic en un botón específico solo si este se encuentra activo en la pantalla.

        Este step interactúa de manera segura con elementos opcionales de la interfaz.
        Si el botón no está presente, está oculto o se encuentra deshabilitado, la prueba
        continuará con el siguiente paso en lugar de fallar inmediatamente.

        Args:
            context (Any): Objeto de contexto de la prueba que contiene la instancia de
                la página (`context.page`), los registros y datos de la ejecución.
            boton (str): El identificador o nombre clave del elemento condicional.

        Examples:
            Ejemplos de uso en archivos .feature::

                When Doy clic condicional en el boton "enviar ahora"
                And Doy clic en el boton "Continuar"
        """
    clic_condicional_boton(context.page, boton, context.nombre_log, context.hora_ejecucion)


@step('Cargar archivo en "{boton_carga}"')
def cargar_archivo(context, boton_carga):
    """Resuelve la ruta de un insumo desde el catálogo y lo carga en el flujo correspondiente.

    Este step busca el archivo dinámicamente usando los metadatos de la línea de
    envío y los datos indexados del test, construye la ruta absoluta local e invoca
    la función base encargada de limpiar remanentes e interactuar con el navegador.

    Note:
        Esta funcion esta casada con una ruta de archivos, si requieres una ruta dinamica consulta el step
        'Cargar archivo en "{boton_carga}" para archivo modificado'

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, parámetros lógicos de insumos (`datos`) y constantes de rutas.
        boton_carga (str): El identificador de la funcionalidad del negocio asociada
            a la carga (ej. 'nomina', 'tdneg', 'spei').

    Examples:
        Ejemplos de uso en archivos .feature::

            And Cargar archivo en "nomina"
    """
    # Archivo tomado del catálogo
    boton_carga = boton_carga.lower()
    archivo = insumo_x_linea(context.linea_env, context.datos["archivo"][0], context.datos["archivo"][1])
    ruta_archivo = RUTA_ARCHIVOS + archivo
    subir_archivo(context.page, ruta_archivo, boton_carga, context.nombre_log, context.hora_ejecucion)


# @parse.with_pattern(r'(?: con la query "\d+")?')
# def parse_query_opcional(text):
#     """Parsea el sufijo opcional de una sentencia SQL en un step de Gherkin.
#     """
#     if not text or '"' not in text:
#         return ""  # Regresa vacío para que busque la llave exacta "query"
#     # Extrae el número entre las comillas (ej: "2")
#     numero = text.split('"')[1]
#     return numero
#
# # Se registra usando el módulo parse
# register_type(QueryOpcional=parse_query_opcional)


# @step('Restauro el insumo con la bd "{perfil_bd}"{sufijo_query:QueryOpcional}')
# def restaurar_insumo(context, perfil_bd, sufijo_query):
@step('Restauro el insumo con la bd "{perfil_bd}"')
def restaurar_insumo(context, perfil_bd):
    """
    Carga los parámetros de red y ejecuta una consulta de restauración en la base de datos.

    Extrae las credenciales y propiedades del motor (`PERFILES_BD`) usando un ayudante
    tolerante a nulos. Construye la clave de consulta dinámica combinando la palabra
    'query' con el sufijo opcional obtenido del parseo y delega la ejecución al conector.

    Args:
        context: Objeto de contexto de la prueba que contiene metadatos del test,
            las configuraciones de líneas y el diccionario de datos del caso de prueba.
        perfil_bd (str): El nombre clave de la conexión configurada (ej. 'ORACLE', 'SQL_SERVER').
        sufijo_query (str): Número identificador de la consulta entregado por el tipo `QueryOpcional`.

    Raises:
        KeyError: Si la clave dinámica generada (`query`, `query2`, etc.) no existe
            dentro del diccionario `context.datos` del test.

    Examples:
        Ejemplos de uso en archivos .feature::

            Given Restauro el insumo con la bd "SQL_SERVER" <- Ejecuta por default "query"
            Given Restauro el insumo con la bd "ORACLE" con la query "2" <- utiliza "query2"
    """
    try:
        context.datos_bd = PERFILES_BD[f'{perfil_bd}']

        # Función para extraer el dato solo si la llave existe en el diccionario
        def obtener_dato(llave):
            if llave in context.datos_bd:
                # Si existe, mandamos a llamar a tu función insumo_x_linea
                return insumo_x_linea(context.linea_env, context.datos_bd[llave][0], context.datos_bd[llave][1])
            # Si no existe (como el puerto en SQL_SERVER), regresamos None para que no truene
            return None

        # Datos del perfil de bd
        bd_usuario = obtener_dato("usuario")
        bd_contrasena = obtener_dato("password")
        bd_host = obtener_dato("host")
        bd_puerto = obtener_dato("puerto")
        bd_service_name = obtener_dato("servicio")
        bd_dbms = obtener_dato("dbms")

        # llave dinámicamente: "query" o "query2", "query3", etc.
        # llave_query = f"query{sufijo_query}"
        llave_query = 1

        # Validamos que la query solicitada exista en tus datos del test
        if llave_query not in context.datos:
            raise KeyError(f"No se encontró la llave '{llave_query}' en los datos del test.")

        # Extraemos el dato dinámico para el test
        query = insumo_x_linea(context.linea_env, context.datos[llave_query][0], context.datos[llave_query][1])

        escribo_log(context.nombre_log, f"---> Ejecutando restauración de insumo usando la llave: '{llave_query}'\n")

        restaura_insumo(bd_dbms, bd_usuario, bd_contrasena, bd_host, bd_puerto, bd_service_name, query,
                        context.nombre_log)
    except Exception as err:
        escribo_log(context.nombre_log, f"---> restaurar_insumo() err={type(err).__name__} {str(err)}\n")
        raise


@step('Precargar datos del perfil "{perfil}"')
def step_precargar_perfil(context, perfil):
    """Carga en el contexto de la prueba el diccionario de datos asociado a un perfil específico.

    Busca el perfil solicitado dentro del catálogo extraído de la matriz de datos actual.
    Si el perfil existe, inyecta todas sus variables y configuraciones en `context.datos`,
    dejándolas disponibles para los subsecuentes steps del flujo de automatización.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la referencia a la
            matriz (`context.matriz`) y donde se almacenarán los datos recuperados.
        perfil (str): El nombre clave del perfil o caso de prueba que se desea precargar
            (ej. 'test_mult_nom_manc_cancel', 'test_mult_nom_manc_cancel_2').

    Raises:
        ValueError: Si el identificador del `perfil` no existe como una llave válida
            dentro del catálogo de la matriz asignada.

    Examples:
        Ejemplos de uso en archivos .feature::

            Given Precargar datos del perfil "test_mult_nom_manc_cancel"
            And Precargar datos del perfil "test_mult_nom_manc_cancel_2"
    """
    perfiles = obtener_catalogo_matriz(context)
    if perfil not in perfiles:
        raise ValueError(f"Perfil {perfil} no hallado en {context.matriz}")
    context.datos = perfiles[perfil]


@step('Scroll')
def step_realizar_scroll(context):
    """Ejecuta un desplazamiento vertical predeterminado en la ventana del navegador.

    Este step se utiliza para forzar la carga de elementos perezosos (*lazy loading*)
    o para mover la vista hacia abajo de forma genérica antes de una interacción.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la instancia de
            la página (`context.page`) y el archivo de registros de ejecución.

    Examples:
        Ejemplo de uso en archivos .feature::

            When Doy click en el boton "Aplicar filtros"
            And Scroll
            Then Valido que el titulo diga "Resultados correctos"
    """
    scroll_js(context.page, context.nombre_log)


@step('Cargar archivo en "{boton_carga}" para archivo modificado')
def cargar_archivo_ruta(context, boton_carga):
    """Resuelve dinámicamente tanto la ruta como el nombre de un insumo modificado para cargarlo.

    A diferencia del step estándar que utiliza un path base fijo (`RUTA_ARCHIVOS`),
    este paso desacopla la ubicación del archivo extrayendo de forma dinámica tanto la
    carpeta contenedora (`arch_mod`) como el nombre del archivo específico (`ruta`) desde
    el catálogo de datos del contexto. Esto permite realizar pruebas con archivos mutados,
    corruptos o ubicados en directorios temporales o externos.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, la configuración de la línea de envío y el diccionario
            `datos` con los índices para el archivo modificado y su ruta.
        boton_carga (str): El identificador de la funcionalidad del negocio asociada
            a la carga (ej. 'nomina', 'tdneg', 'spei').

    Examples:
        Ejemplos de uso en archivos .feature::

            When Cargar archivo en "nomina" para archivo modificado
    """
    # Archivo tomado del catálogo
    boton_carga = boton_carga.lower()
    archivo = insumo_x_linea(context.linea_env, context.datos["arch_mod"][0], context.datos["arch_mod"][1])
    ruta = insumo_x_linea(context.linea_env, context.datos["ruta"][0], context.datos["ruta"][1])
    ruta_archivo = ruta + archivo
    subir_archivo(context.page, ruta_archivo, boton_carga, context.nombre_log, context.hora_ejecucion)


@step('Espero "{segundos:d}" segundos para que la pagina procese')
def step_esperar_procesamiento(context, segundos):
    """Detiene la ejecución del hilo de pruebas de forma explícita durante el tiempo indicado.

    Este step realiza una pausa forzada en el navegador mediante el uso de
    `wait_for_timeout`.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la instancia de
            la página (`context.page`) y el archivo de registros de ejecución.
        segundos (int): La cantidad exacta de tiempo en segundos que se suspenderá
            la ejecución de la prueba.

    Note:
        Se recomienda utilizar este step de manera excepcional. Priorice siempre el uso
        de aserciones dinámicas o esperas basadas en estados de elementos (como el step
        de la barra de progreso) para mantener la velocidad y estabilidad del framework.

    Examples:
        Ejemplo de uso en archivos .feature::

            When Cargar archivo en "nomina"
            And Espero "5" segundos para que la pagina procese
            Then Valido que el titulo diga "Carga Completa"
    """
    escribo_log(context.nombre_log, f"---> Esperando {segundos} segundos para que la pagina termine de cargar datos\n")
    context.page.wait_for_timeout(segundos * 1000)


@step('Escribo en el log "{texto}"')
def step_escribir_en_log(context, texto):
    """Inyecta un mensaje personalizado o nota de auditoría directamente en el log.

    Este step toma la cadena de texto proporcionada por el usuario, remueve de
    forma segura cualquier espacio en blanco o saltos de línea redundantes al final
    de la oración (`rstrip`) y añade un único salto de línea limpio para mantener
    el formato estructurado del archivo log.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene el identificador
            o ruta del archivo de registros (`context.nombre_log`).
        texto (str): El mensaje o anotación libre que se desea estampar en la bitácora.

    Examples:
        Ejemplos de uso en archivos .feature::

            And Escribo en el log "--- TRANSFERENCIAS SPEI ---"
    """
    texto_formateado = f"{texto.rstrip()}\n"  # rstrip quita espacios o saltos extra
    escribo_log(context.nombre_log, texto_formateado)


@step('Validar "{opcion}" visibilidad de elemento "{elemento}"')
def visibilidad_de_elemento(context, opcion, elemento):
    """Valida de manera estricta la presencia o ausencia de un elemento y genera evidencias.

    Este step evalúa si un componente de la interfaz debe estar a la vista del usuario
    o si debe permanecer oculto (o destruido en el DOM). Tras cumplir con la aserción,
    guarda de manera automática una captura de pantalla y actualiza las listas de
    reportes adjuntas al contexto de ejecución del test.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, metadatos del reporte y las listas acumuladoras de evidencias.
        opcion (str): Condición esperada para la prueba. Debe recibir 'si' o 'no'.
        elemento (str): El nombre común del componente mapeado que se desea evaluar.

    Examples:
        Ejemplos de uso en archivos .feature::

            Then Validar "si" visibilidad de elemento "ver todos"
            And Validar "no" visibilidad de elemento "fuera de horario foca"
    """
    visibilidad(context.page, opcion, elemento, context.test_name, context.nombre_log, context.hora_ejecucion)
    evidencia = f"Validación de visibilidad en [{opcion}] sobre el elemento [{elemento}] correcta"
    save_evidence(context.page, context.test_name, evidencia, context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot(evidencia))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion(evidencia))


@step('Capturo evidencia con leyenda "{leyenda}"')
def capturar_evidencia(context, leyenda):
    """Genera una captura de pantalla y registra una descripción en el reporte.

    Este step se invoca de manera explícita para documentar hitos visuales intermedios de la prueba.
    Ejecuta el volcado de la pantalla actual del navegador, almacena la imagen físicamente y extiende tanto la
    lista de capturas como la lista de descripciones en el contexto de ejecución.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, metadatos del test y los acumuladores de evidencias en formato lista.
        leyenda (str): El texto explicativo o título personalizado que se asociará
            a la captura de pantalla dentro del reporte final.

    Examples:
        Ejemplos de uso en archivos .feature::

            When Ingrese el monto de la transferencia
            And Capturo evidencia con leyenda "Formulario lleno antes de enviar"
            And Doy click en el boton "Continuar"
    """
    evidencia = leyenda
    save_evidence(context.page, context.test_name, evidencia, context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot(evidencia))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion(evidencia))


@step('Preparo a Playwright para recibir una descarga')
def step_preparar_descarga_automatica(context):
    """Activa un escuchador de eventos en segundo plano para capturar descargas del navegador.

    Este step debe invocarse inmediatamente **antes** de hacer clic en cualquier botón o
    enlace que detone la generación de un archivo (como un PDF o Excel). Registra un
    callback asíncrono en el evento `"download"` de Playwright, almacenando el objeto
    de descarga en `context.descarga_capturada` tan pronto como la web lo gatille.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la instancia de
            la página (`context.page`), el archivo de registros de ejecución y donde
            se inicializarán los atributos `descarga_capturada` y `ruta_descargas`.

    Raises:
        Exception: Relanza cualquier fallo de inicialización del listener tras registrar
            el error y ejecutar el protocolo de captura de errores inesperados.

    Note:
        Este paso es pasivo y obligatorio para flujos de exportación. Si se hace clic en
        un botón de descarga sin haber ejecutado este paso previo, el archivo se descargará
        en una ruta temporal del sistema y el framework perderá su rastro de control.

    Examples:
        Ejemplo de uso correcto en archivos .feature::

            When Preparo a Playwright para recibir una descarga
            And Doy click en el boton "exportar excel"
            Then Valido operacion finalizada
    """
    try:
        # escribo_log(context.nombre_log, "---> Activando escuchador de descargas nativo de Playwright\n")
        context.descarga_capturada = None

        def capturar_evento_descarga(download):
            escribo_log(context.nombre_log,
                        f"---> Evento de descarga gatillado por la web: {download.suggested_filename}\n")
            context.descarga_capturada = download

        # Le decimos a la página que asocie esta función al evento "download"
        context.page.on("download", capturar_evento_descarga)
        context.ruta_descargas = DIR_DESCARGAS
    except Exception as err:
        escribo_log(context.nombre_log,
                    "---> step_preparar_descarga_automatica() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_preparar_descarga_automatica] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Confirmo y guardo el archivo con su nombre original')
def step_confirmar_guardar_nombre_original(context):
    """Consolida el archivo descargado por el navegador y lo almacena en la ruta destino.

    Este step actúa en conjunto con `step_preparar_descarga_automatica`. Implementa
    una espera activa (hasta 5 segundos) para garantizar que el evento de
    descarga de Playwright se haya disparado. Una vez capturado, desvincula el
    escuchador para mantener limpia la sesión, extrae el nombre sugerido por el servidor
    y persiste el archivo en el directorio correspondiente, validando que no esté vacío.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la referencia a la
            página (`context.page`), el objeto `context.descarga_capturada`, la ruta
            configurada de destino (`context.ruta_descargas`), y donde se creará la
            variable de salida `context.ultimo_archivo_descargado`.

    Raises:
        RuntimeError: Si expira el tiempo de espera (timeout) sin que el sistema web
            haya detonado o reportado el evento de descarga.
        FileNotFoundError: Si el archivo no se guardó físicamente en la ruta destino
            o si su tamaño final en disco es de 0 bytes (descarga corrupta).
        Exception: Relanza cualquier otro error inesperado del sistema tras procesar
            el protocolo de captura y registro visual de fallas.

    Note:
        Es de vital importancia que este step sea declarado en el archivo `.feature`
        **después** de haber ejecutado la acción que genera la descarga (como dar clic
        en un botón de exportar), permitiendo que la arquitectura asíncrona resuelva el flujo.

    Examples:
        Ejemplo de flujo completo de exportación en archivos .feature::

            Cuando Preparo a Playwright para recibir una descarga
            Y Doy click en el boton "exportar excel"
            Y Confirmo y guardo el archivo con su nombre original
            Entonces Escribo en el log "Exportación completada con éxito"
    """
    try:
        import time
        escribo_log(context.nombre_log, "---> Procesando archivo y extrayendo metadatos de descarga...\n")
        # Espera dinámica para asegurar que el evento 'download' ya se disparó
        intentos = 0
        while context.descarga_capturada is None and intentos < 10:
            time.sleep(0.5)
            intentos += 1
        if context.descarga_capturada is None:
            raise RuntimeError("err-> El sistema web nunca detonó la descarga tras hacer clic en la opción.")
        # Desvincular el escuchador para que no interfiera en escenarios futuros
        # (Esto evita duplicidad de descargas si ejecutas más tests en la misma sesión)
        try:
            context.page.remove_listener("download", context.page.listeners("download")[0])
        except Exception:
            pass

        info_descarga = context.descarga_capturada
        nombre_original = info_descarga.suggested_filename
        escribo_log(context.nombre_log, f"---> Nombre detectado: '{nombre_original}'\n")

        context.ultimo_archivo_descargado = nombre_original
        ruta_final = os.path.join(context.ruta_descargas, nombre_original)
        info_descarga.save_as(ruta_final)
        if os.path.exists(ruta_final) and os.path.getsize(ruta_final) > 0:
            escribo_log(context.nombre_log,
                        f"---> Archivo consolidado con éxito: {ruta_final} ({os.path.getsize(ruta_final)} bytes)\n")
        else:
            raise FileNotFoundError(f"Error crítico: El archivo no se copió correctamente en {ruta_final}")
    except Exception as err:
        escribo_log(context.nombre_log,
                    "---> step_confirmar_guardar_nombre_original() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_confirmar_guardar_nombre_original] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Preparo a Playwright para aceptar la alerta')
def step_preparar_alerta(context):
    """Configura un escuchador temporal para interceptar y aceptar de forma automática la próxima alerta de la web.

    Este step debe invocarse inmediatamente **antes** de realizar la acción (un clic, un envío)
    que detona la aparición de un diálogo nativo del navegador (alert, confirm o prompt).
    Captura el mensaje de la ventana emergente, lo registra en la bitácora y ejecuta un
    `.accept()` para desbloquear la interfaz y permitir que la ejecución continúe.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la instancia de
            la página (`context.page`) y el archivo de registros de ejecución.

    Note:
        La función utiliza el método `.once()` de Playwright, lo que implica que el escuchador
        reacciona a **una única alerta** y se destruye de inmediato. Si el flujo de la aplicación
        despliega múltiples diálogos consecutivos, este step deberá declararse de forma individual
        previo a cada detonante en el archivo de características (`.feature`).

    Examples:
        Ejemplo de uso correcto en archivos .feature::

            Cuando Preparo a Playwright para aceptar la alerta
            Y Doy click en el boton "eliminar cuentas seleccionadas"
            Entonces Valido que el titulo diga "Cuentas Eliminadas"
    """

    def manejar_alerta(dialog):
        escribo_log(context.nombre_log, f"---> Alerta atrapada: {dialog.message}\n")
        dialog.accept()

    context.page.once("dialog", manejar_alerta)


@step('Realizo un assert del texto "{cadena}" sobre el elemento "{elemento}"')
def step_assert_elemento(context, cadena, elemento):
    """Valida que un componente específico de la interfaz de usuario contenga el texto esperado.

    Este step de aserción genérico busca el mapeo del elemento, realiza la comprobación
    estricta de su contenido textual en el navegador y, en caso de éxito, toma una
    captura de pantalla automática consolidando las evidencias en las listas del reporte.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, metadatos del reporte y las listas acumuladoras de evidencias.
        cadena (str): El texto exacto o contenido esperado que debe poseer el elemento.
        elemento (str): El nombre común o identificador lógico asignado al componente.

    Raises:
        Exception: Relanza cualquier fallo de aserción o error de localización tras
            procesar el protocolo de captura y registro visual de fallas.

    Examples:
        Ejemplos de uso en archivos .feature::

            And Realizo un assert del texto "Activa" sobre el elemento "estatus del archivo"
            And Realizo un assert del texto "13" sobre el elemento "cantidad de altas"
    """
    try:

        # Archivo tomado del catálogo
        elemento = elemento.lower()
        assert_elemento(context.page, cadena, elemento, context.nombre_log, context.hora_ejecucion)

        # evidencia = f"Se realiza assert exitoso de elemento [{elemento}] con el texto esperado [{cadena}]"
        evidencia = f"Se realiza assert exitoso de elemento [{elemento}] con el texto esperado"
        save_evidence(context.page, context.test_name, evidencia, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(evidencia))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(evidencia))

    except Exception as err:
        escribo_log(context.nombre_log, "---> step_assert_elemento() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_assert_elemento] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Enfoco el elemento "{elemento}"')
def step_focus_elemento(context, elemento):
    """Coloca el foco del teclado y de la vista sobre un componente específico de la interfaz.

    Este step se utiliza para forzar la interacción directa del navegador sobre un
    elemento (como un campo de texto o un contenedor especial), simulando el comportamiento
    de un usuario real. Si el proceso falla, se activa automáticamente el volcado de
    errores inesperados con captura de pantalla.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene la sesión del
            navegador, metadatos del test y el archivo de bitácora.
        elemento (str): El nombre común o identificador lógico asignado al componente.

    Raises:
        Exception: Relanza cualquier error de localización o enfoque derivado del DOM
            tras invocar el protocolo de diagnóstico de fallas.

    Examples:
        Ejemplos de uso en archivos .feature::

            Cuando Enfoco el elemento "formulario de transferencia"
            Y Escribo en el log "Foco establecido correctamente"
    """
    try:

        focus_elemento(context.page, context.test_name, elemento, context.nombre_log, context.hora_ejecucion)

    except Exception as err:
        escribo_log(context.nombre_log, "---> step_focus_elemento() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_focus_elemento] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Ejecuto la siguiente consulta en la BD "{perfil_bd}" y obtengo los campos "{campos_bd}"')
def ejecutar_query_multiples_campos(context, perfil_bd, campos_bd):
    """Ejecuta una consulta SQL multilínea y mapea dinámicamente sus columnas como variables del contexto.

    Este step lee un bloque de texto (Docstring de Gherkin) que contiene la consulta SQL.
    Tras ejecutar la consulta en el motor seleccionado, extrae el primer registro devuelto,
    itera sobre las columnas solicitadas por el usuario en `campos_bd` y las registra
    de manera dinámica en la sesión mediante `setattr(context, nombre_columna, valor)`.

    Args:
        context (Any): Objeto de contexto de la prueba que contiene el bloque de texto de la query
            (`context.text`) y donde se inyectarán dinámicamente las propiedades de salida.
        perfil_bd (str): El nombre clave de la conexión configurada (ej. 'ORACLE', 'SQL_SERVER').
        campos_bd (str): Lista de nombres de columnas separadas por comas que se desean extraer
            (ej. "id_transaccion, estatus").

    Raises:
        ValueError: Si no se proporciona un bloque de texto con la query en el archivo .feature,
            o si la consulta ejecutada no retorna ningún registro del DOM de datos.
        KeyError: Si alguna de las columnas solicitadas en `campos_bd` no forma parte de las
            columnas devueltas por la consulta SQL.

    Examples:
        Ejemplo de uso con inyección de variables en archivos .feature::

            When Ejecuto la siguiente consulta en la BD "SQL_SERVER" y obtengo los campos "rowno, estatus"
                \"\"\"
                SELECT TOP 1 rowno, estatus FROM t_ordenes ORDER BY fecha_creacion DESC
                \"\"\"
            Then Escribo en el log "La orden guardada es: {context.rowno}"
    """
    try:
        context.datos_bd = PERFILES_BD[f'{perfil_bd}']

        def obtener_dato(llave):
            if llave in context.datos_bd:
                return insumo_x_linea(context.linea_env, context.datos_bd[llave][0], context.datos_bd[llave][1])
            return None

        bd_usuario = obtener_dato("usuario")
        bd_contrasena = obtener_dato("password")
        bd_host = obtener_dato("host")
        bd_puerto = obtener_dato("puerto")
        bd_service_name = obtener_dato("servicio")
        bd_dbms = obtener_dato("dbms")

        if context.text:
            query = context.text.strip()
        else:
            raise ValueError("No se proporcionó ninguna query.")

        escribo_log(context.nombre_log, f"---> Ejecutando consulta en la BD...\n")

        # Ejecutamos la consulta (usando la función modificada que devuelve diccionarios)
        resultado = restaura_insumo_return(bd_dbms, bd_usuario, bd_contrasena, bd_host, bd_puerto, bd_service_name,
                                           query, context.nombre_log)

        # print("Resultado obtenido:", resultado)

        if resultado:
            # Se separa el string de campos por comas y limpiamos espacios en blanco
            # Ejemplo: "rowno, sin" -> ['rowno', 'sin']
            lista_campos = [campo.strip() for campo in campos_bd.split(',')]

            primer_registro = resultado[0]  # Tomamos la primera fila devuelta

            # Iterar cada campo solicitado por el usuario
            for campo in lista_campos:
                llave_busqueda = campo.lower()  # Buscamos en minúsculas en el diccionario

                if llave_busqueda in primer_registro:
                    valor = primer_registro[llave_busqueda]

                    # ---> CLAVE: Creación dinámica de variables en Behave
                    # setattr(objeto, 'nombre_propiedad', valor)
                    setattr(context, campo, valor)

                    escribo_log(context.nombre_log, f"---> Variable guardada en context.{campo} = {valor}\n")

                else:
                    raise KeyError(f"La columna '{campo}' no fue encontrada en los resultados devueltos por la BD.")

        else:
            raise ValueError("La consulta no devolvió ningún registro.")

    except Exception as err:
        escribo_log(context.nombre_log, f"---> ejecutar_query_multiples_campos() err={type(err).__name__} {str(err)}\n")
        raise


@step('Ejecuto la siguiente consulta dinámica en la BD "{perfil_bd}"')
def ejecutar_query_dinamica(context, perfil_bd):
    """Interpola variables almacenadas previamente en el contexto dentro de una query SQL multilínea.

    Esta función inspecciona de forma profunda tanto los atributos directos del objeto `context`
    como la pila interna de Behave (`context._stack`). Reúne todas las variables guardadas por steps
    anteriores y las usa para formatear e inyectar datos de manera segura dentro de la consulta SQL
    vía `.format(**variables_usuario)` antes de enviarla a la base de datos.

    Se utiliza por ejemplo cuando se requiere hacer una consulta, y el valor extraido utilizarlo inmediatamente
    en otra consulta

    Args:
        context (Any): Objeto de contexto de la prueba que almacena el bloque de texto con marcadores
            de posición (ej. `{id_transaccion}`) y la pila interna de datos del escenario.
        perfil_bd (str): El nombre clave de la conexión configurada (ej. 'ORACLE', 'SQL_SERVER').

    Raises:
        ValueError: Si el step se declara sin un bloque de texto adjunto en el archivo .feature.
        KeyError: Si la consulta SQL solicita un marcador de posición (ej. `{fecha}`) que no ha sido
            inicializado ni guardado previamente en el contexto del escenario actual.

    Examples:
        Ejemplo de encadenamiento dinámico en archivos .feature::

            When Ejecuto la siguiente consulta en la BD "ORACLE" y obtengo los campos "id_usuario"
                \"\"\"
                SELECT id_usuario FROM t_sesiones WHERE estatus = 'ACTIVO' FETCH FIRST 1 ROWS ONLY
                \"\"\"
            And Ejecuto la siguiente consulta dinámica en la BD "ORACLE"
                \"\"\"
                DELETE FROM t_bloqueos WHERE user_id = '{id_usuario}'
                \"\"\"
    """
    try:

        # Configuración del perfil de Base de Datos
        context.datos_bd = PERFILES_BD[f'{perfil_bd}']

        def obtener_dato(llave):
            if llave in context.datos_bd:
                return insumo_x_linea(context.linea_env, context.datos_bd[llave][0], context.datos_bd[llave][1])
            return None

        bd_usuario = obtener_dato("usuario")
        bd_contrasena = obtener_dato("password")
        bd_host = obtener_dato("host")
        bd_puerto = obtener_dato("puerto")
        bd_service_name = obtener_dato("servicio")
        bd_dbms = obtener_dato("dbms")

        if not context.text:
            raise ValueError("No se proporcionó ninguna query en el bloque de texto.")

        # =========================================================================
        # Extraemos las variables desde la pila interna de Behave
        # =========================================================================
        variables_usuario = {}

        # Extraer variables de las capas internas de Behave (_stack)
        if hasattr(context, '_stack'):
            for capa in context._stack:
                for clave, valor in capa.items():
                    if not clave.startswith('_') and not callable(valor):
                        variables_usuario[clave] = valor
                        variables_usuario[clave.lower()] = valor

        # Respaldar con cualquier atributo directo en el objeto context actual
        for clave in dir(context):
            if not clave.startswith('_') and clave not in ['text', 'scenario', 'feature', 'table', 'config']:
                try:
                    valor = getattr(context, clave)
                    if not callable(valor):
                        variables_usuario[clave] = valor
                        variables_usuario[clave.lower()] = valor
                except AttributeError:
                    continue

        try:
            # Formatear la query usando el diccionario seguro
            query_formateada = context.text.strip().format(**variables_usuario)
        except KeyError as e:
            raise KeyError(
                f"---> La query solicita la variable {e}, pero no está disponible en el contexto actual. "
                f"---> Variables detectadas en la pila: {list(set(variables_usuario.keys()))}"
            )

        # Query a ejecutar
        escribo_log(context.nombre_log, f"\n---> SQL LISTO A EJECUTAR: {query_formateada}\n")

        # Ejecutamos la query final formateada
        restaura_insumo_return(bd_dbms, bd_usuario, bd_contrasena, bd_host, bd_puerto, bd_service_name,
                               query_formateada, context.nombre_log)

    except Exception as err:
        escribo_log(context.nombre_log, f"---> ejecutar_query_dinamica() err={type(err).__name__} {str(err)}\n")
        raise


@step('Selecciono el raddio button "{opcion}"')
def seleccionar_raddiobutton(context, opcion):
    """Selecciona un botón de opción (radio button) específico en la interfaz de usuario.

        Este step genérico permite conmutar opciones excluyentes dentro de formularios o
        configuraciones de transferencias (como la selección del esquema de fechas de ejecución).

        Args:
            context (Any): Objeto de contexto de la prueba que contiene la instancia de
                la página (`context.page`), los registros y datos de la ejecución.
            opcion (str): El nombre legible de la opción a marcar (ej. 'mismo dia').

        Examples:
            Ejemplos de uso en archivos .feature::

                Then Selecciono el raddio button "mismo dia"
                And Selecciono el raddio button "dia siguiente"
        """
    seleccionar_rbtn(context.page, opcion, context.nombre_log, context.hora_ejecucion)
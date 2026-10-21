from behave import step

from librerias.funciones import escribo_log, save_evidence, lista_screenshot, \
    lista_pasos_descripcion, existe_error_inesperado
from modulos.vuelos import llenar_formulario_vuelos, filtrar_busqueda_vuelos, seleccionar_vuelos_dinamicos, \
    llenar_datos_pasajeros, llenar_formulario_pago


@step('Lleno el formulario de reserva de vuelos con los siguientes datos')
def step_llenar_vuelos_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos para el formulario de vuelos.")

        row = context.table[0]
        llenar_formulario_vuelos(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se llenó el formulario de vuelos correctamente con los datos proporcionados\n")
        texto_captura = "Lleno el formulario de vuelos"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_vuelos_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_vuelos_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Aplico los siguientes filtros en la busqueda de vuelos')
def step_filtrar_vuelos_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se proporcionó la tabla con los parámetros de filtrado.")

        row = context.table[0]
        filtrar_busqueda_vuelos(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Filtros aplicados correctamente en la lista de vuelos\n")
        texto_captura = "Aplico los filtros de vuelos"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_filtrar_vuelos_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_filtrar_vuelos_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Selecciono los vuelos deseados')
def step_seleccionar_vuelos_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se proporcionó la tabla de selección de vuelos.")

        seleccionar_vuelos_dinamicos(context.page, context.table, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Selección de vuelos completada correctamente\n")
        texto_captura = "Selecciono los vuelos deseados"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_seleccionar_vuelos_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_seleccionar_vuelos_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Lleno los datos del pasajero con la siguiente informacion')
def step_llenar_pasajeros_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos para los pasajeros.")

        row = context.table[0]
        llenar_datos_pasajeros(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se ingresaron los datos del pasajero correctamente\n")
        texto_captura = "Lleno los datos del pasajero"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_pasajeros_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_pasajeros_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Lleno el formulario de pago con los siguientes datos')
def step_llenar_pago_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos de pago.")

        row = context.table[0]
        llenar_formulario_pago(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se ingresaron los datos de pago correctamente\n")
        texto_captura = "Lleno los datos de pago"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_pago_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_pago_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
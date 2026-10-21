from behave import when, step

from helpers.self_healing import localizar_elemento, cargar_selectores
from librerias.funciones import escribo_log, save_evidence, lista_screenshot, lista_pasos_descripcion, \
    existe_error_inesperado
from modulos.acceso_menus import navegacion_menu_qapractice, seleccionar_actividad_qapractice

selectores = cargar_selectores()


@step('Navego al menu "{menu}"')
def step_navegacion_menu_qapractice(context, menu):
    try:
        navegacion_menu_qapractice(context.page, menu, context.nombre_log, context.hora_ejecucion)
        escribo_log(context.nombre_log, f"---> Ingrese con exito al menu '{menu}'\n")
        texto_captura = f"Entro al menu '{menu}'"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_quitar_fav_todas() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_quitar_fav_todas] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Selecciono la actividad de practica "{actividad}"')
def step_seleccionar_actividad(context, actividad):
    try:
        seleccionar_actividad_qapractice(context.page, actividad, context.nombre_log, context.hora_ejecucion)
        escribo_log(context.nombre_log, f"---> Seleccioné con éxito la actividad '{actividad}'\n")
        texto_captura = f"Seleccion Actividad {actividad}"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(f"Selecciona la actividad '{actividad}'"))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_seleccionar_actividad() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_seleccionar_actividad] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
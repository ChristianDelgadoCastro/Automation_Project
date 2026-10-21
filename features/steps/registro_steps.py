from behave import step

from librerias.funciones import escribo_log, save_evidence, lista_screenshot, \
    lista_pasos_descripcion, existe_error_inesperado
from modulos.registro import llenar_formulario_registro


@step('Lleno el formulario de registro con los siguientes datos')
def step_llenar_formulario_bdd(context):
    try:
        # La tabla de BDD viene integrada en el objeto context
        if not context.table:
            raise ValueError("El paso requiere una tabla de datos BDD en el archivo .feature.")

        row = context.table[0]
        llenar_formulario_registro(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se llenó el formulario de registro correctamente con los datos proporcionados\n")
        texto_captura = "Llenado de formulario"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Llenado del formulario de registro exitoso"))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_formulario_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_formulario_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise

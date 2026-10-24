from behave import step,when

from librerias.funciones import insumo_x_linea, escribo_log, save_evidence, lista_screenshot, \
    lista_pasos_descripcion, existe_error_inesperado
from modulos.base import obtener_catalogo_matriz
from modulos.login import login_script_labs, logout_script_labs, login_qa_practice, logout_qa_practice, login_dojo, \
    logout_dojo
from modulos.labs import buscar_producto_ecommerce, Labs
from modulos.crudLab import CrudLab
from modulos.adminShop import AdminShop

SITIOS_CONFIG = {
    "Script Labs": {"key": "sl",
                    "func": login_script_labs},
    "QA Practice": {"key": "qapractice",
                    "func": login_qa_practice},
    "UPEX Dojo": {"key": "dojo",
                  "func": login_dojo}
}

def _ejecutar_login(context, perfil, nombre_sitio):
    try:
        if nombre_sitio not in SITIOS_CONFIG:
            raise ValueError(f"El sitio '{nombre_sitio}' no está configurado en SITIOS_CONFIG.")

        config = SITIOS_CONFIG[nombre_sitio]
        perfiles_login = obtener_catalogo_matriz(context)

        if perfil not in perfiles_login:
            raise ValueError(f"El perfil '{perfil}' no existe en la matriz {context.matriz}.")

        context.datos = perfiles_login[perfil]
        usuario_final = insumo_x_linea(context.linea_env, context.datos["usuario"][0], context.datos["usuario"][1])
        contrasena_final = insumo_x_linea(context.linea_env, context.datos["password"][0], context.datos["password"][1])

        escribo_log(context.nombre_log, f"---> Iniciando sesión para perfil [{perfil}] en [{nombre_sitio}]\n")

        # Ejecuta la función de login correspondiente
        config["func"](context.nombre_log, context.page, usuario_final, contrasena_final, context.hora_ejecucion)

        context.sesiones_activas[config["key"]] = True

        save_evidence(context.page, context.test_name, "Login_correcto", context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot("Login_correcto"))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Login correcto"))
    except Exception as err:
        escribo_log(context.nombre_log, "---> _ejecutar_login() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [_ejecutar_login] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


# SCRIPT LABS
@step('Realizar login con el perfil "{perfil}" en Script Labs')
def step_login_script_labs(context, perfil):
    _ejecutar_login(context, perfil, "Script Labs")

@step('Cierro sesion en Script Labs')
def step_cerrar_sesion_script_labs(context):
    logout_script_labs(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['sl'] = False


# QA PRACTICE
@step('Realizar login con el perfil "{perfil}" en QA Practice')
def step_login_qa_practice(context, perfil):
    _ejecutar_login(context, perfil, "QA Practice")

@step('Cierro sesion en QA Practice')
def step_cerrar_sesion_qa_practice(context):
    logout_qa_practice(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['qapractice'] = False


# UPEX DOJO
@step('Realizar login con el perfil "{perfil}" en UPEX Dojo')
def step_login_dojo(context, perfil):
    _ejecutar_login(context, perfil, "UPEX Dojo")

@step('Cierro sesion en UPEX Dojo')
def step_cerrar_sesion_dojo(context):
    logout_dojo(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['dojo'] = False

@when('Busco el producto "{producto}" en el ecommerce')
def step_buscar_producto(context, producto):
    buscar_producto_ecommerce(
        context.nombre_log, context.page, producto, context.hora_ejecucion
    )


@when('Realizo el flujo de compra del producto "{producto}" en Script Labs')
def step_flujo_compra(context, producto):
    Labs(context.page, context.nombre_log, context.hora_ejecucion).flujo_compra(producto)
    context.sesiones_activas['sl'] = True
    save_evidence(context.page, context.test_name, "Compra_finalizada", context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot("Compra_finalizada"))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Compra finalizada"))

@when('Realizo el flujo CRUD de scripts en Script Labs')
def step_flujo_crud(context):
    CrudLab(context.page, context.nombre_log, context.hora_ejecucion).flujo_crud()
    context.sesiones_activas['sl'] = True
    save_evidence(context.page, context.test_name, "CRUD_finalizado", context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot("CRUD_finalizado"))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion("CRUD finalizado"))

    @when('Realizo el flujo de compra como administrador en Script Labs')
    def step_flujo_admin(context):
        AdminShop(context.page, context.nombre_log, context.hora_ejecucion).flujo_admin()
        context.sesiones_activas['sl'] = True
        save_evidence(context.page, context.test_name, "Admin_finalizado", context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot("Admin_finalizado"))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Admin finalizado"))
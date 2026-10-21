import re
import sys

from playwright.sync_api import expect

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.directorios import URL_SCRIPT_LABS, URL_UPEX_DOJO, URL_QA_PRACTICE
from librerias.funciones import escribo_log
from modulos.base import clic_condicional_boton

sys.path.append(".")
selectores = cargar_selectores()


def _ejecutar_login_base(nombre_log, page, url, usuario, contrasena, hora_ejecucion,
                         key_usuario, key_pass, key_btn_ingresar, key_elemento_exito):
    try:
        page.goto(url)

        usuario_sel = localizar_elemento(page, key_usuario, selectores.get(key_usuario),
                                         nombre_log, hora_ejecucion, timeout=10000)
        usuario_sel.clear()
        usuario_sel.press_sequentially(usuario, delay=100)
        usuario_sel.blur()

        contrasena_sel = localizar_elemento(page, key_pass, selectores.get(key_pass),
                                            nombre_log, hora_ejecucion, timeout=10000)
        escribo_log(nombre_log, f"---> Ingresando pass [{contrasena}]...\n")
        contrasena_sel.fill(contrasena)

        escribo_log(nombre_log, "---> Presionando ingresar...\n")
        aceptar_sel = localizar_elemento(page, key_btn_ingresar, selectores.get(key_btn_ingresar),
                                         nombre_log, hora_ejecucion)
        expect(aceptar_sel).to_be_enabled(timeout=10000)
        aceptar_sel.click()

        elem_exito = localizar_elemento(page, key_elemento_exito, selectores.get(key_elemento_exito),
                                        nombre_log, hora_ejecucion, timeout=60000)
        expect(elem_exito).to_be_visible(timeout=60000)
        escribo_log(nombre_log, f"---> Login Correcto con el usuario '{usuario}'\n")

    except Exception as e:
        if "[MANTENIMIENTO]" not in str(e):
            escribo_log(nombre_log, f"[ERROR] No se pudo iniciar sesion: {e}\n")
        raise


# SCRIPT LABS
def login_script_labs(nombre_log, page, usuario, contrasena, hora_ejecucion):
    _ejecutar_login_base(
        nombre_log, page, URL_SCRIPT_LABS, usuario, contrasena, hora_ejecucion,
        key_usuario="ipt_usuario_SL",
        key_pass="ipt_contraseña_SL",
        key_btn_ingresar="btn_ingresar_SL",
        key_elemento_exito="btn_logout_SL"
    )

def logout_script_labs(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, "---> Cerrando sesión en Script Labs...\n")
    btn_logout_sl = localizar_elemento(page, "btn_logout_SL", selectores.get("btn_logout_SL"),
                                       nombre_log, hora_ejecucion, timeout=60000)
    expect(btn_logout_sl).to_be_visible(timeout=8000)
    btn_logout_sl.click()


# QA PRACTICE
def login_qa_practice(nombre_log, page, usuario, contrasena, hora_ejecucion):
    _ejecutar_login_base(
        nombre_log, page, URL_QA_PRACTICE, usuario, contrasena, hora_ejecucion,
        key_usuario="ipt_usuario_QAP",
        key_pass="ipt_contraseña_QAP",
        key_btn_ingresar="btn_ingresar_QAP",
        key_elemento_exito="titulo_bienvenida_QAP"
    )

def logout_qa_practice(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, "---> Cerrando sesión en QA Practice...\n")
    # no hay boton de logout :c



# UPEX DOJO
def login_dojo(nombre_log, page, usuario, contrasena, hora_ejecucion):
    _ejecutar_login_base(
        nombre_log, page, URL_UPEX_DOJO, usuario, contrasena, hora_ejecucion,
        key_usuario="ipt_usuario_DOJO",
        key_pass="ipt_contraseña_DOJO",
        key_btn_ingresar="btn_ingresar_DOJO",
        key_elemento_exito="titulo_bienvenida_DOJO"
    )

def logout_dojo(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, "---> Cerrando sesión en UPEX Dojo...\n")
    page.get_by_test_id("nav-desktop").get_by_test_id("user-menu-button").dblclick()
    page.get_by_test_id("nav-logout-button").click()
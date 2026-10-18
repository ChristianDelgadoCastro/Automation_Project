import re
import sys

from playwright.sync_api import expect

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.directorios import URL_SCRIPT_LABS, URL_UPEX_DOJO, URL_QA_PRACTICE
from librerias.funciones import escribo_log
from modulos.base import clic_condicional_boton

sys.path.append(".")
selectores = cargar_selectores()


def login_script_labs(nombre_log, page, usuario, contrasena, hora_ejecucion):
    try:
        URL_LOGIN = URL_SCRIPT_LABS
        page.goto(URL_LOGIN)

        usuario_sel = localizar_elemento(page, "ipt_usuario_SL", selectores.get("ipt_usuario_SL"),
                                         nombre_log, hora_ejecucion, timeout=10000)
        usuario_sel.clear()
        usuario_sel.press_sequentially(usuario, delay=100)
        usuario_sel.blur()

        contrasena_sel = localizar_elemento(page, "ipt_contraseña_SL", selectores.get("ipt_contraseña_SL"),
                                            nombre_log, hora_ejecucion, timeout=10000)
        escribo_log(nombre_log, f"---> Ingresando pass [{contrasena}]...\n")
        contrasena_sel.fill(contrasena)

        escribo_log(nombre_log, f"---> Presionando ingresar...\n")
        aceptar_sel = localizar_elemento(page, "btn_ingresar_SL", selectores.get("btn_ingresar_SL"),
                                         nombre_log, hora_ejecucion)
        expect(aceptar_sel).to_be_enabled(timeout=10000)
        aceptar_sel.click()

        btn_logout_sl = localizar_elemento(page, "btn_logout_SL", selectores.get("btn_logout_SL"),
                                            nombre_log, hora_ejecucion, timeout=60000)
        expect(btn_logout_sl).to_be_visible(timeout=60000)
        escribo_log(nombre_log, f"---> Login Correcto con el usuario '{usuario}'\n")
    except Exception as e:
        if "[MANTENIMIENTO]" not in str(e):
            escribo_log(nombre_log, f"[ERROR] No se pudo iniciar sesion: {e}\n")
        raise


def logout_script_labs(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, f"---> Cerre sesión \n")
    btn_logout_sl = localizar_elemento(page, "btn_logout_SL", selectores.get("btn_logout_SL"),
                                       nombre_log, hora_ejecucion, timeout=60000)
    expect(btn_logout_sl).to_be_visible(timeout=8000)
    btn_logout_sl.click()


def login_qa_practice(nombre_log, page, usuario, contrasena, hora_ejecucion):
    try:
        URL_LOGIN = URL_QA_PRACTICE
        page.goto(URL_LOGIN)

        usuario_sel = localizar_elemento(page, "ipt_usuario_QAP", selectores.get("ipt_usuario_QAP"),
                                         nombre_log, hora_ejecucion, timeout=10000)
        usuario_sel.clear()
        usuario_sel.press_sequentially(usuario, delay=100)
        usuario_sel.blur()

        contrasena_sel = localizar_elemento(page, "ipt_contraseña_QAP", selectores.get("ipt_contraseña_QAP"),
                                            nombre_log, hora_ejecucion, timeout=10000)
        escribo_log(nombre_log, f"---> Ingresando pass [{contrasena}]...\n")
        contrasena_sel.fill(contrasena)

        escribo_log(nombre_log, f"---> Presionando ingresar...\n")
        aceptar_sel = localizar_elemento(page, "btn_ingresar_QAP", selectores.get("btn_ingresar_QAP"),
                                         nombre_log, hora_ejecucion)
        expect(aceptar_sel).to_be_enabled(timeout=10000)
        aceptar_sel.click()

        titulo_bienvenida_QAP = localizar_elemento(page, "titulo_bienvenida_QAP", selectores.get("titulo_bienvenida_QAP"),
                                                  nombre_log, hora_ejecucion, timeout=60000)
        expect(titulo_bienvenida_QAP).to_be_visible(timeout=60000)
        escribo_log(nombre_log, f"---> Login Correcto con el usuario '{usuario}'\n")
    except Exception as e:
        if "[MANTENIMIENTO]" not in str(e):
            escribo_log(nombre_log, f"[ERROR] No se pudo iniciar sesion: {e}\n")
        raise


def logout_qa_practice(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, f"---> Cerre sesión \n")


def login_dojo(nombre_log, page, usuario, contrasena, hora_ejecucion):
    try:
        URL_LOGIN = URL_UPEX_DOJO
        page.goto(URL_LOGIN)

        usuario_sel = localizar_elemento(page, "ipt_usuario_DOJO", selectores.get("ipt_usuario_DOJO"),
                                         nombre_log, hora_ejecucion, timeout=10000)
        usuario_sel.clear()
        usuario_sel.press_sequentially(usuario, delay=100)
        usuario_sel.blur()

        contrasena_sel = localizar_elemento(page, "ipt_contraseña_DOJO", selectores.get("ipt_contraseña_DOJO"),
                                            nombre_log, hora_ejecucion, timeout=10000)
        escribo_log(nombre_log, f"---> Ingresando pass [{contrasena}]...\n")
        contrasena_sel.fill(contrasena)

        escribo_log(nombre_log, f"---> Presionando ingresar...\n")
        aceptar_sel = localizar_elemento(page, "btn_ingresar_DOJO", selectores.get("btn_ingresar_DOJO"),
                                         nombre_log, hora_ejecucion)
        expect(aceptar_sel).to_be_enabled(timeout=10000)
        aceptar_sel.click()

        logo_dojo = localizar_elemento(page, "titulo_bienvenida_DOJO", selectores.get("titulo_bienvenida_DOJO"),
                                            nombre_log, hora_ejecucion, timeout=60000)
        expect(logo_dojo).to_be_visible(timeout=60000)
        escribo_log(nombre_log, f"---> Login Correcto con el usuario '{usuario}'\n")
    except Exception as e:
        if "[MANTENIMIENTO]" not in str(e):
            escribo_log(nombre_log, f"[ERROR] No se pudo iniciar sesion: {e}\n")
        raise


def logout_dojo(page, nombre_log, hora_ejecucion):
    escribo_log(nombre_log, f"---> Cerre sesión \n")
    page.get_by_test_id("nav-desktop").get_by_test_id("user-menu-button").dblclick()
    page.get_by_test_id("nav-logout-button").click()
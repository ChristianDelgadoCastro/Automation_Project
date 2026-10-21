from playwright.sync_api import expect

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.funciones import escribo_log

selectores = cargar_selectores()


def navegacion_menu_qapractice(page, menu, nombre_log, hora_ejecucion):
    try:
        if not menu:
            raise ValueError("El parámetro 'menu' no puede estar vacío.")

        menu_limpio = menu.lower().strip()
        mapa_menus = {
            "practice sites": "btn_menu_practice_sites",
            "interview prep": "btn_menu_interview_prep",
            "about": "btn_menu_about",
            "contact": "btn_menu_contact",
        }

        elemento = mapa_menus.get(menu_limpio)
        if not elemento:
            opciones = ", ".join(mapa_menus.keys())
            raise ValueError(f"Menú no reconocido: '{menu}'. Opciones válidas: [{opciones}]")

        selector_actual = selectores.get(elemento)
        if not selector_actual:
            raise KeyError(f"No se encontraron selectores configurados para el identificador '{elemento}'.")

        elemento_menu = localizar_elemento(page, elemento, selector_actual, nombre_log, hora_ejecucion)
        if not elemento_menu:
            raise TimeoutError(f"No se pudo localizar el elemento de menú '{menu}' en la página actual.")

        elemento_menu.click(timeout=5000)
        page.wait_for_timeout(1000)

    except Exception as e:
        error_msg = f"err-> servicios() - Fallo al navegar al menu {menu}: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e

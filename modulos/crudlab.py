import time

from playwright.sync_api import expect

from librerias.funciones import escribo_log, save_evidence, lista_screenshot, lista_pasos_descripcion
from modulos.login import login_script_labs

USUARIO_LABS = "standard_user@example.com"
CONTRASENA_LABS = "script_sauce"

SECTION = "#root > div > main > section > div.script-section"
SEL_TITULO = "#title"
SEL_DESCRIPCION = "#description"
SEL_BOTON_CREAR = f"{SECTION} > div.script-form > form > button"

SEL_TAB_DASHBOARD = "#root > div > main > section > div.dashboard-tabs > button.dashboard-tab.active"
SCRIPTS = f"{SECTION} > div.scripts-container > div"
CARD = f"{SCRIPTS} > div.scripts-grid > div"
SEL_BUSCADOR = f"{SCRIPTS} > div.search-bar-container > input"
SEL_BTN_SECONDARY = f"{CARD} > div.script-actions > button.btn.secondary"
SEL_BTN_PRIMARY = f"{CARD} > div.script-actions > button.btn.primary"
SEL_BTN_DANGER = f"{CARD} > div.script-actions > button.btn.danger"
SEL_TEXTAREA = f"{CARD} > textarea"
SEL_INPUT_EDIT = f"{CARD} > input"
SEL_MODAL_DANGER = f"{SCRIPTS} > div.scripts-grid > div.modal-overlay > div > div.modal-actions > button.btn.danger"


class CrudLab:
    def __init__(self, page_or_context, nombre_log=None, hora_ejecucion=None):
        if hasattr(page_or_context, "page"):
            self.context = page_or_context
            self.page = self.context.page
            self.nombre_log = self.context.nombre_log
            self.hora_ejecucion = self.context.hora_ejecucion
        else:
            self.context = None
            self.page = page_or_context
            self.nombre_log = nombre_log
            self.hora_ejecucion = hora_ejecucion
        self.test_name = "test_crud_scriptlabs"

    def _log(self, texto):
        escribo_log(self.nombre_log, f"---> {texto}\n")

    def tomar_captura(self, leyenda):
        test_name = getattr(self.context, "test_name", self.test_name)
        save_evidence(self.page, test_name, leyenda, self.hora_ejecucion)
        if self.context and hasattr(self.context, "lista_screenshot"):
            self.context.lista_screenshot.extend(lista_screenshot(leyenda))
        if self.context and hasattr(self.context, "lista_pasos_descripcion"):
            self.context.lista_pasos_descripcion.extend(lista_pasos_descripcion(leyenda))

    def _clic(self, selector, descripcion):
        elemento = self.page.locator(selector).first
        expect(elemento).to_be_visible(timeout=10000)
        elemento.click()
        self._log(f"Clic en {descripcion}")
        self.page.wait_for_timeout(500)

    def _escribir(self, selector, texto, descripcion, delay=100):
        campo = self.page.locator(selector).first
        expect(campo).to_be_visible(timeout=10000)
        campo.click()
        campo.fill("")  # borra el texto previo
        campo.press_sequentially(texto, delay=delay)  # escribe letra por letra
        self._log(f"Se escribió '{texto}' en {descripcion}")

    def iniciar_sesion(self, usuario=USUARIO_LABS, contrasena=CONTRASENA_LABS):
        self._log(f"Iniciando sesión en Script Labs con {usuario}")
        login_script_labs(self.nombre_log, self.page, usuario, contrasena, self.hora_ejecucion)

    def abrir_tab_dashboard(self):
        tab = self.page.get_by_role("tab", name="Script CRUD")
        expect(tab).to_be_visible(timeout=10000)
        tab.click()
        self._log("Clic en la pestaña Script CRUD")
        self.page.locator(SEL_TITULO).wait_for(state="visible", timeout=10000)

    def crear_script(self, titulo="Test",
                     descripcion="Verificar que el usuario pueda iniciar sesión correctamente en la aplicación web."):
        self._escribir(SEL_TITULO, titulo, "título")
        self._escribir(SEL_DESCRIPCION, descripcion, "descripción")
        self._clic(SEL_BOTON_CREAR, "botón crear script")


    def buscar(self, texto):
        self._escribir(SEL_BUSCADOR, texto, "buscador")
        time.sleep(5)

    def editar_script(self):
        self._clic(SEL_BTN_SECONDARY, "botón secondary (1)")
        self._escribir(SEL_TEXTAREA, "Prueba 1", "textarea")
        self._clic(SEL_BTN_SECONDARY, "botón secondary (2)")
        self._clic(SEL_BTN_SECONDARY, "botón secondary (3)")
        self._escribir(SEL_INPUT_EDIT, "Test1", "input de edición")
        self._clic(SEL_BTN_PRIMARY, "botón primary (guardar)")

    def eliminar_script(self):
        self._clic(SEL_BTN_DANGER, "botón danger (eliminar)")
        self._clic(SEL_MODAL_DANGER, "botón danger del modal (confirmar)")

    def flujo_crud(self):
        try:
            self.iniciar_sesion()
            self.abrir_tab_dashboard()
            self.tomar_captura("Abrir Tab Dashboard")
            self.crear_script()
            self.tomar_captura("Crear Script")
            self.buscar("Test")
            self.tomar_captura("Buscar test")
            self.editar_script()
            self.tomar_captura("Editar script")
            self.eliminar_script()
            self.tomar_captura("Eliminar script")
            self.buscar("Test1")
            self.tomar_captura("Buscar test1")
        except Exception as e:
            self._log(f"flujo_crud() {type(e).__name__}: {e}")
            raise Exception(f"err={type(e).__name__} [flujo_crud] {e}")
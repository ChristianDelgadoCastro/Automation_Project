import time

from playwright.sync_api import expect

from librerias.funciones import escribo_log
from modulos.login import login_script_labs

USUARIO_ADMIN = "admin@example.com"
CONTRASENA_ADMIN = "admin123"

TOOLBAR = "#root > div > main > section > section > div.shop-toolbar"
LAYOUT = "#root > div > main > section > section > div.shop-layout"
ASIDE = f"{LAYOUT} > aside"

SEL_BUSCADOR = f"{TOOLBAR} > input[type=search]"
SEL_SELECT = f"{TOOLBAR} > select"
SEL_OPCION_5 = f"{TOOLBAR} > select > option:nth-child(5)"
SEL_BTN_PRODUCTO = f"{LAYOUT} > div > article > div.product-footer > button"
SEL_MAS_CANTIDAD = f"{ASIDE} > div.cart-items > div > div.quantity-controls > button:nth-child(3)"
SEL_NOMBRE = f"{ASIDE} > form > label:nth-child(2) > input"
SEL_EMAIL = f"{ASIDE} > form > label:nth-child(3) > input[type=email]"
SEL_EMPRESA = f"{ASIDE} > form > label:nth-child(4) > input"
SEL_NOTAS = f"{ASIDE} > form > label:nth-child(5) > textarea"
SEL_BTN_FORM = f"{ASIDE} > form > button"


class AdminShop:
    def __init__(self, page, nombre_log, hora_ejecucion):
        self.page = page
        self.nombre_log = nombre_log
        self.hora_ejecucion = hora_ejecucion

    def _log(self, texto):
        escribo_log(self.nombre_log, f"---> {texto}\n")

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
        campo.fill("")
        campo.press_sequentially(texto, delay=delay)
        self._log(f"Se escribió '{texto}' en {descripcion}")

    def iniciar_sesion(self, usuario=USUARIO_ADMIN, contrasena=CONTRASENA_ADMIN):
        self._log(f"Iniciando sesión en Script Labs con {usuario}")
        login_script_labs(self.nombre_log, self.page, usuario, contrasena, self.hora_ejecucion)

    def buscar_y_filtrar(self, producto="Postman"):
        self._escribir(SEL_BUSCADOR, producto, "buscador")
        select = self.page.locator(SEL_SELECT).first
        expect(select).to_be_visible(timeout=10000)
        valor = self.page.locator(SEL_OPCION_5).first.get_attribute("value")
        select.select_option(value=valor)
        self._log(f"Se seleccionó la opción 5 del filtro (value='{valor}')")
        self.page.wait_for_timeout(500)

    def agregar_al_carrito(self):
        self._clic(SEL_BTN_PRODUCTO, "botón del producto (Add to Cart)")
        self._clic(SEL_MAS_CANTIDAD, "botón aumentar cantidad")

    def llenar_formulario(self):
        self._escribir(SEL_NOMBRE, "Fabiola Torres", "nombre")
        # El email se deja vacío a propósito
        self._log("Campo email se deja vacío")
        self._escribir(SEL_EMPRESA, "Company Api", "empresa")
        self._escribir(SEL_NOTAS, "Api Automation", "notas")

    def enviar_formulario(self, descripcion):
        self._clic(SEL_BTN_FORM, descripcion)

    def flujo_admin(self):
        try:
            self.iniciar_sesion()
            self.buscar_y_filtrar("Postman")
            self.agregar_al_carrito()
            self.llenar_formulario()
            self.enviar_formulario("botón del formulario (sin email)")
            time.sleep(3)
            self._escribir(SEL_EMAIL, "ftorres", "email")
            self.enviar_formulario("botón del formulario (con email)")
        except Exception as e:
            self._log(f"flujo_admin() {type(e).__name__}: {e}")
            raise Exception(f"err={type(e).__name__} [flujo_admin] {e}")
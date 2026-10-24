import re

from playwright.sync_api import expect

from librerias.funciones import escribo_log
from modulos.login import login_script_labs

USUARIO_LABS = "standard_user@example.com"
CONTRASENA_LABS = "script_sauce"

BASE = "#root > div > main > section > section > div.shop-layout > aside"
SEL_BUSCADOR = "#root > div > main > section > section > div.shop-toolbar > input[type=search]"
SEL_MAS_CANTIDAD = f"{BASE} > div.cart-items > div > div.quantity-controls > button:nth-child(3)"
SEL_NOMBRE = f"{BASE} > form > label:nth-child(2) > input"
SEL_EMAIL = f"{BASE} > form > label:nth-child(3) > input[type=email]"
SEL_EMPRESA = f"{BASE} > form > label:nth-child(4) > input"
SEL_NOTAS = f"{BASE} > form > label:nth-child(5) > textarea"
SEL_BOTON_FORM = f"{BASE} > form > button"


class Labs:
    def __init__(self, page, nombre_log, hora_ejecucion):
        self.page = page
        self.nombre_log = nombre_log
        self.hora_ejecucion = hora_ejecucion

    def _log(self, texto):
        escribo_log(self.nombre_log, f"---> {texto}\n")

    def escribir_letra_por_letra(self, selector, texto, delay=150):
        """Escribe un texto tecla por tecla en el campo indicado."""
        campo = self.page.locator(selector)
        expect(campo).to_be_visible(timeout=10000)
        campo.click()
        campo.fill("")  # limpia el campo antes de escribir
        campo.press_sequentially(texto, delay=delay)
        self._log(f"Se escribió letra por letra '{texto}' en [{selector}]")

    def iniciar_sesion(self, usuario=USUARIO_LABS, contrasena=CONTRASENA_LABS):
        self._log(f"Iniciando sesión en Script Labs con {usuario}")
        login_script_labs(self.nombre_log, self.page, usuario, contrasena, self.hora_ejecucion)

    def buscar_producto(self, nombre_producto):
        self._log(f"Buscando producto: {nombre_producto}")
        tarjetas = self.page.locator(".product-card.ecommerce-product-card")
        tarjetas.first.wait_for(state="visible", timeout=15000)

        self.escribir_letra_por_letra(SEL_BUSCADOR, nombre_producto)
        self.page.wait_for_timeout(500)

        tarjeta = tarjetas.filter(
            has_text=re.compile(re.escape(nombre_producto), re.IGNORECASE)
        ).first
        expect(tarjeta).to_be_visible(timeout=10000)
        tarjeta.scroll_into_view_if_needed()
        self._log(f"Producto encontrado: {tarjeta.inner_text().strip().replace(chr(10), ' | ')}")
        return tarjeta

    def agregar_al_carrito(self, tarjeta):
        self._log("Presionando 'Add to Cart'")
        tarjeta.get_by_role("button", name="Add to Cart").click()
        self.page.wait_for_timeout(500)

    def aumentar_cantidad(self, veces=2):
        boton = self.page.locator(SEL_MAS_CANTIDAD)
        expect(boton).to_be_visible(timeout=10000)
        for i in range(veces):
            boton.click()
            self._log(f"Clic {i + 1} de {veces} en aumentar cantidad")
            self.page.wait_for_timeout(300)

    def llenar_checkout(self, nombre, email, empresa, notas):
        self._log("Llenando datos de checkout")
        self.escribir_letra_por_letra(SEL_NOMBRE, nombre, delay=80)
        self.escribir_letra_por_letra(SEL_EMAIL, email, delay=80)
        self.escribir_letra_por_letra(SEL_EMPRESA, empresa, delay=80)
        self.escribir_letra_por_letra(SEL_NOTAS, notas, delay=80)

    def enviar_checkout(self):
        boton = self.page.locator(SEL_BOTON_FORM)
        expect(boton).to_be_enabled(timeout=10000)
        self._log("Presionando botón de checkout")
        boton.click()
        self.page.wait_for_timeout(1000)

    def flujo_compra(self, producto="Selenium"):
        """Login -> búsqueda -> Add to Cart -> cantidad x2 -> formulario -> enviar."""
        try:
            self.iniciar_sesion()
            tarjeta = self.buscar_producto(producto)
            self.agregar_al_carrito(tarjeta)
            self.aumentar_cantidad(2)
            self.llenar_checkout(
                nombre="Luna Castillo Herrera",
                email="lunacast@gmail.com",
                empresa="LabTesting",
                notas="Pruebas",
            )
            self.enviar_checkout()
        except Exception as e:
            self._log(f"flujo_compra() {type(e).__name__}: {e}")
            raise Exception(f"err={type(e).__name__} [flujo_compra] {e}")


def buscar_producto_ecommerce(nombre_log, page, nombre_producto, hora_ejecucion):
    """Envoltorio para no romper el step existente."""
    return Labs(page, nombre_log, hora_ejecucion).buscar_producto(nombre_producto)
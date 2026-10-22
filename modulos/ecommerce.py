import re
import sys

from playwright.sync_api import expect

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.funciones import escribo_log

sys.path.append(".")
selectores = cargar_selectores()


def validar_catalogo_inicial(page, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Validando catálogo inicial\n")

        selector_actual = selectores.get("btn_ecom_cart")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'btn_ecom_cart' en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_actual, nombre_log, hora_ejecucion)

        tarjetas = page.get_by_test_id(re.compile(r"^product-card-\d+$"))
        expect(tarjetas.first).to_be_visible()
        assert tarjetas.count() > 0, "El catálogo no muestra productos."

        digitos = re.search(r"\d+", boton_carrito.inner_text())
        contador = int(digitos.group(0)) if digitos else 0
        assert contador == 0, f"El carrito debía iniciar en 0 y está en {contador}."

    except Exception as e:
        error_msg = f"err-> validar_catalogo_inicial() - Fallo al validar el catálogo: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def buscar_producto(page, termino, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Buscando el producto '{termino}'\n")

        selector_actual = selectores.get("ipt_ecom_search")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'ipt_ecom_search' en la configuración.")
        elemento = localizar_elemento(page, "ipt_ecom_search", selector_actual, nombre_log, hora_ejecucion)

        elemento.clear()
        elemento.fill(termino)

        # La lista se filtra sola: esperamos a que no quede ninguna tarjeta ajena al término
        tarjetas = page.get_by_test_id(re.compile(r"^product-card-\d+$"))
        expect(tarjetas.filter(has_not_text=re.compile(re.escape(termino), re.I))).to_have_count(0)

    except Exception as e:
        error_msg = f"err-> buscar_producto() - Fallo al buscar el producto: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def validar_resultados_busqueda(page, termino, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Validando resultados de la búsqueda\n")

        nombres = page.get_by_test_id(re.compile(r"^view-product-\d+$")).all_inner_texts()
        assert nombres, f"La búsqueda '{termino}' no devolvió resultados."
        ajenos = [n for n in nombres if termino.lower() not in n.lower()]
        assert not ajenos, f"Resultados que no corresponden a '{termino}': {ajenos}"

        selector_actual = selectores.get("txt_ecom_result_count")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'txt_ecom_result_count' en la configuración.")
        conteo = localizar_elemento(page, "txt_ecom_result_count", selector_actual, nombre_log, hora_ejecucion)
        assert str(len(nombres)) in conteo.inner_text(), \
            f"El contador dice '{conteo.inner_text()}' y hay {len(nombres)} resultados."

    except Exception as e:
        error_msg = f"err-> validar_resultados_busqueda() - Fallo al validar los resultados: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def seleccionar_producto_listado(page, posicion, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Seleccionando el producto número {posicion} del listado\n")

        tarjeta = page.get_by_test_id(re.compile(r"^product-card-\d+$")).nth(int(posicion) - 1)
        tarjeta.scroll_into_view_if_needed()

        pid = tarjeta.get_attribute("data-testid").rsplit("-", 1)[-1]
        nombre = page.get_by_test_id(f"view-product-{pid}").inner_text().strip()
        precio_txt = tarjeta.get_by_text(re.compile(r"^\$\s?\d")).inner_text()
        precio = float(re.search(r"\d+(?:\.\d+)?", precio_txt.replace(",", "")).group(0))

        escribo_log(nombre_log, f"---> Producto elegido: id={pid}, nombre='{nombre}', precio={precio}\n")
        return {"id": pid, "nombre": nombre, "precio": precio}

    except Exception as e:
        error_msg = f"err-> seleccionar_producto_listado() - Fallo al seleccionar el producto: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def abrir_detalle_producto(page, producto, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Abriendo el detalle de '{producto['nombre']}'\n")

        page.get_by_test_id(f"view-product-{producto['id']}").click()

        selector_actual = selectores.get("cnt_ecom_product_detail")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'cnt_ecom_product_detail' en la configuración.")
        localizar_elemento(page, "cnt_ecom_product_detail", selector_actual, nombre_log, hora_ejecucion)

    except Exception as e:
        error_msg = f"err-> abrir_detalle_producto() - Fallo al abrir el detalle: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def validar_detalle_producto(page, producto, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Validando el detalle del producto\n")

        selector_nombre = selectores.get("txt_ecom_detail_name")
        selector_precio = selectores.get("txt_ecom_detail_price")
        if not selector_nombre or not selector_precio:
            raise KeyError("No se encontraron los selectores del detalle del producto en la configuración.")
        nombre = localizar_elemento(page, "txt_ecom_detail_name", selector_nombre, nombre_log, hora_ejecucion)
        precio = localizar_elemento(page, "txt_ecom_detail_price", selector_precio, nombre_log, hora_ejecucion)

        assert nombre.inner_text().strip() == producto["nombre"], \
            f"Nombre en detalle '{nombre.inner_text()}' distinto al del listado '{producto['nombre']}'."
        precio_detalle = float(re.search(r"\d+(?:\.\d+)?", precio.inner_text().replace(",", "")).group(0))
        assert precio_detalle == producto["precio"], \
            f"Precio en detalle {precio_detalle} distinto al del listado {producto['precio']}."
        expect(page.get_by_test_id(f"add-to-cart-{producto['id']}")).to_be_visible()

    except Exception as e:
        error_msg = f"err-> validar_detalle_producto() - Fallo al validar el detalle: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def agregar_al_carrito(page, producto, cantidad, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Agregando desde el detalle '{producto['nombre']}' x{cantidad}\n")

        campo_cantidad = page.get_by_test_id(f"quantity-{producto['id']}")
        campo_cantidad.fill(str(cantidad))
        assert campo_cantidad.input_value() == str(cantidad), "La cantidad no quedó registrada."
        page.get_by_test_id(f"add-to-cart-{producto['id']}").click()

        selector_actual = selectores.get("btn_ecom_cart")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'btn_ecom_cart' en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_actual, nombre_log, hora_ejecucion)
        expect(boton_carrito).to_contain_text(str(cantidad))

    except Exception as e:
        error_msg = f"err-> agregar_al_carrito() - Fallo al agregar al carrito: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def agregar_desde_listado(page, producto, cantidad, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Agregando desde el listado '{producto['nombre']}' x{cantidad}\n")

        campo_cantidad = page.get_by_test_id(f"quantity-{producto['id']}")
        campo_cantidad.scroll_into_view_if_needed()
        campo_cantidad.fill(str(cantidad))
        assert campo_cantidad.input_value() == str(cantidad), "La cantidad no quedó registrada en la tarjeta."
        page.get_by_test_id(f"add-to-cart-{producto['id']}").click()

        selector_actual = selectores.get("btn_ecom_cart")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'btn_ecom_cart' en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_actual, nombre_log, hora_ejecucion)
        expect(boton_carrito).to_contain_text(str(cantidad))

    except Exception as e:
        error_msg = f"err-> agregar_desde_listado() - Fallo al agregar desde el listado: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e

    
def validar_carrito(page, producto, cantidad, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Validando en el carrito: '{producto['nombre']}' x{cantidad}\n")

        selector_comprar = selectores.get("btn_ecom_proceed_to_buy")
        if not selector_comprar:
            raise KeyError("No se encontró el selector 'btn_ecom_proceed_to_buy' en la configuración.")
        localizar_elemento(page, "btn_ecom_proceed_to_buy", selector_comprar, nombre_log, hora_ejecucion)
        expect(page.get_by_test_id(f"remove-from-cart-{producto['id']}")).to_be_visible()

        texto = page.get_by_role("dialog").inner_text()

        linea = re.search(r"(.+?)\s*-\s*\$\s?(\d+(?:\.\d+)?)\s*x\s*(\d+)", texto)
        assert linea, f"El carrito no muestra una línea 'producto - $precio x cantidad'. Texto: {texto!r}"
        assert linea.group(1).strip() == producto["nombre"], \
            f"Producto en el carrito '{linea.group(1).strip()}' distinto a '{producto['nombre']}'."
        assert float(linea.group(2)) == producto["precio"], \
            f"Precio en el carrito {linea.group(2)} distinto al del listado {producto['precio']}."
        assert int(linea.group(3)) == int(cantidad), \
            f"Cantidad en el carrito {linea.group(3)} distinta a {cantidad}."

        total = re.search(r"Total:\s*\$\s?(\d+(?:\.\d+)?)", texto)
        assert total, f"El carrito no muestra el total. Texto: {texto!r}"
        esperado = round(producto["precio"] * int(cantidad), 2)
        assert float(total.group(1)) == esperado, \
            f"Total en el carrito {total.group(1)} distinto a {esperado} ({producto['precio']} x {cantidad})."

        selector_carrito = selectores.get("btn_ecom_cart")
        selector_comprar = selectores.get("btn_ecom_proceed_to_buy")
        if not selector_carrito or not selector_comprar:
            raise KeyError("No se encontraron los selectores del carrito en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_carrito, nombre_log, hora_ejecucion)
        digitos = re.search(r"\d+", boton_carrito.inner_text())
        assert digitos and int(digitos.group(0)) == int(cantidad), \
            f"Contador del carrito distinto de {cantidad}: '{boton_carrito.inner_text()}'."
        boton_comprar = localizar_elemento(page, "btn_ecom_proceed_to_buy", selector_comprar, nombre_log, hora_ejecucion)
        expect(boton_comprar).to_be_enabled()

    except Exception as e:
        error_msg = f"err-> validar_carrito() - Fallo al validar el carrito: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def llenar_direccion_envio(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "nombre": "ipt_ecom_addr_name",
            "calle": "ipt_ecom_addr_street",
            "ciudad": "ipt_ecom_addr_city",
            "estado": "ipt_ecom_addr_state",
            "zip": "ipt_ecom_addr_zip"
        }

        escribo_log(nombre_log, "---> Llenando la dirección de envío\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo [{campo}]\n")
                    continue

                escribo_log(nombre_log, f"---> Ingresando en [{campo}]: '{valor}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)
                elemento.scroll_into_view_if_needed()
                elemento.clear()
                # [borrar] solo limpia el campo (para probar "campo faltante" sobre datos ya escritos)
                if valor.lower() != "[borrar]":
                    elemento.fill(valor)
            else:
                escribo_log(nombre_log, f"---> El campo [{campo}] no se especificó o viene vacío. Se omite.\n")

    except Exception as e:
        error_msg = f"err-> llenar_direccion_envio() - Fallo al ingresar la dirección: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def llenar_pago_ecommerce(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "numero_tarjeta": "ipt_ecom_card_number",
            "expiracion": "ipt_ecom_card_expiry",
            "cvv": "ipt_ecom_card_cvv"
        }

        escribo_log(nombre_log, "---> Llenando información del método de pago...\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo [{campo}]\n")
                    continue

                # Mascaramos el log si es CVV por privacidad en evidencias
                valor_log = "*****" if campo == "cvv" else valor
                escribo_log(nombre_log, f"---> Ingresando en [{campo}]: '{valor_log}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)
                elemento.scroll_into_view_if_needed()
                elemento.clear()
                if valor.lower() != "[borrar]":
                    elemento.fill(valor)
            else:
                escribo_log(nombre_log, f"---> El campo [{campo}] no se especificó o viene vacío. Se omite.\n")

    except Exception as e:
        error_msg = f"err-> llenar_pago_ecommerce() - Fallo al ingresar datos de pago: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def validar_sin_avanzar_a_pago(page, alertas, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Validando que no se avance a la pantalla de pago\n")

        selector_actual = selectores.get("ipt_ecom_addr_name")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'ipt_ecom_addr_name' en la configuración.")
        campo_nombre = localizar_elemento(page, "ipt_ecom_addr_name", selector_actual, nombre_log, hora_ejecucion)
        expect(campo_nombre).to_be_visible()
        expect(page.get_by_test_id("ecom-card-number")).to_have_count(0)

        assert alertas, "No apareció ninguna alerta de campos faltantes."
        assert alertas[-1] == "Please fill in all address fields.", \
            f"La alerta dice '{alertas[-1]}' y se esperaba 'Please fill in all address fields.'."

    except Exception as e:
        error_msg = f"err-> validar_sin_avanzar_a_pago() - Fallo al validar que no avanza: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def validar_direccion_conservada(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "nombre": "ipt_ecom_addr_name",
            "calle": "ipt_ecom_addr_street",
            "ciudad": "ipt_ecom_addr_city",
            "estado": "ipt_ecom_addr_state",
            "zip": "ipt_ecom_addr_zip"
        }

        escribo_log(nombre_log, "---> Validando que los datos de la dirección se conserven\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()
                if valor.lower() in ["[vacío]", "[omitir]", "none", "[borrar]"]:
                    continue

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)
                assert elemento.input_value() == valor, \
                    f"[{campo}] se perdió: esperado '{valor}', actual '{elemento.input_value()}'."

    except Exception as e:
        error_msg = f"err-> validar_direccion_conservada() - Fallo al validar los datos: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e

def agregar_producto_acumulado(page, producto, cantidad, en_carrito, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Sumando al carrito '{producto['nombre']}' x{cantidad}\n")
 
        campo_cantidad = page.get_by_test_id(f"quantity-{producto['id']}")
        campo_cantidad.scroll_into_view_if_needed()
        campo_cantidad.fill(str(cantidad))
        assert campo_cantidad.input_value() == str(cantidad), "La cantidad no quedó registrada en la tarjeta."
        page.get_by_test_id(f"add-to-cart-{producto['id']}").click()
 
        selector_actual = selectores.get("btn_ecom_cart")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'btn_ecom_cart' en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_actual, nombre_log, hora_ejecucion)
 
        # El contador del carrito debe ser la suma de lo que ya había más lo recién agregado
        esperado = sum(item["cantidad"] for item in en_carrito) + int(cantidad)
        expect(boton_carrito).to_have_text(re.compile(rf"^\s*{esperado}\s*$"))
 
    except Exception as e:
        error_msg = f"err-> agregar_producto_acumulado() - Fallo al sumar el producto al carrito: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
 
 
def validar_carrito_acumulado(page, en_carrito, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Validando el carrito con {len(en_carrito)} producto(s)\n")
 
        selector_comprar = selectores.get("btn_ecom_proceed_to_buy")
        if not selector_comprar:
            raise KeyError("No se encontró el selector 'btn_ecom_proceed_to_buy' en la configuración.")
        boton_comprar = localizar_elemento(page, "btn_ecom_proceed_to_buy", selector_comprar, nombre_log, hora_ejecucion)
 
        texto = page.get_by_role("dialog").inner_text()
 
        lineas = re.findall(r"-\s*\$\s?\d+(?:\.\d+)?\s*x\s*\d+", texto)
        assert len(lineas) == len(en_carrito), \
            f"El carrito muestra {len(lineas)} línea(s) y se esperaban {len(en_carrito)}. Texto: {texto!r}"
 
        total_esperado = 0
        for item in en_carrito:
            producto = item["producto"]
            linea = re.search(re.escape(producto["nombre"]) + r"\s*-\s*\$\s?(\d+(?:\.\d+)?)\s*x\s*(\d+)", texto)
            assert linea, f"El carrito no muestra la línea de '{producto['nombre']}'. Texto: {texto!r}"
            assert float(linea.group(1)) == producto["precio"], \
                f"Precio de '{producto['nombre']}' en el carrito {linea.group(1)} distinto a {producto['precio']}."
            assert int(linea.group(2)) == item["cantidad"], \
                f"Cantidad de '{producto['nombre']}' en el carrito {linea.group(2)} distinta a {item['cantidad']}."
            expect(page.get_by_test_id(f"remove-from-cart-{producto['id']}")).to_be_visible()
            total_esperado += producto["precio"] * item["cantidad"]
 
        total = re.search(r"Total:\s*\$\s?(\d+(?:\.\d+)?)", texto)
        assert total, f"El carrito no muestra el total. Texto: {texto!r}"
        assert float(total.group(1)) == round(total_esperado, 2), \
            f"Total en el carrito {total.group(1)} distinto a la suma esperada {round(total_esperado, 2)}."
 
        selector_carrito = selectores.get("btn_ecom_cart")
        if not selector_carrito:
            raise KeyError("No se encontró el selector 'btn_ecom_cart' en la configuración.")
        boton_carrito = localizar_elemento(page, "btn_ecom_cart", selector_carrito, nombre_log, hora_ejecucion)
        piezas = sum(item["cantidad"] for item in en_carrito)
        expect(boton_carrito).to_have_text(re.compile(rf"^\s*{piezas}\s*$"))
        expect(boton_comprar).to_be_enabled()
 
    except Exception as e:
        error_msg = f"err-> validar_carrito_acumulado() - Fallo al validar el carrito: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
 
 
def eliminar_del_carrito(page, producto, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Quitando '{producto['nombre']}' del carrito\n")
 
        boton_quitar = page.get_by_test_id(f"remove-from-cart-{producto['id']}")
        expect(boton_quitar).to_be_visible()
        boton_quitar.click()
        expect(boton_quitar).to_have_count(0)
 
    except Exception as e:
        error_msg = f"err-> eliminar_del_carrito() - Fallo al quitar el producto del carrito: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
 
 
def validar_busqueda_sin_resultados(page, termino, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, f"---> Validando que '{termino}' no tenga resultados\n")
 
        tarjetas = page.get_by_test_id(re.compile(r"^product-card-\d+$"))
        expect(tarjetas).to_have_count(0)
 
        selector_actual = selectores.get("txt_ecom_result_count")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'txt_ecom_result_count' en la configuración.")
        conteo = localizar_elemento(page, "txt_ecom_result_count", selector_actual, nombre_log, hora_ejecucion)
        expect(conteo).to_contain_text("0")
 
    except Exception as e:
        error_msg = f"err-> validar_busqueda_sin_resultados() - Fallo al validar la búsqueda vacía: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
 
 
def validar_sin_confirmar_pedido(page, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Validando que el pedido no se confirme\n")
 
        selector_actual = selectores.get("ipt_ecom_card_number")
        if not selector_actual:
            raise KeyError("No se encontró el selector 'ipt_ecom_card_number' en la configuración.")
        campo_tarjeta = localizar_elemento(page, "ipt_ecom_card_number", selector_actual, nombre_log, hora_ejecucion)
        expect(campo_tarjeta).to_be_visible()
        expect(page.get_by_test_id("ecom-order-success")).to_have_count(0)
 
    except Exception as e:
        error_msg = f"err-> validar_sin_confirmar_pedido() - Fallo al validar que no se confirma: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def registrar_alertas(page, alertas, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Activando la captura de alertas del navegador\n")

        def capturar(dialogo):
            alertas.append(dialogo.message)
            dialogo.accept()

        page.on("dialog", capturar)

    except Exception as e:
        error_msg = f"err-> registrar_alertas() - Fallo al activar la captura de alertas: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
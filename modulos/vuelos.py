import sys

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.funciones import escribo_log

sys.path.append(".")
selectores = cargar_selectores()

def llenar_formulario_vuelos(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "from": "sel_flight_from",
            "to": "sel_flight_to",
            "departure_date": "ipt_flight_departure_date",
            "return_date": "ipt_flight_return_date",
            "passengers": "ipt_flight_passengers",
            "class": "sel_flight_class",
            "one_way": "chckb_flight_one_way"
        }

        escribo_log(nombre_log, "---> Llenando formulario de reserva de vuelos\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                # Omitir campos opcionales marcados como vacíos
                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo [{campo}]\n")
                    continue

                escribo_log(nombre_log, f"---> Configurando [{campo}]: '{valor}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en el archivo de selectores.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)

                # Identificamos el tipo de campo para aplicar la acción adecuada de Playwright
                tag_name = elemento.evaluate("el => el.tagName.toLowerCase()")
                input_type = elemento.get_attribute("type")

                if tag_name == "select":
                    # Para elementos <option> desplegables
                    elemento.select_option(label=valor)
                elif tag_name == "input" and input_type == "checkbox":
                    # Para la casilla de 'One Way' (espera true/false, sí/no, etc.)
                    marcar = valor.lower() in ["true", "si", "sí", "1", "yes"]
                    elemento.set_checked(marcar)
                else:
                    # Para inputs de texto, fecha, números
                    elemento.scroll_into_view_if_needed()
                    elemento.clear()
                    elemento.fill(valor)
            else:
                escribo_log(nombre_log, f"---> El campo [{campo}] no se especificó o viene vacío. Se omite.\n")

    except Exception as e:
        error_msg = f"err-> llenar_formulario_vuelos() - Fallo al procesar la reserva: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def filtrar_busqueda_vuelos(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_filtros = {
            "sort_by": "sel_flight_sort",
            "airline": "sel_flight_filter_airline",
            "non_stop": "chckb_flight_filter_nonstop"
        }
        escribo_log(nombre_log, "---> Aplicando filtros en la búsqueda de vuelos...\n")

        for campo, key_selector in mapa_filtros.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                # Omitir si viene marcado como opcional/vacío
                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo filtro [{campo}]\n")
                    continue

                escribo_log(nombre_log, f"---> Configurando filtro [{campo}]: '{valor}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)

                tag_name = elemento.evaluate("el => el.tagName.toLowerCase()")
                input_type = elemento.get_attribute("type")

                if tag_name == "select":
                    elemento.select_option(label=valor)
                elif tag_name == "input" and input_type == "checkbox":
                    marcar = valor.lower() in ["true", "si", "sí", "1", "yes"]
                    elemento.set_checked(marcar)

                page.wait_for_timeout(300)
            else:
                escribo_log(nombre_log, f"---> El filtro [{campo}] no se especificó. Se omite.\n")
    except Exception as e:
        error_msg = f"err-> filtrar_busqueda_vuelos() - Fallo al aplicar filtros: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def seleccionar_vuelos_dinamicos(page, table, nombre_log, hora_ejecucion):
    try:
        escribo_log(nombre_log, "---> Procesando selección dinámica de vuelos...\n")

        for row in table:
            trayecto = row.get("trayecto", "departure").lower().strip()
            aerolinea = row.get("aerolinea", "").strip()
            codigo = row.get("codigo", "").strip()

            escribo_log(nombre_log, f"---> Buscando vuelo [{trayecto}] -> Aerolínea: '{aerolinea}', Código: '{codigo}'...\n")

            if trayecto in ["departure", "ida", "salida"]:
                contenedor_id = "flight-departure-list"
            elif trayecto in ["return", "regreso", "vuelta"]:
                contenedor_id = "flight-return-list"
            else:
                raise ValueError(f"Trayecto no reconocido: '{trayecto}'. Usar 'departure' o 'return'.")

            contenedor = page.locator(f"[data-testid='{contenedor_id}']")

            # Botón 'Select' según los parámetros recibidos
            if codigo and codigo.lower() not in ["[vacío]", "[omitir]", "none"]:
                # Búsqueda directa por data-testid del botón del código específico
                btn_select = contenedor.locator(f"[data-testid='flight-select-{codigo}']")
            elif aerolinea and aerolinea.lower() not in ["[vacío]", "[omitir]", "none"]:
                # Búsqueda por texto de aerolínea dentro del contenedor
                tarjeta = contenedor.locator(f".card:has-text('{aerolinea}')").first
                btn_select = tarjeta.locator("button:has-text('Select')")
            else:
                # Si no hay filtros, toma el primer vuelo disponible en el contenedor
                btn_select = contenedor.locator("button:has-text('Select')").first

            if btn_select.count() == 0:
                raise TimeoutError(f"No se encontró ningún vuelo disponible para [{trayecto}] con los criterios especificados.")

            btn_select.scroll_into_view_if_needed()
            btn_select.click(timeout=5000)
            page.wait_for_timeout(500)

    except Exception as e:
        error_msg = f"err-> seleccionar_vuelos_dinamicos() - Fallo al seleccionar vuelos: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def llenar_datos_pasajeros(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "nombre": "ipt_flight_passenger_name",
            "email": "ipt_flight_passenger_email",
            "telefono": "ipt_flight_passenger_phone"
        }

        escribo_log(nombre_log, "---> Llenando formulario de datos del pasajero...\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                # Omitir si viene marcado explícitamente como opcional/vacío
                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo opcional [{campo}]\n")
                    continue

                escribo_log(nombre_log, f"---> Ingresando en [{campo}]: '{valor}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)

                elemento.scroll_into_view_if_needed()
                elemento.clear()
                elemento.fill(valor)
            else:
                escribo_log(nombre_log, f"---> El campo [{campo}] no se especificó o viene vacío. Se omite.\n")

    except Exception as e:
        error_msg = f"err-> llenar_datos_pasajeros() - Fallo al ingresar datos del pasajero: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e


def llenar_formulario_pago(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "numero_tarjeta": "ipt_flight_card_number",
            "expiracion": "ipt_flight_expiry",
            "cvv": "ipt_flight_cvv"
        }

        escribo_log(nombre_log, "---> Llenando información del método de pago...\n")

        for campo, key_selector in mapa_campos.items():
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo [{campo}]\n")
                    continue

                # Mascaramos el log si es CVV o número de tarjeta por privacidad en evidencias
                valor_log = "*****" if campo == "cvv" else valor
                escribo_log(nombre_log, f"---> Ingresando en [{campo}]: '{valor_log}'...\n")

                selector_actual = selectores.get(key_selector)
                if not selector_actual:
                    raise KeyError(f"No se encontró el selector '{key_selector}' en la configuración.")

                elemento = localizar_elemento(page, key_selector, selector_actual, nombre_log, hora_ejecucion)

                elemento.scroll_into_view_if_needed()
                elemento.clear()
                elemento.fill(valor)
            else:
                escribo_log(nombre_log, f"---> El campo [{campo}] no se especificó o viene vacío. Se omite.\n")

    except Exception as e:
        error_msg = f"err-> llenar_formulario_pago() - Fallo al ingresar datos de pago: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e
import sys

from helpers.self_healing import cargar_selectores, localizar_elemento
from librerias.funciones import escribo_log

sys.path.append(".")
selectores = cargar_selectores()

def llenar_formulario_registro(page, row, nombre_log, hora_ejecucion):
    try:
        mapa_campos = {
            "email": "ipt_register_email_QAP",
            "password": "ipt_register_password_QAP",
            "password2": "ipt_register_confirm_password_QAP"
        }
        escribo_log(nombre_log, f"---> Llenando tabla de registro\n")
        for campo, key_selector in mapa_campos.items():
            # Verificamos si la columna viene en la tabla y tiene contenido
            if campo in row.headings and row[campo].strip():
                valor = row[campo].strip()

                # Omitir campos marcados explícitamente como vacíos
                if valor.lower() in ["[vacío]", "[omitir]", "none"]:
                    escribo_log(nombre_log, f"---> Omitiendo campo opcional [{campo}]\n")
                    continue

                escribo_log(nombre_log, f"---> Ingresando en [{campo}]: '{valor}'...\n")

                input_elem = localizar_elemento(
                    page, key_selector, selectores.get(key_selector),
                    nombre_log, hora_ejecucion, timeout=10000
                )
                input_elem.clear()
                input_elem.fill(valor)
            else:
                escribo_log(nombre_log,
                            f"---> El campo [{campo}] no se especificó o viene vacío. Se omite el llenado.\n")

    except Exception as e:
        error_msg = f"err-> llenar_formulario_registro() - Fallo al procesar el formulario: {str(e)}\n."
        escribo_log(nombre_log, f"---> {error_msg}\n")
        raise e

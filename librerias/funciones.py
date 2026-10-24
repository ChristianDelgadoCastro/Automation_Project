import base64
import io
import os.path as path
import secrets
import shutil
import string
import subprocess
import time
from datetime import date
# Para mapa de calor, guardar en CSV
from datetime import datetime
from datetime import timedelta

import lxml.etree as et
import oracledb
import pyodbc
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, Flowable
)

from librerias.directorios import *

lista_fotos = []
lista_pasos = []
util_path = "C:/Py_drivers/util/"

os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
os.makedirs(ALLURE_REPORT_DIR, exist_ok=True)

tracker_evidencias = {}


def existe_popup_error(page, selector, descripcion, test_name, nombre_log, hora_ejecucion, timeout=100):
    """
    Verifica si un popup de error está visible en la página.
    :param page: Objeto Playwright Page
    :param selector: selector CSS o XPath del elemento a buscar
    :param descripcion: descripción para el log
    :param test_name: nombre del test
    :param nombre_log: archivo de log
    :param hora_ejecucion: hora de ejecución
    :param timeout: timeout en ms (Playwright usa ms)
    :return: 1 si existe, 0 si no
    """
    try:
        # Playwright espera visible con timeout
        page.locator(selector).wait_for(state="visible", timeout=timeout)
        # Opcional: save_evidence si quieres capturar screenshot
        save_evidence(page, test_name, "PopUpError", hora_ejecucion)
        return 1
    except PlaywrightTimeoutError:
        # escribo_log(nombre_log, f"---> No encontre: {descripcion}\n")
        return 0
    except Exception as e:
        escribo_log(nombre_log, f"---> existe_popup_error() {str(e)}\n")
        return 0


def clic_popup_error(page, selector, test_name, nombre_log, hora_ejecucion, timeout=3000):
    """
    Hace clic en el botón del popup de error.
    :param page: Objeto Playwright Page
    :param selector: selector CSS o XPath del botón
    :param test_name: nombré del test
    :param nombre_log: archivo de log
    :param hora_ejecucion: hora de ejecución
    :param timeout: timeout en ms
    :return: 1 si cliqueó, 0 si no
    """
    try:
        save_evidence(page, test_name, "PopUpError", hora_ejecucion)
        boton = page.locator(selector)
        boton.wait_for(state="visible", timeout=timeout)
        boton.click()
        escribo_log(nombre_log, f"---> Se presionó [{selector}]\n")
        return 1
    except PlaywrightTimeoutError:
        escribo_log(nombre_log, f"---> No se encontró {selector}\n")
        return 0
    except Exception as e:
        escribo_log(nombre_log, f"---> clic_popup_error() {str(e)}\n")
        return 0
        pass


def existe_error_inesperado(page, rastreo, test_name, nombre_log, hora_ejecucion, exception=Exception()):
    escribo_log(nombre_log, "---> Se inicia rutina para buscar posibles modales con mensajes de error\n")
    fail_xml = rastreo
    descripcion = 'G20'

    errores = [
        ("//*[contains(text(), '(G20)')]", "G20"),
        ("//*[contains(text(), '(B50)')]", "B50"),
        ("//*[contains(text(), '(H23)')]", "H23"),
        ("//*[contains(text(), '(ZZZ)')]", "ZZZ"),
        ("//*[contains(text(), '(H89)')]", "H89"),
        ("//*[contains(text(), '(C01)')]", "C01"),
        ("//*[contains(text(), '(C02)')]", "C02"),
        ("//*[contains(text(), '(IDM)')]", "IDM"),
        ("//*[contains(text(), '(H04)')]", "H04"),
        ("//*[contains(text(), '(H35)')]", "H35"),
        ("//*[contains(text(), '(C45)')]", "C45"),
        ("//*[contains(text(), '(E90)')]", "E90"),
        ("//*[contains(text(), '(H500)')]", "H500"),
        ("//*[contains(text(), '(H78)')]", "H78"),
        ("//*[contains(text(), '[12]')]", "Error 12"),
        ("//*[contains(text(), 'Número máximo de intentos permitidos')]", "Número máximo de intentos permitidos"),
        ("//*[contains(text(), 'no es posible enviar el SMS')]", "No es posible enviar SMS"),
        ("//*[contains(text(), 'cuenta no pertenece al cliente')]", "La cuenta no pertenece al cliente"),
        ("//*[contains(text(), 'Cliente no tiene una FIEL vigente.')]", "FIEL vencida"),
        ("//*[contains(text(), 'FIEL')]", "Error relacionado con la FIEL"),
        ("//*[@id='fpnModalErrorPago']", "Ha ocurrido un error (nomina)"),
        ("//*[@id='txtTitleOpera']", "Archivo en Proceso (nomina)"),
        ("//div[@id='fpnH1' and contains(text(), 'Estamos actualizando Baj')]", "Estamos actualizando B"),
        ("//span[@id='code' and contains(text(), 'A77BF')]", "Estamos actualizando B (A77BF)"),
        ("//div[@id='vtAlert_content' and contains(text(), 'WH001')]", "X_ERROR_WH001"),
        ("//*[contains(text(), 'Tu token físico ha vencido')]", "Token vencido"),
        ("//*[contains(text(), 'Ha ocurrido un error en tu dispersión.')]", "Error en dispersión"),
        ("//*[contains(text(), 'Estas abandonando el alta de empleados')]", "Abandonar empleados"),
    ]

    existe_error = 0
    for selector, desc in errores:
        if existe_popup_error(page, selector, desc, test_name, nombre_log, hora_ejecucion):
            descripcion = desc
            existe_error = 1
            break

    # Manejo error no mapeado (último recurso)
    if existe_error == 0:
        selector_error_gral = ("//div[@id='pupError']/div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']/span["
                               "@id='txtTitlePopUpError' and contains(text(), 'Ha ocurrido un error')]")
        if existe_popup_error(page, selector_error_gral, "Error no mapeado (Ha ocurrido un error)", test_name,
                              nombre_log, hora_ejecucion):
            descripcion = "Error no mapeado (Ha ocurrido un error)"
            # Obtener texto descriptivo
            selector_desc_error = ("//div[@id='pupError']/div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']/span["
                                   "@id='txtDescPopUpError']")
            try:
                texto_desc = page.locator(selector_desc_error).inner_text(timeout=500)
                descripcion += f" [{sustituir_acentos(texto_desc)}]"
            except Exception:
                pass
            existe_error = 1

    if existe_error == 1:
        escribo_log(nombre_log, "---> ENCONTRE: " + descripcion + "\n")
        fail_xml = f"Se encontro modal de Error Inesperado: {descripcion} {rastreo}"
        # almacenar_evidencias(page, test_name, "PopUpError", "", hora_ejecucion, fail_xml)
        # time.sleep(1)  # Espera para que se guarde la evidencia

        escribo_log(nombre_log, "---> Se intentará presionar [Aceptar] en los distintos botones de error...\n")

        botones_error = [
            "//div[@id='pupError']/div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']/button["
            "@id='btnExitPopUpError']",
            "//div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']//button[@id='btnExitPopUpError']",
            "div[id='fpnModalCambiosContainer']>div[id='pnlBotonesCambios']>button[id='btnContinuarCambios1']",
            "div[id='fpnContButon']>button[id='btnAceptarErrorPago']", "//button[@id='btnAccionCambios']",
            "//*[@id='btnAccionCambios']",
            "//*[@id='btnCancelCambiosPer']"
            "//*[@id='txtSalir']"
        ]

        bandera = 0
        for btn_selector in botones_error:
            bandera = clic_popup_error(page, btn_selector, test_name, nombre_log, hora_ejecucion)
            if bandera == 1:
                break

    if existe_error == 1:
        raise Exception(f"Se encontró modal de Error Inesperado: {descripcion}\n")
    else:
        raise Exception(rastreo)


def existe_error_inesperado_empl(page, rastreo, test_name, nombre_log, hora_ejecucion, exception=Exception()):
    escribo_log(nombre_log, "---> Se inicia rutina para buscar posibles modales con mensajes de error (empleados)\n")
    fail_xml = rastreo
    descripcion = None

    errores = [
        ("//*[contains(text(), '(C45)')]", "C45"),
        ("//*[contains(text(), '(E90)')]", "E90"),
        ("//*[contains(text(), '(H78)')]", "H78"),
        ("//*[contains(text(), '(H89)')]", "H89"),
        ("//*[contains(text(), 'intente nuevamente')]", "intente nuevamente"),
        ("//*[contains(text(), 'Revise archivo de propiedades')]", "Revise archivo de propiedades"),
        ("//*[contains(text(), 'valida la referencia')]", "valida la referencia"),
        ("//*[contains(text(), '(H500)')]", "H500"),
        ("//*[contains(text(), 'No pudo realizarse')]", "No pudo realizarse"),
        ("//*[contains(text(), 'SPIDEnvio')]", "SPIDEnvio"),
        ("//*[contains(text(), 'Error en Fecha de Operacion')]", "Error en Fecha de Operacion"),
        ("//*[contains(text(), 'Claves inválidas')]", "Claves inválidas"),
        ("//*[contains(text(), 'Ha ocurrido un error en tu dispersion')]", "Error en dispersion"),
    ]

    existe_error = 0
    for selector, desc in errores:
        try:
            # Espera visible con timeout corto para no demorar mucho
            page.locator(f"xpath={selector}").wait_for(state="visible", timeout=1000)
            descripcion = desc
            existe_error = 1
            break
        except Exception:
            continue

    if existe_error == 1:
        escribo_log(nombre_log, f"---> ENCONTRE: {descripcion}\n")
        fail_xml = f"Se encontro modal de Error Inesperado: {descripcion} {rastreo}"
        almacenar_evidencias(page, test_name, "PopUpError", "", hora_ejecucion, fail_xml)
        time.sleep(1)  # Espera para que se guarde la evidencia

        escribo_log(nombre_log, "---> Se intentará presionar [Aceptar] en los distintos botones de error...\n")

        botones_error = [
            "//div[@id='pupError']/div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']/button["
            "@id='btnExitPopUpError']",
            "//div[@id='fpnPopUpError']/div[@id='fpnContPopUpError']//button[@id='btnExitPopUpError']",
            "div[id='fpnModalCambiosContainer']>div[id='pnlBotonesCambios']>button[id='btnContinuarCambios1']",
            "div[id='fpnContButon']>button[id='btnAceptarErrorPago']",
        ]

        for btn_selector in botones_error:
            try:
                boton = page.locator(f"xpath={btn_selector}" if btn_selector.startswith("//") else btn_selector)
                boton.wait_for(state="visible", timeout=3000)
                boton.click()
                escribo_log(nombre_log, f"---> Se presionó [{btn_selector}]\n")
                break
            except Exception:
                continue

        escribo_log(nombre_log, "---> (2) Cerre Sesion\n")

        # Actualiza XML con fallo
        validar_existe_xml(XML_REGRESION, '1', '1', '1', test_name, 'FAIL', fail_xml,
                           "existe_error_inesperado_empl()", nombre_log)

        raise Exception(f"Se encontró modal de Error Inesperado: {descripcion}\n")
    else:
        # No se encontró error, pero igual actualiza XML con fallo y cierra sesión
        validar_existe_xml(XML_REGRESION, '1', '1', '1', test_name, 'FAIL', fail_xml,
                           "existe_error_inesperado_empl()", nombre_log)
        escribo_log(nombre_log, "---> (2) Cerre Sesion\n")
        raise type(exception)(rastreo)


def encabezado_log(nombre_log, test_name, hora_ejecucion):
    escribo_log(nombre_log, "==============================================\n")
    escribo_log(nombre_log, test_name + " " + hora_ejecucion + "\n")
    escribo_log(nombre_log, "==============================================\n")


def leer_hora():
    ruta_hora = Path(DIR_HORA_EJECUCION)

    if not ruta_hora.exists():
        print(f"El archivo [{ruta_hora}] no existe. Creando archivo...")

        ruta_hora.parent.mkdir(parents=True, exist_ok=True)
        ruta_hora.touch(exist_ok=True)

    with open(ruta_hora, mode="r", encoding="utf-8") as f:
        hora = f.readline().strip()
    print("--->" + str(hora))
    return hora


def escribo_log(nombre_log, texto):
    with open(nombre_log, "a+", encoding="utf-8") as f:
        f.write(texto)


def creo_log(test_name, hora_ejecucion):
    try:
        today = date.today()
        fecha = today.strftime("%Y_%m_%d")

        path_log = Path(DIR_EVIDENCIAS) / fecha / hora_ejecucion / test_name
        if not path_log.exists():
            path_log.mkdir(parents=True, exist_ok=True)

        file_log = path_log / f"{test_name}.txt"
        return str(file_log)
    except Exception as err:
        print("Error al crear log: " + str(err))


def restaura_insumo(dbms, user, password, host, port, service_name, query, nombre_log):
    """Establece conexiones síncronas hacia Oracle o SQL Server para ejecutar comandos DML/DDL.

    Discrimina el motor utilizando el parámetro `dbms`. Para 'oracle', inicializa el cliente
    pesado/ligero y ejecuta la consulta con confirmación automática. Para 'sqlserver',
    construye una cadena de conexión basada en el Driver 18 de ODBC con autenticación
    integrada (Trusted Connection), confirmando los cambios al finalizar.

    Args:
        dbms (str): Identificador del motor de base de datos ('oracle' o 'sqlserver').
        user (str, optional): Nombre del usuario de conexión (puede ser None para SQL Server Trust).
        password (str, optional): Contraseña de la cuenta (puede ser None para SQL Server Trust).
        host (str): Dirección IP o nombre de host del servidor de base de datos.
        port (str, optional): Puerto de red del servicio de base de datos.
        service_name (str): Nombre del servicio/SID (Oracle) o nombre de la base de datos (SQL Server).
        query (str): Sentencia SQL nativa estructurada que se someterá a ejecución (ej. DELETE, UPDATE).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.

    Note:
        Las excepciones internas de los controladores (`oracledb.Error`, etc.) se mitigan localmente
        escribiendo el error detallado en el log sin interrumpir drásticamente la pila de ejecución,
        a menos que ocurra una falla crítica de infraestructura de alto nivel.
    """
    try:
        if dbms == "oracle":
            try:
                oracledb.init_oracle_client(lib_dir=DIR_ORACLE)
                connection = oracledb.connect(user=user, password=password,
                                              host=host,
                                              port=port,
                                              service_name=service_name)
                cursor = connection.cursor()
                # cursor.execute("delete from soa_tae_grupotddn where id_grupotddn = '389406'")
                cursor.execute(query)
                connection.commit()
                escribo_log(nombre_log, "---> Commit a: " + query + "\n")
                cursor.close()
                connection.close()
            except oracledb.Error as error:
                escribo_log(nombre_log, "---> restaura_insumo() [oracle]" + f"{str(error)=}\n")
        elif dbms == "sqlserver":
            try:
                connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};" \
                                    f"SERVER={host};" \
                                    f"DATABASE={service_name};" \
                                    f"Trusted_Connection=yes;" \
                                    f"TrustServerCertificate=yes;" \
                                    f"Encrypt=no;" \
                                    f"Connection Timeout=30;"
                # f"UID={user};" \
                # f"PWD={password};" \

                escribo_log(nombre_log, "--->\tAbriendo conexion a bd...\n")
                connection = pyodbc.connect(connection_string)

                cursor = connection.cursor()

                # cursor.execute("select top 1 rowno from sipi")
                # for fila in cursor.fetchall():
                #     escribo_log(nombre_log, f"---> resultado [{fila}]\n")

                escribo_log(nombre_log, "--->\tRestaurando insumo...\n")
                cursor.execute(query)
                cursor.commit()
                escribo_log(nombre_log, "--->    Commit a: " + query + "\n")
                cursor.close()

                escribo_log(nombre_log, "--->\tCerrando conexion a bd...\n")
                connection.close()
            except Exception as error:
                escribo_log(nombre_log, "---> restaura_insumo() [sql_server]" + f"{str(error)=}\n")
    except Exception:
        raise


def validar_existe_xml(tipo_regresion, cantidad_failures, cantidad_exito, cantidad_test, test_name, status,
                       descripcion_error, rastreo, nombre_log, path_evidencia=None, test_case_id=None):
    descripcion_error = sustituir_acentos(descripcion_error)

    try:
        # Preguntamos si existe el archivo regresion.xml
        if path.exists(ARCHIVO_XML):
            escribo_log(nombre_log, "---> Actualizo XML existente\n")

            # Abrimos el archivo como solo lectura
            with open(ARCHIVO_XML, 'rt', encoding='utf-8') as f:
                regresion_xml = et.parse(f)

            # Busco el nodo <testsuite> para preguntar si es el archivo coincidiente
            for nodo in regresion_xml.findall('./testsuite'):
                if nodo.attrib.get('name') == tipo_regresion:
                    testcase = et.SubElement(nodo, 'testcase')
                    testcase.set('status', status)
                    testcase.set('name', test_name)
                    # Vincular Elemento de Trabajo (Test Case ID de Azure)
                    if test_case_id:
                        props = et.SubElement(testcase, 'properties')
                        prop = et.SubElement(props, 'property')
                        prop.set('name', 'testCaseId')
                        prop.set('value', str(test_case_id))
                    #  Adjuntar Evidencia (PDF o Captura)
                    if path_evidencia and path.exists(path_evidencia):
                        sys_out = et.SubElement(testcase, 'system-out')
                        sys_out.text = f"[[ATTACHMENT|{path_evidencia}]]"
                    if status == 'FAIL':
                        failure = et.SubElement(testcase, 'failure')
                        failure.set("message", descripcion_error)
                    elif status == 'BLOQUEADO':
                        skipped = et.SubElement(testcase, 'skipped')
                        skipped.set("message", descripcion_error)
                    with open(ARCHIVO_XML, 'wb') as f:
                        regresion_xml.write(f, xml_declaration=True, pretty_print=True, encoding='UTF-8')
        else:
            escribo_log(nombre_log, "---> Genero XML nuevo\n")
            escribe_nuevo_xml('1', '1', '1', test_name, status, descripcion_error, rastreo, path_evidencia,
                              test_case_id)
    except Exception:
        raise


def escribe_nuevo_xml(cantidad_failures, cantidad_exito, cantidad_test, test_name, status, descripcion_error, rastreo, path_evidencia=None, test_case_id=None):
    testsuites = et.Element('testsuites')
    construye_xml(testsuites, cantidad_failures, cantidad_exito, cantidad_test, test_name, status, descripcion_error, path_evidencia, test_case_id)
    with open(ARCHIVO_XML, 'wb') as f:
        doc = et.ElementTree(testsuites)
        doc.write(f, xml_declaration=True, pretty_print=True, encoding='UTF-8')


def construye_xml(testsuites, failures, exito, cantidad_test, test_name, status, descripcion_error, path_evidencia=None,
                  test_case_id=None):
    testsuite = et.SubElement(testsuites, 'testsuite')
    testsuite.set('name', XML_REGRESION)
    testsuite.set('pass', exito)
    testsuite.set('failures', failures)
    testsuite.set('test', cantidad_test)

    testcase = et.SubElement(testsuite, 'testcase')
    testcase.set('status', status)
    testcase.set('name', test_name)
    if test_case_id:
        props = et.SubElement(testcase, 'properties')
        prop = et.SubElement(props, 'property')
        prop.set('name', 'testCaseId')
        prop.set('value', str(test_case_id))
    if path_evidencia and path.exists(path_evidencia):
        sys_out = et.SubElement(testcase, 'system-out')
        sys_out.text = f"[[ATTACHMENT|{path_evidencia}]]"
    if status == 'FAIL':
        failure = et.SubElement(testcase, 'failure')
        failure.set("message", descripcion_error)
    elif status == 'BLOQUEADO':
        skipped = et.SubElement(testcase, 'skipped')
        skipped.set("message", descripcion_error)
    testsuites.append(testsuite)


def save_evidence(page, test_name, paso, hoja_ejecucion):
    global tracker_evidencias
    try:
        today = date.today()
        fecha = today.strftime("%Y_%m_%d")
        path_evidence = os.path.join(DIR_EVIDENCIAS, fecha, hoja_ejecucion, test_name)
        if not os.path.exists(path_evidence):
            os.makedirs(path_evidence)
        # Lógica del tracker
        if paso not in tracker_evidencias:
            # si es la primera vez que vemos este nombre
            tracker_evidencias[paso] = 0
            nombre_final = paso
        else:
            # Si ya existe, le sumamos 1
            tracker_evidencias[paso] += 1
            nombre_final = f"{paso}_{tracker_evidencias[paso]}"
        # Ruta completa del archivo usando el nombre_final
        file_evidence = os.path.join(path_evidence, f"{nombre_final}.png")
        # Tomar screenshot
        page.screenshot(path=file_evidence)
    except Exception as err:
        print("Error al tomar screenshot de evidencia: " + str(err))


def almacenar_evidencias(page, test_name, nombre_screnshot, descripcion_screnshot, hoja_ejecucion, err_desc=""):
    """
    Función para guardar un screshot en una ruta específica, luego guardar este nombre y descripcion en listas que se
    retornan como valores para después usar al generar un pdf
    :param page: Objeto Playwright Page
    :param test_name: nombre del caso de prueba
    :param nombre_screnshot: nombre que se le dará al archivo png y al paso en la evidencia
    :param descripcion_screnshot: descripcion del screnshot a tomar
    :param hoja_ejecucion: hora de ejecucion del caso de prueba
    :param err_desc: (Opcional) Descripción del error a guardar en la descripciónd de la evidencia
    :return: none
    """
    descripcion_final = ""
    try:
        today = date.today()
        fecha = today.strftime("%Y_%m_%d")
        # Obtener path de evidencias
        path_evidence = DIR_EVIDENCIAS + "/" + fecha + "/" + hoja_ejecucion + "/" + test_name

        # Calcular path + archivo evidencias
        file_evidence = path_evidence + "/" + nombre_screnshot + ".png"

        # crear directorio de evidencias si no existe
        if not os.path.exists(path_evidence):
            os.makedirs(path_evidence)
        # tomar screenshot
        # print("---> " + str(file_evidence))
        page.save_screenshot(file_evidence)

        # Agregar a una lista los screnshot
        lista_fotos.append(nombre_screnshot)

        # Agregar a una lista la descripcion de los screnshot
        if descripcion_screnshot != "":
            descripcion_final += descripcion_screnshot
            if err_desc != "":
                descripcion_final += f" - {err_desc}"
        elif err_desc != "":
            descripcion_final += err_desc

        lista_pasos.append(descripcion_final)

        return lista_fotos, lista_pasos
    except FileExistsError:
        print("El directorio para almacenar la evidencia ya existia")
    except Exception as err:
        print("Error al tomar screenshot de evidencia" + str(err))


def obtener_evidencias():
    return lista_fotos, lista_pasos


def generar_archivo_pdf(p_lista_fotos, p_lista_pasos, test_name, extension, hora_ejecucion, nombre_log=""):
    filename = "env_" + test_name + extension

    today = date.today()
    fecha = today.strftime("%Y_%m_%d")
    fecha_reporte = today.strftime("%d %b %Y")

    # Construcción de la ruta usando pathlib para evitar problemas con '+' o '/'
    path_evidence = Path(DIR_EVIDENCIAS) / fecha / hora_ejecucion / test_name
    path_evidence.mkdir(parents=True, exist_ok=True)

    ruta_archivo_pdf = path_evidence / filename
    pdf = canvas.Canvas(str(ruta_archivo_pdf))

    a = 0
    b = 0
    ancho_maximo_texto = 500
    for i in p_lista_fotos:
        screenshotpath = path_evidence / f"{p_lista_fotos[a]}.png"
        b = b + 1
        a = a + 1

        mensaje_paso = p_lista_pasos[a - 1]

        if b == 1:
            encabezado_pdf(pdf, test_name, fecha_reporte)
            pdf.drawInlineImage(str(screenshotpath), 35, 385, width=500, height=300)

            tamanio_fuente = 10.0
            while pdfmetrics.stringWidth(mensaje_paso, "FuenteVerdana",
                                         tamanio_fuente) > ancho_maximo_texto and tamanio_fuente > 7.5:
                tamanio_fuente -= 0.5

            palabras = mensaje_paso.split()
            lineas = []
            linea_actual = ""
            for palabra in palabras:
                if pdfmetrics.stringWidth(linea_actual + palabra + " ", "FuenteVerdana",
                                          tamanio_fuente) <= ancho_maximo_texto:
                    linea_actual += palabra + " "
                else:
                    lineas.append(linea_actual.strip())
                    linea_actual = palabra + " "
            if linea_actual:
                lineas.append(linea_actual.strip())

            text = pdf.beginText(35, 373)
            text.setFont("FuenteVerdana", tamanio_fuente)
            text.setFillColor(colors.black)
            text.setLeading(tamanio_fuente + 2)
            for linea in lineas:
                text.textLine(linea)
            pdf.drawText(text)

        elif b == 2:
            pdf.drawInlineImage(str(screenshotpath), 35, 55, width=500, height=300)

            tamanio_fuente = 10.0
            while pdfmetrics.stringWidth(mensaje_paso, "FuenteVerdana",
                                         tamanio_fuente) > ancho_maximo_texto and tamanio_fuente > 7.5:
                tamanio_fuente -= 0.5

            palabras = mensaje_paso.split()
            lineas = []
            linea_actual = ""
            for palabra in palabras:
                if pdfmetrics.stringWidth(linea_actual + palabra + " ", "FuenteVerdana",
                                          tamanio_fuente) <= ancho_maximo_texto:
                    linea_actual += palabra + " "
                else:
                    lineas.append(linea_actual.strip())
                    linea_actual = palabra + " "
            if linea_actual:
                lineas.append(linea_actual.strip())

            text = pdf.beginText(35, 43)
            text.setFont("FuenteVerdana", tamanio_fuente)
            text.setFillColor(colors.black)
            text.setLeading(tamanio_fuente + 2)
            for linea in lineas:
                text.textLine(linea)
            pdf.drawText(text)
            pdf.showPage()
            b = 0

    if ruta_archivo_pdf.exists():
        ruta_archivo_pdf.unlink()

    pdf.save()

    # Vaciar listas si existen globalmente
    if 'lista_fotos' in globals():
        lista_fotos.clear()
    if 'lista_pasos' in globals():
        lista_pasos.clear()


def guardar_trace(test_name, origen_trace, hora_ejecucion):
    """Mueve el trace exacto generado por Playwright a la carpeta de evidencias"""
    if not origen_trace or not os.path.exists(origen_trace):
        return

    fecha = date.today().strftime("%Y_%m_%d")
    path_evidence = Path(DIR_EVIDENCIAS) / fecha / hora_ejecucion / test_name
    path_evidence.mkdir(parents=True, exist_ok=True)

    destino_trace = path_evidence / f"trace_{test_name}.zip"

    try:
        shutil.move(origen_trace, str(destino_trace))
    except Exception as e:
        print(f"Error al mover el trace: {e}")


def guardar_video(test_name, origen_video, hora_ejecucion):
    """Mueve el video exacto generado por Playwright a la carpeta de evidencias"""
    if not origen_video or not os.path.exists(origen_video):
        return

    fecha = date.today().strftime("%Y_%m_%d")
    path_evidence = Path(DIR_EVIDENCIAS) / fecha / hora_ejecucion / test_name
    path_evidence.mkdir(parents=True, exist_ok=True)
    destino_video = path_evidence / f"video_{test_name}.webm"

    try:
        shutil.move(origen_video, str(destino_video))
    except Exception as e:
        print(f"Error al mover el video: {e}")


def encabezado_pdf(pdf, test_case, fecha):
    title2 = ['Pruebas Automatizadas', 'Equipo QA 1']
    sub_title = test_case

    # Obtenemos el path actual usando pathlib
    logo = Path.cwd() / 'res' / 'BACKGTOUNDLESS.png'

    pdfmetrics.registerFont(
        TTFont('FuenteVerdana', 'C:\\Windows\\Fonts\\Verdana.ttf')
    )
    text = pdf.beginText(20, 770)
    text.setFont("FuenteVerdana", 16)
    text.setFillColor(colors.black)
    for line in title2:
        text.textLine(line)
    pdf.drawText(text)

    if logo.exists():
        pdf.drawInlineImage(str(logo), 488, 744, width=40, height=40)

    text = pdf.beginText(20, 720)
    text.setFont("FuenteVerdana", 16)
    text.setFillColor(colors.gray)
    text.textLine(sub_title)
    pdf.drawText(text)

    text = pdf.beginText(480, 720)
    text.setFont("FuenteVerdana", 10)
    text.setFillColor(colors.gray)
    text.textLine(fecha)
    pdf.drawText(text)

    pdf.line(20, 710, 550, 710)
    title2 = ['Pruebas Automatizadas',
              'Equipo QA 1']
    sub_title = test_case
    path_res = os.getcwd().split("\\")
    logo = "/".join(path_res) + '/res/BACKGTOUNDLESS.png'
    pdfmetrics.registerFont(
        TTFont('FuenteVerdana', 'C:\\Windows\\Fonts\\Verdana.ttf')
    )
    text = pdf.beginText(20, 770)
    text.setFont("FuenteVerdana", 16)
    text.setFillColor(colors.black)
    for line in title2:
        text.textLine(line)
    pdf.drawText(text)

    pdf.drawInlineImage(logo, 488, 744, width=40, height=40)

    text = pdf.beginText(20, 720)
    text.setFont("FuenteVerdana", 16)
    text.setFillColor(colors.gray)
    text.textLine(sub_title)
    pdf.drawText(text)

    text = pdf.beginText(480, 720)
    text.setFont("FuenteVerdana", 10)
    text.setFillColor(colors.gray)
    text.textLine(fecha)
    pdf.drawText(text)

    pdf.line(20, 710, 550, 710)


def lista_screenshot(name_picture):
    global tracker_evidencias
    # Consultamos el tracker para saber con qué nombre se guardó hace 1 milisegundo
    count = tracker_evidencias.get(name_picture, 0)
    if count == 0:
        nombre_real = name_picture
    else:
        nombre_real = f"{name_picture}_{count}"
    # Devolvemos el nombre exacto (ej. "Capturar cuenta_2") para que el PDF lo encuentre
    return [nombre_real]


def lista_pasos_descripcion(paso_descripcion):
    return [paso_descripcion]


def escribir_archivo_control(texto, archivo, nombre_log):
    """
    :param texto: Lo que se escribe en el archivo
    :param archivo:  La ruta del archivo
    :param nombre_log: Nombre del log
    :return: None
    """
    # Crea el archivo de control si no existe y si existe lo actualiza.
    escribo_log(nombre_log, "---> Escribir en el archivo de control...\n")
    try:
        f = open(archivo, "a")
        f.write(texto + "\n")
        f.close()
    except Exception as err:
        print("Error al escribir en archivo de control : " + str(err))


def sustituir_acentos(cadena_original):
    cadena_sin_acentos = cadena_original
    cadena_sin_acentos = cadena_sin_acentos.replace("á", "-a")
    cadena_sin_acentos = cadena_sin_acentos.replace("ó", "-o")
    cadena_sin_acentos = cadena_sin_acentos.replace("é", "-e")
    cadena_sin_acentos = cadena_sin_acentos.replace("ú", "-u")
    cadena_sin_acentos = cadena_sin_acentos.replace("í", "-i")
    cadena_sin_acentos = cadena_sin_acentos.replace("Á", "-A")
    cadena_sin_acentos = cadena_sin_acentos.replace("Ó", "-O")
    cadena_sin_acentos = cadena_sin_acentos.replace("É", "-E")
    cadena_sin_acentos = cadena_sin_acentos.replace("Ú", "-U")
    cadena_sin_acentos = cadena_sin_acentos.replace("Í", "-I")
    return cadena_sin_acentos


def obtener_fecha(dias=0, formato="%d%m%Y", semana_laboral=True):
    """
    Devuelve la fecha actual. Se puede agregar un desfase y un formato opcional.
    :param dias: Opcional. Desfase en días respecto a la fecha actual. Por default es 0.
    :param formato: Opcional. Formato de fecha (strtime()). Por default es "%d%m%Y".
    :param semana_laboral: Opcional. Si es True la fecha devuelta será un día de lunes a viernes,
                           es decir, la fecha caerá en una semana laboral. Por default es True.
    :return: (str) Fecha actual + desfase
    """
    fecha = date.today()
    fecha = fecha + timedelta(days=dias)
    if semana_laboral:
        if fecha.weekday() > 4:
            fecha = fecha + timedelta(days=(7 - fecha.weekday()))
    return fecha.strftime(formato)


def formatear_tiempo(tiempo_segundos):
    minutos = int(tiempo_segundos // 60)
    segundos = tiempo_segundos % 60

    if minutos > 0:
        return f"{minutos} minuto(s) con {segundos:.2f} segundo(s)"
    else:
        return f"{segundos:.2f} segundo(s)"


def generar_num_aleatorio(longitud):
    digitos = string.digits

    num = ''
    for i in range(longitud):
        num += ''.join(secrets.choice(digitos))

    return num


def insumo_x_linea(linea, variable1, variable2):
    if linea == "L1":
        return variable1
    else:
        return variable2


def clic_condicional(page, selector, nombre_log, timeout=3000):
    """
    Intenta hacer clic en un elemento si existe en la página.
    :param page: Objeto Playwright Page
    :param selector: selector CSS o XPath (string)
    :param nombre_log: archivo de log
    :param timeout: tiempo máximo para esperar el selector (ms)
    """
    escribo_log(nombre_log, f"--->\tSe intentará hacer clic en elemento [{selector}]...\n")
    try:
        locator = page.locator(selector)
        if locator.count() > 0:
            escribo_log(nombre_log, f"--->\tElemento encontrado: [{selector}]. Se procede a presionarlo...\n")
            locator.first.click()
        else:
            escribo_log(nombre_log, f"--->\tElemento: [{selector}] no se encontro. Continuando...\n")
    except Exception as err:
        escribo_log(nombre_log, "---> clic_condicional() " + f"{err=}\n")
        pass


def fecha_formateada(fecha=None):
    meses = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]
    if fecha is None:
        fecha = datetime.today()
    dia = fecha.day
    mes = meses[fecha.month - 1]
    anio = fecha.year
    return f"{dia:02d}-{mes}-{anio}"


def obtener_texto(page, selector, nombre_log, timeout=5000):
    """
    Obtiene el texto de un elemento esperando que sea visible.
    :param page: Objeto Playwright Page
    :param selector: selector CSS o XPath (string)
    :param nombre_log: archivo de log
    :param timeout: tiempo máximo para esperar visibilidad (ms)
    :return: texto en minúsculas y sin espacios al inicio/fin
    """
    try:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        texto_elemento = locator.inner_text().lower().strip()
        return texto_elemento
    except PlaywrightTimeoutError as err:
        mensaje = f"Elemento con selector [{selector}] no encontrado (timeout)"
        escribo_log(nombre_log, f"---> obtener_texto() {err=} {mensaje}\n")
        raise TimeoutError(mensaje) from err
    except Exception as err:
        mensaje = f"Error al obtener texto del elemento [{selector}]"
        escribo_log(nombre_log, f"---> obtener_texto() {err=}\n")
        raise type(err)(mensaje) from err


def reemplazar_fecha_archivo_nomina(tipo, ruta, archivo, archivo_modficado):
    today = ""
    fecha = ""
    dias = 0
    contenido3 = ""

    if tipo == 'ahora':
        dias = 0
        fecha = obtener_fecha(dias=dias, formato="%Y%m%d", semana_laboral=True)
    elif tipo == 'programado':
        dias = 2
        fecha = obtener_fecha(dias=dias, formato="%Y%m%d", semana_laboral=True)

    with open(ruta + archivo, "r") as entrada, open(ruta + archivo_modficado, "w") as salida:
        for i, linea in enumerate(entrada):
            if i == 0:  # Encabezado del archivo
                contenido1 = linea.replace(linea[23:31], fecha)
                contenido3 += contenido1
            elif i == 1 and len(linea) == 182:  # Contenido (2 fechas por línea)
                contenido2 = linea.replace(linea[11:19], fecha)
                contenido2 = linea.replace(linea[40:48], fecha)
                contenido3 += contenido2
            else:
                contenido3 += linea
        salida.write(contenido3)


def scroll_js(page, nombre_log, altura=300, incremental=True):
    """Realiza un desplazamiento vertical en la ventana del navegador mediante JavaScript.

    Ejecuta código JS en el contexto de la página utilizando animaciones fluidas
    (`smooth`). Dependiendo del parámetro `incremental`, el desplazamiento se calcula
    de manera relativa a la posición actual o de forma absoluta en el documento.

    Args:
        page (Page): Instancia del navegador activa (Playwright Page).
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.
        altura (int, optional): La cantidad de píxeles que se desea desplazar.
            Por defecto es 300.
        incremental (bool, optional): Si es True, suma los píxeles a la posición actual
            (`scrollBy`). Si es False, se desplaza a la coordenada exacta (`scrollTo`).
            Por defecto es True.

    Raises:
        Exception: Si ocurre un fallo al evaluar el script en el navegador, encapsulando
            el error original de Playwright.

    Note:
        La función incluye una pausa implícita de 500ms tras el desplazamiento. Esto
        asegura que las animaciones del navegador concluyan y los eventos del DOM
        (como la carga diferida de imágenes o componentes) terminen de dispararse.
    """
    try:
        # Definimos si usamos scrollBy (relativo) o scrollTo (absoluto)
        metodo = "scrollBy" if incremental else "scrollTo"

        # Ejecutamos el JS directamente en el contexto de la página
        # Usamos 'smooth' para una transición fluida que ayude a disparar eventos de carga
        page.evaluate(f"""
            window.{metodo}({{
                top: {altura},
                behavior: 'smooth'
            }});
        """)

        # Opcional: Pequeña espera para que el scroll termine antes de la siguiente acción
        page.wait_for_timeout(500)

        escribo_log(nombre_log, f"---> Se realiza scroll\n")

    except Exception as err:
        error_msg = f"Error en javascript {metodo}() con altura {altura}"
        escribo_log(nombre_log, f"---> scroll_js() err={err}\n")
        # Re-lanzamos la excepción manteniendo el rastro del error original
        raise Exception(f"{error_msg}: {str(err)}")


def actualizar_fecha_prog_para_dispersar(page, linea, num_programacion, test_name, nombre_log, hora_ejecucion):
    respuesta = ""
    # Limpieza de la lógica de línea (L1 -> 1, L2 -> 2)
    linea_str = "1" if linea == "L1" else "2"
    # Construimos la cadena de argumentos
    args = f"{linea_str} -f {num_programacion}"
    try:
        respuesta = ejecutar_utileria("java", util_path, "HMACPosix.jar", args, "true", nombre_log)
    except AssertionError as err:
        escribo_log(nombre_log, f"--->\tactualizar_fecha_prog_para_dispersar() "
                                f"No fue posible actualizar fecha de programacion. Respuesta: [{respuesta}] "
                                f"{type(err).__name__}\n")
    except Exception as err:
        escribo_log(nombre_log, f"--->\tactualizar_fecha_prog_para_dispersar(). Respuesta: [{respuesta}] "
                                f"{type(err).__name__}\n")
        rastreo = f"err={type(err).__name__} [Buscar por numero de programacion] {str(err)}"
        # Llamamos al manejador de errores pasando 'page' (Playwright) en lugar de 'driver' y 'wait'
        existe_error_inesperado(page, rastreo, test_name, nombre_log, hora_ejecucion)
        raise


def ejecutar_utileria(tipo, ruta, ejecutable, args, respuesta_esperada, nombre_log):
    try:
        salida = ""
        comando = []
        ruta_ejecutable = os.path.join(ruta, ejecutable)
        # Verificar que el .jar realmente exista antes de intentar ejecutarlo
        if not os.path.exists(ruta_ejecutable):
            raise FileNotFoundError(f"No se encontro el ejecutable en la ruta: {ruta_ejecutable}")
        if tipo == "java":
            # Pasamos los argumentos como lista.
            comando = ["java", "-jar", ruta_ejecutable] + args.split()
        escribo_log(nombre_log, f"--->\tEjecutando comando: [{' '.join(comando)}]...\n")
        # Ejecución segura. text=True hace que stdout sea un string limpio automáticamente.
        p = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ruta, text=True)
        # Guardamos la salida y le quitamos los saltos de línea innecesarios
        salida = p.stdout.strip()
        escribo_log(nombre_log, f"--->\tRespuesta: [{salida}]\n")
        # Validación de la respuesta esperada
        coincidencias = salida.count(respuesta_esperada)
        escribo_log(nombre_log, f"--->\t# de veces que aparece la respuesta esperada [{respuesta_esperada}]: "
                                f"{coincidencias}\n")
        assert coincidencias >= 1, f"--->\tNo se encontro la respuesta esperada [{respuesta_esperada}]. Salida real: {salida}"
        return salida
    except Exception as err:
        escribo_log(nombre_log, f"--->\tejecutar_utileria() {type(err).__name__}: {str(err)}\n")
        raise


class NumberedCanvas(canvas.Canvas):
    """ Canvas que recibe el total de páginas y dibuja el pie de página """

    def __init__(self, *args, total_pages=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_pages = total_pages

    def showPage(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        # Pie de página
        self.drawString(36, 20, "Equipo 1 — Pruebas Automatizadas Automation Project")
        total_str = self.total_pages if self.total_pages > 0 else self._pageNumber
        page_text = f"Página {self._pageNumber} de {total_str}"
        self.drawRightString(612 - 36, 20, page_text)
        # Línea divisoria superior del pie de página
        self.setStrokeColor(colors.HexColor("#D1D1D6"))
        self.setLineWidth(0.5)
        self.line(36, 32, 612 - 36, 32)
        self.restoreState()
        super().showPage()


class BookmarkAnchor(Flowable):
    """ Elemento invisible que registra la página exacta donde se ubica cada escenario y agrega un marcador nativo
    al panel lateral del PDF."""

    def __init__(self, key, title, page_dict):
        super().__init__()
        self.width = 0
        self.height = 0
        self.key = key
        self.title = title
        self.page_dict = page_dict

    def wrap(self, availWidth, availHeight):
        return 0, 0

    def draw(self):
        self.page_dict[self.key] = self.canv._pageNumber
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, level=0, closed=False)


LOGO_BASE64 = "data:image/png;base64,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"
RUTA_LOGO = "./res/BACKGTOUNDLESS.png"
RUTA_LOGO_DERECHA = "./res/BACKGTOUNDLESS.png"


def obtener_imagen_base64(b64_string, width=160, height=35):
    """Convierte una cadena Base64 en un objeto Image de ReportLab."""
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        image_bytes = base64.b64decode(b64_string)
        image_buffer = io.BytesIO(image_bytes)
        return Image(image_buffer, width=width, height=height)
    except Exception as e:
        print(f"Error cargando imagen Base64: {e}")
        return None


def formatear_tiempo_hms(segundos_totales):
    hrs = int(segundos_totales // 3600)
    mins = int((segundos_totales % 3600) // 60)
    segs = int(segundos_totales % 60)
    return f"Hrs : {hrs} Min: {mins} seg: {segs}"


def generar_pdf_consolidado_general(suite_results, ruta_salida=None):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    page_dict = {}

    def construir_story(p_dict):
        styles = getSampleStyleSheet()
        COLOR_PURPLE = colors.HexColor("#4A1B82")
        COLOR_LIGHT_BG = colors.HexColor("#EFEFEF")
        COLOR_CARD_BG = colors.HexColor("#FAFAFA")
        COLOR_CARD_BORDER = colors.HexColor("#E5E7EB")
        style_purple_left = ParagraphStyle('PurpleLeft', parent=styles['Normal'], fontSize=10, leading=13,
                                           textColor=colors.white, fontName="Helvetica-Bold")
        style_gray_right = ParagraphStyle('GrayRight', parent=styles['Normal'], fontSize=10, leading=13,
                                          textColor=colors.HexColor("#222222"))
        style_index_title = ParagraphStyle('IndexTitle', parent=styles['Heading1'], fontSize=16, leading=20,
                                           textColor=colors.white, fontName="Helvetica-Bold")
        style_section_lbl = ParagraphStyle('SectionLbl', parent=styles['Normal'], fontSize=10, leading=14,
                                           textColor=COLOR_PURPLE, fontName="Helvetica-Bold")
        style_link_item = ParagraphStyle('LinkItem', parent=styles['Normal'], fontSize=9, leading=14,
                                         textColor=colors.HexColor("#333333"))
        style_link_item.wordWrap = 'CJK'
        style_h2_card = ParagraphStyle('H2CardStyle', parent=styles['Heading2'], fontSize=12, leading=15,
                                       textColor=colors.HexColor("#111827"), fontName="Helvetica-Bold")
        style_body = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13,
                                    textColor=colors.HexColor("#374151"))
        style_error = ParagraphStyle('ErrorStyle', parent=styles['Normal'], fontSize=9, leading=12,
                                     textColor=colors.HexColor("#DC3545"))
        # Estilos para badges de estado (PASSED/FAILED)
        style_badge_passed = ParagraphStyle('BadgePassed', parent=styles['Normal'], fontSize=9, leading=11,
                                            textColor=colors.HexColor("#155724"), fontName="Helvetica-Bold",
                                            alignment=1)
        style_badge_failed = ParagraphStyle('BadgeFailed', parent=styles['Normal'], fontSize=9, leading=11,
                                            textColor=colors.HexColor("#721C24"), fontName="Helvetica-Bold",
                                            alignment=1)
        story = []

        # Header con imagenes superiores
        story.append(Paragraph("<a name='top_index'/>", style_body))
        img_left = obtener_imagen_base64(LOGO_BASE64, width=160, height=35)
        if not img_left:
            img_left = Paragraph("<b>QA_Automation</b>", style_h2_card)
        img_right = Image(RUTA_LOGO_DERECHA, width=90, height=90) if os.path.exists(RUTA_LOGO_DERECHA) else Paragraph(
            "", style_body)
        header_images_table = Table([[img_left, img_right]], colWidths=[380, 160])
        header_images_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(header_images_table)
        story.append(Spacer(1, 5))

        # Metricas generales

        total_escenarios = len(suite_results)
        passed_tests = sum(1 for r in suite_results if r['status'] == 'PASSED')
        failed_tests = total_escenarios - passed_tests
        rate = (passed_tests / total_escenarios * 100) if total_escenarios > 0 else 0
        tiempo_total_segundos = sum(res.get('segundos_totales', 0) for res in suite_results)
        tiempo_formateado_hms = formatear_tiempo_hms(tiempo_total_segundos)
        fecha_actual_str = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p").lower()
        info_data = [
            [Paragraph("Tipo de Prueba", style_purple_left), Paragraph("Regresión (E2E)", style_gray_right)],
            [Paragraph("Tiempo de ejecución", style_purple_left), Paragraph(tiempo_formateado_hms, style_gray_right)],
            [Paragraph("Total escenarios ejecutados", style_purple_left),
             Paragraph(str(total_escenarios), style_gray_right)],
            [Paragraph("Porcentaje de Éxito", style_purple_left),
             Paragraph(f"<b>{rate:.1f}%</b> ({passed_tests}/{total_escenarios})", style_gray_right)],
            [Paragraph("Fecha ejecución", style_purple_left), Paragraph(fecha_actual_str, style_gray_right)],
        ]
        table_info = Table(info_data, colWidths=[220, 320])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), COLOR_PURPLE),
            ('BACKGROUND', (1, 0), (1, -1), COLOR_LIGHT_BG),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_PURPLE),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table_info)
        story.append(Spacer(1, 15))

        # Tarjeta flotante del indice
        index_header = Table([[Paragraph("ÍNDICE DE ESCENARIOS", style_index_title)]], colWidths=[540])
        index_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_PURPLE),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(index_header)
        story.append(Spacer(1, 10))

        story.append(Paragraph("<b>◆ EVIDENCIAS DE EJECUCIÓN</b>", style_section_lbl))
        story.append(Spacer(1, 6))

        # Renderizamos cada fila directamente en el story con un fondo sutil
        for idx, res in enumerate(suite_results, 1):
            target_id = f"escenario_{idx}"
            nombre_test = res['test_name']
            num_pagina = p_dict.get(target_id, "--")
            is_passed = res['status'] == 'PASSED'
            # 1. Configuración dinámica de colores para el badge
            color_badge_bg = colors.HexColor("#D4EDDA") if is_passed else colors.HexColor("#F8D7DA")
            color_accent = colors.HexColor("#28A745") if is_passed else colors.HexColor("#DC3545")
            style_b = style_badge_passed if is_passed else style_badge_failed
            # 2. Creación de la etiqueta de estado para la columna
            badge_index = Table([[Paragraph(f"<b>{res['status']}</b>", style_b)]], colWidths=[60])
            badge_index.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), color_badge_bg),
                ('BOX', (0, 0), (-1, -1), 0.5, color_accent),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            # 3. Enlaces HTML
            link_html = f"&nbsp;&nbsp;<b><font color='#4A1B82'>⦿</font></b> <a href='#{target_id}' color='#222222'><u>{idx}. {nombre_test}</u></a>"
            page_html = f"<a href='#{target_id}' color='#4A1B82'><b>Pág. {num_pagina}</b></a>"
            # 4. Tabla de 3 columnas (Nombre, Estatus, Página) = 540pt total
            t_index_item = Table([
                [
                    Paragraph(link_html, style_link_item),
                    badge_index,
                    Paragraph(page_html, ParagraphStyle('RPage', parent=style_link_item, alignment=2))
                ]
            ], colWidths=[370, 70, 100])
            # 5. Estilo con barra lateral verde/roja
            t_index_item.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_CARD_BG),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBEFORE', (0, 0), (0, -1), 3, color_accent),  # Borde según el estatus
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t_index_item)
            story.append(Spacer(1, 3))
        story.append(PageBreak())

        # Tarjetas flotantes de escenarios y pasos

        for idx, res in enumerate(suite_results, 1):
            target_id = f"escenario_{idx}"
            title_outline = f"{idx}. [{res['status']}] {res['test_name']}"
            story.append(BookmarkAnchor(target_id, title_outline, p_dict))
            # Tarjeta de encabezado de escenario
            is_passed = res['status'] == 'PASSED'
            color_accent = colors.HexColor("#28A745") if is_passed else colors.HexColor("#DC3545")
            color_badge_bg = colors.HexColor("#D4EDDA") if is_passed else colors.HexColor("#F8D7DA")
            style_badge = style_badge_passed if is_passed else style_badge_failed
            # Badge/Etiqueta flotante de estado
            badge_table = Table([[Paragraph(f"<b>{res['status']}</b>", style_badge)]], colWidths=[75])
            badge_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), color_badge_bg),
                ('BOX', (0, 0), (-1, -1), 0.5, color_accent),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            # Datos del escenario
            header_text = f"<a name='{target_id}'/><b>{idx}. {res['test_name']}</b>"
            scenario_info = [
                Paragraph(header_text, style_h2_card),
                Spacer(1, 2),
                Paragraph(f"<b>Hora:</b> {res['hora']} | <b>Duración:</b> {res['duracion']}", style_body)
            ]
            if res.get('error_msg'):
                scenario_info.append(Spacer(1, 3))
                scenario_info.append(Paragraph(f"<b>Detalle del Error:</b> {res['error_msg']}", style_error))
            # Tarjeta de Escenario
            t_scenario_card = Table([[scenario_info, badge_table]], colWidths=[425, 85])
            t_scenario_card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_CARD_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_CARD_BORDER),
                ('LINEBEFORE', (0, 0), (0, -1), 4, color_accent),  # Barra lateral verde/roja
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(t_scenario_card)
            story.append(Spacer(1, 12))
            # Tarjetas flotantes pasos y evidencias
            screenshots = res.get('screenshots', [])
            pasos = res.get('pasos', [])
            for i, img_path in enumerate(screenshots):
                paso_desc = pasos[i] if i < len(pasos) else f"Evidencia {i + 1}"
                step_content = [
                    Paragraph(f"<b>• Paso {i + 1}:</b> {paso_desc}", style_body)
                ]
                # Búsqueda de imagen
                ruta_real = img_path
                if not os.path.isfile(ruta_real) and 'DIR_EVIDENCIAS' in globals():
                    fecha_hoy = date.today().strftime("%Y_%m_%d")
                    posible_ruta = os.path.join(DIR_EVIDENCIAS, fecha_hoy, res['hora'], res['test_name'],
                                                f"{img_path}.png")
                    if os.path.isfile(posible_ruta):
                        ruta_real = posible_ruta
                # Carga e inclusión de la imagen en el contenido de la tarjeta
                if os.path.isfile(ruta_real):
                    try:
                        img = Image(ruta_real, width=460, height=258)
                        step_content.append(Spacer(1, 6))
                        step_content.append(img)
                    except Exception as img_err:
                        step_content.append(Spacer(1, 4))
                        step_content.append(Paragraph(f"<i>[Error al cargar imagen: {img_err}]</i>", style_error))
                else:
                    step_content.append(Spacer(1, 4))
                    step_content.append(Paragraph(f"<i>[Imagen no disponible en ruta: {ruta_real}]</i>", style_error))
                # Construcción de la Tarjeta del Paso
                t_step_card = Table([[step_content]], colWidths=[520])
                t_step_card.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ('LINEBEFORE', (0, 0), (0, -1), 3, COLOR_PURPLE),  # Borde acentuado morado
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(t_step_card)
                # story.append(t_step_card)
                story.append(Spacer(1, 8))
            # Barra de navegacion inferior
            story.append(Spacer(1, 4))
            story.append(
                HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"), spaceBefore=4, spaceAfter=8))
            btn_volver_indice = "<a href='#top_index' color='#4A1B82'><b>↑ Volver al Índice</b></a>"
            if idx < total_escenarios:
                siguiente_escenario_nombre = suite_results[idx]['test_name']
                if len(siguiente_escenario_nombre) > 28:
                    siguiente_escenario_nombre = siguiente_escenario_nombre[:25] + "..."
                btn_siguiente = f"<a href='#escenario_{idx + 1}' color='#4A1B82'><b>Ir al siguiente ({siguiente_escenario_nombre}) →</b></a>"
            else:
                btn_siguiente = "<font color='#888888'><i>Fin de los escenarios</i></font>"
            cell_left = Paragraph(btn_volver_indice, style_body)
            cell_right = Paragraph(btn_siguiente, ParagraphStyle('RNav', parent=style_body, alignment=2))
            t_nav = Table([[cell_left, cell_right]], colWidths=[200, 320])
            t_nav.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(t_nav)
            story.append(PageBreak())

        # Resumen final

        story.append(Paragraph("<b>RESUMEN GENERAL DE EJECUCIÓN</b>", style_h2_card))
        story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PURPLE, spaceAfter=15))
        passed_tests = sum(1 for r in suite_results if r['status'] == 'PASSED')
        failed_tests = total_escenarios - passed_tests
        rate = (passed_tests / total_escenarios * 100) if total_escenarios > 0 else 0
        style_right_cell = ParagraphStyle('RightCell', parent=styles['Normal'], fontSize=9, leading=12)
        resumen_data = [
            [Paragraph("<b>Métrica</b>", style_purple_left),
             Paragraph("<b>Resultado acumulado</b>", style_purple_left)],
            [Paragraph("Total de Escenarios Evaluados", style_body),
             Paragraph(str(total_escenarios), style_right_cell)],
            [Paragraph("Escenarios Exitosos (PASS)", style_body),
             Paragraph(f"<font color='#28A745'><b>{passed_tests}</b></font>", style_right_cell)],
            [Paragraph("Escenarios Fallidos (FAIL)", style_body),
             Paragraph(f"<font color='#DC3545'><b>{failed_tests}</b></font>", style_right_cell)],
            [Paragraph("Porcentaje Global de Éxito", style_body), Paragraph(f"<b>{rate:.1f}%</b>", style_right_cell)],
            [Paragraph("Tiempo Total Acumulado de Ejecución", style_body),
             Paragraph(f"<b>{tiempo_formateado_hms}</b>", style_right_cell)],
        ]
        t_resumen_final = Table(resumen_data, colWidths=[270, 270])
        t_resumen_final.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PURPLE),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_resumen_final)
        return story

    # Ejecucion de dos pasadas, sirve para poner todos los numeros de hojas y href
    doc_pass1 = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36,
                                  bottomMargin=36, compress=1)
    story_pass1 = construir_story(page_dict)
    doc_pass1.build(story_pass1, canvasmaker=NumberedCanvas)
    total_paginas = doc_pass1.page
    doc_pass2 = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36,
                                  bottomMargin=36, compress=1)
    story_pass2 = construir_story(page_dict)
    doc_pass2.build(
        story_pass2,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, total_pages=total_paginas, **kwargs)
    )


def dividir_en_lotes(lista, tam_lote=10, minimo_ultimo_lote=5):
    lotes = [lista[i:i + tam_lote]
        for i in range(0, len(lista), tam_lote)]
    if len(lotes) > 1 and len(lotes[-1]) < minimo_ultimo_lote:
        lotes[-2].extend(lotes[-1])
        lotes.pop()
    return lotes


def crear_grafico_pie(passed, failed):
    """Genera un gráfico vectorial de pastel con leyenda dinámica."""
    total = passed + failed
    d = Drawing(200, 95)
    # Configuración del gráfico de pastel
    pc = Pie()
    pc.x = 5
    pc.y = 5
    pc.width = 85
    pc.height = 85
    pc.data = [passed, failed] if total > 0 else [1, 0]
    pc.slices[0].fillColor = colors.HexColor("#28A745")  # Verde PASSED
    pc.slices[1].fillColor = colors.HexColor("#DC3545")  # Rojo FAILED
    pc.slices[0].strokeColor = colors.white
    pc.slices[1].strokeColor = colors.white
    pc.slices[0].strokeWidth = 1.5
    pc.slices[1].strokeWidth = 1.5
    # Porcentajes calculados
    pct_passed = (passed / total * 100) if total > 0 else 0
    pct_failed = (failed / total * 100) if total > 0 else 0
    # Leyenda lateral
    legend = Legend()
    legend.x = 100
    legend.y = 80
    legend.dx = 10
    legend.dy = 10
    legend.fontName = 'Helvetica-Bold'
    legend.fontSize = 8
    legend.boxAnchor = 'nw'
    legend.colorNamePairs = [
        (colors.HexColor("#28A745"), f' PASSED: {passed} ({pct_passed:.0f}%)'),
        (colors.HexColor("#DC3545"), f' FAILED: {failed} ({pct_failed:.0f}%)')
    ]
    d.add(pc)
    d.add(legend)
    return d


def generar_pdf_resumen(suite_results, ruta_salida):
    """Genera un PDF ultraligero con métricas, gráfico y tabla consolidada."""
    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
    styles = getSampleStyleSheet()
    COLOR_PURPLE = colors.HexColor("#4A1B82")
    COLOR_LIGHT_BG = colors.HexColor("#EFEFEF")
    COLOR_CARD_BG = colors.HexColor("#FAFAFA")
    style_purple_left = ParagraphStyle('PurpleLeftRes', parent=styles['Normal'], fontSize=9, leading=12,
                                       textColor=colors.white, fontName="Helvetica-Bold")
    style_gray_right = ParagraphStyle('GrayRightRes', parent=styles['Normal'], fontSize=9, leading=12,
                                      textColor=colors.HexColor("#222222"))
    style_h2_title = ParagraphStyle('H2TitleRes', parent=styles['Heading2'], fontSize=12, leading=15,
                                    textColor=COLOR_PURPLE, fontName="Helvetica-Bold")
    style_body = ParagraphStyle('BodyStyleRes', parent=styles['Normal'], fontSize=8, leading=11,
                                textColor=colors.HexColor("#374151"))
    style_error = ParagraphStyle('ErrorStyleRes', parent=styles['Normal'], fontSize=7.5, leading=10,
                                 textColor=colors.HexColor("#DC3545"))
    style_th = ParagraphStyle('THRes', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.white,
                              fontName="Helvetica-Bold")
    style_badge_passed = ParagraphStyle('BadgePassedR', parent=styles['Normal'], fontSize=7.5, leading=9,
                                        textColor=colors.HexColor("#155724"), fontName="Helvetica-Bold", alignment=1)
    style_badge_failed = ParagraphStyle('BadgeFailedR', parent=styles['Normal'], fontSize=7.5, leading=9,
                                        textColor=colors.HexColor("#721C24"), fontName="Helvetica-Bold", alignment=1)
    story = []
    # 1. Header con Logos
    img_left = obtener_imagen_base64(LOGO_BASE64, width=150, height=32)
    if not img_left:
        img_left = Paragraph("<b>QA_Automation</b>", style_h2_title)
    img_right = Image(RUTA_LOGO_DERECHA, width=90, height=90) if os.path.exists(RUTA_LOGO_DERECHA) else Paragraph("",
                                                                                                                  style_body)
    header_table = Table([[img_left, img_right]], colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    # 2. Métricas + Gráfico Pie (Dashboard)
    total_escenarios = len(suite_results)
    passed_tests = sum(1 for r in suite_results if r['status'] == 'PASSED')
    failed_tests = total_escenarios - passed_tests
    rate = (passed_tests / total_escenarios * 100) if total_escenarios > 0 else 0
    tiempo_total_segundos = sum(res.get('segundos_totales', 0) for res in suite_results)
    tiempo_formateado_hms = formatear_tiempo_hms(tiempo_total_segundos)
    fecha_actual_str = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p").lower()
    info_data = [
        [Paragraph("Tipo de Prueba", style_purple_left), Paragraph("Regresión (E2E) - Resumen", style_gray_right)],
        [Paragraph("Tiempo total", style_purple_left), Paragraph(tiempo_formateado_hms, style_gray_right)],
        [Paragraph("Total escenarios", style_purple_left), Paragraph(str(total_escenarios), style_gray_right)],
        [Paragraph("Efectividad", style_purple_left),
         Paragraph(f"<b>{rate:.1f}%</b> ({passed_tests}/{total_escenarios})", style_gray_right)],
        [Paragraph("Fecha ejecución", style_purple_left), Paragraph(fecha_actual_str, style_gray_right)],
    ]
    table_info = Table(info_data, colWidths=[120, 200])
    table_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_PURPLE),
        ('BACKGROUND', (1, 0), (1, -1), COLOR_LIGHT_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_PURPLE),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    chart_pie = crear_grafico_pie(passed_tests, failed_tests)
    top_dashboard = Table([[table_info, chart_pie]], colWidths=[330, 210])
    top_dashboard.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
    story.append(top_dashboard)
    story.append(Spacer(1, 10))
    # 3. Título de la Sección
    story.append(Paragraph("<b>RESUMEN DE PRUEBAS</b>", style_h2_title))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PURPLE, spaceBefore=2, spaceAfter=8))
    # 4. Tabla Consolidada (Matriz)
    matrix_data = [
        [
            Paragraph("<b>#</b>", style_th),
            Paragraph("<b>Escenario / Prueba</b>", style_th),
            Paragraph("<b>Estado</b>", style_th),
            Paragraph("<b>Duración</b>", style_th),
            Paragraph("<b>Observaciones / Error</b>", style_th)
        ]
    ]
    for idx, res in enumerate(suite_results, 1):
        is_passed = res['status'] == 'PASSED'
        color_badge_bg = colors.HexColor("#D4EDDA") if is_passed else colors.HexColor("#F8D7DA")
        color_accent = colors.HexColor("#28A745") if is_passed else colors.HexColor("#DC3545")
        style_b = style_badge_passed if is_passed else style_badge_failed
        badge_table = Table([[Paragraph(f"<b>{res['status']}</b>", style_b)]], colWidths=[55])
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), color_badge_bg),
            ('BOX', (0, 0), (-1, -1), 0.5, color_accent),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        obs_content = Paragraph("Efectuado correctamente", style_body) if is_passed else Paragraph(
            f"<b>Error:</b> {res.get('error_msg', 'N/A')}", style_error)
        matrix_data.append([
            Paragraph(str(idx), style_body),
            Paragraph(f"<b>{res['test_name']}</b>", style_body),
            badge_table,
            Paragraph(res.get('duracion', '--'), style_body),
            obs_content
        ])
    t_matrix = Table(matrix_data, colWidths=[20, 200, 65, 65, 190])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PURPLE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_CARD_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_matrix)
    # Compilación en 1 sola pasada (es ligero)
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36,
                            compress=1)
    doc.build(story, canvasmaker=NumberedCanvas)


from PIL import Image as PILImage


def optimizar_e_incluir_imagen(ruta_origen, width=460, height=258, max_dimension=1200, calidad=70):
    """Comprime y redimensiona una captura en memoria antes de meterla al PDF."""
    try:
        if not os.path.isfile(ruta_origen):
            return None
        with PILImage.open(ruta_origen) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.thumbnail((max_dimension, max_dimension), PILImage.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=calidad, optimize=True)
            buffer.seek(0)
            return Image(buffer, width=width, height=height)
    except Exception as e:
        print(f"Error optimizando imagen {ruta_origen}: {e}")
        return None


def restaura_insumo_return(dbms, user, password, host, port, service_name, query, nombre_log):
    """Establece conexiones síncronas a BD y formatea las filas devueltas como diccionarios nativos.

    A diferencia de los ejecutores DML puros, esta función inspecciona si la consulta tiene un
    conjunto de resultados (`cursor.description`). Si detecta columnas, procesa las filas mapeando
    los encabezados dinámicamente como llaves de un diccionario forzadas a minúsculas, resolviendo
    la diferencia en la lectura de tuplas planas entre los drivers de Oracle y SQL Server.

    Args:
        dbms (str): Identificador del motor de base de datos ('oracle' o 'sqlserver').
        user (str, optional): Nombre del usuario de conexión.
        password (str, optional): Contraseña de acceso.
        host (str): Dirección de red o IP del servidor.
        port (str, optional): Puerto de escucha del servicio.
        service_name (str): Instancia/SID (Oracle) o catálogo/base de datos (SQL Server).
        query (str): Sentencia SQL limpia enviada por el step para su ejecución física.
        nombre_log (str): Ruta o identificador del archivo log de la ejecución actual.

    Returns:
        Optional[list]: Una lista de diccionarios donde cada elemento representa una fila del set
            de datos con sus llaves en minúscula (ej. `[{"rowno": 1, "sin": "002"}]`), o `None` si la
            sentencia no arrojó registros.

    Raises:
        oracledb.Error: Ante fallos sintácticos, relacionales o de permisos en el conector de Oracle.
        Exception: Ante fallos en la cadena de conexión u operaciones del driver ODBC de SQL Server.
    """
    resultado = None
    try:
        if dbms == "oracle":
            try:
                oracledb.init_oracle_client(lib_dir=DIR_ORACLE)
                connection = oracledb.connect(user=user, password=password, host=host, port=port,
                                              service_name=service_name)

                # ---> CAMBIO: Configurar Oracle para devolver diccionarios (llaves en minúsculas)
                connection.rowfactory = lambda *args: dict(zip([d[0].lower() for d in cursor.description], args))
                cursor = connection.cursor()
                cursor.execute(query)

                if cursor.description:
                    resultado = cursor.fetchall()

                connection.commit()
                escribo_log(nombre_log, "---> Commit a: " + query + "\n")
                cursor.close()
                connection.close()
            except oracledb.Error as error:
                escribo_log(nombre_log, f"---> restaura_insumo() [oracle] str(error)=\n")
                raise

        elif dbms == "sqlserver":
            try:
                connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={service_name};Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=no;Connection Timeout=30;"

                escribo_log(nombre_log, "--->\tAbriendo conexion a bd...\n")
                connection = pyodbc.connect(connection_string)
                cursor = connection.cursor()

                escribo_log(nombre_log, "--->\tRestaurando insumo...\n")
                cursor.execute(query)

                if cursor.description:
                    # ---> CAMBIO: Mapeamos dinámicamente las columnas a un diccionario (llaves en minúsculas)
                    columnas = [columna[0].lower() for columna in cursor.description]
                    resultado = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

                cursor.commit()
                escribo_log(nombre_log, "--->    Commit a: " + query + "\n")
                cursor.close()

                escribo_log(nombre_log, "--->\tCerrando conexion a bd...\n")
                connection.close()
            except Exception as error:
                escribo_log(nombre_log, f"---> restaura_insumo() [sql_server] str(error)=\n")
                raise

        return resultado

    except Exception:
        raise
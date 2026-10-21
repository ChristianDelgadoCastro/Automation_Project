import logging
import os
import shutil
import time
import traceback
import zipfile
from datetime import date, datetime

# from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from playwright.sync_api import sync_playwright

from features.rollback_steps import RECOVERY_MAP
from librerias.directorios import XML_REGRESION, DIR_EVIDENCIAS
from librerias.funciones import (leer_hora, creo_log, encabezado_log, escribo_log, formatear_tiempo,
                                 generar_archivo_pdf, save_evidence, lista_screenshot, lista_pasos_descripcion,
                                 guardar_trace, guardar_video, existe_error_inesperado, validar_existe_xml,
                                 generar_pdf_consolidado_general, formatear_tiempo_hms, dividir_en_lotes,
                                 generar_pdf_resumen)
from modulos.login import logout_script_labs, logout_qa_practice, logout_dojo

headless = False


# Mapeo dinámico de funciones de logout por sitio
MAPA_LOGOUT = {
    'sl': logout_script_labs,
    'qapractice': logout_qa_practice,
    'dojo': logout_dojo
}


def before_all(context):
    """Se ejecuta una sola vez al inicio de toda la ejecución de Behavex"""
    context.playwright = sync_playwright().start()
    # Acumulador para el reporte general consolidado
    context.suite_results = []


def before_feature(context, feature):
    """Se ejecuta ANTES de cada Feature"""
    # Para extraer la matriz
    nombre_archivo = os.path.basename(feature.filename)
    context.matriz = nombre_archivo.replace('.feature', '')


def before_scenario(context, scenario):
    """Se ejecuta ANTES de cada Escenario"""
    if "Scraping" in scenario.tags:
        return

    context.inicio = time.time()
    # Variables de Entorno (Estas se manipulan desde el archivo run_behavex.py)
    context.linea_env = os.getenv("LINEA", "L1")
    context.headless = os.getenv("HEADLESS", "False").lower() == "true"
    context.pdf_general = os.getenv("PDF_GENERAL", "False").lower() == "true"

    # Definir el nombre del test basado en el nombre del escenario, por ejemplo:
    # "Ejecutar test_contrata_gpo_nomina"
    base_name = scenario.name.replace("Ejecutar ", "").strip()
    if context.linea_env == "L2":
        context.test_name = base_name.replace("test_", "test_l2_")
    else:
        context.test_name = base_name

    # Configuracion de Logs y Tiempos
    context.hora_ejecucion = leer_hora()
    context.nombre_log = creo_log(context.test_name, context.hora_ejecucion)
    encabezado_log(context.nombre_log, context.test_name, context.hora_ejecucion)

    context.sesiones_activas = {
        'sl': False,
        'qapractice': False,
        'dojo': False
    }

    # Listas globales para el PDF de este escenario
    context.lista_screenshot = []
    context.lista_pasos_descripcion = []

    # Configurar Playwright (Browser, Context y Page)
    context.browser = context.playwright.chromium.launch(headless=context.headless, slow_mo=0.3)
    context.context_pw = context.browser.new_context(
        ignore_https_errors=True, permissions=["geolocation"],
        geolocation={"latitude": 21.1664998, "longitude": -101.6922205},
        viewport={'width': 1920, 'height': 1080}, record_video_dir="videos",
        record_video_size={"width": 1920, "height": 1080}
    )
    context.context_pw.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.page = context.context_pw.new_page()


def after_scenario(context, scenario):
    """Se ejecuta siempre despeues de cada Escenario, sin importar si pasó o falló"""
    if "Scraping" in scenario.tags:
        return
    nombre_scenario = scenario.name.replace("Ejecutar ", "").strip()
    context.final = time.time()
    total_tiempo = context.final - context.inicio
    total_tiempo_segundos = context.final - context.inicio
    tiempo_segundos_formateado = formatear_tiempo_hms(total_tiempo_segundos)
    tiempo_formateado = formatear_tiempo(total_tiempo)
    # Variables iniciales para el XML y Rastreo
    rastreo_error = "Ejecución finalizada"
    estado_xml = "PASS"
    desc_xml = "Test Correcto"

    algun_paso_fallido = any(str(step.status) == "failed" or step.exception is not None for step in scenario.steps)
    escenario_fallido = (str(scenario.status) == "failed") or algun_paso_fallido

    if escenario_fallido:
        context.status = "FAILED"
        estado_xml = "FAIL"
        escribo_log(context.nombre_log, f"\n---> El escenario [{scenario.name}] FALLÓ.\n")

        # Capturamos el error "crudo" de Behave iterando los pasos
        error_crudo = ""
        for step in scenario.steps:
            if str(step.status) == "failed" or step.exception is not None:
                error_crudo = f"Paso fallido: '{step.name}'"
                if step.exception:
                    error_crudo += f" | Excepción: {str(step.exception).strip()}"
                break

        if not error_crudo and hasattr(scenario, 'error_message') and scenario.error_message:
            error_crudo = str(scenario.error_message).strip()

        # Prioridad a la función de error inesperado
        if hasattr(context, 'page') and context.page:
            try:
                existe_error_inesperado(context.page, error_crudo, context.test_name, context.nombre_log,
                                        context.hora_ejecucion)
            except Exception as error_definitivo:
                rastreo_error = str(error_definitivo).strip()
        else:
            rastreo_error = error_crudo or "Error desconocido en el escenario"

        desc_xml = rastreo_error

        if hasattr(context, 'page') and context.page:
            try:
                save_evidence(context.page, context.test_name, "PopUpError", context.hora_ejecucion)
                context.lista_screenshot.extend(lista_screenshot("PopUpError"))
                context.lista_pasos_descripcion.extend(lista_pasos_descripcion(f"Error: {rastreo_error}"))
            except Exception as ev_err:
                escribo_log(context.nombre_log, f"---> No se pudo guardar evidencia de error: {ev_err}\n")

        # Lógica de rollback / rescate si aplica...
        hay_sesion_activa = any(context.sesiones_activas.values())
        if nombre_scenario in RECOVERY_MAP:
            # Validamos si la sesión realmente llegó a iniciarse con éxito
            if hay_sesion_activa:
                escribo_log(context.nombre_log, f"\n" + "=" * 88 +
                            f"\n---> Aplicando el reestablecimiento de insumo para: '{nombre_scenario}'...\n"
                            + "=" * 88 + "\n")
                try:
                    # Ejecuta los pasos dinámicamente en el navegador
                    context.execute_steps(RECOVERY_MAP[nombre_scenario])
                    escribo_log(context.nombre_log, f"\n---> El entorno ha sido restablecido correctamente.\n")
                    if hasattr(context, 'page') and context.page:
                        save_evidence(context.page, context.test_name, "Rescato_Exitoso", context.hora_ejecucion)
                        context.lista_screenshot.extend(lista_screenshot("Rescato_Exitoso"))
                        context.lista_pasos_descripcion.extend(
                            lista_pasos_descripcion(
                                "TEST FAIL - Restablecimiento ejecutado: Entorno restaurado con éxito."))
                except Exception as error_rescate:
                    escribo_log(context.nombre_log,
                                f"---> No se pudo completar la restauración del entorno: {str(error_rescate)}\n")
                    if hasattr(context, 'page') and context.page:
                        save_evidence(context.page, context.test_name, "Error_En_Rescato", context.hora_ejecucion)
                        context.lista_screenshot.extend(lista_screenshot("Error_En_Rescato"))
                        context.lista_pasos_descripcion.extend(
                            lista_pasos_descripcion(
                                f"Incidencia durante la restauración. \nError: {str(error_rescate)}"))
            else:
                escribo_log(context.nombre_log,
                            f"---> Se omite el restablecimiento para '{nombre_scenario}' ya que la sesión no logró iniciar.\n")
        else:
            escribo_log(context.nombre_log,
                        f"---> No hay plan de rescate configurado para: '{nombre_scenario}'. Continuando...\n")
    else:
        context.status = "PASSED"
        escribo_log(context.nombre_log, "---> Testcase PASS\n")
        if hasattr(context, 'page') and context.page:
            save_evidence(context.page, context.test_name, "Test_correcto", context.hora_ejecucion)
            context.lista_screenshot.extend(lista_screenshot("Test_correcto"))
            context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Test correcto"))
    sesiones_cerradas = 0
    for sitio, esta_activa in context.sesiones_activas.items():
        if esta_activa:
            if hasattr(context, 'page') and context.page:
                try:
                    funcion_logout = MAPA_LOGOUT.get(sitio)
                    if funcion_logout:
                        escribo_log(context.nombre_log,
                                    f"---> Ejecutando logout automático para el sitio [{sitio}]...\n")
                        funcion_logout(context.page, context.nombre_log, context.hora_ejecucion)
                        context.sesiones_activas[sitio] = False
                        sesiones_cerradas += 1
                except Exception as logout_err:
                    escribo_log(context.nombre_log, f"---> No se pudo cerrar sesión en [{sitio}]: {logout_err}\n")

    if sesiones_cerradas == 0:
        escribo_log(context.nombre_log,
                    "---> Se omite el cierre de sesión automático (No había sesiones activas pendientes).\n")
    # Generar PDF
    path_pdf = None
    try:
        generar_archivo_pdf(context.lista_screenshot, context.lista_pasos_descripcion, context.test_name, ".pdf",
                            context.hora_ejecucion, tiempo_formateado)
        # Resolución dinámica de la ruta real del PDF
        fecha_hoy = date.today().strftime("%Y_%m_%d")
        nombre_pdf = f"env_{context.test_name}.pdf"
        candidatos = [
            # Ruta directa con subcarpeta 'cargado'
            os.path.join(DIR_EVIDENCIAS, fecha_hoy, context.test_name, "cargado", nombre_pdf),
            # Ruta con hora y subcarpeta 'cargado'
            os.path.join(DIR_EVIDENCIAS, fecha_hoy, context.hora_ejecucion, context.test_name, "cargado", nombre_pdf),
            # Ruta directa estándar
            os.path.join(DIR_EVIDENCIAS, fecha_hoy, context.test_name, nombre_pdf),
            # Ruta estándar con hora
            os.path.join(DIR_EVIDENCIAS, fecha_hoy, context.hora_ejecucion, context.test_name, nombre_pdf)
        ]
        # Seleccionar la primera ruta existente en disco
        for ruta in candidatos:
            if os.path.exists(ruta):
                path_pdf = ruta
                break
    except Exception as e:
        escribo_log(context.nombre_log, f"---> Error al generar PDF: {e}\n")

    # Actualizar XML de regresion
    try:
        case_id = getattr(context, 'test_case_id', None)
        validar_existe_xml(XML_REGRESION, '1', '1', '1', context.test_name, estado_xml, desc_xml,
                           f"{context.test_name}()", context.nombre_log,
                           path_evidencia=path_pdf, test_case_id=case_id)
    except Exception as e:
        escribo_log(context.nombre_log, f"---> Error actualizando XML: {e}\n")
    # Cerrar navegador y contexto
    ruta_video_origen = None
    ruta_trace_origen = f"trace_{context.test_name}_{context.hora_ejecucion}.zip"
    if hasattr(context, 'page') and context.page:
        try:
            ruta_video_origen = context.page.video.path()
        except Exception:
            pass
    if hasattr(context, 'context_pw') and context.context_pw:
        context.context_pw.tracing.stop(path=ruta_trace_origen)
        context.context_pw.close()
    if hasattr(context, 'browser') and context.browser:
        context.browser.close()
    # Mover evidencias
    evidence_path_safe = getattr(context, 'evidence_path', 'evidencias')
    if ruta_video_origen and os.path.exists(ruta_video_origen):
        try:
            nombre_video = f"Ejecucion_{context.test_name}.webm"
            ruta_destino_behavex = os.path.join(evidence_path_safe, nombre_video)
            os.makedirs(os.path.dirname(ruta_destino_behavex), exist_ok=True)
            shutil.copy(ruta_video_origen, ruta_destino_behavex)
        except Exception as e:
            logging.error(f"No se pudo inyectar el video a BehaveX: {e}")
    if os.path.exists(ruta_trace_origen):
        try:
            ruta_destino_trace = os.path.join(evidence_path_safe, ruta_trace_origen)
            os.makedirs(os.path.dirname(ruta_destino_trace), exist_ok=True)
            shutil.copy(ruta_trace_origen, ruta_destino_trace)
        except Exception as e:
            pass
        # Mover evidencias a carpetas locales
    try:
        guardar_trace(context.test_name, ruta_trace_origen, context.hora_ejecucion)
        if ruta_video_origen:
            guardar_video(context.test_name, ruta_video_origen, context.hora_ejecucion)
    except Exception as e:
        escribo_log(context.nombre_log, f"---> Error moviendo evidencias multimedia: {e}\n")
        # Guardamos los datos recolectados para el informe general
    if hasattr(context, 'suite_results'):
        context.suite_results.append({
            "test_name": context.test_name,
            "status": context.status,
            "duracion": tiempo_segundos_formateado,
            "segundos_totales": total_tiempo_segundos,
            "hora": context.hora_ejecucion,
            "error_msg": desc_xml if context.status == "FAILED" else "",
            "screenshots": list(getattr(context, 'lista_screenshot', [])),
            "pasos": list(getattr(context, 'lista_pasos_descripcion', []))
        })


def after_all(context):
    """Se ejecuta una sola vez al final de toda la ejecución"""
    if hasattr(context, 'playwright'):
        context.playwright.stop()

    generar_pdf = os.getenv("PDF_GENERAL", "False").lower() == "true"
    # Subida de PDF General ZIP al Run si está habilitado
    if generar_pdf and hasattr(context, 'suite_results') and context.suite_results:
        try:
            fecha_hoy = getattr(context, 'fecha', date.today().strftime("%Y_%m_%d"))
            hora_limpia = datetime.now().strftime("%H_%M_%S")
            carpeta_base = os.path.join(DIR_EVIDENCIAS, fecha_hoy, f"Reporte_General_{hora_limpia}")
            os.makedirs(carpeta_base, exist_ok=True)
            pdfs_generados = []
            # Generar el PDF resumen
            ruta_pdf_resumen = os.path.join(carpeta_base, f"00_Resumen_General_{hora_limpia}.pdf")
            generar_pdf_resumen(context.suite_results, ruta_pdf_resumen)
            pdfs_generados.append(ruta_pdf_resumen)
            print(f"PDF Resumen generado: {os.path.basename(ruta_pdf_resumen)}")
            # Generar los pdf de evidencias
            ESCENARIOS_POR_PDF = 10
            for numero_lote, lote in enumerate(dividir_en_lotes(context.suite_results, ESCENARIOS_POR_PDF), start=1):
                inicio = ((numero_lote - 1) * ESCENARIOS_POR_PDF) + 1
                fin = inicio + len(lote) - 1
                nombre_pdf = f"Reporte_Detallado_Parte_{numero_lote:02d}_Escenarios_{inicio:03d}_{fin:03d}.pdf"
                ruta_pdf_detallado = os.path.join(carpeta_base, nombre_pdf)
                logging.info(f"Generando PDF Detallado {numero_lote}: escenarios {inicio} al {fin}")
                generar_pdf_consolidado_general(lote, ruta_pdf_detallado)
                pdfs_generados.append(ruta_pdf_detallado)
            # Empaquetado
            ruta_zip = os.path.join(DIR_EVIDENCIAS, fecha_hoy, f"Reporte_General_Ejecucion_{hora_limpia}.zip")
            with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf in pdfs_generados:
                    zipf.write(pdf, arcname=os.path.basename(pdf))
            logging.info(f"ZIP generado correctamente: {ruta_zip}")

        except Exception:
            logging.error(traceback.format_exc())


def before_step(context, step):
    context.step_inicio = time.time()


def after_step(context, step):
    context.step_count = getattr(context, 'step_count', 0) + 1
    tiempo_step = time.time() - context.step_inicio
    duracion = step.duration if hasattr(step, 'duration') else 0.0
    logging.info(f"Terminó en: {duracion:.2f} segundos")

    if hasattr(context, "page"):
        try:
            context.page.locator("#ajaxloader").wait_for(state="hidden", timeout=45000)
        except Exception as e:
            escribo_log(context.nombre_log, f"---> El loader no se ocultó tras 45s: {e}")

    if tiempo_step > 5.0:
        escribo_log(context.nombre_log, f"")

    # Validación robusta del estatus del paso
    if str(step.status) == "failed" or step.exception is not None:
        error_real = str(step.exception) if step.exception else "Error desconocido"
        mensaje_fallo = f"\n[ERROR] El paso '{step.name}' falló:\n{error_real}"
        escribo_log(context.nombre_log, mensaje_fallo)
        print(mensaje_fallo)

    # Captura de pantalla para el behavex
    if hasattr(context, 'page') and context.page:
        try:
            nombre_limpio = "".join([c for c in step.name if c.isalnum() or c == ' ']).replace(" ", "_")[:60]
            estado = "FAIL" if (str(step.status) == "failed" or step.exception is not None) else "OK"
            nombre_foto = f"{estado}_{context.step_count:02d}_{nombre_limpio}.png"
            evidence_path_safe = getattr(context, 'evidence_path', 'evidencias')
            os.makedirs(evidence_path_safe, exist_ok=True)
            ruta_foto = os.path.join(evidence_path_safe, nombre_foto)
            context.page.screenshot(path=ruta_foto, full_page=True)
        except Exception as e:
            logging.error(f"No se pudo guardar la captura del paso: {e}")

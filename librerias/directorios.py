# *********************************************************************************************************************
#                                                   DIRECTORIOS
# *********************************************************************************************************************
import os
from pathlib import Path
# Este obtiene la ruta del usuario actual
USER_HOME = Path.home()

appdata = os.getenv('APPDATA')

#Directorio del proyecto y salidas dentro del usuario
DIR_PROYECT = USER_HOME / "Documents" / "Scripts" / "Automation_Project"
DIR_OUTPUT = USER_HOME / "output"

ALLURE_RESULTS_DIR = DIR_PROYECT / "Reportes" / "allure-results"
ALLURE_REPORT_DIR = DIR_PROYECT / "Reportes" / "allure-report"
DIR_ARCHIVOS = DIR_PROYECT / "archivos"
DIR_EVIDENCIAS = DIR_PROYECT / "evidencias"
DIR_EVIDENCIAS_PDF = DIR_PROYECT / "evidencias"
DIR_LOG = DIR_PROYECT / "Resultados_xml"
ARCHIVO_XML = DIR_LOG / "regresion.xml"
DIR_HORA_EJECUCION = DIR_LOG / "tiempo_ejecucion.txt"
DIR_STATUS_USR_LOG = DIR_LOG / "estatus_usuarios.txt"

DIR_DESCARGAS = USER_HOME / "Downloads"
RUTA_ARCHIVOS = Path(r"C:\Py_drivers\archivos")

# Logs de servicios dinámicos
DIR_LOGS_SERVICIOS = DIR_PROYECT / "logs_servicios"
DIR_LOGS_SERVICIOS_CSV = DIR_LOGS_SERVICIOS / "estatus_servicios.csv"

# Archivo de control
ARCHIVO_CONTROL = DIR_PROYECT / "Casos_Regresion.txt"

DIR_UTILERIAS = Path(r"C:\Py_drivers")
DIR_ORACLE = DIR_UTILERIAS / "util" / "instantclient_21_9"
DIR_AZURE_FLAG = DIR_UTILERIAS / "util" / "azure.flag"
DIR_AZURE_PROPERTIES = DIR_UTILERIAS / "util" / "temp.properties"

XML_REGRESION = 'Regresion Automatizada'


# *********************************************************************************************************************
#                                                       URLS
# *********************************************************************************************************************
URL_SCRIPT_LABS = "https://labs.hendri.me/"
URL_QA_PRACTICE = "https://www.qapractice.com/practice-login-form"
URL_UPEX_DOJO = "https://dojo.upexgalaxy.com/login"
XML_REGRESION_CORE = 'Regresion Automatizada'

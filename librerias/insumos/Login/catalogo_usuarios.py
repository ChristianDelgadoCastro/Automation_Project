from librerias.directorios import *
from librerias.insumos.Login.datos_test import *
from librerias.insumos.Login.datos_test_L2 import *

PERFILES_LOGIN = {
    "test_menu_contextual_inicio_persfis": {
        "usuario": (USUARIO_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "password": (CONTRASENA_MENU_CONTEXTUAL_INICIO_PERSFIS),
        # "token": (TOKEN, L2_TOKEN),
        "cta_vista": (CTA_VISTA_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "cta_vista_usd": (CTA_VISTA_USD_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "cta_vista_eur": (CTA_VISTA_EUR_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "cashback": (CASHBACK_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "inversiones_plazo": (INVERSIONES_PLAZO_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "mesa_de_dinero": (MESA_DINERO_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "mesa_de_dinero_num": (MESA_DINERO_MENU_CONTEXTUAL_INICIO_PERSFIS_TARJ),
        "fondo_inversion": (FONDO_INVERSION_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "inversiones_plazo_usd": (INVERSIONES_PLAZO_USD_MENU_CONTEXTUAL_INICIO_PERSFIS,),
        "inversiones_plazo_eur": (INVERSIONES_PLAZO_EUR_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "cta_tdc": (CTA_TDC_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "creditos": (CREDITOS_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "linea_credito": (LINEA_CREDITO_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "anticipo_nomina": (ANTICIPO_NOMINA_MENU_CONTEXTUAL_INICIO_PERSFIS),
        "anticipo_nomina_num": (ANTICIPO_NOMINA_MENU_CONTEXTUAL_INICIO_PERSFIS_TARJ),
        "linea_credito_usd": (LINEA_CREDITO_USD_MENU_CONTEXTUAL_INICIO_PERSFIS),
    },
    "test_login_scriptlabs": {
        "usuario": (STANDARD_USER_SCRIPTLABS, L2_ADMIN_USER_SCRIPTLABS),
        "password": (STANDARD_PASS_SCRIPTLABS, L2_ADMIN_PASS_SCRIPTLABS),
    },
    "test_login_qa_practice": {
        "usuario": (STANDARD_USER_QAPRACTICE, L2_STANDARD_USER_QAPRACTICE),
        "password": (STANDARD_PASS_QAPRACTICE, L2_STANDARD_PASS_QAPRACTICE),
    },
    "test_login_dojo": {
        "usuario": (STANDARD_USER_DOJO, L2_STANDARD_USER_DOJO),
        "password": (STANDARD_PASS_DOJO, L2_STANDARD_PASS_DOJO),
    }
}

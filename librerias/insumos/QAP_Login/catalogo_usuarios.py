from librerias.directorios import *
from librerias.insumos.QAP_Flight.datos_test import *
from librerias.insumos.QAP_Flight.datos_test_L2 import *

PERFILES_LOGIN = {
    "test_login_qa_practice": {
        "usuario": (STANDARD_USER_QAPRACTICE, L2_STANDARD_USER_QAPRACTICE),
        "password": (STANDARD_PASS_QAPRACTICE, L2_STANDARD_PASS_QAPRACTICE),
    },
    "test_login_qa_practice_datos_incorrectos": {
        "usuario": (STANDARD_USER_QAPRACTICE, L2_STANDARD_USER_QAPRACTICE),
        "password": ("error", "error"),
    },
    "test_login_qa_practice_datos_vacios": {
        "usuario": ("", ""),
        "password": ("", ""),
    },
    "test_login_qa_practice_pass_vacia": {
        "usuario": (STANDARD_USER_QAPRACTICE, L2_STANDARD_USER_QAPRACTICE),
        "password": ("", ""),
    }
}

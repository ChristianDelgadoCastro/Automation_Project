from librerias.insumos.datos_bd import *

PERFILES_BD = {
    "AUTHENTIC": {
        "usuario": (USUARIO_AUTHENTIC),
        "password": (PASS_AUTHENTIC),
        "host": (HOST_AUTHENTIC),
        "puerto": (PUERTO_AUTHENTIC),
        "servicio": (SERVICE_NAME_AUTHENTIC),
        "dbms": ("oracle", "oracle"),

    },
    "INTBANK": {
        "usuario": (USUARIO_INTBANK),
        "password": (PASS_INTBANK),
        "host": (HOST_INTBANK),
        "puerto": (PUERTO_INTBANK),
        "servicio": (SERVICE_NAME_INTBANK),
        "dbms": ("oracle", "oracle"),
    },
    "SQL_SERVER": {
        "usuario": (USUARIO_SQL),
        "password": (PASS_SQL),
        "host": (HOST_SQL),
        "servicio": (BD_SQL),
        "dbms": ("sqlserver", "sqlserver"),
    },
}

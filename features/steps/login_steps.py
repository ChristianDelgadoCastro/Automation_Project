from behave import step

from librerias.funciones import insumo_x_linea, escribo_log, save_evidence, lista_screenshot, \
    lista_pasos_descripcion
from modulos.base import obtener_catalogo_matriz
from modulos.login import login_script_labs, logout_script_labs, login_qa_practice, logout_qa_practice, login_dojo, \
    logout_dojo



@step('Realizar login con el perfil "{perfil}" en Script Labs')
def step_when_login(context, perfil):
    # Usamos el helper para traer los perfiles de la matriz actual
    perfiles_login = obtener_catalogo_matriz(context)
    # Validamos que el perfil exista
    if perfil not in perfiles_login:
        raise ValueError(f"El perfil '{perfil}' no existe en la matriz {context.matriz}.")
    # Asignamos los datos al contexto
    context.datos = perfiles_login[perfil]
    usuario_final = insumo_x_linea(context.linea_env, context.datos["usuario"][0], context.datos["usuario"][1])
    contrasena_final = insumo_x_linea(context.linea_env, context.datos["password"][0], context.datos["password"][1])

    escribo_log(context.nombre_log, f"---> Iniciando sesión para perfil [{perfil}] en línea [{context.linea_env}]\n")
    login_script_labs(context.nombre_log, context.page, usuario_final, contrasena_final, context.hora_ejecucion)
    # Esta bandera me sirve para que la funcion logout no se ejecute si ni siquiera se pudo iniciar sesion
    context.sesiones_activas['sl'] = True
    save_evidence(context.page, context.test_name, "Login_correcto", context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot("Login_correcto"))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Login correcto"))


@step('Cierro sesion en Script Labs')
def step_cerrar_sesion(context):
    logout_script_labs(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['sl'] = False


@step('Realizar login con el perfil "{perfil}" en QA Practice')
def step_when_login(context, perfil):
    perfiles_login = obtener_catalogo_matriz(context)
    # Validamos que el perfil exista
    if perfil not in perfiles_login:
        raise ValueError(f"El perfil '{perfil}' no existe en la matriz {context.matriz}.")
    # Asignamos los datos al contexto
    context.datos = perfiles_login[perfil]
    usuario_final = insumo_x_linea(context.linea_env, context.datos["usuario"][0], context.datos["usuario"][1])
    contrasena_final = insumo_x_linea(context.linea_env, context.datos["password"][0], context.datos["password"][1])

    escribo_log(context.nombre_log, f"---> Iniciando sesión para perfil [{perfil}] en línea [{context.linea_env}]\n")
    login_qa_practice(context.nombre_log, context.page, usuario_final, contrasena_final, context.hora_ejecucion)
    # Esta bandera me sirve para que la funcion logout no se ejecute si ni siquiera se pudo iniciar sesion
    context.sesiones_activas['qapractice'] = True
    save_evidence(context.page, context.test_name, "Login_correcto", context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot("Login_correcto"))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Login correcto"))


@step('Cierro sesion en QA Practice')
def step_cerrar_sesion(context):
    logout_qa_practice(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['qapractice'] = False


@step('Realizar login con el perfil "{perfil}" en UPEX Dojo')
def step_when_login(context, perfil):
    perfiles_login = obtener_catalogo_matriz(context)
    # Validamos que el perfil exista
    if perfil not in perfiles_login:
        raise ValueError(f"El perfil '{perfil}' no existe en la matriz {context.matriz}.")
    # Asignamos los datos al contexto
    context.datos = perfiles_login[perfil]
    usuario_final = insumo_x_linea(context.linea_env, context.datos["usuario"][0], context.datos["usuario"][1])
    contrasena_final = insumo_x_linea(context.linea_env, context.datos["password"][0], context.datos["password"][1])

    escribo_log(context.nombre_log, f"---> Iniciando sesión para perfil [{perfil}] en línea [{context.linea_env}]\n")
    login_dojo(context.nombre_log, context.page, usuario_final, contrasena_final, context.hora_ejecucion)
    # Esta bandera me sirve para que la funcion logout no se ejecute si ni siquiera se pudo iniciar sesion
    context.sesiones_activas['dojo'] = True
    save_evidence(context.page, context.test_name, "Login_correcto", context.hora_ejecucion)
    context.lista_screenshot.extend(lista_screenshot("Login_correcto"))
    context.lista_pasos_descripcion.extend(lista_pasos_descripcion("Login correcto"))


@step('Cierro sesion en UPEX Dojo')
def step_cerrar_sesion(context):
    logout_dojo(context.page, context.nombre_log, context.hora_ejecucion)
    context.sesiones_activas['dojo'] = False
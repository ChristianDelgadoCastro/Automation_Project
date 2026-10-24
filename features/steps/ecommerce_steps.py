from behave import step

from librerias.funciones import escribo_log, save_evidence, lista_screenshot, \
    lista_pasos_descripcion, existe_error_inesperado
from modulos.ecommerce import validar_catalogo_inicial, buscar_producto, validar_resultados_busqueda, \
    seleccionar_producto_listado, abrir_detalle_producto, validar_detalle_producto, agregar_al_carrito, \
    agregar_desde_listado, validar_carrito, llenar_direccion_envio, validar_sin_avanzar_a_pago, \
    validar_direccion_conservada, llenar_pago_ecommerce, agregar_producto_acumulado, validar_carrito_acumulado, \
    eliminar_del_carrito, validar_busqueda_sin_resultados, validar_sin_confirmar_pedido, registrar_alertas


@step('Valido que el catalogo cargue y el carrito este en cero')
def step_validar_catalogo_inicial_bdd(context):
    try:
        validar_catalogo_inicial(context.page, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> El catalogo cargo y el carrito esta en cero correctamente\n")
        texto_captura = "Catalogo inicial"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_catalogo_inicial_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_catalogo_inicial_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Busco el producto "{termino}"')
def step_buscar_producto_bdd(context, termino):
    try:
        context.ecom_termino = termino
        buscar_producto(context.page, termino, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se busco el producto en el catalogo correctamente\n")
        texto_captura = "Busco el producto"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_buscar_producto_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_buscar_producto_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que los resultados correspondan a la busqueda')
def step_validar_resultados_bdd(context):
    try:
        context.ecom_resultados = validar_resultados_busqueda(context.page, context.ecom_termino, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Los resultados corresponden a la busqueda correctamente\n")
        texto_captura = "Resultados de la busqueda"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_resultados_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_resultados_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Selecciono el producto numero {posicion:d} del listado')
def step_seleccionar_producto_bdd(context, posicion):
    try:
        context.ecom_producto = seleccionar_producto_listado(context.page, posicion, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se selecciono el producto del listado correctamente\n")
        texto_captura = "Selecciono el producto del listado"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_seleccionar_producto_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_seleccionar_producto_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Abro el detalle del producto seleccionado')
def step_abrir_detalle_bdd(context):
    try:
        abrir_detalle_producto(context.page, context.ecom_producto, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se abrio el detalle del producto correctamente\n")
        texto_captura = "Abro el detalle del producto"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_abrir_detalle_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_abrir_detalle_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que el detalle coincida con el producto seleccionado')
def step_validar_detalle_bdd(context):
    try:
        validar_detalle_producto(context.page, context.ecom_producto, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> El detalle coincide con el producto seleccionado correctamente\n")
        texto_captura = "Detalle del producto"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_detalle_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_detalle_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Agrego al carrito desde el detalle con cantidad {cantidad:d}')
def step_agregar_desde_detalle_bdd(context, cantidad):
    try:
        context.ecom_cantidad = cantidad
        agregar_al_carrito(context.page, context.ecom_producto, cantidad, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se agrego el producto al carrito desde el detalle correctamente\n")
        texto_captura = "Agrego al carrito desde el detalle"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_agregar_desde_detalle_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_agregar_desde_detalle_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Agrego al carrito desde el listado con cantidad {cantidad:d}')
def step_agregar_desde_listado_bdd(context, cantidad):
    try:
        context.ecom_cantidad = cantidad
        agregar_desde_listado(context.page, context.ecom_producto, cantidad, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se agrego el producto al carrito desde el listado correctamente\n")
        texto_captura = "Agrego al carrito desde el listado"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_agregar_desde_listado_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_agregar_desde_listado_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que el carrito refleje el producto, la cantidad y el total')
def step_validar_carrito_bdd(context):
    try:
        validar_carrito(context.page, context.ecom_producto, context.ecom_cantidad, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> El carrito refleja el producto, la cantidad y el total correctamente\n")
        texto_captura = "Carrito validado"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_carrito_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_carrito_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Ingreso los datos de la direccion de envio')
def step_llenar_direccion_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos para el paso 'Ingreso los datos de la direccion de envio'.")

        row = context.table[0]
        llenar_direccion_envio(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se ingresaron los datos de la direccion de envio correctamente\n")
        texto_captura = "Lleno la direccion de envio"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_direccion_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_direccion_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que no se avance a la pantalla de pago')
def step_validar_sin_avanzar_bdd(context):
    try:
        validar_sin_avanzar_a_pago(context.page, context.ecom_alertas, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> La aplicacion no avanzo a la pantalla de pago correctamente\n")
        texto_captura = "Direccion rechazada"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_sin_avanzar_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_sin_avanzar_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Valido que los datos de la direccion se conserven')
def step_validar_direccion_conservada_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos para el paso 'Valido que los datos de la direccion se conserven'.")

        row = context.table[0]
        validar_direccion_conservada(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Los datos de la direccion se conservaron correctamente\n")
        texto_captura = "Direccion conservada"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_direccion_conservada_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_direccion_conservada_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Ingreso los datos de pago del e-commerce')
def step_llenar_pago_ecommerce_bdd(context):
    try:
        if not hasattr(context, 'table') or not context.table:
            raise ValueError("No se encontró la tabla de datos para el paso 'Ingreso los datos de pago del e-commerce'.")

        row = context.table[0]
        llenar_pago_ecommerce(context.page, row, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se ingresaron los datos de pago correctamente\n")
        texto_captura = "Lleno los datos de pago"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_llenar_pago_ecommerce_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_llenar_pago_ecommerce_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Agrego al carrito el producto numero {posicion:d} del listado con cantidad {cantidad:d}')
def step_agregar_producto_acumulado_bdd(context, posicion, cantidad):
    try:
        if not hasattr(context, "ecom_carrito"):
            context.ecom_carrito = []
        producto = seleccionar_producto_listado(context.page, posicion, context.nombre_log, context.hora_ejecucion)
        agregar_producto_acumulado(context.page, producto, cantidad, context.ecom_carrito, context.nombre_log, context.hora_ejecucion)
        context.ecom_carrito.append({"producto": producto, "cantidad": cantidad})
 
        escribo_log(context.nombre_log, "---> Se sumo el producto al carrito correctamente\n")
        texto_captura = "Sumo producto al carrito"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_agregar_producto_acumulado_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_agregar_producto_acumulado_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
 
 
@step('Valido que el carrito refleje todos los productos agregados y el total')
def step_validar_carrito_acumulado_bdd(context):
    try:
        validar_carrito_acumulado(context.page, context.ecom_carrito, context.nombre_log, context.hora_ejecucion)
 
        escribo_log(context.nombre_log, "---> El carrito refleja todos los productos y el total correctamente\n")
        texto_captura = "Carrito con varios productos"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_carrito_acumulado_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_carrito_acumulado_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
 
 
@step('Elimino del carrito el producto agregado numero {posicion:d}')
def step_eliminar_del_carrito_bdd(context, posicion):
    try:
        item = context.ecom_carrito.pop(posicion - 1)
        eliminar_del_carrito(context.page, item["producto"], context.nombre_log, context.hora_ejecucion)
 
        escribo_log(context.nombre_log, "---> Se elimino el producto del carrito correctamente\n")
        texto_captura = "Elimino producto del carrito"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_eliminar_del_carrito_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_eliminar_del_carrito_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
 
 
@step('Valido que la busqueda no tenga resultados')
def step_validar_busqueda_sin_resultados_bdd(context):
    try:
        validar_busqueda_sin_resultados(context.page, context.ecom_termino, context.nombre_log, context.hora_ejecucion)
 
        escribo_log(context.nombre_log, "---> La busqueda no devolvio resultados correctamente\n")
        texto_captura = "Busqueda sin resultados"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_busqueda_sin_resultados_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_busqueda_sin_resultados_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
 
 
@step('Valido que el pedido no se confirme')
def step_validar_sin_confirmar_pedido_bdd(context):
    try:
        validar_sin_confirmar_pedido(context.page, context.nombre_log, context.hora_ejecucion)
 
        escribo_log(context.nombre_log, "---> El pedido no se confirmo, como se esperaba\n")
        texto_captura = "Pedido no confirmado"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_validar_sin_confirmar_pedido_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_validar_sin_confirmar_pedido_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise


@step('Activo la captura de alertas del navegador')
def step_registrar_alertas_bdd(context):
    try:
        context.ecom_alertas = []
        registrar_alertas(context.page, context.ecom_alertas, context.nombre_log, context.hora_ejecucion)

        escribo_log(context.nombre_log, "---> Se activo la captura de alertas correctamente\n")
        texto_captura = "Activo captura de alertas"
        save_evidence(context.page, context.test_name, texto_captura, context.hora_ejecucion)
        context.lista_screenshot.extend(lista_screenshot(texto_captura))
        context.lista_pasos_descripcion.extend(lista_pasos_descripcion(texto_captura))
    except Exception as err:
        escribo_log(context.nombre_log, "---> step_registrar_alertas_bdd() " + f"err={type(err).__name__} {str(err)}\n")
        rastreo = f"err={type(err).__name__}" + f" [step_registrar_alertas_bdd] {str(err)}"
        existe_error_inesperado(context.page, rastreo, context.test_name, context.nombre_log, context.hora_ejecucion)
        raise
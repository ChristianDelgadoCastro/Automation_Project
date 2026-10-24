# Diccionario centralizado de planes de 'contingencia'
# Llave: Nombre exacto del escenario en el archivo .feature
# Valor: Los pasos Gherkin en texto que Behavex ejecutara en el navegador si el test falla

RECOVERY_MAP = {
    "test_login_scriptlabs": """
    Estos son de ejemplo:
        When Navego al menu "Todos mis productos" y selecciono "Todos mis Productos"
          And Quito de favoritos todas las cuentas
    """,
}
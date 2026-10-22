@automated @Qa_Practice @ecommerce_scenarios
#noinspection CucumberUndefinedStep
Feature: E-commerce

  @test @test_ecom_compra_busqueda_detalle @positivo
  Scenario: Ejecutar test_ecom_compra_busqueda_detalle
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
    Then Busco el producto "Mouse"
      And Valido que los resultados correspondan a la busqueda
      And Selecciono el producto numero 1 del listado
    Then Abro el detalle del producto seleccionado
      And Valido que el detalle coincida con el producto seleccionado
      And Agrego al carrito desde el detalle con cantidad 2
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje el producto, la cantidad y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Ingreso los datos de la direccion de envio
      | nombre | calle           | ciudad | estado | zip   |
      | Ana QA | 123 Main Street | Austin | TX     | 73301 |
      And Doy click en el boton "Guardar Direccion y Continuar"
    Then Ingreso los datos de pago del e-commerce
      | numero_tarjeta      | expiracion | cvv |
      | 4111 1111 1111 1111 | 12/30      | 123 |
      And Doy click en el boton "Comprar Ahora"
      And Valido que el titulo diga "Order Successful!"


  @test @test_ecom_busqueda_sin_resultados @negativo
  Scenario: Ejecutar test_ecom_busqueda_sin_resultados
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
    Then Busco el producto "Xyz123"
      And Valido que la busqueda no tenga resultados


  @test @test_ecom_direccion_campos_vacios @negativo
  Scenario: Ejecutar test_ecom_direccion_campos_vacios
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
      And Activo la captura de alertas del navegador
    Then Selecciono el producto numero 3 del listado
      And Agrego al carrito desde el listado con cantidad 2
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje el producto, la cantidad y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Doy click en el boton "Guardar Direccion y Continuar"
      And Valido que no se avance a la pantalla de pago


  @test @test_ecom_direccion_incompleta @negativo
  Scenario: Ejecutar test_ecom_direccion_incompleta
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
      And Activo la captura de alertas del navegador
    Then Selecciono el producto numero 3 del listado
      And Agrego al carrito desde el listado con cantidad 2
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje el producto, la cantidad y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Ingreso los datos de la direccion de envio
      | nombre | calle       | ciudad | estado | zip      |
      | Ana QA | [omitir]    | Austin | TX     | [omitir] |
      And Doy click en el boton "Guardar Direccion y Continuar"
      And Valido que no se avance a la pantalla de pago


  @test @test_ecom_varios_productos_quitar_uno @positivo
  Scenario: Ejecutar test_ecom_varios_productos_quitar_uno
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
    Then Agrego al carrito el producto numero 1 del listado con cantidad 2
      And Agrego al carrito el producto numero 2 del listado con cantidad 3
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje todos los productos agregados y el total
    Then Elimino del carrito el producto agregado numero 1
      And Valido que el carrito refleje todos los productos agregados y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Ingreso los datos de la direccion de envio
      | nombre | calle           | ciudad | estado | zip   |
      | Ana QA | 123 Main Street | Austin | TX     | 73301 |
      And Doy click en el boton "Guardar Direccion y Continuar"
    Then Ingreso los datos de pago del e-commerce
      | numero_tarjeta      | expiracion | cvv |
      | 4111 1111 1111 1111 | 12/30      | 123 |
      And Doy click en el boton "Comprar Ahora"
      And Valido que el titulo diga "Order Successful!"


    @test @test_ecom_pago_campos_vacios @negativo
  Scenario: Ejecutar test_ecom_pago_incompleto_campos_vacios
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
    Then Selecciono el producto numero 1 del listado
      And Agrego al carrito desde el listado con cantidad 1
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje el producto, la cantidad y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Ingreso los datos de la direccion de envio
      | nombre | calle           | ciudad | estado | zip   |
      | Ana QA | 123 Main Street | Austin | TX     | 73301 |
      And Doy click en el boton "Guardar Direccion y Continuar"
    Then Doy click en el boton "Comprar Ahora"
      And Valido que el pedido no se confirme


  @test @test_ecom_pago_incompleto @negativo
  Scenario: Ejecutar test_ecom_pago_incompleto
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "E-comerce Automation"
      And Valido que el catalogo cargue y el carrito este en cero
    Then Selecciono el producto numero 1 del listado
      And Agrego al carrito desde el listado con cantidad 1
    Then Doy click en el boton "Carrito"
      And Valido que el carrito refleje el producto, la cantidad y el total
      And Doy click en el boton "Proceder a Comprar"
    Then Ingreso los datos de la direccion de envio
      | nombre | calle           | ciudad | estado | zip   |
      | Ana QA | 123 Main Street | Austin | TX     | 73301 |
      And Doy click en el boton "Guardar Direccion y Continuar"
    Then Ingreso los datos de pago del e-commerce
      | numero_tarjeta      | expiracion | cvv      |
      | 4111 1111 1111 1111 | 12/30      | [omitir] |
      And Doy click en el boton "Comprar Ahora"
      And Valido que el pedido no se confirme

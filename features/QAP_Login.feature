@automated @Qa_Practice @login_scenarios
#noinspection CucumberUndefinedStep
Feature: Login

  @test @test_login_qa_practice_datos_correctos @positivo
  Scenario: Ejecutar test_login_qa_practice_datos_correctos
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Valido que el titulo diga "Login Successful! Welcome to Premium Banking."

  @test @test_login_qa_practice_datos_incorrectos @negativo
  Scenario: Ejecutar test_login_qa_practice_datos_incorrectos
    Given Realizar login con el perfil "test_login_qa_practice_datos_incorrectos" en QA Practice
    Then Valido que el titulo diga "Invalid email id and password"

  @test @test_login_qa_practice_datos_vacios @negativo
  Scenario: Ejecutar test_login_qa_practice_datos_vacios
    Given Realizar login con el perfil "test_login_qa_practice_datos_vacios" en QA Practice
    Then Valido que el titulo diga "Email and Password are required"

  @test @test_login_qa_practice_pass_vacia @negativo
  Scenario: Ejecutar test_login_qa_practice_pass_vacia
    Given Realizar login con el perfil "test_login_qa_practice_pass_vacia" en QA Practice
    Then Valido que el titulo diga "Password is required"


  @test @test_login_qa_practice_crear_cuenta @positivo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | email              | password | password2 |
      | qaprueba@email.com | Pass123! | Pass123!  |
      And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Registration Successful"


  @test @test_login_qa_practice_crear_cuenta_email_vacio @negativo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta_email_vacio
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | password | password2 |
      | Pass123! | Pass123!  |
      And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Email is required"


  @test @test_login_qa_practice_crear_cuenta_password_vacio @negativo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta_password_vacio
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | email              |
      | qaprueba@email.com |
      And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Password is required"


  @test @test_login_qa_practice_crear_cuenta_password2_vacio @negativo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta_password2_vacio
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | email              | password |
      | qaprueba@email.com | Pass123! |
    And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Please confirm your password"


  @test @test_login_qa_practice_crear_cuenta_contraseñas_diferentes @negativo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta_contraseñas_diferentes
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | email              | password | password2 |
      | qaprueba@email.com | Pass123! | Pass123   |
    And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Passwords do not match"


  @test @test_login_qa_practice_crear_cuenta_contraseñas_debil @negativo
  Scenario: Ejecutar test_login_qa_practice_crear_cuenta_contraseñas_debil
    Given Abro la pagina de "Qa Practice"
    Then Doy click en el boton "registrar ahora qap"
    Then Lleno el formulario de registro con los siguientes datos
      | email              | password | password2 |
      | qaprueba@email.com | Pass     | Pass      |
    And Doy click en el boton "registrar qap"
    Then Valido que el titulo diga "Password does not meet the requirements"




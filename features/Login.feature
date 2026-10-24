@automated @login
#noinspection CucumberUndefinedStep
Feature: Login

  @test @test_login_scriptlabs
  Scenario: Ejecutar test_login_scriptlabs
    Given Realizar login con el perfil "test_login_scriptlabs" en Script Labs


  @test @test_login_qa_practice
  Scenario: Ejecutar test_login_qa_practice
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice

  @test @test_login_dojo
  Scenario: Ejecutar test_login_dojo
    Given Realizar login con el perfil "test_login_dojo" en UPEX Dojo

  @test @test_compra_scriptlabs
  Scenario: Ejecutar test_compra_scriptlabs
    When Realizo el flujo de compra del producto "Selenium" en Script Labs

  @test @test_crud_scriptlabs
  Scenario: Ejecutar test_crud_scriptlabs
    When Realizo el flujo CRUD de scripts en Script Labs

  @test @test_admin_scriptlabs
  Scenario: Ejecutar test_admin_scriptlabs
    When Realizo el flujo de compra como administrador en Script Labs
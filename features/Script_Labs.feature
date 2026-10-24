@automated @ScriptLabs
#noinspection CucumberUndefinedStep
Feature: ScriptLabs

    @test @test_compra_scriptlabs @positivo
  Scenario: Ejecutar test_compra_scriptlabs
    When Realizo el flujo de compra del producto "Selenium" en Script Labs

  @test @test_crud_scriptlabs @positivo
  Scenario: Ejecutar test_crud_scriptlabs
    When Realizo el flujo CRUD de scripts en Script Labs

  @test @test_admin_scriptlabs @positivo
  Scenario: Ejecutar test_admin_scriptlabs
    When Realizo el flujo de compra como administrador en Script Labs
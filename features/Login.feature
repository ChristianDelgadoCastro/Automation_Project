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

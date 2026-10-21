@automated @Qa_Practice @flight_booking_scenarios
#noinspection CucumberUndefinedStep
Feature: Flight Booking

  @test @test_reservar_vuelo @positivo
  Scenario: Ejecutar test_reservar_vuelo
    Given Realizar login con el perfil "test_login_qa_practice" en QA Practice
    Then Navego al menu "Practice Sites"
      And Selecciono la actividad de practica "Flight Booking Automation"
    Then Lleno el formulario de reserva de vuelos con los siguientes datos
      | from     | to      | departure_date | return_date | passengers | class    | one_way |
      | New York | London  | 2026-06-15     | 2026-06-30  | 2          | Business | false   |
      And Doy click en el boton "Buscar vuelos"
      And Capturo evidencia con leyenda "Vuelos encontrados"
    Then Aplico los siguientes filtros en la busqueda de vuelos
      | sort_by           | airline           | non_stop |
      | Price: Low to High| Sky High Airlines | true     |
    Then Selecciono los vuelos deseados
      | trayecto | aerolinea         | codigo |
      | salida   | Sky High Airlines | SH137  |
      | regreso  | Sky High Airlines | SH237  |
      And Doy click en el boton "Continuar a Detalles de Pasajeros"
    Then Lleno los datos del pasajero con la siguiente informacion
    | nombre        | email              | telefono   |
    | Juan Pérez    | juan.perez@test.com| 5551234567 |
      And Doy click en el boton "Continuar a Pago"
    Then Lleno el formulario de pago con los siguientes datos
      | numero_tarjeta   | expiracion | cvv |
      | 4532111122223333 | 12/28      | 123 |
      And Doy click en el boton "Pagar y Continuar Reservacion"
      And Valido que el titulo diga "Booking Confirmed!"
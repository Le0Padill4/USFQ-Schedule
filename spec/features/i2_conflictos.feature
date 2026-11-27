Feature: Cruces entre reuniones semanales sintéticas
  Scenario: clases consecutivas
    Given dos reuniones el mismo día donde una termina al empezar la otra
    Then no existe cruce entre ellas
  Scenario: clases solapadas
    Given dos reuniones el mismo día con minutos comunes
    Then existe cruce entre ellas
  Scenario: horario ausente
    Given un horario sin reuniones conocidas
    Then el detector no encuentra cruces, pero no certifica que el horario sea válido

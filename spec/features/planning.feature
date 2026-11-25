Feature: Planificación de horarios
  Scenario: Bloquear materia con prerrequisito pendiente
    Given una malla con una materia que requiere otra
    And el estudiante no tiene aprobada la materia previa
    When consulta las materias habilitadas
    Then la materia dependiente no aparece como habilitada

  Scenario: Evitar cruces entre secciones
    Given dos ofertas con reuniones que se superponen
    When el estudiante genera horarios
    Then ningún horario contiene ambas ofertas

  Scenario: Respetar preferencias
    Given ofertas válidas y una preferencia de días libres
    When solicita horarios ordenados
    Then cada horario cumple restricciones duras
    And el ranking explica cómo influyó la preferencia

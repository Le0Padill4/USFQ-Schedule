Feature: Selección de carrera del MVP
  Scenario: listar carreras disponibles
    When el cliente consulta GET /api/v1/careers
    Then recibe únicamente las carreras 1CMP y 1MAC

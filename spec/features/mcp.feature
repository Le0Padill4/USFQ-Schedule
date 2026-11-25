Feature: Consulta MCP de oferta académica
  Scenario: Consultar materias por código
    Given el servidor MCP tiene conexión de solo lectura a datos sintéticos
    When un agente consulta una materia por código
    Then recibe solo campos permitidos y el origen del registro
    And la base de datos no cambia

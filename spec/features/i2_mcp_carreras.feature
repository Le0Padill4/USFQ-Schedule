Feature: Consulta MCP de carreras del MVP
  Scenario: lista de herramientas y consulta de carreras
    Given un cliente MCP conectado por stdio
    When consulta las herramientas disponibles y ejecuta list_careers
    Then recibe únicamente 1CMP y 1MAC y no dispone de herramientas de sincronización

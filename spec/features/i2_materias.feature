Feature: Índice por código de materia
  Scenario: búsqueda ordenada
    Given materias sintéticas con códigos únicos
    When se consultan los códigos en un rango inclusivo
    Then se devuelven en orden lexicográfico
  Scenario: clave duplicada
    When se agrega una materia con código ya presente
    Then se rechaza el duplicado y se conserva el valor anterior

Feature: Identificación de una oferta por período y NRC
  Scenario: Mismo NRC en períodos distintos
    Given dos ofertas sintéticas con el mismo NRC en períodos diferentes
    Then el índice conserva y permite buscar cada oferta por separado
  Scenario: NRC repetido dentro de un período
    When se agrega una segunda oferta con el mismo período y NRC
    Then se rechaza el duplicado y se conserva la oferta anterior

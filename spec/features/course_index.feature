Feature: Índice ordenado de materias y ofertas
  Scenario: búsqueda exacta y reemplazo de una clave
    Given un índice vacío de claves únicas
    When inserto dos valores con la misma clave
    Then el índice conserva el valor más reciente y cuenta una clave
  Scenario: búsqueda por rango inclusivo
    Given varias claves ordenables
    When consulto un rango válido
    Then obtengo las claves del rango en orden, incluidos sus extremos
  Scenario: eliminación y ausencia
    When elimino una clave existente
    Then ya no se puede consultar y el árbol conserva sus invariantes AVL
    And eliminar o consultar una clave ausente informa KeyError

Feature: Grafo curricular del Integrante 1
  # Fixtures sintéticos. No expresa reglas verificadas de una malla real.
  Scenario: Habilitar únicamente materias con reglas completas
    Given las materias sintéticas A, B y C
    And las reglas de A y B están completas y A es prerrequisito de B
    And los requisitos de C son desconocidos
    When consulto las habilitadas con A aprobada
    Then recibo únicamente B
    And C permanece bloqueada por información desconocida

  Scenario: Exigir todos los prerrequisitos del contrato vigente
    Given A y B son prerrequisitos de C con reglas completas
    When consulto las habilitadas con solo A aprobada
    Then C no está habilitada

  Scenario: Rechazar ciclos sin modificar el grafo
    Given A es prerrequisito de B y B de C
    When intento añadir C como prerrequisito de A
    Then recibo el error CYCLE
    And se conservan las aristas y grados anteriores

  Scenario: Mantener recorridos reproducibles
    Given un grafo con componentes desconectados y materias aisladas
    When consulto BFS, DFS, dependencias y orden topológico
    Then los resultados son deterministas independientemente del orden de inserción
    And cada prerrequisito aparece antes que su dependiente en la topología

  Scenario: No habilitar automáticamente al eliminar un requisito
    Given A es prerrequisito de B con reglas completas
    When elimino A o elimino la relación A B
    Then las reglas de B quedan desconocidas hasta confirmación explícita

  Scenario: Validar entradas y proteger las consultas
    Given un grafo válido
    When recibo un código vacío, desconocido o duplicado
    Then devuelvo un error explícito según la operación
    And ninguna operación fallida altera el estado

  Scenario: Comparar mi módulo con una referencia independiente
    Given una semilla fija y un motor de referencia basado en listas
    When ejecuto 10000 operaciones sintéticas incluyendo errores y cambios
    Then comparo cada respuesta y estado observable
    And verifico los invariantes del grafo después de cada operación
    # Este escenario solo verifica el grafo; no sustituye el diferencial global de I3.

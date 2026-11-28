Característica: Selección inicial de materias habilitadas
  Escenario: Solo se recuperan registros habilitados con reglas conocidas
    Dadas materias sintéticas con requisitos AND y un índice por código
    Cuando se consultan las materias habilitadas con una materia aprobada
    Entonces se obtienen sus registros en orden de código
    Y se excluyen las materias con requisitos desconocidos

  Escenario: Un registro habilitado falta en el índice
    Dado un grafo con una materia habilitada ausente del índice
    Cuando se consultan los registros habilitados
    Entonces se informa un error sin mutar las estructuras

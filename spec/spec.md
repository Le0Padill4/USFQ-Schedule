# Especificación del producto

## Problema y usuario
Un estudiante necesita saber qué materias puede tomar y combinar NRC/paralelos sin violar prerrequisitos ni horarios.

## MVP
Cuenta de demostración; carrera y malla; materias aprobadas; consulta de oferta académica permitida; materias habilitadas; generación de horarios según restricciones/preferencias; explicación del resultado. Datos sintéticos hasta autorización de la fuente.

## Requisitos

- R1: autenticar y asociar materias aprobadas a un usuario de demostración.
- R2: mostrar malla y prerrequisitos por carrera.
- R3: no ofrecer una materia cuyo prerrequisito no esté aprobado.
- R4: obtener NRC/profesor/horario solo de fuente registrada o fixture identificado.
- R5: no generar horarios con reuniones superpuestas.
- R6: ordenar resultados según preferencias declaradas y explicar el puntaje.
- R7: MCP responde consultas académicas permitidas con acceso de solo lectura.
- R8: CI verifica lint, pruebas y build; release final documenta límites.

Criterios verificables y BDD están en `spec/features/`. Toda ampliación del MVP necesita aceptación en PR.

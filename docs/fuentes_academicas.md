# Fuentes académicas y oferta — investigación inicial I2

Consulta: 25 de noviembre de 2026 (hora de Ecuador). Este documento registra
observaciones, no autoriza recolección automatizada ni afirma que los datos
obtenidos sean completos. El MVP solo permite elegir las carreras 1CMP y 1MAC;
las materias compartidas, Colegio General, inglés, laboratorios, ejercicios,
optativas y electivas se incluyen según reglas verificadas, no por prefijo.

## Mallas oficiales

| Fuente | Observado | SHA-256 del HTML recibido |
| --- | --- | --- |
| [1CMP digital](https://wsexternal.usfq.edu.ec/MallaCurricular-USFQ/DetalleMallaCurricular/DetalleMalla?codigoCarrera=1CMP) | 9 semestres, 142 créditos | `b734ab3b4d53e4bf8ff43ccc656f107299b095e0cce250f374a97ee4d5d12fe0` |
| [1MAC digital](https://wsexternal.usfq.edu.ec/MallaCurricular-USFQ/DetalleMallaCurricular/DetalleMalla?codigoCarrera=1MAC&out=1) | 9 semestres y 1 verano, 139 créditos | `b37e1851753c41657ebb5a8b7178e81c342abfe966cdfcbe06b92f2990746a06` |

Los hashes identifican las respuestas HTML de la consulta, no una versión
oficial ni un archivo preservado. Ambas páginas muestran códigos, nombres,
créditos y semestres sugeridos, y advierten que la malla está sujeta a cambios.
Ambas muestran materias como ESP 1001 y MAT 1201. El HTML incluye controles de
prerrequisitos y descripción para materias; el contenido y semántica de esos
controles aún no se han verificado de forma completa. Una arista ausente no
debe interpretarse como ausencia de requisitos.

Contrastes disponibles: [PDF de bloques 1CMP](https://www.usfq.edu.ec/sites/default/files/2026-05/malla_de_bloques_ingenieria_en_ciencias_de_la_computacion_06052026.pdf),
[PDF de bloques 1MAC](https://www.usfq.edu.ec/sites/default/files/2026-01/malla_de_bloques_ingenieria_en_matematicas_aplicadas_y_computacion.pdf),
[página 1CMP](https://www.usfq.edu.ec/es/oferta-academica/pregrado/ingenieria-en-ciencias-de-la-computacion) y
[página 1MAC](https://www.usfq.edu.ec/es/oferta-academica/pregrado/ingenieria-en-matematicas-aplicadas-y-computacion-mac).
Los PDF identifican secciones de ejercicios y laboratorios; queda pendiente una
comparación detallada de versiones, requisitos de graduación, optativas,
correquisitos, alternativas y notas mínimas. No se ha aprobado importar reglas.

## Catálogo de oferta

[Formulario de oferta](https://catalogodecursos.usfq.edu.ec/dashboard/home):
redirige a inicio de sesión institucional Microsoft; el usuario ingresó por su
cuenta para una inspección puntual de la interfaz. La página permite filtrar
por periodo, colegio, área, campus, sesión, días, hora, texto, inglés, writing
intensive y cupos disponibles. Los resultados observados están paginados y la
vista ofrece tamaños de página. La búsqueda `3002` en el periodo seleccionado
`202610` devolvió 79 resultados, incluyendo múltiples paralelos de ADM-3002.
Esto es una observación puntual de la UI, no una muestra persistida de datos
oficiales ni una inferencia sobre elegibilidad.

Los campos visibles incluyen código, NRC, nombre, paralelo, lugar, sesión,
horario (días, horas y fechas), docente, créditos, colegio, cupos, inscritos y
restricciones. Se observaron modalidades presencial y en línea; un resultado en
línea mostraba `0000–0001` sin días, cuyo significado es desconocido. No se ha
comprobado cómo se vinculan laboratorios/ejercicios, la fecha de actualización
ni si todo campo aparece siempre. El NRC debe tratarse junto con su periodo.

No se han verificado términos de uso, límites ni autorización institucional para
automatizar o redistribuir los resultados. Tampoco se ha identificado API o
exportación oficial autorizada. No se han extraído cookies ni credenciales, ni
se ha realizado scraping; la accesibilidad visual no equivale a permiso para
automatizar. No se debe implementar un scraper específico hasta documentar
permisos y presentar y aprobar el plan de extracción correspondiente.

## Plan pendiente de validación

1. Completar inspección de filtros, paginación, datos vinculados y una muestra
   mínima autorizada; comprobar términos, límites y vía oficial disponible.
2. Determinar reglas de pertenencia y opciones elegibles para las dos mallas sin
   filtrar solamente por CMP/MAC ni descargar indiscriminadamente el catálogo.
3. Si se autoriza automatización, proponer una fuente concreta, mapeo y pruebas;
   deduplicar por periodo/NRC, preservar reuniones y origen, validar antes de
   publicar, limitar solicitudes, usar reintentos acotados y conservar la última
   versión válida si falla la actualización. Definir cadencia con el equipo.
4. Si no existe permiso, usar importación de archivo oficial autorizado o
   fixtures sintéticos rotulados. Separar importación de mallas y oferta;
   herramientas MCP de sincronización requieren acuerdo con el contrato actual,
   que establece lectura únicamente.

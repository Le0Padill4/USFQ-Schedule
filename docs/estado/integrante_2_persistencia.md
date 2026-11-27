# Propuesta de persistencia y aislamiento — I2

Estado: borrador para revisión de I1/I3. No modifica los contratos vigentes ni
crea migraciones. Las relaciones, nombres y restricciones exactas pueden cambiar
tras revisar las reglas académicas y las interfaces de cada integrante.

## Datos académicos

- `career`: id estable restringido a `1CMP` o `1MAC` para el MVP.
- `curriculum_version`: carrera, identificador de versión, fuente, fecha de
  consulta y referencia a evidencia; conservar versiones históricas.
- `course`: identificador/código y nombre. Los créditos variables deben quedar
  como desconocidos o expresarse mediante regla verificada, no suponerse fijos.
- `curriculum_entry`: pertenencia de materia o requisito agrupado a una versión
  de malla; semestre sugerido, tipo y créditos aplicables cuando se conozcan.
  No asumir que una materia pertenezca a una sola carrera o que una optativa
  equivalga a una asignatura concreta.
- `requirement`: regla versionada de prerrequisito, correquisito o graduación,
  con fuente y estado de conocimiento; representación de AND/OR y notas mínimas
  pendiente de acuerdo con I1. Distinguir explícitamente «sin requisito
  confirmado» de «requisito no verificado».
- `term`: identificador y fechas si la fuente las documenta.
- `catalog_snapshot`: periodo, procedencia, captura, estado de validación y
  puntero a la versión activa. Importar mallas y oferta como procesos separados.
- `offering`: identidad única `(catalog_snapshot, term, nrc)`, código de materia,
  paralelo y campos observados, conservando datos de origen y sin inventar cupos.
- `meeting`: cero o más reuniones con día, horario y fechas de vigencia, más
  estado explícito para horarios desconocidos o asíncronos. Una lista vacía no
  demuestra que una oferta pueda combinarse sin conflictos. Los intervalos
  conocidos usan extremos semiabiertos tras validar interpretación y zona.
- Componentes vinculados: representar relaciones de paralelo/laboratorio solo
  si la fuente documenta su significado. No inferirlas por cercanía o nombre.

## Perfiles sintéticos y seguridad

Perfiles de demostración, progreso, preferencias y horarios guardados se vinculan
por usuario. El acceso a cada recurso debe comprobar identidad y propiedad en
el servidor, con pruebas entre usuarios. No cargar expedientes reales. El diseño
de autenticación, contraseña y sesiones requiere revisión antes de implementarse;
no incluir credenciales reales en código ni logs. El rol MCP de lectura solo
obtendría datos autorizados mediante casos de uso, nunca SQL arbitrario. La
sincronización administrativa permanece fuera del contrato MCP de lectura hasta
que se acuerden roles y aprobación humana.

## Publicación de un catálogo

La importación propuesta valida primero un conjunto completo en almacenamiento
separado. Se debe comprobar alcance, claves, reuniones, procedencia, completitud
conocida y relación con el periodo. En una sola transacción se marca la versión
nueva como activa; si falla la validación o la transacción, se conserva la
versión previa. Se necesita definir cómo se reconocen fuentes parciales o vacías:
no convertir una respuesta vacía o error en eliminación automática de oferta.
Conservar un registro sin credenciales ni datos privados, con motivo y fecha.
La política exacta de retención, concurrencia y actualización es una decisión
pendiente del equipo y de los permisos de la fuente.

## Verificación e infraestructura

El 25 de noviembre de 2026 se comprobó PostgreSQL 17.11 en el servidor mediante
un contenedor temporal `--network none`, sin puertos, volumen ni datos reales.
Una tabla temporal, inserción y consulta sintéticas funcionaron; el contenedor
se eliminó. El contenedor de PostgreSQL del homelab no se usó ni alteró. Esto no
prueba la aplicación, migraciones, autenticación ni las transacciones descritas.
La validación posterior debe cubrir rollback, concurrencia de sincronización,
restricciones, conflictos entre versiones y separación de usuarios, con una
base aislada y reproducible. Ningún servicio nuevo debe exponerse públicamente
sin autorización.

## Preguntas para revisión

1. I1: representación de requisitos AND/OR, correquisitos y estado desconocido;
   mecanismo para relacionar una materia con ambas carreras y grupos elegibles.
2. I3: estructura de salida de ofertas con horarios desconocidos o fechas
   diferentes; estrategia que evita tratar desconocido como libre.
3. Equipo: identidad y retención de versiones, contrato de API, estrategia de
   autenticación de demostración y formato de migraciones antes de ejecutarlas.

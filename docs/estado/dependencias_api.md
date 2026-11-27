# Dependencias de la API de carreras

Comprobación: 27 nov 2026. Las versiones son las declaradas en
`requirements-i2-api.txt`, no necesariamente las más recientes. Se eligieron
para una API local de lectura y sus pruebas, no para desplegar un servicio.

| Paquete y versión | Uso | Licencia | Mantenimiento y fuente oficial | Costo local |
| --- | --- | --- | --- | --- |
| FastAPI 0.141.1 | Definir ruta y respuesta REST | MIT | [Paquete y versiones en PyPI](https://pypi.org/project/fastapi/0.141.1/); [publicaciones del proyecto](https://github.com/fastapi/fastapi/releases) muestran actividad. | Sin cargo por licencia; consume recursos del equipo. |
| Uvicorn 0.53.0 | Servidor ASGI de desarrollo | BSD-3-Clause | [Paquete y versiones en PyPI](https://pypi.org/project/uvicorn/0.53.0/); [publicaciones del proyecto](https://github.com/Kludex/uvicorn/releases) muestran actividad. | Sin cargo por licencia; consume recursos del equipo. |
| HTTPX 0.28.1 | Cliente utilizado por la prueba de la API | BSD-3-Clause | [Paquete y versiones en PyPI](https://pypi.org/project/httpx/0.28.1/); [publicaciones del proyecto](https://github.com/encode/httpx/releases) muestran actividad. | Sin cargo por licencia; consume recursos del equipo. |

Las licencias requieren conservar sus avisos en las distribuciones según sus
condiciones. Las versiones directas están fijadas; las transitivas aún no tienen
lock. Actividad de publicaciones no garantiza soporte ni ausencia de
vulnerabilidades. Se debe revisar compatibilidad y seguridad antes de una
entrega o actualización. Starlette advierte de la deprecación de la integración
de `TestClient` con HTTPX; no se ha sustituido en este cambio.

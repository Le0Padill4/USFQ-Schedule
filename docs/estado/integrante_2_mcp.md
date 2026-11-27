# MCP local de carreras — propuesta I2

`services.mcp_server` expone por stdio únicamente `list_careers`, que llama a la
misma función que la ruta REST propuesta en #9. No usa datos personales,
credenciales, red, SQL ni herramientas de sincronización. Es una primera
integración de lectura; no conecta aún a PostgreSQL ni implementa las demás
herramientas de dominio. No desplegarlo ni tratarlo como un servidor completo.

El repositorio selecciona FastMCP. La versión utilizada es `mcp==1.30.0`, línea
v1: la [documentación oficial de v1](https://py.sdk.modelcontextprotocol.io/v1/)
y la [guía de migración a v2](https://py.sdk.modelcontextprotocol.io/whats-new/)
indican que la interfaz cambia de nombre en v2. Esta decisión requiere revisión
del equipo al bloquear dependencias. Las dependencias transitivas no están
bloqueadas todavía.

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-i2-mcp.txt
.venv/bin/python -m unittest discover -s tests -p 'test_i2_mcp.py' -v
.venv/bin/python -m services.mcp_server
```

La prueba levanta el servidor como subproceso y usa un cliente MCP real por
stdio. La ausencia de herramientas de escritura también se verifica. Cualquier
sincronización requiere un contrato y permisos administrativos acordados.

## Verificación adicional del 25 de noviembre

En un worktree y entorno virtual aislados se instalaron las dependencias de
`requirements-i2-mcp.txt` y se ejecutó `python -m unittest discover -s tests
-p 'test_i2*.py' -v`: 2 pruebas correctas (API y cliente MCP real por stdio).
La instalación produjo una advertencia de deprecación de Starlette sobre el
uso de httpx con TestClient; requiere revisión de dependencias antes de
congelarlas. Esta prueba no conecta PostgreSQL ni un servidor de red.

Véase [dependencia MCP](dependencias_mcp.md) para versión, licencia,
mantenimiento, costo y los enlaces a las dependencias de la API.

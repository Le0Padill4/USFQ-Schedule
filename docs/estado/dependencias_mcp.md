# Dependencia MCP

Comprobación: 27 nov 2026. `requirements-i2-mcp.txt` incluye las
[dependencias de la API](dependencias_api.md) y fija `mcp==1.30.0`.

| Paquete y versión | Uso | Licencia | Mantenimiento y fuentes oficiales | Costo local |
| --- | --- | --- | --- | --- |
| MCP Python SDK 1.30.0 | Servidor y cliente de prueba por stdio con FastMCP | MIT | [Paquete y metadatos](https://pypi.org/project/mcp/1.30.0/), [licencia del proyecto](https://github.com/modelcontextprotocol/python-sdk/blob/v1.x/LICENSE) y [documentación v1](https://py.sdk.modelcontextprotocol.io/v1/). La línea v1 recibe correcciones críticas y de seguridad; v2 es la línea actual y requiere revisar su migración. | Sin cargo por licencia; la ejecución local consume recursos del equipo. |

La licencia requiere conservar sus avisos según sus condiciones. La versión
directa está fijada, pero no sus dependencias transitivas. La existencia de
mantenimiento no garantiza ausencia de vulnerabilidades. Revisar seguridad,
compatibilidad y bloqueo transitivo antes de entregar o actualizar.

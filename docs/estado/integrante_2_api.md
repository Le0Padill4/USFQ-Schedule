# API de carreras — Integrante 2

`GET /api/v1/careers` devuelve las dos carreras admitidas por el MVP. Es una
lista explícita de alcance, no una malla, oferta, cuenta, ni conexión a la USFQ.
El formato `{id, name}` deriva de la propuesta de contrato del integrante 3 y
requiere revisión antes de integrar el frontend. El resto de rutas de
`docs/CONTRATOS_INTEGRACION.md` aún no existe. No hay autenticación,
persistencia, autorización, sincronización ni servidor MCP en esta rama.

Preparación aislada sugerida (Python 3.13):

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-i2-api.txt
.venv/bin/python -m unittest discover -s tests -p 'test_i2_api.py' -v
.venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

La lista fija versiones directas de la prueba, no las transitivas; hay que
acordar el gestor y bloqueo reproducible de dependencias con el equipo. El
servidor se indica solo para desarrollo local, sin desplegar. Consulta de
documentación: https://fastapi.tiangolo.com/tutorial/testing/ y
https://fastapi.tiangolo.com/tutorial/bigger-applications/.

Validación local: la prueba pasó también en un entorno virtual recién creado
con las dependencias anteriores. Starlette emitió una advertencia de que su
integración `TestClient` con `httpx` está deprecada; debe revisarse al acordar
versiones y dependencias del proyecto.

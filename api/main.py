"""Small read-only API entry point; curriculum and persistence are pending."""
from fastapi import FastAPI
from pydantic import BaseModel


class Career(BaseModel):
    id: str
    name: str


app = FastAPI(title="USFQ Schedule API", version="0.1.0")


@app.get("/api/v1/careers", response_model=list[Career])
def list_careers() -> list[Career]:
    return [
        Career(id="1CMP", name="Ingeniería en Ciencias de la Computación"),
        Career(id="1MAC", name="Ingeniería en Matemáticas Aplicadas y Computación"),
    ]

from fastapi import FastAPI, HTTPException
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = FastAPI(
    title="REM BCRA API",
    description="API para obtener el último Relevamiento de Expectativas de Mercado",
    version="1.1.0"
)

BASE_URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/"


def obtener_ultimo_rem():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # 1. Obtener listado de archivos
    r = requests.get(BASE_URL, headers=headers, timeout=15)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="No se pudo acceder al directorio del BCRA")

    soup = BeautifulSoup(r.text, "html.parser")

    links = [
        a["href"] for a in soup.find_all("a", href=True)
        if "relevamiento" in a["href"].lower() and a["href"].endswith(".xlsx")
    ]

    if not links:
        raise HTTPException(status_code=404, detail="No se encontraron archivos REM")

    # 2. Ordenar por fecha implícita (último es el más nuevo)
    links.sort(reverse=True)

    archivo = links[0]
    url = BASE_URL + archivo

    # 3. Leer Excel
    df = pd.read_excel(url, sheet_name="Cuadros de resultados", header=None)

    periodos = df.iloc[6:13, 1]
    valores = df.iloc[6:13, 4]

    return {
        "archivo": archivo,
        "url": url,
        "datos": {str(p): float(v) for p, v in zip(periodos, valores)}
    }


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/rem/latest")
def get_latest_rem():
    return obtener_ultimo_rem()

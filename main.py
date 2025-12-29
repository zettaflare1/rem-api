from fastapi import FastAPI, HTTPException
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings

warnings.filterwarnings("ignore")

app = FastAPI(
    title="REM BCRA API",
    description="API para obtener el último Relevamiento de Expectativas de Mercado",
    version="1.0.0"
)

MESES = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr",
    5: "may", 6: "jun", 7: "jul", 8: "ago",
    9: "sep", 10: "oct", 11: "nov", 12: "dic"
}

BASE_URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/"


def obtener_ultimo_rem(max_intentos=6):
    fecha = datetime.today().replace(day=1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for _ in range(max_intentos):
        fecha -= relativedelta(months=1)

        mes = MESES[fecha.month]
        anio = fecha.year

        nombre = f"tablas-relevamiento-expectativas-mercado-{mes}-{anio}.xlsx"
        url = BASE_URL + nombre

        try:
            r = requests.get(url, headers=headers, stream=True, timeout=10)

            if r.status_code == 200:
                df = pd.read_excel(url, sheet_name="Cuadros de resultados", header=None)

                periodos = df.iloc[6:13, 1]
                valores = df.iloc[6:13, 4]

                return {
                    "fecha_rem": f"{mes}-{anio}",
                    "url": url,
                    "datos": {str(p): float(v) for p, v in zip(periodos, valores)}
                }

        except Exception as e:
            print("Error:", e)

    raise HTTPException(status_code=404, detail="No se encontró un REM válido")

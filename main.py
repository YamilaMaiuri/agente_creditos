"""
API de consulta a organismos externos (RENAPER, BCRA, AFIP)
Datos dummy para demo de créditos hipotecarios BNA
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="BNA - API Créditos Hipotecarios",
    description="API para consultar RENAPER, BCRA y AFIP en el flujo de solicitud de créditos hipotecarios del BNA",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# DATA DUMMY
# ---------------------------------------------------------------------------

RENAPER_DB = {
    "28441123": {
        "dni": "28441123",
        "nombre_completo": "Carlos Alberto Méndez",
        "cuil": "20-28441123-4",
        "fecha_nacimiento": "1985-03-12",
        "domicilio": "Av. Rivadavia 4521, CABA",
    },
    "35782456": {
        "dni": "35782456",
        "nombre_completo": "Luciana Paola Ferreyra",
        "cuil": "27-35782456-3",
        "fecha_nacimiento": "1992-07-28",
        "domicilio": "Mitre 340, Rosario, Santa Fe",
    },
    "22315789": {
        "dni": "22315789",
        "nombre_completo": "Roberto Carlos Sánchez",
        "cuil": "20-22315789-6",
        "fecha_nacimiento": "1978-11-05",
        "domicilio": "San Martín 1120, Córdoba Capital",
    },
    "40123654": {
        "dni": "40123654",
        "nombre_completo": "Valentina Inés Torres",
        "cuil": "27-40123654-1",
        "fecha_nacimiento": "1998-02-14",
        "domicilio": "Corrientes 2890, CABA",
    },
    "31567890": {
        "dni": "31567890",
        "nombre_completo": "Martín Ezequiel Ibáñez",
        "cuil": "20-31567890-9",
        "fecha_nacimiento": "1988-09-30",
        "domicilio": "Belgrano 780, Mendoza Capital",
    },
}

BCRA_DB = {
    "20-28441123-4": {
        "cuil": "20-28441123-4",
        "situacion": "1 - Normal",
        "score": 940,
        "deudas_activas_pesos": 0,
        "informes_negativos_12m": False,
    },
    "27-35782456-3": {
        "cuil": "27-35782456-3",
        "situacion": "1 - Normal",
        "score": 910,
        "deudas_activas_pesos": 85000,
        "informes_negativos_12m": False,
    },
    "20-22315789-6": {
        "cuil": "20-22315789-6",
        "situacion": "2 - Riesgo bajo",
        "score": 720,
        "deudas_activas_pesos": 340000,
        "informes_negativos_12m": True,
    },
    "27-40123654-1": {
        "cuil": "27-40123654-1",
        "situacion": "1 - Normal",
        "score": 965,
        "deudas_activas_pesos": 0,
        "informes_negativos_12m": False,
    },
    "20-31567890-9": {
        "cuil": "20-31567890-9",
        "situacion": "1 - Normal",
        "score": 955,
        "deudas_activas_pesos": 120000,
        "informes_negativos_12m": False,
    },
}

AFIP_DB = {
    "20-28441123-4": {
        "cuil": "20-28441123-4",
        "categoria": "relacion_dependencia",
        "empleador": "Farmacity S.A.",
        "actividad": None,
        "categoria_monotributo": None,
        "estado": "activo",
        "fecha_inscripcion": "2010-04-01",
    },
    "27-35782456-3": {
        "cuil": "27-35782456-3",
        "categoria": "monotributista",
        "empleador": None,
        "actividad": None,
        "categoria_monotributo": "H",
        "estado": "activo",
        "fecha_inscripcion": "2018-06-15",
    },
    "20-22315789-6": {
        "cuil": "20-22315789-6",
        "categoria": "relacion_dependencia",
        "empleador": "Textil San Jorge S.R.L.",
        "actividad": None,
        "categoria_monotributo": None,
        "estado": "activo",
        "fecha_inscripcion": "2005-08-20",
    },
    "27-40123654-1": {
        "cuil": "27-40123654-1",
        "categoria": "autonomo",
        "empleador": None,
        "actividad": "Servicios de consultoría empresarial",
        "categoria_monotributo": None,
        "estado": "activo",
        "fecha_inscripcion": "2020-03-10",
    },
    "20-31567890-9": {
        "cuil": "20-31567890-9",
        "categoria": "relacion_dependencia",
        "empleador": "Ministerio de Economía de la Nación",
        "actividad": None,
        "categoria_monotributo": None,
        "estado": "activo",
        "fecha_inscripcion": "2012-02-28",
    },
}


# ---------------------------------------------------------------------------
# RESPONSE MODELS
# ---------------------------------------------------------------------------

class RenaperResponse(BaseModel):
    dni: str
    nombre_completo: str
    cuil: str
    fecha_nacimiento: str
    domicilio: str


class BcraResponse(BaseModel):
    cuil: str
    situacion: str
    score: int
    deudas_activas_pesos: int
    informes_negativos_12m: bool


class AfipResponse(BaseModel):
    cuil: str
    categoria: str
    estado: str
    fecha_inscripcion: str
    empleador: str | None = None
    actividad: str | None = None
    categoria_monotributo: str | None = None


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/health", summary="Health check")
def health():
    """Health check para Code Engine"""
    return {"status": "ok"}


@app.get(
    "/renaper/{dni}",
    response_model=RenaperResponse,
    summary="Consultar RENAPER por DNI",
    description=(
        "Devuelve nombre completo, CUIL, fecha de nacimiento y domicilio "
        "registrado en el padrón del RENAPER."
    ),
    tags=["RENAPER"],
)
def consultar_renaper(dni: str):
    """Consulta los datos de identidad de una persona en RENAPER dado su DNI."""
    dni_clean = dni.strip().replace(".", "").replace(" ", "")
    persona = RENAPER_DB.get(dni_clean)
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"DNI {dni_clean} no encontrado en el padrón RENAPER.",
        )
    return persona


@app.get(
    "/bcra/{cuil}",
    response_model=BcraResponse,
    summary="Consultar BCRA por CUIL",
    description=(
        "Devuelve la situación crediticia, score, deudas activas e informes "
        "negativos en los últimos 12 meses."
    ),
    tags=["BCRA"],
)
def consultar_bcra(cuil: str):
    """Consulta la situación crediticia de una persona en el BCRA dado su CUIL."""
    registro = BCRA_DB.get(cuil.strip())
    if not registro:
        raise HTTPException(
            status_code=404,
            detail=f"CUIL {cuil} no encontrado en el registro BCRA.",
        )
    return registro


@app.get(
    "/afip/{cuil}",
    response_model=AfipResponse,
    summary="Consultar AFIP por CUIL",
    description=(
        "Devuelve la categoría tributaria, empleador o actividad según "
        "corresponda, estado fiscal y fecha de inscripción en AFIP/ARCA."
    ),
    tags=["AFIP"],
)
def consultar_afip(cuil: str):
    """Consulta la situación impositiva de una persona en AFIP dado su CUIL."""
    registro = AFIP_DB.get(cuil.strip())
    if not registro:
        raise HTTPException(
            status_code=404,
            detail=f"CUIL {cuil} no encontrado en el padrón AFIP.",
        )
    return {k: v for k, v in registro.items() if v is not None}

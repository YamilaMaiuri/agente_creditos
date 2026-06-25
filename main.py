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

PROPIEDADES_DB = [
    {
        "id": "HOG-001",
        "direccion": "Av. Corrientes 3840, Piso 5 Dto B",
        "localidad": "CABA",
        "tipo": "Departamento",
        "superficie_m2": 52,
        "ambientes": 2,
        "precio_pesos": 145000000,
        "apta_hipoteca": True,
        "estado_documental": "verificada",
    },
    {
        "id": "HOG-002",
        "direccion": "Gurruchaga 1456, PB A",
        "localidad": "CABA",
        "tipo": "PH",
        "superficie_m2": 68,
        "ambientes": 3,
        "precio_pesos": 185000000,
        "apta_hipoteca": True,
        "estado_documental": "verificada",
    },
    {
        "id": "HOG-003",
        "direccion": "San Lorenzo 892, Piso 2 Dto A",
        "localidad": "Rosario",
        "tipo": "Departamento",
        "superficie_m2": 48,
        "ambientes": 2,
        "precio_pesos": 98000000,
        "apta_hipoteca": True,
        "estado_documental": "verificada",
    },
    {
        "id": "HOG-004",
        "direccion": "Colón 234, Piso 3 Dto B",
        "localidad": "Córdoba Capital",
        "tipo": "Departamento",
        "superficie_m2": 55,
        "ambientes": 2,
        "precio_pesos": 112000000,
        "apta_hipoteca": True,
        "estado_documental": "verificada",
    },
    {
        "id": "HOG-005",
        "direccion": "Arístides Villanueva 540",
        "localidad": "Mendoza Capital",
        "tipo": "Casa",
        "superficie_m2": 90,
        "ambientes": 3,
        "precio_pesos": 165000000,
        "apta_hipoteca": True,
        "estado_documental": "verificada",
    },
]

RESERVAS_DB: dict = {}


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


class PropiedadResponse(BaseModel):
    id: str
    direccion: str
    localidad: str
    tipo: str
    superficie_m2: int
    ambientes: int
    precio_pesos: int
    apta_hipoteca: bool
    estado_documental: str


class ReservaRequest(BaseModel):
    cuil_cliente: str
    nombre_cliente: str


class ReservaResponse(BaseModel):
    id_reserva: str
    id_propiedad: str
    confirmada: bool
    vigencia_dias: int
    mensaje: str


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


@app.get(
    "/propiedades",
    response_model=list[PropiedadResponse],
    summary="Buscar propiedades en +Hogares BNA",
    description=(
        "Devuelve un listado de propiedades disponibles en el portal +Hogares "
        "con BNA compatibles con el monto aprobado y la ubicación deseada."
    ),
    tags=["Propiedades"],
)
def buscar_propiedades(precio_max: int, localidad: str):
    """
    Busca propiedades en +Hogares BNA filtrando por precio máximo y localidad.
    El precio máximo debe ser el monto del crédito aprobado dividido 0.75.
    """
    localidad_lower = localidad.strip().lower()
    resultados = [
        p for p in PROPIEDADES_DB
        if p["precio_pesos"] <= precio_max
        and localidad_lower in p["localidad"].lower()
    ]
    if not resultados:
        resultados = [
            p for p in PROPIEDADES_DB
            if p["precio_pesos"] <= precio_max
        ]
    if not resultados:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron propiedades disponibles para los filtros indicados.",
        )
    return resultados


@app.post(
    "/propiedades/{id}/reserva",
    response_model=ReservaResponse,
    summary="Reservar una propiedad en +Hogares BNA",
    description="Genera una reserva sobre la propiedad seleccionada para el solicitante.",
    tags=["Propiedades"],
)
def reservar_propiedad(id: str, body: ReservaRequest):
    """Genera una reserva de la propiedad indicada para el solicitante."""
    propiedad = next((p for p in PROPIEDADES_DB if p["id"] == id), None)
    if not propiedad:
        raise HTTPException(
            status_code=404,
            detail=f"Propiedad {id} no encontrada.",
        )
    if id in RESERVAS_DB:
        raise HTTPException(
            status_code=409,
            detail=f"La propiedad {id} ya tiene una reserva activa.",
        )
    import uuid
    id_reserva = f"RES-2026-{str(uuid.uuid4())[:6].upper()}"
    RESERVAS_DB[id] = {
        "id_reserva": id_reserva,
        "cuil_cliente": body.cuil_cliente,
        "nombre_cliente": body.nombre_cliente,
    }
    return {
        "id_reserva": id_reserva,
        "id_propiedad": id,
        "confirmada": True,
        "vigencia_dias": 10,
        "mensaje": f"Reserva confirmada para {propiedad['direccion']}. Tenés 10 días para avanzar con la tasación.",
    }

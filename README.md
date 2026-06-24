# Agentes BNA — Crédito Hipotecario UVA
## IBM watsonx Orchestrate · MVP

Sistema multi-agente para automatizar el proceso de solicitud de Crédito Hipotecario UVA del Banco de la Nación Argentina (+Hogares con BNA).

---

## Arquitectura

```
Orquestador_Creditos_Cliente
├── Subagente_Identidad_Creditos
├── Subagente_Ingresos_Creditos
├── Subagente_Propiedades_Creditos
└── Subagente_Notificaciones_Creditos
```

El orquestador es el único punto de contacto con el cliente. Los subagentes son especializados y solo se activan cuando el orquestador los invoca.

---

## Agentes

### `Orquestador_Creditos_Cliente`
- **Audiencia:** Cliente externo
- **Modelo:** granite-3-8b-instruct · react
- **Rol:** Conduce la conversación de principio a fin. Entiende qué quiere el cliente, delega verificaciones y cálculos a los subagentes, y presenta la oferta final.
- **Knowledge Base:** F-66405 (Términos Ingreso Digital) + F-66406 (Términos Propuesta Crediticia)
- **Colaboradores:** Los 4 subagentes

---

### `Subagente_Identidad_Creditos`
- **Modelo:** granite-3-8b-instruct · default
- **Rol:** Verifica identidad y situación crediticia consultando RENAPER, BCRA y AFIP en cadena.
- **Tools:** `consultar_renaper` · `consultar_bcra` · `consultar_afip`
- **Criterios de aprobación:**
  - Score BCRA ≥ 900 pts
  - Situación BCRA: "1 - Normal"
  - Sin informes negativos en los últimos 12 meses
  - Edad al cancelar ≤ 85 años

---

### `Subagente_Ingresos_Creditos`
- **Modelo:** granite-3-8b-instruct · react
- **Rol:** Procesa documentos de ingresos subidos por el cliente y calcula la cuota máxima y el monto de crédito por plazo.
- **Tools:** ninguna (opera con Chat with Docs)
- **Documentos que acepta:** Recibos de sueldo · DDJJ de Ganancias · Pagos de monotributo · Recibos de jubilación
- **Cálculo clave:** Cuota máxima = ingreso neto promedio × 25%

---

### `Subagente_Propiedades_Creditos`
- **Modelo:** granite-3-2b-instruct · default
- **Rol:** Busca propiedades en +Hogares BNA compatibles con el monto aprobado y gestiona la reserva.
- **Tools:** `buscar_propiedades` · `reservar_propiedad`
- **Regla clave:** Precio máximo de propiedad = monto aprobado / 0.75

---

### `Subagente_Notificaciones_Creditos`
- **Modelo:** granite-3-2b-instruct · default
- **Rol:** Envía email y SMS en cada hito del proceso. Es el único subagente compartido (lo usa también el orquestador empleado).
- **Tools:** `enviar_email` · `enviar_sms`
- **Eventos cubiertos:** Solicitud iniciada · Identidad OK/rechazada · Docs procesados · Oferta emitida · Recordatorio día 45 · Propiedad reservada · Tasación programada/completada · Turno de escritura

---

## Tools — Data Dummy

Las tools simulan las integraciones reales con sistemas externos. Cada una tiene datos de 5 clientes de prueba en distintos momentos del proceso.

### Clientes de prueba

| # | Nombre | DNI | CUIL | Estado en el proceso |
|---|---|---|---|---|
| 1 | Carlos Méndez | 28.441.123 | 20-28441123-4 | Apto · dependencia · cargando docs |
| 2 | Luciana Ferreyra | 35.782.456 | 27-35782456-3 | Apta · monotributista · tiene propiedad en mente |
| 3 | Roberto Sánchez | 22.315.789 | 20-22315789-6 | No apto · score BCRA 720 · informes negativos |
| 4 | Valentina Torres | 40.123.654 | 27-40123654-1 | Apta · autónoma · oferta emitida |
| 5 | Martín Ibáñez | 31.567.890 | 20-31567890-9 | Apto · sector público · turno de escritura asignado |

---

### Tool: `consultar_renaper`

**Subagente:** Subagente_Identidad_Creditos  
**Input:** `dni` (string)  
**Output:** nombre, cuil, fecha_nacimiento, domicilio

```json
[
  {
    "dni": "28441123",
    "nombre_completo": "Carlos Alberto Méndez",
    "cuil": "20-28441123-4",
    "fecha_nacimiento": "1985-03-12",
    "domicilio": "Av. Rivadavia 4521, CABA"
  },
  {
    "dni": "35782456",
    "nombre_completo": "Luciana Paola Ferreyra",
    "cuil": "27-35782456-3",
    "fecha_nacimiento": "1992-07-28",
    "domicilio": "Mitre 340, Rosario, Santa Fe"
  },
  {
    "dni": "22315789",
    "nombre_completo": "Roberto Carlos Sánchez",
    "cuil": "20-22315789-6",
    "fecha_nacimiento": "1978-11-05",
    "domicilio": "San Martín 1120, Córdoba Capital"
  },
  {
    "dni": "40123654",
    "nombre_completo": "Valentina Inés Torres",
    "cuil": "27-40123654-1",
    "fecha_nacimiento": "1998-02-14",
    "domicilio": "Corrientes 2890, CABA"
  },
  {
    "dni": "31567890",
    "nombre_completo": "Martín Ezequiel Ibáñez",
    "cuil": "20-31567890-9",
    "fecha_nacimiento": "1988-09-30",
    "domicilio": "Belgrano 780, Mendoza Capital"
  }
]
```

---

### Tool: `consultar_bcra`

**Subagente:** Subagente_Identidad_Creditos  
**Input:** `cuil` (string)  
**Output:** situacion, score, deudas_activas_pesos, informes_negativos_12m

```json
[
  {
    "cuil": "20-28441123-4",
    "situacion": "1 - Normal",
    "score": 940,
    "deudas_activas_pesos": 0,
    "informes_negativos_12m": false
  },
  {
    "cuil": "27-35782456-3",
    "situacion": "1 - Normal",
    "score": 910,
    "deudas_activas_pesos": 85000,
    "informes_negativos_12m": false
  },
  {
    "cuil": "20-22315789-6",
    "situacion": "2 - Riesgo bajo",
    "score": 720,
    "deudas_activas_pesos": 340000,
    "informes_negativos_12m": true
  },
  {
    "cuil": "27-40123654-1",
    "situacion": "1 - Normal",
    "score": 965,
    "deudas_activas_pesos": 0,
    "informes_negativos_12m": false
  },
  {
    "cuil": "20-31567890-9",
    "situacion": "1 - Normal",
    "score": 955,
    "deudas_activas_pesos": 120000,
    "informes_negativos_12m": false
  }
]
```

---

### Tool: `consultar_afip`

**Subagente:** Subagente_Identidad_Creditos  
**Input:** `cuil` (string)  
**Output:** categoria, empleador/actividad, estado, fecha_inscripcion

```json
[
  {
    "cuil": "20-28441123-4",
    "categoria": "relacion_dependencia",
    "empleador": "Farmacity S.A.",
    "estado": "activo",
    "fecha_inscripcion": "2010-04-01"
  },
  {
    "cuil": "27-35782456-3",
    "categoria": "monotributista",
    "categoria_monotributo": "H",
    "estado": "activo",
    "fecha_inscripcion": "2018-06-15"
  },
  {
    "cuil": "20-22315789-6",
    "categoria": "relacion_dependencia",
    "empleador": "Textil San Jorge S.R.L.",
    "estado": "activo",
    "fecha_inscripcion": "2005-08-20"
  },
  {
    "cuil": "27-40123654-1",
    "categoria": "autonomo",
    "actividad": "Servicios de consultoría empresarial",
    "estado": "activo",
    "fecha_inscripcion": "2020-03-10"
  },
  {
    "cuil": "20-31567890-9",
    "categoria": "relacion_dependencia",
    "empleador": "Ministerio de Economía de la Nación",
    "estado": "activo",
    "fecha_inscripcion": "2012-02-28"
  }
]
```

---

### Tool: `buscar_propiedades`

**Subagente:** Subagente_Propiedades_Creditos  
**Input:** `precio_max` (number), `localidad` (string)  
**Output:** listado de propiedades disponibles en +Hogares BNA

```json
[
  {
    "id": "HOG-001",
    "direccion": "Av. Corrientes 3840, Piso 5 Dto B",
    "localidad": "CABA",
    "tipo": "Departamento",
    "superficie_m2": 52,
    "ambientes": 2,
    "precio_pesos": 145000000,
    "apta_hipoteca": true,
    "estado_documental": "verificada"
  },
  {
    "id": "HOG-002",
    "direccion": "Gurruchaga 1456, PB A",
    "localidad": "CABA",
    "tipo": "PH",
    "superficie_m2": 68,
    "ambientes": 3,
    "precio_pesos": 185000000,
    "apta_hipoteca": true,
    "estado_documental": "verificada"
  },
  {
    "id": "HOG-003",
    "direccion": "San Lorenzo 892",
    "localidad": "Rosario",
    "tipo": "Departamento",
    "superficie_m2": 48,
    "ambientes": 2,
    "precio_pesos": 98000000,
    "apta_hipoteca": true,
    "estado_documental": "verificada"
  },
  {
    "id": "HOG-004",
    "direccion": "Colón 234, Piso 3",
    "localidad": "Córdoba Capital",
    "tipo": "Departamento",
    "superficie_m2": 55,
    "ambientes": 2,
    "precio_pesos": 112000000,
    "apta_hipoteca": true,
    "estado_documental": "verificada"
  },
  {
    "id": "HOG-005",
    "direccion": "Arístides Villanueva 540",
    "localidad": "Mendoza Capital",
    "tipo": "Casa",
    "superficie_m2": 90,
    "ambientes": 3,
    "precio_pesos": 165000000,
    "apta_hipoteca": true,
    "estado_documental": "verificada"
  }
]
```

---

### Tool: `reservar_propiedad`

**Subagente:** Subagente_Propiedades_Creditos  
**Input:** `id_propiedad` (string), `cuil_cliente` (string)  
**Output:** confirmación de reserva con ID y vigencia

```json
[
  {
    "id_propiedad": "HOG-001",
    "id_reserva": "RES-2026-0041",
    "confirmada": true,
    "vigencia_dias": 10,
    "mensaje": "Reserva confirmada. Tenés 10 días para avanzar con la tasación."
  },
  {
    "id_propiedad": "HOG-002",
    "id_reserva": "RES-2026-0042",
    "confirmada": true,
    "vigencia_dias": 10,
    "mensaje": "Reserva confirmada. Tenés 10 días para avanzar con la tasación."
  },
  {
    "id_propiedad": "HOG-003",
    "id_reserva": "RES-2026-0043",
    "confirmada": true,
    "vigencia_dias": 10,
    "mensaje": "Reserva confirmada. Tenés 10 días para avanzar con la tasación."
  },
  {
    "id_propiedad": "HOG-004",
    "id_reserva": "RES-2026-0044",
    "confirmada": true,
    "vigencia_dias": 10,
    "mensaje": "Reserva confirmada. Tenés 10 días para avanzar con la tasación."
  },
  {
    "id_propiedad": "HOG-005",
    "id_reserva": "RES-2026-0045",
    "confirmada": true,
    "vigencia_dias": 10,
    "mensaje": "Reserva confirmada. Tenés 10 días para avanzar con la tasación."
  }
]
```

---

### Tool: `enviar_email`

**Subagente:** Subagente_Notificaciones_Creditos  
**Input:** `destinatario_email`, `destinatario_nombre`, `asunto`, `cuerpo`  
**Output:** confirmación de envío

```json
{
  "status": "enviado",
  "message_id": "MSG-EMAIL-001",
  "timestamp": "2026-06-24T10:00:00Z"
}
```

---

### Tool: `enviar_sms`

**Subagente:** Subagente_Notificaciones_Creditos  
**Input:** `telefono`, `mensaje` (máx 160 caracteres)  
**Output:** confirmación de envío

```json
{
  "status": "enviado",
  "message_id": "MSG-SMS-001",
  "timestamp": "2026-06-24T10:00:00Z"
}
```

---

## Knowledge Base

Cargar en el `Orquestador_Creditos_Cliente`:

| Archivo | Contenido | Cuándo lo consulta el agente |
|---|---|---|
| `F-66405.pdf` | Términos y Condiciones de Ingreso Digital Web | Cuando el cliente pregunta sobre el proceso, privacidad o consentimiento |
| `F-66406.pdf` | Términos y Condiciones de la Propuesta Crediticia | Cuando necesita condiciones reales: montos, plazos, tasas, mora, CVS |

---

## Flujo del proceso

```
Cliente escribe
      ↓
Orquestador_Creditos_Cliente
      ↓
  ¿Qué quiere?
      ↓
  Verificar identidad → Subagente_Identidad_Creditos
      ↓                 (RENAPER + BCRA + AFIP)
  ¿Apto?
  ├── No → Informar motivo → Subagente_Notificaciones_Creditos
  └── Sí → Analizar ingresos → Subagente_Ingresos_Creditos
                ↓              (Chat with Docs)
           ¿Alcanza?
           ├── No → Sugerir cotitular o codeudor
           └── Sí → Buscar propiedad → Subagente_Propiedades_Creditos
                         ↓              (API +Hogares)
                    Presentar oferta
                         ↓
                    Confirmar → Subagente_Notificaciones_Creditos
                                (email + SMS)
```

---

## Pendiente

- [ ] Orquestador_Creditos_Empleado — prompt, tools y subagentes propios
- [ ] Subagentes internos del empleado (consulta, pipeline, escalados, tasaciones)
- [ ] Conectar tools reales (RENAPER, BCRA, AFIP, +Hogares) cuando estén disponibles
- [ ] Cargar F-66405 y F-66406 en la Knowledge Base del orquestador cliente

---

## Stack

- **Plataforma:** IBM watsonx Orchestrate
- **Modelos:** granite-3-8b-instruct (orquestador + identidad + ingresos) · granite-3-2b-instruct (propiedades + notificaciones)
- **Cliente:** Banco de la Nación Argentina (BNA)
- **Versión:** MVP · Junio 2026
- **Equipo:** IBM Expert Labs Argentina

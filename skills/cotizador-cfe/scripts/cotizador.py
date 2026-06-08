"""
Paso 3 del flujo cotizador-cfe.
Recibe las 4 variables anuales del PDF + nombre y teléfono del remitente
y las envía al endpoint de Nisa Energy.
"""

import requests

ENDPOINT = "https://base44.app/api/apps/698bd38c0ecaed3d486131ee/functions/recibirClienteWhatsapp"


def enviar_cotizacion(nombre, telefono, consumo_anual, facturacion_anual, precio_promedio, kw_en_punta):
    payload = {
        "nombre": nombre,
        "telefono": str(telefono),
        "consumo_anual": consumo_anual,
        "facturacion_anual": facturacion_anual,
        "precio_promedio": precio_promedio,
        "kw_en_punta": kw_en_punta,
    }
    try:
        resp = requests.post(ENDPOINT, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP {resp.status_code}", "detalle": resp.text}
    except requests.exceptions.RequestException as e:
        return {"error": "No se pudo conectar con el servidor", "detalle": str(e)}

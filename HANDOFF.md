# HANDOFF — nisa-quoter-agent

## Goal

Configurar, estructurar y deployar el agente cotizador de recibos CFE (México) siguiendo el estándar de **Hermes Agent profile distributions** (Nous Research), para que vendedores de Nisa Energy puedan enviar un PDF de recibo de luz por WhatsApp/Telegram y recibir una cotización.

El gateway de Hermes ya está configurado en el VPS del cliente (`fernandoassef@hotmail.com`). El repo es el profile distribution que se instala encima.

---

## Current Progress

El repo está **en producción v0.2** — flujo completo hasta el endpoint real de Nisa Energy:

```
nisa-quoter-agent/
├── distribution.yaml        ✅ v0.2, name: cfe-agent
├── SOUL.md                  ✅ personalidad del agente (español MX, Nisa Energy)
├── config.yaml              ✅ modelo real: glm-5.1 / ollama-cloud / https://ollama.com/v1
├── mcp.json                 ✅ placeholder vacío {} (sin MCP por ahora)
├── README.md                ✅ documentación
└── skills/
    └── cotizador-cfe/
        ├── SKILL.md         ✅ flujo de 4 pasos — sin preguntas, con POST al endpoint
        └── scripts/
            ├── extraccion_pdf.py   ✅ extrae historial mensual del PDF (pdfplumber)
            ├── variables_pdf.py    ✅ consolida 4 variables anuales
            └── cotizador.py        ✅ POST al endpoint de Nisa Energy (paso 3)
```

### Deploy
El profile ya está deployado en el VPS con:
```bash
cfe-agent profile install git@github.com:hazu-low-code-solutions/nisa-quoter-agent.git --force
```

Para re-deployar tras cambios:
```bash
cfe-agent profile install git@github.com:hazu-low-code-solutions/nisa-quoter-agent.git --force
```

### Stack del cliente
- **Hermes Agent** (Nous Research) en VPS dedicado
- **Modelo:** `glm-5.1` vía `ollama-cloud` (`https://ollama.com/v1`)
- **Profile existente en VPS:** `~/.hermes/profiles/cfe-agent/`
- **Gateway:** ya configurado para WhatsApp / Telegram

---

## Flujo del agente (v0.2)

1. **Vendedor envía PDF** → agente llama `extraer_historico_cfe_real(pdf_path)`
2. **Agente llama** `calcular_metricas_anuales(datos)` → obtiene 4 variables anuales
3. **Agente llama** `enviar_cotizacion(...)` con las 4 variables + nombre/teléfono del remitente → POST a `https://base44.app/api/apps/698bd38c0ecaed3d486131ee/functions/recibirClienteWhatsapp`
4. **Agente responde** con mensaje natural confirmando el registro (cotización en PDF pendiente — lógica no lista aún)

### Contrato del endpoint (Nisa Energy)

**Request:**
```json
{
  "nombre": "Nombre del cliente",
  "telefono": "5512345678",
  "consumo_anual": 120000,
  "facturacion_anual": 250000,
  "precio_promedio": 2.08,
  "kw_en_punta": 45
}
```

**Response 200 OK:**
```json
{
  "status": "OK",
  "message": "Datos recibidos",
  "cliente_id": "6a27373d28079639f846966f",
  "contacto_id": "6a27373d6bdaf8516f0eaefb"
}
```

---

## Lo que funciona

- Estructura estándar de Hermes profile distribution.
- Los 3 scripts Python funcionan como pipeline: `extraccion_pdf.py` → `variables_pdf.py` → `cotizador.py`.
- El endpoint de Nisa Energy (`base44.app`) ya acepta los datos y responde correctamente.
- Deploy vía `cfe-agent profile install ... --force` ya probado.

---

## Lo que NO funciona / está pendiente

- **Entrega de cotización en PDF:** el endpoint registra al cliente pero la generación y envío del PDF cotizador no está lista. El agente informa al vendedor que la recibirá en breve.

---

## Next Steps

### Inmediatos
1. **Probar con PDF real de CFE en el VPS:** enviar por WhatsApp/Telegram y verificar extracción + POST al endpoint.
2. **Verificar dependencias Python en el VPS:** `pdfplumber`, `pandas`, `requests`.

### Incremento futuro (v0.3)
3. **Cotización en PDF:** cuando Nisa Energy habilite la lógica de generación de PDF, actualizar el PASO 4 de SKILL.md para devolver/enviar el archivo.
4. **Nombre del cliente:** hoy el agente usa el nombre del remitente de WhatsApp/Telegram. Evaluar si se necesita capturarlo explícitamente (ej. "¿Cuál es el nombre de tu cliente?").

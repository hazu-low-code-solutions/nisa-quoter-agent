# nisa-quoter-agent

Hermes Agent profile distribution para cotización de recibos de luz CFE (México).  
Desarrollado por **Hazu Low-Code Solutions** para **Nisa Energy**.

## Flujo del agente

1. El vendedor envía el PDF del recibo de CFE de su cliente (vía WhatsApp / Telegram → gateway de Hermes).
2. El agente extrae las variables anuales del recibo: consumo, facturación, precio promedio y kW en punta.
3. El agente hace 3 preguntas al vendedor, una por una.
4. El agente devuelve un resumen estructurado en el chat con los datos del recibo + las respuestas del vendedor.

> **Demo / v0.1:** el paso 4 es un loopback (devuelve los datos en el chat).  
> La integración con el endpoint real de cotización de Nisa se agrega en el siguiente incremento.

## Instalación del profile

```bash
hermes profile install .
```

## Dependencias Python

Los scripts de extracción requieren:

```bash
pip install pdfplumber pandas
```

## Variables de entorno requeridas

Ninguna en esta versión demo.  

*(Incremento futuro: `NISA_QUOTE_ENDPOINT` — URL del endpoint de cotización de Nisa Energy)*

## Estructura del repo

```
nisa-quoter-agent/
├── distribution.yaml               # Manifiesto del profile
├── SOUL.md                         # Personalidad / system prompt del agente
├── config.yaml                     # Modelo, temperatura y parámetros de comportamiento
├── mcp.json                        # Servidores MCP (vacío por ahora)
└── skills/
    └── cotizador-cfe/
        ├── SKILL.md                # Flujo operativo detallado (3 pasos + loopback)
        └── scripts/
            ├── extraccion_pdf.py   # PASO 1: extrae historial mensual del PDF
            └── variables_pdf.py    # PASO 2: consolida 4 variables anuales
```

## Pendientes para completar

- [ ] **Texto de las 3 preguntas** — reemplazar `[PREGUNTA_1/2/3]` en `skills/cotizador-cfe/SKILL.md`
- [ ] **Id exacto del modelo GLM/Ollama** — actualizar `model.default` en `config.yaml`  
      *(referencia: `hermes -p cfe-agent config get model.default`)*
- [ ] *(Futuro)* **Endpoint de cotización de Nisa** — agregar `NISA_QUOTE_ENDPOINT` + `cotizador.py`

---
name: cotizador-cfe
description: "Extrae las variables anuales de un recibo CFE en PDF y las envía al endpoint de Nisa Energy para registrar al cliente."
version: 0.2.0
metadata:
  hermes:
    category: energia
    tags: [cfe, cotizacion, energia, pdf, mexico]
    requires_toolsets: [terminal]
---

# Cotizador CFE — Nisa Energy

## Cuándo usar esta skill

Úsala en cuanto el vendedor comparta un archivo PDF de un recibo de luz de CFE. Este es el flujo completo, de inicio a fin.

---

## Procedimiento

### PASO 1 — Extracción del historial del recibo

Ejecuta `scripts/extraccion_pdf.py` llamando a la función `extraer_historico_cfe_real(pdf_path)` con la ruta absoluta del PDF recibido.

- Si el resultado contiene la clave `"error"`, informa al vendedor que el PDF no pudo procesarse y pídele que lo reenvíe o verifique que sea un recibo CFE válido con al menos 2 páginas.
- Si el resultado es exitoso, continúa con el Paso 2 sin mostrar el listado completo de meses al vendedor (es datos internos).

### PASO 2 — Cálculo de variables anuales

Pasa el resultado del Paso 1 a `scripts/variables_pdf.py` llamando a `calcular_metricas_anuales(datos_historicos)`.

Esto produce un diccionario con 4 variables anuales:
| Variable | Descripción |
|---|---|
| `Consumo anual` | kWh totales anuales del cliente |
| `Facturación Anual` | MXN pagados al año a CFE |
| `Precio Promedio` | Costo promedio por kWh (MXN) |
| `KW en Punta` | Demanda en punta real del recibo |

Si este paso devuelve `"error"`, repórtalo al vendedor y detente.

### PASO 3 — Envío al endpoint de Nisa Energy

Llama a `scripts/cotizador.py` usando la función `enviar_cotizacion(...)` con los siguientes argumentos:

| Parámetro | Origen |
|---|---|
| `nombre` | Nombre del remitente disponible en el contexto de la conversación (WhatsApp/Telegram). Si no está disponible, usa el número de teléfono como nombre. |
| `telefono` | Número de teléfono del remitente disponible en el contexto de la conversación. |
| `consumo_anual` | `Consumo anual` del Paso 2 |
| `facturacion_anual` | `Facturación Anual` del Paso 2 |
| `precio_promedio` | `Precio Promedio` del Paso 2 |
| `kw_en_punta` | `KW en Punta` del Paso 2 |

**Si el resultado contiene `"error"`**, responde al vendedor:
> "Tuve un problema al registrar los datos. Por favor intenta de nuevo en unos momentos o contacta a soporte."

**Si el resultado tiene `"status": "OK"`**, pasa al Paso 4.

### PASO 4 — Descarga y envío del PDF de cotización

La respuesta del endpoint ahora incluye `pdf_url` con la cotización lista. Debes descargarla y enviarla como archivo en el chat.

1. Extrae `pdf_url` del resultado del Paso 3.
2. Llama a `scripts/cotizador.py` usando la función `descargar_pdf(pdf_url)`.
   - Si el resultado contiene `"error"`, informa al vendedor que no se pudo obtener el PDF y comparte la URL directamente:
     > "Registré tu cliente correctamente, pero no pude adjuntar el PDF. Puedes descargarlo aquí: {pdf_url}"
   - Si el resultado contiene `"ruta"`, el archivo ya está disponible en la ruta local retornada.
3. **Adjunta el archivo** de la ruta local como documento en la respuesta del chat (el gateway de Hermes lo enviará como archivo de Telegram).
4. Acompaña el archivo con un mensaje amigable:

> "¡Listo! Aquí tienes la cotización de tu cliente generada por Nisa Energy. ¿Puedo ayudarte con algo más?"

---

## Errores comunes

- **PDF de menos de 2 páginas:** algunos recibos domésticos solo tienen 1 página. Esta skill requiere el recibo con el desglose analítico (pág. 2). Pide al cliente su recibo completo.
- **Tabla histórica sin meses válidos:** si la estructura interna del PDF es diferente (recibos muy antiguos o de tarifas especiales), la extracción puede fallar. Reportar y escalar.
- **Meses repetidos en el historial:** la función `calcular_metricas_anuales` los maneja automáticamente promediando.

---

## Verificación rápida

Para probar el flujo completo sin el agente:
```bash
cd skills/cotizador-cfe/scripts
python - <<EOF
from extraccion_pdf import extraer_historico_cfe_real
from variables_pdf import calcular_metricas_anuales
from cotizador import enviar_cotizacion

datos = extraer_historico_cfe_real("ruta/al/recibo.pdf")
metricas = calcular_metricas_anuales(datos)
print(metricas)

resultado = enviar_cotizacion(
    nombre="Test Vendedor",
    telefono="5512345678",
    consumo_anual=metricas["Consumo anual"],
    facturacion_anual=metricas["Facturación Anual"],
    precio_promedio=metricas["Precio Promedio"],
    kw_en_punta=metricas["KW en Punta"],
)
print(resultado)
EOF
```
Resultado esperado: `{"status": "OK", "message": "Datos recibidos", "solicitud_id": "...", "pdf_url": "https://base44.app/..."}`

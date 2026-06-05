---
name: cotizador-cfe
description: "Extrae las variables anuales de un recibo CFE en PDF, recopila 3 respuestas del vendedor y devuelve el resumen de cotización en el chat."
version: 0.1.0
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

### PASO 3 — Recopilación de datos del vendedor (3 preguntas)

Haz las siguientes preguntas **una por una**, esperando la respuesta de cada una antes de pasar a la siguiente:

1. **[PREGUNTA_1]** *(pendiente — reemplaza este placeholder con la pregunta real)*
2. **[PREGUNTA_2]** *(pendiente — reemplaza este placeholder con la pregunta real)*
3. **[PREGUNTA_3]** *(pendiente — reemplaza este placeholder con la pregunta real)*

### PASO 4 — Resumen de cotización (loopback)

Una vez que tengas las 4 variables del PDF y las 3 respuestas del vendedor, presenta el siguiente resumen en el chat:

```
📋 RESUMEN DE COTIZACIÓN — Nisa Energy

📊 Datos extraídos del recibo CFE:
• Consumo anual:     {Consumo anual} kWh
• Facturación anual: ${Facturación Anual} MXN
• Precio promedio:   ${Precio Promedio} MXN/kWh
• KW en Punta:       {KW en Punta} kW

💬 Datos del vendedor:
• [PREGUNTA_1]: {respuesta_1}
• [PREGUNTA_2]: {respuesta_2}
• [PREGUNTA_3]: {respuesta_3}
```

> **Nota (incremento futuro):** este paso de loopback será reemplazado por el envío
> de estos datos al endpoint de cotización de Nisa Energy (`NISA_QUOTE_ENDPOINT`)
> cuando se tenga la URL y el contrato del API.

---

## Errores comunes

- **PDF de menos de 2 páginas:** algunos recibos domésticos solo tienen 1 página. Esta skill requiere el recibo con el desglose analítico (pág. 2). Pide al cliente su recibo completo.
- **Tabla histórica sin meses válidos:** si la estructura interna del PDF es diferente (recibos muy antiguos o de tarifas especiales), la extracción puede fallar. Reportar y escalar.
- **Meses repetidos en el historial:** la función `calcular_metricas_anuales` los maneja automáticamente promediando.

---

## Verificación rápida

Para probar la extracción sin el agente:
```bash
cd skills/cotizador-cfe/scripts
python - <<EOF
from extraccion_pdf import extraer_historico_cfe_real
from variables_pdf import calcular_metricas_anuales
datos = extraer_historico_cfe_real("ruta/al/recibo.pdf")
print(calcular_metricas_anuales(datos))
EOF
```
Resultado esperado: dict con `Consumo anual`, `Facturación Anual`, `Precio Promedio` y `KW en Punta`.

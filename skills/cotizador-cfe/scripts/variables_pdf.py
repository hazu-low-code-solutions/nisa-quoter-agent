def calcular_metricas_anuales(datos_historicos: list) -> dict:
    """
    PASO 2 DEL PROCESO DE CFE.
    Usa esta herramienta analítica después de haber extraído el historial con 'extraer_historico_cfe_real'.
    Toma la lista de registros históricos de CFE y calcula de forma consolidada 4 variables anuales clave.
    
    Reglas que deben ser aplicadas:
    1. Consumo anual: Suma de los consumos totales (kWh). Si un mes se repite, calcula primero el promedio de ese mes.
    2. Facturación Anual: Multiplica fila por fila Consumo (kWh) por Precio Medio (MXN) y después suma los resultados (promediando meses repetidos).
    3. Precio Promedio: Divide la Facturación Anual resultante entre el Consumo Anual resultante.
    4. KW en Punta: Valor de "kW punta" extraído directamente de la página 1 del recibo (campo
       'KW en Punta Real' del paso anterior). No es un promedio de la columna Demanda (kW) del historial.
    
    Args:
        datos_historicos (list): Lista de diccionarios mensuales obtenida del paso de extracción.
        
    Returns:
        dict: Un diccionario con las 4 variables finales calculadas: 
              'Consumo anual', 'Precio Promedio', 'Facturacion Anual' y 'KW en Punta'.
              Si la entrada es inválida, retorna un diccionario con la clave 'error'.
    """
    if not datos_historicos or not isinstance(datos_historicos, list):
        return {"error": "No se proporcionó una lista válida de datos históricos para procesar."}
        
    if "error" in datos_historicos[0]:
        return {"error": f"No se pueden calcular métricas porque el paso previo falló: {datos_historicos[0]['error']}"}

    kw_en_punta_final = datos_historicos[0].get("KW en Punta Real", 0.0)

    agrupacion_consumo = {}
    agrupacion_facturacion = {}
    
    for registro in datos_historicos:
        try:
            mes = registro["Periodo"].split("-")[0].upper()
            
            consumo = float(registro["Consumo total (kWh)"])
            
            # Limpieza de caracteres monetarios por seguridad y conversión a decimal
            precio_medio_str = str(registro["Precio medio (MXN)"]).replace("$", "").strip()
            precio_medio = float(precio_medio_str)
            
            # REGLA 2 (Parte 1): Multiplicación fila por fila Consumo * Precio Medio
            facturacion_fila = consumo * precio_medio
            
            # Agrupamos datos por mes para resolver duplicados
            if mes not in agrupacion_consumo:
                agrupacion_consumo[mes] = [consumo]
                agrupacion_facturacion[mes] = [facturacion_fila]
            else:
                agrupacion_consumo[mes].append(consumo)
                agrupacion_facturacion[mes].append(facturacion_fila)
                
        except KeyError as e:
            return {"error": f"Falta una columna esperada en los datos origen: {str(e)}"}
        except ValueError as e:
            return {"error": f"Error al convertir un dato de texto a formato numérico: {str(e)}"}
            
    consumos_consolidados = []
    facturaciones_consolidadas = []
    
    # Aplicando promedios cuando un mes se repite
    for mes in agrupacion_consumo:
        if len(agrupacion_consumo[mes]) > 1:
            # REGLA 1: Si un mes se repite, calcula primero el promedio del consumo de ese mes
            consumo_final = sum(agrupacion_consumo[mes]) / len(agrupacion_consumo[mes])
            # REGLA 2 (Parte 2): Promediando meses repetidos para la facturación resultante
            facturacion_final = sum(agrupacion_facturacion[mes]) / len(agrupacion_facturacion[mes])
        else:
            consumo_final = agrupacion_consumo[mes][0]
            facturacion_final = agrupacion_facturacion[mes][0]
            
        consumos_consolidados.append(consumo_final)
        facturaciones_consolidadas.append(facturacion_final)
        
    # REGLA 1 (Final): Suma de todos los consumos anuales consolidados
    consumo_anual_final = sum(consumos_consolidados)
    
    # REGLA 2 (Final): Suma de todos los resultados de facturación consolidados
    facturacion_anual_final = sum(facturaciones_consolidadas)
    
    # REGLA 3: Divide la Facturación Anual resultante entre el Consumo Anual resultante
    precio_promedio_final = facturacion_anual_final / consumo_anual_final if consumo_anual_final > 0 else 0
    
    return {
        "Consumo anual": round(consumo_anual_final, 2),
        "Precio Promedio": round(precio_promedio_final, 4),
        "Facturacion Anual": round(facturacion_anual_final, 2),
        "KW en Punta": round(kw_en_punta_final, 2)
    }
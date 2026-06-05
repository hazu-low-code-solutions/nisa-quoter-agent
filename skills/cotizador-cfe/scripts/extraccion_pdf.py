import pdfplumber
import pandas as pd
import re

def extraer_historico_cfe_real(pdf_path: str) -> list:
    """
    PASO 1 DEL PROCESO DE CFE.
    Usa esta herramienta cuando el usuario te proporcione un recibo de luz de CFE en formato PDF 
    y requieras conocer los datos históricos o calcular métricas agregadas anuales.
    Esta herramienta abre el archivo, extrae el historial de meses, consumos, demandas y precios 
    desde el desglose analítico de la segunda página.
    
    Args:
        pdf_path (str): La ruta absoluta o relativa del archivo PDF del recibo de CFE en el sistema.
        
    Returns:
        list: Una lista de diccionarios (JSON) donde cada elemento es un mes con las columnas:
              'Periodo', 'Demanda (kW)', 'Consumo total (kWh)', 'Factor potencia', 'Factor carga' y 'Precio medio (MXN)'.
              Si ocurre un error, retorna una lista con un diccionario que contiene la clave 'error'.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) < 2:
                return [{"error": "El PDF proporcionado no tiene una segunda página donde se ubica el histórico."}]
                
            pagina1 = pdf.pages[0]
            texto_p1 = pagina1.extract_text() or ""
            
            kw_punta_real = 0.0
            match_punta = re.search(r"kW\s+punta\s*\",\s*\"([\d,.]+)", texto_p1, re.IGNORECASE)
            if match_punta:
                kw_punta_real = float(match_punta.group(1).replace(",", ""))
            else:
                match_punta_alt = re.search(r"kW\s+punta\s+([\d,.]+)", texto_p1, re.IGNORECASE)
                if match_punta_alt:
                    kw_punta_real = float(match_punta_alt.group(1).replace(",", ""))

            # PROCESAMIENTO DE LA TABLA HISTÓRICA
            pagina2 = pdf.pages[1]
            texto_p2 = pagina2.extract_text() or ""

            meses_validos = {"ENE", "FEB", "MAR", "MZO", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"}
            
            periodos = []
            demandas = []
            consumos = []
            factores_potencia = []
            factores_carga = []
            precios_medio = []
            
            lineas = texto_p2.split("\n")
            
            for linea in lineas:
                linea_limpia = linea.replace('"', '').replace(',', '')
                elementos = linea_limpia.split()

                if len(elementos) < 7:
                    continue
                    
                primer_elemento = elementos[0].upper()
                if primer_elemento in meses_validos:
                    try:
                        mes = elementos[0]
                        anio = elementos[1]
                        demanda_kw = elementos[2]
                        consumo_kwh = int(elementos[3])
                        
                        fact_potencia = elementos[4]
                        fact_carga = elementos[5]
        
                        precio_crudo = elementos[6]
                        if len(precio_crudo) > 2 and "." not in precio_crudo:
                            precio_m = f"{precio_crudo[0]}.{precio_crudo[1:]}"
                        else:
                            precio_m = precio_crudo
                        
                        periodos.append(f"{mes}-{anio}")
                        demandas.append(demanda_kw)
                        consumos.append(consumo_kwh)
                        factores_potencia.append(f"{fact_potencia}%")
                        factores_carga.append(f"{fact_carga}%")
                        precios_medio.append(f"${precio_m}")
                        
                    except (ValueError, IndexError):
                        continue
                        
            if not periodos:
                return [{"error": "No se encontraron filas con meses válidos en el desglose de la página 2."}]
                        
            df_historico = pd.DataFrame({
                "Periodo": periodos,
                "Demanda (kW)": demandas,
                "Consumo total (kWh)": consumos,
                "Factor potencia": factores_potencia,
                "Factor carga": factores_carga,
                "Precio medio (MXN)": precios_medio
            })
            
            # DataFrame a lista nativa de diccionarios JSON
            registros_finales = df_historico.to_dict(orient="records")
            
            for registro in registros_finales:
                registro["KW en Punta Real"] = kw_punta_real
                
            return registros_finales
            
    except Exception as e:
        return [{"error": f"Error crítico al intentar procesar el PDF local: {str(e)}"}]
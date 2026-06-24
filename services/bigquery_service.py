import uuid
import logging
from google.cloud import bigquery

def salvar_inventario(dados_bot):
    """
    Salva inventário no BigQuery. O campo 'loc' deve ser string 
    no formato 'Lat: -XX, Long: -YY' ou endereço textual.
    """
    try:
        client = bigquery.Client(project="vtal-inventariorede-prd")
        table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
        
        # Converter Lat/Long para WKT (GEOGRAPHY)
        # BigQuery espera POINT(longitude latitude)
        loc_str = dados_bot.get('loc', 'N/A')
        wkt = "POINT(0 0)" # Valor fallback
        if "Lat:" in loc_str and "Long:" in loc_str:
            try:
                # Extrai números: "Lat: -22.88, Long: -43.46" -> POINT(-43.46 -22.88)
                parts = loc_str.replace("Lat:", "").replace("Long:", "").split(",")
                lat = parts[0].strip()
                lon = parts[1].strip()
                wkt = f"POINT({lon} {lat})"
            except:
                pass
        
        row_to_insert = {
            "id_registro": str(uuid.uuid4()),
            "user_id": int(dados_bot.get('user_id', 0)),
            "idsap": str(dados_bot.get('idsap', 'N/A')),
            "hostname": str(dados_bot.get('hostname', 'N/A')),
            "localizacao": wkt, 
            "fabricante": str(dados_bot.get('dados_ia', {}).get('fabricante', 'N/A')),
            "modelo": str(dados_bot.get('dados_ia', {}).get('modelo', 'N/A')),
            "funcao": str(dados_bot.get('dados_ia', {}).get('funcao', 'N/A')),
            "serial_number": str(dados_bot.get('dados_ia', {}).get('serial_number', 'N/A')),
            "gcs_url": str(dados_bot.get('gcs_url', 'N/A'))
        }

        errors = client.insert_rows_json(table_id, [row_to_insert])
        
        if errors:
            logging.error(f"Erro ao inserir linhas: {errors}")
            return False
        
        logging.info("✅ Inventário inserido com sucesso na tabela documentada.")
        return True

    except Exception as e:
        logging.error(f"❌ Erro crítico no BigQuery: {e}")
        return False
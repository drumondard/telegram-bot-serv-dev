import uuid
import logging

def salvar_inventario(dados_bot: dict, bq_client) -> bool:
    try:
        table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
        loc_str = dados_bot.get('loc', 'N/A')
        wkt = "POINT(0 0)"
        
        if "Lat:" in loc_str:
            parts = loc_str.replace("Lat:", "").replace("Long:", "").split(",")
            wkt = f"POINT({parts[1].strip()} {parts[0].strip()})"
        
        row = {
            "id_registro": str(uuid.uuid4()),
            "user_id": int(dados_bot.get('user_id', 0)),
            "idsap": str(dados_bot.get('idsap', 'N/A')),
            "hostname": str(dados_bot.get('hostname', 'N/A')),
            "localizacao": wkt,
            **dados_bot.get('dados_ia', {}),
            "gcs_url": str(dados_bot.get('gcs_url', 'N/A'))
        }
        
        errors = bq_client.insert_rows_json(table_id, [row])
        return not errors
    except Exception as e:
        logging.error(f"Erro no BigQuery: {e}")
        return False
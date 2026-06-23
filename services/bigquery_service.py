from google.cloud import bigquery
import os

def salvar_inventario(dados):
    """Grava os dados coletados pelo bot no BigQuery."""
    # O client utiliza as credenciais do ambiente
    client = bigquery.Client()
    table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
    
    rows_to_insert = [{
        "equipamento_id": dados['idsap'],
        "fabricante": dados['ia_data'].get('fabricante', 'N/A'),
        "modelo": dados['ia_data'].get('modelo', 'N/A'),
        "funcao": dados['ia_data'].get('funcao', 'N/A'),
        "serial_number": dados['ia_data'].get('serial_number', 'N/A'),
        "latitude": dados['latitude'],
        "longitude": dados['longitude'],
        "gcs_path": dados['gcs_url'],
        "status_confirmacao": "CONFIRMADO",
        "usuario_id": str(dados['user_id'])
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    return errors
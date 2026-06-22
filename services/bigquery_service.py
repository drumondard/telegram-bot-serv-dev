from google.cloud import bigquery

def salvar_inventario(dados):
    client = bigquery.Client()
    table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
    
    rows_to_insert = [{
        "equipamento_id": dados['idsap'],
        "fabricante": dados['ia_data']['fabricante'],
        "modelo": dados['ia_data']['modelo'],
        "funcao": dados['ia_data']['funcao'],
        "serial_number": dados['ia_data']['serial_number'],
        "latitude": dados['latitude'],
        "longitude": dados['longitude'],
        "gcs_path": dados['gcs_url'],
        "status_confirmacao": "CONFIRMADO",
        "usuario_id": str(dados['user_id'])
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    return errors
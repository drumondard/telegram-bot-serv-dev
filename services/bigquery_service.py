from google.cloud import bigquery
from google.oauth2 import service_account
import os
from datetime import datetime

def salvar_inventario(data):
    """
    Insere os dados do inventário na tabela: vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot
    """
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    credentials = service_account.Credentials.from_service_account_file(cred_path)
    client = bigquery.Client(credentials=credentials)
    
    # ID da tabela completo
    table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
    
    ia_data = data.get('dados_ia', {})
    
    # Mapeamento conforme o schema da sua tabela
    rows_to_insert = [{
        "equipamento_id": str(data.get('idsap', 'N/A')), # Usando idsap como ID do equipamento
        "data_criacao": datetime.utcnow().isoformat(),
        "fabricante": str(ia_data.get('fabricante', 'N/A')),
        "modelo": str(ia_data.get('modelo', 'N/A')),
        "funcao": str(ia_data.get('funcao', 'N/A')), # Adicionei campo extra no schema
        "serial_number": str(ia_data.get('serie', 'N/A')),
        "latitude": float(data.get('lat', 0.0)),
        "longitude": float(data.get('long', 0.0)),
        "precisao_gps": float(data.get('precisao', 0.0)),
        "gcs_path": str(data.get('gcs_url', 'N/A')),
        "status_confirmacao": "CONFIRMADO",
        "usuario_id": str(data.get('user_id', 'N/A')),
        "confianca_ia": float(ia_data.get('confianca', 0.0))
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"❌ Erros ao inserir no BigQuery: {errors}")
    else:
        print("✅ Dados salvos com sucesso na tabela tb_ref_foto_bot.")
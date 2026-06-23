from google.cloud import bigquery
from google.oauth2 import service_account
import os

def salvar_inventario(data):
    """
    Salva os dados do inventário no BigQuery.
    'data' deve conter: user_id, lat, long, idsap, hostname, gcs_url, dados_ia
    """
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    credentials = service_account.Credentials.from_service_account_file(cred_path)
    client = bigquery.Client(credentials=credentials)
    
    table_id = "seu-projeto.seu_dataset.sua_tabela"
    
    # Extração segura dos dados da IA
    ia_data = data.get('dados_ia', {})
    
    rows_to_insert = [{
        "user_id": str(data.get('user_id')),
        "lat": data.get('lat'),
        "long": data.get('long'),
        "idsap": data.get('idsap'),
        "hostname": data.get('hostname'),
        "gcs_url": data.get('gcs_url'),
        "modelo": ia_data.get('modelo', 'N/A'),
        "fabricante": ia_data.get('fabricante', 'N/A'),
        "data_registro": bigquery.Timestamp.utcnow().isoformat()
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"❌ Erro ao inserir no BigQuery: {errors}")
    else:
        print("✅ Dados salvos com sucesso no BigQuery.")
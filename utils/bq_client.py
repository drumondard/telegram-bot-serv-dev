from google.cloud import bigquery
import os

def get_bigquery_client():
    """
    Inicializa e retorna o cliente do BigQuery utilizando 
    as credenciais de serviço definidas nas variáveis de ambiente.
    """
    try:
        # A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS 
        # já deve estar apontando para o JSON no main.py
        client = bigquery.Client()
        return client
    except Exception as e:
        print(f"Erro ao inicializar cliente BigQuery: {e}")
        return None
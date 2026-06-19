import os
from google.cloud import storage
from google.oauth2 import service_account

class GCSService:
    def __init__(self, cred_path: str):
        """
        Inicializa o cliente do GCS usando o arquivo de credenciais.
        """
        self.credentials = service_account.Credentials.from_service_account_file(cred_path)
        self.client = storage.Client(credentials=self.credentials)

    def upload_file(self, bucket_name: str, source_file_path: str, destination_blob_name: str):
        """
        Realiza o upload de um arquivo local para um bucket específico.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(source_file_path)
            
            return f"gs://{bucket_name}/{destination_blob_name}"
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo para o GCS: {e}")
            raise e

# Exemplo de uso (pode ser instanciado no main.py ou dentro de uma feature)
# gcs_service = GCSService(cred_path=os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO"))
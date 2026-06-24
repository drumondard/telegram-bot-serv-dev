import logging
from google.cloud import storage

class GCSService:
    def __init__(self, credentials):
        # Certifique-se de que o projeto esteja correto
        self.client = storage.Client(credentials=credentials, project="vtal-inventariorede-prd")

    def upload_file(self, bucket_name: str, data, destination_blob_name: str) -> str:
        """Faz upload de bytes ou bytearray para o bucket especificado."""
        try:
            # FORÇA a conversão para bytes imutáveis aqui
            if isinstance(data, (bytearray, memoryview)):
                data = bytes(data)
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # upload_from_string aceita bytes, string ou buffer. 
            # Se for bytes, funciona direto.
            blob.upload_from_string(data, content_type='image/jpeg')
            return f"gs://{bucket_name}/{destination_blob_name}"
        except Exception as e:
            logging.error(f"❌ Erro ao enviar arquivo para o GCS: {e}")
            raise e
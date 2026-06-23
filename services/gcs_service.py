from google.cloud import storage
from google.oauth2 import service_account

class GCSService:
    def __init__(self, cred_path: str):
        self.credentials = service_account.Credentials.from_service_account_file(cred_path)
        self.client = storage.Client(credentials=self.credentials)

    def upload_file(self, bucket_name: str, data, destination_blob_name: str):
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Converte para bytes puro caso receba bytearray
            if isinstance(data, bytearray):
                data = bytes(data)
                
            blob.upload_from_string(data, content_type='image/jpeg')
            return f"gs://{bucket_name}/{destination_blob_name}"
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo para o GCS: {e}")
            raise e
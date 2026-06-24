import uuid
import logging
import os
from google.cloud import storage
from google.oauth2 import service_account

def upload_foto_gcs(image_bytes, user_id):
    try:
        # 1. Carrega as credenciais explicitamente do seu arquivo .env
        caminho_chave = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
        credentials = service_account.Credentials.from_service_account_file(caminho_chave)
        
        # 2. Inicializa o cliente com as credenciais corretas
        client = storage.Client(credentials=credentials, project="vtal-inventariorede-prd")
        
        bucket_name = "vtal-bucket-inventariorede-prd"
        # O caminho solicitado: fotos_bot_telegram/user_id/uuid.jpg
        blob_name = f"fotos_bot_telegram/{uuid.uuid4()}.jpg"
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # 3. Upload garantindo que image_bytes seja bytes puros
        blob.upload_from_string(bytes(image_bytes), content_type='image/jpeg')
        
        return f"gs://{bucket_name}/{blob_name}"
        
    except Exception as e:
        logging.error(f"❌ Erro crítico ao salvar no Bucket {bucket_name}: {e}")
        return "N/A"
    
    
    
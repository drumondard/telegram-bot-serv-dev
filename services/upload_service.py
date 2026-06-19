# /home/inventario/automacao/scripts_python/telegram_bot/services/upload_service.py
import os
from google.cloud import storage

def enviar_foto_para_bucket(photo_bytes, chat_id, file_unique_id):
    """Lógica de upload para o bucket GCS."""
    bucket_name = os.getenv('BUCKET_NAME')
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    file_path = f"telegram_uploads/{chat_id}_{file_unique_id}.jpg"
    blob = bucket.blob(file_path)
    blob.upload_from_string(photo_bytes, content_type='image/jpeg')
    return True
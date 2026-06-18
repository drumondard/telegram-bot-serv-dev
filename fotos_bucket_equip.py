from google.cloud import storage
import os

async def upload_para_bucket(update, context):
    # Sua lógica de handle_upload_gcs vai aqui
    client = storage.Client()
    bucket = client.bucket(os.getenv("BUCKET_NAME_FOTOS"))
    # ... resto do código ...
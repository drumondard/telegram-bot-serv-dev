

#### DESCONTINUADO #####

from google.cloud import storage
import os
import logging

async def upload_para_bucket(update, context):
    # Adicionamos uma mensagem de status inicial
    msg = await update.message.reply_text("⏳ Enviando para o GCS...")
    
    try:
        # Pega a foto de maior resolução
        photo_file = await update.message.photo[-1].get_file()
        
        # Inicializa cliente e bucket
        client = storage.Client()
        bucket = client.bucket(os.getenv("BUCKET_NAME_FOTOS"))
        
        # Define o caminho do arquivo
        file_name = f"uploads/{update.message.from_user.id}/{photo_file.file_unique_id}.jpg"
        blob = bucket.blob(file_name)
        
        # Download para memória e upload para GCS
        image_bytes = await photo_file.download_as_bytearray()
        blob.upload_from_string(image_bytes, content_type='image/jpeg')
        
        # Edita a mensagem original informando o sucesso
        await msg.edit_text("✅ Foto enviada com sucesso!")
        logging.info(f"Foto enviada por {update.message.from_user.id} para {file_name}")
        
    except Exception as e:
        # Em caso de erro (ex: Bucket não encontrado, rede, etc), avisa o usuário e loga o erro
        logging.error(f"Erro ao subir foto: {e}")
        await msg.edit_text("❌ Erro ao enviar foto para o GCS. Tente novamente mais tarde.")

##/home/inventario/telegram-bot-serv/features/fotos_bucket.py

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

# Diretório para armazenamento temporário
TEMP_DIR = "/home/inventario/telegram-bot-serv/data"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a foto recebida e faz o upload para o Bucket GCS."""
    
    # 1. Recupera o serviço de GCS injetado no main.py
    gcs_service = context.bot_data.get('gcs_service')
    if not gcs_service:
        await update.message.reply_text("❌ Erro: Serviço de Storage não inicializado.")
        return

    msg_status = await update.message.reply_text("📥 Recebendo imagem...")

    # 2. Garante que o diretório temporário existe
    os.makedirs(TEMP_DIR, exist_ok=True)

    # 3. Faz o download do arquivo de maior resolução disponível
    file = await update.message.photo[-1].get_file()
    file_id = update.message.photo[-1].file_id
    local_path = os.path.join(TEMP_DIR, f"{file_id}.jpg")

    try:
        await file.download_to_drive(local_path)
        
        # 4. Upload para o GCS
        # Defina o nome do seu bucket aqui (ou via .env para maior flexibilidade)
        bucket_name = "vtal-bucket-inventariorede-prd" 
        destination = f"fotos_bot_telegram/{update.message.from_user.id}/{file_id}.jpg"
        
        await msg_status.edit_text("☁️ Enviando para o Storage...")
        
        # Chama o serviço que criamos anteriormente
        gcs_uri = gcs_service.upload_file(bucket_name, local_path, destination)
        
        await msg_status.edit_text(f"✅ Foto salva com sucesso!\n\n`{gcs_uri}`", parse_mode='Markdown')
        logging.info(f"Foto salva por {update.message.from_user.id}: {gcs_uri}")

    except Exception as e:
        logging.error(f"Erro ao processar foto: {e}")
        await msg_status.edit_text("❌ Erro ao enviar foto para o bucket.")
    
    finally:
        # 5. Limpeza obrigatória do arquivo local
        if os.path.exists(local_path):
            os.remove(local_path)

def registrar_handlers_fotos(app):
    """Registra o handler de foto na aplicação."""
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
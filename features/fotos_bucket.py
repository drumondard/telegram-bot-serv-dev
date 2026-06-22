import logging
import os
import time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa foto, renomeia, envia ao GCS e limpa o ambiente local."""
    
    # 1. Validação de Estado
    if context.user_data.get('servico_ativo') != 'AGUARDANDO_FOTO':
        return await update.message.reply_text("⚠️ Use o menu para iniciar o processo.")

    msg = await update.message.reply_text("⏳ Processando e enviando...")
    
    # 2. Configuração de diretório temporário
    ##temp_dir = "/tmp/fotos_bot"
    temp_dir = "/home/inventario/telegram-bot-serv/data"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Garante a criação do ID de Grupo para fotos do mesmo equipamento
        if 'id_foto_grupo' not in context.user_data:
            context.user_data['id_foto_grupo'] = int(time.time() % 100000)

        file = await update.message.photo[-1].get_file()
        local_path = os.path.join(temp_dir, f"{file.file_unique_id}.jpg")
        
        # 3. Nomenclatura Profissional: Grupo_Unico_SAP_Host
        id_grupo = context.user_data['id_foto_grupo']
        id_unico = file.file_unique_id
        id_sap = context.user_data.get('id_sap', 'SEM_IDSAP')
        host = context.user_data.get('hostname', 'SEM_HOST')
        
        nome_arquivo = f"{id_grupo}_{id_unico}_{id_sap}_{host}.jpg"
        destination = f"fotos_bot_telegram/{nome_arquivo}"
        
        # 4. Download, Upload e Limpeza
        await file.download_to_drive(custom_path=local_path)
        
        gcs_service = context.bot_data.get('gcs_service')
        gcs_uri = gcs_service.upload_file("vtal-bucket-inventariorede-prd", local_path, destination)
        
        # Remove arquivo local após upload
        if os.path.exists(local_path):
            os.remove(local_path)

        # 5. Menu de Fluxo (Loop)
        teclado = [
            [KeyboardButton("📸 Tirar outra do mesmo")], 
            [KeyboardButton("🆕 Novo equipamento")], 
            [KeyboardButton("🏁 Finalizar")]
        ]
        
        await msg.edit_text(f"✅ Salvo como: `{nome_arquivo}`", parse_mode='Markdown')
        await update.message.reply_text("O que deseja fazer?", reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True))
        
    except Exception as e:
        logging.error(f"Erro ao processar foto: {e}")
        await msg.edit_text("❌ Erro ao salvar arquivo no bucket.")

def registrar_handlers_fotos(app):
    """Registra o handler de fotos."""
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
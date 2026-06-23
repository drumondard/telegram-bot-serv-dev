from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento
from services.bigquery_service import salvar_inventario

LOCALIZACAO, SAP, HOSTNAME, FOTO, CONFIRMACAO = range(5)

async def iniciar_inventario(update, context):
    context.user_data.clear()
    await update.message.reply_text("🚀 Iniciando novo inventário.\nEnvie sua localização:", reply_markup=ReplyKeyboardRemove())
    return LOCALIZACAO

async def receber_localizacao(update, context):
    context.user_data.update({'lat': update.message.location.latitude, 'long': update.message.location.longitude})
    await update.message.reply_text("✅ Localização capturada! Digite o ID SAP:")
    return SAP

async def receber_sap(update, context):
    context.user_data['idsap'] = update.message.text
    await update.message.reply_text("✅ ID SAP registrado. Qual o Hostname?")
    return HOSTNAME

async def receber_hostname(update, context):
    context.user_data['hostname'] = update.message.text
    await update.message.reply_text("📸 Perfeito! Envie a foto do equipamento.")
    return FOTO

async def processar_foto(update, context):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    
    dados_ia = extrair_dados_equipamento(image_bytes)
    context.user_data.update({'dados_ia': dados_ia, 'foto_bytes': image_bytes})
    
    keyboard = [[InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')]]
    await update.message.reply_text(f"IA: {dados_ia.get('modelo', 'N/A')}. Confirma?", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMACAO

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirmar':
        gcs = context.bot_data.get('gcs_service')
        nome = f"inventario/{context.user_data['idsap']}_{context.user_data['hostname']}.jpg"
        url = gcs.upload_file("vtal-bucket-inventariorede-prd", context.user_data['foto_bytes'], nome)
        
        salvar_inventario({**context.user_data, 'gcs_url': url, 'user_id': update.effective_user.id})
        await query.edit_message_text("✅ Salvo com sucesso no BigQuery!")
    
    context.user_data.clear()
    return ConversationHandler.END

inventario_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'(?i)^(📷 Enviar Fotos)$'), iniciar_inventario)],
    states={
        LOCALIZACAO: [MessageHandler(filters.LOCATION, receber_localizacao)],
        SAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sap)],
        HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_hostname)],
        FOTO: [MessageHandler(filters.PHOTO, processar_foto)],
        CONFIRMACAO: [CallbackQueryHandler(button_handler)]
    },
    fallbacks=[],
    per_message=False
)
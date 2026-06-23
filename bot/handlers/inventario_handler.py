import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento
from services.bigquery_service import salvar_inventario

# Definição dos estados da conversa
LOCALIZACAO, SAP, HOSTNAME, FOTO, CONFIRMACAO = range(5)

async def iniciar_inventario(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text(
        "🚀 Iniciando inventário.\nEnvie sua localização (clipe > Localização).",
        reply_markup=ReplyKeyboardRemove()
    )
    return LOCALIZACAO

async def receber_localizacao(update: Update, context: CallbackContext):
    context.user_data.update({'lat': update.message.location.latitude, 'long': update.message.location.longitude})
    await update.message.reply_text("✅ Localização capturada! Digite o ID SAP:")
    return SAP

async def receber_sap(update: Update, context: CallbackContext):
    context.user_data['idsap'] = update.message.text
    await update.message.reply_text("✅ ID SAP registrado. Qual o Hostname?")
    return HOSTNAME

async def receber_hostname(update: Update, context: CallbackContext):
    context.user_data['hostname'] = update.message.text
    await update.message.reply_text("📸 Perfeito! Agora, envie a foto do equipamento.")
    return FOTO

async def processar_foto(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    
    status_msg = await update.message.reply_text("🤖 Analisando com IA...")
    
    dados_ia = extrair_dados_equipamento(image_bytes)
    context.user_data.update({'dados_ia': dados_ia, 'foto_bytes': image_bytes})
    
    resumo = (f"🔍 **Identificação:**\n"
              f"Fab: {dados_ia.get('fabricante', 'N/A')}\n"
              f"Mod: {dados_ia.get('modelo', 'N/A')}\n\n"
              f"Confirma?")
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')],
        [InlineKeyboardButton("✏️ Editar", callback_data='editar')]
    ]
    await status_msg.edit_text(resumo, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMACAO

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirmar':
        gcs = context.bot_data.get('gcs_service')
        nome = f"inv/{context.user_data['idsap']}_{context.user_data['hostname']}.jpg"
        url = gcs.upload_file("vtal-bucket-inventariorede-prd", context.user_data['foto_bytes'], nome)
        
        salvar_inventario({**context.user_data, 'gcs_url': url, 'user_id': update.effective_user.id})
        await query.edit_message_text("✅ Salvo no BigQuery!")
        context.user_data.clear()
        return ConversationHandler.END
    
    elif query.data == 'editar':
        await query.edit_message_text("✏️ Reiniciando dados. Digite o novo ID SAP:")
        return SAP

inventario_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'(?i)^(📷 Enviar Fotos)$'), iniciar_inventario)],
    states={
        LOCALIZACAO: [MessageHandler(filters.LOCATION, receber_localizacao)],
        SAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sap)],
        HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_hostname)],
        FOTO: [MessageHandler(filters.PHOTO, processar_foto)],
        CONFIRMACAO: [CallbackQueryHandler(button_handler)]
    },
    fallbacks=[CommandHandler("cancelar", lambda u, c: ConversationHandler.END)],
    allow_reentry=True,
    per_message=False
)
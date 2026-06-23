import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento
from services.bigquery_service import salvar_inventario

# Definição dos estados da conversa
LOCALIZACAO, SAP, HOSTNAME, FOTO, CONFIRMACAO = range(5)

# --- Funções do Fluxo de Conversação ---

async def iniciar_inventario(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text(
        "🚀 Iniciando novo inventário.\nPor favor, envie sua localização atual.",
        reply_markup=ReplyKeyboardRemove()
    )
    return LOCALIZACAO

async def receber_localizacao(update: Update, context: CallbackContext):
    if not update.message.location:
        await update.message.reply_text("Por favor, envie a localização utilizando o clipe de anexo.")
        return LOCALIZACAO
    
    context.user_data['lat'] = update.message.location.latitude
    context.user_data['long'] = update.message.location.longitude
    await update.message.reply_text("✅ Localização capturada! Agora, digite o ID SAP do equipamento:")
    return SAP

async def receber_sap(update: Update, context: CallbackContext):
    context.user_data['idsap'] = update.message.text
    await update.message.reply_text("✅ ID SAP registrado. Qual o Hostname do equipamento?")
    return HOSTNAME

async def receber_hostname(update: Update, context: CallbackContext):
    context.user_data['hostname'] = update.message.text
    await update.message.reply_text("📸 Perfeito! Agora, envie a foto do equipamento para identificação pela IA.")
    return FOTO

async def processar_foto(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    
    status_msg = await update.message.reply_text("🤖 Analisando imagem com a IA VTAL... Aguarde.")
    
    dados_ia = extrair_dados_equipamento(image_bytes)
    context.user_data.update({'dados_ia': dados_ia, 'foto_bytes': image_bytes})
    
    resumo = (f"🔍 **Equipamento Identificado:**\n"
              f"**Fabricante:** {dados_ia.get('fabricante', 'N/A')}\n"
              f"**Modelo:** {dados_ia.get('modelo', 'N/A')}\n\n"
              f"Confirma os dados acima?")
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')],
        [InlineKeyboardButton("✏️ Editar", callback_data='editar')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await status_msg.edit_text(resumo, parse_mode='Markdown', reply_markup=reply_markup)
    return CONFIRMACAO

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirmar':
        gcs_service = context.bot_data.get('gcs_service')
        nome_arq = f"inventario/{context.user_data['idsap']}_{context.user_data['hostname']}.jpg"
        
        # Faz o upload
        gcs_url = gcs_service.upload_file("vtal-bucket-inventariorede-prd", context.user_data['foto_bytes'], nome_arq)
        
        # Salva no BigQuery
        dados_finais = {
            'idsap': context.user_data['idsap'],
            'hostname': context.user_data['hostname'],
            'ia_data': context.user_data['dados_ia'],
            'latitude': context.user_data['lat'],
            'longitude': context.user_data['long'],
            'gcs_url': gcs_url,
            'user_id': update.effective_user.id
        }
        
        salvar_inventario(dados_finais)
        await query.edit_message_text("✅ Inventário concluído e registrado no BigQuery!")
    else:
        await query.edit_message_text("✏️ Modo de edição acionado.")
        
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text("❌ Inventário cancelado.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- REGISTRO CORRIGIDO (Dicionário com Listas) ---
inventario_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("novo_inventario", iniciar_inventario)],
    states={
        LOCALIZACAO: [MessageHandler(filters.LOCATION, receber_localizacao)],
        SAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sap)],
        HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_hostname)],
        FOTO: [MessageHandler(filters.PHOTO, processar_foto)],
        CONFIRMACAO: [CallbackQueryHandler(button_handler)]
    },
    fallbacks=[CommandHandler("cancelar", cancelar)],
    allow_reentry=True,
    per_message=False
)
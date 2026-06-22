import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento

# Definição dos estados da conversa
LOCALIZACAO, SAP, HOSTNAME, FOTO, CONFIRMACAO = range(5)

# --- Funções do Fluxo de Conversação ---

async def iniciar_inventario(update: Update, context: CallbackContext):
    """Inicia o fluxo de inventário, limpando estados anteriores."""
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
    context.user_data['dados_ia'] = dados_ia
    
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
        await query.edit_message_text("✅ Inventário concluído com sucesso!")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await query.edit_message_text("✏️ Modo de edição ativado (implemente aqui a lógica).")
        return CONFIRMACAO

async def cancelar(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text("❌ Inventário cancelado.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Registro do ConversationHandler (DEVE FICAR NO FINAL) ---

inventario_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("novo_inventario", iniciar_inventario),
        MessageHandler(filters.Regex(r'(?i).*Enviar Fotos.*'), iniciar_inventario)
    ],
    states={
        LOCALIZACAO: [MessageHandler(filters.LOCATION, receber_localizacao)],
        SAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sap)],
        HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_hostname)],
        FOTO: [MessageHandler(filters.PHOTO, processar_foto)],
        # O filtro 'pattern' garante que este handler só responda a botões deste fluxo
        CONFIRMACAO: [CallbackQueryHandler(button_handler, pattern='^(confirmar|editar)$')]
    },
    fallbacks=[CommandHandler("cancelar", cancelar)],
    allow_reentry=True
)
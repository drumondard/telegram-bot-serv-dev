from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters, CallbackContext
from features.rede_ftth import processar_consulta_rede

# Estado da conversa para a rede
AGUARDANDO_GPS = 1

async def iniciar_rede(update: Update, context: CallbackContext):
    """Inicia o fluxo da Rede FTTH."""
    await update.message.reply_text(
        "🌐 **Rede FTTH ativa.**\nEnvie sua localização atual (clique no clipe > Localização).", 
        reply_markup=ReplyKeyboardRemove(), 
        parse_mode='Markdown'
    )
    return AGUARDANDO_GPS

async def receber_gps(update: Update, context: CallbackContext):
    """
    Recebe a localização e chama o processador de rede.
    Como processar_consulta_rede já espera um objeto Update, 
    nós o reutilizamos aqui.
    """
    await processar_consulta_rede(update, context)
    return ConversationHandler.END

# Definindo o ConversationHandler específico para a Rede
rede_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'(?i)^(🌐 Rede FTTH)$'), iniciar_rede)],
    states={
        AGUARDANDO_GPS: [MessageHandler(filters.LOCATION, receber_gps)]
    },
    fallbacks=[],
    per_message=False
)
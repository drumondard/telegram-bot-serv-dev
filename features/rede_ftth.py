import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters, CallbackContext
from services.rede_service import consultar_rede

# Estado da conversa
AGUARDANDO_GPS = 1

async def iniciar_rede(update: Update, context: CallbackContext):
    """Entrada do fluxo: pede a localização."""
    await update.message.reply_text(
        "🌐 **Rede FTTH ativa.**\nEnvie sua localização atual (clique no clipe > Localização).",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return AGUARDANDO_GPS

async def processar_consulta_rede(update: Update, context: CallbackContext):
    """Processamento da consulta no BigQuery."""
    # Recupera o cliente injetado no main.py
    bq_client = context.bot_data.get('bq_client')
    
    if not bq_client:
        logging.error("bq_client não encontrado em bot_data!")
        await update.message.reply_text("❌ Erro interno: Cliente BigQuery não configurado.")
        return ConversationHandler.END

    lat = update.message.location.latitude
    lon = update.message.location.longitude
    tipo_rede = "🌐 Rede FTTH"
    
    status_msg = await update.message.reply_text("🔎 Consultando base de rede...")

    try:
        resultados = consultar_rede(lon, lat, tipo_rede, bq_client)
        rows = list(resultados)
        
        if not rows:
            await status_msg.edit_text(f"📭 Nenhuma rede {tipo_rede} próxima.")
        else:
            resposta = f"🔍 **Resultado para sua localização:**\n📡 **Tipo:** {tipo_rede}\n───────────────────\n\n"
            for row in rows[:5]:
                id_cdoe = getattr(row, 'id_cdoe', 'N/A')
                status = getattr(row, 'status', 'N/A')
                dist = getattr(row, 'distancia_metros', 0)
                
                resposta += f"📦 **ID:** `{id_cdoe}` | 📊 {status}\n"
                resposta += f"📏 Distância: **{int(dist)}m**\n───────────────────\n"
            
            await status_msg.edit_text(resposta, parse_mode='Markdown', disable_web_page_preview=True)

    except Exception as e:
        logging.error(f"Erro na consulta FTTH: {e}")
        await status_msg.edit_text("⚠️ Erro ao processar dados técnicos.")
        
    return ConversationHandler.END

# Definimos o handler aqui para importar no main.py
rede_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'(?i)^(🌐 Rede FTTH)$'), iniciar_rede)],
    states={
        AGUARDANDO_GPS: [MessageHandler(filters.LOCATION, processar_consulta_rede)]
    },
    fallbacks=[],
    per_message=False
)
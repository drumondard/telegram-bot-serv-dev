from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o menu principal e limpa qualquer estado anterior."""
    context.user_data.clear()
    teclado = [[KeyboardButton("🌐 Rede FTTH")], [KeyboardButton("📷 Enviar Fotos")]]
    await update.message.reply_text(
        "🛰️ **InventarIAr Vtal - Agente 2.0**\n\nSelecione o serviço:",
        reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True, one_time_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Orquestrador principal de mensagens."""
    texto = update.message.text
    texto_low = texto.lower()
    estado = context.user_data.get('servico_ativo')

    # --- 1. Rota de Emergência / Reset ---
    if "menu inicial" in texto_low or "🏁 finalizar" in texto_low or "/start" in texto_low:
        return await start(update, context)

    # --- 2. Rota de Rede FTTH (Prioridade Alta) ---
    if "rede ftth" in texto_low:
        context.user_data['servico_ativo'] = 'REDE'
        context.user_data['tipo_rede'] = "🌐 Rede FTTH"
        kb = [[KeyboardButton("📍 Enviar GPS", request_location=True)], [KeyboardButton("🏁 Finalizar")]]
        await update.message.reply_text(
            "✅ Serviço Ativo: **🌐 Rede FTTH**\nEnvie seu GPS para iniciar:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
            parse_mode='Markdown'
        )
        return

    # --- 3. Rota de Envio de Fotos (Início) ---
    if "enviar fotos" in texto_low or "📷" in texto:
        context.user_data['servico_ativo'] = 'AGUARDANDO_SAP'
        kb = [[KeyboardButton("Não tenho SAP")]]
        await update.message.reply_text(
            "🆔 **Passo 1:** Digite o ID SAP (ou clique em 'Não tenho SAP'):", 
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    # --- 4. Estados de Coleta (Identificação) ---
    if estado == 'AGUARDANDO_SAP':
        context.user_data['id_sap'] = texto if "não tenho" not in texto_low else "SEM_SAP"
        context.user_data['servico_ativo'] = 'AGUARDANDO_HOST'
        kb = [[KeyboardButton("Não tenho Hostname")]]
        await update.message.reply_text(
            "🆔 **Passo 2:** Digite o Hostname (ou clique em 'Não tenho Hostname'):", 
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
        return

    if estado == 'AGUARDANDO_HOST':
        context.user_data['hostname'] = texto if "não tenho" not in texto_low else "SEM_HOST"
        context.user_data['servico_ativo'] = 'AGUARDANDO_FOTO'
        await update.message.reply_text(
            "✅ Identificação concluída! Agora envie a foto do equipamento.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # --- 5. Rota de Loop (Pós-upload) ---
    if "tirar outra do mesmo" in texto_low:
        context.user_data['servico_ativo'] = 'AGUARDANDO_FOTO'
        await update.message.reply_text("📸 Aguardando próxima foto para este equipamento...")
        return
    
    if "novo equipamento" in texto_low:
        context.user_data.pop('id_foto_grupo', None)
        context.user_data['servico_ativo'] = 'AGUARDANDO_SAP'
        await update.message.reply_text("🆔 Reiniciando... Passo 1: Digite o ID SAP:")
        return

    await update.message.reply_text("Comando não reconhecido. Use o menu principal.")
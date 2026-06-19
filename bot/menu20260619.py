# /home/inventario/telegram-bot-serv/menu.py

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

# Importamos as features para que o menu possa interagir com elas se necessário
from features import rede_ftth

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o menu principal do InventarIAr."""
    teclado = [
        [KeyboardButton("🌐 Rede FTTH")],
        [KeyboardButton("📷 Enviar Fotos")],
        [KeyboardButton("🔍 Identificação da última foto (Em breve)")]
    ]
    await update.message.reply_text(
        "🛰️ **InventarIAr Vtal**\n\nSelecione o serviço desejado:",
        reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Orquestrador de mensagens de texto."""
    texto = update.message.text
    texto_low = texto.lower()
    
    # 1. Lógica de encerramento
    if any(x in texto_low for x in ["encerrar", "não", "nao", "obrigado"]):
        await update.message.reply_text(
            "👍 Consulta finalizada.", 
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear() # Limpa estados ativos
        return

    # 2. Lógica de navegação para Menu Inicial
    if any(x in texto_low for x in ["nova consulta", "menu inicial", "sim", "voltar"]):
        context.user_data.clear()
        return await start(update, context)

    # 3. Lógica para o Módulo de Envio de Fotos
    if "enviar fotos" in texto_low or "📷" in texto:
        context.user_data['servico_ativo'] = 'UPLOAD_FOTO'
        await update.message.reply_text(
            "📸 **Modo Upload Ativo**\nEnvie a foto que deseja salvar no Bucket.",
            parse_mode='Markdown'
        )
        return

    # 4. Lógica de Seleção de Rede FTTH
    if "rede ftth" in texto_low:
        context.user_data['servico_ativo'] = 'REDE'
        context.user_data['tipo_rede'] = "🌐 Rede FTTH"
        
        kb = [[KeyboardButton("📍 Enviar GPS", request_location=True)], [KeyboardButton("⬅️ Menu Inicial")]]
        await update.message.reply_text(
            "✅ Serviço Ativo: **🌐 Rede FTTH**\nEnvie seu GPS para iniciar a consulta:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
            parse_mode='Markdown'
        )
        return

    # 5. Fallback para comandos não reconhecidos
    await update.message.reply_text("Comando não reconhecido. Use o menu ou envie uma localização.")
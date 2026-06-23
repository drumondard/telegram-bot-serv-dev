from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o menu principal."""
    context.user_data.clear()
    teclado = [[KeyboardButton("🌐 Rede FTTH")], [KeyboardButton("📷 Enviar Fotos")]]
    await update.message.reply_text(
        "🛰️ **InventarIAr Vtal - Agente 2.0**\n\nSelecione o serviço:",
        reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True, one_time_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback para mensagens não reconhecidas."""
    await update.message.reply_text("Opção não reconhecida. Use /start para ver o menu.")
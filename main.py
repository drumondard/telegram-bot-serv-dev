from telegram.ext import Application, CommandHandler, MessageHandler, filters
from menu import start, handle_message, handle_photo_router
from dotenv import load_dotenv
import os

load_dotenv("/home/inventario/automacao/config/.env")

if __name__ == '__main__':
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()
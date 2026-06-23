import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Importações dos módulos
from bot import menu
from bot.handlers.inventario_handler import inventario_conv_handler
from bot.handlers.rede_handler import rede_conv_handler
from services.gcs_service import GCSService

# Carregamento do arquivo .env
load_dotenv("/home/inventario/automacao/config/.env")

def main():
    # Garantir que o ambiente utilize os proxies definidos no .env
    proxy = os.getenv("HTTPS_PROXY")
    if proxy:
        os.environ['https_proxy'] = proxy
        os.environ['all_proxy'] = proxy
        print(f"🌐 Proxy configurado: {proxy}")

    token = os.getenv("TELEGRAM_DEV_TOKEN")
    if not token:
        print("ERRO: Token TELEGRAM_DEV_TOKEN não encontrado no .env.")
        return

    # Inicialização da aplicação (sem argumentos de proxy complexos)
    app = Application.builder().token(token).build()

    # Injeção de dependência dos serviços
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    if cred_path and os.path.exists(cred_path):
        app.bot_data['gcs_service'] = GCSService(cred_path)
    
    # --- REGISTRO DE HANDLERS ---
    # A ordem aqui define quem "escuta" primeiro.
    
    app.add_handler(inventario_conv_handler)
    app.add_handler(rede_conv_handler)
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    
    print("🚀 Bot operacional.")
    app.run_polling()

if __name__ == '__main__':
    main()
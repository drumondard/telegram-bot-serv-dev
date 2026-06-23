import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application

# --- CORREÇÃO: Certifique-se de que este import existe ---
from services.gcs_service import GCSService 
from services.bigquery_service import salvar_inventario
from bot.handlers.inventario_handler import inventario_conv_handler

# Carregar o .env (ajuste o caminho se necessário)
load_dotenv("/home/inventario/automacao/config/.env")

def main():
    token = os.getenv("TELEGRAM_DEV_TOKEN")
    if not token:
        print("ERRO: Token não encontrado.")
        return

    app = Application.builder().token(token).build()

    # Agora o GCSService será reconhecido
    app.bot_data['gcs_service'] = GCSService(os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO"))
    
    # Registro do handler
    app.add_handler(inventario_conv_handler)
    
    print("🚀 Bot operacional.")
    app.run_polling()

if __name__ == '__main__':
    main()
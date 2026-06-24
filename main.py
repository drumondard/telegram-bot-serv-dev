'''
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google.cloud import bigquery
from google.oauth2 import service_account

# Imports dos módulos
from bot import menu
from bot.handlers.inventario_handler import inventario_conv_handler
from features.rede_ftth import rede_conv_handler
from services.gcs_service import GCSService

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
load_dotenv("/home/inventario/automacao/config/.env")

def main():
    token = os.getenv("TELEGRAM_DEV_TOKEN")
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    
    if not token or not cred_path:
        print("❌ ERRO CRÍTICO: Variáveis de ambiente faltando.")
        return

    # Injeção de Dependências
    credentials = service_account.Credentials.from_service_account_file(cred_path)
    
    app = Application.builder().token(token).build()
    
    # Injetando serviços no bot_data
    app.bot_data['gcs_service'] = GCSService(credentials)
    app.bot_data['bq_client'] = bigquery.Client(credentials=credentials, project="vtal-inventariorede-prd")

    # Registro de Handlers
    app.add_handler(rede_conv_handler)
    app.add_handler(inventario_conv_handler)
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    
    print("🚀 Bot operacional.")
    app.run_polling()

if __name__ == '__main__':
    main()
'''

import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google.cloud import bigquery
from google.oauth2 import service_account

from bot import menu
from bot.handlers.inventario_handler import inventario_conv_handler
from features.rede_ftth import rede_conv_handler
from services.gcs_service import GCSService

logging.basicConfig(level=logging.INFO)
load_dotenv("/home/inventario/automacao/config/.env")

def main():
    token = os.getenv("TELEGRAM_DEV_TOKEN")
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    
    # Cria o objeto de credenciais UMA VEZ aqui
    credentials = service_account.Credentials.from_service_account_file(cred_path)
    
    app = Application.builder().token(token).build()
    
    # Injeta o objeto autenticado (resolve o AttributeError anterior)
    app.bot_data['gcs_service'] = GCSService(credentials)
    app.bot_data['bq_client'] = bigquery.Client(credentials=credentials, project="vtal-inventariorede-prd")

    app.add_handler(rede_conv_handler)
    app.add_handler(inventario_conv_handler)
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    
    print("🚀 Bot operacional.")
    app.run_polling()

if __name__ == '__main__':
    main()
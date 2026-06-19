# /home/inventario/telegram-bot-serv/main.py

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google.cloud import bigquery
from google.oauth2 import service_account

# Importação dos seus módulos locais
import menu
import rede_ftth

# 1. Definição do caminho fixo (Hardcoded para evitar falhas de leitura no .env)
CRED_PATH = "/home/inventario/automacao/conta_servico/vtal-inventariorede-prd-GA58818.json"
TELEGRAM_TOKEN = "8694791486:AAE0IppzpX4JbLLwnLpKUijjEVcwK-5A8Oo"

# 2. Inicialização Segura do Cliente BigQuery
def get_bq_client():
    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError(f"❌ Credencial não encontrada em: {CRED_PATH}")
    
    # Autenticação explícita com o arquivo JSON
    credentials = service_account.Credentials.from_service_account_file(CRED_PATH)
    
    print(f"✅ DEBUG: Autenticando com a conta: {credentials.service_account_email}")
    
    # Forçamos o projeto de produção para garantir que a consulta seja executada no escopo correto
    return bigquery.Client(
        credentials=credentials, 
        project="vtal-inventariorede-prd"
    )

# Inicializa o cliente
bq_client = get_bq_client()

# 3. Configuração de Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

def main():
    print("🚀 InventarIAr Vtal - Iniciando Bot...")
    
    # Inicialização do Bot
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, rede_ftth.processar_consulta_rede))

    print("✅ Application started - Monitorando...")
    
    # Roda o bot sem conflitos de loop de eventos
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
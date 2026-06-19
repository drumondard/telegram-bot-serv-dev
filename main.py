import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google.cloud import bigquery
from google.oauth2 import service_account

# Importação dos módulos da nova arquitetura
from bot import menu
from features import rede_ftth, fotos_bucket
from services.gcs_service import GCSService

# Caminho fixo para o arquivo de configuração (.env)
ENV_PATH = "/home/inventario/automacao/config/.env"
load_dotenv(ENV_PATH)

# Recupera as variáveis do .env
CRED_PATH = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_DEV_TOKEN")

def main():
    # 1. Validação crítica de ambiente
    if not CRED_PATH or not TELEGRAM_TOKEN:
        raise EnvironmentError("❌ Erro: Credenciais ou Token não encontrados nas variáveis de ambiente.")

    # 2. Configuração de Logs
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # 3. Inicialização dos Serviços de Infraestrutura
    try:
        # Autenticação BigQuery
        credentials = service_account.Credentials.from_service_account_file(CRED_PATH)
        bq_client = bigquery.Client(credentials=credentials, project="vtal-inventariorede-prd")
        
        # Inicialização Serviço GCS
        gcs_service = GCSService(CRED_PATH)
    except Exception as e:
        logging.error(f"Erro ao inicializar clientes de GCP: {e}")
        return

    # 4. Inicialização e Injeção de Dependência no Bot
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Injetamos os serviços no bot_data para uso em qualquer módulo
    app.bot_data['bq_client'] = bq_client
    app.bot_data['gcs_service'] = gcs_service

    # 5. Registro de Handlers (Orquestração)
    
    # Comandos e Menu Principal
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))

    # Registro dos Módulos (Features)
    rede_ftth.registrar_handlers_rede(app)
    fotos_bucket.registrar_handlers_fotos(app)

    print("🚀 InventarIAr Vtal - Agente 2.0 Operacional.")
    
    # 6. Execução
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
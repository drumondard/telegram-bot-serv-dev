import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google.cloud import bigquery

# Imports dos seus módulos
from bot import menu
from bot.handlers.inventario_handler import inventario_conv_handler
from features.rede_ftth import rede_conv_handler
from services.gcs_service import GCSService

# Carrega o arquivo .env do caminho absoluto
ENV_PATH = "/home/inventario/automacao/config/.env"
load_dotenv(ENV_PATH)

def main():
    # 1. Validação do Token
    token = os.getenv("TELEGRAM_DEV_TOKEN")
    if not token:
        print(f"ERRO CRÍTICO: Token não encontrado em {ENV_PATH}")
        return

    # 2. Configuração da aplicação
    app = Application.builder().token(token).build()

    # 3. Injeção de Serviços (BotData)
    # Certifique-se de que o caminho da credencial GCP esteja correto no seu .env
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    
    app.bot_data['gcs_service'] = GCSService(cred_path)
    
    # Inicializa e injeta o cliente BigQuery explicitamente
    try:
        bq_client = bigquery.Client.from_service_account_json(cred_path)
        app.bot_data['bq_client'] = bq_client
        print("✅ BigQuery Client configurado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao configurar BigQuery: {e}")
        return

    # 4. REGISTRO DE HANDLERS (Ordem de prioridade é fundamental)
    
    # A) ConversationHandlers primeiro (Eles capturam apenas quando o fluxo está ativo)
    app.add_handler(rede_conv_handler)
    app.add_handler(inventario_conv_handler)
    
    # B) Comandos e mensagens genéricas (Por último)
    app.add_handler(CommandHandler("start", menu.start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    
    print("🚀 Bot operacional e aguardando comandos.")
    app.run_polling()

if __name__ == '__main__':
    main()
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
ENV_PATH = "/home/inventario/automacao/config/.env"
load_dotenv(ENV_PATH)

def main():
    # Validação do token
    token = os.getenv("TELEGRAM_DEV_TOKEN")
    if not token:
        print("ERRO: Token TELEGRAM_DEV_TOKEN não encontrado no .env.")
        return

    # Construção da aplicação com timeout aumentado para evitar erros de conexão
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(read_timeout=30.0, connect_timeout=30.0)
    
    app = Application.builder().token(token).request(request).build()

    # Injeção de dependência dos serviços
    cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
    if cred_path:
        app.bot_data['gcs_service'] = GCSService(cred_path)
    
    # --- REGISTRO DE HANDLERS (ORDEM IMPORTANTE) ---
    
    # 1. Fluxos de Conversação (Prioridade Máxima)
    # Eles só capturam se o usuário clicar nos botões específicos configurados neles
    app.add_handler(inventario_conv_handler)
    app.add_handler(rede_conv_handler)
    
    # 2. Comando de Início
    app.add_handler(CommandHandler("start", menu.start))
    
    # 3. Fallback para qualquer outra mensagem de texto (Prioridade Mínima)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu.handle_message))
    
    print("🚀 Bot operacional e aguardando interações.")
    app.run_polling()

if __name__ == '__main__':
    main()
from telegram.ext import Application
import os

def iniciar_bot(token):
    """Inicializa a aplicação do Telegram."""
    return Application.builder().token(token).build()
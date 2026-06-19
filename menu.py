# /home/inventario/telegram-bot-serv/menu.py

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
import rede_ftth
import fotos_bucket_equip

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o Menu Principal inicial."""
    teclado = [
        [KeyboardButton("🌐 Rede FTTH")],
        [KeyboardButton("📷 Enviar Fotos")],
        [KeyboardButton("🔍 Identificação da última foto")]
    ]
    await update.message.reply_text(
        "🛰️ **InventarIAr Vtal - Agente**\n\nSelecione o serviço desejado:",
        reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def exibir_menu_loop(update: Update):
    """Exibe o menu de opções após o término de um processo."""
    teclado_loop = [
        [KeyboardButton("🔄 Nova Consulta"), KeyboardButton("⬅️ Menu Inicial")],
        [KeyboardButton("❌ Encerrar Atendimento")]
    ]
    await update.message.reply_text(
        "O que deseja fazer agora?", 
        reply_markup=ReplyKeyboardMarkup(teclado_loop, resize_keyboard=True)
    )

async def handle_photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roteador para fotos."""
    servico = context.user_data.get('servico_ativo')
    if servico == 'UPLOAD_FOTO':
        await fotos_bucket_equip.handle_upload_gcs(update, context)
    else:
        await update.message.reply_text("⚠️ Por favor, selecione '📷 Enviar Fotos' no menu antes.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa textos e chamadas de estados dos módulos com verificação de segurança."""
    
    # Verificação de segurança: evita erro se a mensagem for None (ex: GPS ou eventos)
    if not update.message or not update.message.text:
        # Se for localização e o estado for REDE, encaminha para o módulo
        if update.message and update.message.location and context.user_data.get('servico_ativo') == 'REDE':
            await rede_ftth.processar_consulta_rede(update, context)
        return

    texto = update.message.text
    texto_low = texto.lower()

    # 1. Comandos de Navegação e Encerramento
    if any(x in texto_low for x in ["encerrar", "não", "nao", "obrigado"]):
        await update.message.reply_text("👍 Consulta finalizada.", reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return

    if any(x in texto_low for x in ["nova consulta", "menu inicial", "sim", "voltar"]):
        return await start(update, context)

    # 2. Seleção de Módulos pelo Usuário
    if texto == "📷 Enviar Fotos":
        context.user_data['servico_ativo'] = 'UPLOAD_FOTO'
        await update.message.reply_text("📸 **Modo Upload Ativo**\nEnvie a foto do equipamento.")
        return

    if texto == "🌐 Rede FTTH":
        context.user_data['servico_ativo'] = 'REDE'
        context.user_data['tipo_rede'] = texto
        kb = [[KeyboardButton("📍 Enviar GPS", request_location=True)], [KeyboardButton("⬅️ Menu Inicial")]]
        await update.message.reply_text(
            f"✅ Serviço Ativo: **{texto}**\nEnvie seu GPS ou digite um endereço para consulta:",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
            parse_mode='Markdown'
        )
        return

    # 3. Roteamento de Estado
    if context.user_data.get('servico_ativo') == 'REDE':
        await rede_ftth.processar_consulta_rede(update, context)
    else:
        await update.message.reply_text("⚠️ Selecione uma opção válida no menu.")
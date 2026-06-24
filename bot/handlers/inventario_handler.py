import uuid
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento
from services.bigquery_service import salvar_inventario

# Definição dos estados da conversação
LOCALIZACAO, SAP, HOSTNAME, FOTO, CONFIRMACAO, EDICAO_CAMPO = range(6)

async def cancelar(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text("❌ Inventário cancelado.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def iniciar_inventario(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.message.reply_text("🚀 Iniciando novo inventário. Envie o GPS ou endereço:", reply_markup=ReplyKeyboardRemove())
    return LOCALIZACAO

async def receber_localizacao(update: Update, context: CallbackContext):
    loc = update.message.location
    context.user_data['loc'] = f"Lat: {loc.latitude}, Long: {loc.longitude}" if loc else update.message.text
    kb = ReplyKeyboardMarkup([['Não tenho']], resize_keyboard=True)
    await update.message.reply_text("✅ Localização registrada. ID SAP (ou 'Não tenho'):", reply_markup=kb)
    return SAP

async def receber_sap(update: Update, context: CallbackContext):
    context.user_data['idsap'] = update.message.text if update.message.text != 'Não tenho' else 'N/A'
    kb = ReplyKeyboardMarkup([['Não tenho']], resize_keyboard=True)
    await update.message.reply_text("✅ SAP ok. Hostname (ou 'Não tenho'):", reply_markup=kb)
    return HOSTNAME

async def receber_hostname(update: Update, context: CallbackContext):
    context.user_data['hostname'] = update.message.text if update.message.text != 'Não tenho' else 'N/A'
    await update.message.reply_text("📸 Agora, envie a foto do equipamento:", reply_markup=ReplyKeyboardRemove())
    return FOTO

async def processar_foto(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    context.user_data['foto_bytes'] = image_bytes
    
    status_msg = await update.message.reply_text("🤖 Analisando imagem...")
    dados = extrair_dados_equipamento(image_bytes)
    context.user_data['dados_ia'] = dados
    
    msg = f"🔍 Detectado:\nFab: {dados.get('fabricante')}\nMod: {dados.get('modelo')}\nFunc: {dados.get('funcao')}\nSerial: {dados.get('serial_number')}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirmar", callback_data='confirmar'), 
                                InlineKeyboardButton("✏️ Editar", callback_data='editar')]])
    await status_msg.edit_text(msg, reply_markup=kb)
    return CONFIRMACAO

async def confirmar_ou_editar(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirmar':
        # Upload via serviço GCS injetado no bot_data
        gcs_service = context.bot_data['gcs_service']
        blob_name = f"fotos_bot_telegram/{uuid.uuid4()}.jpg"
        
        # O GCS Service agora converte bytearray para bytes internamente
        gcs_url = gcs_service.upload_file("vtal-bucket-inventariorede-prd", context.user_data['foto_bytes'], blob_name)
        
        # Salvar BigQuery via cliente injetado
        sucesso = salvar_inventario({
            'idsap': context.user_data.get('idsap'),
            'hostname': context.user_data.get('hostname'),
            'loc': context.user_data.get('loc'),
            'dados_ia': context.user_data['dados_ia'],
            'user_id': update.effective_user.id,
            'gcs_url': gcs_url
        }, context.bot_data['bq_client'])
        
        if sucesso:
            await query.message.edit_text("✅ Inventário finalizado e salvo!")
        else:
            await query.message.edit_text("❌ Erro ao salvar inventário no banco de dados.")
            
        context.user_data.clear()
        return ConversationHandler.END
    
    elif query.data == 'editar':
        await query.message.edit_text("✏️ Envie o nome do campo seguido do valor (ex: 'fabricante Huawei'):")
        context.user_data['campo_editando'] = True # Exemplo de controle
        return EDICAO_CAMPO

async def realizar_edicao(update: Update, context: CallbackContext):
    # Simples lógica de atualização
    msg = update.message.text
    await update.message.reply_text(f"✅ Campo atualizado para: {msg}")
    return CONFIRMACAO

# Handler principal
inventario_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'(?i)^(📷 Enviar Fotos)$'), iniciar_inventario)],
    states={
        LOCALIZACAO: [MessageHandler(filters.LOCATION | filters.TEXT, receber_localizacao)],
        SAP: [MessageHandler(filters.TEXT, receber_sap)],
        HOSTNAME: [MessageHandler(filters.TEXT, receber_hostname)],
        FOTO: [MessageHandler(filters.PHOTO, processar_foto)],
        CONFIRMACAO: [CallbackQueryHandler(confirmar_ou_editar)],
        EDICAO_CAMPO: [MessageHandler(filters.TEXT, realizar_edicao)]
    },
    fallbacks=[CommandHandler("cancelar", cancelar)],
    per_message=False
)
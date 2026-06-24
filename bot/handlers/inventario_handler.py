import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from services.ai_service import extrair_dados_equipamento
from services.bigquery_service import salvar_inventario
from services.storage_service import upload_foto_gcs

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
    context.user_data['loc'] = f"Lat: {update.message.location.latitude}, Long: {update.message.location.longitude}" if update.message.location else update.message.text
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
        # Upload GCS
        gcs_url = upload_foto_gcs(context.user_data['foto_bytes'], update.effective_user.id)
        # Salvar BigQuery
        salvar_inventario({
            'idsap': context.user_data.get('idsap'),
            'hostname': context.user_data.get('hostname'),
            'loc': context.user_data.get('loc'),
            'dados_ia': context.user_data['dados_ia'],
            'user_id': update.effective_user.id,
            'gcs_url': gcs_url
        })
        await query.message.delete()
        await query.message.reply_text("✅ Inventário finalizado e salvo!", reply_markup=ReplyKeyboardMarkup([['📷 Enviar Fotos']], resize_keyboard=True))
        context.user_data.clear()
        return ConversationHandler.END
    
    elif query.data == 'editar':
        kb = ReplyKeyboardMarkup([['Fabricante', 'Modelo'], ['Função', 'Serial']], resize_keyboard=True)
        await query.message.delete()
        await query.message.reply_text("✏️ Qual campo deseja alterar?", reply_markup=kb)
        return EDICAO_CAMPO

async def realizar_edicao(update: Update, context: CallbackContext):
    msg = update.message.text.lower()
    mapa = {'fabricante': 'fabricante', 'modelo': 'modelo', 'função': 'funcao', 'serial': 'serial_number'}
    
    if msg in mapa:
        context.user_data['campo_editando'] = mapa[msg]
        await update.message.reply_text(f"Digite o novo valor para {msg}:", reply_markup=ReplyKeyboardRemove())
        return EDICAO_CAMPO
    else:
        campo = context.user_data.get('campo_editando')
        context.user_data['dados_ia'][campo] = update.message.text
        dados = context.user_data['dados_ia']
        
        msg_final = f"🔍 **Atualizado:**\nFab: {dados.get('fabricante')}\nMod: {dados.get('modelo')}\nFunc: {dados.get('funcao')}\nSerial: {dados.get('serial_number')}\n\nConfirma?"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirmar", callback_data='confirmar'), 
                                    InlineKeyboardButton("✏️ Editar", callback_data='editar')]])
        await update.message.reply_text(msg_final, reply_markup=kb)
        return CONFIRMACAO

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
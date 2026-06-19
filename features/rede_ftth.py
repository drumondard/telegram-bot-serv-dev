
## /home/inventario/telegram-bot-serv/features/rede_ftth.py

import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
# Descomente os imports abaixo
from services.rede_service import consultar_rede 

async def processar_consulta_rede(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para processar a localização (GPS) e consultar a rede no BigQuery.
    """
    # 1. Recupera dependências injetadas
    bq_client = context.bot_data.get('bq_client')
    
    if not bq_client:
        await update.message.reply_text("❌ Erro: Cliente BigQuery não configurado.")
        return

    # 2. Extração da Localização
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    tipo_rede = context.user_data.get('tipo_rede', '🌐 Rede FTTH')
    
    status_msg = await update.message.reply_text("🔎 Consultando base de rede...")

    try:
        # 3. Execução da consulta
        resultados = consultar_rede(lon, lat, tipo_rede, bq_client)
        rows = list(resultados)
        
        if not rows:
            await status_msg.edit_text(f"📭 Nenhuma rede {tipo_rede} próxima.")
            return
        
        # 4. Formatação da Resposta (Layout Completo)
        resposta = f"🔍 **Resultado para:**\n_{context.user_data.get('endereco_pesquisado', 'Localização informada')}_\n📡 **Tipo:** {tipo_rede}\n"
        resposta += f"───────────────────\n\n"
        
        for row in rows[:5]:
            # Recupera os dados com getattr para evitar erros de campo ausente
            id_cdoe = getattr(row, 'id_cdoe', 'N/A')
            status = getattr(row, 'status', 'N/A')
            dist = getattr(row, 'distancia_metros', 0)
            cod_est = getattr(row, 'cod_est', 'N/A')
            cd_celula = getattr(row, 'cd_celula', 'N/A')
            survey = getattr(row, 'cd_codido_survey', 'N/A')
            hp = getattr(row, 'qtd_hp', 0)
            
            # Coordenadas do ativo (ou fallback para lat/lon informada)
            r_lat = getattr(row, 'latitude', lat)
            r_lon = getattr(row, 'longitude', lon)
            
            # Links de Navegação
            link_arcgis = f"https://v-tal.maps.arcgis.com/apps/mapviewer/index.html?webmap=3f161fb302b442f4ab3de6c84619630f&center={r_lon},{r_lat}&level=18"
            link_google = f"https://www.google.com/maps/search/?api=1&query={r_lat},{r_lon}"

            # Construção da mensagem formatada
            resposta += f"📦 **ID:** `{id_cdoe}`\n"
            resposta += f"🏗️ **Estação:** `{cod_est}`\n"
            resposta += f"📏 Distância: **{int(dist)}m** | 🏘️ **HC:** {hp}\n"
            resposta += f"📊 Status: {status}\n"            
            resposta += f"📝 **Survey:** `{survey}` | 🧬 **Célula:** `{cd_celula}`\n"        
            resposta += f"🌐 [Abrir no ArcGIS Online]({link_arcgis})\n"
            resposta += f"📍 [Navegar no Google Maps]({link_google})\n"
            resposta += f"───────────────────\n"
            
        await status_msg.edit_text(resposta, parse_mode='Markdown', disable_web_page_preview=True)

    except Exception as e:
        logging.error(f"Erro na consulta FTTH: {e}")
        await status_msg.edit_text("⚠️ Erro ao processar dados técnicos.")

def registrar_handlers_rede(app):
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.LOCATION, processar_consulta_rede))
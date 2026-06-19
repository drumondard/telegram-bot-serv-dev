# /home/inventario/telegram-bot-serv/rede_ftth.py
from utils.maps_helper import get_coordinates
from services.rede_service import consultar_rede
from utils.bq_client import get_bigquery_client
import menu  # Importamos o menu para chamar o loop final
import os

async def processar_consulta_rede(update, context):
    texto = update.message.text
    lat, lon = None, None
    
    # 1. Geocodificação (GPS ou Endereço)
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        addr = "Sua Localização Atual (GPS)"
    else:
        lat, lon, addr = get_coordinates(texto, os.getenv("MAPS_KEY"))
    
    if not lat:
        await update.message.reply_text("❌ Endereço não encontrado ou GPS inválido.")
        return

    # 2. Execução da Consulta
    status_msg = await update.message.reply_text(f"📍 **Identificado:** _{addr}_\n🔎 Consultando rede...")
    
    client = get_bigquery_client()
    tipo = context.user_data.get('tipo_rede', '🌐 Rede FTTH')
    resultados = consultar_rede(lon, lat, tipo, client)
    rows = list(resultados)
    
    # 3. Formatação e Envio dos Resultados
    if not rows:
        await status_msg.edit_text(f"📭 Nenhuma rede próxima a:\n_{addr}_", parse_mode='Markdown')
    else:
        resposta = f"🔍 **Resultado para:**\n_{addr}_\n📡 **Tipo:** {tipo}\n"
        resposta += f"───────────────────\n\n"
        
        for row in rows[:5]:
            # Extração segura de dados
            id_cdoe = getattr(row, 'id_cdoe', 'N/A')
            status = getattr(row, 'status', 'N/A')
            dist = getattr(row, 'distancia_metros', 0)
            cod_est = getattr(row, 'cod_est', 'N/A')
            cd_celula = getattr(row, 'cd_celula', 'N/A')
            survey = getattr(row, 'cd_codido_survey', 'N/A')
            hp = getattr(row, 'qtd_hp', 0)
            r_lat, r_lon = getattr(row, 'latitude', lat), getattr(row, 'longitude', lon)
            
            link_arcgis = f"https://v-tal.maps.arcgis.com/apps/mapviewer/index.html?webmap=3f161fb302b442f4ab3de6c84619630f&center={r_lon},{r_lat}&level=18"
            link_google = f"https://www.google.com/maps/search/?api=1&query={r_lat},{r_lon}"

            resposta += f"📦 **ID:** `{id_cdoe}`\n🏗️ **Estação:** `{cod_est}`\n📏 Distância: **{int(dist)}m** | 🏘️ **HC:** {hp}\n"
            resposta += f"📊 Status: {status}\n📝 **Survey:** `{survey}` | 🧬 **Célula:** `{cd_celula}`\n"
            resposta += f"🌐 [Abrir no ArcGIS Online]({link_arcgis})\n📍 [Navegar no Google Maps]({link_google})\n"
            resposta += f"───────────────────\n"
        
        await status_msg.edit_text(resposta, parse_mode='Markdown', disable_web_page_preview=True)

    # 4. Chama o loop do menu final para reiniciar o ciclo
    from menu import exibir_menu_loop
    await exibir_menu_loop(update)
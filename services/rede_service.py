# /home/inventario/telegram-bot-serv/services/rede_service.py

from google.cloud import bigquery
import requests
from google.auth.transport.requests import Request

# Configure o proxy no client do BigQuery
session = requests.Session()
session.proxies = {
    'http': 'http://10.130.12.13:82',
    'https': 'http://10.130.12.13:82'
}


def consultar_rede(lon, lat, tipo, client):
    """Executa a query de rede diretamente no BigQuery."""
    
    # Raio de busca de 500 metros
    raio_busca_metros = 500
    
    # Query otimizada com ST_DWithin
    query = f"""
        SELECT 
            cod_est,
            cd_celula,
            cd_codido_survey,
            ds_cdo_name AS id_cdoe,
            ds_cdo_est_operacional AS status,
            qtd_hc AS qtd_hp,
            ROUND(ST_DISTANCE(localizacao_geog, ST_GEOGPOINT({lon}, {lat})), 2) AS distancia_metros,
            ST_Y(localizacao_geog) AS latitude,
            ST_X(localizacao_geog) AS longitude
        FROM 
            `vtal-inventariorede-prd.telegram_bot.tb_ntw_cdoe_otimizada_v2`
        WHERE 
            ST_DWithin(localizacao_geog, ST_GEOGPOINT({lon}, {lat}), {raio_busca_metros})
        ORDER BY 
            distancia_metros ASC
        LIMIT 5;
    """
    
    query_job = client.query(query)
    return query_job.result()
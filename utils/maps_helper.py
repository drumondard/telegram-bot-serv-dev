# /home/inventario/telegram-bot-serv/utils/maps_helper.py

import requests

def get_coordinates(address, api_key):
    """
    Converte um endereço em latitude e longitude usando a API do Google Maps.
    Retorna (lat, lon, endereco_formatado) ou (None, None, None) em caso de erro.
    """
    if not api_key:
        print("Erro: API Key não configurada.")
        return None, None, None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
        "language": "pt-BR"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            result = data['results'][0]
            lat = result['geometry']['location']['lat']
            lon = result['geometry']['location']['lng']
            formatted_address = result['formatted_address']
            return lat, lon, formatted_address
        else:
            print(f"Erro na Geocodificação: {data.get('status')}")
            return None, None, None
            
    except Exception as e:
        print(f"Erro na requisição da API de Maps: {e}")
        return None, None, None
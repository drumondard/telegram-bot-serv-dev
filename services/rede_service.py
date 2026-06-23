
## /home/inventario/telegram-bot-serv/services/rede_service.py


def consultar_rede(lon, lat, tipo_rede, client):
    """
    Roteia para a Procedure correta no BigQuery baseada no tipo de rede.
    """
    if "FTTH" in tipo_rede:
        # Versão otimizada para FTTH conforme seu histórico
        dataset_procedure = "telegram_bot.get_nearby_cdoe_v2"
    elif "Backbone" in tipo_rede:
        dataset_procedure = "telegram_bot.get_nearby_backbone"
    elif "Acesso" in tipo_rede:
        dataset_procedure = "telegram_bot.get_nearby_acesso"
    else:
        raise ValueError("Tipo de rede não reconhecido.")

    # O CALL executa a procedure armazenada no BQ
    query = f"CALL `{dataset_procedure}`({lon}, {lat}, 5000)"
    
    return client.query(query).result()
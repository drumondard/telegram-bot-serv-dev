import os
import json
import logging
from google import genai
from google.genai import types

def extrair_dados_equipamento(image_bytes):
    """
    Analisa a imagem utilizando uma lista de modelos de IA em cascata (fallback).
    Se o primeiro falhar (por indisponibilidade ou erro), tenta o próximo.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY não definida.")
        return {"fabricante": "Erro", "modelo": "Configuração"}

    client = genai.Client(api_key=api_key)
    image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    
    prompt = (
        "Analise a foto deste equipamento de telecomunicações. "
        "Retorne APENAS um objeto JSON (sem formatação markdown) "
        "com as chaves: 'fabricante', 'modelo', 'funcao', 'serial_number'. "
        "Se não encontrar algum dado, preencha com 'N/A'."
    )

    # Lista de modelos disponíveis no seu servidor, ordenados por preferência.
    # O bot tentará o primeiro; se der erro, pulará para o próximo.
    modelos_para_tentar = [
        'gemini-3.5-flash',
        'gemini-2.0-flash',
        'gemini-flash-latest'
    ]
    
    for modelo in modelos_para_tentar:
        try:
            logging.info(f"Tentando extração com o modelo: {modelo}")
            
            response = client.models.generate_content(
                model=modelo,
                contents=[prompt, image_part]
            )
            
            # Limpeza do retorno para garantir que o JSON seja processado
            cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)
            
        except Exception as e:
            logging.warning(f"Erro ao usar o modelo {modelo}: {e}")
            # Continua para o próximo modelo da lista se houver erro
            continue
            
    # Caso todos os modelos falhem, retorna um dicionário padrão
    logging.error("Todos os modelos de IA falharam na extração.")
    return {
        "fabricante": "N/A", 
        "modelo": "N/A", 
        "funcao": "N/A", 
        "serial_number": "N/A"
    }
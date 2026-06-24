import os
import json
import logging
from google import genai
from google.genai import types

def extrair_dados_equipamento(image_bytes):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    
    prompt = (
        "Analise a foto deste equipamento de telecomunicações. "
        "Retorne APENAS um objeto JSON com as chaves: 'fabricante', 'modelo', 'funcao', 'serial_number'. "
        "Se não encontrar algum dado, preencha com 'N/A'."
    )

    modelos_para_tentar = ['gemini-3.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    
    for modelo in modelos_para_tentar:
        try:
            logging.info(f"Tentando extração com: {modelo}")
            response = client.models.generate_content(
                model=modelo,
                contents=[prompt, image_part]
            )
            cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)
            
        except Exception as e:
            if "429" in str(e):
                logging.error("Cota excedida no modelo atual.")
            logging.warning(f"Erro ao usar {modelo}: {e}")
            continue
            
    return {"fabricante": "N/A", "modelo": "N/A", "funcao": "N/A", "serial_number": "N/A"}
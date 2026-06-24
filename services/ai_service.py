
import json
import logging
import os
from google import genai
from google.genai import types

def extrair_dados_equipamento(image_bytes: bytes) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    prompt = "Analise este equipamento. Retorne APENAS um JSON: {'fabricante', 'modelo', 'funcao', 'serial_number'}. Se não achar, 'N/A'."
    
    # Tentativa com modelos prioritários
    for modelo in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-3.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']:
        try:
            response = client.models.generate_content(model=modelo, contents=[prompt, image_part])
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except Exception as e:
            logging.warning(f"Erro no modelo {modelo}: {e}")
            
    return {"fabricante": "N/A", "modelo": "N/A", "funcao": "N/A", "serial_number": "N/A"}

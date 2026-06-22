import os
import json
import re
from google import genai
from google.genai import types

def extrair_dados_equipamento(image_bytes):
    """Analisa a imagem e retorna um dicionário com os dados do equipamento."""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
        
        prompt = (
            "Analise a foto deste equipamento de telecomunicações. "
            "Retorne estritamente em formato JSON com as chaves: "
            "'fabricante', 'modelo', 'funcao', 'serial_number'. "
            "Não adicione texto explicativo, apenas o JSON."
        )
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        return json.loads(response.text)
    except Exception as e:
        return {"erro": str(e)}
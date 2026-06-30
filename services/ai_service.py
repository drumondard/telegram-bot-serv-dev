
'''
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
'''

import json
import logging
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

def extrair_dados_equipamento(image_bytes: bytes) -> dict:
    # Inicializa o cliente (o SDK já busca a variável GEMINI_API_KEY automaticamente)
    client = genai.Client()
    
    image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    
    prompt = (
        "Analise a imagem deste equipamento de TI/infraestrutura e extraia os dados solicitados. "
        "Se não encontrar alguma informação, preencha o campo com 'N/A'."
    )
    
    # 1. Definimos a estrutura exata do JSON que queremos usando Pydantic/Types
    # Isso força o modelo a responder estritamente neste formato.
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "fabricante": {"type": "STRING"},
                "modelo": {"type": "STRING"},
                "funcao": {"type": "STRING"},
                "serial_number": {"type": "STRING"}
            },
            "required": ["fabricante", "modelo", "funcao", "serial_number"]
        }
    )
    
    # 2. Lista atualizada de modelos (os modelos 1.5 antigos e inconsistentes foram removidos/corrigidos)
    # Colocamos o gemini-2.5-flash como principal (mais rápido, barato e moderno)
    ###modelos = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.5-pro']
    modelos = ['gemini-2.5-flash']
    
    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=[prompt, image_part],
                config=config
            )
            
            # Como usamos 'response_mime_type', a resposta já vem como string JSON pura
            return json.loads(response.text)
            
        except APIError as e:
            logging.warning(f"Erro de API no modelo {modelo}: {e.message} (Código: {e.code})")
            
            # Se for erro de limite de requisições (429) ou instabilidade (503), espera um pouco antes do fallback
            if e.code in [429, 503]:
                time.sleep(2)
                
        except Exception as e:
            logging.warning(f"Erro inesperado no modelo {modelo}: {e}")
            
    # Fallback caso todos os modelos falhem
    return {"fabricante": "N/A", "modelo": "N/A", "funcao": "N/A", "serial_number": "N/A"}
import os
from dotenv import load_dotenv
from google import genai

load_dotenv("/home/inventario/automacao/config/.env")

def listar_modelos():
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        print("Modelos disponíveis:")
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")

if __name__ == "__main__":
    listar_modelos()
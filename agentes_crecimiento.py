import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Inicialización segura
client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class CampanaWhatsApp(BaseModel):
    mensaje_texto: str = Field(description="Texto ultra corto, persuasivo, con emojis.")
    guion_nota_voz: str = Field(description="Guion conversacional muy natural.")
    link_wa: str = Field(description="URL formato wa.me/numero?text=mensaje")

class ArticuloSEO(BaseModel):
    titulo_h1: str = Field(description="Título SEO atractivo para B2B.")
    slug: str = Field(description="URL amigable.")
    meta_description: str = Field(description="Meta descripción.")
    contenido_md: str = Field(description="Contenido completo en Markdown.")

def invocar_modelo_seguro(prompt, response_schema, temperature=0.4):
    modelos = ["gemini-2.5-flash", "gemini-1.5-flash"]
    for modelo in modelos:
        try:
            response = client_ai.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=response_schema,
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            print(f"Error en {modelo}: {e}")
    return None

def generar_campana_whatsapp(objetivo: str, numero: str = "573000000000"):
    prompt = f"Campaña para ViveroOnline. Objetivo: {objetivo}. Audiencia: Viveristas Sabana Bogotá."
    json_res = invocar_modelo_seguro(prompt, CampanaWhatsApp, 0.7)
    return CampanaWhatsApp.model_validate_json(json_res) if json_res else None

def generar_seo_desde_inventario(datos: dict):
    prompt = f"Estratega SEO ViveroOnline. Inventario: {datos}. Crea artículo B2B técnico."
    json_res = invocar_modelo_seguro(prompt, ArticuloSEO, 0.4)
    return ArticuloSEO.model_validate_json(json_res) if json_res else None

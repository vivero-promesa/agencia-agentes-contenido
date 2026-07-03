import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Inicialización segura
try:
    client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    client_ai = None
    print(f"Error inicializando SDK: {e}")

# ==========================================
# MODELOS (Pydantic - Sin cambios)
# ==========================================
class CampanaWhatsApp(BaseModel):
    mensaje_texto: str = Field(description="Texto ultra corto, persuasivo, con emojis.")
    guion_nota_voz: str = Field(description="Guion conversacional muy natural.")
    link_wa: str = Field(description="URL formato wa.me/numero?text=mensaje")

class ArticuloSEO(BaseModel):
    titulo_h1: str = Field(description="Título SEO atractivo para B2B.")
    slug: str = Field(description="URL amigable.")
    meta_description: str = Field(description="Meta descripción 150 caracteres.")
    contenido_md: str = Field(description="Contenido completo en Markdown.")

# ==========================================
# LÓGICA DE FALLBACK (Motor de Resiliencia)
# ==========================================
def invocar_modelo_seguro(prompt, response_schema, temperature=0.7):
    """
    Intenta generar contenido con modelos alternativos si el principal falla.
    """
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
            print(f"Fallo en {modelo}: {e}. Probando siguiente...")
    return None

# ==========================================
# AGENTES AJUSTADOS
# ==========================================
def generar_campana_whatsapp(objetivo: str, numero_contacto: str = "573000000000") -> CampanaWhatsApp | None:
    if not client_ai: return None
    
    prompt = f"Crea una campaña WhatsApp para ViveroOnline. Objetivo: {objetivo}. Contacto: {numero_contacto}. Audiencia: Viveristas en la Sabana. Tono: Cercano y directo."
    
    resultado_json = invocar_modelo_seguro(prompt, CampanaWhatsApp, temperature=0.7)
    return CampanaWhatsApp.model_validate_json(resultado_json) if resultado_json else None

def generar_seo_desde_inventario(datos_inventario: dict) -> ArticuloSEO | None:
    if not client_ai: return None
    
    prompt = f"""
    Eres el Agente SEO de ViveroOnline. Inventario: {datos_inventario}.
    Redacta un artículo optimizado para B2B (constructoras/paisajistas).
    """
    
    resultado_json = invocar_modelo_seguro(prompt, ArticuloSEO, temperature=0.4)
    return ArticuloSEO.model_validate_json(resultado_json) if resultado_json else None

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
    prompt_b2b = f"""
    Eres un Estratega SEO y Copywriter B2B experto en el sector agrónomo y de construcción en Colombia.
    Tu objetivo es redactar un artículo SEO transaccional para ViveroOnline, diseñado para capturar la demanda de constructoras, arquitectos y paisajistas que buscan comprar lotes mayoristas.

    DATOS DEL LOTE DISPONIBLE:
    - Especie: {datos.get('especie')}
    - Cantidad en Stock: {datos.get('cantidad')} unidades
    - Ubicación Logística: {datos.get('ubicacion')}
    - Vivero Productor: {datos.get('vendedor')}

    INSTRUCCIONES DE REDACCIÓN (Usa el Framework PAS):
    1. PROBLEMA (H2): Inicia identificando un dolor operativo crítico (ej. alta mortalidad vegetal en proyectos, plantas no aclimatadas al clima frío, retrasos en entregas).
    2. AGITACIÓN (Párrafo): Explica el costo oculto de ese problema (pérdida de dinero por garantías de plantas muertas, entregas de obra retrasadas).
    3. SOLUCIÓN (H2): Presenta este lote exacto de {datos.get('cantidad')} {datos.get('especie')} aclimatadas en {datos.get('ubicacion')} como la solución logística y biológica perfecta.
    4. RESPALDO: Menciona a {datos.get('vendedor')} como un aliado estratégico verificado de ViveroOnline.

    REGLAS ESTRICTAS:
    - Responde EXCLUSIVAMENTE en el formato JSON estructurado según el esquema.
    - El 'titulo_h1' debe incluir la especie, la palabra "Lote" o "Mayorista" y la ubicación.
    - El contenido ('contenido_md') debe estar en Markdown impecable.
    - Termina con un Call to Action (CTA) claro para cotizar el volumen completo.
    - Tono: Consultivo, corporativo, directo al grano. Cero lenguaje romántico sobre la naturaleza; háblales de rentabilidad y eficiencia logística.
    """
    
    # Invocamos al modelo con una temperatura baja (0.3) para priorizar estructura y precisión sobre creatividad excesiva
    json_res = invocar_modelo_seguro(prompt_b2b, ArticuloSEO, 0.3)
    return ArticuloSEO.model_validate_json(json_res) if json_res else None

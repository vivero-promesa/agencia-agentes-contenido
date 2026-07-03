import os
from pydantic import BaseModel, Field
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Inicialización segura
try:
    client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    client_ai = None
    print(f"Error inicializando SDK: {e}")

# ==========================================
# ESTRUCTURAS DE DATOS (Pydantic Models)
# ==========================================
class CampanaWhatsApp(BaseModel):
    mensaje_texto: str = Field(description="Texto ultra corto, máximo 4 líneas, persuasivo, con emojis agrícolas. Debe incluir un placeholder para el link.")
    guion_nota_voz: str = Field(description="Guion conversacional, empático y muy natural (sin sonar locutor) para generar audio de WhatsApp.")
    link_wa: str = Field(description="URL pre-llenada usando formato wa.me/numero?text=mensaje_codificado")

class ArticuloSEO(BaseModel):
    titulo_h1: str = Field(description="Título SEO atractivo para B2B o compradores mayoristas.")
    slug: str = Field(description="URL amigable, ej: comprar-orquideas-mayor-cajica")
    meta_description: str = Field(description="Meta descripción de máximo 150 caracteres.")
    contenido_md: str = Field(description="Contenido completo en Markdown, estructurado con H2, H3 y viñetas.")

# ==========================================
# AGENTE 1: CONVERSIÓN WHATSAPP (Fase 1)
# ==========================================
def generar_campana_whatsapp(objetivo: str, numero_contacto: str = "573000000000") -> CampanaWhatsApp | None:
    """Genera el copy y el guion de nota de voz optimizado para productores rústicos."""
    if not client_ai: return None
    
    prompt = f"""
    Crea una campaña de captación por WhatsApp para ViveroOnline.
    Objetivo: {objetivo}
    Número de contacto: {numero_contacto}
    Audiencia: Viveristas y constructores en la Sabana de Bogotá. Tono directo, confianza, cero tecnicismos.
    """
    
    # SOLUCIÓN: Usamos gemini-2.5-flash, alineado con la versión de API de tu proyecto
    response = client_ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': CampanaWhatsApp,
            'temperature': 0.7
        },
    )
    # Parseamos la respuesta JSON a nuestro objeto Pydantic
    return CampanaWhatsApp.model_validate_json(response.text)

# ==========================================
# AGENTE 3: SEO PROGRAMÁTICO (Fase 3)
# ==========================================
def generar_seo_desde_inventario(datos_inventario: dict) -> ArticuloSEO | None:
    """Lee datos crudos de Supabase y redacta un artículo para indexar esa oferta."""
    if not client_ai: return None
    
    prompt = f"""
    Eres el Agente de Crecimiento SEO de ViveroOnline. 
    Se ha detectado nuevo inventario en el marketplace:
    - Especie: {datos_inventario.get('especie')}
    - Cantidad disponible: {datos_inventario.get('cantidad')} unidades
    - Ubicación: {datos_inventario.get('ubicacion')}
    - Vendedor: {datos_inventario.get('vendedor')}
    
    Redacta un artículo optimizado para búsquedas B2B (constructoras, paisajistas buscando este volumen). 
    Incluye un llamado a la acción claro para comprar este lote específico en ViveroOnline.
    """
    
    # SOLUCIÓN: Usamos gemini-2.5-flash
    response = client_ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ArticuloSEO,
            'temperature': 0.4 # Más bajo para mayor precisión técnica SEO
        },
    )
    return ArticuloSEO.model_validate_json(response.text)

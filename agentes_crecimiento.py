import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

from identidad_marca import IDENTIDAD_COMPACTA

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class CampanaWhatsApp(BaseModel):
    mensaje_texto: str = Field(description="Texto ultra corto, persuasivo, con emojis.")
    guion_nota_voz: str = Field(description="Guion conversacional muy natural.")
    link_wa: str = Field(description="URL formato wa.me/numero?text=mensaje")


class ArticuloSEO(BaseModel):
    titulo_h1: str = Field(description="Título SEO atractivo y transaccional para B2B.")
    slug: str = Field(description="URL amigable.")
    meta_description: str = Field(description="Meta descripción orientada a conversión.")
    contenido_md: str = Field(description="Contenido completo en Markdown impecable.")


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


def generar_campana_whatsapp(objetivo: str, numero: str = "573000000000", audiencia: str = "institucional"):
    """
    Genera un kit de WhatsApp (mensaje de texto + guion de nota de voz).

    audiencia:
      - "institucional" (default): comprador (paisajista, constructora,
        arquitecto). Discurso "frente al mercado" — captación o cierre de venta.
      - "viverista": productor. Discurso "frente al viverista" — onboarding,
        activación o resolver una duda sobre el marketplace. Lenguaje simple,
        cero tecnicismos, nunca hacerlo sentir atrasado.
    """
    if audiencia == "viverista":
        instrucciones_audiencia = """
Le escribes a un VIVERISTA (productor), no a un comprador. Usa el discurso
"frente al viverista" de la identidad de marca: lenguaje simple, cercano,
cero tecnicismos. Nunca lo hagas sentir atrasado por no saber de tecnología.
El objetivo suele ser onboarding, activación en el marketplace o resolver
una duda — no una venta.
"""
    else:
        instrucciones_audiencia = """
Le escribes a un COMPRADOR INSTITUCIONAL (paisajista, constructora,
arquitecto). Usa el discurso "frente al mercado" de la identidad de marca:
profesional pero cercano, nunca corporativo frío. El objetivo suele ser
captación o cierre de una venta concreta.
"""

    prompt_wa = f"""
{IDENTIDAD_COMPACTA}

{instrucciones_audiencia}

Eres el encargado de comunicación por WhatsApp de ViveroOnline.

OBJETIVO DE LA CAMPAÑA: {objetivo}

Instrucciones de formato — "Fricción Cero":
1. mensaje_texto: máximo 3-4 líneas, directo al grano, con 1-2 emojis (🌿🚚)
   naturales, no forzados. Sin presión ni urgencia artificial ("últimas
   unidades", "solo hoy" quedan prohibidos).
2. guion_nota_voz: versión hablada, conversacional, como si un asesor
   llamara — más cálido que el texto, pero igual de concreto. Debe sonar a
   persona real, no a locución publicitaria.
3. link_wa: usa el número {numero} en formato
   https://wa.me/{numero}?text=<mensaje_texto codificado para URL>

Responde únicamente con los campos del schema solicitado.
"""
    json_res = invocar_modelo_seguro(prompt_wa, CampanaWhatsApp, 0.5)
    return CampanaWhatsApp.model_validate_json(json_res) if json_res else None


def generar_seo_desde_inventario(datos: dict):
    """
    Genera un artículo SEO B2B a partir de un lote de inventario, usando el
    framework PAS (Problema, Agitación, Solución) y el discurso institucional
    ("frente al mercado") de la identidad de marca.
    """
    prompt_b2b = f"""
{IDENTIDAD_COMPACTA}

Eres el Estratega SEO B2B de ViveroOnline. Vas a escribir un artículo
optimizado para compradores institucionales (paisajistas, constructoras,
arquitectos) a partir de este lote real de inventario:

DATOS DEL LOTE: {datos}

Estructura obligatoria (framework PAS):
1. PROBLEMA (H2): el reto de abastecimiento o especificación que enfrenta un
   comprador institucional al buscar esta especie en volumen.
2. AGITACIÓN (párrafo): por qué ese problema cuesta tiempo/dinero/riesgo si
   no se resuelve bien (sin exagerar ni inventar cifras).
3. SOLUCIÓN (H2/H3): cómo este lote específico, con estos datos reales,
   resuelve el problema — menciona especie, cantidad y ubicación tal como
   aparecen en DATOS DEL LOTE.
4. RESPALDO LOGÍSTICO (H3): cómo se coordina el despacho de planta viva
   (sin inventar detalles que no están en los datos).
5. CTA: invitación concreta a cotizar el lote en ViveroOnline.

Formato: Markdown limpio, tono profesional pero humano — nunca corporativo
frío ni con lenguaje de urgencia. Responde únicamente con los campos del
schema solicitado.
"""
    json_res = invocar_modelo_seguro(prompt_b2b, ArticuloSEO, 0.3)
    return ArticuloSEO.model_validate_json(json_res) if json_res else None

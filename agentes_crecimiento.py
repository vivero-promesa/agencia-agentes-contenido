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


class CampanaGoogleAds(BaseModel):
    keywords_positivas: list[str] = Field(description="Lista de 10-15 palabras clave de alta intención de compra.")
    keywords_negativas: list[str] = Field(description="Lista de 5-10 exclusiones críticas para evitar tráfico basura o cruces.")
    titulos: list[str] = Field(description="Mínimo 5 opciones de títulos persuasivos. Máximo 30 caracteres por título.")
    descripciones: list[str] = Field(description="Mínimo 3 opciones de descripciones. Máximo 90 caracteres por descripción.")


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


def generar_campana_whatsapp(objetivo: str, numero: str = "573000000000", audiencia: str = "institucional", prioridad_estrategica: str = None):
    if audiencia == "viverista":
        instrucciones_audiencia = """
Le escribes a un VIVERISTA (productor), no a un comprador. Usa el discurso
"frente al viverista" de la identidad de marca: lenguaje simple, cercano,
cero tecnicismos. Nunca lo hagas sentir atrasado por no saber de tecnología.
El objetivo suele ser onboarding, activación en el marketplace o resolver
una duda — no una venta.
"""
    else:
        prioridad_texto = (
            f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL (ajusta el CTA en función de esto):\n{prioridad_estrategica}\n"
            if prioridad_estrategica else ""
        )
        instrucciones_audiencia = f"""
Le escribes a un COMPRADOR INSTITUCIONAL (paisajista, constructora,
arquitecto). Usa el discurso "frente al mercado" de la identidad de marca:
profesional pero cercano, nunca corporativo frío. El objetivo suele ser
captación o cierre de una venta concreta.
{prioridad_texto}"""

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


def generar_seo_por_intencion(cluster_busqueda: str, dolores_intermediarios: str = None, prioridad_estrategica: str = None, insights_pauta_data: dict = None):
    dolores_texto = (
        f"\n\nCONTEXTO — dolores frente a intermediarios tradicionales (usar solo si es relevante al tema, nunca inventar más allá de esto):\n{dolores_intermediarios}\n"
        if dolores_intermediarios else ""
    )
    prioridad_texto = (
        f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL (ajusta el CTA en función de esto):\n{prioridad_estrategica}\n"
        if prioridad_estrategica else ""
    )
    
    contexto_pauta = ""
    if insights_pauta_data:
        keywords_inyectadas = ", ".join(insights_pauta_data.get("keywords_positivas", []))
        contexto_pauta = f"""
\n[ALIMENTACIÓN DE ADS]: Este artículo debe posicionar orgánicamente términos que estamos pagando en pauta.
Integra de forma completamente natural las siguientes palabras clave dentro de los textos y encabezados H2/H3: {keywords_inyectadas}.
"""

    prompt_intencion = f"""
{IDENTIDAD_COMPACTA}
{dolores_texto}{prioridad_texto}{contexto_pauta}
Eres el Estratega SEO B2B de ViveroOnline. Vas a escribir un artículo
optimizado para capturar esta intención de búsqueda transaccional:

CLUSTER / INTENCIÓN DE BÚSQUEDA OBJETIVO: {cluster_busqueda}

Este artículo es PROACTIVO: no depende de un lote de inventario específico
— existe para posicionar a ViveroOnline como autoridad en este tema/producto
antes de que el comprador busque, y para capturar la búsqueda aunque hoy no
haya stock exacto disponible.

Estructura obligatoria (framework PAS):
1. PROBLEMA (H2): el reto real que enfrenta un comprador institucional
   buscando exactamente esto.
2. AGITACIÓN (párrafo): por qué resolverlo mal cuesta tiempo/dinero/riesgo
   (sin exagerar ni inventar cifras).
3. SOLUCIÓN (H2/H3): cómo ViveroOnline resuelve esta necesidad como
   categoría — sin prometer un lote específico si no lo tienes confirmado.
4. RESPALDO LOGÍSTICO (H3): cómo se coordina el despacho de planta viva en
   general (sin inventar detalles de un pedido específico).
5. CTA: invitación a dejar el requerimiento/cotizar disponibilidad en
   ViveroOnline — nunca prometas stock inmediato que no está confirmado.

Formato: Markdown limpio, tono profesional pero humano — nunca corporativo
frío ni con lenguaje de urgencia. Nunca inventes cifras, alianzas o clientes.
Responde únicamente con los campos del schema solicitado.
"""
    json_res = invocar_modelo_seguro(prompt_intencion, ArticuloSEO, 0.3)
    return ArticuloSEO.model_validate_json(json_res) if json_res else None


def generar_seo_desde_inventario(datos: dict, prioridad_estrategica: str = None):
    prioridad_texto = (
        f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL (ajusta el CTA en función de esto):\n{prioridad_estrategica}\n"
        if prioridad_estrategica else ""
    )
    prompt_b2b = f"""
{IDENTIDAD_COMPACTA}
{prioridad_texto}
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


def generar_y_guardar_pauta(objetivo: str, modo: str, supabase_client) -> dict:
    if not supabase_client:
        print("Error: Cliente de Supabase no proporcionado.")
        return None

    if modo == "B2B":
        contexto_marca = "Enfoque institucional B2B (constructoras, paisajistas). Tono profesional, enfocado en volumen, logística y rentabilidad en la Sabana de Bogotá."
    else:
        contexto_marca = "Enfoque minorista B2C (consumidor final, venta de materas y decoración). Tono cercano, emocional, enfocado en diseño y estética para el hogar."

    prompt_pauta = f"""
{IDENTIDAD_COMPACTA}

Eres el Director de Performance y Growth Marketing de ViveroOnline. 
Tu tarea es diseñar una campaña de Google Ads optimizada para el siguiente objetivo:
"{objetivo}"

Contexto operativo de esta campaña: {contexto_marca}

Reglas estrictas de validación de Google Ads:
1. Ningún título puede superar los 30 caracteres. Si te pasas de 30 caracteres, la campaña fallará.
2. Ninguna descripción puede superar los 90 caracteres. Si te pasas, fallará.
3. Las keywords negativas deben bloquear activamente el mercado contrario (si es B2B, bloquea búsquedas minoristas tipo "para mi casa"; si es B2C, bloquea palabras corporativas tipo "por mayor").

Responde únicamente con los campos del schema solicitado.
"""
    
    json_res = invocar_modelo_seguro(prompt_pauta, CampanaGoogleAds, 0.3)
    
    if json_res:
        datos_campana = CampanaGoogleAds.model_validate_json(json_res)
        
        registro = {
            "modo": modo,
            "keyword_objetivo": objetivo,
            "keywords_positivas": datos_campana.keywords_positivas,
            "keywords_negativas": datos_campana.keywords_negativas,
            "titulos_anuncio": datos_campana.titulos,
            "descripciones_anuncio": datos_campana.descripciones,
            "estado": "pendiente_uso_seo"
        }
        
        try:
            supabase_client.table("insights_pauta").insert(registro).execute()
            return registro
        except Exception as e:
            print(f"Error al guardar en Supabase: {e}")
            return None
            
    return None

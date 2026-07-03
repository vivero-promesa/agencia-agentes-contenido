import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Inicialización segura del cliente Gemini
client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# ESQUEMAS DE DATOS (PYDANTIC)
# ==========================================
class CampanaWhatsApp(BaseModel):
    mensaje_texto: str = Field(description="Texto ultra corto, persuasivo, con emojis para la pantalla de bloqueo.")
    guion_nota_voz: str = Field(description="Guion conversacional muy natural con pausas y respiraciones.")
    link_wa: str = Field(description="URL formato wa.me/numero?text=mensaje")

class ArticuloSEO(BaseModel):
    titulo_h1: str = Field(description="Título SEO atractivo y transaccional para B2B.")
    slug: str = Field(description="URL amigable.")
    meta_description: str = Field(description="Meta descripción orientada a conversión.")
    contenido_md: str = Field(description="Contenido completo en Markdown impecable.")

# ==========================================
# MOTOR DE INVOCACIÓN SEGURO
# ==========================================
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

# ==========================================
# AGENTE 1: WHATSAPP B2B (Fricción Cero)
# ==========================================
def generar_campana_whatsapp(objetivo: str, numero: str = "573000000000"):
    prompt_wa = f"""
    Eres el Director de Ventas B2B de ViveroOnline, una plataforma AgTech que conecta viveros de la Sabana de Bogotá con constructoras y paisajistas.
    
    OBJETIVO DE LA CAMPAÑA: {objetivo}
    
    INSTRUCCIONES PARA EL MENSAJE DE TEXTO (mensaje_texto):
    - Debe ser ultra corto (máximo 3-4 líneas), diseñado para leerse en la pantalla de bloqueo.
    - Estructura: Gancho logístico + Valor + Pregunta de fricción cero (ej. "¿Te envío el catálogo o prefieres que hablemos?").
    - Tono: Profesional pero directo. Usa máximo 2 emojis (🚚, 🌱, 🏢, 📈).
    - Cero saludos acartonados como "Estimado señor".
    
    INSTRUCCIONES PARA LA NOTA DE VOZ (guion_nota_voz - Para ElevenLabs):
    - Debe sonar 100% natural, como un humano enviando un audio rápido mientras revisa un invernadero.
    - Longitud: MÁXIMO 60 palabras (para que dure unos 35 segundos). Los jefes de obra no escuchan audios largos.
    - Acústica y Ritmo: Usa comas y puntos suspensivos (...) para forzar a la IA de ElevenLabs a respirar y hacer pausas naturales.
    - Tono: Seguro, consultivo. Arranca con un saludo natural ("Hola, qué tal, te hablo desde ViveroOnline...").
    - Ve directo al grano: qué volumen manejamos, cómo le resolvemos la logística y cierra con una instrucción clara.
    
    URL DE WHATSAPP (link_wa): 
    - Genera un link formato wa.me/{numero}?text=Hola%20quiero%20info
    
    Genera EXCLUSIVAMENTE el JSON solicitado.
    """
    
    # Temperatura 0.5: balance entre estructura comercial y naturalidad conversacional
    json_res = invocar_modelo_seguro(prompt_wa, CampanaWhatsApp, 0.5)
    return CampanaWhatsApp.model_validate_json(json_res) if json_res else None

# ==========================================
# AGENTE 2: SEO TRANSACCIONAL DINÁMICO
# ==========================================
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
    
    # Temperatura 0.3: prioriza estructura y precisión B2B
    json_res = invocar_modelo_seguro(prompt_b2b, ArticuloSEO, 0.3)
    return ArticuloSEO.model_validate_json(json_res) if json_res else None

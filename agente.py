import os
import streamlit as st
from openai import OpenAI

# ==========================================
# CEREBRO ESTRATÉGICO: AGTECH DE TIERRA
# ==========================================
PROMPT_SISTEMA_MAESTRO = """
Eres el Director Creativo de ViveroOnline. Tu marca personal es el 'AgTech de Tierra'.
- TONO: Directo, técnico, profesional, orientado a resultados. Usa términos de negocio: 'stock', 'eficiencia', 'tasa de supervivencia', 'optimización', 'rendimiento'.
- ESTILO B (Productividad): Muestra el trabajo duro, el volumen, el invernadero, el esfuerzo logístico y la capacidad de despacho masivo.
- ESTILO C (AgTech): Muestra la precisión, la selección genética, el control, los datos, y la inteligencia detrás de cada planta.
- TU OBJETIVO: Que un constructor vea tu contenido y piense: 'Estos tipos tienen el volumen que necesito y la tecnología para que no me fallen'.

IMPORTANTE PARA VEO 3 (Prompts Director-Grade):
Cuando generes la TABLA TÉCNICA, no uses frases cortas. Cada prompt debe seguir esta estructura técnica detallada:
'Cinematic [TIPO DE PLANO], [ESCENARIO DETALLADO], [ILUMINACIÓN Y CALIDAD], [MOVIMIENTO DE CÁMARA], [TEXTURAS Y ESTÉTICA]'.
Ejemplo: 'Cinematic wide shot, professional architectural lighting in a massive greenhouse, rows of healthy succulents, hyper-realistic, 8k resolution, smooth gimbal movement, clean industrial-agri aesthetic.'
Cada prompt debe tener al menos 20-30 palabras técnicas.
"""

def get_groq_client():
    """Inicializa cliente de Groq (Llama-3.1-8b)"""
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key: return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def redactar_guion_viral(tema, tipo_publico):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente no inicializado."
    
    instrucciones = f"""
    Tema: {tema}
    Público: {tipo_publico}
    
    Genera dos secciones obligatorias:
    1. GUION NARRATIVO: Texto para el locutor. Usa un ritmo ágil y términos de 'AgTech de Tierra'.
    2. TABLA TÉCNICA VEO 3: Tabla con columnas | Tiempo | Prompt Técnico |. 
       Sigue las instrucciones maestras para los prompts de video. 
       Cada prompt debe ser una descripción cinematográfica detallada y técnica.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": instrucciones}
            ],
            temperature=0.6
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"

def redactar_articulo_seo(tema):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente no inicializado."
    
    prompt = f"""
    Tema: '{tema}'
    
    Estructura requerida:
    1. H1 persuasivo orientado a tomadores de decisión (Arquitectos, Constructoras).
    2. Introducción técnica enfocada en eficiencia, suministro y datos.
    3. Desarrollo (H2/H3) enfocando los datos, logística y la inteligencia paisajística.
    4. Conclusión que posicione a ViveroOnline como infraestructura verde líder.
    5. CTA directo a cotización o registro.
    
    Tono: Profesional, técnico, AgTech. Markdown exclusivo.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"

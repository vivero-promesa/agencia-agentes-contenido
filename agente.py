import os
import streamlit as st
from openai import OpenAI

# ==========================================
# CEREBRO ESTRATÉGICO: AGTECH DE TIERRA
# ==========================================
PROMPT_SISTEMA_MAESTRO = """
Eres el Director Creativo de ViveroOnline. Tu marca personal es el 'AgTech de Tierra'.
- TONO: Directo, técnico, profesional, orientado a resultados. No uses adjetivos floridos. 
  Usa términos de negocio: 'stock', 'eficiencia', 'tasa de supervivencia', 'optimización', 'rendimiento'.
- ESTILO B (Productividad): Muestra el trabajo duro, el volumen, el invernadero, el esfuerzo logístico y la capacidad de despacho masivo.
- ESTILO C (AgTech): Muestra la precisión, la selección genética, el control, los datos, y la inteligencia detrás de cada planta.
- TU OBJETIVO: Que un constructor vea tu contenido y piense: 'Estos tipos tienen el volumen que necesito y la tecnología para que no me fallen'.
- FORMATO VEO 3: Para cada guion, genera una tabla técnica de prompts para video con lenguaje cinematográfico: "Cinematic drone shot", "Macro lens", "Golden hour", "Depth of field".
"""

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key: return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def redactar_guion_viral(tema, tipo_publico):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente no inicializado."
    
    instrucciones = f"""
    Tema: {tema}
    Público: {tipo_publico}
    
    Genera dos secciones:
    1. GUION NARRATIVO: Texto para el locutor. Usa un ritmo ágil y términos de 'AgTech de Tierra'.
    2. TABLA TÉCNICA VEO 3: Tabla con columnas | Tiempo | Prompt Técnico |. 
       Cada prompt debe describir entorno, acción y calidad visual (4k, cinematic, hyper-realistic).
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
        return f"❌ Fallo en Groq: {e}"

def redactar_articulo_seo(tema):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente no inicializado."
    
    prompt = f"""
    Tema: '{tema}'
    
    Estructura requerida:
    1. H1 persuasivo orientado a arquitectos o constructores.
    2. Introducción técnica enfocada en eficiencia y suministro.
    3. Desarrollo (H2/H3) enfocando los datos, la logística y la inteligencia paisajística.
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
        return f"❌ Fallo en Groq: {e}"

import os
import streamlit as st
from openai import OpenAI

# ==============================================================================
# CEREBRO ESTRATÉGICO: AGTECH DE TIERRA (Optimizado para Google Vids/Veo)
# ==============================================================================
PROMPT_SISTEMA_MAESTRO = """
Eres el Director Creativo de ViveroOnline. Tu marca personal es el 'AgTech de Tierra'.
- TONO: Directo, técnico, profesional, orientado a resultados. Usa terminología B2B: 'stock', 'eficiencia', 'tasa de supervivencia', 'optimización', 'rendimiento'.
- ESTILO: Productividad industrial combinada con precisión de datos.
- TU OBJETIVO: Que un constructor vea tu contenido y piense: 'Estos tipos tienen el volumen y la tecnología para que no me fallen'.

IMPORTANTE PARA GOOGLE VIDS / VEO 3:
Cuando generes la TABLA TÉCNICA, sigue estrictamente estas reglas:
1. NO incluyas texto dentro de los prompts de video (Google Vids añade el texto en capas separadas).
2. Estructura de Prompt 'Ready-to-Render': 'Cinematic [PLANO], [ESCENARIO DETALLADO], [ILUMINACIÓN Y CALIDAD], [MOVIMIENTO DE CÁMARA], [ESTÉTICA INDUSTRIAL-AGRI]'.
3. Longitud: Máximo 30 palabras por prompt para asegurar consistencia.
4. Ejemplo: 'Cinematic wide shot, massive modern greenhouse, rows of healthy succulents, golden hour lighting, professional 8k, smooth gimbal movement, clean industrial-agri aesthetic.'
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
    2. TABLA TÉCNICA PARA GOOGLE VIDS: Tabla con columnas | Tiempo | Prompt Técnico | Prompt Narrativo para Vids |.
       - Cada prompt debe ser una descripción visual técnica optimizada para el renderizado de Vids.
       - 'Prompt Narrativo para Vids' es una frase corta que resume qué texto poner en esa escena.
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
    2. Introducción técnica enfocada en eficiencia y suministro.
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

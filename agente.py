# Archivo: agente.py
import os
import streamlit as st
from openai import OpenAI

PROMPT_SISTEMA_MAESTRO = """
Eres el Director Creativo de ViveroOnline. Tu marca personal es el 'AgTech de Tierra'.
- TONO: Directo, técnico, profesional, orientado a resultados. 
- ESTILO: Productividad industrial combinada con precisión de datos.
- IMPORTANTE PARA GOOGLE VIDS / VEO 3: Estructura 'Ready-to-Render'. Máximo 30 palabras por prompt. 
PALABRAS CLAVE OBLIGATORIAS EN PROMPTS VISUALES: escala, invernadero comercial, lote mayorista, carga logística.
"""

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key: return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def redactar_guion_viral(tema, tipo_publico="Constructoras y Jefes de Compras B2B"):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente Groq no inicializado."
    
    instrucciones = f"""
    Tema Visual: {tema}
    Público: {tipo_publico}
    Genera dos secciones obligatorias en formato Markdown:
    1. GUION NARRATIVO: Texto para el locutor. 
    2. TABLA TÉCNICA PARA VEO 3 / VIDS.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": instrucciones}
            ],
            temperature=0.5
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"

def redactar_articulo_seo(tema):
    client = get_groq_client()
    if not client: return "⚠️ Error: Cliente Groq no inicializado."
    
    prompt = f"""
    Tema: '{tema}'
    Estructura requerida (Framework PAS B2B):
    1. PROBLEMA (H2)
    2. AGITACIÓN (Párrafo)
    3. SOLUCIÓN (H2/H3)
    4. RESPALDO LOGÍSTICO
    5. CTA
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

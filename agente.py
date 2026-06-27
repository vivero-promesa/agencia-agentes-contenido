import os
import streamlit as st
from openai import OpenAI

def get_groq_client():
    """
    Inicializa el cliente de Groq de forma segura (Lazy Loading).
    Solo se ejecuta cuando se necesita generar contenido, evitando caídas en el arranque.
    """
    try:
        # Busca en st.secrets primero, si falla busca en las variables locales (.env)
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        
        if not api_key:
            return None
            
        return OpenAI(
            api_key=api_key, 
            base_url="https://api.groq.com/openai/v1"
        )
    except Exception as e:
        print(f"Error de inicialización de cliente: {e}")
        return None

def redactar_guion_viral(tema, tipo_publico):
    """Genera un guion corto optimizado para retención en redes sociales."""
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente no inicializado. Revisa tu GROQ_API_KEY."
    
    instrucciones = f"""
    Eres el Director Creativo de una agencia de contenido en Silicon Valley.
    Tu misión es crear guiones cortos (Reels/TikToks) altamente virales.
    
    Tema del video: {tema}
    Público objetivo: {tipo_publico}
    
    Reglas:
    1. Primeros 3 segundos: Un gancho visual y narrativo brutal.
    2. Desarrollo: Valor directo.
    3. Cierre: Llamado a la acción claro (visitar ViveroOnline).
    
    Devuelve SOLO el guion estructurado.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": instrucciones}]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la API de Groq: {e}"

def redactar_articulo_seo(tema):
    """Genera un artículo de blog estructurado y optimizado para buscadores."""
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente no inicializado. Revisa tu GROQ_API_KEY."
    
    prompt = f"""
    Actúa como un experto en SEO y AgTech en Colombia. Escribe un artículo de blog de unas 600 palabras 
    sobre: '{tema}'.
    
    Estructura requerida:
    1. Título gancho optimizado para buscadores.
    2. Introducción que conecte con el problema del productor o comprador ornamental.
    3. Desarrollo con subtítulos claros (H2 y H3) que resuelva la duda técnica.
    4. Conclusión que posicione a ViveroOnline como la solución definitiva.
    5. Llamado a la acción (CTA) directo: Invita a visitar el marketplace de ViveroOnline para cotizar.
    
    Usa un tono profesional, informativo y cercano al mercado de la Sabana de Bogotá.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la API de Groq: {e}"

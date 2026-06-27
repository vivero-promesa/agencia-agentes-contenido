import streamlit as st
import os
from openai import OpenAI

def get_blog_client():
    """
    Inicializa el cliente de forma segura solo cuando se va a generar un artículo.
    Evita que la app colapse al arrancar.
    """
    try:
        # Busca en los secretos de la nube o en el entorno local
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        if not api_key:
            return None
            
        return OpenAI(
            api_key=api_key, 
            base_url="https://api.groq.com/openai/v1"
        )
    except Exception as e:
        print(f"Error cargando credenciales: {e}")
        return None

def redactar_articulo_seo(tema):
    """
    Genera el artículo llamando al cliente de Groq de forma controlada.
    """
    client = get_blog_client()
    
    if not client:
        return "❌ Error: La llave 'GROQ_API_KEY' no fue encontrada en st.secrets."

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
        # Si la API de Groq se cae, capturamos el error sin romper la app
        return f"❌ Fallo al generar el artículo con la IA: {e}"

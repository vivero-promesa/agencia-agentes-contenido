import streamlit as st
from openai import OpenAI

def get_client():
    """Inicializa el cliente de forma segura utilizando los secretos de Streamlit."""
    try:
        # Accedemos a la llave desde los secretos de Streamlit
        api_key = st.secrets["GROQ_API_KEY"]
        return OpenAI(
            api_key=api_key, 
            base_url="https://api.groq.com/openai/v1"
        )
    except KeyError:
        st.error("Error: La llave 'GROQ_API_KEY' no está configurada en los secretos de Streamlit.")
        return None

def redactar_guion_viral(tema, tipo_publico):
    client = get_client()
    if not client: return "Error de configuración."
    
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
    
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[{"role": "user", "content": instrucciones}]
    )
    return respuesta.choices[0].message.content

def redactar_articulo_seo(tema):
    client = get_client()
    if not client: return "Error de configuración."
    
    prompt = f"""
    Actúa como un experto en SEO y AgTech en Colombia. Escribe un artículo de blog sobre: '{tema}'.
    
    Estructura requerida:
    1. Título gancho optimizado.
    2. Introducción que conecte con el problema del productor.
    3. Desarrollo con subtítulos (H2 y H3).
    4. Conclusión que posicione a ViveroOnline como la solución.
    5. CTA directo a ViveroOnline.
    
    Tono: Profesional, informativo y cercano a la Sabana de Bogotá.
    """
    
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return respuesta.choices[0].message.content

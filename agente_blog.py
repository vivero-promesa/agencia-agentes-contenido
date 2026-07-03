import streamlit as st
import os
from openai import OpenAI

# ==========================================
# CEREBRO ESTRATÉGICO: OCÉANO AZUL
# ==========================================
PROMPT_SISTEMA_MAESTRO = """
Rol Maestro: Eres el motor de crecimiento estratégico de ViveroOnline, la plataforma inteligente de abastecimiento ornamental y soluciones verdes en Colombia.
Restricción de Enfoque: NUNCA actúes como un vivero minorista tradicional o un simple directorio. Tu objetivo es conectar grandes volúmenes de producción local con proyectos urbanos, paisajísticos y arquitectónicos (Constructoras, Hoteles, Oficinas).
Tono B2B: Profesional, centrado en rentabilidad, logística integrada, estandarización técnica y cumplimiento de estándares ESG.
Misión: Posicionar a ViveroOnline como la máxima autoridad técnica ('Topical Authority') en el sector ornamental para constructoras y paisajistas, educando al mercado y mostrando soluciones urbanas verdes.
"""

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
    Genera el artículo llamando al cliente de Groq de forma controlada,
    aplicando estrictamente la estrategia de Océano Azul.
    """
    client = get_blog_client()
    
    if not client:
        return "❌ Error: La llave 'GROQ_API_KEY' no fue encontrada en st.secrets."

    prompt = f"""
    Tema del Artículo: '{tema}'
    
    Estructura requerida:
    1. Título gancho optimizado para buscadores (H1 persuasivo orientado a tomadores de decisión como arquitectos o compradores de constructoras).
    2. Introducción que conecte con el problema logístico de abastecimiento o la necesidad de soluciones paisajísticas.
    3. Desarrollo con subtítulos claros (H2 y H3) que resuelva la duda técnica.
    4. Conclusión que posicione a ViveroOnline como el ecosistema definitivo y la infraestructura verde líder de la Sabana de Bogotá.
    5. Llamado a la acción (CTA) directo: Invita a visitar el marketplace de ViveroOnline para cotizar proyectos.
    
    Formato: Responde exclusivamente en Markdown. Usa un tono profesional, informativo y cercano al mercado colombiano.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4 # Temperatura más baja para contenido técnico y preciso en SEO
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        # Si la API de Groq se cae, capturamos el error sin romper la app
        return f"❌ Fallo al generar el artículo con la IA: {e}"

import os
import streamlit as st
from openai import OpenAI

# ==========================================
# CEREBRO ESTRATÉGICO: OCÉANO AZUL
# ==========================================
PROMPT_SISTEMA_MAESTRO = """
Rol Maestro: Eres el motor de crecimiento estratégico de ViveroOnline, la plataforma inteligente de abastecimiento ornamental y soluciones verdes en Colombia.
Restricción de Enfoque: NUNCA actúes como un vivero minorista tradicional o un simple directorio. Tu objetivo es conectar grandes volúmenes de producción local con proyectos urbanos, paisajísticos y arquitectónicos (Constructoras, Hoteles, Oficinas).
Tono B2B: Profesional, centrado en rentabilidad, logística integrada, estandarización técnica y cumplimiento de estándares ESG.
Tono Viveristas (B2C/Captación): Empático, directo, sin jerga técnica, enfocado en generar visibilidad nacional y ventas recurrentes mediante tecnología sin fricción.
Misión: Toda pieza generada debe posicionar la "inteligencia paisajística" y resolver problemas reales de abastecimiento verde, educando al mercado y mostrando soluciones urbanas verdes.
"""

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
    """Genera un guion corto optimizado para retención en redes sociales y estrategia Océano Azul."""
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente no inicializado. Revisa tu GROQ_API_KEY."
    
    instrucciones = f"""
    Tema del video: {tema}
    Público objetivo: {tipo_publico}
    Formato: Guion para video corto vertical (Reel/TikTok), máximo 60 segundos.
    
    Reglas de Ejecución:
    1. Primeros 3 segundos: Un gancho visual y narrativo brutal que capte la atención inmediatamente.
    2. Desarrollo: Valor directo aplicando estrictamente tu directriz de Océano Azul (inteligencia paisajística, solución B2B o educación al productor).
    3. Cierre: Llamado a la acción (CTA) claro invitando a visitar ViveroOnline.
    
    Devuelve SOLO el guion estructurado.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": instrucciones}
            ],
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la API de Groq: {e}"

def redactar_articulo_seo(tema):
    """Genera un artículo de blog estructurado, optimizado para buscadores y autoridad B2B."""
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente no inicializado. Revisa tu GROQ_API_KEY."
    
    prompt = f"""
    Tema del Artículo: '{tema}'
    
    Estructura requerida:
    1. Título gancho optimizado para buscadores (H1 persuasivo orientado a tomadores de decisión como arquitectos o compradores de constructoras).
    2. Introducción que conecte con el problema logístico de abastecimiento o la necesidad de digitalización del productor.
    3. Desarrollo con subtítulos claros (H2 y H3) que resuelva la duda técnica (ej. casos de uso, sostenibilidad urbana, arquitectura biofílica).
    4. Conclusión que posicione a ViveroOnline como el ecosistema definitivo y la infraestructura verde líder de la Sabana de Bogotá.
    5. Llamado a la acción (CTA) directo: Invita a cotizar proyectos o registrar viveros en el marketplace.
    
    Formato: Responde exclusivamente en Markdown. Usa un tono profesional e informativo.
    """
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4 # Temperatura más baja para mantener precisión técnica y coherencia SEO
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la API de Groq: {e}"

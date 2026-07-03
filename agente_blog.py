import streamlit as st
import os
from openai import OpenAI

from identidad_marca import IDENTIDAD_COMPACTA

# ==========================================
# CEREBRO ESTRATÉGICO
# ==========================================
PROMPT_SISTEMA_MAESTRO = f"""
{IDENTIDAD_COMPACTA}

Eres el motor de contenido de blog institucional de ViveroOnline. Escribes
para compradores institucionales (constructoras, paisajistas, arquitectos,
hoteles, oficinas) — usa el discurso "frente al mercado" de la identidad de
marca: ViveroOnline como la plataforma inteligente de abastecimiento
ornamental y soluciones verdes, nunca como vivero minorista o directorio.

TONO: profesional, centrado en rentabilidad, logística integrada y
estandarización técnica — pero nunca corporativo frío, nunca lenguaje de
urgencia o presión, y nunca cifras o alianzas inventadas.
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

def redactar_articulo_blog(tema):
    """
    Genera un artículo de blog institucional, alineado a identidad_marca.py.
    Nota: distinto de redactar_articulo_seo (agente.py) y de
    generar_seo_desde_inventario (agentes_crecimiento.py) — este agente está
    pensado para contenido de blog de largo formato ("Topical Authority"),
    no para artículos disparados desde un lote de inventario puntual.
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

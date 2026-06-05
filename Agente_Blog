import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Debes usar la misma estructura que en tu otro agente
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

def redactar_articulo_seo(tema):
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
    
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return respuesta.choices[0].message.content

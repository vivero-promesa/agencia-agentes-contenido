import streamlit as st
import os
from datetime import date
from openai import OpenAI

from identidad_marca import IDENTIDAD_COMPACTA

# ==========================================
# CEREBRO ESTRATÉGICO
# ==========================================
PROMPT_SISTEMA_MAESTRO = f"""
{IDENTIDAD_COMPACTA}

Eres el motor de contenido de blog institucional de ViveroOnline, optimizado
para GEO/AEO (Generative Engine Optimization / Answer Engine Optimization):
buscadores con IA como ChatGPT, Perplexity y Gemini, que extraen o citan
pasajes directos en vez de solo indexar páginas. Escribes para compradores
institucionales (constructoras, paisajistas, arquitectos, hoteles, oficinas)
— usa el discurso "frente al mercado" de la identidad de marca: ViveroOnline
como la plataforma inteligente de abastecimiento ornamental y soluciones
verdes, nunca como vivero minorista o directorio.

Reglas de escritura para GEO/AEO (además del tono de marca):

1. EXTRACCIÓN POR PÁRRAFO: cada H2 debe abrir con una mini-respuesta
   autocontenida de 40-80 palabras — no solo la introducción del artículo.
   Un motor de IA puede citar cualquier sección, no solo la primera; cada
   una debe sostenerse sola, sin depender de leer el resto.

2. VERIFICABILIDAD: cuando tengas un dato real disponible (especificación
   técnica, altitud, comportamiento de una especie, plazo logístico
   documentado), inclúyelo con precisión — un dato concreto pesa más que
   una frase de marketing genérica. Nunca inventes cifras que no te dieron;
   pero tampoco omitas por seguridad un dato real que sí tengas — omitirlo
   es igual de débil que inventarlo.

3. AUTORIDAD DE NICHO: escribe como alguien con conocimiento real del
   sector viverista de la Sabana de Bogotá — condiciones de altiplano
   (~2.600 msnm), clima frío/húmedo, comportamiento real de las especies en
   esa zona. Evita generalidades que cualquier blog genérico de plantas
   podría decir.

4. Define cualquier término técnico la primera vez que aparece, en una
   frase clara y autocontenida.

TONO: profesional, centrado en rentabilidad, logística integrada y
estandarización técnica — pero nunca corporativo frío, nunca lenguaje de
urgencia o presión.
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

def redactar_articulo_blog(tema, datos_verificables=None, prioridad_estrategica=None):
    """
    Genera un artículo de blog institucional optimizado para GEO/AEO
    (buscadores con IA), alineado a identidad_marca.py.

    datos_verificables: opcional — cifras/especificaciones REALES que
    tengas a mano (ej. "tiempo de aclimatación: 15 días: peso bulto: 12kg").
    Si no lo pasas, el agente no inventa ninguno, pero sí puede usar hechos
    generales ya conocidos del sector (altitud, clima) vía identidad_marca.

    La fecha de "última actualización" se inserta en Python (no la genera
    el LLM) para que sea siempre exacta, nunca alucinada.

    Distinto de redactar_articulo_seo (agente.py) y de
    generar_seo_desde_inventario/generar_seo_por_intencion
    (agentes_crecimiento.py) — este agente está pensado para contenido de
    blog de largo formato ("Topical Authority"), no para artículos
    disparados desde un lote de inventario o cluster puntual.
    """
    client = get_blog_client()
    
    if not client:
        return "❌ Error: La llave 'GROQ_API_KEY' no fue encontrada en st.secrets."

    fecha_hoy = date.today().strftime("%d de %B de %Y")

    prioridad_texto = (
        f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL (ajusta el CTA en función de esto):\n{prioridad_estrategica}\n"
        if prioridad_estrategica else ""
    )
    datos_texto = (
        f"\n\nDATOS VERIFICABLES REALES para este artículo (úsalos con precisión, no los redondees ni generalices):\n{datos_verificables}\n"
        if datos_verificables else
        "\n\nNo se suministraron datos verificables puntuales para este artículo — no inventes cifras específicas, pero sí usa los hechos generales reales del sector (altitud, clima) que ya conoces.\n"
    )

    prompt = f"""
    Tema del Artículo: '{tema}'
    {prioridad_texto}{datos_texto}
    Estructura requerida (formato GEO/AEO):

    1. TÍTULO (H1): claro y directo, en lenguaje natural — cómo alguien
       realmente le preguntaría esto a un asistente de IA, no una frase
       gancho publicitaria.

    2. RESPUESTA DIRECTA (40-80 palabras, justo debajo del título, sin
       encabezado): responde la pregunta central del tema de forma completa
       y autocontenida — esto es lo primero que un motor de IA va a citar.

    3. DESARROLLO: 3-4 secciones, cada una con un H2 en forma de pregunta
       natural. CADA H2 debe abrir con su propia mini-respuesta autocontenida
       de 40-80 palabras (no solo el primero) — recuerda que un motor de IA
       puede citar cualquier sección de forma aislada. Usa listas o tablas
       donde ayude a estructurar la información (formato de datos
       estructurados, no solo párrafos).

    4. PREGUNTAS FRECUENTES (H2 "Preguntas Frecuentes"): exactamente 3-5
       pares, en este formato exacto para poder copiarlos directo a un
       bloque de FAQ (cada uno en líneas separadas, sin numeración ni
       viñetas adicionales):

       PREGUNTA 1: [pregunta natural]
       RESPUESTA 1: [respuesta autocontenida, 2-4 frases]

       PREGUNTA 2: [pregunta natural]
       RESPUESTA 2: [respuesta autocontenida, 2-4 frases]

       (y así sucesivamente hasta 5 máximo)

       Reglas para esta sección — son las que más se rompen si no se
       siguen:
       - CONDENSAR, NUNCA DUPLICAR: cada respuesta es un resumen ultra
         condensado de una idea que ya está en el cuerpo del artículo,
         con palabras DISTINTAS a como se explicó ahí — nunca copies o
         parafrasees casi textual un párrafo del desarrollo. Si una
         pregunta no puede resumirse en 2-4 frases sin perder lo
         esencial, no es una buena pregunta para esta sección.
       - Máximo 5 preguntas — más que eso diluye la señal para el motor
         de IA en vez de reforzarla; calidad y foco importan más que
         cantidad.
       - Nunca dejes texto de un intento anterior mezclado con uno nuevo
         (revisa que cada respuesta empiece limpia, sin fragmentos
         sueltos al inicio).

    5. CTA: invitación concreta a cotizar en ViveroOnline.

    6. Opcional / solo si no vas a usar el bloque FAQ nativo de tu plugin
       de SEO: al final, agrega un bloque de código con el schema JSON-LD
       (Article + FAQPage, usando las mismas preguntas/respuestas del
       punto 4). Si usas Rank Math u otro plugin con bloque FAQ nativo,
       este bloque de código NO es necesario — el plugin genera el schema
       automáticamente y de forma más confiable que un JSON armado por un
       LLM. Indica igual cuál de los dos caminos aplica, para que quede
       claro en el resultado.

    Formato: Markdown limpio para el artículo. Tono profesional,
    informativo, cercano al mercado colombiano — nunca corporativo frío
    ni con lenguaje de urgencia. Al final de todo, agrega una nota corta
    "Cómo publicar el FAQ:" recordando: (a) insertar un encabezado H2
    "Preguntas Frecuentes" antes del bloque en el editor, (b) usar el
    bloque de contenido nativo "FAQ" del plugin de SEO (no el Generador
    de Schema si es una función marcada como PRO), pegando cada pregunta
    y respuesta ahí.
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
        contenido = respuesta.choices[0].message.content
        return f"{contenido}\n\n---\n*Última actualización: {fecha_hoy}*"
    except Exception as e:
        # Si la API de Groq se cae, capturamos el error sin romper la app
        return f"❌ Fallo al generar el artículo con la IA: {e}"

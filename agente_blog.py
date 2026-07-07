import streamlit as st
import os
import re
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

TONO: profesional, centrado en rentabilidad, logística integrada y
estandarización técnica — pero nunca corporativo frío, nunca lenguaje de
urgencia o presión.
"""

# Marcadores mínimos de autoridad de nicho — si ninguno aparece en el
# cuerpo, se considera que el artículo quedó genérico y se reintenta.
_MARCADORES_NICHO = ["sabana de bogotá", "msnm", "altiplano", "2.600", "2600"]


def get_blog_client():
    """
    Inicializa el cliente de forma segura solo cuando se va a generar un artículo.
    Evita que la app colapse al arrancar.
    """
    try:
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


def _llamar_modelo(client, prompt_usuario, temperature=0.4):
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA_MAESTRO},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=temperature
    )
    return respuesta.choices[0].message.content


def _contiene_autoridad_nicho(texto: str) -> bool:
    texto_low = texto.lower()
    return any(m in texto_low for m in _MARCADORES_NICHO)


def _frase_larga_repetida(respuesta: str, cuerpo: str, min_palabras: int = 6) -> bool:
    """Detecta si la respuesta copia una secuencia de min_palabras o más
    palabras consecutivas del cuerpo, sin importar mayúsculas/orden del
    resto del texto — señal fuerte de duplicación real.

    Se prefiere esto sobre una similitud global (tipo difflib ratio contra
    todo el cuerpo) porque una respuesta corta comparada contra un artículo
    mucho más largo diluye el porcentaje de parecido incluso cuando SÍ hay
    frases enteras copiadas — probado con un caso real donde el ratio
    global salía en 0.2-0.3 (bajo el umbral) pese a tener 19 secuencias de
    6+ palabras copiadas literalmente.
    """
    palabras_resp = re.findall(r"\w+", respuesta.lower())
    texto_cuerpo = " ".join(re.findall(r"\w+", cuerpo.lower()))
    for i in range(len(palabras_resp) - min_palabras + 1):
        secuencia = " ".join(palabras_resp[i:i + min_palabras])
        if secuencia in texto_cuerpo:
            return True
    return False


def _faq_duplica_cuerpo(respuestas, cuerpo: str) -> bool:
    return any(_frase_larga_repetida(r, cuerpo) for r in respuestas)


def _generar_cuerpo(client, tema, prioridad_texto, datos_texto, forzar_nicho=False):
    """Paso 1: genera el artículo SIN la sección de FAQ — un prompt más
    simple, con menos reglas simultáneas, que un modelo pequeño cumple
    mejor que un prompt gigante con 6 reglas a la vez."""
    refuerzo_nicho = (
        "\nRECORDATORIO CRÍTICO: el intento anterior no incluyó ningún "
        "detalle real de la Sabana de Bogotá (altitud ~2.600 msnm, clima "
        "frío/húmedo de altiplano). Esta vez SÍ debes mencionarlo "
        "explícitamente al menos una vez, de forma natural.\n"
        if forzar_nicho else ""
    )

    prompt = f"""
    Tema del Artículo: '{tema}'
    {prioridad_texto}{datos_texto}{refuerzo_nicho}
    Estructura requerida (formato GEO/AEO):

    1. TÍTULO (H1): claro y directo, en lenguaje natural — cómo alguien
       realmente le preguntaría esto a un asistente de IA.

    2. RESPUESTA DIRECTA (40-80 palabras, justo debajo del título, sin
       encabezado): responde la pregunta central del tema de forma completa
       y autocontenida — esto es lo primero que un motor de IA va a citar.

    3. DESARROLLO: 3-4 secciones, cada una con un H2 en forma de pregunta
       natural. CADA H2 debe abrir con una mini-respuesta autocontenida de
       40-80 palabras ANTES de cualquier lista o tabla — nunca vayas
       directo a una lista sin esa mini-respuesta primero. Usa listas donde
       ayude a estructurar, pero después del párrafo inicial, no en vez de él.

    4. AUTORIDAD DE NICHO (obligatorio, no opcional): en al menos una
       sección, escribe como alguien con conocimiento real del sector
       viverista de la Sabana de Bogotá — menciona explícitamente la
       altitud (~2.600 msnm) o el clima frío/húmedo de altiplano y cómo
       afecta el tema del artículo. Evita generalidades que cualquier blog
       genérico de plantas podría decir.

    5. CTA: invitación concreta a cotizar en ViveroOnline.

    NO incluyas sección de Preguntas Frecuentes — eso se genera aparte.

    Formato: Markdown limpio. Nunca inventes cifras que no te dieron; si no
    hay datos verificables, usa hechos generales reales del sector, nunca
    números inventados.
    """
    return _llamar_modelo(client, prompt, temperature=0.4)


def _generar_faq(client, tema, cuerpo, forzar_distinto=False):
    """Paso 2: genera el FAQ en una llamada aparte, mostrándole al modelo
    el cuerpo ya escrito y pidiéndole explícitamente que NO lo repita.
    Separar esto del paso 1 reduce muchísimo la duplicación, porque el
    modelo ya no tiene que 'recordar' no copiarse a sí mismo dentro del
    mismo texto que está generando."""
    refuerzo = (
        "\nATENCIÓN: un intento anterior repitió casi las mismas frases del "
        "cuerpo del artículo en las respuestas del FAQ. Esta vez cada "
        "respuesta debe estar escrita con palabras notablemente distintas "
        "— resume la idea, no la copies.\n"
        if forzar_distinto else ""
    )

    prompt = f"""
    Este es el artículo ya escrito (NO lo repitas, NO copies frases de aquí
    literalmente):
    ---
    {cuerpo}
    ---
    {refuerzo}
    Genera EXACTAMENTE 4 preguntas frecuentes, todas directamente
    relacionadas con el tema central: "{tema}". Nunca incluyas una pregunta
    genérica sobre el catálogo general de ViveroOnline (ej. "qué plantas
    hay disponibles") salvo que sea literalmente el tema del artículo.

    Formato exacto, sin numeración ni viñetas adicionales:

    PREGUNTA 1: [pregunta natural]
    RESPUESTA 1: [resumen en 2-4 frases, con palabras DISTINTAS a como se
    explicó en el cuerpo]

    PREGUNTA 2: ...
    RESPUESTA 2: ...

    (hasta la Pregunta 4)
    """
    return _llamar_modelo(client, prompt, temperature=0.5)


def _extraer_respuestas_faq(faq_texto: str):
    """Extrae solo el texto de las respuestas (sin las preguntas) para
    poder medir similitud contra el cuerpo del artículo."""
    return re.findall(r"RESPUESTA\s*\d+:\s*(.+)", faq_texto)


def redactar_articulo_blog(tema, datos_verificables=None, prioridad_estrategica=None):
    """
    Genera un artículo de blog institucional optimizado para GEO/AEO,
    alineado a identidad_marca.py.

    Proceso en 2 pasos + validación automática (en vez de un solo prompt
    gigante, que un modelo como Llama 3.1 8B no cumple de forma confiable
    cuando tiene muchas reglas simultáneas):
      1. Genera el cuerpo del artículo (sin FAQ). Si no menciona la Sabana
         de Bogotá / altitud, se reintenta una vez con recordatorio explícito.
      2. Genera el FAQ aparte, mostrándole el cuerpo ya escrito y pidiendo
         explícitamente que no lo repita. Si alguna respuesta copia una
         frase de 6+ palabras consecutivas del cuerpo, se reintenta una vez
         con una instrucción más fuerte (ver _frase_larga_repetida — un
         ratio de similitud global resultó poco sensible en la práctica).

    datos_verificables: opcional — cifras/especificaciones REALES que
    tengas a mano. Si no lo pasas, el agente no inventa ninguno.

    La fecha de "última actualización" se inserta en Python (no la genera
    el LLM) para que sea siempre exacta, nunca alucinada.
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

    try:
        # --- PASO 1: Cuerpo del artículo ---
        cuerpo = _generar_cuerpo(client, tema, prioridad_texto, datos_texto)
        nota_nicho = ""
        if not _contiene_autoridad_nicho(cuerpo):
            cuerpo_reintento = _generar_cuerpo(client, tema, prioridad_texto, datos_texto, forzar_nicho=True)
            if _contiene_autoridad_nicho(cuerpo_reintento):
                cuerpo = cuerpo_reintento
            else:
                # Tras el reintento sigue sin aparecer — se avisa en vez de
                # fingir que quedó resuelto.
                nota_nicho = "\n\n⚠️ *Nota interna: este artículo no incluyó lenguaje de autoridad de nicho (Sabana de Bogotá / altitud) tras 2 intentos — revisar manualmente antes de publicar.*"

        # --- PASO 2: FAQ, condicionado al cuerpo ya escrito ---
        faq = _generar_faq(client, tema, cuerpo)
        respuestas = _extraer_respuestas_faq(faq)
        hay_duplicado = _faq_duplica_cuerpo(respuestas, cuerpo)

        nota_faq = ""
        if hay_duplicado:
            faq_reintento = _generar_faq(client, tema, cuerpo, forzar_distinto=True)
            respuestas_reintento = _extraer_respuestas_faq(faq_reintento)
            if not _faq_duplica_cuerpo(respuestas_reintento, cuerpo):
                faq = faq_reintento
                hay_duplicado = False
            else:
                nota_faq = "\n\n⚠️ *Nota interna: el FAQ generado repite frases textuales del cuerpo del artículo tras 2 intentos — revisar y reescribir manualmente antes de publicar.*"

        nota_publicacion = (
            "\n\n---\n**Cómo publicar el FAQ:** inserta un encabezado H2 "
            "\"Preguntas Frecuentes\" antes del bloque en el editor, y usa "
            "el bloque de contenido nativo \"FAQ\" de tu plugin de SEO "
            "(ej. Rank Math) — no el Generador de Schema si es función PRO."
        )

        contenido_final = (
            f"{cuerpo}\n\n## Preguntas Frecuentes\n\n{faq}"
            f"{nota_publicacion}{nota_nicho}{nota_faq}"
            f"\n\n---\n*Última actualización: {fecha_hoy}*"
        )
        return contenido_final

    except Exception as e:
        # Si la API de Groq se cae, capturamos el error sin romper la app
        return f"❌ Fallo al generar el artículo con la IA: {e}"

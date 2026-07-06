# Archivo: agente.py
import os
import streamlit as st
from openai import OpenAI

from identidad_marca import IDENTIDAD_COMPACTA
from brand_book import GUIA_VISUAL_VIDEO

def _construir_prompt_sistema(prioridad_estrategica: str = None) -> str:
    extra = f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL:\n{prioridad_estrategica}\n" if prioridad_estrategica else ""
    return f"""
{IDENTIDAD_COMPACTA}
{extra}
Eres el Director Creativo de ViveroOnline. Escribes para compradores
institucionales (constructoras, paisajistas, arquitectos, jefes de compras
B2B) — usa el discurso "frente al mercado" de la identidad de marca.

TONO: profesional, concreto, orientado a resultados — nunca corporativo frío
ni exagerado, nunca lenguaje de urgencia o presión.
"""


def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def redactar_guion_viral(tema, tipo_publico="Constructoras y Jefes de Compras B2B", prioridad_estrategica=None):
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente Groq no inicializado."

    instrucciones = f"""
    Tema Visual: {tema}
    Público: {tipo_publico}

    Genera dos secciones obligatorias en formato Markdown:

    1. GUION NARRATIVO: texto para el locutor, tono cercano y profesional,
       nunca de venta agresiva.

    2. TABLA TÉCNICA PARA VEO 3 / VIDS: una tabla con columnas
       Escena | Visual | Cámara | Nota de estilo, donde cada fila respete
       esta guía visual (vivero real de la Sabana de Bogotá, no bodega
       industrial genérica):

    {GUIA_VISUAL_VIDEO.strip()}
    """

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _construir_prompt_sistema(prioridad_estrategica)},
                {"role": "user", "content": instrucciones}
            ],
            temperature=0.5
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"


def redactar_articulo_seo(tema, prioridad_estrategica=None):
    client = get_groq_client()
    if not client:
        return "⚠️ Error: Cliente Groq no inicializado."

    prompt = f"""
    Tema: '{tema}'
    Estructura requerida (Framework PAS B2B):
    1. PROBLEMA (H2)
    2. AGITACIÓN (Párrafo — sin exagerar ni inventar cifras)
    3. SOLUCIÓN (H2/H3)
    4. RESPALDO LOGÍSTICO (cómo se coordina el despacho de planta viva)
    5. CTA (invitación concreta a cotizar en ViveroOnline — si hay una
       prioridad estratégica activa, el CTA debe reflejarla)
    """

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _construir_prompt_sistema(prioridad_estrategica)},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"

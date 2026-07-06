# Archivo: competencia.py
import os
import streamlit as st
from openai import OpenAI

from identidad_marca import IDENTIDAD_COMPACTA


def get_client_competencia():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def analizar_contra_competencia(tema_o_planta: str, estrategia_competitiva: str, prioridad_estrategica: str = None):
    """
    Genera un pitch competitivo real, usando SOLO la estrategia competitiva
    escrita a mano por el usuario (guardada en Supabase, ver estrategia.py /
    clave CLAVE_ESTRATEGIA_COMPETITIVA) como contexto de competidores.

    A propósito, esta función nunca inventa nombres de competidores ni sus
    características — si no hay estrategia_competitiva guardada, lo dice
    en vez de fabricar algo (nada de "Vivero X" genérico).
    """
    if not estrategia_competitiva or not estrategia_competitiva.strip():
        return (
            "⚠️ Aún no has escrito tu estrategia competitiva (pestaña "
            "Competencia → cuadro de arriba, guárdalo primero). Sin eso, "
            "el agente no tiene información real de competidores para "
            "comparar, y no va a inventarla."
        )

    client = get_client_competencia()
    if not client:
        return "⚠️ Error: Cliente Groq no inicializado (falta GROQ_API_KEY)."

    prioridad_texto = (
        f"\n\nPRIORIDAD ESTRATÉGICA ACTUAL:\n{prioridad_estrategica}\n"
        if prioridad_estrategica else ""
    )

    prompt_sistema = f"""
{IDENTIDAD_COMPACTA}
{prioridad_texto}
Eres el analista competitivo de ViveroOnline. Escribes pitches breves y
concretos que resaltan la ventaja real frente a la competencia — nunca
inventas competidores, cifras o características que no estén en el
contexto competitivo que te dan. Si el contexto no cubre algo, no lo
menciones, no lo inventes.
"""

    prompt_usuario = f"""
CONTEXTO COMPETITIVO REAL (escrito a mano por el equipo — única fuente de verdad sobre competidores):
{estrategia_competitiva}

Genera un pitch de 3-5 líneas para: {tema_o_planta}

El pitch debe destacar la ventaja de ViveroOnline frente a lo descrito en
el contexto de arriba, en tono profesional y concreto, nunca corporativo
frío ni con lenguaje de urgencia.
"""

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.4
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ Fallo en la comunicación con Groq: {e}"

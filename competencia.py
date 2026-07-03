# Archivo: competencia.py
import streamlit as st

def get_config_competencia():
    """Aquí el humano edita el cerebro."""
    return st.text_area("🧠 Edita la Estrategia Competitiva:", value="""
    1. Vivero X: Fuertes en precio, débiles en puntualidad logística.
    2. Vivero Y: Buena calidad pero catálogo desactualizado.
    3. Nuestra ventaja: Calidad técnica + Entrega garantizada en menos de 48h.
    """, height=200)

def analizar_contra_competencia(tema_o_planta):
    estrategia = get_config_competencia()
    # Aquí el agente usa 'estrategia' como base para redactar un pitch
    # (Similar a tus otros agentes, pero usando 'estrategia' como contexto)
    return f"Basado en nuestra estrategia: {estrategia}. Pitch para {tema_o_planta}..."

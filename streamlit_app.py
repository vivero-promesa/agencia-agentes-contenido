import streamlit as st
import os
from supabase import create_client, Client
from agente import redactar_guion_viral, redactar_articulo_seo
from agente_video import generar_broll_veo

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# --- CONEXIÓN A SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Error conectando a Supabase: {e}")

# --- ESTADOS GLOBALES ---
if "contenido_actual" not in st.session_state: st.session_state.contenido_actual = None
if "video_url_actual" not in st.session_state: st.session_state.video_url_actual = None

# --- ESTRUCTURA ---
tab1, tab2 = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video (Veo 3)"])

# PESTAÑA 1: TEXTOS (Funcionalidad garantizada)
with tab1:
    st.subheader("Creador de Contenido Escrito")
    tipo = st.selectbox("Formato:", ["Reel/TikTok", "Artículo de Blog"])
    tema = st.text_input("Tema:")
    
    if st.button("Generar Contenido"):
        with st.spinner("Redactando con IA..."):
            try:
                if tipo == "Reel/TikTok":
                    st.session_state.contenido_actual = redactar_guion_viral(tema, "B2C")
                else:
                    st.session_state.contenido_actual = redactar_articulo_seo(tema)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.contenido_actual:
        st.markdown(st.session_state.contenido_actual)
        if st.button("Limpiar"):
            st.session_state.contenido_actual = None
            st.rerun()

# PESTAÑA 2: VIDEO (Funcionalidad Aislada)
with tab2:
    st.subheader("Generación Estratégica B-Roll")
    
    plantillas = {
        "🌱 Conseguir nuevos viveristas": {"estilo": "Estilo documental, cámara en mano", "entorno": "Vivero moderno en la Sabana"},
        "🛒 Vender planta": {"estilo": "Primer plano extremo, detalle de hojas", "entorno": "Gotas de rocío, luz de estudio natural"}
    }
    
    obj = st.selectbox("Objetivo:", list(plantillas.keys()))
    especie = st.text_input("Protagonista (Planta/Lugar):")
    
    if st.button("Generar B-Roll"):
        with st.spinner("Renderizando en Veo 3..."):
            try:
                url, feedback = generar_broll_veo(especie, plantillas[obj]["estilo"], plantillas[obj]["entorno"])
                if url:
                    st.session_state.video_url_actual = url
                    st.success("¡Clip generado!")
                else:
                    st.warning(f"Estado: {feedback}")
            except Exception as e:
                st.error("Fallo crítico en el motor de video.")

    if st.session_state.video_url_actual:
        st.video(st.session_state.video_url_actual)

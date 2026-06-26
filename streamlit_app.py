import streamlit as st
import os
from supabase import create_client, Client
from google import genai
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# --- CONEXIONES ---
def get_secret(key):
    return st.secrets.get(key, os.getenv(key))

try:
    supabase: Client = create_client(get_secret("SUPABASE_URL"), get_secret("SUPABASE_KEY"))
    client_ai = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
except Exception as e:
    st.error(f"Error en configuración de clientes: {e}")
    client_ai = None

# --- ESTADOS ---
if "contenido_actual" not in st.session_state: st.session_state.contenido_actual = None
if "video_url_actual" not in st.session_state: st.session_state.video_url_actual = None

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video (Veo 3)"])

# PESTAÑA 1: TEXTOS (Funcionalidad original recuperada)
with tab1:
    st.subheader("Creador de Contenido Escrito")
    tipo = st.selectbox("Formato:", ["Reel/TikTok", "Artículo de Blog"])
    tema = st.text_input("Tema:")
    
    if st.button("Generar Contenido"):
        with st.spinner("Conectando con IA..."):
            try:
                if tipo == "Reel/TikTok":
                    st.session_state.contenido_actual = redactar_guion_viral(tema, "B2C")
                else:
                    st.session_state.contenido_actual = redactar_articulo_seo(tema)
            except Exception as e:
                st.error(f"Error en generación: {e}")

    if st.session_state.contenido_actual:
        st.markdown(st.session_state.contenido_actual)
        if st.button("❌ Limpiar"):
            st.session_state.contenido_actual = None
            st.rerun()

# PESTAÑA 2: VIDEO (Funcionalidad nueva)
with tab2:
    st.subheader("Generación Estratégica B-Roll")
    # ... [Aquí mantienes el bloque de selectbox y campos de texto] ...
    # Asegúrate de envolver el botón de generar en un try/except como en los ejemplos anteriores

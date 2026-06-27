import streamlit as st
import os
from supabase import create_client
from openai import OpenAI
from google import genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ViveroOnline Comando", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# --- CONEXIONES SEGURAS ---
def get_secret(key):
    return st.secrets.get(key, os.getenv(key))

# Inicializar clientes
try:
    supabase = create_client(get_secret("SUPABASE_URL"), get_secret("SUPABASE_KEY"))
    groq_client = OpenAI(api_key=get_secret("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
    gemini_client = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video"])

# --- PESTAÑA 1: TEXTOS ---
with tab1:
    tipo = st.selectbox("Formato:", ["Reel/TikTok", "Artículo de Blog"], key="t1")
    tema = st.text_input("Tema del contenido:", key="t2")
    
    if st.button("Generar Contenido"):
        prompt = f"Actúa como experto en Viveros y escribe un {tipo} sobre {tema}. Estructura profesional y persuasiva."
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        st.session_state.texto = response.choices[0].message.content
        st.rerun()

    if "texto" in st.session_state:
        st.markdown(st.session_state.texto)

# --- PESTAÑA 2: VIDEO ---
with tab2:
    especie = st.text_input("Protagonista (Planta/Lugar):", key="v1")
    if st.button("Generar B-Roll con Veo 3"):
        with st.spinner("Renderizando..."):
            try:
                prompt_final = f"Video 4K, {especie}, estilo comercial cinematográfico."
                op = gemini_client.models.generate_videos(
                    model="veo-3.1-generate-preview",
                    prompt=prompt_final,
                    config={"aspect_ratio": "9:16"}
                )
                # Intento de obtener la URL
                st.session_state.video = op.generated_videos[0].video.uri if hasattr(op, 'generated_videos') else "Error"
                st.rerun()
            except Exception as e:
                st.error(f"Fallo en API Veo: {e}")

    if "video" in st.session_state:
        st.video(st.session_state.video)

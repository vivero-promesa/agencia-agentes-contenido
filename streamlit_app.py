import streamlit as st
import os
from supabase import create_client, Client
from google import genai

# Importamos los agentes
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo

# 1. Configuración de Conexión (Obteniendo desde st.secrets)
# Esto funciona tanto en local (.streamlit/secrets.toml) como en la nube
def get_secret(key):
    return st.secrets.get(key, os.getenv(key))

url_supabase = get_secret("SUPABASE_URL")
clave_supabase = get_secret("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, clave_supabase)

# Inicialización segura
try:
    client_ai = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
except Exception:
    client_ai = None

st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# 2. Estados
if "contenido_actual" not in st.session_state: st.session_state.contenido_actual = None
if "tabla_destino" not in st.session_state: st.session_state.tabla_destino = None
if "video_url_actual" not in st.session_state: st.session_state.video_url_actual = None

# 3. Pestañas
tab_texto, tab_video = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video (Veo 3)"])

with tab_texto:
    tipo_formato = st.selectbox("Formato:", ["Reel/TikTok", "Artículo de Blog"])
    tema_input = st.text_input("Tema:")
    if st.button("Generar Contenido"):
        with st.spinner("Conectando..."):
            if tipo_formato == "Reel/TikTok":
                # INYECTAMOS LA LLAVE AL AGENTE
                st.session_state.contenido_actual = redactar_guion_viral(tema=tema_input, tipo_publico="B2C")
                st.session_state.tabla_destino = "guiones"
            else:
                st.session_state.contenido_actual = redactar_articulo_seo(tema=tema_input)
                st.session_state.tabla_destino = "blog_posts"

    if st.session_state.contenido_actual:
        st.markdown(st.session_state.contenido_actual)
        if st.button("✅ Aprobar y Guardar"):
            supabase.table(st.session_state.tabla_destino).insert({"tema": tema_input, "contenido": st.session_state.contenido_actual}).execute()
            st.rerun()

with tab_video:
    st.subheader("Generación Estratégica B-Roll")
    # ... [Insertar aquí el bloque de plantillas que ya tienes] ...
    # Asegúrate de usar client_ai.models.generate_videos(...)

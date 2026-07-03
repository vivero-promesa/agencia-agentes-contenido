import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai

# Importación de agentes
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# ==========================================
# 1. MANEJO PROFESIONAL DE SECRETOS
# ==========================================
load_dotenv() 

def get_secret(key):
    try:
        return st.secrets[key]
    except KeyError:
        return os.getenv(key)

# ==========================================
# 2. INICIALIZACIÓN DE CLIENTES
# ==========================================
try:
    url_supabase = get_secret("SUPABASE_URL")
    clave_supabase = get_secret("SUPABASE_KEY")
    supabase: Client = create_client(url_supabase, clave_supabase) if url_supabase else None
except Exception as e:
    st.error(f"Error conectando a la base de datos: {e}")
    supabase = None

try:
    client_ai = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
except Exception:
    client_ai = None

# ==========================================
# 3. MEMORIA DE ESTADOS (Session State)
# ==========================================
if "contenido_actual" not in st.session_state: st.session_state.contenido_actual = None
if "tabla_destino" not in st.session_state: st.session_state.tabla_destino = None
if "video_url_actual" not in st.session_state: st.session_state.video_url_actual = None
if "prompt_video_procesado" not in st.session_state: st.session_state.prompt_video_procesado = None
if "wa_copy" not in st.session_state: st.session_state.wa_copy = ""
if "wa_link" not in st.session_state: st.session_state.wa_link = ""
if "wa_script" not in st.session_state: st.session_state.wa_script = ""
if "wa_generado" not in st.session_state: st.session_state.wa_generado = False

# ==========================================
# 4. ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs([
    "📝 Textos y Guiones", 
    "💬 Campañas WhatsApp", 
    "🎬 Generador B-Roll (Veo 3)", 
    "🚀 SEO Programático"
])

# --- PESTAÑA 1: TEXTOS ---
with tab_texto:
    st.subheader("Creador de Contenido Escrito (Ventas & SEO)")
    tipo_formato = st.selectbox("Formato:", ["Reel/TikTok", "Artículo de Blog"], key="sb_formato")
    tema_input = st.text_input("¿De qué quieres que trate el contenido?", key="ti_tema")

    if st.button("Generar Contenido con IA", type="primary"):
        if tema_input:
            with st.spinner("Escribiendo... 🧠"):
                try:
                    if tipo_formato == "Reel/TikTok":
                        st.session_state.contenido_actual = redactar_guion_viral(tema=tema_input, tipo_publico="B2B/B2C")
                        st.session_state.tabla_destino = "guiones"
                    else:
                        st.session_state.contenido_actual = redactar_articulo_seo(tema=tema_input)
                        st.session_state.tabla_destino = "blog_posts"
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.contenido_actual:
        st.markdown(st.session_state.contenido_actual)
        if st.button("✅ Aprobar y Guardar"):
            if supabase:
                supabase.table(st.session_state.tabla_destino).insert({"tema": tema_input, "contenido": st.session_state.contenido_actual}).execute()
                st.success("Guardado en Supabase!")
                st.session_state.contenido_actual = None
                st.rerun()

# --- PESTAÑA 2: WHATSAPP ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    obj_wa = st.text_input("Objetivo de comunicación:")
    tel_wa = st.text_input("Número (formato internacional):", value="573000000000")
    
    if st.button("Generar Kit de WhatsApp"):
        campana = generar_campana_whatsapp(obj_wa, tel_wa)
        if campana:
            st.session_state.wa_copy = campana.mensaje_texto
            st.session_state.wa_link = campana.link_wa
            st.session_state.wa_script = campana.guion_nota_voz
            st.session_state.wa_generado = True

    if st.session_state.wa_generado:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.wa_copy = st.text_area("Copy:", value=st.session_state.wa_copy)
            st.session_state.wa_link = st.text_input("Link:", value=st.session_state.wa_link)
        with c2:
            st.session_state.wa_script = st.text_area("Guion:", value=st.session_state.wa_script)
            if st.button("🎧 Generar Nota de Voz"):
                audio_bytes = generar_audio_elevenlabs(st.session_state.wa_script)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("📥 Descargar", audio_bytes, "nota_voz.mp3", "audio/mp3")

# --- PESTAÑA 3: VIDEO (VEO 3) ---
with tab_video:
    st.subheader("Agente Productor: B-Roll")
    especie = st.text_input("Protagonista:")
    if st.button("Renderizar B-Roll"):
        with st.spinner("Renderizando..."):
            op = client_ai.models.generate_videos(model="veo-3.1-generate-preview", prompt=f"Formato vertical 9:16, {especie}")
            st.session_state.video_url_actual = op.generated_videos[0].video.uri if hasattr(op, 'generated_videos') else op.output
            st.video(st.session_state.video_url_actual)

# --- PESTAÑA 4: SEO PROGRAMÁTICO ---
with tab_seo:
    st.subheader("Trigger SEO")
    if st.button("Ejecutar Trigger"):
        articulo = generar_seo_desde_inventario({"especie": "Orquídeas", "cantidad": 500, "ubicacion": "Cajicá", "vendedor": "Vivero El Edén"})
        st.markdown(articulo.contenido_md)

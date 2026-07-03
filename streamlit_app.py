import streamlit as st
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# Inicialización segura
url_supabase = os.getenv("SUPABASE_URL")
clave_supabase = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, clave_supabase) if url_supabase else None

# ==========================================
# 4. ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs([
    "📝 Textos y Guiones", 
    "💬 Campañas WhatsApp", 
    "🎬 Generador B-Roll (Veo 3)", 
    "🚀 SEO Programático"
])

# --- PESTAÑA 2: WHATSAPP (Con validación) ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    obj_wa = st.text_input("Objetivo:")
    
    if st.button("Generar Kit de WhatsApp"):
        with st.spinner("Conectando con Agente de Crecimiento..."):
            campana = generar_campana_whatsapp(obj_wa)
            if campana:
                st.session_state.wa_copy = campana.mensaje_texto
                st.session_state.wa_script = campana.guion_nota_voz
                st.session_state.wa_generado = True
            else:
                st.error("El agente de crecimiento no pudo responder. Intenta de nuevo.")

    if st.session_state.get("wa_generado"):
        # ... (Tu código de visualización aquí) ...
        if st.button("🎧 Generar Nota de Voz"):
            audio = generar_audio_elevenlabs(st.session_state.wa_script)
            if audio:
                st.audio(audio, format="audio/mp3")
            else:
                st.warning("No se pudo generar el audio.")

# --- PESTAÑA 4: SEO PROGRAMÁTICO (Fase 3 - Con validación) ---
with tab_seo:
    st.subheader("Trigger SEO")
    if st.button("Ejecutar Trigger SEO"):
        with st.spinner("Analizando inventario y redactando..."):
            datos = {"especie": "Orquídeas", "cantidad": 500, "ubicacion": "Cajicá", "vendedor": "Vivero El Edén"}
            
            # BLOQUE PROTEGIDO: Aquí está el ajuste clave
            try:
                articulo = generar_seo_desde_inventario(datos)
                if articulo:
                    st.success("Artículo generado con éxito.")
                    st.markdown(f"### {articulo.titulo_h1}")
                    st.markdown(articulo.contenido_md)
                else:
                    st.error("El agente SEO no devolvió datos. La API podría estar saturada.")
            except Exception as e:
                st.error(f"Error inesperado en el motor SEO: {e}")

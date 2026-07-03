import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# Inicialización segura de Supabase
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

# --- PESTAÑA WHATSAPP ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    obj_wa = st.text_input("Objetivo de la campaña:")
    
    if st.button("Generar Kit de WhatsApp"):
        with st.spinner("Conectando con Agente de Crecimiento..."):
            campana = generar_campana_whatsapp(obj_wa)
            if campana:
                st.session_state.wa_copy = campana.mensaje_texto
                st.session_state.wa_script = campana.guion_nota_voz
                st.success("Kit generado con éxito.")
                st.text_area("Copy WhatsApp:", value=campana.mensaje_texto)
                st.text_area("Guion nota de voz:", value=campana.guion_nota_voz)
                st.session_state.wa_generado = True
            else:
                st.error("El agente de crecimiento no pudo responder.")

    if st.session_state.get("wa_generado"):
        if st.button("🎧 Generar Nota de Voz"):
            with st.spinner("Generando audio..."):
                audio = generar_audio_elevenlabs(st.session_state.wa_script)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.warning("No se pudo generar el audio.")

# --- PESTAÑA SEO PROGRAMÁTICO (Fase 3 - Relacional Dinámica) ---
with tab_seo:
    st.subheader("Trigger SEO: Inventario Relacional")
    
    if st.button("Ejecutar Trigger SEO con Inventario Real"):
        if not supabase:
            st.error("Error: Configuración de Supabase no encontrada.")
        else:
            with st.spinner("Consultando inventario relacionado en Supabase..."):
                try:
                    # Consulta relacional usando las FK de tu base de datos
                    # Asegúrate de ajustar los nombres de las columnas si difieren
                    response = supabase.table("inventario") \
                        .select("stock, viveros(vendedor_nombre, ubicacion), plantas(especie_nombre)") \
                        .order("inventario_id", desc=True) \
                        .limit(1) \
                        .execute()
                    
                    if not response.data:
                        st.warning("No se encontraron registros en la tabla 'inventario'.")
                    else:
                        item = response.data[0]
                        
                        # Mapeo a los datos que espera tu agente
                        datos_preparados = {
                            "especie": item["plantas"]["especie_nombre"],
                            "cantidad": item["stock"],
                            "ubicacion": item["viveros"]["ubicacion"],
                            "vendedor": item["viveros"]["vendedor_nombre"]
                        }
                        
                        st.info(f"Generando para: {datos_preparados['especie']} en {datos_preparados['ubicacion']}")
                        
                        # Llamada al Agente SEO
                        articulo = generar_seo_desde_inventario(datos_preparados)
                        
                        if articulo:
                            st.success("Artículo generado con éxito.")
                            st.markdown(f"### {articulo.titulo_h1}")
                            st.markdown(articulo.contenido_md)
                        else:
                            st.error("El agente SEO no devolvió datos.")
                            
                except Exception as e:
                    st.error(f"Error técnico en la consulta relacional: {e}")

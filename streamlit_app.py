import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# Inicialización segura usando Secrets
url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
key_ext = st.secrets.get("SUPABASE_KEY_EXTERNA")
supabase = create_client(url_ext, key_ext) if url_ext and key_ext else None

tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs(["📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO"])

# --- PESTAÑA SEO ---
with tab_seo:
    st.subheader("Trigger SEO: Inventario Real")
    
    if st.button("Ejecutar Trigger SEO con Inventario Real"):
        if not supabase:
            st.error("Error: Configuración de Supabase no encontrada en Secrets.")
        else:
            with st.spinner("Consultando inventario..."):
                try:
                    # 1. Obtenemos el registro más reciente del inventario
                    res = supabase.table("inventario") \
                        .select("*") \
                        .order("inventario_id", desc=True) \
                        .limit(1) \
                        .execute()
                    
                    if not res.data:
                        st.warning("No hay registros en la tabla inventario.")
                    else:
                        item = res.data[0]
                        
                        # 2. Consultamos los detalles relacionados usando los IDs
                        # Si tus tablas se llaman distinto, cambia 'plantas' o 'viveros'
                        planta = supabase.table("plantas").select("especie_nombre").eq("id", item["planta_id"]).execute()
                        vivero = supabase.table("viveros").select("vendedor_nombre, ubicacion").eq("id", item["vivero_id"]).execute()
                        
                        especie = planta.data[0]["especie_nombre"] if planta.data else "Planta Especial"
                        vendedor = vivero.data[0]["vendedor_nombre"] if vivero.data else "ViveroAliado"
                        ubicacion = vivero.data[0]["ubicacion"] if vivero.data else "Sabana de Bogotá"
                        
                        datos_preparados = {
                            "especie": especie,
                            "cantidad": item["stock"],
                            "ubicacion": ubicacion,
                            "vendedor": vendedor
                        }
                        
                        # 3. Generación con IA
                        articulo = generar_seo_desde_inventario(datos_preparados)
                        
                        if articulo:
                            st.success("Generado con éxito.")
                            st.markdown(f"### {articulo.titulo_h1}")
                            st.markdown(articulo.contenido_md)
                        else:
                            st.error("Error al generar con IA.")
                            
                except Exception as e:
                    st.error(f"Error técnico: {e}")

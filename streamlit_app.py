import streamlit as st
import os
from supabase import create_client, Client
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# Conexión a la BD externa (la del otro usuario)
url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
key_ext = st.secrets.get("SUPABASE_KEY_EXTERNA")
supabase = create_client(url_ext, key_ext) if url_ext and key_ext else None

tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs(["📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO"])

with tab_seo:
    st.subheader("Trigger SEO: Inventario Real")
    if st.button("Ejecutar Trigger SEO con Inventario Real"):
        if not supabase:
            st.error("Error: Configuración de Supabase no encontrada en Secrets.")
        else:
            with st.spinner("Consultando Supabase..."):
                try:
                    # Consulta relacional ajustada a tu esquema
                    res = supabase.table("inventario") \
                        .select("stock, viveros(vendedor_nombre, ubicacion), plantas(especie_nombre)") \
                        .order("inventario_id", desc=True) \
                        .limit(1) \
                        .execute()
                    
                    if not res.data:
                        st.warning("No hay registros en la tabla.")
                    else:
                        item = res.data[0]
                        datos = {
                            "especie": item["plantas"]["especie_nombre"],
                            "cantidad": item["stock"],
                            "ubicacion": item["viveros"]["ubicacion"],
                            "vendedor": item["viveros"]["vendedor_nombre"]
                        }
                        
                        articulo = generar_seo_desde_inventario(datos)
                        if articulo:
                            st.success("Generado con éxito.")
                            st.markdown(f"### {articulo.titulo_h1}")
                            st.markdown(articulo.contenido_md)
                        else:
                            st.error("Error al generar con IA.")
                except Exception as e:
                    st.error(f"Error técnico: {e}")

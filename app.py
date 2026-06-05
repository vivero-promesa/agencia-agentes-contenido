import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo

# 1. Configuración y conexión
load_dotenv()
url_supabase = os.getenv("SUPABASE_URL")
clave_supabase = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, clave_supabase)

st.set_page_config(page_title="Agencia ViveroOnline", layout="wide")
st.title("🌱 Centro de Comando - ViveroOnline")

# 2. Inicializar memoria
if "contenido_actual" not in st.session_state:
    st.session_state.contenido_actual = None
    st.session_state.tabla_destino = None

# 3. Interfaz de selección
tipo_formato = st.selectbox("Selecciona el formato de contenido:", ["Reel/TikTok", "Artículo de Blog"])
tema_input = st.text_input("¿De qué quieres que trate el contenido?")

if st.button("Generar Contenido con IA", type="primary"):
    if tema_input:
        with st.spinner("Conectando con la IA... 🧠"):
            if tipo_formato == "Reel/TikTok":
                st.session_state.contenido_actual = redactar_guion_viral(tema=tema_input, tipo_publico="B2C")
                st.session_state.tabla_destino = "guiones"
            else:
                st.session_state.contenido_actual = redactar_articulo_seo(tema=tema_input)
                st.session_state.tabla_destino = "blog_posts"
    else:
        st.warning("Por favor, ingresa un tema.")

# 4. Zona de revisión y guardado inteligente
if st.session_state.contenido_actual:
    st.success(f"¡{tipo_formato} generado con éxito!")
    st.markdown(st.session_state.contenido_actual)
    
    st.markdown("### ¿Qué deseas hacer?")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("✅ Aprobar y Guardar"):
            try:
                # Se guarda en la tabla que elegimos arriba (guiones o blog_posts)
                datos = {"tema": tema_input, "contenido": st.session_state.contenido_actual}
                supabase.table(st.session_state.tabla_destino).insert(datos).execute()
                
                st.success(f"¡Guardado exitosamente en {st.session_state.tabla_destino}!")
                st.session_state.contenido_actual = None
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                
    with col_b:
        if st.button("❌ Rechazar"):
            st.session_state.contenido_actual = None
            st.rerun()

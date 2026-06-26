import streamlit as st
import agente_blog # Asumiendo que así importas tu lógica actual
import agente_video # Importamos el nuevo agente

st.set_page_config(page_title="Centro de Comando - ViveroOnline", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# Crear las pestañas
tab_texto, tab_video = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video (Veo 3)"])

# --- PESTAÑA 1: TEXTOS (Tu código actual) ---
with tab_texto:
    st.write("Selecciona el formato de contenido:")
    formato = st.selectbox(
        "Formato",
        ["Reel/TikTok", "Artículo de Blog"],
        label_visibility="collapsed"
    )
    
    if st.button("Generar Contenido con IA", key="btn_texto"):
        st.success(f"Generando {formato}...")
        # Aquí llamas a tu función actual, ej: agente_blog.generar(...)

# --- PESTAÑA 2: VIDEOS ---
with tab_video:
    st.subheader("Clips Promocionales")
    st.write("Crea videos cortos de alta calidad para redes sociales o WhatsApp.")
    
    col1, col2 = st.columns(2)
    with col1:
        especie = st.text_input("Planta/Especie objetivo (Ej. Orquídeas Phalaenopsis)")
    with col2:
        estilo = st.selectbox("Estilo visual", ["Cinematográfico", "Primer Plano (Macro)", "Toma aérea"])
        
    contexto = st.text_area("Detalles del entorno (Ej. Luz de atardecer, follaje verde intenso):")

    if st.button("Generar Video con Veo 3", type="primary"):
        if especie:
            with st.spinner("Generando video con Veo 3... (Esto puede tomar unos minutos)"):
                # Llamamos al nuevo agente
                resultado = agente_video.generar_video_promocional(especie, estilo, contexto)
                
                if "Error" not in resultado:
                    st.success("¡Video generado con éxito!")
                    # st.video(resultado) # Descomentar cuando la API devuelva el archivo real
                else:
                    st.error(resultado)
        else:
            st.warning("Por favor, ingresa al menos la especie o planta objetivo.")

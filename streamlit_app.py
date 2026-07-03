import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN DEL CENTRO DE COMANDO
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# INICIALIZACIÓN SEGURA DE ADMINISTRADOR (Bypasses RLS)
url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
# ¡Clave! Usamos la llave de servicio, no la anónima
key_service = st.secrets.get("SUPABASE_SERVICE_KEY") 
supabase = create_client(url_ext, key_service) if url_ext and key_service else None

# ==========================================
# 4. ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs(["📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO"])

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

# --- PESTAÑA SEO PROGRAMÁTICO (Estructura Definitiva) ---
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")
    
    # 1. Selector de modo
    modo_seo = st.radio("Modo de operación:", ["📡 Diagnóstico/Automático", "✍️ Ingreso Manual"], horizontal=True)
    
    if modo_seo == "📡 Diagnóstico/Automático":
        # Botón para ejecutar el diagnóstico que te dará las llaves correctas
        if st.button("Analizar BD y Generar SEO"):
            with st.spinner("Analizando esquema y generando artículo..."):
                try:
                    # Obtenemos registro de inventario
                    item = supabase.table("inventario").select("*").limit(1).execute().data[0]
                    
                    # Obtenemos la estructura real de las tablas relacionadas
                    planta_data = supabase.table("plantas").select("*").eq("id", item["planta_id"]).execute().data[0]
                    vivero_data = supabase.table("viveros").select("*").eq("id", item["vivero_id"]).execute().data[0]
                    
                    # --- AQUÍ MOSTRAREMOS LOS NOMBRES REALES PARA QUE LOS VEAS ---
                    st.write("Columnas detectadas:", list(planta_data.keys()))
                    
                    # --- CONFIGURA ESTOS NOMBRES SEGÚN LO QUE SALGA ARRIBA ---
                    # Una vez sepas los nombres, solo cambia los strings de abajo:
                    nombre_especie = planta_data.get("nombre", planta_data.get("especie_nombre", "Planta"))
                    nombre_vivero = vivero_data.get("nombre", vivero_data.get("vendedor_nombre", "Vivero"))
                    locacion = vivero_data.get("ubicacion", "Sabana de Bogotá")
                    
                    datos_auto = {
                        "especie": nombre_especie,
                        "cantidad": item["stock"],
                        "ubicacion": locacion,
                        "vendedor": nombre_vivero
                    }
                    
                    articulo = generar_seo_desde_inventario(datos_auto)
                    if articulo:
                        st.success("¡Artículo generado con éxito!")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
                
                except Exception as e:
                    st.error(f"Error en la consulta automática: {e}")
                    st.info("💡 Tip: Revisa los nombres de las columnas que aparecieron arriba y actualiza los campos '.get()' en el código.")

    else:
        # MODO MANUAL: Respaldo total
        col1, col2 = st.columns(2)
        with col1:
            man_especie = st.text_input("Especie:", placeholder="Ej: Eugenia")
            man_vendedor = st.text_input("Vendedor:", placeholder="Ej: Vivero El Edén")
        with col2:
            man_cantidad = st.number_input("Cantidad:", min_value=1, value=100)
            man_ubicacion = st.text_input("Ubicación:", placeholder="Ej: Cajicá")
            
        if st.button("Generar Artículo Manual"):
            datos_manuales = {"especie": man_especie, "cantidad": man_cantidad, "ubicacion": man_ubicacion, "vendedor": man_vendedor}
            articulo = generar_seo_desde_inventario(datos_manuales)
            if articulo:
                st.markdown(f"### {articulo.titulo_h1}")
                st.markdown(articulo.contenido_md)

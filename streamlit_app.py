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

# --- PESTAÑA SEO PROGRAMÁTICO (REESTRUCTURADA) ---
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")
    
    # Selector de modo operativo
    modo_seo = st.radio("Modo de ingesta de datos:", ["📡 Conexión a Base de Datos (Automático)", "✍️ Ingreso Manual (Respaldo)"], horizontal=True)
    
    st.markdown("---")
    
    if modo_seo == "📡 Conexión a Base de Datos (Automático)":
        if st.button("Ejecutar Trigger Automático"):
            if not supabase:
                st.error("Falta configurar SUPABASE_SERVICE_KEY en los Secrets.")
            else:
                with st.spinner("Consultando inventario de forma segura..."):
                    try:
                        # La Service Key ignora el RLS, permitiendo la lectura
                        res = supabase.table("inventario").select("*").order("inventario_id", desc=True).limit(1).execute()
                        
                        if not res.data:
                            st.warning("El inventario está vacío.")
                        else:
                            item = res.data[0]
                            
                            # Consultas relacionadas
                            planta = supabase.table("plantas").select("especie_nombre").eq("id", item["planta_id"]).execute()
                            vivero = supabase.table("viveros").select("vendedor_nombre, ubicacion").eq("id", item["vivero_id"]).execute()
                            
                            datos_preparados = {
                                "especie": planta.data[0]["especie_nombre"] if planta.data else f"Planta ID {item['planta_id']}",
                                "cantidad": item["stock"],
                                "ubicacion": vivero.data[0]["ubicacion"] if vivero.data else "Sabana de Bogotá",
                                "vendedor": vivero.data[0]["vendedor_nombre"] if vivero.data else "Aliado Estratégico"
                            }
                            
                            articulo = generar_seo_desde_inventario(datos_preparados)
                            
                            if articulo:
                                st.success(f"Artículo B2B generado para: {datos_preparados['especie']}")
                                st.markdown(f"### {articulo.titulo_h1}")
                                st.markdown(articulo.contenido_md)
                            else:
                                st.error("Fallo en la comunicación con el Agente SEO.")
                    except Exception as e:
                        st.error(f"Error de ejecución: {e}")

    else:
        # MODO MANUAL: Por si la BD falla o necesitas crear un artículo para un vivero que aún no está en el sistema
        col1, col2 = st.columns(2)
        with col1:
            man_especie = st.text_input("Especie de Planta:", placeholder="Ej: Eugenia")
            man_vendedor = st.text_input("Vendedor / Vivero:", placeholder="Ej: Vivero El Edén")
        with col2:
            man_cantidad = st.number_input("Cantidad Disponible (Stock):", min_value=1, value=100)
            man_ubicacion = st.text_input("Ubicación:", placeholder="Ej: Cajicá")
            
        if st.button("Ejecutar Trigger Manual"):
            if man_especie and man_vendedor and man_ubicacion:
                with st.spinner("Redactando artículo estratégico..."):
                    datos_manuales = {
                        "especie": man_especie,
                        "cantidad": man_cantidad,
                        "ubicacion": man_ubicacion,
                        "vendedor": man_vendedor
                    }
                    articulo = generar_seo_desde_inventario(datos_manuales)
                    
                    if articulo:
                        st.success("Artículo manual generado exitosamente.")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
                    else:
                        st.error("Error al generar el contenido.")
            else:
                st.warning("Por favor, completa todos los campos para el modo manual.")

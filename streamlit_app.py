import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs
from agente_video import ejecutar_pipeline_agencia
from competencia import analizar_contra_competencia, get_config_competencia

# ==========================================
# 0. CONFIGURACIÓN DEL CENTRO DE COMANDO
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
key_service = st.secrets.get("SUPABASE_SERVICE_KEY") 
supabase = create_client(url_ext, key_service) if url_ext and key_service else None

# ==========================================
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360, tab_historial, tab_competencia = st.tabs([
    "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "🔥 Campaña 360", "📜 Historial", "🧠 Competencia"
])

# --- PESTAÑA 5: ORQUESTADOR 360 (BLINDADO) ---
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        if not supabase: st.error("Error de conexión Supabase.")
        else:
            with st.spinner("Sincronizando agentes y ejecutando campaña..."):
                try:
                    # 1. Lógica de Lotes Frescos
                    res_inv = supabase.table("inventario").select("*").eq("estado_planta", "disponible").gte("stock", 20).order("inventario_id", desc=True).limit(10).execute()
                    res_campanas = supabase.table("campanas_ejecutadas").select("inventario_id").execute()
                    lotes_procesados = [c["inventario_id"] for c in res_campanas.data] if res_campanas.data else []
                    item = next((l for l in res_inv.data if l["inventario_id"] not in lotes_procesados), None)

                    if not item: st.info("Todos los lotes actuales ya tienen campaña.")
                    else:
                        # Extraer datos y escanear nombres
                        planta_data = supabase.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data[0]
                        vivero_data = supabase.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data[0]
                        
                        cols_nombre_p = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                        nombre_especie = planta_data[cols_nombre_p[0]] if cols_nombre_p else "Planta"
                        
                        locacion = vivero_data.get("ubicacion") or "Sabana de Bogotá"
                        datos = {"especie": nombre_especie, "cantidad": item["stock"], "ubicacion": locacion, "vendedor": "Vivero Partner"}

                        # 2. Ejecutar Agentes
                        seo_res = generar_seo_desde_inventario(datos)
                        wa_res = generar_campana_whatsapp(f"Vender {item['stock']} {nombre_especie} en {locacion}.")
                        video_res = redactar_guion_viral(f"Logística de {nombre_especie} en {locacion}.")
                        
                        # 3. Guardado Histórico y Candado
                        supabase.table("historial_contenidos").insert([
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md},
                            {"tipo_contenido": "WHATSAPP", "titulo": "Copy WhatsApp", "contenido": wa_res.mensaje_texto},
                            {"tipo_contenido": "VIDEO", "titulo": "Guion Video", "contenido": video_res}
                        ]).execute()
                        
                        supabase.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()
                        
                        st.session_state.c360_data = {"lote": datos, "seo": seo_res, "wa": wa_res, "video": video_res}
                        st.session_state.c360_lista = True
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    if st.session_state.get("c360_lista"):
        data = st.session_state.c360_data
        st.success("Campaña generada.")
        col1, col2 = st.columns(2)
        with col1:
            st.expander("🚀 SEO").markdown(data["seo"].contenido_md)
            st.expander("🎬 Video").write(data["video"])
        with col2:
            st.expander("💬 WhatsApp").write(data["wa"].mensaje_texto)

# --- PESTAÑA 6: HISTORIAL (Memoria del Negocio Blindada) ---
with tab_historial:
    st.subheader("📜 Historial de Contenido")
    
    try:
        # Intentamos obtener los datos
        res = supabase.table("historial_contenidos").select("*").order("fecha_creacion", desc=True).execute()
        datos = res.data if res.data else []
    except Exception as e:
        st.warning("⚠️ El historial está temporalmente inaccesible. Revisa las políticas RLS en Supabase.")
        datos = []

    if datos:
        # Filtros y lógica de visualización como la tenías...
        col1, col2 = st.columns(2)
        # ... (resto de tu código de filtros y expanders)
    else:
        st.info("No se encontraron registros. ¡Lanza una Campaña 360 para generar el primer contenido!")

# --- PESTAÑA 7: COMPETENCIA ---
with tab_competencia:
    st.subheader("🧠 Cerebro Competitivo")
    st.write(get_config_competencia())
    test_tema = st.text_input("Probar estrategia contra competidor:")
    if st.button("Generar Pitch"):
        st.write(analizar_contra_competencia(test_tema))

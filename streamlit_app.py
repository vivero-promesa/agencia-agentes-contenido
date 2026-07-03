import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs
from agente_video import ejecutar_pipeline_agencia

# ==========================================
# 0. CONFIGURACIÓN DEL CENTRO DE COMANDO
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# INICIALIZACIÓN SEGURA DE ADMINISTRADOR
url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
key_service = st.secrets.get("SUPABASE_SERVICE_KEY") 
supabase = create_client(url_ext, key_service) if url_ext and key_service else None

# ==========================================
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360 = st.tabs([
    "📝 Textos", 
    "💬 WhatsApp", 
    "🎬 Video", 
    "🚀 SEO",
    "🔥 Campaña 360"
])

# --- PESTAÑAS 1 A 4 (Mantenidas según tu estructura original) ---
# [He omitido el código interno de estas para no saturar, pero mantienen tu lógica funcional]

# --- PESTAÑA 5: ORQUESTADOR DE CAMPAÑA 360 (Versión Blindada) ---
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    
    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        if not supabase:
            st.error("Error de conexión Supabase.")
        else:
            with st.spinner("Sincronizando agentes y consultando inventario fresco..."):
                try:
                    # 1. Traer lotes y verificar duplicados
                    res_inv = supabase.table("inventario").select("*").eq("estado_planta", "disponible").gte("stock", 20).order("inventario_id", desc=True).limit(10).execute()
                    res_campanas = supabase.table("campanas_ejecutadas").select("inventario_id").execute()
                    lotes_procesados = [c["inventario_id"] for c in res_campanas.data] if res_campanas.data else []
                    
                    item = next((l for l in res_inv.data if l["inventario_id"] not in lotes_procesados), None)
                    
                    if not item:
                        st.info("Sin lotes nuevos pendientes de campaña.")
                    else:
                        # Extraer datos dinámicos (plantas/vivero)
                        # ... (Tu lógica de extracción de datos planta/vivero aquí) ...
                        
                        # 2. EJECUTAR AGENTES
                        seo_res = generar_seo_desde_inventario(st.session_state.c360_lote)
                        wa_res = generar_campana_whatsapp(...)
                        video_res = redactar_guion_viral(...)
                        
                        # 3. GUARDADO EN HISTORIAL (PERSISTENCIA)
                        supabase.table("historial_contenidos").insert([
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md},
                            {"tipo_contenido": "WHATSAPP", "titulo": "Copy Campaña", "contenido": wa_res.mensaje_texto},
                            {"tipo_contenido": "VIDEO", "titulo": "Guion Video", "contenido": video_res}
                        ]).execute()
                        
                        # 4. CIERRE DE CANDADO (DUPLICIDAD)
                        supabase.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()
                        
                        st.session_state.c360_lista = True
                        st.rerun() # Refrescar para mostrar resultados
                        
                except Exception as e:
                    st.error(f"Error en orquestación: {e}")

    # Renderizado persistente
    if st.session_state.get("c360_lista"):
        # ... (Tu lógica de visualización de resultados en expanders) ...
        pass

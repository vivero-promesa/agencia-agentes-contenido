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
# ARQUITECTURA DE PESTAÑAS (Ahora con Motor 360)
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360 = st.tabs([
    "📝 Textos", 
    "💬 WhatsApp", 
    "🎬 Video", 
    "🚀 SEO",
    "🔥 Campaña 360"
])

# --- PESTAÑA 1: TEXTOS ---
with tab_texto:
    st.subheader("Redacción de Artículos y Copy B2B")
    tema_texto = st.text_input("Tema o requerimiento del texto:", placeholder="Ej: Beneficios de especies nativas en proyectos de paisajismo")
    
    if st.button("Generar Texto B2B"):
        if tema_texto:
            with st.spinner("El agente está redactando..."):
                try:
                    resultado_texto = redactar_articulo_seo(tema_texto)
                    if resultado_texto:
                        st.success("Texto generado con éxito.")
                        st.write(resultado_texto)
                    else:
                        st.error("El agente no devolvió respuesta.")
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Por favor ingresa un tema.")

# --- PESTAÑA 2: WHATSAPP ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    obj_wa = st.text_input("Objetivo de la campaña:", placeholder="Ej: Vender 500 Eugenias a paisajistas")
    
    if st.button("Generar Kit de WhatsApp"):
        if obj_wa:
            with st.spinner("Conectando con Agente de Crecimiento..."):
                campana = generar_campana_whatsapp(obj_wa)
                if campana:
                    st.session_state.wa_copy = campana.mensaje_texto
                    st.session_state.wa_script = campana.guion_nota_voz
                    st.success("Kit generado con éxito.")
                    st.text_area("Copy WhatsApp:", value=campana.mensaje_texto, height=100)
                    st.text_area("Guion nota de voz:", value=campana.guion_nota_voz, height=150)
                    st.session_state.wa_generado = True
                else:
                    st.error("El agente de crecimiento no pudo responder.")
        else:
            st.warning("Por favor ingresa un objetivo.")

    if st.session_state.get("wa_generado"):
        st.markdown("---")
        if st.button("🎧 Generar Nota de Voz con ElevenLabs"):
            with st.spinner("Sintetizando audio..."):
                audio = generar_audio_elevenlabs(st.session_state.wa_script)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.warning("No se pudo generar el audio.")

# --- PESTAÑA 3: VIDEO (B-Roll y Producción Veo 3.1) ---
with tab_video:
    st.subheader("🎬 Producción de Video B2B (Veo 3.1)")
    st.markdown("Diseña el concepto estratégico y renderiza los clips directamente con la API de Google.")
    
    # PASO 1: IDEACIÓN (GROQ / LLAMA 3)
    with st.expander("📝 1. Pre-Producción (Generar Concepto y Guion)", expanded=True):
        tema_video = st.text_input("Concepto visual del comercial:", placeholder="Ej: Lote mayorista de eugenias para constructoras")
        if st.button("Generar Concepto Visual"):
            if tema_video:
                with st.spinner("Estructurando tomas, guion y copy para redes..."):
                    try:
                        resultado_video = redactar_guion_viral(tema_video)
                        st.success("Concepto generado. Úsalo como inspiración para tu Storyboard.")
                        st.write(resultado_video)
                    except Exception as e:
                        st.error(f"Error técnico: {e}")
            else:
                st.warning("Ingresa un concepto primero.")

    # PASO 2: RENDERIZADO EN LA NUBE (GOOGLE VEO 3.1)
    with st.expander("🎥 2. Producción (Renderizar Escenas)", expanded=False):
        st.markdown("Pega el JSON de tu storyboard para enviar las instrucciones técnicas de renderizado a Google Veo.")
        
        # Plantilla JSON de ejemplo estructurada para el sector viverista
        plantilla_json = '''{
    "escena_1": {
        "nombre": "Intro Logística",
        "tipo": "IA_GENERATIVE",
        "visual": "Camión de carga recibiendo estibas llenas de plantas sanas",
        "emocion": "Eficiencia y escala industrial",
        "camara": "Plano general, movimiento de dron lento hacia adelante",
        "texto": "Capacidad logística en toda la Sabana"
    },
    "escena_2": {
        "nombre": "Detalle de Calidad",
        "tipo": "IA_GENERATIVE",
        "visual": "Manos con guantes inspeccionando raíces blancas y sustrato premium",
        "emocion": "Confianza y calidad técnica",
        "camara": "Plano detalle (Macro), enfoque nítido",
        "texto": "Cero mortalidad en obra"
    }
}'''
        storyboard_input = st.text_area("Storyboard (Formato JSON):", value=plantilla_json, height=250)
        
        if st.button("🚀 Iniciar Renderizado", type="primary"):
            with st.spinner("Conectando con Google Veo 3.1 y renderizando clips... (Esto toma tiempo)"):
                try:
                    resultados_render = ejecutar_pipeline_agencia(storyboard_input)
                    if resultados_render:
                        st.success("¡Pipeline de producción finalizado!")
                        
                        # Renderizamos los videos devueltos en la interfaz
                        for key, data in resultados_render.items():
                            st.markdown(f"### {key.replace('_', ' ').title()}")
                            
                            if data["status"] == "Listo" and data.get("url"):
                                st.video(data["url"])
                                st.caption(f"**Texto sugerido para edición:** {data.get('texto', '')}")
                            else:
                                st.warning(f"**Estado:** {data['status']} - {data.get('texto', '')}")
                    else:
                        st.error("No se pudieron generar los videos. Revisa los logs o tu cuota de API.")
                except Exception as e:
                    st.error(f"Error crítico en el orquestador: {e}")

# --- PESTAÑA 4: SEO PROGRAMÁTICO (Motor Dinámico) ---
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")
    
    modo_seo = st.radio("Modo de operación:", ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual"], horizontal=True)
    
    if modo_seo == "📡 Automatizado (Base de Datos)":
        if st.button("Analizar BD y Generar SEO"):
            if not supabase:
                st.error("Falta configurar la conexión a Supabase en los Secrets.")
            else:
                with st.spinner("Decodificando esquema de base de datos y generando contenido..."):
                    try:
                        # 1. Obtener el último registro del inventario (Blindaje B2B)
                        res_inv = supabase.table("inventario") \
                            .select("*") \
                            .eq("estado_planta", "disponible") \
                            .gte("stock", 20) \
                            .order("inventario_id", desc=True) \
                            .limit(1) \
                            .execute()
                        
                        if not res_inv.data:
                            st.warning("No hay inventario 'disponible' con más de 20 unidades en este momento.")
                        else:
                            item = res_inv.data[0]
                            
                            muestra_planta = supabase.table("plantas").select("*").limit(1).execute().data[0]
                            muestra_vivero = supabase.table("viveros").select("*").limit(1).execute().data[0]
                            
                            col_id_planta = [c for c in muestra_planta.keys() if "id" in c.lower()][0]
                            col_id_vivero = [c for c in muestra_vivero.keys() if "id" in c.lower()][0]
                            
                            planta_data = supabase.table("plantas").select("*").eq(col_id_planta, item["planta_id"]).execute().data[0]
                            vivero_data = supabase.table("viveros").select("*").eq(col_id_vivero, item["vivero_id"]).execute().data[0]
                            
                            # ESCÁNER DINÁMICO DE NOMBRES PARA PLANTA
                            cols_nombre_planta = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                            nombre_especie = planta_data[cols_nombre_planta[0]] if cols_nombre_planta else f"Planta_ID_{item['planta_id']}"
                            
                            # ESCÁNER DINÁMICO DE NOMBRES PARA VIVERO
                            cols_nombre_vivero = [k for k in vivero_data.keys() if "nombre" in k.lower() or "vendedor" in k.lower()]
                            nombre_vivero = vivero_data[cols_nombre_vivero[0]] if cols_nombre_vivero else f"Vivero_ID_{item['vivero_id']}"
                            
                            locacion = (
                                vivero_data.get("ubicacion") or 
                                vivero_data.get("ciudad") or 
                                vivero_data.get("municipio") or 
                                "Sabana de Bogotá"
                            )
                            
                            st.write(f"📊 **Datos extraídos:** {nombre_especie} | Stock: {item['stock']} | Ubicación: {locacion} ({nombre_vivero})")
                            
                            datos_auto = {
                                "especie": nombre_especie,
                                "cantidad": item["stock"],
                                "ubicacion": locacion,
                                "vendedor": nombre_vivero
                            }
                            
                            articulo = generar_seo_desde_inventario(datos_auto)
                            if articulo:
                                st.success("¡Artículo estratégico B2B generado con éxito!")
                                st.markdown(f"### {articulo.titulo_h1}")
                                st.markdown(articulo.contenido_md)
                            else:
                                st.error("El motor de IA no devolvió un formato válido.")
                    except Exception as e:
                        st.error(f"Error en la consulta automática: {e}")

    else:
        col1, col2 = st.columns(2)
        with col1:
            man_especie = st.text_input("Especie de planta:", placeholder="Ej: Palma Areca")
            man_vendedor = st.text_input("Nombre del Vivero:", placeholder="Ej: Vivero El Edén")
        with col2:
            man_cantidad = st.number_input("Cantidad (Stock):", min_value=1, value=500)
            man_ubicacion = st.text_input("Ubicación del lote:", placeholder="Ej: Chía")
            
        if st.button("Generar Artículo Manual"):
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
                st.warning("Completa los campos requeridos para proceder.")

# --- PESTAÑA 5: ORQUESTADOR DE CAMPAÑA 360 (Corregida con Persistencia) ---
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    st.markdown("Genera una campaña B2B unificada (SEO, WhatsApp y Video) basada en el inventario real de alto volumen.")
    
    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        if not supabase:
            st.error("Falta configurar la conexión a Supabase en los Secrets.")
        else:
            with st.spinner("Sincronizando agentes y consultando inventario B2B..."):
               try:
                    # 1. Traer los últimos 10 lotes B2B disponibles (Stock alto)
                    res_inv = supabase.table("inventario") \
                        .select("*").eq("estado_planta", "disponible").gte("stock", 20) \
                        .order("inventario_id", desc=True).limit(10).execute()
                    
                    if not res_inv.data:
                        st.warning("No hay inventario disponible con más de 20 unidades.")
                    else:
                        # 2. Consultar qué lotes YA tuvieron campaña
                        res_campanas = supabase.table("campanas_ejecutadas").select("inventario_id").execute()
                        lotes_procesados = [c["inventario_id"] for c in res_campanas.data] if res_campanas.data else []
                        
                        # 3. Encontrar el primer lote "Fresco" (que no esté en la lista de procesados)
                        item = None
                        for lote in res_inv.data:
                            if lote["inventario_id"] not in lotes_procesados:
                                item = lote
                                break
                        
                        # 4. Candado de seguridad
                        if not item:
                            st.info("Tranquilo, todos los lotes de alto volumen actuales ya tienen campañas activas. Espera a que ingrese nuevo inventario.")
                        else:
                            # --- INICIA EXTRACCIÓN DE DATOS PARA EL LOTE FRESCO ---
                            muestra_planta = supabase.table("plantas").select("*").limit(1).execute().data[0]
                            muestra_vivero = supabase.table("viveros").select("*").limit(1).execute().data[0]
                            
                            col_id_planta = [c for c in muestra_planta.keys() if "id" in c.lower()][0]
                            col_id_vivero = [c for c in muestra_vivero.keys() if "id" in c.lower()][0]
                            
                            planta_data = supabase.table("plantas").select("*").eq(col_id_planta, item["planta_id"]).execute().data[0]
                            vivero_data = supabase.table("viveros").select("*").eq(col_id_vivero, item["vivero_id"]).execute().data[0]
                            
                            # ESCÁNER DINÁMICO DE NOMBRES PARA PLANTA
                            cols_nombre_planta = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                            nombre_especie = planta_data[cols_nombre_planta[0]] if cols_nombre_planta else f"Planta_ID_{item['planta_id']}"
                            
                            # ESCÁNER DINÁMICO DE NOMBRES PARA VIVERO
                            cols_nombre_vivero = [k for k in vivero_data.keys() if "nombre" in k.lower() or "vendedor" in k.lower()]
                            nombre_vivero = vivero_data[cols_nombre_vivero[0]] if cols_nombre_vivero else f"Vivero_ID_{item['vivero_id']}"
                            
                            locacion = vivero_data.get("ubicacion") or "Sabana de Bogotá"
                            
                            st.session_state.c360_lote = {
                                "especie": nombre_especie, "cantidad": item["stock"], 
                                "ubicacion": locacion, "vendedor": nombre_vivero
                            }
                            
                            # 5. EJECUTAR AGENTES CON EL LOTE FRESCO
                            st.session_state.c360_seo = generar_seo_desde_inventario(st.session_state.c360_lote)
                            st.session_state.c360_wa = generar_campana_whatsapp(f"Vender lote urgente de {item['stock']} {nombre_especie} en {locacion}.")
                            st.session_state.c360_video = redactar_guion_viral(f"Carga logística y revisión de calidad de {item['stock']} {nombre_especie} en {locacion}.")
                            
                            # 6. REGISTRAR ÉXITO EN LA BASE DE DATOS (Cierra el candado)
                            supabase.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()
                            
                            st.session_state.c360_lista = True
                        
                except Exception as e:
                    st.error(f"Error en la orquestación: {e}")
    # Renderizado fuera del botón principal usando persistencia
    if st.session_state.get("c360_lista"):
        lote = st.session_state.c360_lote
        st.info(f"🎯 **Campaña Activa:** {lote['cantidad']} {lote['especie']} | {lote['ubicacion']} ({lote['vendedor']})")
        
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🚀 1. Artículo SEO B2B", expanded=True):
                if st.session_state.c360_seo:
                    st.markdown(f"### {st.session_state.c360_seo.titulo_h1}")
                    st.markdown(st.session_state.c360_seo.contenido_md)
            
            with st.expander("🎬 3. Guion Visual (Veo 3)", expanded=True):
                if st.session_state.c360_video:
                    st.write(st.session_state.c360_video)

        with col2:
            with st.expander("💬 2. Estrategia WhatsApp", expanded=True):
                wa = st.session_state.c360_wa
                if wa:
                    st.text_area("Copy Rápido:", value=wa.mensaje_texto, height=100)
                    st.text_area("Guion de Audio:", value=wa.guion_nota_voz, height=150)
                    st.markdown(f"[🔗 Enlace Directo WhatsApp]({wa.link_wa})")
                    
                    # Este botón ahora funciona perfectamente sin borrar la pantalla
                    if st.button("🎧 Sintetizar Audio Campaña"):
                        with st.spinner("Sintetizando..."):
                            audio_campana = generar_audio_elevenlabs(wa.guion_nota_voz)
                            if audio_campana:
                                st.audio(audio_campana, format="audio/mp3")
                            else:
                                st.warning("Fallo en la API de ElevenLabs.")

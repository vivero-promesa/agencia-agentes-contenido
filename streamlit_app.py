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

# ==========================================
# ARQUITECTURA DE DOBLE BASE DE DATOS
# ==========================================
# 1. MARKETPLACE (solo LECTURA): inventario, plantas, viveros
url_mkt = st.secrets.get("SUPABASE_URL_EXTERNA")
key_mkt = st.secrets.get("SUPABASE_SERVICE_KEY")
supabase_mkt = create_client(url_mkt, key_mkt) if url_mkt and key_mkt else None

# 2. AGENCIA (LECTURA/ESCRITURA): historial_contenidos, campanas_ejecutadas
url_ag = st.secrets.get("SUPABASE_URL_AGENCIA")
key_ag = st.secrets.get("SUPABASE_KEY_AGENCIA")
supabase_ag = create_client(url_ag, key_ag) if url_ag and key_ag else None

# ==========================================
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360, tab_historial, tab_competencia = st.tabs([
    "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "🔥 Campaña 360", "📜 Historial", "🧠 Competencia"
])

# ==========================================
# --- PESTAÑA 1: TEXTOS ---
# ==========================================
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

# ==========================================
# --- PESTAÑA 2: WHATSAPP ---
# ==========================================
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
                    st.session_state.wa_generado = True
                    st.success("Kit generado con éxito.")
                else:
                    st.error("El agente de crecimiento no pudo responder.")
        else:
            st.warning("Por favor ingresa un objetivo.")

    # Renderizado persistente (el botón de audio funciona sin borrar pantalla)
    if st.session_state.get("wa_generado"):
        st.text_area("Copy WhatsApp:", value=st.session_state.wa_copy, height=100)
        st.text_area("Guion nota de voz:", value=st.session_state.wa_script, height=150)
        st.markdown("---")
        if st.button("🎧 Generar Nota de Voz con ElevenLabs"):
            with st.spinner("Sintetizando audio..."):
                audio = generar_audio_elevenlabs(st.session_state.wa_script)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.warning("No se pudo generar el audio.")

# ==========================================
# --- PESTAÑA 3: VIDEO (B-Roll y Producción Veo 3.1) ---
# ==========================================
with tab_video:
    st.subheader("🎬 Producción de Video B2B (Veo 3.1)")
    st.markdown("Diseña el concepto estratégico y renderiza los clips directamente con la API de Google.")

    # PASO 1: IDEACIÓN
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

        plantilla_json = '''{
    "escena_1": {
        "nombre": "Inicio de Jornada",
        "tipo": "IA_GENERATIVE",
        "visual": "Viverista revisando sus plantas temprano en la mañana, hojas húmedas de riego",
        "emocion": "Cercana, tranquila, orgullo por el oficio",
        "camara": "Plano general, movimiento suave hacia adelante",
        "texto": "Cada planta, revisada a mano"
    },
    "escena_2": {
        "nombre": "Detalle de Calidad",
        "tipo": "IA_GENERATIVE",
        "visual": "Manos con tierra inspeccionando raíces blancas y sustrato",
        "emocion": "Confianza y conocimiento del oficio",
        "camara": "Plano detalle (macro), enfoque nítido",
        "texto": "Años de experiencia en cada raíz"
    }
}'''
        storyboard_input = st.text_area("Storyboard (Formato JSON):", value=plantilla_json, height=250)

        if st.button("🚀 Iniciar Renderizado", type="primary"):
            with st.spinner("Conectando con Google Veo 3.1 y renderizando clips... (Esto toma tiempo)"):
                try:
                    resultados_render = ejecutar_pipeline_agencia(storyboard_input)
                    if resultados_render:
                        st.success("¡Pipeline de producción finalizado!")
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

# ==========================================
# --- PESTAÑA 4: SEO PROGRAMÁTICO (lee del MARKETPLACE) ---
# ==========================================
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")

    modo_seo = st.radio("Modo de operación:", ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual"], horizontal=True)

    if modo_seo == "📡 Automatizado (Base de Datos)":
        if st.button("Analizar BD y Generar SEO"):
            if not supabase_mkt:
                st.error("Falta configurar la conexión al Marketplace en los Secrets (SUPABASE_URL_EXTERNA / SUPABASE_SERVICE_KEY).")
            else:
                with st.spinner("Decodificando esquema de base de datos y generando contenido..."):
                    try:
                        # 1. Último registro de inventario (Blindaje B2B)
                        res_inv = supabase_mkt.table("inventario") \
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

                            planta_data = supabase_mkt.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data[0]
                            vivero_data = supabase_mkt.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data[0]

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

# ==========================================
# --- PESTAÑA 5: ORQUESTADOR 360 ---
# LEE del Marketplace | ESCRIBE en la Agencia
# ==========================================
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    st.markdown("Lee el inventario del **Marketplace**, genera la campaña (SEO, WhatsApp y Video) y la guarda en la base de la **Agencia**.")

    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        if not supabase_mkt:
            st.error("Falta la conexión al Marketplace (SUPABASE_URL_EXTERNA / SUPABASE_SERVICE_KEY).")
        elif not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            with st.spinner("Sincronizando agentes y ejecutando campaña..."):
                try:
                    # 1. Lógica de Lotes Frescos
                    #    Inventario: se lee del MARKETPLACE
                    #    Candado de campañas: se lee de la AGENCIA
                    res_inv = supabase_mkt.table("inventario").select("*").eq("estado_planta", "disponible").gte("stock", 20).order("inventario_id", desc=True).limit(10).execute()
                    res_campanas = supabase_ag.table("campanas_ejecutadas").select("inventario_id").execute()
                    lotes_procesados = [c["inventario_id"] for c in res_campanas.data] if res_campanas.data else []
                    item = next((l for l in res_inv.data if l["inventario_id"] not in lotes_procesados), None)

                    if not item:
                        st.info("Todos los lotes actuales ya tienen campaña.")
                    else:
                        # Extraer datos dinámicos (MARKETPLACE)
                        planta_data = supabase_mkt.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data[0]
                        vivero_data = supabase_mkt.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data[0]

                        cols_nombre_p = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                        nombre_especie = planta_data[cols_nombre_p[0]] if cols_nombre_p else "Planta"

                        cols_nombre_v = [k for k in vivero_data.keys() if "nombre" in k.lower() or "vendedor" in k.lower()]
                        nombre_vivero = vivero_data[cols_nombre_v[0]] if cols_nombre_v else "Vivero Partner"

                        locacion = vivero_data.get("ubicacion") or "Sabana de Bogotá"
                        datos = {"especie": nombre_especie, "cantidad": item["stock"], "ubicacion": locacion, "vendedor": nombre_vivero}

                        # 2. Ejecutar Agentes
                        seo_res = generar_seo_desde_inventario(datos)
                        wa_res = generar_campana_whatsapp(f"Vender lote urgente de {item['stock']} {nombre_especie} en {locacion}.")
                        video_res = redactar_guion_viral(f"Carga logística y revisión de calidad de {nombre_especie} en {locacion}.")

                        # 3. Guardado Histórico (AGENCIA)
                        supabase_ag.table("historial_contenidos").insert([
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md},
                            {"tipo_contenido": "WHATSAPP", "titulo": "Copy WhatsApp", "contenido": wa_res.mensaje_texto},
                            {"tipo_contenido": "VIDEO", "titulo": "Guion Video", "contenido": video_res}
                        ]).execute()

                        # 4. Cierre de Candado Anti-Duplicidad (AGENCIA)
                        supabase_ag.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()

                        st.session_state.c360_data = {"lote": datos, "seo": seo_res, "wa": wa_res, "video": video_res}
                        st.session_state.c360_lista = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Error en la orquestación: {e}")

    # Renderizado persistente (sobrevive al rerun y a clics posteriores)
    if st.session_state.get("c360_lista"):
        data = st.session_state.c360_data
        lote = data["lote"]
        st.success("Campaña generada y guardada en el historial de la Agencia.")
        st.info(f"🎯 **Campaña Activa:** {lote['cantidad']} {lote['especie']} | {lote['ubicacion']} ({lote['vendedor']})")

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🚀 1. Artículo SEO B2B", expanded=True):
                if data["seo"]:
                    st.markdown(f"### {data['seo'].titulo_h1}")
                    st.markdown(data["seo"].contenido_md)

            with st.expander("🎬 3. Guion Visual (Veo 3)", expanded=True):
                if data["video"]:
                    st.write(data["video"])

        with col2:
            with st.expander("💬 2. Estrategia WhatsApp", expanded=True):
                wa = data["wa"]
                if wa:
                    st.text_area("Copy Rápido:", value=wa.mensaje_texto, height=100)
                    st.text_area("Guion de Audio:", value=wa.guion_nota_voz, height=150)
                    if getattr(wa, "link_wa", None):
                        st.markdown(f"[🔗 Enlace Directo WhatsApp]({wa.link_wa})")

                    if st.button("🎧 Sintetizar Audio Campaña"):
                        with st.spinner("Sintetizando..."):
                            audio_campana = generar_audio_elevenlabs(wa.guion_nota_voz)
                            if audio_campana:
                                st.audio(audio_campana, format="audio/mp3")
                            else:
                                st.warning("Fallo en la API de ElevenLabs.")

# ==========================================
# --- PESTAÑA 6: HISTORIAL (lee de la AGENCIA) ---
# ==========================================
with tab_historial:
    st.subheader("📜 Historial de Contenido Generado")
    if not supabase_ag:
        st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
    else:
        try:
            res = supabase_ag.table("historial_contenidos").select("*").order("fecha_creacion", desc=True).execute()
            if not res.data:
                st.info("Aún no hay contenido en el historial. Lanza una Campaña 360 para empezar.")
            else:
                for item in res.data:
                    with st.expander(f"{item.get('tipo_contenido', 'N/A')} | {item.get('titulo', 'Sin título')}"):
                        st.markdown(item.get('contenido', ''))
        except Exception as e:
            st.error(f"❌ Error técnico real: {e}")

# ==========================================
# --- PESTAÑA 7: COMPETENCIA ---
# ==========================================
with tab_competencia:
    st.subheader("🧠 Cerebro Competitivo")
    try:
        st.write(get_config_competencia())
    except Exception as e:
        st.warning(f"No se pudo cargar la configuración de competencia: {e}")

    test_comp = st.text_input("Probar contra:", placeholder="Ej: Vivero tradicional de la 80 con precios bajos")
    if st.button("Generar Pitch Competitivo"):
        if test_comp:
            with st.spinner("Analizando ventaja competitiva..."):
                try:
                    st.write(analizar_contra_competencia(test_comp))
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Ingresa un competidor o escenario para analizar.")

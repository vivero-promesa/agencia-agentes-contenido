import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo

# ==========================================
# 🚨 BLOQUE DE DIAGNÓSTICO (CAZADOR DE ERRORES)
# Streamlit Cloud redacta el mensaje real de ImportError por seguridad.
# Este bloque lo captura y lo muestra en pantalla para saber la causa
# exacta (nombre no encontrado, error de sintaxis interno, dependencia
# faltante, etc.) en vez de adivinar.
# ==========================================
try:
    from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario, generar_seo_por_intencion, generar_y_guardar_pauta
except Exception as e:
    st.error("🚨 Error real detectado al importar 'agentes_crecimiento.py':")
    st.exception(e)
    st.stop()
# ==========================================

from agente_audio import generar_audio_elevenlabs
from agente_video import ejecutar_pipeline_agencia
from agente_blog import redactar_articulo_blog
from competencia import analizar_contra_competencia, proponer_estrategia_desde_competencia
from estrategia import obtener_prioridad_estrategica, guardar_prioridad_estrategica, CLAVE_DOLORES_INTERMEDIARIOS, CLAVE_ESTRATEGIA_COMPETITIVA, cluster_ya_ejecutado, registrar_cluster_ejecutado

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

# Prioridad estratégica dinámica
if "prioridad_estrategica" not in st.session_state:
    st.session_state.prioridad_estrategica = obtener_prioridad_estrategica(supabase_ag)

# Dolores del viverista frente a intermediarios
if "dolores_intermediarios" not in st.session_state:
    st.session_state.dolores_intermediarios = obtener_prioridad_estrategica(supabase_ag, clave=CLAVE_DOLORES_INTERMEDIARIOS)

# ==========================================
# ARQUITECTURA DE PESTAÑAS (ORDEN SOLICITADO)
# ==========================================
tab_competencia, tab_estrategia, tab_360, tab_ads, tab_seo, tab_blog, tab_texto, tab_whatsapp, tab_video, tab_historial = st.tabs([
    "🧠 Competencia", "⚙️ Estrategia", "🔥 Campaña 360", "📊 Google Ads", "🚀 SEO", "📰 Blog GEO/AEO", "📝 Textos", "💬 WhatsApp", "🎬 Video", "📜 Historial"
])

# ==========================================
# --- PESTAÑA 1: COMPETENCIA ---
# ==========================================
with tab_competencia:
    st.subheader("🧠 Estrategia Competitiva")
    st.caption(
        "Escribe aquí a mano quiénes son tus competidores reales y en qué "
        "eres mejor — a propósito, ningún agente lo genera automáticamente, "
        "para no inventar competidores que no existen. Esto se guarda en Supabase."
    )

    if "estrategia_competitiva" not in st.session_state:
        st.session_state.estrategia_competitiva = obtener_prioridad_estrategica(supabase_ag, clave=CLAVE_ESTRATEGIA_COMPETITIVA)

    nueva_estrategia_competitiva = st.text_area(
        "Estrategia competitiva:",
        value=st.session_state.estrategia_competitiva,
        height=200,
        placeholder="Ej: Vivero X — fuerte en precio, débil en puntualidad logística. Nuestra ventaja: entrega garantizada en menos de 48h."
    )
    if st.button("💾 Guardar Estrategia Competitiva"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nueva_estrategia_competitiva, clave=CLAVE_ESTRATEGIA_COMPETITIVA)
            if ok:
                st.session_state.estrategia_competitiva = nueva_estrategia_competitiva
                st.success("Estrategia competitiva actualizada.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("🔗 Proponer Prioridad y Dolores desde esta Competencia")
    st.caption(
        "Genera un borrador de Prioridad y de Dolores razonando a partir de "
        "lo que escribiste arriba. Lo revisas, editas y decides si guardarlo."
    )

    if st.button("🧠 Generar Propuesta desde la Competencia"):
        if not st.session_state.estrategia_competitiva.strip():
            st.warning("Primero escribe y guarda tu estrategia competitiva arriba.")
        else:
            with st.spinner("Razonando propuesta a partir de la competencia..."):
                prioridad_prop, dolores_prop = proponer_estrategia_desde_competencia(
                    st.session_state.estrategia_competitiva,
                    prioridad_actual=st.session_state.prioridad_estrategica
                )
                if not prioridad_prop and not dolores_prop:
                    st.error("No se pudo generar la propuesta (revisa la conexión con Groq).")
                else:
                    st.session_state.propuesta_prioridad = prioridad_prop
                    st.session_state.propuesta_dolores = dolores_prop
                    st.session_state.propuesta_generada = True
                    st.rerun()

    if st.session_state.get("propuesta_generada"):
        st.markdown("**Propuesta de Prioridad** (editable antes de guardar):")
        prioridad_editable = st.text_area("Prioridad propuesta:", value=st.session_state.propuesta_prioridad, height=120, key="prioridad_editable_propuesta")
        
        if st.button("💾 Guardar como Prioridad Actual"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, prioridad_editable)
                if ok:
                    st.session_state.prioridad_estrategica = prioridad_editable
                    st.success("Guardado como Prioridad Actual.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        st.markdown("**Propuesta de Dolores frente a Intermediarios** (editable antes de guardar):")
        dolores_editable = st.text_area("Dolores propuestos:", value=st.session_state.propuesta_dolores, height=120, key="dolores_editable_propuesta")
        
        if st.button("💾 Guardar como Dolores frente a Intermediarios"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, dolores_editable, clave=CLAVE_DOLORES_INTERMEDIARIOS)
                if ok:
                    st.session_state.dolores_intermediarios = dolores_editable
                    st.success("Guardado como Dolores frente a Intermediarios.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        if st.button("🔄 Volver a generar (no me convence esta propuesta)"):
            with st.spinner("Generando una nueva propuesta..."):
                prioridad_prop, dolores_prop = proponer_estrategia_desde_competencia(st.session_state.estrategia_competitiva, prioridad_actual=st.session_state.prioridad_estrategica)
                st.session_state.propuesta_prioridad = prioridad_prop
                st.session_state.propuesta_dolores = dolores_prop
                st.rerun()

    st.markdown("---")
    test_comp = st.text_input("Generar pitch para:", placeholder="Ej: Palmas Botella por lote en Bogotá")
    if st.button("Generar Pitch Competitivo"):
        if test_comp:
            with st.spinner("Analizando ventaja competitiva..."):
                try:
                    resultado_pitch = analizar_contra_competencia(
                        test_comp,
                        estrategia_competitiva=st.session_state.estrategia_competitiva,
                        prioridad_estrategica=st.session_state.prioridad_estrategica
                    )
                    st.write(resultado_pitch)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Ingresa un tema o producto para generar el pitch.")

# ==========================================
# --- PESTAÑA 2: ESTRATEGIA ---
# ==========================================
with tab_estrategia:
    st.subheader("Prioridad Estratégica Actual")
    st.caption("Ajusta el CTA de los agentes orientados al mercado institucional.")
    nueva_prioridad = st.text_area("Prioridad actual:", value=st.session_state.prioridad_estrategica, height=150)
    
    if st.button("💾 Guardar Prioridad", key="btn_guardar_prioridad"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia.")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nueva_prioridad)
            if ok:
                st.session_state.prioridad_estrategica = nueva_prioridad
                st.success("Prioridad estratégica actualizada.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("Dolores del Viverista frente a Intermediarios Tradicionales")
    nuevos_dolores = st.text_area(
        "Dolores frente a intermediarios:",
        value=st.session_state.dolores_intermediarios,
        height=150,
        placeholder="Ej: El viverista pierde entre 30-40% del margen con intermediarios..."
    )
    if st.button("💾 Guardar Dolores", key="btn_guardar_dolores"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia.")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nuevos_dolores, clave=CLAVE_DOLORES_INTERMEDIARIOS)
            if ok:
                st.session_state.dolores_intermediarios = nuevos_dolores
                st.success("Dolores actualizados.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("🚀 Generar Campaña desde la Estrategia")
    st.caption("Usa la Prioridad y Dolores para generar Texto + WhatsApp + Video + SEO en un clic.")
    
    tema_campana_estrategia = st.text_input("Tema / ángulo de la campaña:", placeholder="Ej: Palmas Botella para constructoras", key="tema_campana_estrategia")
    audiencia_campana_estrategia = st.radio("Audiencia del WhatsApp:", options=["institucional", "viverista"], format_func=lambda x: "Comprador institucional" if x == "institucional" else "Viverista", horizontal=True, key="audiencia_campana_estrategia")
    forzar_duplicado_estrategia = st.checkbox("Generar de todas formas aunque ya exista un artículo SEO para este tema", key="forzar_duplicado_estrategia")

    if st.button("⚡ Generar Campaña desde Estrategia", type="primary"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia.")
        elif not tema_campana_estrategia:
            st.warning("Escribe un tema o ángulo para la campaña.")
        else:
            cluster_existente = cluster_ya_ejecutado(supabase_ag, tema_campana_estrategia)
            if cluster_existente and not forzar_duplicado_estrategia:
                st.warning(f"⚠️ Ya generaste SEO para un tema igual o muy parecido el {cluster_existente.get('fecha_creacion', 'anteriormente')}. Marca la casilla de arriba para forzar.")
            else:
                with st.spinner("Generando campaña completa a partir de la estrategia..."):
                    try:
                        prioridad_actual = st.session_state.prioridad_estrategica
                        dolores_actuales = st.session_state.dolores_intermediarios

                        texto_res = redactar_articulo_seo(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        wa_res = generar_campana_whatsapp(tema_campana_estrategia, audiencia=audiencia_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        video_res = redactar_guion_viral(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        seo_res = generar_seo_por_intencion(tema_campana_estrategia, dolores_intermediarios=dolores_actuales, prioridad_estrategica=prioridad_actual)

                        registros = [
                            {"tipo_contenido": "TEXTO", "titulo": tema_campana_estrategia, "contenido": texto_res or "", "estado": "borrador"},
                            {"tipo_contenido": "WHATSAPP", "titulo": f"WhatsApp — {tema_campana_estrategia}", "contenido": wa_res.mensaje_texto if wa_res else "", "estado": "borrador"},
                            {"tipo_contenido": "VIDEO", "titulo": f"Guion Video — {tema_campana_estrategia}", "contenido": video_res or "", "estado": "borrador"},
                        ]
                        if seo_res:
                            registros.append({"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md, "estado": "borrador"})
                            registrar_cluster_ejecutado(supabase_ag, tema_campana_estrategia)

                        supabase_ag.table("historial_contenidos").insert(registros).execute()

                        st.session_state.campana_estrategia_data = {
                            "tema": tema_campana_estrategia,
                            "texto": texto_res,
                            "wa": wa_res,
                            "video": video_res,
                            "seo": seo_res,
                        }
                        st.session_state.campana_estrategia_lista = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generando la campaña: {e}")

    if st.session_state.get("campana_estrategia_lista"):
        data = st.session_state.campana_estrategia_data
        st.success(f"Campaña generada y guardada en el Historial — tema: {data['tema']}")

        with st.expander("📝 Texto", expanded=True):
            st.write(data["texto"])

        with st.expander("💬 WhatsApp"):
            if data["wa"]:
                st.text_area("Copy:", value=data["wa"].mensaje_texto, height=100, key="ce_wa_copy")
                st.text_area("Guion nota de voz:", value=data["wa"].guion_nota_voz, height=150, key="ce_wa_script")
            else:
                st.warning("El agente de WhatsApp no devolvió resultado.")

        with st.expander("🎬 Video (concepto)"):
            st.write(data["video"])

        with st.expander("🚀 SEO Proactivo"):
            if data["seo"]:
                st.markdown(f"### {data['seo'].titulo_h1}")
                st.markdown(data["seo"].contenido_md)
            else:
                st.warning("El agente de SEO no devolvió resultado.")

# ==========================================
# --- PESTAÑA 3: ORQUESTADOR 360 ---
# ==========================================
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    st.markdown("Lee el inventario del **Marketplace**, genera la campaña (SEO, WhatsApp y Video) y la guarda en la base de la **Agencia**.")

    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        if not supabase_mkt:
            st.error("Falta la conexión al Marketplace.")
        elif not supabase_ag:
            st.error("Falta la conexión a la Agencia.")
        else:
            with st.spinner("Sincronizando agentes y ejecutando campaña..."):
                try:
                    res_inv = supabase_mkt.table("inventario").select("*").eq("estado_planta", "disponible").gte("stock", 20).order("inventario_id", desc=True).limit(10).execute()
                    res_campanas = supabase_ag.table("campanas_ejecutadas").select("inventario_id").execute()
                    lotes_procesados = [c["inventario_id"] for c in res_campanas.data] if res_campanas.data else []
                    item = next((l for l in res_inv.data if l["inventario_id"] not in lotes_procesados), None)

                    if not item:
                        st.info("Todos los lotes actuales ya tienen campaña.")
                    else:
                        planta_data = supabase_mkt.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data[0]
                        vivero_data = supabase_mkt.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data[0]

                        cols_nombre_p = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                        nombre_especie = planta_data[cols_nombre_p[0]] if cols_nombre_p else "Planta"

                        cols_nombre_v = [k for k in vivero_data.keys() if "nombre" in k.lower() or "vendedor" in k.lower()]
                        nombre_vivero = vivero_data[cols_nombre_v[0]] if cols_nombre_v else "Vivero Partner"

                        locacion = vivero_data.get("ubicacion") or "Sabana de Bogotá"
                        datos = {"especie": nombre_especie, "cantidad": item["stock"], "ubicacion": locacion, "vendedor": nombre_vivero}

                        seo_res = generar_seo_desde_inventario(datos, prioridad_estrategica=st.session_state.prioridad_estrategica)
                        wa_res = generar_campana_whatsapp(f"Vender lote disponible de {item['stock']} {nombre_especie} en {locacion}.", audiencia="institucional", prioridad_estrategica=st.session_state.prioridad_estrategica)
                        video_res = redactar_guion_viral(f"Carga logística y revisión de calidad de {nombre_especie} en {locacion}.", prioridad_estrategica=st.session_state.prioridad_estrategica)

                        supabase_ag.table("historial_contenidos").insert([
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md, "estado": "borrador"},
                            {"tipo_contenido": "WHATSAPP", "titulo": "Copy WhatsApp", "contenido": wa_res.mensaje_texto, "estado": "borrador"},
                            {"tipo_contenido": "VIDEO", "titulo": "Guion Video", "contenido": video_res, "estado": "borrador"}
                        ]).execute()

                        supabase_ag.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()

                        st.session_state.c360_data = {"lote": datos, "seo": seo_res, "wa": wa_res, "video": video_res}
                        st.session_state.c360_lista = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Error en la orquestación: {e}")

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
# --- PESTAÑA 4: GOOGLE ADS (DEPARTAMENTO DE PERFORMANCE) ---
# ==========================================
with tab_ads:
    st.subheader("📊 Generador de Pauta (Google Ads)")
    st.markdown("Estructura campañas segregadas (retail vs. institucional) y guarda los insights para alimentar al agente de SEO proactivo.")

    modo_pauta = st.radio(
        "Selecciona el enfoque de la campaña:",
        ["B2C", "B2B"],
        format_func=lambda x: "🪴 B2C (Materas, Retail, Consumidor Final)" if x == "B2C" else "🏢 B2B (Marketplace, Constructoras, Mayoristas)",
        horizontal=True
    )

    obj_pauta = st.text_input(
        "Objetivo o producto de la campaña:",
        placeholder="Ej: Vender materas modernas de cemento en Bogotá" if modo_pauta == "B2C" else "Ej: Proveedor mayorista de eugenias para proyectos paisajísticos"
    )

    if st.button("🚀 Generar y Guardar Campaña", type="primary"):
        if obj_pauta:
            if not supabase_ag:
                st.error("Falta la conexión a la base de datos de la Agencia para guardar los insights.")
            else:
                with st.spinner("Analizando mercado y redactando copies bajo reglas de Google Ads..."):
                    resultados_ads = generar_y_guardar_pauta(obj_pauta, modo_pauta, supabase_ag)
                    
                    if resultados_ads:
                        st.success("¡Campaña estructurada y guardada en la Agencia! El Agente de SEO ya puede usarla.")
                        
                        col_kw, col_copy = st.columns(2)
                        with col_kw:
                            st.markdown("### 🔑 Palabras Clave")
                            st.write("**Positivas (Atacar):**")
                            for kw in resultados_ads["keywords_positivas"]:
                                st.caption(f"✅ {kw}")
                            
                            st.write("**Negativas (Bloquear vital):**")
                            for kw in resultados_ads["keywords_negativas"]:
                                st.caption(f"❌ {kw}")
                                
                        with col_copy:
                            st.markdown("### ✍️ Copy para Anuncios")
                            st.write("**Títulos (Máx 30 carac.):**")
                            for t in resultados_ads["titulos_anuncio"]:
                                st.caption(f"📌 {t}")
                            
                            st.write("**Descripciones (Máx 90 carac.):**")
                            for d in resultados_ads["descripciones_anuncio"]:
                                st.caption(f"📝 {d}")
                    else:
                        st.error("Hubo un problema generando la campaña. Revisa los logs de la consola.")
        else:
            st.warning("Por favor ingresa un objetivo para la campaña.")

# ==========================================
# --- PESTAÑA 5: SEO PROGRAMÁTICO ---
# ==========================================
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")
    modo_seo = st.radio("Modo de operación:", ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual", "🎯 Proactivo (Intención de Búsqueda)"], horizontal=True)

    if modo_seo == "📡 Automatizado (Base de Datos)":
        if st.button("Analizar BD y Generar SEO"):
            if not supabase_mkt:
                st.error("Falta configurar la conexión al Marketplace.")
            else:
                with st.spinner("Decodificando esquema y generando contenido..."):
                    try:
                        res_inv = supabase_mkt.table("inventario").select("*").eq("estado_planta", "disponible").gte("stock", 20).order("inventario_id", desc=True).limit(1).execute()
                        if not res_inv.data:
                            st.warning("No hay inventario disponible con más de 20 unidades.")
                        else:
                            item = res_inv.data[0]
                            planta_data = supabase_mkt.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data[0]
                            vivero_data = supabase_mkt.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data[0]

                            cols_nombre_planta = [k for k in planta_data.keys() if "nombre" in k.lower() or "especie" in k.lower()]
                            nombre_especie = planta_data[cols_nombre_planta[0]] if cols_nombre_planta else f"Planta_ID_{item['planta_id']}"

                            cols_nombre_vivero = [k for k in vivero_data.keys() if "nombre" in k.lower() or "vendedor" in k.lower()]
                            nombre_vivero = vivero_data[cols_nombre_vivero[0]] if cols_nombre_vivero else f"Vivero_ID_{item['vivero_id']}"

                            locacion = vivero_data.get("ubicacion") or vivero_data.get("ciudad") or vivero_data.get("municipio") or "Sabana de Bogotá"
                            
                            datos_auto = {"especie": nombre_especie, "cantidad": item["stock"], "ubicacion": locacion, "vendedor": nombre_vivero}
                            articulo = generar_seo_desde_inventario(datos_auto, prioridad_estrategica=st.session_state.prioridad_estrategica)
                            if articulo:
                                st.success("¡Artículo estratégico B2B generado con éxito!")
                                st.markdown(f"### {articulo.titulo_h1}")
                                st.markdown(articulo.contenido_md)
                            else:
                                st.error("El motor de IA no devolvió un formato válido.")
                    except Exception as e:
                        st.error(f"Error en la consulta automática: {e}")

    elif modo_seo == "✍️ Ingreso Manual":
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
                    datos_manuales = {"especie": man_especie, "cantidad": man_cantidad, "ubicacion": man_ubicacion, "vendedor": man_vendedor}
                    articulo = generar_seo_desde_inventario(datos_manuales, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    if articulo:
                        st.success("Artículo manual generado exitosamente.")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
            else:
                st.warning("Completa los campos requeridos para proceder.")

    else:
        cluster_seo = st.text_input("Cluster / intención de búsqueda objetivo:", placeholder="Ej: Comprar palmas botella por lote en Bogotá")
        forzar_duplicado_seo = st.checkbox("Generar de todas formas aunque ya exista un artículo para este cluster", key="forzar_duplicado_seo")
        if st.button("Generar Artículo Proactivo"):
            if not cluster_seo:
                st.warning("Escribe el cluster o intención de búsqueda objetivo.")
            else:
                cluster_existente = cluster_ya_ejecutado(supabase_ag, cluster_seo) if supabase_ag else None
                if cluster_existente and not forzar_duplicado_seo:
                    st.warning(f"⚠️ Ya existe un artículo para un cluster igual o muy parecido el {cluster_existente.get('fecha_creacion', 'anteriormente')}.")
                else:
                    with st.spinner("Redactando artículo de intención de búsqueda..."):
                        articulo = generar_seo_por_intencion(
                            cluster_seo,
                            dolores_intermediarios=st.session_state.dolores_intermediarios,
                            prioridad_estrategica=st.session_state.prioridad_estrategica
                        )
                        if articulo:
                            st.success("Artículo proactivo generado con éxito.")
                            st.markdown(f"### {articulo.titulo_h1}")
                            st.markdown(articulo.contenido_md)
                            if supabase_ag:
                                supabase_ag.table("historial_contenidos").insert({
                                    "tipo_contenido": "SEO", "titulo": articulo.titulo_h1, "contenido": articulo.contenido_md, "estado": "borrador"
                                }).execute()
                                registrar_cluster_ejecutado(supabase_ag, cluster_seo)
                        else:
                            st.error("El motor de IA no devolvió un formato válido.")

# ==========================================
# --- PESTAÑA 6: BLOG GEO/AEO ---
# ==========================================
with tab_blog:
    st.subheader("📰 Blog Institucional (GEO/AEO)")
    st.caption("Genera artículos de blog de largo formato optimizados para IA (ChatGPT, Perplexity, Gemini).")

    tema_blog = st.text_input("Tema del artículo (en forma de pregunta natural funciona mejor):", placeholder="Ej: ¿Cuánto se pierde realmente al comprar plantas a través de un intermediario?", key="tema_blog")
    datos_verificables_blog = st.text_area("Datos verificables reales (opcional):", placeholder="Ej: tiempo aclimatación: 15 días...", height=80, key="datos_verificables_blog")

    if st.button("📝 Generar Artículo de Blog", type="primary"):
        if not tema_blog:
            st.warning("Escribe un tema para el artículo.")
        else:
            with st.spinner("Redactando artículo de blog optimizado para GEO/AEO..."):
                try:
                    articulo_blog = redactar_articulo_blog(tema_blog, datos_verificables=datos_verificables_blog or None, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    st.session_state.articulo_blog_data = {"tema": tema_blog, "contenido": articulo_blog}
                    st.session_state.articulo_blog_listo = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error técnico: {e}")

    if st.session_state.get("articulo_blog_listo"):
        data = st.session_state.articulo_blog_data
        st.success(f"Artículo generado — tema: {data['tema']}")
        st.markdown(data["contenido"])
        st.markdown("---")
        if st.button("💾 Guardar en Historial como borrador"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                supabase_ag.table("historial_contenidos").insert({
                    "tipo_contenido": "BLOG", "titulo": data["tema"], "contenido": data["contenido"], "estado": "borrador"
                }).execute()
                st.success("Guardado en el Historial como borrador.")

# ==========================================
# --- PESTAÑA 7: TEXTOS ---
# ==========================================
with tab_texto:
    st.subheader("Redacción de Artículos y Copy B2B")
    tema_texto = st.text_input("Tema o requerimiento del texto:", placeholder="Ej: Beneficios de especies nativas")

    if st.button("Generar Texto B2B"):
        if tema_texto:
            with st.spinner("El agente está redactando..."):
                try:
                    resultado_texto = redactar_articulo_seo(tema_texto, prioridad_estrategica=st.session_state.prioridad_estrategica)
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
# --- PESTAÑA 8: WHATSAPP ---
# ==========================================
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    audiencia_wa = st.radio("¿A quién le escribes?", options=["institucional", "viverista"], format_func=lambda x: "Comprador institucional" if x == "institucional" else "Viverista", horizontal=True)
    obj_wa = st.text_input("Objetivo de la campaña:", placeholder="Ej: Vender 500 Eugenias a paisajistas")

    if st.button("Generar Kit de WhatsApp"):
        if obj_wa:
            with st.spinner("Conectando con Agente de Crecimiento..."):
                campana = generar_campana_whatsapp(obj_wa, audiencia=audiencia_wa, prioridad_estrategica=st.session_state.prioridad_estrategica)
                if campana:
                    st.session_state.wa_copy = campana.mensaje_texto
                    st.session_state.wa_script = campana.guion_nota_voz
                    st.session_state.wa_generado = True
                    st.success("Kit generado con éxito.")
                else:
                    st.error("El agente de crecimiento no pudo responder.")
        else:
            st.warning("Por favor ingresa un objetivo.")

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
# --- PESTAÑA 9: VIDEO ---
# ==========================================
with tab_video:
    st.subheader("🎬 Producción de Video B2B (Veo 3.1)")
    with st.expander("📝 1. Pre-Producción (Generar Concepto y Guion)", expanded=True):
        tema_video = st.text_input("Concepto visual del comercial:", placeholder="Ej: Lote mayorista de eugenias")
        if st.button("Generar Concepto Visual"):
            if tema_video:
                with st.spinner("Estructurando tomas..."):
                    try:
                        resultado_video = redactar_guion_viral(tema_video, prioridad_estrategica=st.session_state.prioridad_estrategica)
                        st.success("Concepto generado.")
                        st.write(resultado_video)
                    except Exception as e:
                        st.error(f"Error técnico: {e}")
            else:
                st.warning("Ingresa un concepto primero.")

    with st.expander("🎥 2. Producción (Renderizar Escenas)", expanded=False):
        plantilla_json = '''{
    "escena_1": {
        "nombre": "Inicio de Jornada",
        "tipo": "IA_GENERATIVE",
        "visual": "Viverista revisando sus plantas temprano en la mañana",
        "emocion": "Orgullo por el oficio",
        "camara": "Plano general",
        "texto": "Cada planta, revisada a mano"
    }
}'''
        storyboard_input = st.text_area("Storyboard (Formato JSON):", value=plantilla_json, height=250)
        if st.button("🚀 Iniciar Renderizado", type="primary"):
            with st.spinner("Conectando con Google Veo 3.1..."):
                try:
                    resultados_render = ejecutar_pipeline_agencia(storyboard_input)
                    if resultados_render:
                        st.success("¡Pipeline finalizado!")
                        for key, data in resultados_render.items():
                            st.markdown(f"### {key.replace('_', ' ').title()}")
                            if data["status"] == "Listo" and data.get("url"):
                                st.video(data["url"])
                            else:
                                st.warning(f"**Estado:** {data['status']}")
                    else:
                        st.error("No se pudieron generar los videos.")
                except Exception as e:
                    st.error(f"Error crítico en el orquestador: {e}")

# ==========================================
# --- PESTAÑA 10: HISTORIAL ---
# ==========================================
with tab_historial:
    st.subheader("📜 Historial de Contenido Generado")
    st.caption("Todo lo generado nace como 'borrador'. Márcalo como 'aprobado' una vez lo revisaste.")
    if not supabase_ag:
        st.error("Falta la conexión a la Agencia.")
    else:
        try:
            res = supabase_ag.table("historial_contenidos").select("*").order("fecha_creacion", desc=True).execute()
            if not res.data:
                st.info("Aún no hay contenido en el historial.")
            else:
                for item in res.data:
                    estado_item = item.get("estado", "borrador") or "borrador"
                    genero_venta_item = item.get("genero_venta")
                    icono_estado = "✅" if estado_item == "aprobado" else "📝"
                    
                    with st.expander(f"{icono_estado} {item.get('tipo_contenido', 'N/A')} | {item.get('titulo', 'Sin título')} | estado: {estado_item}"):
                        titulo_editado = st.text_input("Título:", value=item.get("titulo", ""), key=f"titulo_{item['id']}")
                        contenido_editado = st.text_area("Contenido:", value=item.get("contenido", ""), height=250, key=f"contenido_{item['id']}")
                        
                        if st.button("💾 Guardar cambios", key=f"guardar_edicion_{item['id']}"):
                            supabase_ag.table("historial_contenidos").update({"titulo": titulo_editado, "contenido": contenido_editado}).eq("id", item["id"]).execute()
                            st.success("Cambios guardados.")
                            st.rerun()

                        st.markdown("---")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if estado_item != "aprobado":
                                if st.button("✅ Marcar como aprobado", key=f"aprobar_{item['id']}"):
                                    supabase_ag.table("historial_contenidos").update({"estado": "aprobado"}).eq("id", item["id"]).execute()
                                    st.rerun()
                            else:
                                st.caption("✅ Aprobado")
                        with col_b:
                            nuevo_resultado = st.selectbox(
                                "¿Generó una venta?",
                                options=["Sin dato", "Sí", "No"],
                                index={"Sin dato": 0, True: 1, False: 2}.get(genero_venta_item, 0) if genero_venta_item is not None else 0,
                                key=f"venta_{item['id']}"
                            )
                            if st.button("Guardar resultado", key=f"guardar_venta_{item['id']}"):
                                valor_venta = {"Sin dato": None, "Sí": True, "No": False}[nuevo_resultado]
                                supabase_ag.table("historial_contenidos").update({"genero_venta": valor_venta}).eq("id", item["id"]).execute()
                                st.rerun()

                        st.markdown("---")
                        confirmar_borrado = st.checkbox("Confirmar que quiero eliminar esto", key=f"confirmar_borrar_{item['id']}")
                        if st.button("🗑️ Eliminar", key=f"eliminar_{item['id']}", disabled=not confirmar_borrado):
                            supabase_ag.table("historial_contenidos").delete().eq("id", item["id"]).execute()
                            st.success("Eliminado.")
                            st.rerun()
        except Exception as e:
            st.error(f"❌ Error técnico real: {e}")

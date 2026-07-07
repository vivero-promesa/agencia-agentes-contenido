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
    from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario, generar_seo_por_intencion
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

# Prioridad estratégica dinámica (ej. "generar transacciones reales") — se
# lee una vez al cargar la app y se usa en todos los agentes institucionales.
if "prioridad_estrategica" not in st.session_state:
    st.session_state.prioridad_estrategica = obtener_prioridad_estrategica(supabase_ag)

# Dolores del viverista frente a intermediarios — escrito a mano por el
# usuario (no generado por IA), se lee una vez al cargar la app.
if "dolores_intermediarios" not in st.session_state:
    st.session_state.dolores_intermediarios = obtener_prioridad_estrategica(supabase_ag, clave=CLAVE_DOLORES_INTERMEDIARIOS)

# ==========================================
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_competencia, tab_estrategia, tab_360, tab_texto, tab_whatsapp, tab_video, tab_seo, tab_blog, tab_historial = st.tabs([
    "🧠 Competencia", "⚙️ Estrategia", "🔥 Campaña 360", "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "📰 Blog GEO/AEO", "📜 Historial"
])

# ==========================================
# --- PESTAÑA NUEVA: ESTRATEGIA ---
# ==========================================
with tab_estrategia:
    st.subheader("Prioridad Estratégica Actual")
    st.caption(
        "Esto no reemplaza el tono de marca (identidad_marca.py) ni la "
        "identidad visual (brand_book.py) — es el énfasis de negocio del "
        "momento (ej. \"generar transacciones reales\") que ajusta el CTA "
        "de los agentes orientados al mercado institucional."
    )
    nueva_prioridad = st.text_area(
        "Prioridad actual:",
        value=st.session_state.prioridad_estrategica,
        height=150
    )
    if st.button("💾 Guardar Prioridad"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nueva_prioridad)
            if ok:
                st.session_state.prioridad_estrategica = nueva_prioridad
                st.success("Prioridad estratégica actualizada. Los próximos contenidos ya la usarán.")
            else:
                st.error("No se pudo guardar en Supabase. Revisa que la tabla configuracion_estrategica exista.")

    st.markdown("---")
    st.subheader("Dolores del Viverista frente a Intermediarios Tradicionales")
    st.caption(
        "Escribe esto a mano — a propósito, ningún agente lo genera "
        "automáticamente, para no inventar quejas o competidores que no son "
        "reales. Los agentes de SEO lo usan como contexto cuando el tema lo "
        "amerita."
    )
    nuevos_dolores = st.text_area(
        "Dolores frente a intermediarios:",
        value=st.session_state.dolores_intermediarios,
        height=150,
        placeholder="Ej: El viverista pierde entre 30-40% del margen con intermediarios que no aportan logística ni visibilidad real..."
    )
    if st.button("💾 Guardar Dolores"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nuevos_dolores, clave=CLAVE_DOLORES_INTERMEDIARIOS)
            if ok:
                st.session_state.dolores_intermediarios = nuevos_dolores
                st.success("Dolores actualizados. El SEO proactivo ya los usará como contexto.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("🚀 Generar Campaña desde la Estrategia")
    st.caption(
        "Usa la Prioridad y los Dolores de arriba (guárdalos primero) más un "
        "tema puntual, para generar Texto + WhatsApp + Video + SEO en un solo "
        "clic — y guardarlo en el Historial, igual que hace la Campaña 360, "
        "pero partiendo de la estrategia en vez del inventario."
    )
    tema_campana_estrategia = st.text_input(
        "Tema / ángulo de la campaña:",
        placeholder="Ej: Palmas Botella para constructoras en la Sabana de Bogotá",
        key="tema_campana_estrategia"
    )
    audiencia_campana_estrategia = st.radio(
        "Audiencia del WhatsApp:",
        options=["institucional", "viverista"],
        format_func=lambda x: "Comprador institucional" if x == "institucional" else "Viverista",
        horizontal=True,
        key="audiencia_campana_estrategia"
    )
    forzar_duplicado_estrategia = st.checkbox(
        "Generar de todas formas aunque ya exista un artículo SEO para este tema (no recomendado — riesgo de competir contigo mismo en Google)",
        key="forzar_duplicado_estrategia"
    )

    if st.button("⚡ Generar Campaña desde Estrategia", type="primary"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        elif not tema_campana_estrategia:
            st.warning("Escribe un tema o ángulo para la campaña.")
        else:
            cluster_existente = cluster_ya_ejecutado(supabase_ag, tema_campana_estrategia)
            if cluster_existente and not forzar_duplicado_estrategia:
                st.warning(
                    f"⚠️ Ya generaste SEO para un tema igual o muy parecido "
                    f"(\"{cluster_existente.get('cluster_original', tema_campana_estrategia)}\") "
                    f"el {cluster_existente.get('fecha_creacion', 'anteriormente')}. "
                    f"Generar otro artículo para el mismo tema compite contigo mismo en "
                    f"buscadores (keyword cannibalization). Si de verdad quieres otro ángulo "
                    f"distinto, marca la casilla de arriba para continuar."
                )
            else:
                with st.spinner("Generando campaña completa a partir de la estrategia..."):
                    try:
                        prioridad_actual = st.session_state.prioridad_estrategica
                        dolores_actuales = st.session_state.dolores_intermediarios

                        texto_res = redactar_articulo_seo(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        wa_res = generar_campana_whatsapp(
                            tema_campana_estrategia,
                            audiencia=audiencia_campana_estrategia,
                            prioridad_estrategica=prioridad_actual
                        )
                        video_res = redactar_guion_viral(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        seo_res = generar_seo_por_intencion(
                            tema_campana_estrategia,
                            dolores_intermediarios=dolores_actuales,
                            prioridad_estrategica=prioridad_actual
                        )

                        # Guardado en Historial (misma tabla y esquema que Campaña 360)
                        # estado: "borrador" — nada se considera aprobado/listo hasta
                        # que se revise a mano en la pestaña Historial.
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
                        st.error(f"Error generando la campaña desde estrategia: {e}")

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
# --- PESTAÑA 1: TEXTOS ---
# ==========================================
with tab_texto:
    st.subheader("Redacción de Artículos y Copy B2B")
    tema_texto = st.text_input("Tema o requerimiento del texto:", placeholder="Ej: Beneficios de especies nativas en proyectos de paisajismo")

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
# --- PESTAÑA 2: WHATSAPP ---
# ==========================================
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    audiencia_wa = st.radio(
        "¿A quién le escribes?",
        options=["institucional", "viverista"],
        format_func=lambda x: "Comprador institucional (paisajista/constructora)" if x == "institucional" else "Viverista (productor)",
        horizontal=True
    )
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
                        resultado_video = redactar_guion_viral(tema_video, prioridad_estrategica=st.session_state.prioridad_estrategica)
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

    modo_seo = st.radio(
        "Modo de operación:",
        ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual", "🎯 Proactivo (Intención de Búsqueda)"],
        horizontal=True
    )

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
                    datos_manuales = {
                        "especie": man_especie,
                        "cantidad": man_cantidad,
                        "ubicacion": man_ubicacion,
                        "vendedor": man_vendedor
                    }
                    articulo = generar_seo_desde_inventario(datos_manuales, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    if articulo:
                        st.success("Artículo manual generado exitosamente.")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
            else:
                st.warning("Completa los campos requeridos para proceder.")

    else:
        st.caption(
            "SEO PROACTIVO: escribe para capturar una búsqueda transaccional "
            "(ej. \"comprar palmas botella por lote en Bogotá\") aunque hoy no "
            "tengas ese stock exacto — construye autoridad temática para "
            "cuando sí lo tengas. No depende del inventario."
        )
        cluster_seo = st.text_input(
            "Cluster / intención de búsqueda objetivo:",
            placeholder="Ej: Comprar palmas botella por lote en Bogotá"
        )
        forzar_duplicado_seo = st.checkbox(
            "Generar de todas formas aunque ya exista un artículo para este cluster (no recomendado)",
            key="forzar_duplicado_seo"
        )
        if st.button("Generar Artículo Proactivo"):
            if not cluster_seo:
                st.warning("Escribe el cluster o intención de búsqueda objetivo.")
            else:
                cluster_existente = cluster_ya_ejecutado(supabase_ag, cluster_seo) if supabase_ag else None
                if cluster_existente and not forzar_duplicado_seo:
                    st.warning(
                        f"⚠️ Ya existe un artículo para un cluster igual o muy parecido "
                        f"(\"{cluster_existente.get('cluster_original', cluster_seo)}\"), generado el "
                        f"{cluster_existente.get('fecha_creacion', 'anteriormente')}. Generar otro compite "
                        f"contigo mismo en buscadores (keyword cannibalization). Marca la casilla de "
                        f"arriba si de verdad es un ángulo distinto."
                    )
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
                                    "tipo_contenido": "SEO",
                                    "titulo": articulo.titulo_h1,
                                    "contenido": articulo.contenido_md,
                                    "estado": "borrador"
                                }).execute()
                                registrar_cluster_ejecutado(supabase_ag, cluster_seo)
                                st.caption("Guardado en el Historial como borrador.")
                        else:
                            st.error("El motor de IA no devolvió un formato válido.")

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
                        seo_res = generar_seo_desde_inventario(datos, prioridad_estrategica=st.session_state.prioridad_estrategica)
                        wa_res = generar_campana_whatsapp(f"Vender lote disponible de {item['stock']} {nombre_especie} en {locacion}.", audiencia="institucional", prioridad_estrategica=st.session_state.prioridad_estrategica)
                        video_res = redactar_guion_viral(f"Carga logística y revisión de calidad de {nombre_especie} en {locacion}.", prioridad_estrategica=st.session_state.prioridad_estrategica)

                        # 3. Guardado Histórico (AGENCIA)
                        supabase_ag.table("historial_contenidos").insert([
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md, "estado": "borrador"},
                            {"tipo_contenido": "WHATSAPP", "titulo": "Copy WhatsApp", "contenido": wa_res.mensaje_texto, "estado": "borrador"},
                            {"tipo_contenido": "VIDEO", "titulo": "Guion Video", "contenido": video_res, "estado": "borrador"}
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
# --- PESTAÑA NUEVA: BLOG GEO/AEO ---
# ==========================================
with tab_blog:
    st.subheader("📰 Blog Institucional (GEO/AEO)")
    st.caption(
        "Genera artículos de blog de largo formato optimizados para que "
        "ChatGPT, Perplexity y Gemini los citen — respuesta directa, "
        "secciones autocontenidas y un bloque de Preguntas Frecuentes listo "
        "para copiar al bloque nativo FAQ de tu plugin de SEO (ej. Rank "
        "Math). Distinto de la pestaña Textos: esto es contenido de blog "
        "extenso, no copy corto."
    )

    tema_blog = st.text_input(
        "Tema del artículo (en forma de pregunta natural funciona mejor):",
        placeholder="Ej: ¿Cuánto se pierde realmente al comprar plantas ornamentales a través de un intermediario?",
        key="tema_blog"
    )
    datos_verificables_blog = st.text_area(
        "Datos verificables reales (opcional, pero recomendado):",
        placeholder="Ej: tiempo de aclimatación: 15 días; peso promedio del bulto: 12kg; margen perdido con intermediarios: 30-40%",
        height=80,
        key="datos_verificables_blog"
    )

    if st.button("📝 Generar Artículo de Blog", type="primary"):
        if not tema_blog:
            st.warning("Escribe un tema para el artículo.")
        else:
            with st.spinner("Redactando artículo de blog optimizado para GEO/AEO..."):
                try:
                    articulo_blog = redactar_articulo_blog(
                        tema_blog,
                        datos_verificables=datos_verificables_blog or None,
                        prioridad_estrategica=st.session_state.prioridad_estrategica
                    )
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
                st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
            else:
                supabase_ag.table("historial_contenidos").insert({
                    "tipo_contenido": "BLOG",
                    "titulo": data["tema"],
                    "contenido": data["contenido"],
                    "estado": "borrador"
                }).execute()
                st.success("Guardado en el Historial como borrador.")

# ==========================================
# --- PESTAÑA 6: HISTORIAL (lee de la AGENCIA) ---
# ==========================================
with tab_historial:
    st.subheader("📜 Historial de Contenido Generado")
    st.caption(
        "Todo lo generado nace como 'borrador'. Márcalo como 'aprobado' una "
        "vez lo revisaste y de verdad lo vas a usar — eso es lo que separa "
        "lo que tiene valor real de lo que fue solo una prueba. Cuando "
        "sepas si una pieza generó una venta, márcalo también: es la única "
        "forma de empezar a conectar contenido con resultado real, mientras "
        "no haya una medición automática. También puedes editar el texto "
        "directamente aquí antes de aprobarlo, o eliminar lo que no sirva."
    )
    if not supabase_ag:
        st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
    else:
        try:
            res = supabase_ag.table("historial_contenidos").select("*").order("fecha_creacion", desc=True).execute()
            if not res.data:
                st.info("Aún no hay contenido en el historial. Lanza una Campaña 360 para empezar.")
            else:
                for item in res.data:
                    estado_item = item.get("estado", "borrador") or "borrador"
                    genero_venta_item = item.get("genero_venta")
                    icono_estado = "✅" if estado_item == "aprobado" else "📝"
                    with st.expander(f"{icono_estado} {item.get('tipo_contenido', 'N/A')} | {item.get('titulo', 'Sin título')} | estado: {estado_item}"):

                        # --- Edición de título y contenido ---
                        titulo_editado = st.text_input(
                            "Título:",
                            value=item.get("titulo", ""),
                            key=f"titulo_{item['id']}"
                        )
                        contenido_editado = st.text_area(
                            "Contenido:",
                            value=item.get("contenido", ""),
                            height=250,
                            key=f"contenido_{item['id']}"
                        )
                        if st.button("💾 Guardar cambios", key=f"guardar_edicion_{item['id']}"):
                            supabase_ag.table("historial_contenidos").update({
                                "titulo": titulo_editado,
                                "contenido": contenido_editado
                            }).eq("id", item["id"]).execute()
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

                        # --- Eliminar, con confirmación para no borrar por accidente ---
                        st.markdown("---")
                        confirmar_borrado = st.checkbox(
                            "Confirmar que quiero eliminar esto permanentemente",
                            key=f"confirmar_borrar_{item['id']}"
                        )
                        if st.button("🗑️ Eliminar", key=f"eliminar_{item['id']}", disabled=not confirmar_borrado):
                            supabase_ag.table("historial_contenidos").delete().eq("id", item["id"]).execute()
                            st.success("Eliminado.")
                            st.rerun()
        except Exception as e:
            st.error(f"❌ Error técnico real: {e}")

# ==========================================
# --- PESTAÑA 7: COMPETENCIA ---
# ==========================================
with tab_competencia:
    st.subheader("🧠 Estrategia Competitiva")
    st.caption(
        "Escribe aquí a mano quiénes son tus competidores reales y en qué "
        "eres mejor — a propósito, ningún agente lo genera automáticamente, "
        "para no inventar competidores que no existen. Esto se guarda en "
        "Supabase (antes se perdía al recargar la página)."
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
        "lo que escribiste arriba — no se guarda solo. Lo revisas, lo editas "
        "si quieres, y decides tú si lo mandas a la pestaña Estrategia. "
        "Puedes regenerar tantas veces como quieras antes de guardar."
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
        prioridad_editable = st.text_area(
            "Prioridad propuesta:",
            value=st.session_state.propuesta_prioridad,
            height=120,
            key="prioridad_editable_propuesta"
        )
        if st.button("💾 Guardar como Prioridad Actual"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, prioridad_editable)
                if ok:
                    st.session_state.prioridad_estrategica = prioridad_editable
                    st.success("Guardado como Prioridad Actual — ya la usan todos los agentes institucionales.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        st.markdown("**Propuesta de Dolores frente a Intermediarios** (editable antes de guardar):")
        dolores_editable = st.text_area(
            "Dolores propuestos:",
            value=st.session_state.propuesta_dolores,
            height=120,
            key="dolores_editable_propuesta"
        )
        if st.button("💾 Guardar como Dolores frente a Intermediarios"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, dolores_editable, clave=CLAVE_DOLORES_INTERMEDIARIOS)
                if ok:
                    st.session_state.dolores_intermediarios = dolores_editable
                    st.success("Guardado como Dolores frente a Intermediarios — ya los usa el SEO proactivo.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        if st.button("🔄 Volver a generar (no me convence esta propuesta)"):
            with st.spinner("Generando una nueva propuesta..."):
                prioridad_prop, dolores_prop = proponer_estrategia_desde_competencia(
                    st.session_state.estrategia_competitiva,
                    prioridad_actual=st.session_state.prioridad_estrategica
                )
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

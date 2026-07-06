import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo

# ==========================================
# 🚨 BLOQUE DE DIAGNÓSTICO (CAZADOR DE ERRORES)
# ==========================================
try:
    from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario, generar_seo_por_intencion
except Exception as e:
    st.error("🚨 Error real detectado al intentar leer 'agentes_crecimiento.py':")
    st.exception(e)
    st.stop()
# ==========================================

from agente_audio import generar_audio_elevenlabs
from agente_video import ejecutar_pipeline_agencia
from competencia import analizar_contra_competencia, get_config_competencia
from estrategia import obtener_prioridad_estrategica, guardar_prioridad_estrategica, CLAVE_DOLORES_INTERMEDIARIOS

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
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360, tab_historial, tab_competencia, tab_estrategia = st.tabs([
    "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "🔥 Campaña 360", "📜 Historial", "🧠 Competencia", "⚙️ Estrategia"
])

# ==========================================
# --- PESTAÑA NUEVA: ESTRATEGIA ---
# ==========================================
with tab_estrategia:
    st.subheader("Prioridad Estratégica Actual")
    st.caption("Ajusta el CTA de los agentes orientados al mercado institucional.")
    nueva_prioridad = st.text_area("Prioridad actual:", value=st.session_state.prioridad_estrategica, height=150)
    
    if st.button("💾 Guardar Prioridad"):
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
    if st.button("💾 Guardar Dolores"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia.")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nuevos_dolores, clave=CLAVE_DOLORES_INTERMEDIARIOS)
            if ok:
                st.session_state.dolores_intermediarios = nuevos_dolores
                st.success("Dolores actualizados.")
            else:
                st.error("No se pudo guardar en Supabase.")

# ==========================================
# --- PESTAÑA 1: TEXTOS ---
# ==========================================
with tab_texto:
    st.subheader("Redacción de Artículos y Copy B2B")
    tema_texto = st.text_input("Tema o requerimiento del texto:")

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
        format_func=lambda x: "Comprador institucional" if x == "institucional" else "Viverista",
        horizontal=True
    )
    obj_wa = st.text_input("Objetivo de la campaña:")

    if st.button("Generar Kit de WhatsApp"):
        if obj_wa:
            with st.spinner("Conectando con Agente..."):
                campana = generar_campana_whatsapp(obj_wa, audiencia=audiencia_wa, prioridad_estrategica=st.session_state.prioridad_estrategica)
                if campana:
                    st.session_state.wa_copy = campana.mensaje_texto
                    st.session_state.wa_script = campana.guion_nota_voz
                    st.session_state.wa_generado = True
                    st.success("Kit generado con éxito.")
                else:
                    st.error("El agente no pudo responder.")
        else:
            st.warning("Ingresa un objetivo.")

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
# --- PESTAÑA 3: VIDEO ---
# ==========================================
with tab_video:
    st.subheader("🎬 Producción de Video B2B (Veo 3.1)")
    
    with st.expander("📝 1. Pre-Producción", expanded=True):
        tema_video = st.text_input("Concepto visual:")
        if st.button("Generar Concepto Visual"):
            if tema_video:
                with st.spinner("Estructurando guion..."):
                    try:
                        resultado_video = redactar_guion_viral(tema_video, prioridad_estrategica=st.session_state.prioridad_estrategica)
                        st.success("Concepto generado.")
                        st.write(resultado_video)
                    except Exception as e:
                        st.error(f"Error técnico: {e}")
            else:
                st.warning("Ingresa un concepto.")

    with st.expander("🎥 2. Producción", expanded=False):
        plantilla_json = '''{
    "escena_1": {
        "nombre": "Inicio de Jornada",
        "tipo": "IA_GENERATIVE",
        "visual": "Viverista revisando plantas, hojas húmedas",
        "emocion": "Orgullo por el oficio",
        "camara": "Plano general",
        "texto": "Cada planta revisada a mano"
    }
}'''
        storyboard_input = st.text_area("Storyboard (JSON):", value=plantilla_json, height=250)
        if st.button("🚀 Iniciar Renderizado", type="primary"):
            with st.spinner("Conectando con Google Veo 3.1..."):
                try:
                    resultados_render = ejecutar_pipeline_agencia(storyboard_input)
                    if resultados_render:
                        st.success("Pipeline finalizado!")
                        for key, data in resultados_render.items():
                            st.markdown(f"### {key.title()}")
                            if data["status"] == "Listo" and data.get("url"):
                                st.video(data["url"])
                            else:
                                st.warning(f"Estado: {data['status']}")
                    else:
                        st.error("No se pudieron generar los videos.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# --- PESTAÑA 4: SEO ---
# ==========================================
with tab_seo:
    st.subheader("Trigger SEO")
    modo_seo = st.radio("Modo:", ["📡 Automatizado", "✍️ Manual", "🎯 Proactivo"], horizontal=True)

    if modo_seo == "📡 Automatizado":
        if st.button("Analizar BD y Generar SEO"):
            st.warning("Conectando a base de datos...")
            # Aquí va la lógica de BD si la requieres
    elif modo_seo == "✍️ Manual":
        st.warning("Ingresa datos manualmente.")
    else:
        cluster_seo = st.text_input("Cluster objetivo:")
        if st.button("Generar Artículo Proactivo"):
            if cluster_seo:
                with st.spinner("Redactando..."):
                    articulo = generar_seo_por_intencion(cluster_seo, dolores_intermediarios=st.session_state.dolores_intermediarios, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    if articulo:
                        st.success("Generado con éxito.")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
            else:
                st.warning("Escribe la intención.")

# ==========================================
# --- PESTAÑA 5: ORQUESTADOR 360 ---
# ==========================================
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    if st.button("⚡ Lanzar Campaña 360", type="primary"):
        st.warning("Iniciando orquestación...")

# ==========================================
# --- PESTAÑA 6: HISTORIAL ---
# ==========================================
with tab_historial:
    st.subheader("📜 Historial de Contenido")
    if not supabase_ag:
        st.error("Falta conexión.")
    else:
        try:
            res = supabase_ag.table("historial_contenidos").select("*").order("fecha_creacion", desc=True).execute()
            if not res.data:
                st.info("Sin contenido.")
            else:
                for item in res.data:
                    with st.expander(f"{item.get('tipo_contenido', '')} | {item.get('titulo', '')}"):
                        st.markdown(item.get('contenido', ''))
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# --- PESTAÑA 7: COMPETENCIA ---
# ==========================================
with tab_competencia:
    st.subheader("🧠 Cerebro Competitivo")
    try:
        st.write(get_config_competencia())
    except Exception as e:
        st.warning(f"Error: {e}")

    test_comp = st.text_input("Probar contra:")
    if st.button("Generar Pitch"):
        if test_comp:
            with st.spinner("Analizando..."):
                try:
                    st.write(analizar_contra_competencia(test_comp))
                except Exception as e:
                    st.error(f"Error: {e}")

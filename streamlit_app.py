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
tab_texto, tab_whatsapp, tab_video, tab_seo, tab_360, tab_historial, tab_competencia, tab_estrategia = st.tabs([
    "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "🔥 Campaña 360", "📜 Historial", "🧠 Competencia", "⚙️ Estrategia"
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
    st.

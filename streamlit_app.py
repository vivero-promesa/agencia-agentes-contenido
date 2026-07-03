import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai

# Importación de tus agentes existentes
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo

# Importación de los nuevos agentes estructurados
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario

# ==========================================
# 0. CONFIGURACIÓN DE PÁGINA (Debe ir primero)
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# ==========================================
# 1. MANEJO PROFESIONAL DE SECRETOS
# ==========================================
load_dotenv() 

def get_secret(key):
    """Busca la llave en la nube (st.secrets); si no está, usa el .env local."""
    try:
        return st.secrets[key]
    except KeyError:
        return os.getenv(key)

# ==========================================
# 2. INICIALIZACIÓN DE CLIENTES
# ==========================================
# Supabase
try:
    url_supabase = get_secret("SUPABASE_URL")
    clave_supabase = get_secret("SUPABASE_KEY")
    supabase: Client = create_client(url_supabase, clave_supabase)
except Exception as e:
    st.error(f"Error conectando a la base de datos: {e}")
    supabase = None

# Google GenAI
try:
    client_ai = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
except Exception:
    client_ai = None

# ==========================================
# 3. MEMORIA DE ESTADOS (Session State)
# ==========================================
if "contenido_actual" not in st.session_state: st.session_state.contenido_actual = None
if "tabla_destino" not in st.session_state: st.session_state.tabla_destino = None
if "video_url_actual" not in st.session_state: st.session_state.video_url_actual = None
if "prompt_video_procesado" not in st.session_state: st.session_state.prompt_video_procesado = None

# ==========================================
# 4. ARQUITECTURA DE PESTAÑAS (Actualizada con Fases 1, 2 y 3)
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs([
    "📝 Textos y Guiones", 
    "💬 Campañas WhatsApp", 
    "🎬 Generador B-Roll (Veo 3)", 
    "🚀 SEO Programático"
])

# --- PESTAÑA 1: TEXTOS (Mantenemos original) ---
with tab_texto:
    st.subheader("Creador de Contenido Escrito (Ventas & SEO)")
    
    tipo_formato = st.selectbox("Selecciona el formato de contenido:", ["Reel/TikTok", "Artículo de Blog"], key="sb_formato")
    tema_input = st.text_input("¿De qué quieres que trate el contenido?", placeholder="Ej. Ventajas de comprar plantas ornamentales al por mayor en la Sabana", key="ti_tema")

    if st.button("Generar Contenido con IA", type="primary", key="btn_generar_texto"):
        if tema_input:
            with st.spinner("El Agente Estratega está escribiendo... 🧠"):
                try:
                    if tipo_formato == "Reel/TikTok":
                        st.session_state.contenido_actual = redactar_guion_viral(tema=tema_input, tipo_publico="B2B/B2C")
                        st.session_state.tabla_destino = "guiones"
                    else:
                        st.session_state.contenido_actual = redactar_articulo_seo(tema=tema_input)
                        st.session_state.tabla_destino = "blog_posts"
                except Exception as e:
                    st.error(f"Error de conexión con el agente de texto: {e}")
        else:
            st.warning("Por favor, ingresa un tema estratégico.")

    if st.session_state.contenido_actual:
        st.success(f"¡{tipo_formato} generado con éxito!")
        st.markdown(st.session_state.contenido_actual)
        
        st.markdown("### Sala de Aprobación")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Aprobar y Guardar en Supabase", key="btn_aprobar_texto"):
                if supabase:
                    try:
                        datos = {"tema": tema_input, "contenido": st.session_state.contenido_actual}
                        supabase.table(st.session_state.tabla_destino).insert(datos).execute()
                        st.success(f"¡Guardado exitosamente en {st.session_state.tabla_destino}!")
                        st.session_state.contenido_actual = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar texto: {e}")
                else:
                    st.error("No hay conexión a la base de datos.")
                    
        with col_b:
            if st.button("❌ Rechazar Texto", key="btn_rechazar_texto"):
                st.session_state.contenido_actual = None
                st.rerun()

# --- NUEVA PESTAÑA: CAMPAÑAS WHATSAPP (Fase 1) ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    st.write("Genera copys cortos y notas de voz para compartir directamente en grupos de viveristas.")
    
    obj_wa = st.text_input("¿Qué quieres comunicar?", placeholder="Ej. Invitarlos a subir sus suculentas a la plataforma sin costo.")
    tel_wa = st.text_input("Número de atención (formato internacional)", value="573000000000")
    
    if st.button("Generar Kit de WhatsApp", type="primary"):
        if obj_wa:
            with st.spinner("Creando copy y guion de audio..."):
                try:
                    campana = generar_campana_whatsapp(obj_wa, tel_wa)
                    if campana:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### 📱 Copy para Chat")
                            st.info(campana.mensaje_texto)
                            st.code(campana.link_wa, language="markdown")
                        
                        with col2:
                            st.markdown("### 🎙️ Guion para Nota de Voz")
                            st.success(campana.guion_nota_voz)
                            st.caption("Próximo paso: Conectar este guion a la API de ElevenLabs para generar el .mp3 automáticamente.")
                except Exception as e:
                     st.error(f"Error generando campaña: Asegúrate de tener creado el archivo agentes_crecimiento.py. Detalle: {e}")
        else:
             st.warning("Debes ingresar un objetivo para la campaña.")

# --- PESTAÑA 2: VIDEO (VEO 3) CON KIT DE EDICIÓN (Fase 2) ---
with tab_video:
    st.subheader("Agente Productor: B-Roll para Redes (Costo Cero)")
    st.write("Genera fondos cinematográficos optimizados para retención móvil.")

    if not client_ai:
        st.error("⚠️ La clave `GEMINI_API_KEY` no está configurada.")
    
    PLANTILLAS_ESTRATEGICAS = {
        "🌱 Atraer Constructoras y Paisajistas (B2B)": {
            "estilo": "Documental cinematográfico hiperrealista, grano fílmico sutil",
            "entorno": "Vivero moderno en la Sabana de Bogotá, luz dorada de amanecer, gran volumen de plantas sanas listas para despacho."
        },
        "🛒 Vender planta específica (B2C)": {
            "estilo": "Primer plano macro, cámara con paneo vertical lento",
            "entorno": "Fondo fuertemente desenfocado (bokeh), luz de estudio natural resaltando la textura de las hojas, colores vivos y orgánicos."
        },
        "📲 Promocionar la App ViveroOnline": {
            "estilo": "Plano subjetivo (POV), dinámico y moderno",
            "entorno": "Manos de un productor sosteniendo una planta de alta calidad, fondo de invernadero vibrante. Transmite eficiencia y tecnología."
        }
    }

    objetivo_seleccionado = st.selectbox("🎯 Objetivo comercial:", list(PLANTILLAS_ESTRATEGICAS.keys()))
    config_actual = PLANTILLAS_ESTRATEGICAS[objetivo_seleccionado]
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        especie_planta = st.text_input("🌿 Protagonista:", placeholder="Ej. Orquídeas, Anturios, Lote de suculentas")
    with c2:
        estilo_visual = st.text_input("🎥 Dirección (Auto):", value=config_actual["estilo"])
        
    detalles_entorno = st.text_area("🌅 Entorno (Auto):", value=config_actual["entorno"])

    if st.button("Renderizar B-Roll con Veo 3", type="primary"):
        if especie_planta:
            prompt_final_veo = (
                f"Formato vertical 9:16. {estilo_visual}. "
                f"Sujeto principal: {especie_planta}. Contexto: {detalles_entorno}. "
                f"IMPORTANTE: Dejar espacio negativo en los tercios superior e inferior. "
                f"Sin texto en pantalla, calidad 4K, texturas orgánicas."
            )
            st.session_state.prompt_video_procesado = prompt_final_veo
            
            # Lógica de reintentos (Exponential Backoff)
            max_reintentos = 3
            tiempo_espera = 30
            exito = False
            
            with st.spinner("Agente renderizando clip... 🎬"):
                for intento in range(max_reintentos):
                    try:
                        operation = client_ai.models.generate_videos(
                            model="veo-3.1-generate-preview",
                            prompt=prompt_final_veo,
                            config={"aspect_ratio": "9:16"}
                        )
                        
                        if hasattr(operation, 'generated_videos') and operation.generated_videos:
                            st.session_state.video_url_actual = operation.generated_videos[0].video.uri
                        else:
                            st.session_state.video_url_actual = operation.output
                        
                        exito = True
                        break
                        
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                            if intento < max_reintentos - 1:
                                st.toast(f"⏳ Cuota alcanzada. El agente esperará {tiempo_espera} segundos y reintentará (Intento {intento + 1}/{max_reintentos})...")
                                time.sleep(tiempo_espera)
                                tiempo_espera *= 2
                            else:
                                st.error("❌ Límite de cuota persistente. Intenta de nuevo en 1 hora.")
                        else:
                            st.error(f"Fallo crítico en Veo 3: {e}")
                            break
                
                if exito:
                    st.success("¡Clip renderizado! Listo para tus redes.")
        else:
            st.warning("⚠️ Ingresa un protagonista (ej. Planta).")

    # Integración del KIT DE EDICIÓN
    if st.session_state.video_url_actual:
        with st.expander("Ver Prompt Técnico del Agente"):
            st.code(st.session_state.prompt_video_procesado)
        
        st.video(st.session_state.video_url_actual)
        
        st.markdown("### ✂️ Kit para Editor Humano (CapCut / Premiere)")
        st.write("Descarga los activos (Assets) para realizar el ensamblaje final rápidamente.")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            # En un entorno real, descargarías el archivo. Por ahora simulamos el botón.
            st.button("📥 1. Descargar B-Roll (.mp4)", help="Clip crudo de Veo 3")
        with col_v2:
            st.button("📥 2. Descargar Locución (.mp3)", help="Audio generado de tu guion")
        with col_v3:
            st.button("📥 3. Descargar Subtítulos (.srt)", help="Tiempos exactos para incrustar")
            
        st.info("💡 **Flujo sugerido:** Arrastra estos 3 archivos a CapCut. Añade la canción en tendencia, ajusta cortes si es necesario y exporta. Tiempo estimado: 2 minutos.")
        
        if st.button("🗑️ Limpiar clip actual", key="btn_limpiar_clip"):
            st.session_state.video_url_actual = None
            st.rerun()

# --- NUEVA PESTAÑA: SEO PROGRAMÁTICO (Fase 3) ---
with tab_seo:
    st.subheader("Crecimiento Impulsado por Oferta")
    st.write("Simulación del Trigger: Detecta automáticamente nuevos ingresos masivos de inventario y genera artículos para captar demanda.")
    
    datos_mock_supabase = {
        "especie": "Orquídeas Phalaenopsis (Colores Mixtos)",
        "cantidad": 500,
        "ubicacion": "Cajicá",
        "vendedor": "Vivero El Edén"
    }
    
    st.json(datos_mock_supabase)
    
    if st.button("Ejecutar Trigger SEO", type="primary"):
        with st.spinner("Analizando inventario y redactando artículo de indexación..."):
            try:
                articulo = generar_seo_desde_inventario(datos_mock_supabase)
                
                if articulo:
                    st.success("Artículo generado y listo para publicar en el CMS.")
                    st.markdown(f"**H1:** {articulo.titulo_h1}")
                    st.caption(f"**Slug:** /{articulo.slug}")
                    st.markdown(f"**Meta:** {articulo.meta_description}")
                    st.markdown("---")
                    st.markdown(articulo.contenido_md)
                    
                    if st.button("🚀 Auto-Publicar en Blog (Simulado)"):
                        st.balloons()
                        st.toast("El artículo ha sido inyectado en la base de datos de producción.")
            except Exception as e:
                st.error(f"Error en el agente SEO: Asegúrate de tener creado el archivo agentes_crecimiento.py. Detalle: {e}")

# Importación del motor de audio (Añade esta línea junto a tus otros imports)
from agente_audio import generar_audio_elevenlabs

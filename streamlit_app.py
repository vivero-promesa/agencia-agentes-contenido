import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai

# Importación de tus agentes existentes
from agente import redactar_guion_viral
from agente_blog import redactar_articulo_seo

# 1. Configuración y conexión
load_dotenv()
url_supabase = os.getenv("SUPABASE_URL")
clave_supabase = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, clave_supabase)

# Inicialización segura del cliente Google GenAI
# Busca automáticamente la variable GEMINI_API_KEY en el entorno o en st.secrets
try:
    client_ai = genai.Client()
except Exception:
    client_ai = None

st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

# 2. Inicializar memoria de estados (Session State)
# Estados para la pestaña de Textos
if "contenido_actual" not in st.session_state:
    st.session_state.contenido_actual = None
if "tabla_destino" not in st.session_state:
    st.session_state.tabla_destino = None

# Estados para la pestaña de Video (Evita que el video desaparezca al redibujar la UI)
if "video_url_actual" not in st.session_state:
    st.session_state.video_url_actual = None
if "prompt_video_procesado" not in st.session_state:
    st.session_state.prompt_video_procesado = None

# 3. Arquitectura de Pestañas
tab_texto, tab_video = st.tabs(["📝 Textos y Guiones", "🎬 Generador de Video (Veo 3)"])

# ==========================================
# PESTAÑA 1: GENERACIÓN DE TEXTO (Tu lógica original intacta)
# ==========================================
with tab_texto:
    st.subheader("Creador de Contenido Escrito")
    
    tipo_formato = st.selectbox("Selecciona el formato de contenido:", ["Reel/TikTok", "Artículo de Blog"], key="sb_formato")
    tema_input = st.text_input("¿De qué quieres que trate el contenido?", key="ti_tema")

    if st.button("Generar Contenido con IA", type="primary", key="btn_generar_texto"):
        if tema_input:
            with st.spinner("Conectando con la IA... 🧠"):
                if tipo_formato == "Reel/TikTok":
                    st.session_state.contenido_actual = redactar_guion_viral(tema=tema_input, tipo_publico="B2C")
                    st.session_state.tabla_destino = "guiones"
                else:
                    st.session_state.contenido_actual = redactar_articulo_seo(tema=tema_input)
                    st.session_state.tabla_destino = "blog_posts"
        else:
            st.warning("Por favor, ingresa un tema.")

    # Zona de revisión y guardado inteligente para Texto
    if st.session_state.contenido_actual:
        st.success(f"¡{tipo_formato} generado con éxito!")
        st.markdown(st.session_state.contenido_actual)
        
        st.markdown("### ¿Qué deseas hacer?")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Aprobar y Guardar Texto", key="btn_aprobar_texto"):
                try:
                    datos = {"tema": tema_input, "contenido": st.session_state.contenido_actual}
                    supabase.table(st.session_state.tabla_destino).insert(datos).execute()
                    
                    st.success(f"¡Guardado exitosamente en {st.session_state.tabla_destino}!")
                    st.session_state.contenido_actual = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar text: {e}")
                    
        with col_b:
            if st.button("❌ Rechazar Texto", key="btn_rechazar_texto"):
                st.session_state.contenido_actual = None
                st.rerun()

# ==========================================
# PESTAÑA 2: GENERACIÓN DE VIDEO (Integración Veo 3)
# ==========================================
with tab_video:
    st.subheader("Generación de Clips con Google Veo 3")
    st.write("Construye videos cinemáticos de alta fidelidad optimizados para el catálogo digital o estados de WhatsApp.")

    if not client_ai:
        st.error("⚠️ La clave `GEMINI_API_KEY` no está configurada o el SDK no se pudo inicializar. Verifica tus credenciales.")
    
    # Parámetros estructurados para mitigar prompts débiles y proteger créditos
    c1, c2 = st.columns(2)
    with c1:
        especie_planta = st.text_input("Especie o producto objetivo:", placeholder="Ej. Sansevieria Trifasciata, Anturio Negro")
    with c2:
        estilo_visual = st.selectbox(
            "Enfoque y estilo óptico:",
            [
                "Cinematográfico (Macro, iluminación natural tenue)", 
                "Primer plano extremo (Detalle de textura de hojas y follaje)", 
                "Toma aérea comercial (Paneo lento sobre camas de cultivo)", 
                "Estilo documental agrícola (Cámara en mano, luz de mañana)"
            ]
        )
        
    detalles_entorno = st.text_area(
        "Detalles específicos del entorno y atmósfera:",
        placeholder="Ej. Gotas de rocío sobre los pétalos, fondo desenfocado (bokeh), invernadero tradicional de la Sabana de Bogotá al atardecer."
    )

    if st.button("Generar Clip con Veo 3", type="primary", key="btn_generar_video"):
        if especie_planta:
            # Ingeniería de prompt controlada en backend
            prompt_final_veo = (
                f"Video promocional de alta resolución. {estilo_visual}. "
                f"Enfoque principal en la planta: {especie_planta}. "
                f"Detalles de la escena: {detalles_entorno}. "
                f"Fotorrealista, texturas orgánicas nítidas, colores vivos saturados naturales, 4k."
            )
            
            st.session_state.prompt_video_procesado = prompt_final_veo
            
            with st.spinner("Orquestando generación en Google Veo 3... (Este proceso toma entre 1 y 2 minutos) 🎬"):
                try:
                    # Llamada a la API oficial de Google GenAI para generación de video
                    operation = client_ai.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt_final_veo,
                        config={"aspect_ratio": "9:16"} # Forzado nativo para Reels/WhatsApp
                    )
                    
                    # Extraer el recurso generado desde los metadatos de la operación completada
                    # Nota: Dependiendo de la estructura exacta del payload del preview, ajustamos el binding
                    if hasattr(operation, 'generated_videos') and operation.generated_videos:
                        st.session_state.video_url_actual = operation.generated_videos[0].video.uri
                    else:
                        st.session_state.video_url_actual = operation.output
                        
                except Exception as e:
                    st.error(f"Fallo en el servicio de Vertex AI / AI Studio: {e}")
        else:
            st.warning("Debes especificar la especie o planta objetivo para estructurar el prompt.")

    # Renderizado y Persistencia del Video Generado
    if st.session_state.video_url_actual:
        st.success("¡Video renderizado por Veo 3 con éxito!")
        
        # Mostrar el prompt exacto utilizado bajo auditoría técnica
        st.info(f"**Prompt técnico ejecutado:** *{st.session_state.prompt_video_procesado}*")
        
        # Reproductor nativo de Streamlit
        st.video(st.session_state.video_url_actual)
        
        st.markdown("### Acciones de Operación Multimedia")
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            if st.button("💾 Guardar Metadata en Supabase", key="btn_guardar_video"):
                try:
                    # Estructura opcional por si deseas persistir la URL generada en tu base de datos
                    datos_video = {
                        "tema": especie_planta,
                        "contenido": f"Prompt: {st.session_state.prompt_video_procesado} | URL: {st.session_state.video_url_actual}"
                    }
                    supabase.table("guiones").insert(datos_video).execute()
                    st.success("Referencia de video guardada exitosamente en la tabla 'guiones'.")
                except Exception as err:
                    st.error(f"No se pudo indexar el video en Supabase: {err}")
                    
        with col_v2:
            if st.button("🗑️ Limpiar Espacio de Trabajo", key="btn_limpiar_video"):
                st.session_state.video_url_actual = None
                st.session_state.prompt_video_procesado = None
                st.rerun()

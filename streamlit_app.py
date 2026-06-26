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
# PESTAÑA 2: GENERACIÓN DE VIDEO (Plantillas Inteligentes)
# ==========================================
with tab_video:
    st.subheader("Generación Estratégica de B-Roll (Google Veo 3)")
    st.write("Selecciona tu objetivo comercial. El sistema configurará automáticamente la dirección de fotografía para maximizar la conversión.")

    if not client_ai:
        st.error("⚠️ La clave `GEMINI_API_KEY` no está configurada o el SDK no se pudo inicializar.")
    
    # 1. El "Cerebro" de las Plantillas (Cero costo de tokens)
    PLANTILLAS_ESTRATEGICAS = {
        "🌱 Conseguir nuevos viveristas": {
            "estilo": "Estilo documental agrícola (Cámara en mano, luz de mañana)",
            "entorno": "Vivero moderno y organizado en la Sabana de Bogotá, sensación de abundancia y negocio próspero, agricultor revisando plantas de forma profesional."
        },
        "🛒 Vender una planta específica": {
            "estilo": "Primer plano extremo (Detalle de textura de hojas y follaje)",
            "entorno": "Gotas de rocío sobre los pétalos, fondo muy desenfocado (efecto bokeh) para resaltar el producto, iluminación de estudio natural."
        },
        "🏡 Promocionar el Vivero (Institucional)": {
            "estilo": "Toma aérea comercial (Paneo lento sobre camas de cultivo)",
            "entorno": "Invernaderos limpios y extensos, luz de atardecer dorada, simetría en la organización de las macetas, ambiente de confianza B2B."
        },
        "📦 Lanzamiento de inventario": {
            "estilo": "Cinematográfico (Movimiento dinámico rápido, colores vivos)",
            "entorno": "Múltiples especies agrupadas, colores altamente saturados y vibrantes, sensación de abundancia y novedad, luz brillante."
        },
        "🎄 Campañas estacionales (Día de la Madre/Navidad)": {
            "estilo": "Cinematográfico (Iluminación cálida y emocional)",
            "entorno": "Plantas decorativas de temporada, atmósfera festiva y acogedora, colores de contraste suaves, ideal para regalo."
        }
    }

    # 2. Interfaz de Selección Rápida
    objetivo_seleccionado = st.selectbox(
        "🎯 ¿Cuál es el objetivo comercial de este clip?", 
        list(PLANTILLAS_ESTRATEGICAS.keys())
    )
    
    st.markdown("---")
    
    # Cargar los parámetros óptimos según la elección
    config_actual = PLANTILLAS_ESTRATEGICAS[objetivo_seleccionado]
    
    c1, c2 = st.columns(2)
    with c1:
        especie_planta = st.text_input("🌿 Especie o elemento protagonista:", placeholder="Ej. Orquídeas, Invernadero general, Anturios")
    with c2:
        estilo_visual = st.text_input("🎥 Dirección de cámara (Auto-configurado):", value=config_actual["estilo"])
        
    detalles_entorno = st.text_area("🌅 Detalles del entorno (Auto-configurado):", value=config_actual["entorno"])

    # 3. Motor de Generación
    if st.button("Generar B-Roll con Veo 3", type="primary", key="btn_generar_video_v2"):
        if especie_planta:
            # Ensamblaje del prompt técnico perfecto sin que el usuario sufra
            prompt_final_veo = (
                f"Video promocional hiperrealista 4K. {estilo_visual}. "
                f"Sujeto principal: {especie_planta}. "
                f"Contexto y atmósfera: {detalles_entorno}. "
                f"Calidad cinematográfica, sin textos, texturas orgánicas nítidas."
            )
            
            st.session_state.prompt_video_procesado = prompt_final_veo
            
            with st.spinner("Renderizando clip cinemático... (Toma ~1 minuto) 🎬"):
                try:
                    operation = client_ai.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt_final_veo,
                        config={"aspect_ratio": "9:16"} # Listo para Reels, TikTok y WhatsApp
                    )
                    
                    if hasattr(operation, 'generated_videos') and operation.generated_videos:
                        st.session_state.video_url_actual = operation.generated_videos[0].video.uri
                    else:
                        st.session_state.video_url_actual = operation.output
                        
                except Exception as e:
                    st.error(f"Fallo en la API de Google: {e}")
        else:
            st.warning("⚠️ Ingresa una especie o protagonista para disparar la generación.")

    # 4. Renderizado Final
    if st.session_state.video_url_actual:
        st.success("¡B-Roll renderizado con éxito! Descárgalo y únelo a tus textos en WhatsApp o Instagram.")
        with st.expander("Ver configuración técnica del Prompt (Modo Dios)"):
            st.code(st.session_state.prompt_video_procesado)
        
        st.video(st.session_state.video_url_actual)

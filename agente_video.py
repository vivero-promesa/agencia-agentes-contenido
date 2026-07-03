import streamlit as st
from google import genai
import json

def get_video_client():
    """Inicializa de forma segura el cliente oficial de Google GenAI."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración en las llaves de Google AI: {e}")
        return None

def optimizar_prompt_produccion(escena_data):
    """
    Agente Productor: Toma la definición humana de la escena y la traduce
    a un prompt de ingeniería visual ultra-detallado para Veo 3.1.
    """
    # Inyección de estándares B2B "AgTech de Tierra"
    prompt_base = (
        f"Estilo: Documental cinematográfico industrial, hiperrealista, resolución 4K. "
        f"Formato: Vertical 9:16. "
        f"Contexto: Operación logística de vivero mayorista (AgTech). "
        f"Sujeto principal y acción: {escena_data.get('visual', 'operación de carga')}. "
        f"Atmósfera: {escena_data.get('emocion', 'profesional y eficiente')}, luz natural de la Sabana, colores orgánicos vivos. "
        f"Cámara: {escena_data.get('camara', 'Plano detalle, movimiento suave de estabilizador')}. "
        f"Regla estricta: NO incluir texto en el video. Dejar tercio inferior despejado para subtítulos."
    )
    return prompt_base

def generar_video_escena(id_escena, prompt_tecnico):
    """Llama a la API de Google Veo 3.1 para generar el B-Roll."""
    client = get_video_client()
    if not client:
        return None

    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt_tecnico,
            config={
                "aspect_ratio": "9:16",
                "duration_seconds": 5 # Control de ritmo para redes sociales
            }
        )
        
        # Extracción segura de la URI del video
        if hasattr(operation, 'generated_videos') and operation.generated_videos:
            return operation.generated_videos[0].video.uri
        return getattr(operation, 'output', None)

    except Exception as e:
        st.error(f"Error generando render para la escena {id_escena}: {e}")
        return None

def ejecutar_pipeline_agencia(storyboard_json):
    """
    Orquestador de la Agencia: Procesa todo el comercial secuencialmente.
    """
    try:
        storyboard = json.loads(storyboard_json)
    except json.JSONDecodeError:
        st.error("El formato del storyboard no es un JSON válido.")
        return {}

    resultados = {}

    for clave, escena in storyboard.items():
        st.write(f"🎬 **Renderizando: {escena.get('nombre', clave)}**")
        
        if escena.get("tipo") == "IA_GENERATIVE":
            prompt_listo = optimizar_prompt_produccion(escena)
            st.caption(f"🤖 *Prompt enviado a Veo 3.1:* {prompt_listo}")
            
            url_video = generar_video_escena(clave, prompt_listo)
            resultados[clave] = {"status": "Listo", "url": url_video, "texto": escena.get("texto", "")}
            
        elif escena.get("tipo") == "UI_RECORDING":
            st.info(f"📱 *Nota:* Esta escena requiere grabación de pantalla de app.viveroonline.com.co.")
            resultados[clave] = {"status": "Requiere_Media_Local", "texto": escena.get("texto", "")}
            
    return resultados

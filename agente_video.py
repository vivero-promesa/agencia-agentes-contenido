import streamlit as st
from google import genai
import json

def get_video_client():
    """Inicializa de forma segura el cliente oficial de Google GenAI."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración en las llaves de Google AI: {e}")
        return None

def optimizar_prompt_produccion(escena_data):
    """
    Agente Productor: Toma la definición humana de la escena y la traduce
    a un prompt de ingeniería visual ultra-detallado para Veo 3.1.
    """
    # Inyección automática de estándares de retención y edición de redes sociales
    prompt_base = (
        f"Estilo: Documental cinematográfico hiperrealista, grano fílmico sutil, resolución 4K. "
        f"Formato: Vertical 9:16 para redes sociales. "
        f"Sujeto principal y acción: {escena_data['visual']}. "
        f"Atmósfera y emociones: {escena_data['emocion']}, iluminación natural profunda, colores orgánicos vivos. "
        f"Dirección de cámara: {escena_data.get('camara', 'Plano fijo con micro-movimiento orgánico')}. "
        f"Composición de marketing: Dejar el tercio superior y el tercio inferior completamente despejados "
        f"(espacio negativo con desenfoque cinematográfico bokeh) para superposición de subtítulos dinámicos."
    )
    return prompt_base

def generar_video_escena(id_escena, prompt_tecnico):
    """Llama a la API de Google para generar el fragmento de video (B-Roll)."""
    client = get_video_client()
    if not client:
        return None

    try:
        # Usando el endpoint de previsualización activa del ecosistema de Google
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt_tecnico,
            config={
                "aspect_ratio": "9:16",
                "duration_seconds": 5 # Duración estándar por fragmento de IA para control de ritmo
            }
        )
        
        if hasattr(operation, 'generated_videos') and operation.generated_videos:
            return operation.generated_videos[0].video.uri
        return getattr(operation, 'output', None)

    except Exception as e:
        st.error(f"Error generando escena {id_escena}: {e}")
        return None

def ejecutar_pipeline_agencia(storyboard_json):
    """
    Orquestador de la Agencia: Procesa todo el comercial secuencialmente
    gestionando qué activos son de IA y cuáles son interactivos.
    """
    storyboard = json.loads(storyboard_json)
    resultados = {}

    for clave, escena in storyboard.items():
        st.write(f"🎬 **Procesando {escena['nombre']} ({escena['tiempo']})**")
        
        if escena["tipo"] == "IA_GENERATIVE":
            prompt_listo = optimizar_prompt_produccion(escena)
            st.caption(f"🤖 *Prompt optimizado por el agente:* {prompt_listo}")
            
            # Simulación de render o llamada activa
            url_video = generar_video_escena(clave, prompt_listo)
            resultados[clave] = {"status": "Listo", "url": url_video, "texto": escena["texto"]}
            
        elif escena["tipo"] == "UI_RECORDING":
            st.info(f"📱 *Nota de Producción:* Esta escena requiere una grabación de pantalla real de app.viveroonline.com.co para garantizar confianza técnica. Sube el archivo correspondiente.")
            resultados[clave] = {"status": "Requiere_Media_Local", "texto": escena["texto"]}
            
    return resultados

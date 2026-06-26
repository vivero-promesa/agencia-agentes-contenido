import streamlit as st
from google import genai
import time

def get_video_client():
    """
    Inicializa el cliente de Google GenAI de forma segura.
    Retorna el cliente o lanza una excepción si la llave no existe.
    """
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración de Google AI Studio: {e}")
        return None

def generar_broll_veo(especie, estilo, entorno):
    """
    Agente encargado de generar B-Roll con Veo 3.
    Recibe los parámetros, construye el prompt y gestiona la llamada a la API.
    """
    client = get_video_client()
    if not client:
        return None, "Error: Cliente de Google no inicializado."

    # Prompt técnico optimizado para Veo 3
    prompt_final = (
        f"Video promocional hiperrealista 4K. {estilo}. "
        f"Sujeto principal: {especie}. "
        f"Contexto y atmósfera: {entorno}. "
        f"Calidad cinematográfica, texturas orgánicas nítidas, colores vivos."
    )

    try:
        # Llamada asíncrona a la API de generación de video
        # Nota: Ajusta 'model' según el endpoint activo en tu consola de Google
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt_final,
            config={"aspect_ratio": "9:16"}
        )
        
        # Extraer la URL de la respuesta
        if hasattr(operation, 'generated_videos') and operation.generated_videos:
            return operation.generated_videos[0].video.uri, prompt_final
        else:
            return operation.output, prompt_final

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return None, "CUOTA_AGOTADA"
        return None, f"Error en API Veo: {error_msg}"

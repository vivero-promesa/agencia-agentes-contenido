import streamlit as st
from google import genai

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

def generar_broll_vivero(especie_o_producto, beneficio_clave, entorno, estilo="Cinematográfico"):
    """
    Agente director de arte para Veo.
    Traduce objetivos de negocio en prompts visuales para ViveroOnline.
    """
    client = get_video_client()
    if not client:
        return None, "Error: Cliente de Google no inicializado."

    # PROMPT DE AGENCIA: Estructurado para guiar al modelo visualmente
    # 1. Formato y Estilo Visual
    # 2. Sujeto y Acción (El Gancho)
    # 3. Contexto (La Solución/Beneficio)
    # 4. Composición (Espacio para el marketing)
    
    prompt_final = (
        f"Estilo visual: {estilo}, hiperrealista, resolución 4K, formato vertical. "
        f"Sujeto: Primer plano detallado de {especie_o_producto} vibrante y de alta calidad. "
        f"Acción y Movimiento: La cámara hace un paneo suave y fluido desde la planta hacia "
        f"un entorno de {entorno}. "
        f"Atmósfera: Iluminación natural dorada que transmite {beneficio_clave} y profesionalismo. "
        f"Composición: Texturas orgánicas nítidas, colores vivos pero naturales. "
        f"Importante: Dejar espacio negativo (desenfocado suavemente) en el tercio superior e inferior para permitir la superposición de texto publicitario."
    )

    try:
        # Llamada asíncrona a la API de generación de video
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
            return None, "CUOTA_AGOTADA: Limite de generación gratuita alcanzado. Intenta más tarde."
        return None, f"Error en API Veo: {error_msg}"

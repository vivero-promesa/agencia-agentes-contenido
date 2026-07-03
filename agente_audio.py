import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def generar_audio_elevenlabs(texto: str, voice_id: str = "pNInz6obpgDQGcFmaJZA") -> bytes | None:
    """
    Sintetiza texto a voz usando ElevenLabs API.
    Nota: El voice_id por defecto es 'Adam'. Puedes cambiarlo por el ID de 
    una voz colombiana cálida que hayas clonado previamente.
    """
    # Buscar la llave de ElevenLabs
    api_key = st.secrets.get("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY"))
    
    if not api_key:
        st.error("⚠️ Falta la llave ELEVENLABS_API_KEY en tus secretos.")
        return None
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2", # Fundamental para buen español
        "voice_settings": {
            "stability": 0.5, # 0.5 da un tono conversacional y natural
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content # Retorna los bytes del archivo mp3
        else:
            st.error(f"Error de ElevenLabs: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error de conexión con ElevenLabs: {e}")
        return None

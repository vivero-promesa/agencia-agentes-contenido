import asyncio
import re
import edge_tts
import io

def generar_audio_edge(texto_guion: str) -> bytes | None:
    """
    Genera audio usando edge-tts (Voz Salomé - Colombia) sin necesidad de API externa.
    """
    # 1. Limpieza estratégica (Mantenemos tu lógica robusta)
    texto_limpio = texto_guion.replace('--- PREGUNTA CENTRAL ---', '').replace('--- CONFLICTO ---', '')
    texto_limpio = re.sub(r'\[.*?\]', '', texto_limpio)
    texto_limpio = texto_limpio.replace('*', '')
    texto_limpio = re.sub(r'(?i)\bnarrador\b[:,]?\s*', '', texto_limpio).strip()
    
    if not texto_limpio:
        return None

    VOICE = "es-CO-SalomeNeural"
    
    # 2. Función asíncrona optimizada para retornar bytes en memoria
    async def generar_en_memoria():
        communicate = edge_tts.Communicate(texto_limpio, VOICE, rate="+5%") # Ligeramente más rápido para redes sociales
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        return audio_data.getvalue()

    try:
        # Ejecutamos el bucle de eventos
        return asyncio.run(generar_en_memoria())
    except Exception as e:
        print(f"Error en edge-tts: {e}")
        return None

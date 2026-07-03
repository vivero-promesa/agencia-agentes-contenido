import asyncio
import re
import edge_tts
import io

def generar_audio_elevenlabs(texto_guion: str) -> bytes | None:
    # Limpieza básica
    texto_limpio = re.sub(r'\[.*?\]|\*|---.*?---', '', texto_guion).strip()
    
    if not texto_limpio:
        return None

    VOICE = "es-CO-SalomeNeural"
    
    async def generar():
        communicate = edge_tts.Communicate(texto_limpio, VOICE, rate="+5%")
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        return audio_data.getvalue()

    try:
        return asyncio.run(generar())
    except Exception as e:
        print(f"Error en audio: {e}")
        return None

import asyncio
import re
import edge_tts
import io

def generar_audio_elevenlabs(texto_guion: str) -> bytes | None:
    # 1. Limpieza estratégica
    texto_limpio = re.sub(r'\[.*?\]|\*|---.*?---', '', texto_guion).strip()
    
    if not texto_limpio:
        return None

    # Voz masculina colombiana con tono de autoridad y cercanía
    VOICE = "es-CO-GonzaloNeural"
    
    async def generar():
        # Tono persuasivo pero pausado y natural
        communicate = edge_tts.Communicate(
            texto_limpio, 
            VOICE, 
            rate="+0%",  # Ritmo de conversación natural
            pitch="-2Hz" # Un tono ligeramente más grave para dar más autoridad de "viverista"
        )
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        return audio_data.getvalue()

    try:
        return asyncio.run(generar())
    except Exception as e:
        print(f"Error en motor de voz masculina: {e}")
        return None

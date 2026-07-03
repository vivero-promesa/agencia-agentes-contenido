import asyncio
import re
import edge_tts
import io

def generar_audio_elevenlabs(texto_guion: str) -> bytes | None:
    # 1. Limpieza de metadatos del guion
    texto_limpio = re.sub(r'\[.*?\]|\*|---.*?---', '', texto_guion).strip()
    
    if not texto_limpio:
        return None

    # Usamos la voz Salomé, que es la más natural y persuasiva para Colombia.
    # Ajustamos la velocidad (rate) y el tono (pitch) para que suene más humana y energética.
    # rate="+10%": Un poco más rápido para mantener la atención.
    # pitch="+2Hz": Un tono ligeramente más alto transmite energía y entusiasmo.
    VOICE = "es-CO-SalomeNeural"
    
    async def generar():
        # Configuramos una velocidad y tono que suene a "negocio serio pero cercano"
        communicate = edge_tts.Communicate(
            texto_limpio, 
            VOICE, 
            rate="+10%", 
            pitch="+2Hz"
        )
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        return audio_data.getvalue()

    try:
        return asyncio.run(generar())
    except Exception as e:
        print(f"Error en motor de voz persuasiva: {e}")
        return None

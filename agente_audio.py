import asyncio
import re
import edge_tts
import io

def generar_audio_elevenlabs(texto_guion: str) -> bytes | None:
    # 1. Limpieza de texto
    texto_limpio = re.sub(r'\[.*?\]|\*|---.*?---', '', texto_guion).strip()
    
    if not texto_limpio:
        return None

    # Gonzalo es nuestra mejor voz para cerrar negocios
    VOICE = "es-CO-GonzaloNeural"
    
    async def generar():
        # Ajuste Pro:
        # rate="+15%": Velocidad ideal para que el receptor sienta urgencia pero no pierda detalle.
        # pitch="+0Hz": Mantener el tono natural pero firme.
        communicate = edge_tts.Communicate(
            texto_limpio, 
            VOICE, 
            rate="+15%", 
            pitch="+0Hz"
        )
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        return audio_data.getvalue()

    try:
        return asyncio.run(generar())
    except Exception as e:
        print(f"Error en motor de voz rápida: {e}")
        return None

from openai import OpenAI

# --- BYPASS DE SEGURIDAD ---
# Pega tu clave real aquí adentro de las comillas:
clave_api = "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"

print("✅ Bypass activado. Encendiendo motores...")

# Conexión al motor Llama 3 (Groq)
client = OpenAI(
    api_key=clave_api,
    base_url="https://api.groq.com/openai/v1"
)

def redactar_guion_viral(tema, tipo_publico):
    instrucciones = f"""
    Eres el Director Creativo de una agencia de contenido en Silicon Valley.
    Tu misión es crear guiones cortos (Reels/TikToks) altamente virales.
    
    Tema del video: {tema}
    Público objetivo: {tipo_publico}
    
    Reglas:
    1. Primeros 3 segundos: Un gancho visual y narrativo brutal.
    2. Desarrollo: Valor directo.
    3. Cierre: Llamado a la acción claro.
    
    Devuelve SOLO el guion estructurado.
    """
    
    print(f"🔌 Procesando: '{tema}'...")
    
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[{"role": "user", "content": instrucciones}]
    )
    return respuesta.choices[0].message.content

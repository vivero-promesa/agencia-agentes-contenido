import streamlit as st
from google import genai
from google.genai import types
import json
import time
import random

from brand_book import GUIA_VISUAL_VIDEO


def get_video_client():
    """Inicializa de forma segura el cliente oficial de Google GenAI."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error de configuración en las llaves de Google AI: {e}")
        return None


def optimizar_prompt_produccion(escena_data):
    """
    Agente Productor: Toma la definición humana de la escena y la traduce
    a un prompt de ingeniería visual para Veo 3.1, anclado al Brand Book
    real de ViveroOnline (vivero familiar de la Sabana de Bogotá), no a
    una estética genérica de bodega industrial.
    """
    prompt_base = (
        f"Sujeto principal y acción: {escena_data.get('visual', 'trabajo diario en el vivero')}. "
        f"Atmósfera: {escena_data.get('emocion', 'cercana, tranquila, auténtica')}. "
        f"Cámara: {escena_data.get('camara', 'plano medio, movimiento suave de estabilizador')}. "
        f"{GUIA_VISUAL_VIDEO.strip()} "
        f"Regla estricta: NO incluir texto en el video. Dejar tercio inferior despejado para subtítulos."
    )
    return prompt_base


def _es_error_de_cuota(excepcion) -> bool:
    texto = str(excepcion)
    return "RESOURCE_EXHAUSTED" in texto or "429" in texto


def generar_video_escena(id_escena, prompt_tecnico, duracion_segundos=8, max_reintentos=4):
    """
    Llama a la API de Google Veo 3.1 para generar el B-Roll.

    Notas técnicas:
    - La generación de video es ASÍNCRONA (long-running operation) — se espera
      (poll) con operation.done hasta que termina antes de leer el resultado.
    - duracion_segundos debe estar entre 4 y 8 (límite de la API), se acota
      automáticamente.
    - Ante error 429 (RESOURCE_EXHAUSTED / límite de cuota), reintenta con
      backoff exponencial + jitter hasta max_reintentos veces. Si la cuota
      está agotada por completo (no es un límite transitorio por minuto),
      los reintentos no ayudan — hay que revisar la facturación en
      https://ai.dev/rate-limit.
    """
    client = get_video_client()
    if not client:
        return None

    duracion_segundos = max(4, min(8, duracion_segundos))
    espera_base = 15  # segundos

    for intento in range(max_reintentos + 1):
        try:
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt_tecnico,
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    duration_seconds=duracion_segundos,
                )
            )

            with st.spinner(f"Renderizando escena {id_escena}... esto puede tardar unos minutos"):
                while not operation.done:
                    time.sleep(10)
                    operation = client.operations.get(operation)

            if operation.response and operation.response.generated_videos:
                return operation.response.generated_videos[0].video.uri

            if operation.error:
                st.error(f"Veo 3.1 no pudo renderizar la escena {id_escena}: {operation.error}")

            return None

        except Exception as e:
            if _es_error_de_cuota(e) and intento < max_reintentos:
                espera = espera_base * (2 ** intento) + random.uniform(0, 3)
                st.warning(
                    f"⏳ Límite de cuota alcanzado en escena {id_escena}. "
                    f"Reintentando en {int(espera)}s (intento {intento + 1}/{max_reintentos})..."
                )
                time.sleep(espera)
                continue

            if _es_error_de_cuota(e):
                st.error(
                    f"❌ Escena {id_escena}: se agotaron los reintentos por límite de cuota (429). "
                    f"Si esto persiste, es cuota agotada (no un límite transitorio) — revisa tu plan "
                    f"de facturación en https://ai.dev/rate-limit."
                )
                return None

            st.error(f"Error generando render para la escena {id_escena}: {e}")
            return None

    return None


def ejecutar_pipeline_agencia(storyboard_json):
    """
    Orquestador de la Agencia: Procesa todo el comercial secuencialmente.
    """
    try:
        storyboard = json.loads(storyboard_json)
    except json.JSONDecodeError:
        st.error("El formato del storyboard no es un JSON válido.")
        return {}

    resultados = {}

    for clave, escena in storyboard.items():
        st.write(f"🎬 **Renderizando: {escena.get('nombre', clave)}**")

        if escena.get("tipo") == "IA_GENERATIVE":
            prompt_listo = optimizar_prompt_produccion(escena)
            st.caption(f"🤖 *Prompt enviado a Veo 3.1:* {prompt_listo}")

            url_video = generar_video_escena(clave, prompt_listo)
            resultados[clave] = {"status": "Listo", "url": url_video, "texto": escena.get("texto", "")}

        elif escena.get("tipo") == "UI_RECORDING":
            st.info(f"📱 *Nota:* Esta escena requiere grabación de pantalla de app.viveroonline.com.co.")
            resultados[clave] = {"status": "Requiere_Media_Local", "texto": escena.get("texto", "")}

    return resultados

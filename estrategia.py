"""
estrategia.py — Configuración estratégica dinámica de ViveroOnline.

A diferencia de identidad_marca.py (tono/voz, cambia poco) y brand_book.py
(identidad visual, cambia poco), este módulo lee y escribe en Supabase —
pensado para contenido de negocio que SÍ cambia seguido o que se escribe a
mano (prioridad del momento, dolores frente a la competencia, etc.), sin
necesidad de tocar código ni esperar un redeploy.

Tabla esperada en el proyecto Supabase de la Agencia: configuracion_estrategica
  - clave (text, primary key)
  - valor (text)
  - actualizado_en (timestamp)

Claves en uso:
  - "prioridad_actual": prioridad de negocio del momento (ver README_ESTRATEGIA.md)
  - "dolores_intermediarios": dolores del viverista frente a intermediarios
    tradicionales, escritos a mano por el usuario (no generados por IA, para
    evitar que un agente invente quejas o competidores que no son reales)
"""

CLAVE_PRIORIDAD_DEFAULT = "prioridad_actual"
CLAVE_DOLORES_INTERMEDIARIOS = "dolores_intermediarios"
CLAVE_ESTRATEGIA_COMPETITIVA = "estrategia_competitiva"

VALOR_FALLBACK_PRIORIDAD = (
    "Posicionamiento de categoría (Océano Azul): ViveroOnline es la "
    "plataforma inteligente de abastecimiento ornamental y soluciones "
    "verdes para proyectos urbanos, paisajísticos y arquitectónicos — "
    "nunca vivero, e-commerce, directorio o marketplace tradicional."
)

VALOR_FALLBACK_DOLORES = ""  # vacío a propósito: si no se ha escrito nada, ningún agente debe inventar dolores/competidores
VALOR_FALLBACK_COMPETENCIA = ""  # vacío a propósito: nunca inventar competidores — si está vacío, el agente debe decirlo, no inventar "Vivero X"

_FALLBACKS_POR_CLAVE = {
    CLAVE_PRIORIDAD_DEFAULT: VALOR_FALLBACK_PRIORIDAD,
    CLAVE_DOLORES_INTERMEDIARIOS: VALOR_FALLBACK_DOLORES,
    CLAVE_ESTRATEGIA_COMPETITIVA: VALOR_FALLBACK_COMPETENCIA,
}


def obtener_prioridad_estrategica(supabase_client, clave: str = CLAVE_PRIORIDAD_DEFAULT) -> str:
    """
    Lee un valor de configuración estratégica desde Supabase (por clave).
    Si no hay cliente, la tabla no existe, o la consulta falla, devuelve el
    fallback correspondiente a esa clave — los agentes nunca deben quedarse
    sin ninguna guía por un error de conexión, ni inventar contenido que
    debía ser escrito a mano (como los dolores frente a intermediarios).
    """
    fallback = _FALLBACKS_POR_CLAVE.get(clave, "")

    if not supabase_client:
        return fallback

    try:
        resp = (
            supabase_client.table("configuracion_estrategica")
            .select("valor")
            .eq("clave", clave)
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]["valor"]
        return fallback
    except Exception as e:
        print(f"Error leyendo estrategia desde Supabase: {e}")
        return fallback


def guardar_prioridad_estrategica(supabase_client, valor: str, clave: str = CLAVE_PRIORIDAD_DEFAULT) -> bool:
    """
    Guarda (upsert) un valor de configuración estratégica en Supabase.
    Devuelve True si se guardó, False si falló.
    """
    if not supabase_client:
        return False

    try:
        supabase_client.table("configuracion_estrategica").upsert(
            {"clave": clave, "valor": valor}
        ).execute()
        return True
    except Exception as e:
        print(f"Error guardando estrategia en Supabase: {e}")
        return False


# --------------------------------------------------------------------------
# Candado anti-duplicidad para SEO Proactivo (evita keyword cannibalization:
# dos artículos distintos compitiendo por la misma búsqueda). Reutiliza el
# mismo patrón de "candado" que ya usa el Orquestador 360 con
# campanas_ejecutadas, pero para clusters de intención de búsqueda.
#
# Tabla esperada en el proyecto Supabase de la Agencia: clusters_seo_ejecutados
#   - cluster_normalizado (text, primary key)
#   - cluster_original (text)
#   - fecha_creacion (timestamp)
# --------------------------------------------------------------------------

def normalizar_cluster(cluster: str) -> str:
    """Normaliza un cluster de búsqueda para comparar de forma consistente
    (minúsculas, sin espacios de más). No es matching difuso — es exacto
    tras normalizar, suficiente y barato para evitar el caso obvio de
    generar el mismo cluster dos veces."""
    return " ".join(cluster.strip().lower().split())


def cluster_ya_ejecutado(supabase_client, cluster: str):
    """
    Devuelve el registro existente (dict) si ya se generó contenido SEO para
    este cluster, o None si es nuevo / si no hay cliente. Ante error de
    conexión, devuelve None (no bloquea la generación por un problema de red).
    """
    if not supabase_client:
        return None

    try:
        resp = (
            supabase_client.table("clusters_seo_ejecutados")
            .select("*")
            .eq("cluster_normalizado", normalizar_cluster(cluster))
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        print(f"Error consultando clusters_seo_ejecutados: {e}")
        return None


def registrar_cluster_ejecutado(supabase_client, cluster: str) -> bool:
    """Registra un cluster como ya ejecutado, para que no se repita a futuro."""
    if not supabase_client:
        return False

    try:
        supabase_client.table("clusters_seo_ejecutados").insert({
            "cluster_normalizado": normalizar_cluster(cluster),
            "cluster_original": cluster,
        }).execute()
        return True
    except Exception as e:
        print(f"Error registrando cluster ejecutado: {e}")
        return False

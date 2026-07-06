"""
estrategia.py — Prioridad estratégica dinámica de ViveroOnline.

A diferencia de identidad_marca.py (tono/voz, cambia poco) y brand_book.py
(identidad visual, cambia poco), este módulo lee y escribe en Supabase —
pensado para prioridades de negocio que SÍ cambian seguido (ej. "este mes
enfocarse en generar transacciones reales" → más adelante "este mes
enfocarse en onboarding de viveristas"), sin necesidad de tocar código ni
esperar un redeploy.

Tabla esperada en el proyecto Supabase de la Agencia: configuracion_estrategica
  - clave (text, primary key)
  - valor (text)
  - actualizado_en (timestamp)
"""

CLAVE_PRIORIDAD_DEFAULT = "prioridad_actual"

VALOR_FALLBACK = (
    "Posicionamiento de categoría (Océano Azul): ViveroOnline es la "
    "plataforma inteligente de abastecimiento ornamental y soluciones "
    "verdes para proyectos urbanos, paisajísticos y arquitectónicos — "
    "nunca vivero, e-commerce, directorio o marketplace tradicional."
)


def obtener_prioridad_estrategica(supabase_client, clave: str = CLAVE_PRIORIDAD_DEFAULT) -> str:
    """
    Lee la prioridad estratégica actual desde Supabase. Si no hay cliente,
    la tabla no existe, o la consulta falla, devuelve VALOR_FALLBACK — los
    agentes nunca deben quedarse sin ninguna guía estratégica por un error
    de conexión.
    """
    if not supabase_client:
        return VALOR_FALLBACK

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
        return VALOR_FALLBACK
    except Exception as e:
        print(f"Error leyendo estrategia desde Supabase: {e}")
        return VALOR_FALLBACK


def guardar_prioridad_estrategica(supabase_client, valor: str, clave: str = CLAVE_PRIORIDAD_DEFAULT) -> bool:
    """
    Guarda (upsert) la prioridad estratégica actual en Supabase.
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

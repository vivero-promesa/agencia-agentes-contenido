"""
campanas.py — Capa de CAMPAÑA del Centro de Comando.

Por qué existe
--------------
Antes cada botón generaba una pieza suelta: el SEO no sabía qué dijo el
WhatsApp, el blog no sabía qué campaña estaba activa y nada recordaba lo que
ya se publicó. Las agencias trabajan al revés: primero una idea que dura
meses (plataforma de campaña), luego pilares fijos, un calendario y una
memoria de lo publicado. Este módulo agrega exactamente eso:

  1. CAMPAÑA   → idea central, mensaje clave, insight, objetivo y fechas.
  2. PILARES   → 4 temas fijos (3 construyen marca, 1 vende).
  3. BRIEF     → texto que TODOS los agentes reciben antes de escribir.
  4. MEMORIA   → resumen de las últimas piezas de la campaña, para dar
                 continuidad sin repetir ni contradecir.
  5. CALENDARIO→ plan de semanas: qué pieza, qué canal, qué pilar, qué día.

No toca los agentes: el brief viaja por el parámetro 'prioridad_estrategica'
que todos ya aceptan. No toca el módulo de video.

Tablas (base AGENCIA): ver migraciones/001_campanas.sql
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

# ==========================================
# 1. PILARES DE CONTENIDO (fijos)
# ==========================================
# 3 de marca + 1 de venta ≈ equilibrio 60/40 (Binet & Field).
PILARES = {
    "oficio": {
        "nombre": "Oficio viverista",
        "tipo": "marca",
        "que": "Historias reales de viveristas aliados: el trabajo, la calidad, el orgullo del oficio.",
        "canales": ["VIDEO", "TEXTO"],
    },
    "abastecer": {
        "nombre": "Abastecer fácil",
        "tipo": "marca",
        "que": "Cotizar, entregar y despachar plantas vivas sin líos: logística, garantía, puente con el comprador.",
        "canales": ["WHATSAPP", "BLOG"],
    },
    "saber": {
        "nombre": "Saber técnico",
        "tipo": "marca",
        "que": "Especies, clima y usos paisajísticos en la Sabana de Bogotá: autoridad técnica útil.",
        "canales": ["BLOG", "SEO"],
    },
    "lotes": {
        "nombre": "Lotes disponibles",
        "tipo": "venta",
        "que": "Stock real del marketplace: activar la venta de un lote concreto.",
        "canales": ["WHATSAPP", "SEO"],
    },
}

# Rol de cada canal dentro de una campaña (no todos hacen lo mismo).
CANALES = {
    "BLOG": "Educa y gana búsquedas e IA (GEO/AEO). Largo formato.",
    "SEO": "Captura una búsqueda concreta con intención de compra.",
    "WHATSAPP": "Activa: lleva a una conversación o cotización con el código de campaña.",
    "VIDEO": "Emociona y muestra el oficio (se produce a mano con Google Vids).",
    "TEXTO": "Texto B2B con estructura PAS (problema, agitación, solución, logística, CTA) para LinkedIn, newsletter o la web.",
}

AUDIENCIAS = {
    "institucional": "Comprador institucional (paisajista, constructora, conjunto)",
    "viverista": "Viverista (productor aliado)",
}

ESTADOS_CAMPANA = ["borrador", "activa", "pausada", "cerrada"]
ESTADOS_CALENDARIO = ["pendiente", "generado", "aprobado", "publicado"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# Columnas nuevas de historial_contenidos (si la migración no corrió, se omiten)
COLUMNAS_META_HISTORIAL = ("campana_id", "calendario_id", "pilar", "canal", "audiencia")


# ==========================================
# 2. UTILIDADES
# ==========================================
def codigo_campana(campana: Optional[dict]) -> str:
    """Código corto y estable que viaja en los enlaces de WhatsApp para
    medir qué campaña trajo cada conversación (ej. VH-003)."""
    if not campana:
        return ""
    return campana.get("codigo") or f"VH-{int(campana.get('id') or 0):03d}"


def _fecha(valor) -> Optional[date]:
    if not valor:
        return None
    if isinstance(valor, date):
        return valor
    try:
        return datetime.fromisoformat(str(valor)[:10]).date()
    except ValueError:
        return None


def tablas_listas(sb) -> bool:
    """True si la migración 001 ya corrió en la base Agencia."""
    if not sb:
        return False
    try:
        sb.table("campanas").select("id").limit(1).execute()
        sb.table("calendario_contenidos").select("id").limit(1).execute()
        # Si la migración quedó a medias, el historial no tiene las columnas
        # nuevas y guardar con etiquetas fallaría: mejor tratarlo como no lista.
        sb.table("historial_contenidos").select(",".join(COLUMNAS_META_HISTORIAL + ("fecha_publicacion", "url_publicada"))).limit(1).execute()
        return True
    except Exception:
        return False


# ==========================================
# 3. CRUD DE CAMPAÑAS
# ==========================================
def listar_campanas(sb, solo_vigentes: bool = False) -> list:
    q = sb.table("campanas").select("*")
    if solo_vigentes:
        q = q.in_("estado", ["activa", "pausada"])
    return q.order("id", desc=True).execute().data or []


def guardar_campana(sb, datos: dict, campana_id: Optional[int] = None) -> Optional[dict]:
    """Crea o actualiza. Devuelve la fila guardada."""
    limpio = {k: v for k, v in datos.items() if k != "id"}
    for k in ("fecha_inicio", "fecha_fin"):
        if isinstance(limpio.get(k), date):
            limpio[k] = limpio[k].isoformat()
    if campana_id:
        res = sb.table("campanas").update(limpio).eq("id", campana_id).execute()
    else:
        res = sb.table("campanas").insert(limpio).execute()
    fila = (res.data or [None])[0]
    # El código se fija una sola vez, al crear, para que no cambie nunca.
    if fila and not fila.get("codigo"):
        codigo = codigo_campana(fila)
        sb.table("campanas").update({"codigo": codigo}).eq("id", fila["id"]).execute()
        fila["codigo"] = codigo
    return fila


# ==========================================
# 4. MEMORIA DE LA CAMPAÑA
# ==========================================
def piezas_campana(sb, campana_id: int, limite: int = 200) -> list:
    return (
        sb.table("historial_contenidos").select("*")
        .eq("campana_id", campana_id)
        .order("fecha_creacion", desc=True)
        .limit(limite).execute().data or []
    )


def memoria_campana(sb, campana_id: int, n: int = 6, largo: int = 220) -> str:
    """Resumen de las últimas piezas de la campaña (primero las aprobadas).
    Es lo que permite que el WhatsApp del miércoles 'sepa' qué dijo el
    artículo del lunes."""
    try:
        piezas = piezas_campana(sb, campana_id, limite=40)
    except Exception:
        return ""
    if not piezas:
        return ""
    piezas.sort(key=lambda p: (0 if p.get("estado") in ("aprobado", "publicado") else 1))
    lineas = []
    for p in piezas[:n]:
        texto = " ".join(str(p.get("contenido") or "").split())
        if len(texto) > largo:
            texto = texto[:largo].rsplit(" ", 1)[0] + "…"
        estado = "publicado" if p.get("url_publicada") else (p.get("estado") or "borrador")
        etiqueta = " · ".join(x for x in [
            str(p.get("tipo_contenido") or ""),
            PILARES.get(p.get("pilar") or "", {}).get("nombre", ""),
            str(p.get("fecha_creacion") or "")[:10],
            estado,
        ] if x)
        lineas.append(f"- [{etiqueta}] {p.get('titulo') or 'Sin título'}: {texto}")
    return "\n".join(lineas)


# ==========================================
# 5. BRIEF QUE VIAJA A LOS AGENTES
# ==========================================
def construir_brief(
    campana: Optional[dict],
    pilar: Optional[str] = None,
    canal: Optional[str] = None,
    audiencia: Optional[str] = None,
    memoria: str = "",
    angulo: Optional[str] = None,
) -> str:
    """Brief creativo, al estilo agencia, que se agrega a la Prioridad
    Estratégica. Si no hay campaña activa devuelve cadena vacía (la app
    se comporta exactamente como antes)."""
    if not campana:
        return ""
    partes = [
        "=== BRIEF DE CAMPAÑA (obligatorio respetarlo) ===",
        f"Campaña: {campana.get('nombre', '')} [{codigo_campana(campana)}]",
        f"Idea central (plataforma): {campana.get('idea_central', '')}",
        f"Mensaje clave que TODA pieza debe reforzar: {campana.get('mensaje_clave', '')}",
    ]
    if campana.get("insight"):
        partes.append(f"Insight de la audiencia: {campana['insight']}")
    if campana.get("objetivo"):
        partes.append(f"Objetivo de negocio: {campana['objetivo']}")
    if campana.get("tono_extra"):
        partes.append(f"Notas de tono para esta campaña: {campana['tono_extra']}")
    if pilar and pilar in PILARES:
        p = PILARES[pilar]
        partes.append(f"Pilar de esta pieza: {p['nombre']} ({p['tipo']}) — {p['que']}")
        if p["tipo"] == "marca":
            partes.append("Esta pieza construye marca: prioriza confianza y recordación; el CTA es suave, sin presión.")
        else:
            partes.append("Esta pieza activa venta: CTA claro hacia cotizar por WhatsApp, sin urgencia falsa. "
                          "Usa SOLO los datos reales de lote que vengan en el tema; si no vienen, no menciones "
                          "cantidades, precios ni disponibilidad concreta.")
    if canal and canal in CANALES:
        partes.append(f"Rol del canal {canal}: {CANALES[canal]}")
    if audiencia and audiencia in AUDIENCIAS:
        partes.append(f"Audiencia: {AUDIENCIAS[audiencia]}")
    if angulo:
        partes.append(f"Ángulo de esta pieza: {angulo}")
    if memoria:
        partes.append(
            "Lo que la campaña YA publicó (da continuidad: mantén el mensaje clave, "
            "no repitas frases ni ángulos, no contradigas; lo marcado como borrador "
            "aún no salió al público):\n" + memoria
        )
    partes.append("=== FIN DEL BRIEF ===")
    return "\n".join(partes)


def contexto_agente(prioridad: str, brief: str) -> str:
    """Prioridad estratégica + brief. Es lo que se pasa como
    'prioridad_estrategica' a cualquier agente."""
    prioridad = (prioridad or "").strip()
    if not brief:
        return prioridad
    return f"{prioridad}\n\n{brief}" if prioridad else brief


# ==========================================
# 6. CALENDARIO EDITORIAL
# ==========================================
class FilaCalendarioIA(BaseModel):
    semana: int = Field(description="Número de semana, empezando en 1.")
    dia: str = Field(description="Día de la semana en español: lunes, martes, miércoles, jueves o viernes.")
    canal: str = Field(description="Uno de: BLOG, SEO, WHATSAPP, VIDEO, TEXTO.")
    pilar: str = Field(description="Uno de: oficio, abastecer, saber, lotes.")
    audiencia: str = Field(description="institucional o viverista.")
    tema: str = Field(description="Tema concreto de la pieza, en una frase.")
    angulo: str = Field(description="Cómo esta pieza refuerza el mensaje clave y conecta con la anterior.")


class CalendarioIA(BaseModel):
    filas: list[FilaCalendarioIA]


def prompt_calendario(campana: dict, semanas: int, piezas_semana: int, memoria: str = "", marca: str = "viveroonline.com.co") -> str:
    pilares_txt = "\n".join(f"- {k}: {v['nombre']} ({v['tipo']}) — {v['que']} Canales naturales: {', '.join(v['canales'])}" for k, v in PILARES.items())
    canales_txt = "\n".join(f"- {k}: {v}" for k, v in CANALES.items())
    total = semanas * piezas_semana
    return f"""Eres planner de una agencia de publicidad B2B. Diseña el calendario editorial
de una campaña del marketplace de plantas ornamentales {marca} (Sabana de Bogotá).

CAMPAÑA
- Nombre: {campana.get('nombre')}
- Idea central: {campana.get('idea_central')}
- Mensaje clave: {campana.get('mensaje_clave')}
- Insight: {campana.get('insight') or 'no definido'}
- Objetivo: {campana.get('objetivo') or 'no definido'}
- Audiencia principal: {AUDIENCIAS.get(campana.get('audiencia') or 'institucional', 'institucional')}

PILARES (usa solo estas claves):
{pilares_txt}

CANALES (usa solo estas claves) y su rol:
{canales_txt}

REGLAS
1. Exactamente {total} piezas: {piezas_semana} por semana durante {semanas} semanas, en días hábiles distintos.
2. Equilibrio: cerca del 75% de las piezas en pilares de marca (oficio, abastecer, saber) y cerca del 25% en 'lotes'.
3. Continuidad: la semana 1 presenta la idea; las siguientes la profundizan. Cada 'angulo' dice cómo se conecta con la pieza anterior.
4. Cada semana usa al menos 2 canales distintos. No repitas el mismo tema.
5. Al menos una pieza por semana para viveristas si la audiencia principal es institucional (el marketplace tiene dos lados), y viceversa.
6. No inventes cifras, nombres de viveros ni clientes.
7. En las piezas del pilar 'lotes' el tema nombra la especie o categoría (ej. "Eugenias para cerramientos"),
   nunca cantidades ni precios: el lote real del inventario se adjunta al momento de generar la pieza.
{('8. Ya se publicó esto en la campaña; continúa desde ahí sin repetir:' + chr(10) + memoria) if memoria else ''}
Devuelve JSON con la lista 'filas'."""


def normalizar_filas(filas: list, campana: dict, semanas: int, desde: Optional[date] = None) -> list:
    """Valida lo que devuelve la IA y calcula la fecha real de cada pieza.
    Arranca en 'desde' (hoy, o el día siguiente a la última pieza ya
    planeada) y nunca antes del inicio de la campaña. Descarta lo que caiga
    después de la fecha de fin."""
    inicio = max(_fecha(campana.get("fecha_inicio")) or date.today(), desde or date.min)
    fin = _fecha(campana.get("fecha_fin"))
    lunes = inicio - timedelta(days=inicio.weekday())
    salida = []
    for f in filas:
        d = f if isinstance(f, dict) else f.model_dump()
        canal = str(d.get("canal", "")).upper().strip()
        pilar = str(d.get("pilar", "")).lower().strip()
        audiencia = str(d.get("audiencia", "")).lower().strip()
        dia = str(d.get("dia", "")).lower().strip().replace("miercoles", "miércoles")
        try:
            semana = max(1, min(int(d.get("semana") or 1), semanas))
        except (TypeError, ValueError):
            semana = 1
        if canal not in CANALES:
            canal = "TEXTO"
        if pilar not in PILARES:
            pilar = "saber"
        if audiencia not in AUDIENCIAS:
            audiencia = campana.get("audiencia") or "institucional"
        idx = DIAS.index(dia) if dia in DIAS else 0
        fecha = lunes + timedelta(weeks=semana - 1, days=idx)
        if fecha < inicio:
            fecha = inicio
        if fin and fecha > fin:
            continue
        salida.append({
            "campana_id": campana.get("id"),
            "fecha": fecha.isoformat(),
            "canal": canal,
            "pilar": pilar,
            "audiencia": audiencia,
            "tema": str(d.get("tema", "")).strip()[:300],
            "angulo": str(d.get("angulo", "")).strip()[:500],
            "estado": "pendiente",
        })
    salida.sort(key=lambda r: r["fecha"])
    return salida


def generar_calendario(invocar, campana: dict, semanas: int = 4, piezas_semana: int = 3, memoria: str = "",
                       marca: str = "viveroonline.com.co", desde: Optional[date] = None) -> list:
    """'invocar' = función (prompt, schema) -> texto JSON (se inyecta
    invocar_modelo_seguro de agentes_crecimiento, Gemini con salida JSON)."""
    texto = invocar(prompt_calendario(campana, semanas, piezas_semana, memoria, marca), CalendarioIA)
    if not texto:
        return []
    try:
        datos = json.loads(texto)
    except (TypeError, json.JSONDecodeError):
        return []
    filas = datos.get("filas", []) if isinstance(datos, dict) else datos
    return normalizar_filas(filas or [], campana, semanas, desde)


def filas_desde_editor(filas: list, campana_id: int) -> list:
    """Limpia lo que la persona editó en la tabla: descarta filas sin tema o
    con fecha inválida y corrige valores fuera de lista."""
    salida = []
    for f in filas or []:
        tema = str(f.get("tema") or "").strip()
        fecha = _fecha(str(f.get("fecha") or "").strip())
        if not tema or not fecha:
            continue
        canal = str(f.get("canal") or "").upper()
        pilar = str(f.get("pilar") or "").lower()
        audiencia = str(f.get("audiencia") or "").lower()
        salida.append({
            "campana_id": campana_id,
            "fecha": fecha.isoformat(),
            "canal": canal if canal in CANALES else "TEXTO",
            "pilar": pilar if pilar in PILARES else "saber",
            "audiencia": audiencia if audiencia in AUDIENCIAS else "institucional",
            "tema": tema[:300],
            "angulo": str(f.get("angulo") or "").strip()[:500] or None,
            "estado": "pendiente",
        })
    return salida


def inicio_siguiente_calendario(calendario: list, hoy: Optional[date] = None) -> date:
    """Un calendario nuevo arranca hoy o justo después de la última pieza ya
    planeada (para continuar la campaña, no reiniciarla)."""
    hoy = hoy or date.today()
    fechas = [_fecha(c.get("fecha")) for c in calendario or []]
    fechas = [f for f in fechas if f]
    return max([hoy] + [f + timedelta(days=1) for f in fechas])


def _normalizar_texto(t: str) -> list:
    import unicodedata
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    palabras = [w for w in "".join(c if c.isalnum() else " " for c in t).split() if len(w) > 3]
    # Plural → singular simple, para que "Eugenias" coincida con "Eugenia"
    return [w[:-2] if w.endswith("es") and len(w) > 5 else (w[:-1] if w.endswith("s") else w) for w in palabras]


def elegir_lote(tema: str, lotes: list, nombre_de) -> Optional[dict]:
    """Lote real cuya planta es la que nombra el tema de la pieza.
    'nombre_de(lote)' devuelve "Nombre común (Nombre científico)". Coincide
    si TODAS las palabras del nombre común están en el tema (así "Palmas
    botella" no se confunde con "Palma areca"), o si aparece el género
    científico. Si nada coincide devuelve None: mejor no inventar que
    vender otra planta."""
    palabras_tema = set(_normalizar_texto(tema))
    mejor, puntaje = None, 0
    for lote in lotes or []:
        nombre = str(nombre_de(lote) or "")
        comun, _, cientifico = nombre.partition("(")
        p_comun = set(_normalizar_texto(comun))
        p_cient = _normalizar_texto(cientifico)
        coincide_comun = bool(p_comun) and p_comun <= palabras_tema
        coincide_genero = bool(p_cient) and p_cient[0] in palabras_tema
        if coincide_comun or coincide_genero:
            valor = len(p_comun & palabras_tema) + len(set(p_cient) & palabras_tema)
            if valor > puntaje:
                mejor, puntaje = lote, valor
    return mejor


def listar_calendario(sb, campana_id: int) -> list:
    return (
        sb.table("calendario_contenidos").select("*")
        .eq("campana_id", campana_id).order("fecha").order("id")
        .execute().data or []
    )


def guardar_calendario(sb, filas: list) -> int:
    if not filas:
        return 0
    res = sb.table("calendario_contenidos").insert(filas).execute()
    return len(res.data or filas)


def actualizar_fila_calendario(sb, fila_id: int, cambios: dict):
    sb.table("calendario_contenidos").update(cambios).eq("id", fila_id).execute()


def borrar_pendientes(sb, campana_id: int):
    """Borra solo filas 'pendiente' (lo ya generado o publicado se conserva)."""
    sb.table("calendario_contenidos").delete().eq("campana_id", campana_id).eq("estado", "pendiente").execute()


# ==========================================
# 7. TABLERO DE LA CAMPAÑA
# ==========================================
def resumen_campana(piezas: list, calendario: list) -> dict:
    """Mezcla marca/venta, cobertura de pilares y canales, avance del plan."""
    por_pilar = {k: 0 for k in PILARES}
    por_canal: dict = {}
    for p in piezas:
        if p.get("pilar") in por_pilar:
            por_pilar[p["pilar"]] += 1
        canal = p.get("canal") or p.get("tipo_contenido") or "OTRO"
        por_canal[canal] = por_canal.get(canal, 0) + 1
    con_pilar = sum(por_pilar.values())
    marca = sum(v for k, v in por_pilar.items() if PILARES[k]["tipo"] == "marca")
    hoy = date.today().isoformat()
    return {
        "piezas": len(piezas),
        "aprobadas": sum(1 for p in piezas if p.get("estado") in ("aprobado", "publicado")),
        "publicadas": sum(1 for p in piezas if p.get("estado") == "publicado" or p.get("url_publicada")),
        "con_venta": sum(1 for p in piezas if p.get("genero_venta") is True),
        "pct_marca": round(100 * marca / con_pilar) if con_pilar else None,
        "por_pilar": por_pilar,
        "por_canal": por_canal,
        "plan_total": len(calendario),
        "plan_hechas": sum(1 for c in calendario if c.get("estado") != "pendiente"),
        "plan_atrasadas": sum(1 for c in calendario if c.get("estado") == "pendiente" and str(c.get("fecha", "")) < hoy),
    }

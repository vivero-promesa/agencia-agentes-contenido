"""
publicador_wordpress.py — Publica/programa artículos del Historial en el blog WordPress.

Flujo: en la pestaña Historial, al pulsar "✅ Marcar como aprobado" en una pieza de
tipo BLOG, la app crea la entrada en WordPress:
  - fecha de "Publicada el" en el futuro  -> entrada PROGRAMADA para ese día (7:00 a. m. Bogotá)
  - fecha de hoy, pasada o vacía          -> entrada PUBLICADA de inmediato
y guarda solo el enlace www.viverohub.com/blog/... en "Enlace donde se publicó".

Seguridad / no romper nada:
  - Si faltan los secrets WP_USUARIO o WP_APP_PASSWORD, el módulo queda APAGADO y la
    app se comporta exactamente igual que antes (aprobar solo cambia el estado).
  - Si la pieza ya tiene enlace, NO se vuelve a crear la entrada (evita duplicados).
  - Cualquier error de WordPress se devuelve como mensaje; nunca revienta la app.

Secrets (Streamlit Cloud -> Settings -> Secrets):
  WP_USUARIO        = "usuario administrador de WordPress"
  WP_APP_PASSWORD   = "contraseña de aplicación (Usuarios -> Perfil -> Contraseñas de aplicación)"
  WP_URL            = "https://viveroonline.com.co"          (opcional, es el valor por defecto)
  WP_BLOG_URL       = "https://www.viverohub.com/blog"       (opcional, es el valor por defecto)
  WP_HORA_PUBLICACION = "07:00"                              (opcional, hora Bogotá)
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

try:
    import markdown as _md
except Exception:  # pragma: no cover
    _md = None


BOGOTA = timezone(timedelta(hours=-5))  # Colombia no tiene horario de verano


@dataclass
class ConfigWP:
    usuario: str | None
    app_password: str | None
    url_api: str = "https://viveroonline.com.co"
    url_blog: str = "https://www.viverohub.com/blog"
    hora: str = "07:00"

    @property
    def activo(self) -> bool:
        return bool(self.usuario and self.app_password and requests is not None)


@dataclass
class ResultadoWP:
    ok: bool
    mensaje: str
    enlace: str | None = None
    fecha: date | None = None
    programado: bool = False


# ------------------------------------------------------------------
# 1. Limpieza del artículo: quitar notas internas y separar el título
# ------------------------------------------------------------------
_PATRON_FAQ = re.compile(
    r"^\s*\**PREGUNTA\s*\d+\s*:?\**\s*:?\s*(?P<p>.+?)\s*$\s*^\s*\**RESPUESTA\s*\d+\s*:?\**\s*:?\s*(?P<r>.+?)\s*(?=\n\s*\n|^\s*\**PREGUNTA\s*\d+|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


_MESES = {"January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
          "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
          "September": "septiembre", "October": "octubre", "November": "noviembre",
          "December": "diciembre"}


def limpiar_articulo(contenido: str, titulo_respaldo: str) -> tuple[str, str]:
    """Devuelve (titulo, markdown_limpio) listo para el blog."""
    texto = (contenido or "").replace("\r\n", "\n")

    # Instrucción interna para Elena: "Cómo publicar el FAQ: ..."
    texto = re.sub(r"\n-{3,}\s*\n\*\*Cómo publicar el FAQ:\*\*.*?(?=\n-{3,}|\n⚠️|\Z)", "\n", texto, flags=re.DOTALL)
    texto = re.sub(r"^\*\*Cómo publicar el FAQ:\*\*.*$", "", texto, flags=re.MULTILINE)
    # Notas internas de validación ("⚠️ *Nota interna...*")
    texto = re.sub(r"^\s*⚠️.*$", "", texto, flags=re.MULTILINE)

    # Título: el H1 que escribe el agente; si no hay, el título del Historial
    titulo = (titulo_respaldo or "").strip()
    m = re.search(r"^\s*#\s+(.+?)\s*$", texto, flags=re.MULTILINE)
    if m:
        titulo = m.group(1).strip().strip("*").strip()
        texto = texto[: m.start()] + texto[m.end():]

    # Fecha de frescura en español (el agente a veces la deja con el mes en inglés)
    for en, es in _MESES.items():
        texto = re.sub(rf"(Última actualización:[^\n]*?)\b{en}\b", rf"\g<1>{es}", texto)
    # Separadores repetidos ("---" seguidos) tras quitar las notas internas
    texto = re.sub(r"(?:\n\s*-{3,}\s*){2,}", "\n\n---\n\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return titulo or "Artículo", texto


def _faq_a_html(md_texto: str) -> tuple[str, list[dict]]:
    """Convierte 'PREGUNTA N: / RESPUESTA N:' en H3 + párrafo y arma el FAQPage."""
    preguntas: list[dict] = []

    def _reemplazo(m: re.Match) -> str:
        p = m.group("p").strip().strip("*").strip()
        r = re.sub(r"\s+", " ", m.group("r").strip().strip("*").strip())
        preguntas.append({"p": p, "r": r})
        return f"\n\n### {p}\n\n{r}\n\n"

    nuevo = _PATRON_FAQ.sub(_reemplazo, md_texto)
    return nuevo, preguntas


def _md_basico(texto: str) -> str:
    """Respaldo si la librería 'markdown' no está instalada."""
    def inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"\[(.+?)\]\((https?://[^\s)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    salida, lista = [], None
    for bloque in re.split(r"\n\s*\n", texto):
        lineas = [l for l in bloque.split("\n") if l.strip()]
        if not lineas:
            continue
        h = re.match(r"^(#{2,6})\s+(.*)$", lineas[0])
        if h and len(lineas) == 1:
            n = len(h.group(1))
            salida.append(f"<h{n}>{inline(h.group(2))}</h{n}>")
        elif all(re.match(r"^\s*[-*]\s+", l) for l in lineas):
            salida.append("<ul>" + "".join(f"<li>{inline(re.sub(r'^\s*[-*]\s+', '', l))}</li>" for l in lineas) + "</ul>")
        elif all(re.match(r"^\s*\d+[.)]\s+", l) for l in lineas):
            salida.append("<ol>" + "".join(f"<li>{inline(re.sub(r'^\s*\d+[.)]\s+', '', l))}</li>" for l in lineas) + "</ol>")
        elif re.match(r"^\s*-{3,}\s*$", lineas[0]) and len(lineas) == 1:
            salida.append("<hr />")
        else:
            salida.append("<p>" + "<br />".join(inline(l) for l in lineas) + "</p>")
    return "\n".join(salida)


def markdown_a_html(md_texto: str) -> str:
    md_texto, preguntas = _faq_a_html(md_texto)
    if _md is not None:
        cuerpo = _md.markdown(md_texto, extensions=["extra", "sane_lists"])
    else:
        cuerpo = _md_basico(md_texto)

    if preguntas:
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q["p"],
                 "acceptedAnswer": {"@type": "Answer", "text": q["r"]}}
                for q in preguntas
            ],
        }
        cuerpo += (
            '\n<!-- wp:html -->\n<script type="application/ld+json">'
            + json.dumps(schema, ensure_ascii=False)
            + "</script>\n<!-- /wp:html -->"
        )
    return cuerpo


# ------------------------------------------------------------------
# 2. Llamada a WordPress (REST API + contraseña de aplicación)
# ------------------------------------------------------------------
def _fecha_programada(dia: date, hora: str) -> datetime:
    hh, mm = (hora or "07:00").split(":")[:2]
    local = datetime(dia.year, dia.month, dia.day, int(hh), int(mm), tzinfo=BOGOTA)
    return local.astimezone(timezone.utc)


def _explicar_error(resp) -> str:
    cuerpo = (resp.text or "")[:400]
    if "Un momento" in cuerpo or "<html" in cuerpo.lower():
        return ("El hosting (Dongee) respondió con su pantalla anti-bot en vez de WordPress. "
                "Hay que pedirle a Dongee que permita /wp-json/ o el tráfico de Streamlit Cloud.")
    if resp.status_code == 401:
        return ("WordPress rechazó el usuario o la contraseña de aplicación (401). "
                "Revisa WP_USUARIO y WP_APP_PASSWORD en los Secrets.")
    if resp.status_code == 403:
        return "El usuario de WordPress no tiene permiso para publicar entradas (403)."
    try:
        return f"WordPress respondió {resp.status_code}: {resp.json().get('message', cuerpo)}"
    except Exception:
        return f"WordPress respondió {resp.status_code}."


def publicar_o_programar(cfg: ConfigWP, titulo: str, contenido_md: str,
                         dia: date | None) -> ResultadoWP:
    if not cfg.activo:
        return ResultadoWP(False, "Publicación automática apagada (faltan WP_USUARIO / WP_APP_PASSWORD).")

    titulo_final, md_limpio = limpiar_articulo(contenido_md, titulo)
    cuerpo_html = markdown_a_html(md_limpio)

    hoy = datetime.now(BOGOTA).date()
    dia = dia or hoy
    datos = {"title": titulo_final, "content": cuerpo_html}
    programado = False
    if dia > hoy:
        datos["status"] = "future"
        datos["date_gmt"] = _fecha_programada(dia, cfg.hora).strftime("%Y-%m-%dT%H:%M:%S")
        programado = True
    else:
        datos["status"] = "publish"
        dia = hoy

    try:
        resp = requests.post(
            cfg.url_api.rstrip("/") + "/wp-json/wp/v2/posts",
            json=datos,
            auth=(cfg.usuario, cfg.app_password.replace(" ", "")),
            headers={"User-Agent": "CentroDeComando-viverohub/1.0"},
            timeout=40,
        )
    except Exception as e:
        return ResultadoWP(False, f"No se pudo conectar con WordPress: {e}")

    if resp.status_code not in (200, 201):
        return ResultadoWP(False, _explicar_error(resp))

    try:
        post = resp.json()
    except Exception:
        return ResultadoWP(False, _explicar_error(resp))

    slug = post.get("slug") or ""
    if slug:
        enlace = f"{cfg.url_blog.rstrip('/')}/{slug}/"
    else:
        enlace = post.get("link") or ""

    accion = f"programado para el {dia.strftime('%d/%m/%Y')} a las {cfg.hora}" if programado else "publicado"
    return ResultadoWP(True, f"Artículo {accion} en el blog.", enlace=enlace, fecha=dia, programado=programado)

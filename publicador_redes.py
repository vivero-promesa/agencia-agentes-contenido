"""
publicador_redes.py — El botón "📢 Publicar" de cada pieza: la manda a su destino.

Destino según el tipo de pieza (el mismo contenido para las tres redes):
  BLOG      -> blog de WordPress (lo hace publicador_wordpress.py, ya existente)
  VIDEO     -> Instagram (Reel) + Facebook (video) + TikTok
  TEXTO     -> Instagram (foto o carrusel) + Facebook (publicación) + TikTok (carrusel de fotos)
  WHATSAPP  -> mensajes: abre WhatsApp con el texto listo (el envío lo hace Elena)
  SEO       -> ficha de producto del marketplace (se pega a mano por ahora)

Cómo publica en cada red
  Instagram + Facebook: con la API oficial de Meta (Graph API), desde la página de
    Facebook y la cuenta de Instagram profesional de viverohub. Solo PUBLICACIONES
    ORGÁNICAS. No usa ni pide permisos de anuncios (regla de oro 1-3): los permisos
    son pages_manage_posts e instagram_content_publish, nunca ads_management.
  TikTok: su API de publicación exige que TikTok audite una app. Mientras tanto, el
    botón deja el texto listo para copiar y abre TikTok Studio para subir el video.
  Si faltan los secrets de Meta, Instagram y Facebook funcionan igual que TikTok:
    texto listo + botón que abre Meta Business Suite (publica en las dos a la vez).

Seguridad / no romper nada
  - Sin secrets, el módulo queda en modo "kit" y la app se comporta igual que antes.
  - Nada se publica solo: cada publicación sale del clic de Elena en una pieza aprobada.
  - Cualquier error de Meta vuelve como mensaje en español; nunca revienta la app.
  - Instagram exige que la foto o el video estén en un enlace PÚBLICO (Drive con
    acceso "cualquier persona", el sitio, etc.). El texto solo no se puede subir a IG.

Secrets (Streamlit Cloud -> Settings -> Secrets), todos de viverohub:
  META_PAGE_ID       = "id de la página de Facebook de viverohub"
  META_PAGE_TOKEN    = "token de página de larga duración (pages_manage_posts, instagram_content_publish)"
  META_IG_USER_ID    = "id de la cuenta de Instagram profesional de viverohub"
  META_API_VERSION   = "v21.0"                       (opcional)
  SITIO_DESTINO      = "https://www.viverohub.com"   (opcional, a dónde lleva el enlace de cada post)
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


# ------------------------------------------------------------------
# 1. A dónde va cada pieza
# ------------------------------------------------------------------
REDES = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "tiktok": "TikTok",
    "whatsapp": "WhatsApp",
}

DESTINOS = {
    "BLOG": {"etiqueta": "📰 Blog viverohub.com/blog", "redes": []},
    "VIDEO": {"etiqueta": "🎬 Instagram · Facebook · TikTok", "redes": ["instagram", "facebook", "tiktok"]},
    "TEXTO": {"etiqueta": "🖼️ Instagram · Facebook · TikTok (carrusel o post)", "redes": ["instagram", "facebook", "tiktok"]},
    "WHATSAPP": {"etiqueta": "💬 Mensajes de WhatsApp", "redes": []},
    "SEO": {"etiqueta": "🛒 Ficha de producto del marketplace", "redes": []},
}

# Abren directo la pantalla de publicar de cada red (modo kit o TikTok)
URL_ABRIR = {
    "meta": "https://business.facebook.com/latest/composer",
    "tiktok": "https://www.tiktok.com/tiktokstudio/upload",
}

LIMITE_TEXTO = {"instagram": 2200, "facebook": 5000, "tiktok": 2200}


def destino_de(tipo: str | None) -> dict:
    return DESTINOS.get((tipo or "").upper(), {"etiqueta": "—", "redes": []})


# ------------------------------------------------------------------
# 2. Enlace rastreable (código de campaña VH-00X en utm_campaign)
# ------------------------------------------------------------------
def enlace_con_utm(base: str, red: str, codigo: str, pieza_id=None, medio: str = "organico") -> str:
    partes = urlparse(base or "https://www.viverohub.com")
    params = dict(parse_qsl(partes.query))
    params.update({"utm_source": red, "utm_medium": medio})
    if codigo:
        params["utm_campaign"] = codigo
    if pieza_id is not None:
        params["utm_content"] = str(pieza_id)
    return urlunparse(partes._replace(query=urlencode(params)))


# ------------------------------------------------------------------
# 3. Texto para redes (de markdown a texto plano, con enlace y límite)
# ------------------------------------------------------------------
def texto_para_redes(contenido: str, enlace: str | None = None, red: str = "instagram") -> str:
    """Quita formato markdown y notas internas, agrega el enlace y respeta el
    largo máximo de la red. Para Instagram y TikTok el enlace no es clicable,
    así que también se invita a usar el enlace de la biografía."""
    t = contenido or ""
    t = re.sub(r"```.*?```", "", t, flags=re.DOTALL)
    t = re.sub(r"^\s*#{1,6}\s*", "", t, flags=re.MULTILINE)         # títulos
    t = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), t)
    t = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", t)      # cursiva
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", t)             # enlaces md
    t = re.sub(r"^\s*[-*]\s+", "• ", t, flags=re.MULTILINE)            # viñetas
    t = re.sub(r"^\s*>\s?", "", t, flags=re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()

    cola = ""
    if enlace:
        cola = f"\n\n👉 {enlace}"
        if red in ("instagram", "tiktok"):
            cola = "\n\n👉 Más en el enlace de nuestra biografía · www.viverohub.com"
    limite = LIMITE_TEXTO.get(red, 2200) - len(cola)
    if len(t) > limite:
        t = t[: max(0, limite - 1)].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…"
    return t + cola


def separar_medios(texto: str) -> tuple[list[str], str | None]:
    """De lo que Elena pega (un enlace por línea) saca las imágenes y el video.
    Varias imágenes = carrusel. Un .mp4/.mov o un enlace marcado como video = video."""
    enlaces = [l.strip() for l in (texto or "").splitlines() if l.strip().startswith("http")]
    video = next((e for e in enlaces if re.search(r"\.(mp4|mov)(\?|$)", e, re.IGNORECASE)), None)
    imagenes = [e for e in enlaces if e != video]
    return imagenes[:10], video  # Instagram admite hasta 10 en un carrusel


def enlace_directo_drive(url: str) -> str:
    """Un enlace de Google Drive para 'ver' no sirve a Meta (devuelve una página,
    no el archivo). Se convierte a enlace de descarga directa."""
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?id=)([\w-]+)", url or "")
    return f"https://drive.google.com/uc?export=download&id={m.group(1)}" if m else url


# ------------------------------------------------------------------
# 4. Meta (Instagram + Facebook) — solo publicaciones orgánicas
# ------------------------------------------------------------------
@dataclass
class ConfigMeta:
    page_id: str | None
    page_token: str | None
    ig_user_id: str | None = None
    version: str = "v21.0"

    @property
    def activo_facebook(self) -> bool:
        return bool(self.page_id and self.page_token and requests is not None)

    @property
    def activo_instagram(self) -> bool:
        return bool(self.ig_user_id and self.page_token and requests is not None)

    @property
    def base(self) -> str:
        return f"https://graph.facebook.com/{self.version}"


@dataclass
class ResultadoRed:
    red: str
    ok: bool
    mensaje: str
    enlace: str | None = None


def _error_meta(resp) -> str:
    try:
        err = resp.json().get("error", {})
    except Exception:
        return f"Meta respondió {getattr(resp, 'status_code', '?')}."
    codigo, msg = err.get("code"), err.get("error_user_msg") or err.get("message") or ""
    if codigo == 190:
        return "El token de Meta venció o no es válido. Genera uno nuevo de larga duración y cámbialo en los Secrets (META_PAGE_TOKEN)."
    if codigo in (10, 200) or "permission" in msg.lower():
        return "Al token le falta un permiso. Para publicar se necesitan pages_manage_posts e instagram_content_publish (nunca ads_management)."
    if codigo == 9004 or ("media" in msg.lower() and "url" in msg.lower()):
        return "Meta no pudo descargar la foto o el video. El enlace debe ser público y llevar directo al archivo (.jpg, .png o .mp4)."
    if codigo in (4, 32, 613):
        return "Meta frenó por exceso de solicitudes. Espera unos minutos y vuelve a intentar."
    return f"Meta respondió: {msg or resp.status_code}"


def _post(cfg: ConfigMeta, ruta: str, datos: dict):
    datos = {**datos, "access_token": cfg.page_token}
    return requests.post(f"{cfg.base}/{ruta}", data=datos, timeout=60)


def _get(cfg: ConfigMeta, ruta: str, params: dict):
    params = {**params, "access_token": cfg.page_token}
    return requests.get(f"{cfg.base}/{ruta}", params=params, timeout=30)


def publicar_facebook(cfg: ConfigMeta, texto: str, imagenes: list | None = None,
                      video: str | None = None, enlace: str | None = None) -> ResultadoRed:
    if not cfg.activo_facebook:
        return ResultadoRed("facebook", False, "Publicación directa apagada (faltan META_PAGE_ID / META_PAGE_TOKEN).")
    imagenes = [enlace_directo_drive(i) for i in (imagenes or [])]
    video = enlace_directo_drive(video) if video else None
    try:
        if video:
            r = _post(cfg, f"{cfg.page_id}/videos", {"file_url": video, "description": texto})
        elif len(imagenes) == 1:
            r = _post(cfg, f"{cfg.page_id}/photos", {"url": imagenes[0], "caption": texto})
        elif len(imagenes) > 1:
            # Varias fotos en una publicación: se suben sin publicar y se adjuntan
            ids = []
            for img in imagenes:
                rf = _post(cfg, f"{cfg.page_id}/photos", {"url": img, "published": "false"})
                if rf.status_code != 200:
                    return ResultadoRed("facebook", False, _error_meta(rf))
                ids.append(rf.json()["id"])
            datos = {"message": texto}
            for i, fid in enumerate(ids):
                datos[f"attached_media[{i}]"] = '{"media_fbid":"%s"}' % fid
            r = _post(cfg, f"{cfg.page_id}/feed", datos)
        else:
            datos = {"message": texto}
            if enlace:
                datos["link"] = enlace
            r = _post(cfg, f"{cfg.page_id}/feed", datos)
    except Exception as e:
        return ResultadoRed("facebook", False, f"No se pudo conectar con Facebook: {e}")
    if r.status_code != 200:
        return ResultadoRed("facebook", False, _error_meta(r))
    dato = r.json()
    post_id = dato.get("post_id") or dato.get("id") or ""
    permalink = f"https://www.facebook.com/{post_id}" if post_id else None
    return ResultadoRed("facebook", True, "Publicado en Facebook.", permalink)


def _esperar_contenedor(cfg: ConfigMeta, contenedor: str, espera_max: int = 90) -> str | None:
    """Instagram procesa el video antes de dejarlo publicar. Devuelve None si
    quedó listo, o el mensaje de error."""
    fin = time.time() + espera_max
    while time.time() < fin:
        r = _get(cfg, contenedor, {"fields": "status_code"})
        estado = r.json().get("status_code") if r.status_code == 200 else None
        if estado == "FINISHED":
            return None
        if estado in ("ERROR", "EXPIRED"):
            return "Instagram no pudo procesar el video (revisa que sea .mp4 vertical, de 3 s a 15 min y con enlace público)."
        time.sleep(5)
    return "Instagram sigue procesando el video. Intenta publicar de nuevo en un par de minutos."


def publicar_instagram(cfg: ConfigMeta, texto: str, imagenes: list | None = None,
                       video: str | None = None) -> ResultadoRed:
    if not cfg.activo_instagram:
        return ResultadoRed("instagram", False, "Publicación directa apagada (faltan META_IG_USER_ID / META_PAGE_TOKEN).")
    imagenes = [enlace_directo_drive(i) for i in (imagenes or [])]
    video = enlace_directo_drive(video) if video else None
    if not imagenes and not video:
        return ResultadoRed("instagram", False, "Instagram necesita una foto o un video: pega su enlace público en 'Fotos o video'.")
    ig = cfg.ig_user_id
    try:
        if video:
            r = _post(cfg, f"{ig}/media", {"media_type": "REELS", "video_url": video, "caption": texto, "share_to_feed": "true"})
        elif len(imagenes) == 1:
            r = _post(cfg, f"{ig}/media", {"image_url": imagenes[0], "caption": texto})
        else:
            hijos = []
            for img in imagenes:
                rh = _post(cfg, f"{ig}/media", {"image_url": img, "is_carousel_item": "true"})
                if rh.status_code != 200:
                    return ResultadoRed("instagram", False, _error_meta(rh))
                hijos.append(rh.json()["id"])
            r = _post(cfg, f"{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(hijos), "caption": texto})
        if r.status_code != 200:
            return ResultadoRed("instagram", False, _error_meta(r))
        contenedor = r.json()["id"]
        if video:
            problema = _esperar_contenedor(cfg, contenedor)
            if problema:
                return ResultadoRed("instagram", False, problema)
        rp = _post(cfg, f"{ig}/media_publish", {"creation_id": contenedor})
        if rp.status_code != 200:
            return ResultadoRed("instagram", False, _error_meta(rp))
        media_id = rp.json().get("id")
        permalink = None
        if media_id:
            rl = _get(cfg, media_id, {"fields": "permalink"})
            if rl.status_code == 200:
                permalink = rl.json().get("permalink")
    except Exception as e:
        return ResultadoRed("instagram", False, f"No se pudo conectar con Instagram: {e}")
    return ResultadoRed("instagram", True, "Publicado en Instagram.", permalink)


# ------------------------------------------------------------------
# 5. Registro: qué salió y dónde (cabe en url_publicada, sin migración)
# ------------------------------------------------------------------
def unir_enlaces(previo: str | None, nuevos: dict) -> str:
    """url_publicada guarda 'red: enlace | red: enlace'. Si antes había un
    enlace suelto (blog), se conserva."""
    actuales: dict = {}
    for parte in (previo or "").split(" | "):
        parte = parte.strip()
        if not parte:
            continue
        red, sep, url = parte.partition(": ")
        if sep and red in REDES:
            actuales[red] = url
        else:
            actuales.setdefault("_", parte)
    actuales.update({k: v for k, v in nuevos.items() if v})
    orden = ["_"] + list(REDES)
    return " | ".join((actuales[k] if k == "_" else f"{k}: {actuales[k]}") for k in orden if k in actuales)


def redes_publicadas(url_publicada: str | None) -> set:
    return {p.partition(": ")[0] for p in (url_publicada or "").split(" | ") if p.partition(": ")[0] in REDES}

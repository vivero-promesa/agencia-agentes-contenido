import streamlit as st
import os
import csv
import io
from urllib.parse import quote
from dotenv import load_dotenv
from supabase import create_client, Client

# Importaciones de agentes
from agente import redactar_guion_viral, redactar_articulo_seo

# ==========================================
# 🚨 BLOQUE DE DIAGNÓSTICO (CAZADOR DE ERRORES)
# Streamlit Cloud redacta el mensaje real de ImportError por seguridad.
# Este bloque lo captura y lo muestra en pantalla para saber la causa
# exacta (nombre no encontrado, error de sintaxis interno, dependencia
# faltante, etc.) en vez de adivinar.
# ==========================================
try:
    from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario, generar_seo_por_intencion
except Exception as e:
    st.error("🚨 Error real detectado al importar 'agentes_crecimiento.py':")
    st.exception(e)
    st.stop()
# ==========================================

from agente_audio import generar_audio_elevenlabs
from agente_video import ejecutar_pipeline_agencia
from agente_blog import redactar_articulo_blog
from competencia import analizar_contra_competencia, proponer_estrategia_desde_competencia
from estrategia import obtener_prioridad_estrategica, guardar_prioridad_estrategica, CLAVE_DOLORES_INTERMEDIARIOS, CLAVE_ESTRATEGIA_COMPETITIVA, cluster_ya_ejecutado, registrar_cluster_ejecutado

# ==========================================
# 0. CONFIGURACIÓN DEL CENTRO DE COMANDO
# ==========================================
# Nombre de marca visible en la interfaz — un solo lugar para cambiarlo.
MARCA_UI = "viveroonline.com.co"

st.set_page_config(page_title=f"Agencia {MARCA_UI}", layout="wide", page_icon="🌱")
st.title(f"🌱 Centro de Comando · {MARCA_UI}")

load_dotenv()


def secreto(nombre: str, defecto=None):
    """Lee primero st.secrets (nube) y luego .env/variables de entorno (local).
    No revienta si no existe secrets.toml en local."""
    try:
        valor = st.secrets.get(nombre)
        if valor:
            return valor
    except Exception:
        pass
    return os.getenv(nombre, defecto)


# ==========================================
# ARQUITECTURA DE DOBLE BASE DE DATOS
# ==========================================
# 1. MARKETPLACE (solo LECTURA): inventario, plantas, viveros
url_mkt = secreto("SUPABASE_URL_EXTERNA")
key_mkt = secreto("SUPABASE_SERVICE_KEY")
supabase_mkt = create_client(url_mkt, key_mkt) if url_mkt and key_mkt else None

# 2. AGENCIA (LECTURA/ESCRITURA): historial_contenidos, campanas_ejecutadas
url_ag = secreto("SUPABASE_URL_AGENCIA")
key_ag = secreto("SUPABASE_KEY_AGENCIA")
supabase_ag = create_client(url_ag, key_ag) if url_ag and key_ag else None

# Número oficial de WhatsApp de la plataforma (el comprador nunca habla
# directo con el viverista: la plataforma hace de puente). Se puede cambiar
# con el secret WHATSAPP_NUMERO sin tocar código.
WHATSAPP_NUMERO = "".join(ch for ch in str(secreto("WHATSAPP_NUMERO", "573178543819")) if ch.isdigit())

# Categorías del inventario que tienen sentido para una campaña de planta viva
CATEGORIAS_CAMPANA_DEFAULT = ["plantas_ornamentales", "arboles"]


# ==========================================
# HELPERS COMPARTIDOS
# ==========================================
def es_error_agente(texto) -> bool:
    """Los agentes de texto devuelven mensajes tipo '⚠️ Error...' o '❌ Fallo...'
    en vez de lanzar excepción. Esto evita que esos mensajes se guarden en el
    Historial como si fueran contenido real."""
    if not texto or not isinstance(texto, str):
        return True
    inicio = texto.strip()[:3]
    return inicio.startswith("⚠️") or inicio.startswith("❌")


def link_whatsapp(texto: str) -> str:
    """Construye el enlace wa.me de forma determinística (no lo inventa la IA)
    hacia el número oficial de la plataforma, con el copy codificado."""
    return f"https://wa.me/{WHATSAPP_NUMERO}?text={quote(texto or '')}"


def limpiar_widgets(*keys):
    """Streamlit ignora el parámetro value= de un widget que ya tiene key en
    session_state. Si se genera contenido nuevo y no se borran estas keys,
    la pantalla sigue mostrando el texto VIEJO. Llamar antes de st.rerun()."""
    for k in keys:
        st.session_state.pop(k, None)


def guardar_en_historial(registros) -> int:
    """Inserta en historial_contenidos solo lo que es contenido real (descarta
    vacíos y mensajes de error de los agentes). Devuelve cuántos guardó."""
    if not supabase_ag:
        st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        return 0
    if isinstance(registros, dict):
        registros = [registros]
    validos = [r for r in registros if not es_error_agente(r.get("contenido"))]
    descartados = len(registros) - len(validos)
    if descartados:
        st.warning(f"{descartados} pieza(s) no se guardaron porque el agente devolvió un error o vino vacía.")
    if not validos:
        return 0
    for r in validos:
        r.setdefault("estado", "borrador")
    try:
        supabase_ag.table("historial_contenidos").insert(validos).execute()
        return len(validos)
    except Exception as e:
        st.error(f"No se pudo guardar en el Historial: {e}")
        return 0


def nombre_planta(planta: dict, planta_id=None) -> str:
    """Prefiere nombre común + científico (el comprador busca por nombre común).
    Antes el escáner tomaba la primera columna con 'nombre' → nombre_cientifico."""
    planta = planta or {}
    comun = planta.get("nombre_comun")
    cientifico = planta.get("nombre_cientifico")
    if comun and cientifico and comun.strip().lower() != cientifico.strip().lower():
        return f"{comun} ({cientifico})"
    if comun or cientifico:
        return comun or cientifico
    # Respaldo: escáner dinámico por si cambian los nombres de columnas
    for k, v in planta.items():
        if ("nombre" in k.lower() or "especie" in k.lower()) and v:
            return v
    return f"Planta #{planta_id}" if planta_id is not None else "Planta"


def municipio_vivero(vivero: dict) -> str:
    """Municipio público del lote. 'ubicacion' viene vacío en la BD real, por
    eso antes todo salía como 'Sabana de Bogotá'. Nunca se usa la dirección."""
    vivero = vivero or {}
    return (
        vivero.get("ciudad")
        or vivero.get("municipio")
        or (vivero.get("ubicacion") if isinstance(vivero.get("ubicacion"), str) else None)
        or "Sabana de Bogotá"
    )


def datos_publicos_lote(item: dict, planta: dict, vivero: dict) -> dict:
    """Datos que SÍ pueden ir en contenido público. El nombre del vivero NO se
    publica: el comprador no contacta al viverista, la plataforma hace de puente
    (y publicarlo invita a saltarse el marketplace)."""
    municipio = municipio_vivero(vivero)
    datos = {
        "especie": nombre_planta(planta, item.get("planta_id")),
        "cantidad": item.get("stock"),
        "ubicacion": municipio,
        "vendedor": f"Vivero aliado verificado de {MARCA_UI} en {municipio}",
    }
    if item.get("altura_cm"):
        altura = f"{item['altura_cm']} cm"
        if item.get("altura_cm_max"):
            altura = f"{item['altura_cm']}–{item['altura_cm_max']} cm"
        datos["altura"] = altura
    if item.get("formato_comercial"):
        datos["formato"] = item["formato_comercial"]
    if (planta or {}).get("uso_paisajistico"):
        datos["uso_paisajistico"] = planta["uso_paisajistico"]
    if (planta or {}).get("clima_ideal"):
        datos["clima_ideal"] = planta["clima_ideal"]
    return datos


def mostrar_articulo_seo(articulo, prefijo: str):
    """Muestra H1, slug y meta description (antes se generaban pero nunca se
    mostraban) + el cuerpo, con descarga en Markdown para WordPress."""
    st.markdown(f"### {articulo.titulo_h1}")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Slug sugerido")
        st.code(getattr(articulo, "slug", "") or "", language=None)
    with c2:
        st.caption("Meta description")
        st.code(getattr(articulo, "meta_description", "") or "", language=None)
    st.markdown(articulo.contenido_md)
    st.download_button(
        "⬇️ Descargar .md",
        data=f"# {articulo.titulo_h1}\n\n{articulo.contenido_md}",
        file_name=f"{(getattr(articulo, 'slug', '') or 'articulo').strip('/')}.md",
        mime="text/markdown",
        key=f"{prefijo}_descargar_md",
    )


def bloque_whatsapp(wa, prefijo: str):
    """Copy + guion editables, enlace wa.me construido desde el copy EDITADO y
    nota de voz desde el guion EDITADO."""
    copy_editado = st.text_area("Copy WhatsApp:", value=wa.mensaje_texto, height=110, key=f"{prefijo}_copy")
    guion_editado = st.text_area("Guion nota de voz:", value=wa.guion_nota_voz, height=150, key=f"{prefijo}_script")
    st.markdown(f"[🔗 Abrir en WhatsApp con este copy]({link_whatsapp(copy_editado)})")
    if st.button("🎧 Generar nota de voz", key=f"{prefijo}_audio"):
        with st.spinner("Sintetizando audio (voz es-CO Gonzalo)..."):
            audio = generar_audio_elevenlabs(guion_editado)
            if audio:
                st.audio(audio, format="audio/mp3")
                st.download_button("⬇️ Descargar audio", data=audio, file_name="nota_de_voz.mp3", mime="audio/mpeg", key=f"{prefijo}_audio_dl")
            else:
                st.warning("No se pudo generar el audio.")
    return copy_editado, guion_editado


@st.cache_data(ttl=300, show_spinner=False)
def lotes_pendientes(_mkt, _ag, categorias: tuple, limite: int = 200):
    """Lotes disponibles (stock ≥ 20) de las categorías elegidas que todavía no
    tienen campaña. Cache de 5 minutos para no consultar en cada clic."""
    q = (
        _mkt.table("inventario").select("*")
        .eq("estado_planta", "disponible").gte("stock", 20)
    )
    if categorias:
        q = q.in_("categoria_producto", list(categorias))
    inv = q.order("inventario_id", desc=True).limit(limite).execute().data or []
    hechos = _ag.table("campanas_ejecutadas").select("inventario_id").execute().data or []
    procesados = {c["inventario_id"] for c in hechos}
    pendientes = [l for l in inv if l["inventario_id"] not in procesados]
    ids_planta = list({l["planta_id"] for l in pendientes if l.get("planta_id") is not None})
    ids_vivero = list({l["vivero_id"] for l in pendientes if l.get("vivero_id") is not None})
    plantas = {p["planta_id"]: p for p in (_mkt.table("plantas").select("*").in_("planta_id", ids_planta).execute().data or [])} if ids_planta else {}
    viveros = {v["vivero_id"]: v for v in (_mkt.table("viveros").select("*").in_("vivero_id", ids_vivero).execute().data or [])} if ids_vivero else {}
    return pendientes, plantas, viveros


@st.cache_data(ttl=120, show_spinner=False)
def kpis_historial(_ag):
    filas = _ag.table("historial_contenidos").select("tipo_contenido, estado, genero_venta").execute().data or []
    total = len(filas)
    aprobados = sum(1 for f in filas if (f.get("estado") or "borrador") == "aprobado")
    ventas = sum(1 for f in filas if f.get("genero_venta") is True)
    con_dato = sum(1 for f in filas if f.get("genero_venta") is not None)
    return {"total": total, "aprobados": aprobados, "borradores": total - aprobados, "ventas": ventas, "con_dato": con_dato}


def cargar_estrategia(forzar: bool = False):
    if forzar or "prioridad_estrategica" not in st.session_state:
        st.session_state.prioridad_estrategica = obtener_prioridad_estrategica(supabase_ag)
    if forzar or "dolores_intermediarios" not in st.session_state:
        st.session_state.dolores_intermediarios = obtener_prioridad_estrategica(supabase_ag, clave=CLAVE_DOLORES_INTERMEDIARIOS)
    if forzar or "estrategia_competitiva" not in st.session_state:
        st.session_state.estrategia_competitiva = obtener_prioridad_estrategica(supabase_ag, clave=CLAVE_ESTRATEGIA_COMPETITIVA)


# Prioridad, dolores y competencia — se leen una vez por sesión (y se pueden
# recargar desde la barra lateral si se editaron en otra pestaña/dispositivo).
cargar_estrategia()

# ==========================================
# BARRA LATERAL: ESTADO DEL SISTEMA
# ==========================================
with st.sidebar:
    st.header("🩺 Estado del sistema")
    estado_conexiones = {
        "Marketplace (lectura)": bool(supabase_mkt),
        "Agencia (escritura)": bool(supabase_ag),
        "Groq (textos)": bool(secreto("GROQ_API_KEY")),
        "Gemini (SEO / WhatsApp / FAQ)": bool(secreto("GEMINI_API_KEY")),
    }
    for nombre, ok in estado_conexiones.items():
        st.write(("🟢 " if ok else "🔴 ") + nombre)

    st.markdown("---")
    st.subheader("🧭 Estrategia cargada")
    st.write(("🟢" if (st.session_state.prioridad_estrategica or "").strip() else "⚪") + " Prioridad actual")
    st.write(("🟢" if (st.session_state.dolores_intermediarios or "").strip() else "⚪") + " Dolores frente a intermediarios")
    st.write(("🟢" if (st.session_state.estrategia_competitiva or "").strip() else "⚪") + " Estrategia competitiva")
    if not (st.session_state.estrategia_competitiva or "").strip():
        st.caption("La estrategia competitiva está vacía: el pitch competitivo y la propuesta no pueden funcionar hasta que la escribas.")
    if st.button("🔄 Recargar desde Supabase"):
        cargar_estrategia(forzar=True)
        lotes_pendientes.clear()
        kpis_historial.clear()
        limpiar_widgets("txt_prioridad", "txt_dolores", "txt_competencia")
        st.rerun()

    if supabase_ag:
        st.markdown("---")
        st.subheader("📊 Resultados")
        try:
            k = kpis_historial(supabase_ag)
            c1, c2 = st.columns(2)
            c1.metric("Piezas", k["total"])
            c2.metric("Aprobadas", k["aprobados"])
            c1.metric("Con venta", k["ventas"])
            c2.metric("Con dato de venta", k["con_dato"])
        except Exception as e:
            st.caption(f"No se pudieron leer los KPIs: {e}")

# ==========================================
# ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_competencia, tab_estrategia, tab_360, tab_texto, tab_whatsapp, tab_video, tab_seo, tab_blog, tab_historial = st.tabs([
    "🧠 Competencia", "⚙️ Estrategia", "🔥 Campaña 360", "📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO", "📰 Blog GEO/AEO", "📜 Historial"
])

# ==========================================
# --- PESTAÑA: ESTRATEGIA ---
# ==========================================
with tab_estrategia:
    st.subheader("Prioridad Estratégica Actual")
    st.caption(
        "Esto no reemplaza el tono de marca (identidad_marca.py) ni la "
        "identidad visual (brand_book.py) — es el énfasis de negocio del "
        "momento (ej. \"generar transacciones reales\") que ajusta el CTA "
        "de los agentes orientados al mercado institucional."
    )
    nueva_prioridad = st.text_area(
        "Prioridad actual:",
        value=st.session_state.prioridad_estrategica,
        height=150,
        key="txt_prioridad"
    )
    if nueva_prioridad != st.session_state.prioridad_estrategica:
        st.caption("✏️ Tienes cambios sin guardar — los agentes siguen usando la versión guardada.")
    if st.button("💾 Guardar Prioridad"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nueva_prioridad)
            if ok:
                st.session_state.prioridad_estrategica = nueva_prioridad
                st.success("Prioridad estratégica actualizada. Los próximos contenidos ya la usarán.")
            else:
                st.error("No se pudo guardar en Supabase. Revisa que la tabla configuracion_estrategica exista.")

    st.markdown("---")
    st.subheader("Dolores del Viverista frente a Intermediarios Tradicionales")
    st.caption(
        "Escribe esto a mano — a propósito, ningún agente lo genera "
        "automáticamente, para no inventar quejas o competidores que no son "
        "reales. Los agentes de SEO lo usan como contexto cuando el tema lo "
        "amerita."
    )
    nuevos_dolores = st.text_area(
        "Dolores frente a intermediarios:",
        value=st.session_state.dolores_intermediarios,
        height=150,
        placeholder="Ej: El viverista pierde entre 30-40% del margen con intermediarios que no aportan logística ni visibilidad real...",
        key="txt_dolores"
    )
    if nuevos_dolores != st.session_state.dolores_intermediarios:
        st.caption("✏️ Tienes cambios sin guardar.")
    if st.button("💾 Guardar Dolores"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nuevos_dolores, clave=CLAVE_DOLORES_INTERMEDIARIOS)
            if ok:
                st.session_state.dolores_intermediarios = nuevos_dolores
                st.success("Dolores actualizados. El SEO proactivo ya los usará como contexto.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("🚀 Generar Campaña desde la Estrategia")
    st.caption(
        "Usa la Prioridad y los Dolores de arriba (guárdalos primero) más un "
        "tema puntual, para generar Texto + WhatsApp + Video + SEO en un solo "
        "clic — y guardarlo en el Historial, igual que hace la Campaña 360, "
        "pero partiendo de la estrategia en vez del inventario."
    )
    tema_campana_estrategia = st.text_input(
        "Tema / ángulo de la campaña:",
        placeholder="Ej: Palmas Botella para constructoras en la Sabana de Bogotá",
        key="tema_campana_estrategia"
    )
    audiencia_campana_estrategia = st.radio(
        "Audiencia del WhatsApp:",
        options=["institucional", "viverista"],
        format_func=lambda x: "Comprador institucional" if x == "institucional" else "Viverista",
        horizontal=True,
        key="audiencia_campana_estrategia"
    )
    forzar_duplicado_estrategia = st.checkbox(
        "Generar de todas formas aunque ya exista un artículo SEO para este tema (no recomendado — riesgo de competir contigo mismo en Google)",
        key="forzar_duplicado_estrategia"
    )

    if st.button("⚡ Generar Campaña desde Estrategia", type="primary"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        elif not tema_campana_estrategia:
            st.warning("Escribe un tema o ángulo para la campaña.")
        else:
            cluster_existente = cluster_ya_ejecutado(supabase_ag, tema_campana_estrategia)
            if cluster_existente and not forzar_duplicado_estrategia:
                st.warning(
                    f"⚠️ Ya generaste SEO para un tema igual o muy parecido "
                    f"(\"{cluster_existente.get('cluster_original', tema_campana_estrategia)}\") "
                    f"el {cluster_existente.get('fecha_creacion', 'anteriormente')}. "
                    f"Generar otro artículo para el mismo tema compite contigo mismo en "
                    f"buscadores (keyword cannibalization). Si de verdad quieres otro ángulo "
                    f"distinto, marca la casilla de arriba para continuar."
                )
            else:
                with st.spinner("Generando campaña completa a partir de la estrategia..."):
                    try:
                        prioridad_actual = st.session_state.prioridad_estrategica
                        dolores_actuales = st.session_state.dolores_intermediarios

                        texto_res = redactar_articulo_seo(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        wa_res = generar_campana_whatsapp(
                            tema_campana_estrategia,
                            numero=WHATSAPP_NUMERO,
                            audiencia=audiencia_campana_estrategia,
                            prioridad_estrategica=prioridad_actual
                        )
                        video_res = redactar_guion_viral(tema_campana_estrategia, prioridad_estrategica=prioridad_actual)
                        seo_res = generar_seo_por_intencion(
                            tema_campana_estrategia,
                            dolores_intermediarios=dolores_actuales,
                            prioridad_estrategica=prioridad_actual
                        )

                        # estado "borrador": nada se considera listo hasta revisarlo en Historial.
                        # guardar_en_historial descarta vacíos y mensajes de error de los agentes.
                        registros = [
                            {"tipo_contenido": "TEXTO", "titulo": tema_campana_estrategia, "contenido": texto_res},
                            {"tipo_contenido": "WHATSAPP", "titulo": f"WhatsApp — {tema_campana_estrategia}", "contenido": wa_res.mensaje_texto if wa_res else ""},
                            {"tipo_contenido": "VIDEO", "titulo": f"Guion Video — {tema_campana_estrategia}", "contenido": video_res},
                        ]
                        if seo_res:
                            registros.append({"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1, "contenido": seo_res.contenido_md})

                        guardados = guardar_en_historial(registros)
                        # El candado SEO se cierra solo si el artículo SEO sí se generó
                        if seo_res:
                            registrar_cluster_ejecutado(supabase_ag, tema_campana_estrategia)
                        kpis_historial.clear()

                        st.session_state.campana_estrategia_data = {
                            "tema": tema_campana_estrategia,
                            "texto": texto_res,
                            "wa": wa_res,
                            "video": video_res,
                            "seo": seo_res,
                            "guardados": guardados,
                        }
                        st.session_state.campana_estrategia_lista = True
                        limpiar_widgets("ce_wa_copy", "ce_wa_script")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generando la campaña desde estrategia: {e}")

    if st.session_state.get("campana_estrategia_lista"):
        data = st.session_state.campana_estrategia_data
        st.success(f"Campaña generada — tema: {data['tema']} · {data.get('guardados', 0)} pieza(s) guardadas en el Historial como borrador.")

        with st.expander("📝 Texto", expanded=True):
            if es_error_agente(data["texto"]):
                st.warning(data["texto"] or "El agente de texto no devolvió resultado.")
            else:
                st.write(data["texto"])

        with st.expander("💬 WhatsApp"):
            if data["wa"]:
                bloque_whatsapp(data["wa"], "ce_wa")
            else:
                st.warning("El agente de WhatsApp no devolvió resultado.")

        with st.expander("🎬 Video (concepto)"):
            st.write(data["video"])

        with st.expander("🚀 SEO Proactivo"):
            if data["seo"]:
                mostrar_articulo_seo(data["seo"], "ce_seo")
            else:
                st.warning("El agente de SEO no devolvió resultado (el candado anti-duplicidad NO se cerró, puedes reintentar).")

# ==========================================
# --- PESTAÑA: TEXTOS ---
# ==========================================
with tab_texto:
    st.subheader("Redacción de Artículos y Copy B2B")
    tema_texto = st.text_input("Tema o requerimiento del texto:", placeholder="Ej: Beneficios de especies nativas en proyectos de paisajismo")

    if st.button("Generar Texto B2B"):
        if tema_texto:
            with st.spinner("El agente está redactando..."):
                try:
                    resultado_texto = redactar_articulo_seo(tema_texto, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    if es_error_agente(resultado_texto):
                        st.error(resultado_texto or "El agente no devolvió respuesta.")
                    else:
                        st.session_state.texto_data = {"tema": tema_texto, "contenido": resultado_texto}
                        st.session_state.texto_guardado = False
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Por favor ingresa un tema.")

    # Renderizado persistente: antes el texto desaparecía con cualquier clic
    if st.session_state.get("texto_data"):
        data = st.session_state.texto_data
        st.success(f"Texto generado — tema: {data['tema']}")
        st.write(data["contenido"])
        if st.session_state.get("texto_guardado"):
            st.caption("✅ Ya está en el Historial.")
        elif st.button("💾 Guardar en Historial como borrador", key="texto_guardar"):
            if guardar_en_historial({"tipo_contenido": "TEXTO", "titulo": data["tema"], "contenido": data["contenido"]}):
                st.session_state.texto_guardado = True
                kpis_historial.clear()
                st.success("Guardado en el Historial como borrador.")

# ==========================================
# --- PESTAÑA: WHATSAPP ---
# ==========================================
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    st.caption(
        "Texto para copiar y enviar a mano (no está conectado a la API de Meta). "
        f"El enlace siempre apunta al WhatsApp oficial de la plataforma (+{WHATSAPP_NUMERO}): "
        "el comprador nunca habla directo con el viverista."
    )
    audiencia_wa = st.radio(
        "¿A quién le escribes?",
        options=["institucional", "viverista"],
        format_func=lambda x: "Comprador institucional (paisajista/constructora)" if x == "institucional" else "Viverista (productor)",
        horizontal=True
    )
    obj_wa = st.text_input("Objetivo de la campaña:", placeholder="Ej: Vender 500 Eugenias a paisajistas")

    if st.button("Generar Kit de WhatsApp"):
        if obj_wa:
            with st.spinner("Conectando con Agente de Crecimiento..."):
                campana = generar_campana_whatsapp(obj_wa, numero=WHATSAPP_NUMERO, audiencia=audiencia_wa, prioridad_estrategica=st.session_state.prioridad_estrategica)
                if campana:
                    st.session_state.wa_kit = campana
                    st.session_state.wa_kit_meta = {"objetivo": obj_wa, "audiencia": audiencia_wa}
                    st.session_state.wa_guardado = False
                    # Sin esto, un segundo kit seguía mostrando el texto del primero
                    limpiar_widgets("wa_copy", "wa_script")
                    st.rerun()
                else:
                    st.error("El agente de crecimiento no pudo responder.")
        else:
            st.warning("Por favor ingresa un objetivo.")

    # Renderizado persistente (el botón de audio funciona sin borrar pantalla)
    if st.session_state.get("wa_kit"):
        meta = st.session_state.wa_kit_meta
        st.success(f"Kit para {'viverista' if meta['audiencia'] == 'viverista' else 'comprador institucional'} — {meta['objetivo']}")
        copy_actual, _ = bloque_whatsapp(st.session_state.wa_kit, "wa")
        st.markdown("---")
        if st.session_state.get("wa_guardado"):
            st.caption("✅ Ya está en el Historial.")
        elif st.button("💾 Guardar copy en Historial", key="wa_guardar"):
            if guardar_en_historial({"tipo_contenido": "WHATSAPP", "titulo": f"WhatsApp ({meta['audiencia']}) — {meta['objetivo']}", "contenido": copy_actual}):
                st.session_state.wa_guardado = True
                kpis_historial.clear()
                st.success("Guardado en el Historial como borrador.")

# ==========================================
# --- PESTAÑA: VIDEO (B-Roll y Producción Veo 3.1) ---
# Sin cambios: el módulo de video se queda tal como está (se opera a mano
# con Google Vids).
# ==========================================
with tab_video:
    st.subheader("🎬 Producción de Video B2B (Veo 3.1)")
    st.markdown("Diseña el concepto estratégico y renderiza los clips directamente con la API de Google.")

    # PASO 1: IDEACIÓN
    with st.expander("📝 1. Pre-Producción (Generar Concepto y Guion)", expanded=True):
        tema_video = st.text_input("Concepto visual del comercial:", placeholder="Ej: Lote mayorista de eugenias para constructoras")
        if st.button("Generar Concepto Visual"):
            if tema_video:
                with st.spinner("Estructurando tomas, guion y copy para redes..."):
                    try:
                        resultado_video = redactar_guion_viral(tema_video, prioridad_estrategica=st.session_state.prioridad_estrategica)
                        st.success("Concepto generado. Úsalo como inspiración para tu Storyboard.")
                        st.write(resultado_video)
                    except Exception as e:
                        st.error(f"Error técnico: {e}")
            else:
                st.warning("Ingresa un concepto primero.")

    # PASO 2: RENDERIZADO EN LA NUBE (GOOGLE VEO 3.1)
    with st.expander("🎥 2. Producción (Renderizar Escenas)", expanded=False):
        st.markdown("Pega el JSON de tu storyboard para enviar las instrucciones técnicas de renderizado a Google Veo.")

        plantilla_json = '''{
    "escena_1": {
        "nombre": "Inicio de Jornada",
        "tipo": "IA_GENERATIVE",
        "visual": "Viverista revisando sus plantas temprano en la mañana, hojas húmedas de riego",
        "emocion": "Cercana, tranquila, orgullo por el oficio",
        "camara": "Plano general, movimiento suave hacia adelante",
        "texto": "Cada planta, revisada a mano"
    },
    "escena_2": {
        "nombre": "Detalle de Calidad",
        "tipo": "IA_GENERATIVE",
        "visual": "Manos con tierra inspeccionando raíces blancas y sustrato",
        "emocion": "Confianza y conocimiento del oficio",
        "camara": "Plano detalle (macro), enfoque nítido",
        "texto": "Años de experiencia en cada raíz"
    }
}'''
        storyboard_input = st.text_area("Storyboard (Formato JSON):", value=plantilla_json, height=250)

        if st.button("🚀 Iniciar Renderizado", type="primary"):
            with st.spinner("Conectando con Google Veo 3.1 y renderizando clips... (Esto toma tiempo)"):
                try:
                    resultados_render = ejecutar_pipeline_agencia(storyboard_input)
                    if resultados_render:
                        st.success("¡Pipeline de producción finalizado!")
                        for key, data in resultados_render.items():
                            st.markdown(f"### {key.replace('_', ' ').title()}")
                            if data["status"] == "Listo" and data.get("url"):
                                st.video(data["url"])
                                st.caption(f"**Texto sugerido para edición:** {data.get('texto', '')}")
                            else:
                                st.warning(f"**Estado:** {data['status']} - {data.get('texto', '')}")
                    else:
                        st.error("No se pudieron generar los videos. Revisa los logs o tu cuota de API.")
                except Exception as e:
                    st.error(f"Error crítico en el orquestador: {e}")

# ==========================================
# --- PESTAÑA: SEO PROGRAMÁTICO (lee del MARKETPLACE) ---
# ==========================================
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")

    modo_seo = st.radio(
        "Modo de operación:",
        ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual", "🎯 Proactivo (Intención de Búsqueda)"],
        horizontal=True
    )

    if modo_seo == "📡 Automatizado (Base de Datos)":
        st.caption("Toma el lote disponible más reciente (stock ≥ 20) de plantas ornamentales o árboles. El nombre del vivero no se publica.")
        if st.button("Analizar BD y Generar SEO"):
            if not supabase_mkt:
                st.error("Falta configurar la conexión al Marketplace en los Secrets (SUPABASE_URL_EXTERNA / SUPABASE_SERVICE_KEY).")
            else:
                with st.spinner("Leyendo inventario y generando contenido..."):
                    try:
                        res_inv = supabase_mkt.table("inventario") \
                            .select("*") \
                            .eq("estado_planta", "disponible") \
                            .gte("stock", 20) \
                            .in_("categoria_producto", CATEGORIAS_CAMPANA_DEFAULT) \
                            .order("inventario_id", desc=True) \
                            .limit(1) \
                            .execute()

                        if not res_inv.data:
                            st.warning("No hay inventario 'disponible' con 20 o más unidades en este momento.")
                        else:
                            item = res_inv.data[0]
                            planta_rows = supabase_mkt.table("plantas").select("*").eq("planta_id", item["planta_id"]).execute().data
                            vivero_rows = supabase_mkt.table("viveros").select("*").eq("vivero_id", item["vivero_id"]).execute().data
                            planta_data = planta_rows[0] if planta_rows else {}
                            vivero_data = vivero_rows[0] if vivero_rows else {}

                            datos_auto = datos_publicos_lote(item, planta_data, vivero_data)
                            st.write(
                                f"📊 **Datos extraídos:** {datos_auto['especie']} | Stock: {datos_auto['cantidad']} | "
                                f"{datos_auto['ubicacion']} · interno: {vivero_data.get('nombre_vivero', 'vivero sin nombre')} (no se publica)"
                            )

                            articulo = generar_seo_desde_inventario(datos_auto, prioridad_estrategica=st.session_state.prioridad_estrategica)
                            if articulo:
                                st.session_state.seo_auto = articulo
                                st.session_state.seo_auto_guardado = False
                            else:
                                st.error("El motor de IA no devolvió un formato válido.")
                    except Exception as e:
                        st.error(f"Error en la consulta automática: {e}")

        if st.session_state.get("seo_auto"):
            st.success("Artículo estratégico B2B generado.")
            mostrar_articulo_seo(st.session_state.seo_auto, "seo_auto")
            if st.session_state.get("seo_auto_guardado"):
                st.caption("✅ Ya está en el Historial.")
            elif st.button("💾 Guardar en Historial como borrador", key="seo_auto_guardar"):
                a = st.session_state.seo_auto
                if guardar_en_historial({"tipo_contenido": "SEO", "titulo": a.titulo_h1, "contenido": a.contenido_md}):
                    st.session_state.seo_auto_guardado = True
                    kpis_historial.clear()
                    st.success("Guardado en el Historial como borrador.")

    elif modo_seo == "✍️ Ingreso Manual":
        col1, col2 = st.columns(2)
        with col1:
            man_especie = st.text_input("Especie de planta:", placeholder="Ej: Palma Areca")
            man_altura = st.text_input("Altura / formato (opcional):", placeholder="Ej: 1,50 m en bolsa de 20 L")
        with col2:
            man_cantidad = st.number_input("Cantidad (Stock):", min_value=1, value=500)
            man_ubicacion = st.text_input("Municipio del lote:", placeholder="Ej: Chía")
        st.caption("El nombre del vivero ya no se pide: no se publica en contenido (la plataforma hace de puente con el comprador).")

        if st.button("Generar Artículo Manual"):
            if man_especie and man_ubicacion:
                with st.spinner("Redactando artículo estratégico..."):
                    datos_manuales = {
                        "especie": man_especie,
                        "cantidad": man_cantidad,
                        "ubicacion": man_ubicacion,
                        "vendedor": f"Vivero aliado verificado de {MARCA_UI} en {man_ubicacion}",
                    }
                    if man_altura:
                        datos_manuales["altura_formato"] = man_altura
                    articulo = generar_seo_desde_inventario(datos_manuales, prioridad_estrategica=st.session_state.prioridad_estrategica)
                    if articulo:
                        st.session_state.seo_manual = articulo
                        st.session_state.seo_manual_guardado = False
                    else:
                        st.error("El motor de IA no devolvió un formato válido.")
            else:
                st.warning("Completa especie y municipio para continuar.")

        if st.session_state.get("seo_manual"):
            st.success("Artículo manual generado.")
            mostrar_articulo_seo(st.session_state.seo_manual, "seo_manual")
            if st.session_state.get("seo_manual_guardado"):
                st.caption("✅ Ya está en el Historial.")
            elif st.button("💾 Guardar en Historial como borrador", key="seo_manual_guardar"):
                a = st.session_state.seo_manual
                if guardar_en_historial({"tipo_contenido": "SEO", "titulo": a.titulo_h1, "contenido": a.contenido_md}):
                    st.session_state.seo_manual_guardado = True
                    kpis_historial.clear()
                    st.success("Guardado en el Historial como borrador.")

    else:
        st.caption(
            "SEO PROACTIVO: escribe para capturar una búsqueda transaccional "
            "(ej. \"comprar palmas botella por lote en Bogotá\") aunque hoy no "
            "tengas ese stock exacto — construye autoridad temática para "
            "cuando sí lo tengas. No depende del inventario."
        )
        cluster_seo = st.text_input(
            "Cluster / intención de búsqueda objetivo:",
            placeholder="Ej: Comprar palmas botella por lote en Bogotá"
        )
        forzar_duplicado_seo = st.checkbox(
            "Generar de todas formas aunque ya exista un artículo para este cluster (no recomendado)",
            key="forzar_duplicado_seo"
        )
        if st.button("Generar Artículo Proactivo"):
            if not cluster_seo:
                st.warning("Escribe el cluster o intención de búsqueda objetivo.")
            else:
                cluster_existente = cluster_ya_ejecutado(supabase_ag, cluster_seo) if supabase_ag else None
                if cluster_existente and not forzar_duplicado_seo:
                    st.warning(
                        f"⚠️ Ya existe un artículo para un cluster igual o muy parecido "
                        f"(\"{cluster_existente.get('cluster_original', cluster_seo)}\"), generado el "
                        f"{cluster_existente.get('fecha_creacion', 'anteriormente')}. Generar otro compite "
                        f"contigo mismo en buscadores (keyword cannibalization). Marca la casilla de "
                        f"arriba si de verdad es un ángulo distinto."
                    )
                else:
                    with st.spinner("Redactando artículo de intención de búsqueda..."):
                        articulo = generar_seo_por_intencion(
                            cluster_seo,
                            dolores_intermediarios=st.session_state.dolores_intermediarios,
                            prioridad_estrategica=st.session_state.prioridad_estrategica
                        )
                        if articulo:
                            st.session_state.seo_proactivo = articulo
                            if supabase_ag and guardar_en_historial({"tipo_contenido": "SEO", "titulo": articulo.titulo_h1, "contenido": articulo.contenido_md}):
                                registrar_cluster_ejecutado(supabase_ag, cluster_seo)
                                kpis_historial.clear()
                                st.session_state.seo_proactivo_nota = "Guardado en el Historial como borrador y cluster registrado."
                            else:
                                st.session_state.seo_proactivo_nota = "⚠️ No se guardó en el Historial (revisa la conexión a la Agencia)."
                        else:
                            st.error("El motor de IA no devolvió un formato válido.")

        if st.session_state.get("seo_proactivo"):
            st.success("Artículo proactivo generado.")
            st.caption(st.session_state.get("seo_proactivo_nota", ""))
            mostrar_articulo_seo(st.session_state.seo_proactivo, "seo_proactivo")

# ==========================================
# --- PESTAÑA: ORQUESTADOR 360 ---
# LEE del Marketplace | ESCRIBE en la Agencia
# ==========================================
with tab_360:
    st.subheader("🔥 Orquestador Maestro de Campaña 360")
    st.markdown("Lee el inventario del **Marketplace**, genera la campaña (SEO, WhatsApp y Video) y la guarda en la base de la **Agencia**.")

    if not supabase_mkt:
        st.error("Falta la conexión al Marketplace (SUPABASE_URL_EXTERNA / SUPABASE_SERVICE_KEY).")
    elif not supabase_ag:
        st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
    else:
        categorias_sel = st.multiselect(
            "Categorías del inventario:",
            options=["plantas_ornamentales", "arboles", "sustrato", "accesorios"],
            default=CATEGORIAS_CAMPANA_DEFAULT,
            help="Por defecto solo planta viva: sustrato y accesorios no encajan con un guion de 'revisión de calidad de la planta'."
        )
        try:
            pendientes, plantas_idx, viveros_idx = lotes_pendientes(supabase_mkt, supabase_ag, tuple(sorted(categorias_sel)))
        except Exception as e:
            pendientes, plantas_idx, viveros_idx = [], {}, {}
            st.error(f"No se pudo leer el inventario: {e}")

        if not pendientes:
            st.info("Todos los lotes disponibles de estas categorías ya tienen campaña.")
        else:
            def _etiqueta_lote(l):
                p = plantas_idx.get(l.get("planta_id"), {})
                v = viveros_idx.get(l.get("vivero_id"), {})
                return f"#{l['inventario_id']} · {nombre_planta(p, l.get('planta_id'))} · {l.get('stock')} und · {municipio_vivero(v)}"

            st.caption(f"{len(pendientes)} lote(s) sin campaña. Por defecto se propone el más reciente; puedes elegir otro.")
            lote_sel = st.selectbox("Lote para la campaña:", options=pendientes, format_func=_etiqueta_lote, key="c360_lote")

            if st.button("⚡ Lanzar Campaña 360", type="primary"):
                with st.spinner("Sincronizando agentes y ejecutando campaña..."):
                    try:
                        item = lote_sel
                        planta_data = plantas_idx.get(item.get("planta_id"), {})
                        vivero_data = viveros_idx.get(item.get("vivero_id"), {})
                        datos = datos_publicos_lote(item, planta_data, vivero_data)
                        especie, locacion = datos["especie"], datos["ubicacion"]
                        prioridad = st.session_state.prioridad_estrategica

                        seo_res = generar_seo_desde_inventario(datos, prioridad_estrategica=prioridad)
                        wa_res = generar_campana_whatsapp(
                            f"Vender lote disponible de {item['stock']} {especie} en {locacion}.",
                            numero=WHATSAPP_NUMERO,
                            audiencia="institucional",
                            prioridad_estrategica=prioridad
                        )
                        video_res = redactar_guion_viral(f"Carga logística y revisión de calidad de {especie} en {locacion}.", prioridad_estrategica=prioridad)

                        registros = [
                            {"tipo_contenido": "SEO", "titulo": seo_res.titulo_h1 if seo_res else f"SEO — {especie}", "contenido": seo_res.contenido_md if seo_res else ""},
                            {"tipo_contenido": "WHATSAPP", "titulo": f"WhatsApp — {especie} ({locacion})", "contenido": wa_res.mensaje_texto if wa_res else ""},
                            {"tipo_contenido": "VIDEO", "titulo": f"Guion Video — {especie}", "contenido": video_res},
                        ]
                        guardados = guardar_en_historial(registros)

                        # El candado del lote se cierra solo si se guardó al menos el SEO,
                        # para no "quemar" un lote cuando falló la generación.
                        if seo_res and guardados:
                            supabase_ag.table("campanas_ejecutadas").insert({"inventario_id": item["inventario_id"]}).execute()
                        lotes_pendientes.clear()
                        kpis_historial.clear()

                        st.session_state.c360_data = {
                            "lote": datos,
                            "vivero_interno": vivero_data.get("nombre_vivero", ""),
                            "seo": seo_res, "wa": wa_res, "video": video_res,
                            "guardados": guardados,
                            "candado": bool(seo_res and guardados),
                        }
                        st.session_state.c360_lista = True
                        limpiar_widgets("c360_wa_copy", "c360_wa_script", "c360_lote")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error en la orquestación: {e}")

    # Renderizado persistente (sobrevive al rerun y a clics posteriores)
    if st.session_state.get("c360_lista"):
        data = st.session_state.c360_data
        lote = data["lote"]
        st.success(f"Campaña generada · {data.get('guardados', 0)} pieza(s) guardadas en el Historial.")
        if not data.get("candado"):
            st.warning("El SEO no se generó o no se guardó: el lote NO quedó marcado como procesado, puedes reintentarlo.")
        st.info(
            f"🎯 **Campaña Activa:** {lote['cantidad']} {lote['especie']} | {lote['ubicacion']}"
            + (f" · interno: {data['vivero_interno']} (no se publica)" if data.get("vivero_interno") else "")
        )

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🚀 1. Artículo SEO B2B", expanded=True):
                if data["seo"]:
                    mostrar_articulo_seo(data["seo"], "c360_seo")
                else:
                    st.warning("El agente SEO no devolvió resultado.")

            with st.expander("🎬 3. Guion Visual (Veo 3)", expanded=True):
                if data["video"]:
                    st.write(data["video"])

        with col2:
            with st.expander("💬 2. Estrategia WhatsApp", expanded=True):
                if data["wa"]:
                    bloque_whatsapp(data["wa"], "c360_wa")
                else:
                    st.warning("El agente de WhatsApp no devolvió resultado.")

# ==========================================
# --- PESTAÑA: BLOG GEO/AEO ---
# ==========================================
with tab_blog:
    st.subheader("📰 Blog Institucional (GEO/AEO)")
    st.caption(
        "Genera artículos de blog de largo formato optimizados para que "
        "ChatGPT, Perplexity y Gemini los citen — respuesta directa, "
        "secciones autocontenidas y un bloque de Preguntas Frecuentes listo "
        "para copiar al bloque nativo FAQ de tu plugin de SEO (ej. Rank "
        "Math). Distinto de la pestaña Textos: esto es contenido de blog "
        "extenso, no copy corto."
    )

    tema_blog = st.text_input(
        "Tema del artículo (en forma de pregunta natural funciona mejor):",
        placeholder="Ej: ¿Cuánto se pierde realmente al comprar plantas ornamentales a través de un intermediario?",
        key="tema_blog"
    )
    datos_verificables_blog = st.text_area(
        "Datos verificables reales (opcional, pero recomendado):",
        placeholder="Ej: tiempo de aclimatación: 15 días; peso promedio del bulto: 12kg; margen perdido con intermediarios: 30-40%",
        height=80,
        key="datos_verificables_blog"
    )

    if st.button("📝 Generar Artículo de Blog", type="primary"):
        if not tema_blog:
            st.warning("Escribe un tema para el artículo.")
        else:
            with st.spinner("Redactando artículo de blog optimizado para GEO/AEO..."):
                try:
                    articulo_blog = redactar_articulo_blog(
                        tema_blog,
                        datos_verificables=datos_verificables_blog or None,
                        prioridad_estrategica=st.session_state.prioridad_estrategica
                    )
                    if es_error_agente(articulo_blog):
                        st.error(articulo_blog or "El agente de blog no devolvió contenido.")
                    else:
                        st.session_state.articulo_blog_data = {"tema": tema_blog, "contenido": articulo_blog}
                        st.session_state.articulo_blog_listo = True
                        st.session_state.articulo_blog_guardado = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Error técnico: {e}")

    if st.session_state.get("articulo_blog_listo"):
        data = st.session_state.articulo_blog_data
        st.success(f"Artículo generado — tema: {data['tema']}")
        st.markdown(data["contenido"])

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.get("articulo_blog_guardado"):
                st.caption("✅ Ya está en el Historial.")
            elif st.button("💾 Guardar en Historial como borrador"):
                if guardar_en_historial({"tipo_contenido": "BLOG", "titulo": data["tema"], "contenido": data["contenido"]}):
                    st.session_state.articulo_blog_guardado = True
                    kpis_historial.clear()
                    st.success("Guardado en el Historial como borrador.")
        with c2:
            st.download_button(
                "⬇️ Descargar .md para WordPress",
                data=data["contenido"],
                file_name="articulo_blog.md",
                mime="text/markdown",
                key="blog_descargar_md",
            )

# ==========================================
# --- PESTAÑA: HISTORIAL (lee de la AGENCIA) ---
# ==========================================
with tab_historial:
    st.subheader("📜 Historial de Contenido Generado")
    st.caption(
        "Todo lo generado nace como 'borrador'. Márcalo como 'aprobado' una "
        "vez lo revisaste y de verdad lo vas a usar — eso es lo que separa "
        "lo que tiene valor real de lo que fue solo una prueba. Cuando "
        "sepas si una pieza generó una venta, márcalo también: es la única "
        "forma de empezar a conectar contenido con resultado real, mientras "
        "no haya una medición automática. También puedes editar el texto "
        "directamente aquí antes de aprobarlo, o eliminar lo que no sirva."
    )
    if not supabase_ag:
        st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
    else:
        POR_PAGINA = 15
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            filtro_tipo = st.selectbox("Tipo:", ["Todos", "SEO", "BLOG", "TEXTO", "WHATSAPP", "VIDEO"], key="hist_tipo")
        with f2:
            filtro_estado = st.selectbox("Estado:", ["Todos", "borrador", "aprobado"], key="hist_estado")
        with f3:
            filtro_texto = st.text_input("Buscar en el título:", key="hist_buscar")

        try:
            q = supabase_ag.table("historial_contenidos").select("*", count="exact")
            if filtro_tipo != "Todos":
                q = q.eq("tipo_contenido", filtro_tipo)
            if filtro_estado != "Todos":
                q = q.eq("estado", filtro_estado)
            if filtro_texto.strip():
                q = q.ilike("titulo", f"%{filtro_texto.strip()}%")

            # Cuenta total para paginar (antes se cargaba TODO el historial cada vez)
            pagina = st.session_state.get("hist_pagina", 1)
            desde = (pagina - 1) * POR_PAGINA
            res = q.order("fecha_creacion", desc=True).range(desde, desde + POR_PAGINA - 1).execute()
            total = res.count or 0
            total_paginas = max(1, -(-total // POR_PAGINA))

            if not res.data:
                if total and pagina > 1:
                    st.session_state.hist_pagina = 1
                    st.rerun()
                st.info("No hay contenido con estos filtros. Lanza una Campaña 360 o genera una pieza para empezar.")
            else:
                cpag, cexp = st.columns([2, 1])
                with cpag:
                    st.caption(f"{total} pieza(s) · página {pagina} de {total_paginas}")
                with cexp:
                    buffer = io.StringIO()
                    writer = csv.writer(buffer)
                    writer.writerow(["id", "fecha_creacion", "tipo_contenido", "estado", "genero_venta", "titulo", "contenido"])
                    for r in res.data:
                        writer.writerow([r.get("id"), r.get("fecha_creacion"), r.get("tipo_contenido"), r.get("estado"), r.get("genero_venta"), r.get("titulo"), r.get("contenido")])
                    st.download_button("⬇️ Exportar esta página (CSV)", data=buffer.getvalue().encode("utf-8-sig"), file_name="historial_contenidos.csv", mime="text/csv")

                for item in res.data:
                    estado_item = item.get("estado", "borrador") or "borrador"
                    genero_venta_item = item.get("genero_venta")
                    icono_estado = "✅" if estado_item == "aprobado" else "📝"
                    icono_venta = " · 💰 venta" if genero_venta_item is True else ""
                    fecha = str(item.get("fecha_creacion", ""))[:10]
                    with st.expander(f"{icono_estado} {fecha} | {item.get('tipo_contenido', 'N/A')} | {item.get('titulo', 'Sin título')}{icono_venta}"):

                        # --- Edición de título y contenido ---
                        titulo_editado = st.text_input(
                            "Título:",
                            value=item.get("titulo", "") or "",
                            key=f"titulo_{item['id']}"
                        )
                        contenido_editado = st.text_area(
                            "Contenido:",
                            value=item.get("contenido", "") or "",
                            height=250,
                            key=f"contenido_{item['id']}"
                        )
                        if st.button("💾 Guardar cambios", key=f"guardar_edicion_{item['id']}"):
                            supabase_ag.table("historial_contenidos").update({
                                "titulo": titulo_editado,
                                "contenido": contenido_editado
                            }).eq("id", item["id"]).execute()
                            st.success("Cambios guardados.")
                            st.rerun()

                        st.markdown("---")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if estado_item != "aprobado":
                                if st.button("✅ Marcar como aprobado", key=f"aprobar_{item['id']}"):
                                    supabase_ag.table("historial_contenidos").update({"estado": "aprobado"}).eq("id", item["id"]).execute()
                                    kpis_historial.clear()
                                    st.rerun()
                            else:
                                st.caption("✅ Aprobado")
                                if st.button("↩️ Volver a borrador", key=f"desaprobar_{item['id']}"):
                                    supabase_ag.table("historial_contenidos").update({"estado": "borrador"}).eq("id", item["id"]).execute()
                                    kpis_historial.clear()
                                    st.rerun()
                        with col_b:
                            indice_venta = 0 if genero_venta_item is None else (1 if genero_venta_item is True else 2)
                            nuevo_resultado = st.selectbox(
                                "¿Generó una venta?",
                                options=["Sin dato", "Sí", "No"],
                                index=indice_venta,
                                key=f"venta_{item['id']}"
                            )
                            if st.button("Guardar resultado", key=f"guardar_venta_{item['id']}"):
                                valor_venta = {"Sin dato": None, "Sí": True, "No": False}[nuevo_resultado]
                                supabase_ag.table("historial_contenidos").update({"genero_venta": valor_venta}).eq("id", item["id"]).execute()
                                kpis_historial.clear()
                                st.rerun()

                        # --- Eliminar, con confirmación para no borrar por accidente ---
                        st.markdown("---")
                        confirmar_borrado = st.checkbox(
                            "Confirmar que quiero eliminar esto permanentemente",
                            key=f"confirmar_borrar_{item['id']}"
                        )
                        if st.button("🗑️ Eliminar", key=f"eliminar_{item['id']}", disabled=not confirmar_borrado):
                            supabase_ag.table("historial_contenidos").delete().eq("id", item["id"]).execute()
                            kpis_historial.clear()
                            st.success("Eliminado.")
                            st.rerun()

                if total_paginas > 1:
                    p1, p2, p3 = st.columns([1, 2, 1])
                    with p1:
                        if st.button("⬅️ Anterior", disabled=pagina <= 1, key="hist_prev"):
                            st.session_state.hist_pagina = pagina - 1
                            st.rerun()
                    with p3:
                        if st.button("Siguiente ➡️", disabled=pagina >= total_paginas, key="hist_next"):
                            st.session_state.hist_pagina = pagina + 1
                            st.rerun()
        except Exception as e:
            st.error(f"❌ Error técnico real: {e}")

# ==========================================
# --- PESTAÑA: COMPETENCIA ---
# ==========================================
with tab_competencia:
    st.subheader("🧠 Estrategia Competitiva")
    st.caption(
        "Escribe aquí a mano quiénes son tus competidores reales y en qué "
        "eres mejor — a propósito, ningún agente lo genera automáticamente, "
        "para no inventar competidores que no existen. Se guarda en Supabase."
    )

    nueva_estrategia_competitiva = st.text_area(
        "Estrategia competitiva:",
        value=st.session_state.estrategia_competitiva,
        height=200,
        placeholder="Ej: Vivero X — fuerte en precio, débil en puntualidad logística. Nuestra ventaja: entrega garantizada en menos de 48h.",
        key="txt_competencia"
    )
    hay_cambios_competencia = nueva_estrategia_competitiva != st.session_state.estrategia_competitiva
    if hay_cambios_competencia:
        st.caption("✏️ Tienes cambios sin guardar — la propuesta y el pitch usan la versión guardada.")
    if st.button("💾 Guardar Estrategia Competitiva"):
        if not supabase_ag:
            st.error("Falta la conexión a la Agencia (SUPABASE_URL_AGENCIA / SUPABASE_KEY_AGENCIA).")
        else:
            ok = guardar_prioridad_estrategica(supabase_ag, nueva_estrategia_competitiva, clave=CLAVE_ESTRATEGIA_COMPETITIVA)
            if ok:
                st.session_state.estrategia_competitiva = nueva_estrategia_competitiva
                st.success("Estrategia competitiva actualizada.")
            else:
                st.error("No se pudo guardar en Supabase.")

    st.markdown("---")
    st.subheader("🔗 Proponer Prioridad y Dolores desde esta Competencia")
    st.caption(
        "Genera un borrador de Prioridad y de Dolores razonando a partir de "
        "lo que escribiste arriba — no se guarda solo. Lo revisas, lo editas "
        "si quieres, y decides tú si lo mandas a la pestaña Estrategia. "
        "Puedes regenerar tantas veces como quieras antes de guardar."
    )

    def _generar_propuesta():
        with st.spinner("Razonando propuesta a partir de la competencia..."):
            prioridad_prop, dolores_prop = proponer_estrategia_desde_competencia(
                st.session_state.estrategia_competitiva,
                prioridad_actual=st.session_state.prioridad_estrategica
            )
        if not prioridad_prop and not dolores_prop:
            st.error("No se pudo generar la propuesta (revisa la conexión con Groq). La propuesta anterior se conserva.")
            return
        st.session_state.propuesta_prioridad = prioridad_prop
        st.session_state.propuesta_dolores = dolores_prop
        st.session_state.propuesta_generada = True
        # Sin esto, "Volver a generar" seguía mostrando la propuesta vieja
        limpiar_widgets("prioridad_editable_propuesta", "dolores_editable_propuesta")
        st.rerun()

    if st.button("🧠 Generar Propuesta desde la Competencia"):
        if not (st.session_state.estrategia_competitiva or "").strip():
            st.warning("Primero escribe y guarda tu estrategia competitiva arriba.")
        else:
            _generar_propuesta()

    if st.session_state.get("propuesta_generada"):
        st.markdown("**Propuesta de Prioridad** (editable antes de guardar):")
        prioridad_editable = st.text_area(
            "Prioridad propuesta:",
            value=st.session_state.propuesta_prioridad,
            height=120,
            key="prioridad_editable_propuesta"
        )
        if st.button("💾 Guardar como Prioridad Actual"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, prioridad_editable)
                if ok:
                    st.session_state.prioridad_estrategica = prioridad_editable
                    limpiar_widgets("txt_prioridad")
                    st.success("Guardado como Prioridad Actual — ya la usan todos los agentes institucionales.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        st.markdown("**Propuesta de Dolores frente a Intermediarios** (editable antes de guardar):")
        dolores_editable = st.text_area(
            "Dolores propuestos:",
            value=st.session_state.propuesta_dolores,
            height=120,
            key="dolores_editable_propuesta"
        )
        if st.button("💾 Guardar como Dolores frente a Intermediarios"):
            if not supabase_ag:
                st.error("Falta la conexión a la Agencia.")
            else:
                ok = guardar_prioridad_estrategica(supabase_ag, dolores_editable, clave=CLAVE_DOLORES_INTERMEDIARIOS)
                if ok:
                    st.session_state.dolores_intermediarios = dolores_editable
                    limpiar_widgets("txt_dolores")
                    st.success("Guardado como Dolores frente a Intermediarios — ya los usa el SEO proactivo.")
                else:
                    st.error("No se pudo guardar en Supabase.")

        if st.button("🔄 Volver a generar (no me convence esta propuesta)"):
            _generar_propuesta()

    st.markdown("---")
    test_comp = st.text_input("Generar pitch para:", placeholder="Ej: Palmas Botella por lote en Bogotá")
    if st.button("Generar Pitch Competitivo"):
        if test_comp:
            with st.spinner("Analizando ventaja competitiva..."):
                try:
                    resultado_pitch = analizar_contra_competencia(
                        test_comp,
                        estrategia_competitiva=st.session_state.estrategia_competitiva,
                        prioridad_estrategica=st.session_state.prioridad_estrategica
                    )
                    if es_error_agente(resultado_pitch):
                        st.warning(resultado_pitch)
                    else:
                        st.write(resultado_pitch)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
        else:
            st.warning("Ingresa un tema o producto para generar el pitch.")

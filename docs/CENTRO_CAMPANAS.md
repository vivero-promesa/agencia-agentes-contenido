# 📡 Centro de Campañas — Plan de acción

**Proyecto:** viverohub (www.viverohub.com) · VIVEROONLINE S.A.S.
**Fecha:** 27 nov 2026
**Estado:** plan aprobado para arrancar por la Fase 0. Todavía no hay código.
**Documento vivo (editable):** https://claude.ai/artifact/W7erd4XwxaKbTcCKz4fYzW

> Las reglas de oro están en [`REGLAS_DE_ORO.md`](REGLAS_DE_ORO.md) y se aplican a todo este módulo.

---

## 1. Resumen

Se agrega al Centro de Comando un módulo **Centro de Campañas**. Enruta cada pieza hacia Google Ads, Facebook, Instagram, TikTok y LinkedIn con un mismo código de campaña (VH-00X) y trae de vuelta los resultados. No reemplaza nada de lo construido: amplía la pestaña 📣 Campañas (brief, pilares, calendario) y el 📜 Historial, que ya existen.

El módulo hace tres cosas:
1. Genera borradores de anuncios y publicaciones por red.
2. Les pone enlaces rastreables.
3. Muestra qué campaña produjo cotizaciones y pagos.

**Publicar, activar campañas, enviar WhatsApp masivos y manejar presupuesto lo hace siempre Elena, a mano.**

Orden: cuentas ordenadas → medición en viverohub.com → enlaces rastreables → generador de anuncios y WhatsApp → datos de vuelta → cierre con ventas reales.

---

## 2. Ruta de una pieza

```
 Campaña VH-00X ──▶ Agentes ──▶ Historial (pieza aprobada + enlace UTM)
 (brief, pilares,   (textos,          │
  calendario)        anuncios,        ▼ Elena revisa
       ▲             blog)     ┌──────────────────────────────┐
       │                       │ ELENA PUBLICA A MANO         │
       │                       │ Presupuesto y pujas: solo    │
       │                       │ aquí, nunca un bot           │
       │                       └──────────────────────────────┘
       │                                      │
       │        viverohub.com ◀── Redes y anuncios (Google Ads, Facebook,
       │        (Pixel, etiqueta     Instagram, TikTok, LinkedIn, WhatsApp)
       │         de Ads, cotización,
       │         pago ePayco)
       │              │
       │              ▼
       └──── Panel de resultados (solo lectura: Search Console,
             Google Ads, Meta y ventas)
```

El único paso donde se publica o se gasta dinero es el de Elena. Todo lo demás prepara o lee.

---

## 3. Mapa de canales

| Canal | Audiencia principal | Para qué | Formato | Al inicio | Se mide con |
| --- | --- | --- | --- | --- | --- |
| Google Ads (búsqueda) | Compradores institucionales: paisajistas, constructoras, conjuntos | Captar a quien ya busca proveedor | Anuncios de búsqueda adaptables | Pagado | Cotización enviada y pago en ePayco |
| Facebook | Viveristas de la Sabana | Reclutar oferta | Anuncios que abren WhatsApp, video corto | Pagado | Conversaciones de WhatsApp con código VH-00X |
| Instagram | Compradores y paisajistas | Vitrina de proyectos y catálogo | Reels, carrusel | Orgánico; luego remarketing | Clics con UTM, Pixel de Meta |
| TikTok | Viveristas jóvenes y público del oficio | Marca y oficio | Video vertical corto | Orgánico | Clics con UTM |
| LinkedIn | Constructoras, administradores de conjuntos, arquitectos | Confianza B2B y alianzas | Página de empresa, publicaciones de la fundadora | Orgánico | Clics con UTM, contactos |
| WhatsApp | Viveristas y compradores ya registrados | Activar oferta y demanda | Plantillas de marketing aprobadas por Meta | Envío manual por lotes | Respuestas y bajas por campaña |

Instagram y Facebook se manejan desde el mismo portafolio de Meta, con un solo Pixel. LinkedIn y TikTok empiezan orgánicos; se pagan solo cuando Elena lo decida.

---

## 4. Lo que ya existe y cómo entra

Nada de lo construido se reemplaza. Cada módulo sigue igual y solo gana el código VH-00X y un enlace rastreable.

| Módulo que ya existe | Qué se le agrega | Qué no se toca |
| --- | --- | --- |
| Marca: `identidad_marca.py`, `brand_book.py`, logo, paleta (#325926, #10B981, #F89933), tipografía Inter | Carpeta de activos por red (logo en positivo y negativo, plantillas cuadrada, vertical 9:16 y horizontal) para el generador de anuncios | El texto de identidad y las reglas del Brand Book |
| Blog GEO/AEO (`agente_blog.py`, `publicador_wordpress.py`) | Enlace con UTM al compartir cada artículo; temas sugeridos con las búsquedas reales de Search Console | Generación en dos pasos, detector de duplicidad, publicación en WordPress |
| SEO de fichas (`generar_seo_por_intencion`) | Búsquedas reales de Search Console como insumo | Candado anti-duplicidad (`clusters_seo_ejecutados`) |
| Generador de pauta Google Ads (`generar_y_guardar_pauta` en `agentes_crecimiento.py`, copia en `agente_ads.py`, tabla `insights_pauta`) | **Es la base de la Fase 3**: se conecta a una pestaña, se le agrega validación de longitud en código, Meta/TikTok/LinkedIn y export CSV | Su esquema y la tabla `insights_pauta`, que ya alimenta al SEO |
| WhatsApp (`generar_campana_whatsapp`, audiencia dual) | Envío a números registrados con plantillas aprobadas, en lotes y solo con el clic de Elena | El flujo del bot, sus plantillas actuales y `plant_identifier` |
| Video (`agente_video.py`) | Nada: Elena lo opera con Google Vids | Todo el módulo |

> **Nota de auditoría (27 nov 2026):** `generar_y_guardar_pauta` existe dos veces (`agente_ads.py` y `agentes_crecimiento.py`) y ninguna está conectada a la interfaz. En la Fase 3 se usa la de `agentes_crecimiento.py`. Borrar `agente_ads.py` queda pendiente de que Elena lo apruebe.

---

## 5. WhatsApp a viveristas y compradores registrados

Es el canal más fuerte con los viveristas y también el más frágil. Si muchas personas bloquean o reportan los mensajes, Meta baja la calidad del número y puede limitarlo. Eso dejaría sin servicio al bot (+57 311 5557154). El envío se diseña para proteger el número primero.

1. **Solo a quien está registrado y aceptó recibir mensajes.** Listas leídas de la base del marketplace, separadas en viveristas y compradores. Quien pida no recibir más queda fuera para siempre.
2. **Solo plantillas aprobadas por Meta.** El agente redacta el borrador; Elena la somete a aprobación.
3. **Cada plantilla de marketing cuesta dinero, así que cuenta como presupuesto.** El botón "Enviar lote" lo pulsa solo Elena, después de ver cuántos destinatarios hay.
4. **Lotes pequeños y espaciados.** Primero un lote de prueba; el siguiente solo si la calidad del número sigue en verde.
5. **Mensaje con valor.** A viveristas: pedidos abiertos o demanda de sus especies. A compradores: lotes con precio real, entrega en unos 3 días hábiles y garantía de 72 horas.
6. **Las respuestas llegan al bot como siempre**, con el código VH-00X para atribuirlas.

**Decisión pendiente:** enviar desde el número del bot con lotes muy controlados, o abrir un segundo número solo para campañas (más seguro, pero las respuestas no caen en el bot).

---

## 6. Carpeta propuesta en este repo

```
centro_campanas/
  reglas.py            reglas de oro y bloqueo de cualquier escritura hacia las plataformas
  cuentas.py           qué cuenta de cada red pertenece a viverohub
  utm.py               generador de enlaces con el código VH-00X
  anuncios.py          usa generar_y_guardar_pauta y la amplía a Meta, TikTok y LinkedIn
  whatsapp_envios.py   listas en modo lectura, conteo, lote de prueba, envío manual
  exportar.py          CSV para Google Ads Editor y Meta
  fuentes/
    search_console.py  lectura
    google_ads.py      lectura (usuario Solo lectura)
    meta.py            lectura (permiso ads_read)
  panel.py             resultados por campaña
activos_marca/         logos y plantillas por red
migraciones/002_centro_campanas.sql
  cuentas_canal, enlaces_utm, anuncios_borrador, envios_whatsapp, metricas_campana
```

Las tablas nuevas van en la base **Agencia Vivero**. La base del marketplace solo recibe las columnas de origen de la cotización (Fase 1), en su propio repo y en rama de prueba.

---

## 7. Plan por fases

Ninguna fase arranca hasta que la anterior cumpla su criterio de "listo".

### Fase 0 — Ordenar cuentas (Elena, sin código)
- [ ] Portafolio comercial de Meta de viverohub: página de Facebook, Instagram de empresa, WhatsApp del bot y cuenta publicitaria.
- [ ] Cuenta de TikTok Business de viverohub, separada de la del podcast.
- [ ] Página de empresa de viverohub en LinkedIn.
- [ ] viverohub.com verificado en Search Console y GA4 midiendo el dominio nuevo.
- [ ] Google Ads vinculado con GA4 y Search Console.
- [ ] Usuario de Google Ads con acceso "Solo lectura" para la app.

**Listo cuando:** existe la tabla de cuentas por canal (administradora, proyecto al que pertenece) y todas son de viverohub.

### Fase 1 — Medición en viverohub.com (repo del marketplace, rama de prueba)
- [ ] Etiqueta AW-433175134 disparando en viverohub.com.
- [ ] Tres conversiones: cotización enviada, pago confirmado en ePayco, clic a WhatsApp.
- [ ] Pixel de Meta + API de Conversiones en el mismo middleware y el mismo banner de consentimiento.
- [ ] Columnas de origen en cada cotización: `gclid`, `fbclid` y UTM.

**Listo cuando:** una conversión de prueba aparece en Google Ads y en Meta, y producción sigue sin errores.

### Fase 2 — Enlaces rastreables (este repo)
- [ ] Generador de enlaces: `utm_source` (red), `utm_medium` (pagado/orgánico), `utm_campaign` (VH-00X), `utm_content` (id de la pieza).
- [ ] El Historial guarda canal y enlace, y no aprueba una pieza sin enlace.

**Listo cuando:** toda pieza aprobada se rastrea hasta su campaña.

### Fase 3 — Generador de anuncios y envíos de WhatsApp (este repo)
- [ ] Conectar `generar_y_guardar_pauta` a la interfaz, con el brief de la campaña activa, inventario real e identidad de marca.
- [ ] Google: 15 títulos ≤ 30 caracteres y 4 descripciones ≤ 90, validados en código.
- [ ] Meta, TikTok y LinkedIn: texto principal, título y llamado a la acción por red.
- [ ] Export CSV para Google Ads Editor y Meta.
- [ ] WhatsApp: vista de contactos con consentimiento, borradores de plantillas, pantalla de envío por lotes con botón manual, registro de cada envío.

**Listo cuando:** Elena sube un anuncio generado sin reescribirlo y hace un primer lote de prueba de WhatsApp sin que baje la calidad del número.

### Fase 4 — Datos de vuelta (solo lectura)
- [ ] Search Console → pestañas SEO y Blog.
- [ ] Google Ads: términos de búsqueda y resultados (developer token; mientras llega, CSV exportado).
- [ ] Meta: resultados con `ads_read`.
- [ ] Panel por campaña VH-00X: inversión (solo se lee), clics, cotizaciones, pagos, costo por cotización.

**Listo cuando:** el panel muestra la campaña activa con un botón "Actualizar". Nada corre solo (Streamlit Cloud se duerme).

### Fase 5 — Cerrar el ciclo con ventas reales
- [ ] Conversión offline con `gclid` al confirmarse un pago, primero como archivo que Elena sube a Google Ads.
- [ ] Evento de compra a Meta desde el marketplace, en rama de prueba.

**Listo cuando:** Google y Meta reciben las ventas reales.

---

## 8. Pendiente de Elena

- [ ] Detalles de la campaña nueva de Google Ads: tipo, objetivo, página de destino y conversión configurada.
- [ ] Objetivo principal de la pauta este trimestre: viveristas o compradores.
- [ ] ¿Existe portafolio de Meta, cuenta publicitaria y Pixel de viverohub?
- [ ] LinkedIn: solo página de empresa, o también su perfil como fundadora.
- [ ] Nombre de la cuenta de TikTok de viverohub.
- [ ] WhatsApp: número del bot o un segundo número para campañas.
- [ ] Aprobar que el módulo amplíe la pestaña 📣 Campañas en vez de crear una paralela.
- [ ] Aprobar o no borrar el duplicado `agente_ads.py`.
- [ ] Antes de guardar tokens nuevos: confirmar si las llaves de Supabase son service_role o anon (para activar RLS) y si el Copilot Agent del repo está desactivado.

# 🌿 Agencia Automática de Contenido - ViveroOnline

Bienvenido al "Centro de Comando" de ViveroOnline. Este repositorio contiene el código fuente de nuestra agencia de marketing interna automatizada, construida con una arquitectura multi-agente a **costo cero**.

El objetivo de esta herramienta no es vender plantas como un vivero tradicional, sino posicionar a ViveroOnline como **la infraestructura digital de abastecimiento ornamental B2B líder en Colombia**, aplicando una Estrategia de Océano Azul — sin perder la cercanía con el viverista tradicional, que sigue siendo el corazón del negocio.

## 🧠 Cerebro Editable

Todos los agentes de contenido consultan tres módulos centrales en vez de tener su propio criterio embebido:

- **`identidad_marca.py`** — tono, voz y los dos discursos de marca: "frente al viverista" (simple, cercano, cero tecnicismos) vs. "frente al mercado institucional" (constructoras, paisajistas, arquitectos). Expone `IDENTIDAD_COMPACTA` para inyectar en prompts sin gastar contexto de más. Cambia poco.
- **`brand_book.py`** — identidad visual: paleta de color, tipografía, y `GUIA_VISUAL_VIDEO` para que Veo 3.1 genere vivero familiar real en vez de estética genérica de bodega industrial. Cambia poco.
- **`estrategia.py`** + tabla Supabase `configuracion_estrategica` — esto **sí cambia seguido**, y se edita **desde la propia app**, sin tocar código ni redeploy:
  - **Prioridad Actual** — el énfasis de negocio del momento (ej. "generar transacciones reales"), ajusta el CTA de los agentes institucionales.
  - **Dolores frente a Intermediarios** — escritos a mano, nunca generados por IA. Los usa el SEO proactivo.
  - **Estrategia Competitiva** — quiénes son los competidores reales y en qué somos mejores, también escrito a mano.

Estas tres piezas están **relacionadas pero no acopladas**: la pestaña Competencia puede *proponer* un borrador de Prioridad y Dolores razonando sobre la estrategia competitiva real — pero todo pasa por edición/aprobación humana antes de guardarse.

## 🚀 Arquitectura y Pestañas

La app está en **Streamlit**, orquestando agentes de IA (Google GenAI y Groq). Las 9 pestañas siguen el orden del flujo real de una agencia — research → estrategia → campaña → producción por canal → revisión:

### 1. 🧠 Competencia
Estrategia competitiva editable y persistida en Supabase. Botón **"Generar Propuesta desde la Competencia"**: razona (nunca inventa hechos nuevos) un borrador de Prioridad y de Dolores a partir de la estrategia competitiva real, editable antes de guardar, con botón "Volver a generar". Generador de pitch competitivo puntual.

### 2. ⚙️ Estrategia
**Prioridad Actual** y **Dolores frente a Intermediarios**, editables y persistidos. **Generar Campaña desde la Estrategia:** con un tema/ángulo puntual, dispara Texto + WhatsApp + Video + SEO en un solo clic, con candado anti-duplicidad de SEO incluido, guardando todo en el Historial.

### 3. 🔥 Campaña 360
Lee inventario disponible del Marketplace (stock ≥ 20), evita repetir campaña sobre el mismo lote, y genera SEO + WhatsApp + Video automáticamente.

### 4. 📝 Textos
Copy corto/mediano puntual (framework PAS, discurso institucional) — no es un artículo de blog, ver la pestaña Blog GEO/AEO para eso.

### 5. 💬 WhatsApp
Kit de WhatsApp con **audiencia dual**: comprador institucional o viverista. Genera texto para copiar/enviar manualmente — no está conectado a la API de Meta.

### 6. 🎬 Video (Veo 3.1)
Prompts cinematográficos anclados al Brand Book. Backoff exponencial + jitter ante error 429 (cuota).

### 7. 🚀 SEO
Tres modos — Automatizado (desde inventario), Manual, y **Proactivo** (por intención de búsqueda, independiente del inventario). Incluye **candado anti-duplicidad** (`clusters_seo_ejecutados`) contra keyword cannibalization.

### 8. 📰 Blog GEO/AEO
Artículos de blog largos optimizados para que ChatGPT, Perplexity y Gemini los citen: respuesta directa autocontenida, secciones H2 con mini-respuesta antes de listas, autoridad de nicho (Sabana de Bogotá / altitud), y FAQ en formato listo para pegar al bloque nativo de un plugin de SEO (ej. Rank Math). **Arquitectura dual de modelos:** el cuerpo del artículo se genera con Groq/Llama (rápido, y ahí cumple bien); el FAQ se genera con **Gemini 2.5 Flash** específicamente, porque Llama demostró en producción que no evita de forma confiable copiar frases del cuerpo. Incluye validación automática (con un reintento) de que el FAQ no duplique el cuerpo y de que el artículo mencione autoridad de nicho — si tras el reintento sigue fallando, el artículo mismo incluye una nota de advertencia visible para revisión manual antes de publicar.

### 9. 📜 Historial
Todo el contenido generado, con **Estado** (`borrador`/`aprobado` — nada se considera listo hasta revisión humana) y **¿Generó una venta?** (Sí/No/Sin dato — primer mecanismo manual para conectar contenido con resultado real).

## 🛠️ Stack Tecnológico

* **Frontend / Orquestador:** Streamlit (Python)
* **Modelos de Lenguaje (LLMs):**
  * Google GenAI (Gemini 2.5 Flash / Veo 3.1) — video, tareas estructuradas (Pydantic), y el FAQ del blog.
  * Groq (Llama-3.1-8b-instant) — redacción masiva a máxima velocidad y bajo costo; cuerpo de artículos y todo el resto de texto.
* **Base de Datos:** Supabase (PostgreSQL) — dos proyectos separados:
  * **Marketplace** (solo lectura): `inventario`, `plantas`, `viveros`.
  * **Agencia** (lectura/escritura): `historial_contenidos`, `campanas_ejecutadas`, `configuracion_estrategica`, `clusters_seo_ejecutados`.
* **Audio:** edge-tts.
* **Control de Estado:** `.env` local / `st.secrets` en la nube.

## ⚙️ Configuración e Instalación Local

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/vivero-promesa/agencia-agentes-contenido.git
   cd agencia-agentes-contenido
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   Incluye: `streamlit`, `supabase`, `openai`, `google-genai`, `python-dotenv`, `pydantic`, `edge-tts`.

4. **Configura tus credenciales** (`.env` local, o `st.secrets` en Streamlit Cloud):
   ```
   GROQ_API_KEY=tu_llave_de_groq
   GEMINI_API_KEY=tu_llave_de_google_ai
   SUPABASE_URL_EXTERNA=tu_url_del_proyecto_marketplace
   SUPABASE_SERVICE_KEY=tu_service_key_del_marketplace
   SUPABASE_URL_AGENCIA=tu_url_del_proyecto_agencia
   SUPABASE_KEY_AGENCIA=tu_key_del_proyecto_agencia
   ```
   `GEMINI_API_KEY` es necesaria también para que el Blog GEO/AEO use Gemini en el FAQ — si falta, cae de vuelta a Groq automáticamente sin romper el agente, pero con más riesgo de que el FAQ duplique el cuerpo del artículo.

5. **Corre la migración SQL** en el proyecto Supabase **Agencia** (crea `configuracion_estrategica`, `clusters_seo_ejecutados`, y las columnas `estado`/`genero_venta` en `historial_contenidos`) — ver `migracion_aprobacion_candado.sql`.

6. **Ejecuta la app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## ⚠️ Notas Operativas Conocidas

- **Veo 3.1 requiere facturación activa.** Error `429 RESOURCE_EXHAUSTED` → revisa "Plan and billing" en [aistudio.google.com](https://aistudio.google.com). El sistema reintenta automáticamente, pero si la cuota está agotada de fondo, los reintentos no van a ayudar.
- **Los nombres de archivo importan, literalmente.** Streamlit Cloud corre en Linux (case-sensitive). Un rename a medias en el editor web de GitHub (dejando un espacio en vez de guion bajo) rompe todos los imports con `ModuleNotFoundError`.
- **Revisa si el Copilot Coding Agent de GitHub está activo en este repo.** El historial de commits ha mostrado refactors no solicitados que causaron al menos un incidente de despliegue — si no lo usas deliberadamente, desactívalo (Settings → Copilot / pestaña Agents / Settings → Actions). *(Pendiente de confirmar — no verificado aún si sigue activo.)*
- **El WhatsApp institucional es texto libre para copiar/enviar a mano.** Automatizarlo vía API de Meta requeriría plantillas de mensaje pre-aprobadas — el formato actual no serviría tal cual.
- **No hay agente de Google/Meta Ads todavía — es una decisión deliberada.** Falta correr campañas manuales 4-6 semanas para tener datos reales (CTR, conversión, CPA) antes de automatizar con criterio.
- **RLS desactivado en Supabase — pausado, pendiente de decisión.** Antes de activarlo, hay que confirmar si `SUPABASE_SERVICE_KEY`/`SUPABASE_KEY_AGENCIA` son la llave `service_role` (activar RLS sería seguro, esa llave lo ignora) o `anon` (activar RLS sin políticas rompería la app).
- **Los modelos pequeños (Llama 3.1 8B) no cumplen bien reglas múltiples simultáneas.** Lección aprendida con el agente de blog: dividir en llamadas más simples y usar un modelo más capaz (Gemini) para la sub-tarea más sutil (condensar sin duplicar) rinde mejor que un solo prompt gigante con muchas reglas a la vez.
- **El sistema cubre bien Producción de contenido, no el ciclo completo de agencia.** No hay calendario editorial, distribución automática, ni medición automática de conversión — el campo "¿Generó una venta?" en Historial es manual, a propósito. Ver `informe_auditoria_agencia_viveronline.md` para el detalle completo.

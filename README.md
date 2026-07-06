# 🌿 Agencia Automática de Contenido - ViveroOnline

Bienvenido al "Centro de Comando" de ViveroOnline. Este repositorio contiene el código fuente de nuestra agencia de marketing interna automatizada, construida con una arquitectura multi-agente a **costo cero**.

El objetivo de esta herramienta no es vender plantas como un vivero tradicional, sino posicionar a ViveroOnline como **la infraestructura digital de abastecimiento ornamental B2B líder en Colombia**, aplicando una Estrategia de Océano Azul — sin perder la cercanía con el viverista tradicional, que sigue siendo el corazón del negocio.

## 🧠 Cerebro Editable

Todos los agentes de contenido consultan tres módulos centrales en vez de tener su propio criterio embebido:

- **`identidad_marca.py`** — tono, voz y los dos discursos de marca: "frente al viverista" (simple, cercano, cero tecnicismos) vs. "frente al mercado institucional" (constructoras, paisajistas, arquitectos). Expone `IDENTIDAD_COMPACTA` para inyectar en prompts sin gastar contexto de más. Cambia poco.
- **`brand_book.py`** — identidad visual: paleta de color, tipografía, y `GUIA_VISUAL_VIDEO` para que Veo 3.1 genere vivero familiar real (vestimenta de trabajo, invernaderos de plástico, luz de sabana andina) en vez de estética genérica de bodega industrial. Cambia poco.
- **`estrategia.py`** + tabla Supabase `configuracion_estrategica` — a diferencia de los dos anteriores, esto **sí cambia seguido**, y se edita **desde la propia app**, sin tocar código ni redeploy:
  - **Prioridad Actual** — el énfasis de negocio del momento (ej. "generar transacciones reales"), ajusta el CTA de los agentes institucionales.
  - **Dolores frente a Intermediarios** — escritos a mano por el usuario, nunca generados por IA (para no inventar quejas o competidores). Los usa el SEO proactivo.
  - **Estrategia Competitiva** — quiénes son los competidores reales y en qué somos mejores, también escrito a mano.

Estas tres piezas están **relacionadas pero no acopladas**: la pestaña Competencia puede *proponer* un borrador de Prioridad y Dolores razonando sobre la estrategia competitiva real — pero todo pasa por edición/aprobación humana antes de guardarse.

## 🚀 Arquitectura y Pestañas

La app está en **Streamlit**, orquestando agentes de IA (Google GenAI y Groq). Las 8 pestañas siguen el orden del flujo real de una agencia — research → estrategia → campaña → producción por canal → revisión:

### 1. 🧠 Competencia
- Estrategia competitiva editable y persistida en Supabase (antes se perdía al recargar la página — corregido).
- **Generar Propuesta desde la Competencia:** razona (nunca inventa hechos nuevos) un borrador de Prioridad y de Dolores a partir de la estrategia competitiva real. Se muestra en cuadros editables con botón de guardado propio cada uno, más un botón "Volver a generar" — nada se autoguarda.
- Generador de pitch competitivo puntual para un tema/producto.

### 2. ⚙️ Estrategia
- **Prioridad Actual** y **Dolores frente a Intermediarios**, editables y persistidos.
- **Generar Campaña desde la Estrategia:** con un tema/ángulo puntual, dispara Texto + WhatsApp + Video + SEO en un solo clic, usando la Prioridad y los Dolores como contexto, y guarda todo en el Historial (con candado anti-duplicidad de SEO incluido).

### 3. 🔥 Campaña 360
Lee inventario disponible del Marketplace (stock ≥ 20), evita repetir campaña sobre el mismo lote (candado en `campanas_ejecutadas`), y genera SEO + WhatsApp + Video automáticamente para el lote más reciente sin procesar.

### 4. 📝 Textos
Redacción de artículos y copy B2B puntual (framework PAS, discurso institucional).

### 5. 💬 WhatsApp
Kit de WhatsApp (mensaje + guion de nota de voz) con **audiencia dual**: comprador institucional (captación/cierre) o viverista (onboarding/activación, discurso simple y cercano). *Nota: genera texto para copiar/enviar manualmente — no está conectado a la API de Meta.*

### 6. 🎬 Video (Veo 3.1)
Traduce conceptos a prompts cinematográficos anclados al Brand Book. La generación es asíncrona (se espera con polling) y ante error 429 (cuota) reintenta con **backoff exponencial + jitter** hasta 4 veces.

### 7. 🚀 SEO
Tres modos:
- **Automatizado** — dispara desde el inventario del Marketplace.
- **Manual** — especie/cantidad/ubicación/vivero a mano.
- **Proactivo** — por intención de búsqueda (ej. "comprar palmas botella por lote en Bogotá"), independiente del inventario actual. Incluye **candado anti-duplicidad** (`clusters_seo_ejecutados`) para evitar competir contigo mismo en buscadores (*keyword cannibalization*) — si el cluster ya se usó, avisa antes de generar otro.

### 8. 📜 Historial
Todo el contenido generado, con:
- **Estado** (`borrador` por defecto / `aprobado`) — nada se considera listo hasta revisión humana.
- **¿Generó una venta?** (Sí/No/Sin dato) — primer mecanismo manual para empezar a conectar contenido con resultado real.

## 🛠️ Stack Tecnológico

* **Frontend / Orquestador:** Streamlit (Python)
* **Modelos de Lenguaje (LLMs):**
  * Google GenAI (Gemini 2.5 Flash / Veo 3.1) para video y tareas estructuradas (Pydantic).
  * Groq (Llama-3.1-8b-instant) para redacción masiva a máxima velocidad y bajo costo.
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

5. **Corre la migración SQL** en el proyecto Supabase **Agencia** (crea `configuracion_estrategica`, `clusters_seo_ejecutados`, y las columnas `estado`/`genero_venta` en `historial_contenidos`) — ver `migracion_aprobacion_candado.sql`.

6. **Ejecuta la app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## ⚠️ Notas Operativas Conocidas

- **Veo 3.1 requiere facturación activa.** Error `429 RESOURCE_EXHAUSTED` → revisa "Plan and billing" en [aistudio.google.com](https://aistudio.google.com). El sistema reintenta automáticamente, pero si la cuota está agotada de fondo (no es un límite transitorio), los reintentos no van a ayudar.
- **Los nombres de archivo importan, literalmente.** Streamlit Cloud corre en Linux (case-sensitive). Un rename a medias en el editor web de GitHub (dejando un espacio en vez de guion bajo) rompe todos los imports con `ModuleNotFoundError` — verifica el nombre exacto tras cualquier rename.
- **Revisa si el Copilot Coding Agent de GitHub está activo en este repo.** El historial de commits ha mostrado refactors no solicitados que causaron al menos un incidente de despliegue — si no lo usas deliberadamente, desactívalo (Settings → Copilot / pestaña Agents / Settings → Actions).
- **El WhatsApp institucional es texto libre para copiar/enviar a mano.** Si en algún momento se automatiza vía API de Meta, se necesitan plantillas de mensaje pre-aprobadas para outreach fuera de la ventana de 24h — el formato actual no serviría tal cual para eso.
- **No hay agente de Google/Meta Ads todavía — es una decisión deliberada.** Automatizar pauta publicitaria sin datos reales de campaña (CTR, conversión, CPA) es automatizar una adivinanza. Recomendación: correr manual 4-6 semanas primero.
- **El sistema cubre bien Producción de contenido, no el ciclo completo de agencia.** No hay calendario editorial, distribución automática, ni medición automática de conversión — el campo "¿Generó una venta?" en Historial es manual, a propósito, hasta que se decida invertir en medición real. Ver `informe_auditoria_agencia_viveronline.md` para el detalle completo.

# 🌿 Agencia Automática de Contenido - ViveroOnline

Bienvenido al "Centro de Comando" de ViveroOnline. Este repositorio contiene el código fuente de nuestra agencia de marketing interna automatizada, construida con una arquitectura multi-agente a **costo cero**.

El objetivo de esta herramienta no es vender plantas como un vivero tradicional, sino posicionar a ViveroOnline como **la infraestructura digital de abastecimiento ornamental B2B líder en Colombia**, aplicando una Estrategia de Océano Azul — sin perder la cercanía con el viverista tradicional, que sigue siendo el corazón del negocio.

## 🧠 Cerebro Editable (identidad_marca.py + brand_book.py)

Todos los agentes de contenido consultan dos módulos centrales en vez de tener su propio criterio de marca embebido:

- **`identidad_marca.py`** — tono, voz y tres discursos de marca. La regla clave: ViveroOnline le habla distinto **al viverista** (simple, cercano, cero tecnicismos, nunca hacerlo sentir atrasado) que **al mercado institucional** (constructoras, paisajistas, arquitectos — profesional pero nunca corporativo frío). Expone `IDENTIDAD_COMPACTA`, un extracto corto pensado para inyectarse en cada prompt sin gastar contexto de más.
- **`brand_book.py`** — identidad visual: paleta de color, tipografía, y sobre todo `GUIA_VISUAL_VIDEO`, la guía que usa el agente de video para que Veo 3.1 genere vivero familiar real (vestimenta de trabajo, invernaderos de plástico, luz de sabana) en vez de estética genérica de bodega industrial.

Editar el tono o la estética de **todos** los agentes a la vez es tan simple como editar estos dos archivos — no hay que tocar cada agente por separado.

## 🚀 Arquitectura y Módulos

La aplicación está construida en **Streamlit** y orquesta múltiples agentes de IA (Google GenAI y Groq) que se encargan de ejecutar nuestra estrategia de crecimiento en 4 frentes:

1. **📝 Textos y Guiones (Topical Authority):**
   - Agente de redacción para artículos SEO y guiones virales (Reels/TikTok).
   - *Regla de negocio:* usa el discurso "frente al mercado" de `identidad_marca.py` para captar constructoras y paisajistas (B2B) — profesional y logístico, pero nunca corporativo frío ni con lenguaje de urgencia.

2. **💬 Campañas WhatsApp (Fricción Cero):**
   - Agente de comunicación con **dos audiencias**, seleccionables desde la interfaz:
     - **Institucional** (paisajistas, constructoras): captación o cierre de venta, discurso "frente al mercado".
     - **Viverista** (productores): onboarding y adopción tecnológica rural, discurso "frente al viverista" — lenguaje simple, nunca hacerlo sentir atrasado.
   - Genera copys cortos y notas de voz, con enlaces `wa.me` listos para usar.

3. **🎬 Generador B-Roll con Veo 3.1 (Motor de Video):**
   - Traductor de directrices de marketing a *prompts* cinematográficos, anclado a `brand_book.py` (vivero real de la Sabana de Bogotá, no bodega industrial genérica).
   - Genera B-Roll automatizado asegurando encuadre 9:16 y espacio negativo para subtítulos.
   - *Resiliencia:* la generación de video es asíncrona — el agente espera (`polling`) a que el render termine, y ante error 429 (límite de cuota) reintenta automáticamente con **backoff exponencial + jitter** hasta 4 veces. Si el error persiste tras los reintentos, generalmente es cuota agotada (no un límite transitorio) — revisar el plan de facturación en [ai.dev/rate-limit](https://ai.dev/rate-limit).

4. **🚀 SEO Programático (Growth Flywheel):**
   - Convierte el inventario en tráfico. Al detectar nuevos ingresos masivos en la base de datos, el agente redacta automáticamente artículos con framework PAS (Problema-Agitación-Solución) para indexar esos lotes específicos en buscadores, dirigidos a compradores institucionales.

## 🛠️ Stack Tecnológico

* **Frontend / Orquestador:** Streamlit (Python)
* **Modelos de Lenguaje (LLMs):**
  * Google GenAI (Gemini 2.5 Flash / Veo 3.1) para video y tareas complejas de estructuración (Pydantic).
  * Groq (Llama-3.1-8b-instant) para redacción masiva de texto a máxima velocidad y bajo costo.
* **Base de Datos:** Supabase (PostgreSQL + API) — dos proyectos separados: uno de solo lectura para el inventario del marketplace, y otro donde la agencia guarda lo que produce (historial, campañas ejecutadas).
* **Control de Estado:** Variables de entorno local (`.env`) y Secretos en la nube (`st.secrets`).

## ⚙️ Configuración e Instalación Local

Para ejecutar el Centro de Comando en tu máquina local:

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

4. **Configura tus credenciales:** crea un archivo `.env` en la raíz con:
   ```
   GROQ_API_KEY=tu_llave_de_groq
   GEMINI_API_KEY=tu_llave_de_google_ai
   SUPABASE_URL_EXTERNA=tu_url_del_proyecto_marketplace
   SUPABASE_SERVICE_KEY=tu_service_key_del_marketplace
   SUPABASE_URL_AGENCIA=tu_url_del_proyecto_agencia
   SUPABASE_KEY_AGENCIA=tu_key_del_proyecto_agencia
   ```
   En Streamlit Cloud, estas mismas llaves van en **Settings → Secrets** en vez de `.env`.

5. **Ejecuta la app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## ⚠️ Notas operativas conocidas

- **Veo 3.1 requiere facturación activa.** Si ves un error `429 RESOURCE_EXHAUSTED`, el plan gratuito de Google AI Studio probablemente no incluye cuota de video. Revisa "Plan and billing" en [aistudio.google.com](https://aistudio.google.com).
- **Los nombres de archivo importan, literalmente.** Streamlit Cloud corre en Linux (case-sensitive). Si renombras `identidad_marca.py` o `brand_book.py` en el editor web de GitHub, verifica que el nombre final no tenga espacios ni mayúsculas de más — un rename a medias rompe todos los imports con `ModuleNotFoundError`.

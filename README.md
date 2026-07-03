# 🌿 Agencia Automática de Contenido - ViveroOnline

Bienvenido al "Centro de Comando" de ViveroOnline. Este repositorio contiene el código fuente de nuestra agencia de marketing interna automatizada, construida con una arquitectura multi-agente a **costo cero**.

El objetivo de esta herramienta no es vender plantas como un vivero tradicional, sino posicionar a ViveroOnline como **la infraestructura digital de abastecimiento ornamental B2B líder en Colombia**, aplicando una Estrategia de Océano Azul.

## 🚀 Arquitectura y Módulos

La aplicación está construida en **Streamlit** y orquesta múltiples agentes de IA (Google GenAI y Groq) que se encargan de ejecutar nuestra estrategia de crecimiento en 4 frentes:

1. **📝 Textos y Guiones (Topical Authority):** - Agente de redacción para artículos SEO y guiones virales (Reels/TikTok).
   - *Regla de negocio:* Tono corporativo y logístico para captar constructoras y paisajistas (B2B).

2. **💬 Campañas WhatsApp (Fricción Cero):** - Agente especializado en la adopción tecnológica rural.
   - Genera copys cortos y notas de voz para grupos de productores, facilitando el *onboarding* al marketplace mediante enlaces `wa.me`.

3. **🎬 Generador B-Roll con Veo 3 (Motor de Video):** - Traductor de directrices de marketing a *prompts* cinematográficos.
   - Genera B-Roll automatizado asegurando encuadres de 9:16 y espacio negativo para subtítulos. 
   - *Resiliencia:* Incluye sistema de reintentos (Exponential Backoff) para mitigar límites de cuota de API.

4. **🚀 SEO Programático (Growth Flywheel):** - Convierte el inventario en tráfico. Al detectar nuevos ingresos masivos en la base de datos, el agente redacta automáticamente artículos H1/H2 para indexar esos lotes específicos en buscadores.

## 🛠️ Stack Tecnológico

* **Frontend / Orquestador:** Streamlit (Python)
* **Modelos de Lenguaje (LLMs):** * Google GenAI (Gemini 2.5 Pro / Veo 3.1) para video y tareas complejas de estructuración (Pydantic).
    * Groq (Llama-3.1-8b-instant) para redacción masiva de texto a máxima velocidad y bajo costo.
* **Base de Datos:** Supabase (PostgreSQL + API)
* **Control de Estado:** Variables de entorno local (`.env`) y Secretos en la nube (`st.secrets`).

## ⚙️ Configuración e Instalación Local

Para ejecutar el Centro de Comando en tu máquina local:

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/vivero-promesa/agencia-agentes-contenido.git](https://github.com/vivero-promesa/agencia-agentes-contenido.git)
   cd agencia-agentes-contenido

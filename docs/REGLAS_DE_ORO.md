# 🛡️ Reglas de oro — Centro de Campañas viverohub

Estas reglas aplican a todo el código de este repo, a cualquier agente de IA (incluido GitHub Copilot) y a cualquier código traído de otra herramienta. Si un cambio rompe alguna, no se une a `main`.

1. **El presupuesto es 100 % manual.** Ningún bot ni agente crea, activa, pausa ni edita campañas, presupuestos, pujas ni métodos de pago en Google Ads, Meta, TikTok o LinkedIn. Eso lo hace solo Elena.
2. **Accesos de solo lectura en anuncios.** Google Ads: usuario de nivel "Solo lectura". Meta: solo el permiso `ads_read`, nunca `ads_management`. Si alguien escribe código que intente modificar algo, la plataforma lo rechaza.
   - *Publicaciones orgánicas (no son anuncios ni gastan dinero):* el token de la página de viverohub puede tener `pages_manage_posts` e `instagram_content_publish`, y solo se usa desde el botón "📢 Publicar" de una pieza **aprobada**, con el clic de Elena. Nunca por un proceso programado.
3. **Sin funciones de escritura hacia las plataformas de anuncios.** No existe ningún botón "Publicar anuncio" ni "Subir presupuesto". Los agentes entregan borradores y CSV; Elena los revisa y los sube.
4. **WhatsApp masivo cuenta como gasto.** Cada plantilla de marketing cuesta. El envío lo dispara solo el clic de Elena, por lotes, solo a contactos registrados que aceptaron recibir mensajes, y nunca por un proceso programado.
5. **Un solo código por campaña.** Toda pieza, anuncio y enlace lleva el código VH-00X en `utm_campaign`. Una pieza sin código no sale del Historial.
6. **Nunca romper viverohub.** Lo que toque el marketplace se hace en su repo, en rama de prueba y con el protocolo de despliegue seguro, nunca directo a `main`.
7. **Cuentas separadas por proyecto.** Las cuentas de TikTok y LinkedIn del podcast y de la búsqueda de empleo no se usan para viverohub. Viverohub tiene sus propias cuentas.
8. **Datos reales, nunca inventados.** Solo precios, inventario y promesas reales: entrega en unos 3 días hábiles y garantía de planta viva de 72 horas.
9. **Consentimiento primero.** Ningún pixel se activa sin el banner de cookies (Ley 1581 de 2012), con todo en "denegado" por defecto.
10. **El módulo de video no se toca.** `agente_video.py` sigue como está; Elena lo opera con Google Vids.
11. **No duplicar trabajo.** Antes de crear un agente o archivo nuevo, se revisa si ya existe algo que haga lo mismo y se reutiliza.

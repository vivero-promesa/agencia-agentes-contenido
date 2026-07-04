"""
brand_book.py — Brand Book visual de ViveroOnline.

Complementa a identidad_marca.py (que rige tono/voz de texto). Este módulo
rige lo visual: color, tipografía, logo, estilo fotográfico y de video.
Consultado principalmente por agente_video.py al construir prompts para Veo 3.1.
"""

BRAND_BOOK = """
# BRAND BOOK — VIVEROONLINE
# Documento de referencia visual y de marca. Complementa a identidad_marca.py
# (que rige tono/voz para texto). Este documento rige lo visual: color,
# tipografía, fotografía, video, iconografía y ejemplos de aplicación.
#
# Estado: v1 — algunas secciones están marcadas [PENDIENTE] porque requieren
# un archivo de diseño real (logo, plantillas) que no se puede generar por texto.

---

## 1. HISTORIA DE LA MARCA

[PENDIENTE] — Aún no se ha documentado el origen de ViveroOnline (por qué nació,
qué problema vio el fundador, hitos clave). Vale la pena escribirla porque
alimenta directamente el "ADN emocional" (sección 12) y le da autoridad a
cualquier pieza de "quiénes somos".

---

## 2. MISIÓN Y VISIÓN

Misión: quitarle al viverista dos cargas que hoy le roban tiempo y sueño —
aprender tecnología y resolver la logística de plantas vivas — para que se
dedique a lo único que nadie más puede hacer por él: producir buena planta.

Visión (narrativa central de marca): "La tecnología no reemplaza el trabajo
del viverista; le abre nuevos caminos para que su esfuerzo llegue más lejos."

---

## 3. VALORES

• Simplicidad — lo difícil lo resolvemos nosotros, no el viverista.
• Confianza logística — la planta llega viva, o se resuelve.
• Cercanía humana — hablamos como vecino de finca, no como startup.
• Paciencia — nadie se queda atrás por no saber de tecnología.
• Transparencia — sin cobros ocultos, sin letra chiquita.
• Respeto por el oficio — el viverista sabe de plantas más que nadie.

---

## 4. PERSONALIDAD DE MARCA

Si ViveroOnline fuera una persona: 45 años, ingeniero agrónomo pero hijo de
viveristas. Conoce la tecnología, pero todavía usa botas. Habla sencillo,
respeta el campo, tiene visión de futuro. Nunca presume. Siempre ayuda.

Esta descripción es el filtro rápido para cualquier agente: si una pieza de
contenido no suena como algo que diría esta persona, no está en tono.

---

## 5. VOZ Y TONO

Ver identidad_marca.py, sección VOZ y TONO, para el detalle completo
(frases reales del viverista, reglas de lenguaje). Resumen aplicado a lo
visual: nada de sobreexplicar con texto en pantalla lo que la imagen ya
comunica; el silencio visual (espacio en blanco) es parte del tono, igual
que la frase corta lo es del texto.

---

## 6. PALETA DE COLORES

Extraída directamente del código en producción del sitio — estos son los
colores reales, no una propuesta nueva.

**Verde principal** — HEX #325926 · RGB 50,89,38 · CMYK 44,0,57,65
Color primario de marca: CTAs principales, títulos, íconos, hojas del
logo, header, pill badges. Verde bosque — comunica experiencia, confianza,
permanencia. No es el verde brillante de una startup nueva; es el verde de
una empresa que parece sólida.

**Verde secundario** — HEX #10B981 · RGB 16,185,129 · CMYK 91,0,30,27
Acento: botón de WhatsApp, badges de estado positivo ("¡Copiado!",
confirmaciones), notificaciones de éxito. Se usa para llamar la atención
sin competir con el verde principal.

**Blancos**
- #F7F7F6 (blanco cálido/roto) — fondo general de la app, backgrounds de sección.
- #FFFFFF (blanco puro) — tarjetas de producto, contenedores de contenido,
  texto sobre fondo verde.
Ambos generan sensación de aire, limpieza y espacio — coherente con la
"mucho espacio blanco, la página respira" de la interfaz actual.

**Grises (jerarquía tipográfica)**
- #0F172A — texto principal / títulos oscuros.
- #475569 — gris principal, párrafos.
- #64748B — labels, etiquetas, texto de apoyo.
- #94A3B8 — placeholders, texto muy sutil.

**Regla de contraste:** verde principal #325926 sobre blanco #F7F7F6 cumple
WCAG AAA (≥7:1) — válido para texto largo, no solo títulos.

**Proporción sugerida de uso en una pieza:**
60% blanco/gris claro (respiración) · 30% verde principal (identidad) ·
10% verde secundario + gris oscuro (acentos y texto).

**Sobre el naranja:** extraído directamente del archivo del logo y del ícono
de la carretilla.
- Naranja principal — HEX #F89933 · usado en la palabra "Online" del
  logotipo y como tono medio del cuerpo de la carretilla.
- Naranja claro (highlight/degradado) — HEX #FFAA33 · zonas iluminadas de
  la carretilla.
- Naranja oscuro (sombra/degradado) — aprox. HEX #F05A28 · zonas de sombra
  de la carretilla, da profundidad al ícono.
- Naranja suave — HEX #ED9746 · usado en ".com.co" del logotipo, más
  apagado que el naranja principal.
El naranja de marca no es un color plano — es un degradado entre estos
cuatro tonos. Para uso de UI (botones, acentos) el más seguro como color
sólido es #F89933; los otros tres son para ilustraciones/gradientes que
imiten el estilo de la carretilla.

**Nota — discrepancia de verde:** el verde del archivo del logotipo es más
claro y saturado (HEX #58B351, con sombra/degradado hacia #3B7044) que el
verde principal ya documentado del sitio en producción (#325926, más oscuro
y "bosque"). Por instrucción del usuario, **#325926 se mantiene como el
verde oficial** (es el que está en producción). Queda anotado que el
archivo actual del logo no coincide exactamente, por si se actualiza el
logo más adelante para alinearlo.

---

## 7. TIPOGRAFÍAS

**Inter** (pesos 400, 500, 600, 700, 800, 900) — Google Fonts. Es la
tipografía real ya usada en producción.

Nota de identidad sobre el logotipo (no es la tipografía de UI, es el
lettering del logo): la palabra "Vivero" tiene trazo con movimiento, casi
manuscrito — comunica cercanía. La palabra "Online" es limpia y geométrica.
Esa combinación es, literalmente, la marca representando su propia
propuesta: tradición + tecnología en la misma palabra. Vale la pena
mantener esa distinción cada vez que el logotipo aparece completo (no
unificar el estilo de las dos palabras).

---

## 8. USO DEL LOGOTIPO

A partir del archivo real ya se puede documentar:

- **Versión principal:** logotipo horizontal completo — "Vivero" en verde
  con trazo manuscrito, "Online" en naranja #F89933, ".com.co" en naranja
  suave #ED9746 debajo/al lado, todo sobre fondo blanco/transparente.
- **Jerarquía de lectura:** "Vivero" es el elemento dominante (mayor peso
  visual por el trazo y el tamaño), "Online" es el segundo, ".com.co" es
  el más discreto — funciona casi como un dominio, no como parte del
  nombre de marca hablado.
- **Fondo:** el logo está diseñado para fondo claro/blanco — el verde y
  naranja pierden contraste sobre fondos oscuros u otros tonos saturados.
  [PENDIENTE] validar o crear una versión para fondo oscuro si se necesita.

[PENDIENTE] aún: zona de seguridad/espacio mínimo alrededor del logo,
tamaño mínimo de reproducción legible, versión monocromo/isotipo solo, y
qué NO hacer (estirar, cambiar colores, rotar). Esto requiere el archivo
vectorial fuente (AI/SVG/EPS) para definir proporciones exactas — el PNG
que se aportó sirve para referencia de color y composición, pero no para
fijar reglas de escalado sin pérdida de calidad.

Lo que sí se puede documentar ya, en términos de contenido de marca:

**La carretilla como símbolo oficial.** No es un carrito de compras
genérico de e-commerce — es una carretilla, y eso la conecta de inmediato
con el trabajo real del viverista, no con un marketplace cualquiera. Se
recomienda tratarla como símbolo del trabajo del viverista (no como
mascota) y usarla de forma consistente en: videos, animaciones, loading
states, onboarding, stickers de WhatsApp, campañas. El naranja de la
carretilla coincide con el naranja del logo — es memoria visual
intencional y debe mantenerse.

---

## 9. ESTILO FOTOGRÁFICO

Filosofía: ViveroOnline no usa fotos de planta sola — cuenta historias.
Cada fotografía debe mostrar una persona, una planta y una acción. El
protagonista nunca es solo la planta; es quien la cultiva.

Reglas concretas para brief de fotografía o para prompts de generación de
imagen:
- Luz natural, como si fuera tomada alrededor de las 8 a.m.
- Después del riego — hojas húmedas visibles.
- Sin sobresaturación de color, sin filtros de "Instagram".
- Con profundidad de campo (fondo desenfocado, sujeto nítido).
- Personas reales trabajando, no modelos posando para cámara.
- Ver también identidad_marca.py → GUÍA VISUAL PARA VIDEO para vestimenta
  y contexto de infraestructura reales de la Sabana de Bogotá.

---

## 10. ESTILO DE VIDEO (para prompts de Veo 3.1 y similares)

Referencia rápida de tono cinematográfico: los videos deben sentirse como
"National Geographic mezclado con Apple" — observacional, con producción
cuidada, nunca como comercial de venta agresiva. Esto es un cambio de
enfoque de prompt importante: en vez de pedir "video promocional de
vivero", pedir algo más cercano a "documental corto sobre el oficio de un
viverista, con producción minimalista".

Combinar siempre con lo ya definido en identidad_marca.py:
vestimenta real, infraestructura mixta (no bodega industrial), escala
familiar de 2-5 personas, luz de sabana andina, sin texto incrustado en el
video (Veo 3.1 lo renderiza mal — agregar rótulos en edición aparte).

---

## 11. ICONOGRAFÍA E ILUSTRACIÓN

Del análisis de la interfaz actual: botones redondeados, tarjetas sin
sombras agresivas, todo con bordes suaves — comunica amabilidad, no
comunica "sistema corporativo". Cualquier ícono o ilustración nueva debe
seguir esa misma suavidad (esquinas redondeadas, líneas no muy delgadas
ni agresivas, sin efectos 3D exagerados).

[PENDIENTE] set formal de iconos/ilustraciones — hoy es una regla de
estilo, no un archivo de assets reutilizables.

---

## 12. ADN EMOCIONAL

Cuando alguien vea contenido de ViveroOnline debe sentir: esperanza,
confianza, tranquilidad, orgullo, naturaleza, crecimiento, profesionalismo.

Nunca debe sentir: presión, urgencia artificial, miedo, venta agresiva,
sensación de tecnología complicada.

Esta es la prueba más rápida para filtrar cualquier pieza antes de
publicarla: si genera urgencia o presión, no es de la marca aunque el
copy esté bien escrito.

---

## 13. PATRONES GRÁFICOS

[PENDIENTE] — No hay un sistema de patrones/texturas de marca definido
todavía. Si se define, debería nacer del verde principal y del concepto
de "espacio que respira" (poco patrón, mucho blanco), no de una textura
decorativa genérica de plantas.

---

## 14. PLANTILLAS PARA REDES SOCIALES

[PENDIENTE] — Esto es un entregable de diseño (Canva/Figma), no un
documento de texto. Con la paleta y tipografía ya documentadas en este
Brand Book, se pueden construir directamente en Canva cuando se necesite.

---

## 15. PLANTILLAS PARA PRESENTACIONES

[PENDIENTE] — Mismo caso que el punto anterior: entregable de diseño,
listo para construirse una vez se defina el logotipo formal (sección 8).

---

## 16. EJEMPLOS DE COMUNICACIÓN CORRECTA E INCORRECTA

**Correcto (texto):** "Esa ya está lista para despacho. Le consigo la
cantidad en ocho días." — directo, en el lenguaje real del viverista.

**Incorrecto (texto):** "¡Optimiza tu inventario y digitaliza tu negocio
hoy mismo!" — lenguaje corporativo, genera exactamente el rechazo que el
PERFIL DEL VIVERISTA (en identidad_marca.py) advierte.

**Correcto (visual):** foto de una persona real regando en la mañana,
hojas húmedas, luz natural, ropa de trabajo con tierra.

**Incorrecto (visual):** imagen de bodega industrial con chalecos
reflectivos y montacargas, o cuadrilla uniformada tipo call center.

**Correcto (video):** documental corto, cámara observacional, sin texto
incrustado, subtítulos añadidos en edición.

**Incorrecto (video):** comercial con música de urgencia, texto grande
tipo "¡OFERTA!", cortes rápidos tipo anuncio de rebajas.

Esta sección debe crecer con cada campaña real — cada vez que algo
funcione o falle, se agrega aquí como ejemplo concreto.

---

## RESUMEN DE PENDIENTES (para cerrar el Brand Book v2)

1. Historia de la marca — texto de origen.
2. Código HEX exacto del naranja del logo/carretilla.
3. Archivo fuente del logo + reglas formales de uso (espacio, tamaño mínimo, versiones).
4. Set de iconos/ilustraciones reutilizables.
5. Patrones gráficos si se decide tener alguno.
6. Plantillas de redes sociales y presentaciones (diseño, no texto).

"""

# --------------------------------------------------------------------------
# Extracto compacto para inyectar directamente en prompts de video (Veo 3.1).
# Mantenerlo corto: los prompts de video rinden mejor con instrucciones
# concretas y breves, no con el documento completo.
# --------------------------------------------------------------------------
GUIA_VISUAL_VIDEO = """
Estilo cinematográfico: documental observacional, tono "National Geographic
mezclado con Apple" — nunca comercial de venta agresiva ni estética industrial
de bodega.

Vestimenta real de trabajo: jean o pantalón resistente, camisa manga larga o
camiseta polo, chaqueta impermeable, botas pantaneras o de seguridad, gorra o
sombrero. Manos con marcas de trabajo, tierra visible en la ropa. Nunca
uniformes corporativos idénticos ni chalecos reflectivos de bodega industrial.

Infraestructura real: invernaderos de plástico o polisombra, microaspersión,
zonas con infraestructura tradicional — nunca un galpón de acero impecable ni
estantería industrial de almacén.

Escala familiar: 2-5 personas trabajando, posible mezcla de generaciones —
nunca cuadrillas uniformadas de 6+ personas tipo bodega.

Luz: natural, difusa, de sabana andina (2.600 msnm) — como alrededor de las
8 a.m., después del riego, hojas húmedas. Nunca luz tropical intensa ni
iluminación de almacén.

Color de marca en overlays/gráficos si aplica: verde #325926, naranja #F89933.

Texto en pantalla: evitar texto incrustado en el video (Veo 3.1 lo renderiza
con errores ortográficos) — dejar espacio limpio para subtítulos añadidos en
edición posterior.
"""

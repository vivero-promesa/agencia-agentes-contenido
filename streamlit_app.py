import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from agentes_crecimiento import generar_campana_whatsapp, generar_seo_desde_inventario
from agente_audio import generar_audio_elevenlabs

# ==========================================
# 0. CONFIGURACIÓN DEL CENTRO DE COMANDO
# ==========================================
st.set_page_config(page_title="Agencia ViveroOnline", layout="wide", page_icon="🌱")
st.title("🌱 Centro de Comando - ViveroOnline")

load_dotenv()

# INICIALIZACIÓN SEGURA DE ADMINISTRADOR (Bypasses RLS)
url_ext = st.secrets.get("SUPABASE_URL_EXTERNA")
# ¡Clave! Usamos la llave de servicio, no la anónima
key_service = st.secrets.get("SUPABASE_SERVICE_KEY") 
supabase = create_client(url_ext, key_service) if url_ext and key_service else None

# ==========================================
# 4. ARQUITECTURA DE PESTAÑAS
# ==========================================
tab_texto, tab_whatsapp, tab_video, tab_seo = st.tabs(["📝 Textos", "💬 WhatsApp", "🎬 Video", "🚀 SEO"])

# --- PESTAÑA WHATSAPP ---
with tab_whatsapp:
    st.subheader("Captación Directa (Fricción Cero)")
    obj_wa = st.text_input("Objetivo de la campaña:")
    
    if st.button("Generar Kit de WhatsApp"):
        with st.spinner("Conectando con Agente de Crecimiento..."):
            campana = generar_campana_whatsapp(obj_wa)
            if campana:
                st.session_state.wa_copy = campana.mensaje_texto
                st.session_state.wa_script = campana.guion_nota_voz
                st.success("Kit generado con éxito.")
                st.text_area("Copy WhatsApp:", value=campana.mensaje_texto)
                st.text_area("Guion nota de voz:", value=campana.guion_nota_voz)
                st.session_state.wa_generado = True
            else:
                st.error("El agente de crecimiento no pudo responder.")

    if st.session_state.get("wa_generado"):
        if st.button("🎧 Generar Nota de Voz"):
            with st.spinner("Generando audio..."):
                audio = generar_audio_elevenlabs(st.session_state.wa_script)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.warning("No se pudo generar el audio.")

# --- PESTAÑA SEO PROGRAMÁTICO (Detección de Esquema Automatizada) ---
with tab_seo:
    st.subheader("Trigger SEO: Generador de Artículos B2B")
    
    modo_seo = st.radio("Modo de operación:", ["📡 Automatizado (Base de Datos)", "✍️ Ingreso Manual"], horizontal=True)
    
    if modo_seo == "📡 Automatizado (Base de Datos)":
        if st.button("Analizar BD y Generar SEO"):
            with st.spinner("Decodificando esquema de base de datos y generando contenido..."):
                try:
                    # 1. Obtener el último registro del inventario
                    res_inv = supabase.table("inventario").select("*").order("inventario_id", desc=True).limit(1).execute()
                    
                    if not res_inv.data:
                        st.warning("El inventario está vacío.")
                    else:
                        item = res_inv.data[0]
                        
                        # 2. AUTO-DETECCIÓN: Leemos una fila de muestra sin filtros para mapear las columnas reales
                        muestra_planta = supabase.table("plantas").select("*").limit(1).execute().data[0]
                        muestra_vivero = supabase.table("viveros").select("*").limit(1).execute().data[0]
                        
                        # Encontramos la columna que actúa como llave primaria (ID)
                        # Busca dinámicamente cualquier columna que contenga 'planta' o 'vivero' e 'id'
                        col_id_planta = [c for c in muestra_planta.keys() if "id" in c.lower()][0]
                        col_id_vivero = [c for c in muestra_vivero.keys() if "id" in c.lower()][0]
                        
                        # 3. Consulta real utilizando los nombres de columna correctos detectados
                        planta_data = supabase.table("plantas").select("*").eq(col_id_planta, item["planta_id"]).execute().data[0]
                        vivero_data = supabase.table("viveros").select("*").eq(col_id_vivero, item["vivero_id"]).execute().data[0]
                        
                        # 4. Extracción flexible de nombres y ubicaciones
                        # Prueba con múltiples variantes comunes de nombres de columna para no fallar
                        nombre_especie = (
                            planta_data.get("especie_nombre") or 
                            planta_data.get("nombre_comun") or 
                            planta_data.get("nombre") or 
                            f"Especie ID {item['planta_id']}"
                        )
                        
                        nombre_vivero = (
                            vivero_data.get("vendedor_nombre") or 
                            vivero_data.get("nombre_vivero") or 
                            vivero_data.get("nombre") or 
                            f"Vivero ID {item['vivero_id']}"
                        )
                        
                        locacion = (
                            vivero_data.get("ubicacion") or 
                            vivero_data.get("ciudad") or 
                            vivero_data.get("municipio") or 
                            "Sabana de Bogotá"
                        )
                        
                        # Mostrar en la UI los metadatos detectados para tu tranquilidad
                        st.write(f"📊 **Datos extraídos:** {nombre_especie} | Stock: {item['stock']} | Ubicación: {locacion} ({nombre_vivero})")
                        
                        # 5. Construcción del payload para el Agente IA
                        datos_auto = {
                            "especie": nombre_especie,
                            "cantidad": item["stock"],
                            "ubicacion": locacion,
                            "vendedor": nombre_vivero
                        }
                        
                        # 6. Generación con la arquitectura de agentes
                        articulo = generar_seo_desde_inventario(datos_auto)
                        if articulo:
                            st.success("¡Artículo estratégico B2B generado con éxito!")
                            st.markdown(f"### {articulo.titulo_h1}")
                            st.markdown(articulo.contenido_md)
                        else:
                            st.error("El motor de IA no devolvió un formato válido.")
                
                except Exception as e:
                    st.error(f"Error en la consulta automática: {e}")

    else:
        # MODO MANUAL (Estructura de respaldo intacta)
        col1, col2 = st.columns(2)
        with col1:
            man_especie = st.text_input("Especie de planta:", placeholder="Ej: Palma Areca")
            man_vendedor = st.text_input("Nombre del Vivero:", placeholder="Ej: Vivero El Edén")
        with col2:
            man_cantidad = st.number_input("Cantidad (Stock):", min_value=1, value=500)
            man_ubicacion = st.text_input("Ubicación del lote:", placeholder="Ej: Chía")
            
        if st.button("Generar Artículo Manual"):
            if man_especie and man_vendedor and man_ubicacion:
                with st.spinner("Redactando artículo estratégico..."):
                    datos_manuales = {
                        "especie": man_especie,
                        "cantidad": man_cantidad,
                        "ubicacion": man_ubicacion,
                        "vendedor": man_vendedor
                    }
                    articulo = generar_seo_desde_inventario(datos_manuales)
                    if articulo:
                        st.success("Artículo manual generado exitosamente.")
                        st.markdown(f"### {articulo.titulo_h1}")
                        st.markdown(articulo.contenido_md)
            else:
                st.warning("Completa los campos requeridos para proceder.")

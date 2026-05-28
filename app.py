import streamlit as st
import mysql.connector
import pandas as pd

# 1. Configuración visual de la pestaña (podés dejar un hongo de ícono temporal o usar el logo)
st.set_page_config(page_title="Colección BAFC-H", page_icon="🍄", layout="wide")

# 2. Mostramos el logo oficial en pantalla
st.image("logo_BAFCH.jpg", width=150) # Podés cambiar el número 150 para achicarlo o agrandarlo

# 3. Título institucional sin emojis de plantas
st.title("Búsqueda Avanzada - Colección BAFC-H")
st.markdown("Bienvenido al portal de consulta pública.")

# Conexión a la base de datos
@st.cache_resource
def iniciar_conexion():
    return mysql.connector.connect(
        host="bafc-h-bafch2026.k.aivencloud.com",
        port=20532, # Ajustá tu puerto si es necesario
        database="bafch_coleccion",
        user="usuario_consulta",
        password="usuario_consulta" # Poné la contraseña de tu usuario_consulta
    )

conexion = iniciar_conexion()

# Barra de búsqueda única y potente
criterio = st.text_input("🔍 Escribí tu búsqueda (separe los términos con espacios):", "")

if criterio:
    # 1. Separamos la frase en palabras individuales y eliminamos conectores
    conectores = ["de", "del", "en", "el", "la", "los", "las", "y"]
    palabras = [p for p in criterio.split() if p.lower() not in conectores]
    
    if palabras:
        condiciones_and = []
        parametros_sql = []
        
        # 2. Para cada palabra, buscamos en estas 11 columnas
        for palabra in palabras:
            bloque_or = """
            (ScientificName LIKE %s 
             OR recordedBy LIKE %s 
             OR CatalogNumber LIKE %s 
             OR Locality LIKE %s 
             OR StateProvince LIKE %s 
             OR previousIdentifications LIKE %s
             OR Continent LIKE %s
             OR identifiedBy LIKE %s
             OR typeStatus LIKE %s
             OR `living culture` LIKE %s
             OR Country LIKE %s)
            """
            condiciones_and.append(bloque_or)
            
            # El comodín % permite encontrar la palabra en cualquier parte del texto
            termino = f"%{palabra}%"
            
            # Multiplicamos el parámetro x11 para que coincida EXACTAMENTE con los 11 "%s" de arriba
            parametros_sql.extend([termino] * 11)
        
        # 3. Unimos todo y armamos la orden final
        query = f"""
        SELECT CatalogNumber, previousIdentifications, ScientificName, recordedBy, Locality, Country
        FROM BAFCH_Darwincore_principal 
        WHERE {" AND ".join(condiciones_and)}
        LIMIT 150
        """
        
        # Ejecutamos la consulta (usamos tuple() por seguridad con MySQL)
        df = pd.read_sql(query, conexion, params=tuple(parametros_sql))
        
        # 4. Mostramos los resultados
        st.write(f"Se encontraron **{len(df)}** registros que coinciden con tu búsqueda:")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Por favor, ingresá términos de búsqueda válidos.")
else:
    st.info("Ejemplo: Escribí 'Agaricus Argentina' para ver las colecciones de ese género en el país.")
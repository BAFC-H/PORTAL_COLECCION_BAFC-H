import streamlit as st
import mysql.connector
import pandas as pd

# 1. Configuración visual de la pestaña (SIEMPRE PRIMERO)
st.set_page_config(page_title="Colección BAFC-H", page_icon="🍄", layout="wide")

# 2. Mostramos el logo oficial en pantalla
st.image("logo_BAFCH.JPG", width=150)

# 3. Diseño total: Título, fondo, logo y carteles
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fredericka+the+Great&display=swap" rel="stylesheet">
    
    <style>
    /* Aplicar la textura de fondo a toda la aplicación */
    .stApp {
        background-image: url("FONDO.png");
        background-repeat: repeat;
        background-size: auto;
    }
    
    /* Estilo del título */
    .titulo-personalizado {
        font-family: 'Fredericka the Great', serif !important;
        color: #A9B709 !important;
        font-size: 48px !important;
        font-weight: normal !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
    }

    /* Estilo específico para el LOGO */
    div[data-testid="stImage"] img {
        border: 3px solid #826F52 !important;
        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.3) !important;
        border-radius: 5px !important;
        padding: 2px !important;
        background-color: white !important; /* Por si el logo tiene fondo transparente */
    }
    
    /* Fondo del cartel de información (st.info) */
    div[data-testid="stAlert"] {
        background-color: #826F52 !important;
        border: none !important;
    }
    
    /* Texto adentro del cartel */
    div[data-testid="stAlert"] p {
        color: #A9B709 !important;
        font-weight: bold !important;
    }
    
    /* Color del iconito de información */
    div[data-testid="stAlert"] svg {
        fill: #A9B709 !important;
    }
    </style>
    
    <h1 class="titulo-personalizado">Búsqueda Avanzada - Colección BAFC-H</h1>
    """,
    unsafe_allow_html=True
)

st.markdown("Bienvenido al portal de consulta pública.")

# Conexión a la base de datos
@st.cache_resource
def iniciar_conexion():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

conexion = iniciar_conexion()

# Barra de búsqueda única y potente
criterio = st.text_input("🔍 Escribí tu búsqueda (separa los términos con espacios):", "")

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
# --- PIE DE PÁGINA (Autoría y Licencia) ---
st.markdown("---") # Esto dibuja una línea horizontal sutil para separar el buscador del final

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <p style="color: #826F52; font-size: 16px; margin-bottom: 5px;">
            <strong>Colección BAFC-H</strong> - Facultad de Ciencias Exactas y Naturales, UBA
        </p>
        <p style="color: #826F52; font-size: 16px; margin-top: 0; margin-bottom: 15px;">
            Instituto de Micología y Botánica (InMiBo)
        </p>
        <p style="color: #3E362E; font-size: 14px;">
            Desarrollo y diseño de base de datos por <strong>Federico Mazzone Pereira</strong>.
        </p>
        <div style="margin-top: 15px;">
            <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank">
                <img alt="Licencia Creative Commons" style="border-width:0; margin-bottom: 5px;" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" />
            </a>
            <br />
            <span style="color: #3E362E; font-size: 12px;">
                Esta obra y sus datos están bajo una 
                <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" style="color: #A9B709; text-decoration: none; font-weight: bold;">
                    Licencia Creative Commons Atribución-NoComercial 4.0 Internacional
                </a>.
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

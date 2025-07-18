import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import load_model
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import os

# 🌿 Configuración general
st.set_page_config(page_title="Clasificador de Reciclaje", layout="wide")

# 🌄 Estilo personalizado
st.markdown("""
<style>
    .stApp {
        background-image: url('https://es.vecteezy.com/foto/2161139-bosque-de-abetos-oscuros-despues-de-la-lluvia');
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        background-color: #0f1f17;
    }
    .main {
        background-color: rgba(15, 31, 23, 0.85);
        padding: 1em;
        border-radius: 10px;
    }
    h1, h2, h3, h4 {
        color: #cde3d2;
    }
    .stButton>button {
        background-color: #6b8e74;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1em;
        margin-bottom: 0.5em;
    }
    .stButton>button:hover {
        background-color: #4f7158;
    }
    .sidebar .sidebar-content {
        background-color: rgba(17, 28, 24, 0.9);
        padding: 1em;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 🧠 Cargar modelo
modelo_path = "modelo.h5"
if os.path.exists(modelo_path):
    modelo = load_model(modelo_path)
else:
    st.error(f"❌ No se encontró el modelo `{modelo_path}`. Sube el archivo correctamente antes de ejecutar la app.")
    st.stop()

# ♻️ ───── Categorías y descripciones ─────
categorias = [
    'Contenedor_urbano_amarillo - Envases',
    'Contenedor_urbano_azul - Papel_y_carton',
    'Contenedor_urbano_verde - Vidrio',
    'Contenedor_urbano_marron - Organico',
    'Contenedor_urbano_gris - Restos',
    'Punto_limpio - Aceite_usado_de_cocina_o_motor',
    'Punto_limpio - Bombillas_y_fluorescentes',
    'Punto_limpio - Cristal_no_reciclable',
    'Punto_limpio - Electrodomesticos',
    'Punto_limpio - Escombros_y_restos_de_obra',
    'Punto_limpio - Juguetes_electronicos',
    'Punto_limpio - Metal_y_chatarra',
    'Punto_limpio - Muebles_y_enseres',
    'Punto_limpio - Pilas_y_baterias',
    'Punto_limpio - Pinturas,_disolventes_y_productos_quimicos',
    'Punto_limpio - Radiografias',
    'Punto_limpio - Raee_residuos_de_aparatos_electronicos',
    'Punto_limpio - Restos_de_poda',
    'Punto_limpio - Ropa_y_calzado',
    'Punto_limpio - Toner_y_cartuchos_de_impresora',
    'Punto_SIGRE - Medicamentos_y_envases'
]

descripciones = {
    'Contenedor_urbano_amarillo - Envases': '🟡 Envases metálicos, briks y plásticos. Latas, botellas PET, tapones y bolsas limpias.',
    'Contenedor_urbano_azul - Papel_y_carton': '🔵 Periódicos, revistas, cajas de cartón, folios y bolsas de papel (sin restos orgánicos).',
    'Contenedor_urbano_verde - Vidrio': '🟢 Botellas, frascos y tarros de vidrio (sin tapas ni restos de cerámica).',
    'Contenedor_urbano_marron - Organico': '🟤 Restos de comida, vegetales, servilletas sucias y residuos biodegradables.',
    'Contenedor_urbano_gris - Restos': '⚫ Residuos no reciclables: colillas, compresas, cerámica rota y polvo de barrer.',
    'Punto_limpio - Aceite_usado_de_cocina_o_motor': '🛢️ Lleva el aceite usado en botellas bien cerradas. Nunca lo viertas por el desagüe.',
    'Punto_limpio - Bombillas_y_fluorescentes': '💡 Bombillas LED, fluorescentes y tubos deben entregarse en el punto limpio.',
    'Punto_limpio - Cristal_no_reciclable': '🪞 Cristales planos, espejos y vidrios de ventanas van al punto limpio. No en el contenedor verde.',
    'Punto_limpio - Electrodomesticos': '⚙️ Frigoríficos, lavadoras, microondas y pequeños aparatos eléctricos. Consulta servicio municipal.',
    'Punto_limpio - Escombros_y_restos_de_obra': '🚧 Restos de cemento, ladrillos, azulejos y tierra: solo en puntos autorizados.',
    'Punto_limpio - Juguetes_electronicos': '🕹️ Juguetes con pilas o circuitos van al punto limpio como RAEE.',
    'Punto_limpio - Metal_y_chatarra': '🔩 Objetos metálicos como tuberías, herramientas, herrajes y muebles metálicos.',
    'Punto_limpio - Muebles_y_enseres': '🪑 Sofás, camas, mesas, estanterías y muebles voluminosos. Puedes solicitar recogida municipal.',
    'Punto_limpio - Pilas_y_baterias': '🔋 Pilas alcalinas, recargables y baterías de litio. Nunca en contenedores urbanos.',
    'Punto_limpio - Pinturas,_disolventes_y_productos_quimicos': '🧪 Restos de pintura, sprays, disolventes, insecticidas y productos tóxicos.',
    'Punto_limpio - Radiografias': '🩻 Radiografías contienen materiales contaminantes. No deben ir a la basura común.',
    'Punto_limpio - Raee_residuos_de_aparatos_electronicos': '🖥️ Móviles, ordenadores, tablets y cargadores deben llevarse al punto limpio (RAEE).',
    'Punto_limpio - Restos_de_poda': '🌿 Ramas, hojas, césped cortado y restos vegetales grandes van al punto limpio.',
    'Punto_limpio - Ropa_y_calzado': '👕 Ropa en buen estado puede donarse. Lo demás va a contenedores específicos o al punto limpio.',
    'Punto_limpio - Toner_y_cartuchos_de_impresora': '🖨️ Cartuchos de tinta y tóner: contaminantes y reciclables. Nunca en restos.',
    'Punto_SIGRE - Medicamentos_y_envases': '💊 Medicamentos caducados y sus envases se depositan en puntos SIGRE (en farmacias).'
}

materiales = {
    "Orgánico": "https://dkv.es/corporativo/blog-360/medioambiente/reciclaje/residuos-organicos",
    "Vidrio": "https://www.ecovidrio.es/reciclaje/cadena-reciclado",
    "Papel y cartón": "https://www.bbva.com/es/sostenibilidad/que-es-el-papel-reciclado-y-cual-es-el-proceso-para-reciclarlo/",
    "Metal": "https://reducereutilizarecicla.org/metal-reciclado/",
    "Plásticos": "https://www.rts.com/es/blog/the-complete-plastics-recycling-process-rts/",
    "Madera": "https://www.gadisa.es/blog/como-se-hace-el-recicleja-de-madera/",
    "Aceite usado": "https://www.sigaus.es",
    "Ropa y calzado": "https://slowfashionnext.com/blog/reciclaje-de-ropa/",
    "Bombillas": "https://www.ambilamp.es",
    "Radiografías": "https://www.garfellacarsi.com/reciclaje-radiografias/",
    "Tapones": "https://fundacionecoruycan.com/reciclaje-de-tapones/",
    "Corcho": "https://www.bourrasse.com/es/el-reciclaje-del-corcho/",
    "Pilas y baterías": "https://www.ecopilas.es/el-reciclaje/procesos-de-reciclaje-de-pilas/",
    "Medicamentos": "https://www.sigre.es",
    "Químicos": "https://www.smv.es/como-es-el-proceso-de-reciclaje-de-quimicos/",
    "Restos de poda": "https://www.leanpio.com/es/blog/reciclaje-poda-beneficios"
}

procesos = {
    "Orgánico": {
        "descripcion": "Se separan y tratan los residuos de origen biológico para transformarlos en recursos útiles, principalmente compost y abono orgánico, y se lleva a cabo mediante el compostaje o la digestión anaeróbica.",
        "link": materiales["Orgánico"]
    },
    "Vidrio": {
        "descripcion": "Se limpia, tritura y funde a más de 1400º para fabricar nuevos envases.",
        "link": materiales["Vidrio"]
    },
    "Papel y cartón": {
        "descripcion": "Se prensa, trocea, mezcla con agua y seca para formar nuevo papel.",
        "link": materiales["Papel y cartón"]
    },
    "Metal": {
        "descripcion": "Se funde y reutiliza en nuevos objetos metálicos.",
        "link": materiales["Metal"]
    },
    "Plásticos": {
        "descripcion": "Se separan por tipo, se trituran y se derriten para formar granza. Algunos se reciclan, otros se incineran.",
        "link": materiales["Plásticos"]
    },
    "Madera": {
        "descripcion": "La madera reciclada se usa para hacer tableros aglomerados, compost o biocombustible.",
        "link": materiales["Madera"]
    },
    "Aceite usado": {
        "descripcion": "Se decanta y filtra. Puede usarse en biodiésel o como lubricante industrial.",
        "link": materiales["Aceite usado"]
    },
    "Ropa y calzado": {
        "descripcion": "Se clasifican por tipo. Si no se donan, se reciclan como trapos o aislantes textiles.",
        "link": materiales["Ropa y calzado"]
    },
    "Tapones": {
        "descripcion": "Se funden y muchos se usan en proyectos solidarios. Importante separarlos del envase.",
        "link": materiales["Tapones"]
    },
    "Bombillas": {
        "descripcion": "Se recupera la plata de las películas. El plástico base también puede reutilizarse.",
        "link": materiales["Bombillas"]
    },
    "Corcho": {
        "descripcion": "Se tritura y prensa para crear paneles aislantes o suelas de zapatos. ¡100 % biodegradable!",
        "link": materiales["Corcho"]
    },
    "Restos de poda": {
        "descripcion": "Poda de grandes cantidades productos vegetales. Se produce compost, biomasa, energía, viruta y serrín.",
        "link": materiales["Restos de poda"]
    },
    "Medicamentos": {
        "descripcion": "Medicamentos caducados, envases y prospectos, deben ir a Puntos SIGRE en farmacias.",
        "link": materiales["Medicamentos"]
    },
    "Pilas y baterías": {
        "descripcion": "El proceso varía según el tipo de batería, pero generalmente implica trituración, separación de componentes y recuperación de metales como zinc, hierro, níquel, cadmio o litio.",
        "link": materiales["Pilas y baterías"]
    },
    "Químicos": {
        "descripcion": "Pinturas, disolventes y productos tóxicos se neutralizan o almacenan en depósitos seguros.",
        "link": materiales["Químicos"]
    },
     "Radiografías": {
        "descripcion": "Siguen un proceso para recuperar materiales como la plata y para que los datos privados se destruyan con seguridad.",
        "link": materiales["Radiografías"]
    }, 
}

# Inicializar session_state si es necesario
if "material_elegido" not in st.session_state:
    st.session_state["material_elegido"] = None

for material in materiales:
    if st.sidebar.button(f"🔎 {material}"):
        st.session_state["material_elegido"] = material

# Sidebar izquierda
st.sidebar.header("🧠 Cómo se recicla")
st.sidebar.markdown("""<div style="background-color: rgba(60, 83, 70, 0.3); padding: 8px; border-radius: 10px; margin-bottom: 1em;">📚 Aprende sobre el reciclaje seleccionando un material para ver enlaces educativos y procesos.</div>""", unsafe_allow_html=True)

for material in materiales:
    if st.sidebar.button(f"🔎 {material}"):
        st.session_state["material_elegido"] = material

        
# Columnas
col1, col2, col3 = st.columns([1, 2, 1])

# Proceso de reciclaje (col1)
with col1:
    st.title("🧪 Proceso de reciclaje")
    material_elegido = st.session_state.get("material_elegido")
    if material_elegido in procesos:
        info = procesos[material_elegido]
        st.markdown(f"""
        <div style="background-color: rgba(60, 83, 70, 0.4); border-left: 6px solid #a2cfa5; padding: 10px; border-radius: 10px; margin-bottom: 20px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
            <h3 style="color:#d5eadd">📋 Material: {material_elegido}</h3>
            <p style="color:#e0e0e0; font-size: 1.05em;">{info["descripcion"]}</p>
            <a href="{info["link"]}" target="_blank" style="color:#c1e9d8; font-weight:bold;">👉 Más información oficial</a>
        </div>
        """, unsafe_allow_html=True)

# Clasificador de reciclaje (col2)
with col2:
    st.title("♻️ Clasificador de Reciclaje Inteligente")
    imagen_subida = st.file_uploader("📸 Sube tu imagen aquí", type=["jpg", "jpeg", "png"])

    if imagen_subida is not None:
        try:
            img = Image.open(imagen_subida).convert("RGB")
            img = img.resize((150, 150))
            img_array = keras_image.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            prediccion = modelo.predict(img_array)
            if prediccion.shape[1] != len(categorias):
                st.error(f"🚫 El modelo devuelve {prediccion.shape[1]} clases, pero hay {len(categorias)} definidas.")
            else:
                top_indices = np.argsort(prediccion[0])[::-1][:2]
                i1, i2 = top_indices
                confianza_principal = prediccion[0][i1]
                clase_principal = categorias[i1]
                descripcion_principal = descripciones.get(clase_principal, "ℹ️ (Sin descripción disponible)")

                st.success(f"✅ Categoría recomendada: **{clase_principal.replace('_', ' ').title()}**")
                st.write(descripcion_principal)
                st.write(f"🔒 Confianza: **{confianza_principal:.2%}**")
                st.image(img, caption="Imagen subida", use_container_width=True)

                confianza_secundaria = prediccion[0][i2]
                if confianza_secundaria > confianza_principal - 0.10:
                    clase_secundaria = categorias[i2]
                    descripcion_secundaria = descripciones.get(clase_secundaria, "ℹ️ (Sin descripción disponible)")
                    st.warning(f"🤔 Alternativa posible: **{clase_secundaria.replace('_', ' ').title()}**")
                    st.write(descripcion_secundaria)
                    st.write(f"📊 Confianza alternativa: **{confianza_secundaria:.2%}**")
        except Exception as e:
            st.error("🚨 Error al procesar la imagen.")
            st.write(f"🛠️ Detalle técnico: `{e}`")
    else:
        st.info("📎 Sube una imagen para comenzar el proceso de clasificación.")

# Geolocalización (col3)
with col3:
    st.markdown("""
    <div style="background-color: rgba(60, 83, 70, 0.4); border-left: 6px solid #a2cfa5; padding: 15px; border-radius: 10px; margin-bottom: 25px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
        <h4 style="color:#d5eadd">📍 Encuentra tu punto limpio</h4>
        <p style="color:#e0e0e0; font-size: 1.05em;">
        Escribe tu ciudad o dirección para localizar tu ubicación y acceder a los puntos limpios cercanos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    direccion = st.text_input("🔎 Introduce tu ubicación")

    if direccion:
        try:
            geolocator = Nominatim(user_agent="reciclaje_app")
            ubicacion = geolocator.geocode(direccion, timeout=10)

            if ubicacion:
                st.success(f"📍 Ubicación detectada: {ubicacion.address}")
                query = f"punto limpio cerca de {ubicacion.address}"
                url_google_maps = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

                st.markdown(f"""
                <div style="margin-top:15px; text-align: center;">
                    <a href="{url_google_maps}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #6b8e74; color: white; padding: 10px 20px; border-radius: 6px; font-size: 16px; font-weight: bold; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
                            🗺️ Abrir mapa completo
                        </div>
                    </a>
                </div>
                """, unsafe_allow_html=True)

                mapa = folium.Map(location=[ubicacion.latitude, ubicacion.longitude], zoom_start=13)
                folium.Marker(
                    [ubicacion.latitude, ubicacion.longitude],
                    popup="Tu ubicación",
                    icon=folium.Icon(color="green")
                ).add_to(mapa)

                st_folium(mapa, width=300, height=250)
            else:
                st.warning("❌ No se pudo encontrar esa ubicación. Intenta con una dirección más precisa.")
        except Exception as e:
            st.error("🚨 Error al conectar con el servicio de geolocalización.")
            st.write(f"🛠️ Detalle técnico: `{e}`")

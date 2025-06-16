import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import warnings
import contextlib
import json
import time
import plotly.graph_objects as go
import random

# Deshabilitar más tipos de warnings en Streamlit
#st.set_option('deprecation.showfileUploaderEncoding', False)
#st.set_option('deprecation.showWarningOnDirectExecution', False)


# --- Definir un valor seguro para esperanza de vida por defecto ---
ESPERANZA_VIDA_DEFAULT = 76

def calcular_semanas(fecha_inicio, fecha_fin):
    return max(0, (fecha_fin - fecha_inicio).days // 7)

def calcular_horas_por_categoria(dias_totales, horas_dormir, horas_trabajo):
    horas_dormidas = dias_totales * horas_dormir
    horas_trabajadas = dias_totales * horas_trabajo
    horas_personales = (dias_totales * 24) - (horas_dormidas + horas_trabajadas)
    return horas_dormidas, horas_trabajadas, horas_personales

def crear_grafico_torta(labels, values, titulo):
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values, hole=0.4))
    fig.update_layout(title=titulo)
    return fig

def crear_grafico_barras(etapas, colores, semanas_vividas):
    fig = go.Figure()
    for etapa, color in zip(etapas.keys(), colores):
        semanas = etapas[etapa]
        fig.add_trace(go.Bar(
            y=[""],
            x=[semanas],
            name=etapa,
            orientation='h',
            marker=dict(color=color),
            hovertemplate=f"<b>{etapa}</b><br>Semanas: {semanas}<extra></extra>"
        ))
    fig.add_trace(go.Scatter(
        y=[""],
        x=[semanas_vividas],
        mode="markers",
        marker=dict(size=12, color="red", symbol="diamond"),
        name="Semana actual",
        hovertemplate=f"<b>Semana actual</b><br>Semanas vividas: {semanas_vividas}<extra></extra>"
    ))
    fig.update_layout(barmode='stack', height=200)
    return fig

# Función para crear el gráfico de barras horizontal acumulado

def crear_grafico_barras_acumulado(etapas, colores, semanas_vividas, semanas_hasta_jubilarse=None, semanas_post_jubilacion=None):
    fig = go.Figure()
    # Fix the color assignment in the bar chart
    for etapa, color in zip(etapas.keys(), colores.values()):
        semanas = etapas[etapa]
        fig.add_trace(go.Bar(
            y=[""],
            x=[semanas],
            name=etapa,
            orientation='h',
            marker=dict(color=color),  # Ensure 'color' is a valid CSS color
            hovertemplate=(
                f"<b>{etapa}</b><br>Semanas vividas: {semanas}<extra></extra>"
            )
        ))

    # Agregar marcador para la semana actual
    fig.add_trace(go.Scatter(
        y=[""],
        x=[semanas_vividas],
        mode="markers",
        marker=dict(size=12, color="red", symbol="diamond"),
        name="Semana actual",
        hovertemplate=f"<b>Semana actual</b><br>Semanas vividas: {semanas_vividas}<extra></extra>"
    ))

    # Agregar barras adicionales si existen
    if semanas_hasta_jubilarse:
        fig.add_trace(go.Bar(
            y=[""],
            x=[semanas_hasta_jubilarse],
            name="Hasta jubilarse restante",
            orientation='h',
            marker=dict(color=colors["Hasta jubilarse (37-65)"], opacity=0.5),
            hovertemplate=(
                f"<b>Hasta jubilarse restante</b><br>Semanas restantes: {semanas_hasta_jubilarse}<extra></extra>"
            )
        ))

    if semanas_post_jubilacion:
        fig.add_trace(go.Bar(
            y=[""],
            x=[semanas_post_jubilacion],
            name="Post jubilación restante",
            orientation='h',
            marker=dict(color=colors["Post jubilación (65-76)"], opacity=0.5),
            hovertemplate=(
                f"<b>Post jubilación restante</b><br>Semanas restantes: {semanas_post_jubilacion}<extra></extra>"
            )
        ))

    fig.update_layout(
        barmode='stack',
        xaxis_title='Fines de semanas vividos',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        height=200
    )
    return fig


# Función para crear el gráfico de círculos

def crear_grafico_circulos(x, y, color_list, current_week_index):
    # Restore original logic for highlighting the current week
    color_list = []
    for etapa, row in df.iterrows():
        color_list.extend([colors[etapa]] * int(row["Semanas"]))

    # Highlight the current week
    current_week_index = semanas_vividas - 1  # Index of the current week
    highlight_color = "#FF0000"  # Strong red color for highlighting
    color_list[current_week_index] = highlight_color

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=-y,
        mode='markers',
        marker=dict(size=6, color=color_list, opacity=0.8),
        text=[f"Semana {i+1}" for i in range(len(x))],
        hoverinfo='text'
    ))
    # Update layout to reduce margins and maximize space
    fig.update_layout(
        title=f"Semanas de vida de {nombre}",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=0, r=0, t=30, b=0),  # Reduce margins
        showlegend=False
    )
    return fig

def calcular_horas_por_etapa(etapa, semanas_etapa, horas_dormir_por_dia, horas_trabajo_por_dia):
    """
    Calculate the hours spent sleeping, working, and on personal time for a specific stage.

    Parameters:
        etapa (str): The name of the stage.
        semanas_etapa (int): The number of weeks in the stage.
        horas_dormir_por_dia (int): Average hours of sleep per day.
        horas_trabajo_por_dia (int): Average hours of work per day.

    Returns:
        tuple: (hours sleeping, hours working, hours personal)
    """
    dias_etapa = semanas_etapa * 7

    # Define the stages where working hours are applicable
    etapas_trabajo = ["Universidad y soltería", "Carrera y noviazgo", "Hasta jubilarse"]

    # Calculate working hours only for specific stages
    if etapa in etapas_trabajo:
        horas_trabajadas = dias_etapa * horas_trabajo_por_dia
    else:
        horas_trabajadas = 0

    horas_dormidas = dias_etapa * horas_dormir_por_dia
    horas_personales = (dias_etapa * 24) - (horas_dormidas + horas_trabajadas)

    return horas_dormidas, horas_trabajadas, horas_personales

# Configuración de la página

st.set_page_config(page_title="Tu vida", layout="wide")
st.title("⏳ Tu vida en semanas")

# Restaurar st.experimental_get_query_params y ocultar el mensaje de advertencia
warnings.filterwarnings("ignore", category=FutureWarning, module="streamlit")

query_params = st.experimental_get_query_params()

# --- Leer parámetros de la URL si existen ---
nombre_url = query_params.get("nombre", [None])[0]
fecha_nacimiento_url = query_params.get("fecha_nacimiento", [None])[0]
esperanza_vida_url = query_params.get("esperanza_vida", [None])[0]

# --- Definir valores iniciales según URL o por defecto ---
nombre_default = nombre_url if nombre_url else "Agustín"
try:
    fecha_nacimiento_default = datetime.strptime(fecha_nacimiento_url, "%Y-%m-%d").date() if fecha_nacimiento_url else datetime(1988, 5, 19).date()
except Exception:
    fecha_nacimiento_default = datetime(1988, 5, 19).date()
try:
    esperanza_vida_default = int(esperanza_vida_url) if esperanza_vida_url else ESPERANZA_VIDA_DEFAULT
except Exception:
    esperanza_vida_default = ESPERANZA_VIDA_DEFAULT

 

# Sidebar para inputs (usando valores iniciales)
st.sidebar.header("Configura tus datos")
nombre = st.sidebar.text_input("¿Cuál es tu nombre?", nombre_default, key="sidebar_nombre")
fecha_nacimiento = st.sidebar.date_input("Fecha de nacimiento", fecha_nacimiento_default, key="sidebar_fecha_nacimiento")


# Add a new variable for retirement age
edad_jubilacion_default = 65
edad_jubilacion = st.sidebar.number_input(
    "Edad de jubilación (años)",
    min_value=1,
    max_value=120,
    value=edad_jubilacion_default,
    key="sidebar_edad_jubilacion"
)

esperanza_vida = st.sidebar.number_input("Esperanza de vida (años)", min_value=1, max_value=120, value=esperanza_vida_default, key="sidebar_esperanza_vida")

# Agregar sliders sincronizados para horas de dormir, trabajo y tiempo personal
st.sidebar.header("Configura tu distribución diaria de tiempo")

# Inicializar valores
horas_totales_dia = 24

# Sliders sincronizados
horas_dormir_por_dia = st.sidebar.slider(
    "Horas de dormir por día",
    min_value=4,
    max_value=12,
    value=7,
    step=1,
    key="slider_horas_dormir"
)

horas_trabajo_por_dia = st.sidebar.slider(
    "Horas de trabajo por día",
    min_value=4,  # Mínimo de horas
    max_value=12,  # Máximo de horas
    value=8,
    step=1,
    key="slider_horas_trabajo"
) 


horas_trabajo_semanales = horas_trabajo_por_dia * 5  # Asumiendo 5 días laborales

# Calcular promedio diario de horas laborales
#horas_trabajo_por_dia = horas_trabajo_semanales / 7

# Calcular automáticamente las horas de tiempo personal para días hábiles
horas_tiempo_personal_habiles = 24 - horas_dormir_por_dia - int(horas_trabajo_por_dia)

# Mostrar el valor calculado en la barra lateral
st.sidebar.markdown(f"**Dormir:** {horas_dormir_por_dia} horas")
st.sidebar.markdown(f"**Jornada laboral:** {horas_trabajo_por_dia} horas")
st.sidebar.markdown(f"**Tiempo personal diario:** {horas_tiempo_personal_habiles} horas")

# Validar que las horas de tiempo personal no sean negativas
if horas_tiempo_personal_habiles < 2:
    st.sidebar.error("Tiempo personal diario no pueden ser menos de dos. Ajusta las horas de dormir o trabajo.")


# Reorganizar cálculos para resolver dependencias





# Calcular semanas totales y semanas vividas
fecha_hoy = datetime.today()
# Convertir fecha_nacimiento a datetime.datetime si es date
if isinstance(fecha_nacimiento, datetime):
    fecha_nac_dt = fecha_nacimiento
else:
    fecha_nac_dt = datetime.combine(fecha_nacimiento, datetime.min.time())

fecha_muerte_estimada = datetime(fecha_nac_dt.year + esperanza_vida, fecha_nac_dt.month, fecha_nac_dt.day)
# Convertir fecha_nacimiento a datetime para que coincida con fecha_muerte
fecha_nacimiento = datetime.combine(fecha_nacimiento, datetime.min.time())
semanas_totales = (fecha_muerte_estimada - fecha_nacimiento).days // 7
semanas_vividas = ((fecha_hoy - fecha_nacimiento).days) // 7

# Calcular semanas restantes
semanas_restantes = semanas_totales - semanas_vividas

# Calcular horas de trabajo semanales y promedio diario
horas_trabajo_semanales = horas_trabajo_por_dia * 5
horas_trabajo_por_dia_promedio = horas_trabajo_semanales / 7

# Calcular horas de tiempo personal para días hábiles
horas_tiempo_personal_habiles = 24 - horas_dormir_por_dia - int(horas_trabajo_por_dia)

# Validar que las horas de tiempo personal no sean negativas
if horas_tiempo_personal_habiles < 2:
    st.sidebar.error("Tiempo personal diario no puede ser menos de dos. Ajusta las horas de dormir o trabajo.")

# Calcular horas libres por semana considerando fines de semana
tiempo_libre_diario = 4  # Valor predeterminado en horas por día
horas_libres_por_semana = horas_tiempo_personal_habiles * 5 + tiempo_libre_diario * 2

# Calcular horas restantes y días libres estimados
horas_restantes = horas_libres_por_semana * semanas_restantes
dias_libres_estimados = horas_restantes // 24

# Calcular porcentaje vivido y años restantes
porcentaje_vivido = min(100, (semanas_vividas / semanas_totales) * 100)
años_restantes = max(0, (fecha_muerte_estimada - fecha_hoy).days // 365)



# Inicializar etapas y colores si no están definidos
if 'etapas' not in locals():
    etapas = {}
if 'colors' not in locals():
    colors = {}

# Asegurar inicialización de variables necesarias antes de su uso

# Inicializar etapas y colores
etapas = {}
colors = {}

# Crear DataFrame de etapas antes de su uso
etapas_input = [
    ("De nacimiento a conciencia", 0, 5, "#FFD700"),
    ("Infancia consciente", 5, 18, "#87CEEB"),
    ("Universidad y soltería", 18, 24, "#32CD32"),
    ("Carrera y noviazgo", 24, min(edad_jubilacion, 37), "#FF8C00"),
    ("Hasta jubilarte", 37, edad_jubilacion, "#FFA07A"),
    ("Jubilación", edad_jubilacion, esperanza_vida, "#F8F8FF")
]

for nombre_etapa, edad_ini, edad_fin, color in etapas_input:
    fecha_ini = max(fecha_nacimiento, datetime(fecha_nacimiento.year + edad_ini, fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_fin = min(datetime(fecha_nacimiento.year + edad_fin, fecha_nacimiento.month, fecha_nacimiento.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[nombre_etapa] = semanas
    colors[nombre_etapa] = color

df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)

# Inicializar fecha_nac_dt
fecha_nac_dt = datetime.combine(fecha_nacimiento, datetime.min.time())



# Fines de semana vividos por etapa
fines_semana_por_etapa = {}
semanas_acumuladas = 0
for etapa, row in df.iterrows():
    semanas_etapa = int(row["Semanas"])
    if semanas_vividas > semanas_acumuladas:
        vividas = min(semanas_etapa, semanas_vividas - semanas_acumuladas)
    else:
        vividas = 0
    fines_semana_por_etapa[etapa] = vividas
    semanas_acumuladas += semanas_etapa

# Mejorar la UX: centrado, paddings, tarjetas y colores suaves
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: auto;
    }
    .kpi-card {
        background: #1e1e1e; /* Dark background */
        border-radius: 12px;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        text-align: center;
        color: #ffffff; /* Light text for contrast */
    }
    .insight-card {
        background: #2a2a2a; /* Slightly lighter dark */
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        font-size: 1.1rem;
        color: #ffffff;
    }
    .stMetric {
        background: #1e1e1e; /* Dark background for KPIs */
        border-radius: 10px;
        padding: 1rem; /* Increase padding for better spacing */
        margin-bottom: 1rem;
        color: #ffffff; /* Light text for contrast */
        box-shadow: 0 2px 6px rgba(0,0,0,0.4); /* Enhanced shadow for depth */
        border: 1px solid #444444; /* Subtle border for separation */
    }
    .stMetric label {
        font-size: 1.2rem; /* Slightly larger font for labels */
        color: #cccccc; /* Softer text color for labels */
    }
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 2rem; /* Larger font for metric values */
        font-weight: bold; /* Emphasize the value */
        color: #ffffff; /* Ensure value is bright and visible */
    }
    .kpi-row {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }
    .insight-banner {
        background: #3a3a3a; /* Dark gray for highlights */
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        text-align: center;
        transition: background 0.5s;
        color: #ffffff;
    }
    .insight-banner:nth-child(odd) {
        background: #4a4a4a; /* Slightly lighter dark gray for alternates */
    }
    </style>
""", unsafe_allow_html=True)

# Add JavaScript to detect dark or light mode
st.markdown(
    """
    <script>
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const root = document.documentElement;
    if (prefersDarkMode) {
        root.style.setProperty('--background-secondary', '#2c2f33');
        root.style.setProperty('--text-primary', '#ffffff');
        root.style.setProperty('--background-highlight', '#4a90e2');
        root.style.setProperty('--background-highlight-alt', '#f5a623');
    } else {
        root.style.setProperty('--background-secondary', '#f5f7fa');
        root.style.setProperty('--text-primary', '#000000');
        root.style.setProperty('--background-highlight', '#e1f5fe');
        root.style.setProperty('--background-highlight-alt', '#fff3e0');
    }
    </script>
    """,
    unsafe_allow_html=True
)



# Force dark mode using custom CSS
st.markdown(
    """
    <style>
    /* Apply dark mode styles globally */
    html, body, [class*="css"] {
        background-color: #0e1117 !important; /* Dark background */
        color: #ffffff !important; /* Light text */
    }
    .stButton > button {
        background-color: #1e1e1e !important; /* Dark button background */
        color: #ffffff !important; /* Light button text */
        border: 1px solid #ffffff !important; /* Button border */
    }
    .stTextInput > div > input {
        background-color: #1e1e1e !important; /* Dark input background */
        color: #ffffff !important; /* Light input text */
        border: 1px solid #ffffff !important; /* Input border */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Cálculos base --- 
# Asegurar que fecha_muerte sea del mismo tipo que fecha_nacimiento
fecha_muerte = fecha_muerte_estimada
semanas_totales = (fecha_muerte - fecha_nacimiento).days // 7
dias_vividos = (fecha_hoy - fecha_nacimiento).days

# Validar que total_semanas esté inicializado correctamente
total_semanas = semanas_totales

# Calcular tiempos en días y horas
horas_por_dia = 24
horas_dormir_por_dia = 8
horas_trabajo_por_dia = 8

dias_totales = total_semanas * 7
dias_dormidos = (dias_totales * horas_dormir_por_dia) / horas_por_dia
dias_despiertos = dias_totales - dias_dormidos

# Calcular tiempo trabajando
if "Carrera y noviazgo (24-37)" in etapas:
    dias_trabajados = (etapas["Carrera y noviazgo (24-37)"] * 7 * horas_trabajo_por_dia) / horas_por_dia
else:
    dias_trabajados = 0

# Tiempo trabajando hasta los 60 años
edad_actual = (fecha_hoy - fecha_nac_dt).days // 365
if edad_actual < 60:
    dias_trabajo_futuro = ((60 - max(edad_actual, 24)) * 365 * horas_trabajo_por_dia) / horas_por_dia
else:
    dias_trabajo_futuro = 0

# Asegurar inicialización de variables necesarias
horas_trabajo_futuro = (etapas.get("Futuro", 0) * 7 * horas_trabajo_por_dia)
horas_personales_restantes = (etapas.get("Futuro", 0) * 7 * horas_por_dia) - horas_trabajo_futuro

# Calcular días libres
if dias_despiertos > (dias_trabajados + dias_trabajo_futuro):
    dias_libres = dias_despiertos - (dias_trabajados + dias_trabajo_futuro)
else:
    dias_libres = 0

# Crear gráfico de torta para tiempo durmiendo y despierto
fig_sleep_awake = go.Figure()
fig_sleep_awake.add_trace(go.Pie(
    labels=["Durmiendo", "Trabajando", "Tiempo personal"],
    values=[
        dias_dormidos,
        dias_trabajados,
        dias_despiertos - dias_trabajados
    ],
    hole=0.4
))
fig_sleep_awake.update_layout(
    title="Distribución del tiempo: Durmiendo, Trabajando y Tiempo Personal"
)

# Inicializar variables necesarias basadas en cálculos existentes
horas_dormidas = dias_dormidos * horas_por_dia
horas_trabajadas = dias_trabajados * horas_por_dia
horas_personales = (dias_despiertos * horas_por_dia) - (horas_dormidas + horas_trabajadas)

# Asegurar inicialización de variables necesarias
horas_trabajo_futuro = (etapas.get("Futuro", 0) * 7 * horas_trabajo_por_dia)
horas_personales_restantes = (etapas.get("Futuro", 0) * 7 * horas_por_dia) - horas_trabajo_futuro



# --- KPIs ---
st.subheader("Resumen actual de tu vida") 

etapas_ordenadas = list(etapas.keys())
semana_actual_acumulada = 0
etapa_actual = None

for etapa in etapas_ordenadas:
    semana_actual_acumulada += etapas[etapa]
    if semanas_vividas <= semana_actual_acumulada:
        etapa_actual = etapa
        break

if etapa_actual:
    semanas_inicio_etapa = semana_actual_acumulada - etapas[etapa_actual]
    semanas_restantes_en_etapa = max(0, semana_actual_acumulada - semanas_vividas)
    dias_restantes_en_etapa = semanas_restantes_en_etapa * 7
    st.success(f"**Semana número {semanas_vividas:,}**, actualmente en la etapa **'{etapa_actual}'**. Te quedan **{semanas_restantes_en_etapa} semanas** (unos **{dias_restantes_en_etapa} días**) en esta etapa.") 


# KPIs en una única línea
kpi_cols = st.columns(5)
kpi_cols[0].metric("% vivido", f"{porcentaje_vivido:.2f}%")
kpi_cols[1].metric("Días vividos", f"{dias_vividos:,}".replace(",", ".") )
kpi_cols[2].metric("Semanas vividas", f"{semanas_vividas:,}".replace(",", "."))
kpi_cols[3].metric("Semanas restantes", f"{semanas_restantes:,}".replace(",", "."))
kpi_cols[4].metric("Años restantes", f"{años_restantes:,}".replace(",", "."))

# Insights dinámicos 
insights = [
    f"🌟 Ya viviste el {porcentaje_vivido:.2f}% de tu vida. Aún te quedan {años_restantes} años llenos de potencial.",
    f"🎨 Cada punto en tu gráfico es una semana: una historia, una oportunidad. ¿Cómo vas a pintar las siguientes {semanas_restantes} semanas?",
    f"⌛ Si te quedan {semanas_restantes} semanas, ¿cuántas dedicarás a lo verdaderamente importante?",
    f"📅 Viviste más de {dias_vividos} días desde que naciste.",
    f"🌕 Sobreviviste a unas {dias_vividos // 29} lunas llenas.",
    f"😴 Estuviste despierto unos {(dias_vividos * 16) // 24} días completos (si dormiste 8 hs por día).",
    f"🍃 Disfrutaste al menos {semanas_vividas // 1} fines de semana: más de {semanas_vividas * 2} días de descanso."
]

# Seleccionar 2 insights aleatorios
insights_random = random.sample(insights, 2) 
for insight in insights_random:
    st.info(f"{insight}") 
 



grafico_barras = crear_grafico_barras_acumulado(etapas, colors, semanas_vividas)
st.plotly_chart(grafico_barras, use_container_width=True)





# Restaurar gráfico de círculos para semanas de vida 
cols = 52
rows = semanas_totales // cols + 1
x = np.tile(np.arange(cols), rows)
y = np.repeat(np.arange(rows), cols)
colors_circulos = ["#F0F0F0"] * semanas_totales
for i in range(semanas_vividas):
    colors_circulos[i] = "#1f77b4"  # azul para semanas vividas
fig_circulos = crear_grafico_circulos(x[:semanas_totales], y[:semanas_totales], colors_circulos, semanas_vividas - 1)
st.plotly_chart(fig_circulos, use_container_width=True)

# --- Tiempo personal proyectado ---
st.subheader("Tu tiempo personal disponible (proyección futura)")
col1, col2, col3 = st.columns(3)
col1.metric("Horas personales/semana", f"{horas_libres_por_semana:,.0f}".replace(",", ".") )
col2.metric("Total de horas personales restantes", f"{horas_restantes:,.0f}".replace(",", ".") )
col3.metric("Equivalente en días libres completos", f"{dias_libres_estimados:,.0f}".replace(",", ".") )
st.info(f"💪 Si dedicás solo 1 hora diaria a algo que amás, te quedan {semanas_restantes * 7} horas para eso.")
st.info(f"📖 Podrías leer unos {int(horas_restantes // 8)} libros (asumiendo 8hs/libro).")


# Dropdown para seleccionar etapa
etapa_seleccionada = st.selectbox(
    "Selecciona una etapa para ver los valores relativos:",
    ["Total"] + list(etapas.keys()),
    key="selectbox_etapa"
)

# Crear gráfico de torta para tiempo restante
fig_remaining_time = go.Figure()
fig_remaining_time.add_trace(go.Pie(
    labels=["Trabajo futuro", "Tiempo personal restante"],
    values=[
        horas_trabajo_futuro,
        horas_personales_restantes
    ],
    hole=0.4
))
fig_remaining_time.update_layout(
    title="Distribución del tiempo restante: Trabajo futuro y Tiempo Personal"
)

# Mostrar gráficos en una línea horizontal
st.subheader("Gráficos de distribución")
col1, col2 = st.columns(2)

with col1:
    # Actualizar el gráfico de torta de horas actuales según la etapa seleccionada
    if etapa_seleccionada == "Total":
        # Recalcular las horas totales correctamente
        horas_dormidas_etapa = dias_dormidos * horas_por_dia
        horas_trabajadas_etapa = dias_trabajados * horas_por_dia
        horas_personales_etapa = (dias_despiertos * horas_por_dia) - (horas_dormidas_etapa + horas_trabajadas_etapa)

        # Crear el gráfico actualizado
        fig_sleep_awake = go.Figure()
        fig_sleep_awake.add_trace(go.Pie(
            labels=["Durmiendo", "Trabajando", "Tiempo personal"],
            values=[
                horas_dormidas_etapa,
                horas_trabajadas_etapa,
                horas_personales_etapa
            ],
            hole=0.4
        ))
        fig_sleep_awake.update_layout(
            title="Distribución del tiempo: Durmiendo, Trabajando y Tiempo Personal"
        )
    else:
        semanas_etapa = etapas[etapa_seleccionada]
        horas_dormidas_etapa, horas_trabajadas_etapa, horas_personales_etapa = calcular_horas_por_etapa(
            etapa_seleccionada, semanas_etapa, horas_dormir_por_dia, horas_trabajo_por_dia
        )

        fig_sleep_awake = go.Figure()
        fig_sleep_awake.add_trace(go.Pie(
            labels=["Durmiendo", "Trabajando", "Tiempo personal"],
            values=[
                horas_dormidas_etapa,
                horas_trabajadas_etapa,
                horas_personales_etapa
            ],
            hole=0.4
        ))
        fig_sleep_awake.update_layout(
            title=f"Distribución del tiempo relativo a la etapa: {etapa_seleccionada}"
        )

    st.plotly_chart(fig_sleep_awake, use_container_width=True, key="plotly_chart_sleep_awake")

with col2:
    # Mantener el gráfico de torta de tiempo restante estático
    st.plotly_chart(fig_remaining_time, use_container_width=True, key="plotly_chart_remaining_time")
 



st.caption("Hecho con ❤️ por TimeLeft")

# Sidebar configuration menu for life stages
st.sidebar.header("Configura las etapas de tu vida")

# Initialize default stages if not already set
if 'etapas_input' not in st.session_state:
    st.session_state['etapas_input'] = [
        {"nombre": "De nacimiento a conciencia","edad_inicio": 0,  "edad_fin": 5, "color": "#FFD700"},
        {"nombre": "Infancia consciente", "edad_inicio": 5, "edad_fin": 18, "color": "#87CEEB"},
        {"nombre": "Universidad y soltería", "edad_inicio": 18,  "edad_fin": 24, "color": "#32CD32"},
        {"nombre": "Carrera y noviazgo","edad_inicio": 24,  "edad_fin": 37, "color": "#FF8C00"},
        {"nombre": "Hasta jubilarte", "edad_inicio": 37,  "edad_fin": 65, "color": "#FFA07A"},
        {"nombre": "Jubilación", "edad_inicio": 65,  "edad_fin": 76, "color": "#F8F8FF"}
    ]

# Dynamic configuration for each stage
for i, etapa in enumerate(st.session_state['etapas_input']):
    with st.sidebar.expander(f"Etapa {i + 1}: {etapa['nombre']}"):
        etapa['nombre'] = st.text_input(f"Nombre de la etapa {i + 1}", etapa['nombre'], key=f"nombre_etapa_{i}") 
        etapa['edad_fin'] = st.number_input(f"Edad de fin de la etapa {i + 1}", min_value=0, max_value=120, value=etapa['edad_fin'], key=f"edad_fin_etapa_{i}")
        etapa['color'] = st.color_picker(f"Color de la etapa {i + 1}", etapa['color'], key=f"color_etapa_{i}")

# Update etapas and colors based on user input
etapas = {}
colors = {}
for etapa in st.session_state['etapas_input']:
    fecha_ini = max(fecha_nacimiento, datetime(fecha_nacimiento.year + etapa['edad_inicio'], fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_fin = min(datetime(fecha_nacimiento.year + etapa['edad_fin'], fecha_nacimiento.month, fecha_nacimiento.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[etapa['nombre']] = semanas
    colors[etapa['nombre']] = etapa['color']

# Recreate DataFrame for stages
df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)


# Initialize dynamic inputs for life stages
etapas_input = []
num_etapas = st.sidebar.number_input("Número de etapas", min_value=1, max_value=10, value=len(etapas_input), step=1, key="num_etapas")

for i in range(num_etapas):
    etapa_nombre = st.sidebar.text_input(f"Nombre de la etapa {i+1}", value=f"Etapa {i+1}", key=f"etapa_nombre_{i}")
    etapa_edad_inicio = 0 if i == 0 else etapas_input[i-1]['edad_fin']  # Dynamically set based on the previous stage
    etapa_edad_fin = st.sidebar.number_input(f"Edad fin de la etapa {i+1}", min_value=0, max_value=120, value=etapa_edad_inicio + 5, key=f"etapa_edad_fin_{i}")
    etapa_color = st.sidebar.color_picker(f"Color de la etapa {i+1}", value="#FFFFFF", key=f"etapa_color_{i}")

    etapas_input.append({
        'nombre': etapa_nombre,
        'edad_inicio': etapa_edad_inicio,
        'edad_fin': etapa_edad_fin,
        'color': etapa_color
    })

# Update etapas and colors dynamically based on user input
etapas = {}
colors = {}

for nombre_etapa, edad_ini, edad_fin, color in etapas_input:
    fecha_ini = max(fecha_nacimiento, datetime(fecha_nacimiento.year + edad_ini, fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_fin = min(datetime(fecha_nacimiento.year + edad_fin, fecha_nacimiento.month, fecha_nacimiento.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[nombre_etapa] = semanas
    colors[nombre_etapa] = color

# Recreate DataFrame for life stages
df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)

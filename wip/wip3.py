import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import contextlib
import json
import time
import plotly.graph_objects as go

# Deshabilitar más tipos de warnings en Streamlit
#st.set_option('deprecation.showfileUploaderEncoding', False)
#st.set_option('deprecation.showWarningOnDirectExecution', False)

st.set_page_config(page_title="TimeLeft - Visualiza tu vida", layout="wide")
st.title("⏳ TimeLeft: Visualiza tu vida en semanas")

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
    esperanza_vida_default = int(esperanza_vida_url) if esperanza_vida_url else 76
except Exception:
    esperanza_vida_default = 76

# Sidebar para inputs (usando valores iniciales)
st.sidebar.header("Configura tus datos")
nombre = st.sidebar.text_input("¿Cuál es tu nombre?", nombre_default, key="sidebar_nombre")
fecha_nacimiento = st.sidebar.date_input("Fecha de nacimiento", fecha_nacimiento_default, key="sidebar_fecha_nacimiento")
esperanza_vida = st.sidebar.number_input("Esperanza de vida (años)", min_value=1, max_value=120, value=esperanza_vida_default, key="sidebar_esperanza_vida")

# Add a new variable for retirement age
edad_jubilacion_default = 65
edad_jubilacion = st.sidebar.number_input(
    "Edad de jubilación (años)",
    min_value=1,
    max_value=120,
    value=edad_jubilacion_default,
    key="sidebar_edad_jubilacion"
)

# --- Sincronizar la URL cuando cambian los inputs ---
st.experimental_set_query_params(
    nombre=nombre,
    fecha_nacimiento=fecha_nacimiento.strftime("%Y-%m-%d"),
    esperanza_vida=str(esperanza_vida)
)

fecha_hoy = datetime.today()

# Convertir fecha_nacimiento a datetime.datetime si es date
if isinstance(fecha_nacimiento, datetime):
    fecha_nac_dt = fecha_nacimiento
else:
    fecha_nac_dt = datetime.combine(fecha_nacimiento, datetime.min.time())

fecha_muerte_estimada = datetime(fecha_nac_dt.year + esperanza_vida, fecha_nac_dt.month, fecha_nac_dt.day)

# Etapas y colores
etapas_input = [
    ("De nacimiento a conciencia", 0, 5, "#FFD700"),  # Amarillo (infancia)
    ("Infancia consciente", 5, 18, "#87CEEB"),         # Celeste (niñez/adolescencia)
    ("Universidad y soltería", 18, 24, "#32CD32"),    # Verde (juventud)
    ("Carrera y noviazgo", 24, min(edad_jubilacion, 37), "#FF8C00"),        # Naranja (adultez)
    ("Hasta jubilarse", 37, edad_jubilacion, "#FFA07A"), # Salmón (adultez tardía)
    ("Post jubilación", edad_jubilacion, esperanza_vida, "#F8F8FF") # Casi blanco (futuro)
]

etapas = {}
colors = {}
for nombre_etapa, edad_ini, edad_fin, color in etapas_input:
    fecha_ini = max(fecha_nac_dt, datetime(fecha_nac_dt.year + edad_ini, fecha_nac_dt.month, fecha_nac_dt.day))
    fecha_fin = min(datetime(fecha_nac_dt.year + edad_fin, fecha_nac_dt.month, fecha_nac_dt.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = semanas
    colors[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = color

df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)

# Colores por semana
total_weeks = int(df["Semanas"].sum())
color_list = []
for etapa, row in df.iterrows():
    color_list.extend([colors[etapa]] * int(row["Semanas"]))

cols = 100
rows = (total_weeks // cols) + 1
x = np.tile(np.arange(cols), rows)[:total_weeks]
y = np.repeat(np.arange(rows), cols)[:total_weeks]

# KPIs
semanas_vividas = ((fecha_hoy - datetime.combine(fecha_nacimiento, datetime.min.time())).days) // 7
semanas_restantes = total_semanas - semanas_vividas
porcentaje_vivido = min(100, (semanas_vividas / total_semanas) * 100)
años_restantes = max(0, (fecha_muerte_estimada - fecha_hoy).days // 365)

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
        background: #f5f7fa;
        border-radius: 12px;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
    }
    .insight-card {
        background: #fff;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        font-size: 1.1rem;
    }
    .stMetric {
        background: #f5f7fa;
        border-radius: 10px;
        padding: 0.5rem 0.5rem;
        margin-bottom: 0.5rem;
    }
    .kpi-row {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }
    .insight-banner {
        background: #e1f5fe;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        text-align: center;
        transition: background 0.5s;
    }
    .insight-banner:nth-child(odd) {
        background: #fff3e0;
    }
    </style>
""", unsafe_allow_html=True)

# Actualizar la referencia de colores para que sea más compacta y en una sola línea
st.markdown("""
    <div style='margin-top: 10px; display: flex; flex-wrap: wrap; align-items: center;'>
""", unsafe_allow_html=True)

for etapa, color in colors.items():
    st.markdown(f"""
        <div style='display: flex; align-items: center; margin-right: 15px;'>
            <span style='display: inline-block; width: 15px; height: 15px; background-color: {color}; margin-right: 5px;'></span>
            <span style='font-size: 12px;'>{etapa}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
""", unsafe_allow_html=True)

# Quitar la leyenda del gráfico de barras horizontal acumulado
fig2 = go.Figure()
left = 0
for etapa, color in zip(fines_semana_por_etapa.keys(), [colors[e] for e in fines_semana_por_etapa.keys()]):
    porcentaje = df.loc[etapa, "Porcentaje"]
    porcentaje_acumulado = df.loc[etapa, "Porcentaje acumulado"]
    fig2.add_trace(go.Bar(
        y=[""],
        x=[fines_semana_por_etapa[etapa]],
        name=etapa,
        orientation='h',
        marker=dict(color=color),
        hovertemplate=(
            f"<b>{etapa}</b><br>"
            f"Semanas vividas: {{x}}<br>"
            f"Porcentaje: {porcentaje:.2f}%<br>"
            f"Porcentaje acumulado: {porcentaje_acumulado:.2f}%<extra></extra>"
        )
    ))
    left += fines_semana_por_etapa[etapa]

# Agregar representación para 'Futuro estimado'
if "Futuro estimado (37-76)" in fines_semana_por_etapa:
    semanas_futuro_estimado = etapas["Futuro estimado (37-76)"] - fines_semana_por_etapa["Futuro estimado (37-76)"]
    if semanas_futuro_estimado > 0:
        porcentaje = (semanas_futuro_estimado / total_semanas) * 100
        porcentaje_acumulado = 100  # Siempre será el 100% acumulado al final
        fig2.add_trace(go.Bar(
            y=[""],
            x=[semanas_futuro_estimado],
            name="Futuro estimado restante",
            orientation='h',
            marker=dict(color=colors["Futuro estimado (37-76)"], opacity=0.5),
            hovertemplate=(
                "<b>Futuro estimado restante</b><br>"
                f"Semanas restantes: {{x}}<br>"
                f"Porcentaje: {porcentaje:.2f}%<br>"
                f"Porcentaje acumulado: {porcentaje_acumulado:.2f}%<extra></extra>"
            )
        ))

fig2.update_layout(
    barmode='stack',
    xaxis_title='Fines de semana vividos',
    showlegend=False,  # Leyenda desactivada
    margin=dict(l=0, r=0, t=30, b=0)  # Ajustar márgenes si es necesario
)
st.plotly_chart(fig2, use_container_width=True)

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

dias_libres = dias_despiertos - (dias_trabajados + dias_trabajo_futuro)

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
        horas_dormidas_etapa = horas_dormidas
        horas_trabajadas_etapa = horas_trabajadas
        horas_personales_etapa = horas_personales

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
        horas_dormidas_etapa = semanas_etapa * 7 * horas_dormir_por_dia
        horas_trabajadas_etapa = semanas_etapa * 7 * horas_trabajo_por_dia
        horas_personales_etapa = (semanas_etapa * 7 * horas_por_dia) - (horas_dormidas_etapa + horas_trabajadas_etapa)

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

# Mostrar tablas con horas
st.subheader("Distribución de horas")
col1, col2 = st.columns(2)

# Botón para elegir entre total o etapa específica
etapa_seleccionada = st.selectbox(
    "Selecciona una etapa para ver los valores relativos:",
    ["Total"] + list(etapas.keys()),
    key="selectbox_etapa_tabla"
)

if etapa_seleccionada == "Total":
    divisor = 1
    titulo_tabla = "Valores totales"
    horas_dormidas_etapa = horas_dormidas
    horas_trabajadas_etapa = horas_trabajadas
    horas_personales_etapa = horas_personales
else:
    divisor = etapas[etapa_seleccionada] * 7 * horas_por_dia
    titulo_tabla = f"Valores relativos a la etapa: {etapa_seleccionada}"
    semanas_etapa = etapas[etapa_seleccionada]
    horas_dormidas_etapa = semanas_etapa * 7 * horas_dormir_por_dia
    horas_trabajadas_etapa = semanas_etapa * 7 * horas_trabajo_por_dia
    horas_personales_etapa = (semanas_etapa * 7 * horas_por_dia) - (horas_dormidas_etapa + horas_trabajadas_etapa)

# Actualizar tabla de "Horas actuales" con valores dinámicos
with col1:
    st.markdown(f"### {titulo_tabla} - Horas actuales")
    st.table(pd.DataFrame({
        "Categoría": ["Durmiendo", "Trabajando", "Tiempo personal"],
        "Horas": [
            f"{int(horas_dormidas_etapa):,}".replace(",", "."),
            f"{int(horas_trabajadas_etapa):,}".replace(",", "."),
            f"{int(horas_personales_etapa):,}".replace(",", ".")
        ],
        "%": [
            f"{(horas_dormidas_etapa / divisor * 100):.2f}%" if divisor > 1 else "-",
            f"{(horas_trabajadas_etapa / divisor * 100):.2f}%" if divisor > 1 else "-",
            f"{(horas_personales_etapa / divisor * 100):.2f}%" if divisor > 1 else "-"
        ]
    }))

with col2:
    st.markdown(f"### {titulo_tabla} - Horas restantes")
    st.table(pd.DataFrame({
        "Categoría": ["Trabajo futuro", "Tiempo personal restante"],
        "Horas": [f"{int(horas_trabajo_futuro):,}".replace(",", "."), f"{int(horas_personales_restantes):,}".replace(",", ".")],
        "%": [
            f"{(horas_trabajo_futuro / divisor * 100):.2f}%" if divisor > 1 else "-",
            f"{(horas_personales_restantes / divisor * 100):.2f}%" if divisor > 1 else "-"
        ]
    }))

# Actualizar gráfico de torta "Distribución del tiempo" dinámicamente
fig_sleep_awake = go.Figure()
fig_sleep_awake.add_trace(go.Pie(
    labels=["Durmiendo", "Trabajando", "Tiempo personal"],
    values=[
        horas_dormidas_etapa / horas_por_dia,
        horas_trabajadas_etapa / horas_por_dia,
        horas_personales_etapa / horas_por_dia
    ],
    hole=0.4
))
fig_sleep_awake.update_layout(
    title="Distribución del tiempo: Durmiendo, Trabajando y Tiempo Personal"
)

# Mostrar gráficos en una línea horizontal
st.subheader("Gráficos de distribución")
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_sleep_awake, use_container_width=True, key="plotly_chart_sleep_awake_2")

with col2:
    st.plotly_chart(fig_remaining_time, use_container_width=True, key="plotly_chart_remaining_time_2")

# Mostrar los insights como una lista estática
insights = [
    f"🌟 Ya viviste el {porcentaje_vivido:.2f}% de tu vida. Aún te quedan {años_restantes} años llenos de potencial.",
    f"🎨 Cada punto en tu gráfico es una semana: una historia, una oportunidad. ¿Cómo vas a pintar las siguientes {semanas_restantes} semanas?",
    f"⌛ Si te quedan {semanas_restantes} semanas, ¿cuántas dedicarás a lo verdaderamente importante?",
    f"📅 Viviste más de {(fecha_hoy - datetime.combine(fecha_nac_dt, datetime.min.time())).days} días desde que naciste.",
    f"🌕 Sobreviviste a unas {((fecha_hoy - datetime.combine(fecha_nac_dt, datetime.min.time())).days // 29)} lunas llenas.",
    f"😴 Estuviste despierto unos {((fecha_hoy - datetime.combine(fecha_nac_dt, datetime.min.time())).days * 2 // 3)} días completos (si dormiste 8 hs por día).",
    f"🍃 Disfrutaste al menos {semanas_vividas // 1} fines de semana: más de {semanas_vividas * 2} días de descanso.",
    "👶 0-5 años: Aprendiste a ser humano.",
    "👦 5-18 años: Formaste tu identidad.",
    "🧑 18-24 años: Exploraste tu independencia.",
    "👨 24-37 años: Construiste vínculos y carrera.",
    "🧘 37+: Tiempo de vivir con intención.",
    "📘 Si querés leer 30 libros antes de los 76, solo necesitás uno cada ~1.3 años.",
    f"🕒 Si dedicaras 1 hora semanal a un proyecto personal, en 20 años sumarías más de 1.000 horas."
]

st.subheader("Insights")
st.markdown("<ul>", unsafe_allow_html=True)
for insight in insights:
    st.markdown(f"<li>{insight}</li>", unsafe_allow_html=True)
st.markdown("</ul>", unsafe_allow_html=True)
 

st.caption("Hecho con ❤️ por TimeLeft")


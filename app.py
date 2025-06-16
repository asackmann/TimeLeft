import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import warnings
import io
import contextlib
import json
import time

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
    ("Carrera y noviazgo", 24, 37, "#FF8C00"),        # Naranja (adultez)
    ("Futuro estimado", 37, esperanza_vida, "#F8F8FF"), # Casi blanco (futuro)
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

# Agregar estilo CSS para ocultar los divs de advertencias
st.markdown(
    """
    <style>
    div[data-testid="stAlert"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Rediseño de la página principal
# KPIs en una única línea
kpi_cols = st.columns(4)
kpi_cols[0].metric("% de vida vivido", f"{porcentaje_vivido:.2f}%")
kpi_cols[1].metric("Fines de semana vividos", semanas_vividas)
kpi_cols[2].metric("Fines de semana restantes", semanas_restantes)
kpi_cols[3].metric("Años restantes", años_restantes)

# Gráficas al final
st.subheader("Gráficas")
# Gráfica de círculos
fig, ax = plt.subplots(figsize=(16, 5))
ax.scatter(x, -y, c=color_list, s=28)
ax.axis("off")
ax.set_title(f"Cada círculo representa una semana de vida de {nombre}", fontsize=20, pad=20)
legend_patches = [mpatches.Patch(color=col, label=etapa) for etapa, col in colors.items()]
ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=2, fontsize=12, frameon=False)
st.pyplot(fig, use_container_width=True)

# Gráfico de barras horizontal acumulado
fig2, ax2 = plt.subplots(figsize=(10, 2))  # Cambiar la altura a 2 cm
left = 0
for etapa, color in zip(fines_semana_por_etapa.keys(), [colors[e] for e in fines_semana_por_etapa.keys()]):
    ax2.barh([""], [fines_semana_por_etapa[etapa]], left=left, color=color, label=etapa)
    left += fines_semana_por_etapa[etapa]

# Agregar representación para 'Futuro estimado'
if "Futuro estimado (37-76)" in fines_semana_por_etapa:
    semanas_futuro_estimado = etapas["Futuro estimado (37-76)"] - fines_semana_por_etapa["Futuro estimado (37-76)"]
    if semanas_futuro_estimado > 0:
        ax2.barh([""], [semanas_futuro_estimado], left=left, color=colors["Futuro estimado (37-76)"], alpha=0.5, label="Futuro estimado restante")

ax2.set_xlabel('Fines de semana vividos')
ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, frameon=False)
fig2.tight_layout()
st.pyplot(fig2, use_container_width=True)

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


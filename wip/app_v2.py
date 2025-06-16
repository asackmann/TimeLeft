import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="TimeLeft Dashboard", layout="wide")
st.title("⏳ TimeLeft Dashboard: Tomá conciencia de tu tiempo")

# --- Entradas del usuario ---
nombre = st.sidebar.text_input("Nombre", "Agustín")
fecha_nacimiento = st.sidebar.date_input("Fecha de nacimiento", datetime.date(1988, 5, 19))
esperanza_vida = st.sidebar.number_input("Esperanza de vida (años)", min_value=1, max_value=120, value=76)
tiempo_libre_diario = st.sidebar.slider("Horas promedio de tiempo personal por día", 0.0, 16.0, 4.0, 0.5)

# --- Cálculos base ---
fecha_hoy = datetime.date.today()
fecha_muerte = datetime.date(fecha_nacimiento.year + esperanza_vida, fecha_nacimiento.month, fecha_nacimiento.day)

dias_vividos = (fecha_hoy - fecha_nacimiento).days
semanas_vividas = dias_vividos // 7
semanas_totales = (fecha_muerte - fecha_nacimiento).days // 7
semanas_restantes = semanas_totales - semanas_vividas

# --- KPIs ---
st.subheader("Resumen actual de tu vida")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("% de vida vivida", f"{(semanas_vividas/semanas_totales)*100:.2f}%")
kpi2.metric("Semanas vividas", semanas_vividas)
kpi3.metric("Semanas restantes", semanas_restantes)
kpi4.metric("Días totales vividos", dias_vividos)

# --- Tiempo personal proyectado ---
st.subheader("Tu tiempo personal disponible (proyección futura)")
horas_libres_por_semana = tiempo_libre_diario * 7
horas_restantes = horas_libres_por_semana * semanas_restantes
dias_libres_estimados = horas_restantes // 24

col1, col2, col3 = st.columns(3)
col1.metric("Horas personales/semana", f"{horas_libres_por_semana:.0f}h")
col2.metric("Total de horas personales restantes", f"{horas_restantes:.0f}h")
col3.metric("Equivalente en días libres completos", f"{dias_libres_estimados:.0f} días")

# --- Insights simples ---
st.subheader("📌 Insights inspiradores")
st.info(f"🌟 Ya viviste el {(semanas_vividas/semanas_totales)*100:.2f}% de tu vida. Aún te quedan {semanas_restantes} semanas.")
st.info(f"💪 Si dedicás solo 1 hora diaria a algo que amás, te quedan {semanas_restantes * 7} horas para eso.")
st.info(f"📖 Podrías leer unos {int(horas_restantes // 8)} libros (asumiendo 8hs/libro).")

# --- Visualización estilo Tail End ---
st.subheader("🟢 Tu vida en semanas (visualización estilo 'The Tail End')")
cols = 52
rows = semanas_totales // cols + 1

x = np.tile(np.arange(cols), rows)
y = np.repeat(np.arange(rows), cols)
colors = ["#F0F0F0"] * semanas_totales
for i in range(semanas_vividas):
    colors[i] = "#1f77b4"  # azul para semanas vividas

fig = go.Figure(data=go.Scatter(
    x=x[:semanas_totales],
    y=-y[:semanas_totales],
    mode='markers',
    marker=dict(size=6, color=colors, opacity=0.8),
    hoverinfo='skip'
))
fig.update_layout(
    title="Cada círculo representa una semana de vida",
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
    height=500,
    margin=dict(t=50, b=20, l=20, r=20)
)
st.plotly_chart(fig, use_container_width=True)

# --- Coming soon ---
st.subheader("🚀 Proximamente")
st.markdown("- Análisis de uso histórico del tiempo")
st.markdown("- Simulador de escenarios \"what if\"")
st.markdown("- Comparación entre prioridades y tiempo real disponible")
st.markdown("- Planificador de proyectos personales con impacto")

st.caption("Hecho con ❤️ por TimeLeft")

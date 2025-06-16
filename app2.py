import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

st.set_page_config(page_title="TimeLeft - Visualiza tu vida", layout="wide")
st.title("⏳ TimeLeft: Visualiza tu vida en semanas")

# --- Definir un valor seguro para esperanza de vida por defecto ---
ESPERANZA_VIDA_DEFAULT = 76

# Leer parámetros de la URL si existen
query_params = st.query_params
nombre_url = query_params.get("nombre", [None])
if isinstance(nombre_url, list):
    if len(nombre_url) == 1:
        nombre_url = nombre_url[0]
    else:
        nombre_url = " ".join(nombre_url)
else:
    pass
if nombre_url is not None and nombre_url.strip():
    if isinstance(nombre_url, list):
        nombre_default = " ".join(nombre_url)
    else:
        nombre_default = nombre_url
else:
    nombre_default = "Agustín"

fecha_nacimiento_str = query_params.get("fecha_nacimiento", [datetime(1988, 5, 19).strftime("%Y-%m-%d")])[0]
try:
    fecha_nacimiento_default = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
except Exception:
    fecha_nacimiento_default = datetime(1988, 5, 19).date()

esperanza_vida_url = int(query_params.get("esperanza_vida", [ESPERANZA_VIDA_DEFAULT])[0])

# --- Etapas por defecto SIEMPRE usan el valor seguro ---
etapas_default = [
    {"nombre": "De nacimiento a conciencia", "inicio": 0, "fin": 5, "color": "#FFD700"},
    {"nombre": "Infancia consciente", "inicio": 5, "fin": 18, "color": "#87CEEB"},
    {"nombre": "Universidad y soltería", "inicio": 18, "fin": 24, "color": "#32CD32"},
    {"nombre": "Carrera y noviazgo", "inicio": 24, "fin": 37, "color": "#FF8C00"},
    {"nombre": "Futuro estimado", "inicio": 37, "fin": ESPERANZA_VIDA_DEFAULT, "color": "#F8F8FF"},
]

# --- Inicialización robusta de session_state ---
if "initialized" not in st.session_state:
    st.session_state["nombre"] = nombre_default
    st.session_state["fecha_nacimiento"] = fecha_nacimiento_default
    st.session_state["esperanza_vida"] = esperanza_vida_url
    st.session_state["etapas"] = [etapa.copy() for etapa in etapas_default]
    st.session_state["n_etapas"] = len(etapas_default)
    st.session_state["initialized"] = True

# Sidebar para inputs (solo una vez, SIEMPRE desde session_state)
st.sidebar.header("Configura tus datos")
nombre = st.sidebar.text_input("¿Cuál es tu nombre?", st.session_state["nombre"], key="sidebar_nombre")
fecha_nacimiento = st.sidebar.date_input("Fecha de nacimiento", st.session_state["fecha_nacimiento"], key="sidebar_fecha_nacimiento")
esperanza_vida = st.sidebar.number_input("Esperanza de vida (años)", min_value=1, max_value=120, value=int(st.session_state["esperanza_vida"]), key="sidebar_esperanza_vida")

# Configuración de etapas personalizables
st.sidebar.markdown("---")
st.sidebar.subheader("Etapas de la vida")

# Mostrar y editar etapas desde session_state
n_etapas = st.sidebar.number_input("Cantidad de etapas", min_value=1, max_value=10, value=st.session_state["n_etapas"], step=1, key="sidebar_n_etapas")

# Ajustar cantidad de etapas en session_state
if n_etapas > len(st.session_state.etapas):
    for _ in range(n_etapas - len(st.session_state.etapas)):
        st.session_state.etapas.append({
            "nombre": f"Etapa {len(st.session_state.etapas)+1}",
            "inicio": 0,
            "fin": int(esperanza_vida),
            "color": "#CCCCCC"
        })
elif n_etapas < len(st.session_state.etapas):
    st.session_state.etapas = st.session_state.etapas[:n_etapas]
st.session_state["n_etapas"] = n_etapas

for i in range(n_etapas):
    fin_val = int(st.session_state.etapas[i]["fin"])
    inicio_val = int(st.session_state.etapas[i]["inicio"])
    if inicio_val > int(esperanza_vida):
        inicio_val = int(esperanza_vida)
    if fin_val < inicio_val:
        fin_val = inicio_val
    if fin_val > int(esperanza_vida):
        fin_val = int(esperanza_vida)
    st.session_state.etapas[i]["nombre"] = st.text_input(f"Nombre etapa {i+1}", st.session_state.etapas[i]["nombre"], key=f"nombre_etapa_{i}")
    st.session_state.etapas[i]["inicio"] = st.number_input(f"Edad inicio {i+1}", min_value=0, max_value=int(esperanza_vida), value=inicio_val, key=f"inicio_etapa_{i}")
    st.session_state.etapas[i]["fin"] = st.number_input(f"Edad fin {i+1}", min_value=inicio_val, max_value=int(esperanza_vida), value=fin_val, key=f"fin_etapa_{i}")
    st.session_state.etapas[i]["color"] = st.color_picker(f"Color etapa {i+1}", st.session_state.etapas[i]["color"], key=f"color_etapa_{i}")

# Menú de configuración avanzada (rueda)
with st.sidebar.expander('⚙️ Configuración avanzada', expanded=False):
    st.markdown('Ajustá todos los parámetros y guardá tu configuración personalizada.')
    nombre_setting = st.text_input("¿Cuál es tu nombre?", st.session_state["nombre"], key="settings_nombre")
    fecha_nacimiento_setting = st.date_input("Fecha de nacimiento", st.session_state["fecha_nacimiento"], key="settings_fecha_nacimiento")
    esperanza_vida_setting = st.number_input("Esperanza de vida (años)", min_value=1, max_value=120, value=int(st.session_state["esperanza_vida"]), key="settings_esperanza_vida")
    n_etapas_setting = st.number_input("Cantidad de etapas", min_value=1, max_value=10, value=st.session_state["n_etapas"], step=1, key="settings_n_etapas")
    if st.button('Restaurar valores por defecto', key='restaurar_default'):
        st.session_state["nombre"] = nombre_default
        st.session_state["fecha_nacimiento"] = fecha_nacimiento_default
        st.session_state["esperanza_vida"] = ESPERANZA_VIDA_DEFAULT
        st.session_state["etapas"] = [etapa.copy() for etapa in etapas_default]
        st.session_state["n_etapas"] = len(etapas_default)
        st.success("Valores por defecto restaurados.")
    if st.button('Guardar configuración', key='guardar_config'):
        st.session_state["etapas"] = st.session_state["etapas"][:n_etapas_setting]
        st.session_state["nombre"] = nombre_setting
        st.session_state["fecha_nacimiento"] = fecha_nacimiento_setting
        st.session_state["esperanza_vida"] = esperanza_vida_setting
        st.session_state["n_etapas"] = n_etapas_setting
        st.success("¡Configuración guardada!")

# Usar los valores de session_state para el resto de la app
nombre = st.session_state["nombre"]
fecha_nacimiento = st.session_state["fecha_nacimiento"]
esperanza_vida = int(st.session_state["esperanza_vida"])
etapas_ordenadas = sorted(st.session_state["etapas"], key=lambda e: e["inicio"])

fecha_hoy = datetime.today()

# Convertir fecha_nacimiento a datetime.datetime si es date
if isinstance(fecha_nacimiento, datetime):
    fecha_nac_dt = fecha_nacimiento
else:
    fecha_nac_dt = datetime.combine(fecha_nacimiento, datetime.min.time())

fecha_muerte_estimada = datetime(fecha_nac_dt.year + esperanza_vida, fecha_nac_dt.month, fecha_nac_dt.day)

# Etapas y colores
etapas = {}
colors = {}
for etapa in etapas_ordenadas:
    nombre_etapa = etapa["nombre"]
    edad_ini = int(etapa["inicio"])
    edad_fin = int(etapa["fin"])
    color = etapa["color"]
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
    </style>
""", unsafe_allow_html=True)

# KPIs primero
st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
st.metric("% de vida vivido", f"{porcentaje_vivido:.2f}%")
st.metric("Fines de semana vividos", semanas_vividas)
st.metric("Fines de semana restantes", semanas_restantes)
st.metric("Años restantes", años_restantes)
st.markdown('</div>', unsafe_allow_html=True)

# Gráfica de círculos
fig, ax = plt.subplots(figsize=(16, 5))
ax.scatter(x, -y, c=color_list, s=28)
ax.axis("off")
ax.set_title(f"Cada círculo representa una semana de vida de {nombre}", fontsize=20, pad=20)
legend_patches = [mpatches.Patch(color=col, label=etapa) for etapa, col in colors.items()]
ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=2, fontsize=12, frameon=False)
#kpi_text = (
#    f"% de vida vivido: {porcentaje_vivido:.2f}%\n"
#    f"Fines de semana vividos: {semanas_vividas}\n"
#    f"Fines de semana restantes: {semanas_restantes}\n"
#    f"Años restantes: {años_restantes}"
#)
#ax.text(1.02, 0.8, kpi_text, transform=ax.transAxes, fontsize=14, va='top', bbox=dict(facecolor='#f5f7fa', alpha=0.9, boxstyle='round,pad=0.5'))
st.pyplot(fig, use_container_width=True)

# Insights
st.subheader("Insights sobre tu vida")
# Insights sobre tu vida
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
for i in insights:
    st.markdown(f'<div class="insight-card">{i}</div>', unsafe_allow_html=True)

# Gráfico de barras horizontal acumulado
st.subheader("Fines de semana vividos por etapa (acumulado)")
fig2, ax2 = plt.subplots(figsize=(10, 3.5))
left = 0
for etapa, color in zip(fines_semana_por_etapa.keys(), [colors[e] for e in fines_semana_por_etapa.keys()]):
    ax2.barh([""], [fines_semana_por_etapa[etapa]], left=left, color=color, label=etapa)
    left += fines_semana_por_etapa[etapa]
ax2.set_xlabel('Fines de semana vividos')
ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, frameon=False)
fig2.tight_layout()
st.pyplot(fig2, use_container_width=True)

# Botón para compartir la URL actual
st.markdown("""
<div style='text-align:right; margin-bottom: 1.5rem;'>
    <button id="share-btn" style="background:#2563eb;color:white;padding:0.5rem 1.2rem;border:none;border-radius:8px;font-size:1rem;cursor:pointer;">🔗 Compartir</button>
    <input id="share-url" type="text" value="" style="width:0px;height:0px;opacity:0;position:absolute;left:-9999px;">
</div>
<script>
    const btn = window.parent.document.getElementById('share-btn');
    if(btn){
        btn.onclick = function(){
            const url = window.parent.location.href;
            const input = window.parent.document.getElementById('share-url');
            input.value = url;
            input.type = 'text';
            input.select();
            document.execCommand('copy');
            input.type = 'hidden';
            btn.innerText = '✅ Copiado!';
            setTimeout(()=>{btn.innerText='🔗 Compartir'}, 1500);
        }
    }
</script>
""", unsafe_allow_html=True)

st.caption("Hecho con ❤️ por TimeLeft")

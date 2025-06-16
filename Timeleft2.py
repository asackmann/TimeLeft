
# Timeleft.py

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def input_default(prompt, default):
    user_input = input(f"{prompt} [{default}]: ")
    return user_input.strip() or default

def generar_insights(nombre, semanas_vividas, semanas_restantes, porcentaje_vivido, años_restantes, fines_semana_por_etapa):
    total_fines = sum(fines_semana_por_etapa.values())
    insights = []

    insights.append(f"🌟 Ya viviste el {porcentaje_vivido:.2f}% de tu vida. Aún te quedan {años_restantes} años llenos de potencial.")
    insights.append(f"🎨 Cada punto en tu gráfico es una semana: una historia, una oportunidad. ¿Cómo vas a pintar las siguientes {semanas_restantes} semanas?")
    insights.append(f"⌛ Si te quedan {semanas_restantes} semanas, ¿cuántas dedicarás a lo verdaderamente importante?")
    dias_totales = semanas_vividas * 7
    insights.append(f"📅 Viviste más de {dias_totales} días desde que naciste.")
    insights.append(f"🌕 Sobreviviste a unas {dias_totales // 29} lunas llenas.")
    insights.append(f"😴 Estuviste despierto unos {(dias_totales * 16)//24} días completos (si dormiste 8 hs por día).")
    insights.append(f"🍃 Disfrutaste al menos {total_fines} fines de semana: más de {total_fines * 2} días de descanso.")
    etapa_reflexiva = [
        "👶 0-5 años: Aprendiste a ser humano.",
        "👦 5-18 años: Formaste tu identidad.",
        "🧑 18-24 años: Exploraste tu independencia.",
        "👨 24-37 años: Construiste vínculos y carrera.",
        "🧘 37+: Tiempo de vivir con intención."
    ]
    insights.extend(etapa_reflexiva)
    insights.append(f"📘 Si querés leer 30 libros antes de los 76, solo necesitás uno cada ~1.3 años.")
    insights.append(f"🕒 Si dedicaras 1 hora semanal a un proyecto personal, en 20 años sumarías más de 1.000 horas.")

    return insights

# Entradas del usuario
nombre = input_default("¿Cuál es tu nombre?", "Agustín")
fecha_nacimiento_str = input_default("Fecha de nacimiento (YYYY-MM-DD)", "1988-05-19")
fecha_hoy = datetime.today()
esperanza_vida = int(input_default("Esperanza de vida (años)", "76"))

fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d")
fecha_muerte_estimada = datetime(fecha_nacimiento.year + esperanza_vida, fecha_nacimiento.month, fecha_nacimiento.day)

# Etapas
etapas_input = [
    ("De nacimiento a conciencia", 0, 5, "#FFD700"),
    ("Infancia consciente", 5, 18, "#87CEEB"),
    ("Universidad y soltería", 18, 24, "#32CD32"),
    ("Carrera y noviazgo", 24, 37, "#FF8C00"),
    ("Futuro estimado", 37, esperanza_vida, "#F8F8FF"),
]

etapas = {}
colors = {}
for nombre_etapa, edad_ini, edad_fin, color in etapas_input:
    fecha_ini = max(fecha_nacimiento, datetime(fecha_nacimiento.year + edad_ini, fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_fin = min(datetime(fecha_nacimiento.year + edad_fin, fecha_nacimiento.month, fecha_nacimiento.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = semanas
    colors[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = color

df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)

color_list = []
for etapa, row in df.iterrows():
    color_list.extend([colors[etapa]] * int(row["Semanas"]))

total_weeks = len(color_list)
cols = 100
rows = (total_weeks // cols) + 1
x = np.tile(np.arange(cols), rows)[:total_weeks]
y = np.repeat(np.arange(rows), cols)[:total_weeks]

# KPIs
semanas_vividas = ((fecha_hoy - fecha_nacimiento).days) // 7
semanas_restantes = total_semanas - semanas_vividas
porcentaje_vivido = min(100, (semanas_vividas / total_semanas) * 100)
años_restantes = max(0, (fecha_muerte_estimada - fecha_hoy).days // 365)

# Fines de semana por etapa
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

# Gráfico de semanas
plt.figure(figsize=(18, 6))
plt.scatter(x, -y, c=color_list, s=20)
plt.axis("off")
plt.title(f"Semana de vida de {nombre}")
kpi_text = (
    f"% de vida vivido: {porcentaje_vivido:.2f}%\n"
    f"Semanas vividas: {semanas_vividas}\n"
    f"Semanas restantes: {semanas_restantes}\n"
    f"Años restantes: {años_restantes}"
)
plt.gcf().text(0.02, 0.85, kpi_text, fontsize=14, bbox=dict(facecolor='white', alpha=0.7))
legend_patches = [mpatches.Patch(color=col, label=etapa) for etapa, col in colors.items()]
plt.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3)
plt.tight_layout()
output_filename = f"semanas_de_vida_{nombre.lower().replace(' ', '_')}.pdf"
plt.savefig(output_filename, format='pdf')
plt.show()

# Gráfico de barras: fines de semana
plt.figure(figsize=(12, 5))
plt.bar(fines_semana_por_etapa.keys(), fines_semana_por_etapa.values(), color=[colors[e] for e in fines_semana_por_etapa.keys()])
plt.ylabel('Fines de semana vividos')
plt.title('Fines de semana vividos por etapa')
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.show()

# Exportar tabla
df.to_csv(f"tabla_etapas_vida_{nombre.lower().replace(' ', '_')}.csv")

# Generar insights
insights = generar_insights(nombre, semanas_vividas, semanas_restantes, porcentaje_vivido, años_restantes, fines_semana_por_etapa)
insights_filename = f"insights_vida_{nombre.lower().replace(' ', '_')}.txt"
with open(insights_filename, "w", encoding="utf-8") as f:
    for frase in insights:
        f.write(frase + "\n")

print(f"✅ Gráfico guardado como: {output_filename}")
print(f"✅ Tabla guardada como: tabla_etapas_vida_{nombre.lower().replace(' ', '_')}.csv")
print(f"✅ Insights guardados como: {insights_filename}")

# Timeleft.py


from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Función para pedir entrada con valor por defecto
def input_default(prompt, default):
    user_input = input(f"{prompt} [{default}]: ")
    return user_input.strip() or default

# Entradas desde consola
nombre = input_default("¿Cuál es tu nombre?", "Agustín")
fecha_nacimiento_str = input_default("Fecha de nacimiento (YYYY-MM-DD)", "1988-05-19")
# Obtener fecha actual automáticamente
fecha_hoy = datetime.today()
fecha_hoy_str = fecha_hoy.strftime("%Y-%m-%d")
esperanza_vida = int(input_default("Esperanza de vida (años)", "76"))

# Convertir fechas
fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d")
# Usar fecha_hoy ya obtenida
fecha_muerte_estimada = datetime(fecha_nacimiento.year + esperanza_vida, fecha_nacimiento.month, fecha_nacimiento.day)

# Etapas configurables con nuevos colores
etapas_input = [
    ("De nacimiento a conciencia", 0, 5, "#FFD700"),  # Amarillo (infancia)
    ("Infancia consciente", 5, 18, "#87CEEB"),         # Celeste (niñez/adolescencia)
    ("Universidad y soltería", 18, 24, "#32CD32"),    # Verde (juventud)
    ("Carrera y noviazgo", 24, 37, "#FF8C00"),        # Naranja (adultez)
    ("Futuro estimado", 37, esperanza_vida, "#F8F8FF"), # Casi blanco (futuro)
]

# Construcción de etapas con semanas
etapas = {}
colors = {}
for nombre_etapa, edad_ini, edad_fin, color in etapas_input:
    fecha_ini = max(fecha_nacimiento, datetime(fecha_nacimiento.year + edad_ini, fecha_nacimiento.month, fecha_nacimiento.day))
    fecha_fin = min(datetime(fecha_nacimiento.year + edad_fin, fecha_nacimiento.month, fecha_nacimiento.day), fecha_muerte_estimada)
    semanas = max(0, (fecha_fin - fecha_ini).days // 7)
    etapas[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = semanas
    colors[nombre_etapa + f" ({edad_ini}-{edad_fin})"] = color

# Crear DataFrame
df = pd.DataFrame.from_dict(etapas, orient="index", columns=["Semanas"])
total_semanas = df["Semanas"].sum()
df["Porcentaje"] = (df["Semanas"] / total_semanas * 100).round(2)
df["Porcentaje acumulado"] = df["Porcentaje"].cumsum().round(2)

# Asignar colores por semana
color_list = []
for etapa, row in df.iterrows():
    color_list.extend([colors[etapa]] * int(row["Semanas"]))

# Grilla
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

# Graficar
plt.figure(figsize=(18, 6))
plt.scatter(x, -y, c=color_list, s=20)
plt.axis("off")
plt.title(f"Semana de vida de {nombre}")

# KPIs en la gráfica principal
kpi_text = (
    f"% de vida vivido: {porcentaje_vivido:.2f}%\n"
    f"Semanas vividas: {semanas_vividas}\n"
    f"Semanas restantes: {semanas_restantes}\n"
    f"Años restantes: {años_restantes}"
)
plt.gcf().text(0.02, 0.85, kpi_text, fontsize=14, bbox=dict(facecolor='white', alpha=0.7))

# Leyenda
legend_patches = [mpatches.Patch(color=col, label=etapa) for etapa, col in colors.items()]
plt.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3)
plt.tight_layout()

# Guardar como PDF
output_filename = f"semanas_de_vida_{nombre.lower().replace(' ', '_')}.pdf"
plt.savefig(output_filename, format='pdf')
plt.show()

# Gráfica de barras: fines de semana vividos por etapa
plt.figure(figsize=(12, 5))
plt.bar(fines_semana_por_etapa.keys(), fines_semana_por_etapa.values(), color=[colors[e] for e in fines_semana_por_etapa.keys()])
plt.ylabel('Fines de semana vividos')
plt.title('Fines de semana vividos por etapa')
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.show()

# Exportar tabla como CSV
df.to_csv(f"tabla_etapas_vida_{nombre.lower().replace(' ', '_')}.csv")

print(f"\n✅ Gráfico guardado como: {output_filename}")
print(f"✅ Tabla guardada como: tabla_etapas_vida_{nombre.lower().replace(' ', '_')}.csv")

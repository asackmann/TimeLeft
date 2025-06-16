# ⏳ Timeleft.py — Visualiza tu vida semana a semana

**Timeleft.py** es una herramienta visual y reflexiva que transforma los datos de tu vida en una narrativa poderosa: cada semana vivida y por vivir se representa como un círculo, organizado por etapas significativas y coloreado de forma única.

Te permite entender cuánto viviste, cuánto podrías vivir según la esperanza de vida, y cómo se distribuye tu tiempo entre distintas fases personales.

---

## 📦 ¿Qué hace este script?

- 🧮 Calcula **todas las semanas de tu vida** desde tu nacimiento hasta una expectativa de vida (por defecto, 76 años).
- 🎨 Genera un **gráfico de círculos** donde cada punto representa una semana vivida o futura, coloreado según la etapa de tu vida.
- 📊 Crea una **tabla resumen** con porcentaje y porcentaje acumulado por etapa.
- 📅 Muestra la cantidad de **fines de semana vividos** por etapa en un gráfico de barras.
- 💡 Produce un archivo `.txt` con **insights personalizados**, reflexiones y datos curiosos de tu vida.

---

## 🚀 Cómo usarlo

### 1. Requisitos

Instalá las dependencias si aún no las tenés:

```bash
pip install matplotlib pandas numpy
```


# IDEAS

## Etapas personalizables
quiero que sea posible configurar el tema de las etapas, para empezar que permita definir la edad donde termina cada etapa, por ejemplo:, el hasta! Tambien que permita definir el color de cada etapa, y que se pueda agregar o quitar etapas, y que cada etapa tenga un nombre descriptivo.

etapas_input = [
    ("De nacimiento a conciencia", 0, 5, "#FFD700"),  # Amarillo (infancia)
    ("Infancia consciente", 5, 18, "#87CEEB"),         # Celeste (niñez/adolescencia)
    ("Universidad y soltería", 18, 24, "#32CD32"),    # Verde (juventud)
    ("Carrera y noviazgo", 24, 37, "#FF8C00"),        # Naranja (adultez)
    ("Futuro estimado", 37, esperanza_vida, "#F8F8FF"), # Casi blanco (futuro)
]

## Durmiendo y trabajando
podrias agregar otra grafica que muestre el tiempo que pase durmiendo en mi vida, el tiempo despierto, el tiempo trabajando planteando la etapa de carrera, el tiempo que voy a estar trabajando de aca a una jubilizaicon hasta los 60, el tiempo que me queda segun esperanza de vida que no sea dormir ni trabajar en dias, horas o lo que creas 

## Etapa de paternidad y viajes
me interesa agregar la posibilidad opcional de etapa de paternidad, que muestre cuantos años tendra un hijo y tendre en distintos momentos de mi vida, que muestre viajes preguntando fechas de cada viaje, idealmente una web app que permita cargar toda la iformacion, 


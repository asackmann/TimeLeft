# charts.py
# This module contains functions for creating various charts.

import plotly.graph_objects as go

def crear_grafico_torta(labels, values, titulo):
    """Create a pie chart."""
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values, hole=0.4))
    fig.update_layout(title=titulo)
    return fig

def crear_grafico_barras(etapas, colores, semanas_vividas):
    """Create a bar chart."""
    fig = go.Figure()
    for etapa, color in zip(etapas.keys(), colores):
        semanas = etapas[etapa]
        fig.add_trace(go.Bar(
            y=[""],
            x=[semanas],
            name=etapa,
            orientation='h',
            marker=dict(color=color)
        ))
    fig.update_layout(barmode='stack', title="Etapas de la vida")
    return fig

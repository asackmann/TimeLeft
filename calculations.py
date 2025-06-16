# calculations.py
# This module contains functions for performing various calculations.

def calcular_semanas(fecha_inicio, fecha_fin):
    """Calculate the number of weeks between two dates."""
    return max(0, (fecha_fin - fecha_inicio).days // 7)

def calcular_horas_por_categoria(dias_totales, horas_dormir, horas_trabajo):
    """Calculate hours spent on different categories."""
    horas_dormidas = dias_totales * horas_dormir
    horas_trabajadas = dias_totales * horas_trabajo
    horas_personales = (dias_totales * 24) - (horas_dormidas + horas_trabajadas)
    return horas_dormidas, horas_trabajadas, horas_personales

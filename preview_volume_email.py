#!/usr/bin/env python3
"""
Test to simulate and preview the MUPAI Volume Engine email output.
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")

# Extract and execute the generate_volume_plan function
with open(streamlit_app_path, "r") as f:
    content = f.read()

# Find and extract the function
func_start = content.find("def generate_volume_plan(")
func_end = content.find("\ndef ", func_start + 10)
if func_end == -1:
    # If not found, look for the next major section
    func_end = content.find("# ==================== ", func_start + 10)

if func_start == -1 or func_end == -1:
    print("✗ Could not extract generate_volume_plan function")
    sys.exit(1)

func_code = content[func_start:func_end]

# Execute the function
exec_globals = {}
exec(compile(func_code, '<string>', 'exec'), exec_globals)
generate_volume_plan = exec_globals['generate_volume_plan']

print("=" * 80)
print("MUPAI VOLUME ENGINE - EMAIL OUTPUT PREVIEW")
print("=" * 80)
print()

# Test case: Intermediate user with good recovery
volume_plan = generate_volume_plan(
    level='intermedio',
    phase_energy='mantenimiento',
    ir_se=75.0,
    rir=2.0,
    training_days=4,
    ffmi_margin=-1.5
)

# Generate email-like output
email_section = f"""
=====================================
MUPAI VOLUME ENGINE — ADMIN ONLY
=====================================

Este análisis científico calcula el volumen de entrenamiento óptimo por grupo muscular
basado en el nivel del atleta, fase energética, capacidad de recuperación y proximidad
al límite genético. Los valores se ajustan dinámicamente según múltiples factores.

PARÁMETROS DE ENTRADA:
- Nivel de entrenamiento: {volume_plan['level'].capitalize()}
- Fase energética: {volume_plan['phase_energy'].capitalize()}
- IR-SE (Recuperación): {volume_plan['ir_se']:.1f}/100
- RIR (Reps in Reserve): {volume_plan['rir']:.1f}
- Días de entrenamiento: {volume_plan['training_days']} días/semana
- Margen FFMI: {volume_plan['ffmi_margin']:+.1f} puntos

FACTORES DE AJUSTE APLICADOS:
- Factor IR-SE (recuperación): {volume_plan['adjustment_factors']['ir_se_factor']} ({"óptima" if volume_plan['adjustment_factors']['ir_se_factor'] >= 0.95 else "reducida" if volume_plan['adjustment_factors']['ir_se_factor'] >= 0.80 else "comprometida"})
- Factor fase energética: {volume_plan['adjustment_factors']['phase_factor']} ({volume_plan['phase_energy']})
- Factor RIR (intensidad): {volume_plan['adjustment_factors']['rir_factor']} ({"alta intensidad" if volume_plan['rir'] <= 1 else "moderada" if volume_plan['rir'] <= 2 else "conservadora"})
- Factor FFMI (potencial): {volume_plan['adjustment_factors']['ffmi_factor']} ({"lejos del límite" if volume_plan['ffmi_margin'] <= -3 else "distancia moderada" if volume_plan['ffmi_margin'] <= 0 else "cerca/en límite"})
- Factor combinado: {volume_plan['adjustment_factors']['combined_factor']}

VOLUMEN RECOMENDADO POR GRUPO MUSCULAR:
┌────────────────┬─────┬─────┬─────┬──────────┬──────────┬──────────┬────────┐
│ Músculo        │ MEV │ MAV │ MRV │ Sets/sem │ Frec/sem │ Sets/ses │ Factor │
├────────────────┼─────┼─────┼─────┼──────────┼──────────┼──────────┼────────┤"""

for muscle, data in volume_plan['muscles'].items():
    email_section += f"""
│ {muscle:<14} │ {data['MEV']:>3} │ {data['MAV']:>3} │ {data['MRV']:>3} │ {data['recommended_sets_week']:>8} │ {data['sessions_per_week']:>8} │ {data['sets_per_session']:>8.1f} │ {data['adjustment_factor']:>6.2f} │"""

email_section += f"""
└────────────────┴─────┴─────┴─────┴──────────┴──────────┴──────────┴────────┘

MÉTRICAS GLOBALES:
- Volumen semanal total: {volume_plan['weekly_cap']} sets/semana
- Promedio por día de entrenamiento: {volume_plan['avg_sets_per_day']:.1f} sets/día
- Viabilidad del plan: {volume_plan['viability']} - {volume_plan['viability_message']}

"""

# Add warnings if any
if volume_plan['warnings']:
    email_section += "⚠️ ALERTAS Y RECOMENDACIONES:\n"
    for i, warning in enumerate(volume_plan['warnings'], 1):
        email_section += f"{i}. {warning}\n"
    email_section += "\n"

# Add distribution suggestions
if volume_plan['distribution_suggestions']:
    email_section += "📊 SUGERENCIAS DE DISTRIBUCIÓN:\n\n"
    for suggestion in volume_plan['distribution_suggestions']:
        email_section += f"{suggestion}\n"

email_section += """
NOTAS TÉCNICAS:
• MEV (Minimum Effective Volume): Volumen mínimo para mantener adaptaciones
• MAV (Maximum Adaptive Volume): Volumen óptimo para máximas ganancias
• MRV (Maximum Recoverable Volume): Volumen máximo antes de sobreentrenamiento
• Factor de ajuste: Multiplica MAV base para obtener recomendación personalizada
• Los valores se ajustan dinámicamente según recuperación, fase y proximidad al límite

INTERPRETACIÓN:
- OK: Plan balanceado y sostenible a largo plazo
- WARNING: Plan viable pero requiere monitoreo cercano de recuperación
- NOT_VIABLE: Plan necesita ajustes significativos antes de implementar

REFERENCIAS CIENTÍFICAS:
- Renaissance Periodization (Mike Israetel et al., 2015-2024)
- Volume Landmarks for Hypertrophy (Schoenfeld, 2017)
- Training Volume and Hypertrophy (Meta-analysis, Schoenfeld et al., 2019)
"""

print(email_section)
print()
print("=" * 80)
print("✓ Email section generated successfully!")
print("=" * 80)
print()
print("Summary:")
print(f"  • Total weekly volume: {volume_plan['weekly_cap']} sets")
print(f"  • Average per training day: {volume_plan['avg_sets_per_day']:.1f} sets")
print(f"  • Viability status: {volume_plan['viability']}")
print(f"  • Number of muscle groups: {len(volume_plan['muscles'])}")
print(f"  • Combined adjustment factor: {volume_plan['adjustment_factors']['combined_factor']}")
print()
print("✓ Preview complete!")

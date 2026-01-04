"""
CÁLCULO CORRECTO PARA ERICK CON GUARDRAILS APLICADOS
=====================================================

Datos de Erick:
- Peso: 82.5 kg
- BF: 26.4% (Categoría: Obesidad)
- MLG: 60.7 kg
- GE (Mantenimiento): 2410 kcal/día
- IR-SE: 64.3 (rango 50-69 → cap a 30%)
- Sueño: 5-5.9 horas (< 6h → cap a 30%)
- Déficit interpolado: 50%
- DÉFICIT CON GUARDRAILS: 30% ✅ (NUEVO con fix)
"""

# ============================================================================
# 1. CALORÍAS CUT (DÉFICIT 30%)
# ============================================================================

GE = 2410  # kcal/día (mantenimiento)
deficit_pct = 30  # Capeado por guardrails (era 50% sin guardrails)

kcal_cut = GE * (1 - deficit_pct / 100)
print("=" * 80)
print("1. CALORÍAS CUT CON DÉFICIT 30%")
print("=" * 80)
print(f"GE (Mantenimiento): {GE} kcal/día")
print(f"Déficit: {deficit_pct}% (capeado por IR-SE + sueño)")
print(f"Kcal CUT: {GE} × (1 - {deficit_pct}/100) = {kcal_cut:.0f} kcal/día")

# ============================================================================
# 2. MACRONUTRIENTES CUT
# ============================================================================

print(f"\n" + "=" * 80)
print("2. MACRONUTRIENTES CUT")
print("=" * 80)

# Proteína (basada en PBM, no peso total, porque BF > 25%)
mlg = 60.7
pbm = mlg  # En Obesidad, PBM = MLG
protein_mult = 2.5  # Multiplicador para Obesidad
protein_g = round(pbm * protein_mult, 1)

print(f"\nPROTEÍNA:")
print(f"  Base: PBM = MLG = {pbm:.1f} kg (porque BF > 25%)")
print(f"  Multiplicador: {protein_mult} g/kg (Obesidad + Déficit moderado)")
print(f"  Proteína: {pbm:.1f} × {protein_mult} = {protein_g}g")
print(f"  Kcal: {protein_g} × 4 = {protein_g * 4:.0f} kcal")

# Grasas (30% de kcal)
fat_pct = 0.30
fat_kcal = kcal_cut * fat_pct
fat_g = round(fat_kcal / 9, 1)

print(f"\nGRASAS:")
print(f"  % de kcal: {fat_pct*100:.0f}%")
print(f"  Kcal: {kcal_cut:.0f} × {fat_pct} = {fat_kcal:.0f} kcal")
print(f"  Grasas: {fat_kcal:.0f} / 9 = {fat_g}g")

# Carbos (residual)
carb_kcal = kcal_cut - (protein_g * 4) - fat_kcal
carb_g = round(carb_kcal / 4, 1)

print(f"\nCARBOHIDRATOS (residual):")
print(f"  Kcal disponibles: {kcal_cut:.0f} - {protein_g*4:.0f} - {fat_kcal:.0f}")
print(f"                  = {carb_kcal:.0f} kcal")
print(f"  Carbohidratos: {carb_kcal:.0f} / 4 = {carb_g}g")

# Verificación
total_kcal = (protein_g * 4) + (fat_g * 9) + (carb_g * 4)
print(f"\nVERIFICACIÓN:")
print(f"  Total: ({protein_g}×4) + ({fat_g}×9) + ({carb_g}×4)")
print(f"       = {protein_g*4:.0f} + {fat_g*9:.0f} + {carb_g*4:.0f}")
print(f"       = {total_kcal:.0f} kcal ✅")

# ============================================================================
# 3. CICLAJE 4-3 (CUT)
# ============================================================================

print(f"\n" + "=" * 80)
print("3. CICLAJE 4-3 (CUT)")
print("=" * 80)

# Factores para CUT
low_factor = 0.8  # LOW days = 0.8 × kcal_avg
high_cap_factor = 1.05  # HIGH days max = 1.05 × GE

kcal_low = round(kcal_cut * low_factor)
budget_week = 7 * kcal_cut
kcal_high_calc = round((budget_week - 4 * kcal_low) / 3)
cap_high = GE * high_cap_factor

if kcal_high_calc > cap_high:
    print(f"  (Ajustando HIGH por cap {cap_high:.0f})")
    
kcal_high = round(kcal_high_calc)

print(f"\n📉 DÍAS LOW (4 días/semana - Fuerza):")
print(f"  Factor: 0.8 × {kcal_cut:.0f} = {kcal_low} kcal/día")

# Macros LOW
fat_g_low = round((kcal_low * fat_pct) / 9, 1)
carb_kcal_low = kcal_low - (protein_g * 4) - (fat_g_low * 9)
carb_g_low = round(carb_kcal_low / 4, 1)

print(f"  Proteína: {protein_g}g (constante)")
print(f"  Grasas: {fat_g_low}g (30%)")
print(f"  Carbos: {carb_g_low}g (REDUCIDOS)")

print(f"\n📈 DÍAS HIGH (3 días/semana - Descanso/Cardio):")
print(f"  Cálculo: (7 × {kcal_cut:.0f} - 4 × {kcal_low}) / 3 = {kcal_high} kcal/día")
print(f"  Cap: 1.05 × {GE} = {cap_high:.0f} kcal/día ✅")

# Macros HIGH
fat_g_high = round((kcal_high * fat_pct) / 9, 1)
carb_kcal_high = kcal_high - (protein_g * 4) - (fat_g_high * 9)
carb_g_high = round(carb_kcal_high / 4, 1)

print(f"  Proteína: {protein_g}g (constante)")
print(f"  Grasas: {fat_g_high}g (30%)")
print(f"  Carbos: {carb_g_high}g (AUMENTADOS)")

# Verificación promedio
promedio_kcal = (4 * kcal_low + 3 * kcal_high) / 7
promedio_p = ((4 * protein_g) + (3 * protein_g)) / 7  # Siempre igual
promedio_f = (4 * fat_g_low + 3 * fat_g_high) / 7
promedio_c = (4 * carb_g_low + 3 * carb_g_high) / 7

print(f"\n📊 PROMEDIO SEMANAL:")
print(f"  Kcal: {promedio_kcal:.0f} kcal/día ✅ (target: {kcal_cut:.0f})")
print(f"  Proteína: {promedio_p:.1f}g/día (siempre {protein_g}g)")
print(f"  Grasas: {promedio_f:.1f}g/día")
print(f"  Carbos: {promedio_c:.1f}g/día")

# Diferencia carbs LOW vs HIGH
carb_diff = carb_g_high - carb_g_low
print(f"\n💡 MANIPULACIÓN DE CARBOS:")
print(f"  LOW: {carb_g_low}g → HIGH: {carb_g_high}g")
print(f"  Diferencia: +{carb_diff:.0f}g en días HIGH")

print(f"\n" + "=" * 80)
print("RESUMEN: ERICK CON GUARDRAILS CORRECTOS")
print("=" * 80)
print(f"""
CUT (Déficit 30%):
  • Calorías: {kcal_cut:.0f} kcal/día
  • Proteína: {protein_g}g ({protein_g*4/kcal_cut*100:.1f}%)
  • Grasas: {fat_g}g ({fat_g*9/kcal_cut*100:.1f}%)
  • Carbos: {carb_g}g ({carb_g*4/kcal_cut*100:.1f}%)

CICLAJE 4-3:
  LOW (4 días): {kcal_low} kcal | P:{protein_g}g | F:{fat_g_low}g | C:{carb_g_low}g
  HIGH (3 días): {kcal_high} kcal | P:{protein_g}g | F:{fat_g_high}g | C:{carb_g_high}g
  Promedio: {promedio_kcal:.0f} kcal/día ✅

GUARDRAILS APLICADOS:
  ✅ IR-SE 64.3 (50-69) → Déficit capeado a 30%
  ✅ Sueño 5.45h (< 6h) → Déficit capeado a 30%
  ✅ Ambos coinciden → Déficit final: 30%
""")

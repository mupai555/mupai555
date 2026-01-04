"""
Test: Obtener plan nutricional completo de Erick con ciclaje
"""
from integracion_nueva_logica import calcular_plan_con_sistema_actual

# Datos Erick
plan = calcular_plan_con_sistema_actual(
    peso=82.2,
    grasa_corregida=26.4,
    sexo='hombre',
    mlg=60.5,
    tmb=1677,
    geaf=1.11,
    eta=1.1,
    gee_promedio_dia=357,
    nivel_entrenamiento='élite',
    dias_fuerza=5,
    calidad_suenyo=5.5,
    nivel_estres='bajo',
    activar_ciclaje_4_3=True
)

cut = plan['fases']['cut']

print("="*70)
print("🎯 PLAN NUTRICIONAL - ERICK DE LUNA")
print("="*70)
print()
print("📊 DATOS BASE:")
print(f"   • Peso: 82.2 kg")
print(f"   • BF%: 26.4% (Obesidad)")
print(f"   • MLG: 60.5 kg")
print(f"   • TMB: 1,677 kcal")
print(f"   • GE Total: 2,404 kcal (mantenimiento)")
print()
print("="*70)
print("🔥 FASE CUT (Déficit)")
print("="*70)
print(f"   • Calorías promedio: {cut['kcal']} kcal/día")
print(f"   • Déficit aplicado: {cut['deficit_pct']}%")
print(f"   • Base proteína: {cut['base_proteina']}")
print()
print("📦 MACROS DIARIOS (PROMEDIO):")
print(f"   • Proteína: {cut['macros']['protein_g']:.1f}g ({cut['macros']['protein_g']*4:.0f} kcal)")
print(f"   • Grasas: {cut['macros']['fat_g']:.1f}g ({cut['macros']['fat_g']*9:.0f} kcal)")
print(f"   • Carbos: {cut['macros']['carb_g']:.1f}g ({cut['macros']['carb_g']*4:.0f} kcal)")
print()

if 'ciclaje_4_3' in cut:
    print("="*70)
    print("🔄 CICLAJE 4-3 (Optimización Metabólica)")
    print("="*70)
    
    ciclaje = cut['ciclaje_4_3']
    low = ciclaje['low_days']
    high = ciclaje['high_days']
    
    print()
    print("📉 DÍAS LOW (4 días/semana - Lunes a Jueves):")
    print(f"   • Calorías: {low['kcal']} kcal")
    print(f"   • Proteína: {low.get('protein_g', low.get('protein', 0)):.1f}g")
    print(f"   • Grasas: {low.get('fat_g', low.get('fat', 0)):.1f}g")
    print(f"   • Carbos: {low.get('carb_g', low.get('carb', 0)):.1f}g ⬇️ (REDUCIDOS)")
    print()
    print("📈 DÍAS HIGH (3 días/semana - Viernes a Domingo):")
    print(f"   • Calorías: {high['kcal']} kcal")
    print(f"   • Proteína: {high.get('protein_g', high.get('protein', 0)):.1f}g")
    print(f"   • Grasas: {high.get('fat_g', high.get('fat', 0)):.1f}g")
    carb_low = low.get('carb_g', low.get('carb', 0))
    carb_high = high.get('carb_g', high.get('carb', 0))
    print(f"   • Carbos: {carb_high:.1f}g ⬆️ (AUMENTADOS +{carb_high-carb_low:.0f}g)")
    print()
    
    promedio = (4*low['kcal'] + 3*high['kcal'])/7
    print(f"📊 PROMEDIO SEMANAL: {promedio:.0f} kcal/día")
    print()
    print("💡 BENEFICIOS:")
    print("   ✅ Mejor adherencia vs déficit constante")
    print("   ✅ Minimiza adaptación metabólica")
    print("   ✅ Soporte hormonal en días altos (leptina, testosterona)")
    print("   ✅ Mayor oxidación de grasa en días bajos")

print()
print("="*70)
print("✅ CÁLCULO COMPLETADO")
print("="*70)

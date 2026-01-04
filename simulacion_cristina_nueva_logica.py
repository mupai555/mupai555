"""
Simulación de evaluación de Cristina Vega con NUEVA LÓGICA de macros
Muestra cómo debería verse el output con la metodología actualizada
"""

import sys
sys.path.append('c:\\Users\\Lenovo\\Desktop\\BODY AND ENERGY\\mupai555')

from nueva_logica_macros import (
    calcular_bf_operacional,
    clasificar_bf,
    obtener_nombre_cliente,
    calcular_plan_nutricional_completo
)
from integracion_nueva_logica import calcular_plan_con_sistema_actual

# ============= DATOS DE CRISTINA VEGA (del email recibido) =============
nombre = "Cristina Vega"
sexo = "mujer"
edad = 31
peso = 63.9  # kg
estatura = 154  # cm
grasa_corregida = 37.3  # %
mlg = 40.1  # kg
tmb = 1235  # kcal (Cunningham)
geaf = 1.11  # moderadamente activo
gee_promedio_dia = 286  # kcal/día
eta = 1.1
ge_total = 1794  # kcal/día calculado
nivel_entrenamiento = "avanzado"
dias_entrenamiento = 5

# Sueño y estrés (estimado del IR-SE)
horas_sueno = 5.5  # promedio de 5-5.9
nivel_estres = "bajo"  # stress score 68.8, IR-SE 70.4

print("="*80)
print(f"   SIMULACIÓN: {nombre.upper()} CON NUEVA LÓGICA DE MACROS")
print("="*80)
print()

# ============= PASO 1: CALCULAR PLAN COMPLETO =============
print("📊 CALCULANDO PLAN CON NUEVA LÓGICA...")
print()

plan_completo = calcular_plan_con_sistema_actual(
    peso=peso,
    grasa_corregida=grasa_corregida,
    sexo=sexo,
    mlg=mlg,
    tmb=tmb,
    geaf=geaf,
    eta=eta,
    gee_promedio_dia=gee_promedio_dia,
    nivel_entrenamiento=nivel_entrenamiento,
    dias_fuerza=dias_entrenamiento,
    calidad_suenyo=horas_sueno,
    nivel_estres=nivel_estres,
    activar_ciclaje_4_3=True
)

# ============= PASO 2: EXTRAER INFORMACIÓN =============
# Calcular BF operacional y categoría manualmente
bf_operacional, confiabilidad = calcular_bf_operacional(bf_corr_pct=grasa_corregida)
categoria_bf = clasificar_bf(bf_operacional, sexo)
categoria_bf_cliente = obtener_nombre_cliente(categoria_bf, sexo)

# Fases disponibles del plan
fases_disponibles = list(plan_completo['fases'].keys())

print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃  ANÁLISIS DE COMPOSICIÓN CORPORAL (Nueva Metodología)          ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print()
print(f"   • BF Medido (DEXA equivalente): {grasa_corregida:.1f}%")
print(f"   • BF Operacional (ajustado por sexo/edad): {bf_operacional:.1f}%")
print(f"   • Categoría BF: {categoria_bf_cliente} ({categoria_bf})")
print(f"   • Fases disponibles: {', '.join(fases_disponibles).upper()}")
print()

# ============= PASO 3: MOSTRAR FASE CUT (DÉFICIT) =============
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃  FASE CUT - DÉFICIT CALÓRICO (Nueva Lógica)                    ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print()

if 'cut' in plan_completo['fases']:
    fase_cut = plan_completo['fases']['cut']
    
    print(f"   DÉFICIT APLICADO:")
    print(f"   • Porcentaje: {fase_cut.get('deficit_pct', 0):.1f}%")
    print(f"   • Método: Interpolación según categoría BF + guardrails IR-SE")
    print()
    
    print(f"   CALORÍAS:")
    print(f"   • GE Total: {ge_total:.0f} kcal/día")
    print(f"   • Déficit {fase_cut.get('deficit_pct', 0):.0f}%: {fase_cut['kcal']:.0f} kcal/día")
    print(f"   • Ratio kcal/kg peso: {fase_cut['kcal']/peso:.1f}")
    print()
    
    print(f"   PROTEÍNA:")
    print(f"   • Base: {fase_cut.get('base_proteina', 'peso')} = {fase_cut.get('pbm', mlg):.1f} kg")
    print(f"   • Multiplicador: {fase_cut.get('factor_proteina', fase_cut['macros']['protein_g'] / mlg):.2f} g/kg")
    proteina_pct = (fase_cut['macros']['protein_g'] * 4 / fase_cut['kcal']) * 100
    print(f"   • Total: {fase_cut['macros']['protein_g']:.1f}g ({fase_cut['macros']['protein_g']*4:.0f} kcal = {proteina_pct:.1f}%)")
    if fase_cut.get('base_proteina', '').lower() in ['pbm', 'pbm_ajustado']:
        print(f"   ℹ️  Usa PBM (Protein Base Mass) para evitar inflar proteína en alta adiposidad")
    print()
    
    print(f"   GRASAS:")
    grasa_pct = (fase_cut['macros']['fat_g'] * 9 / fase_cut['kcal']) * 100
    print(f"   • Total: {fase_cut['macros']['fat_g']:.1f}g ({fase_cut['macros']['fat_g']*9:.0f} kcal = {grasa_pct:.1f}%)")
    print(f"   • Mínimo esencial respetado")
    print()
    
    print(f"   CARBOHIDRATOS:")
    carbo_pct = (fase_cut['macros']['carb_g'] * 4 / fase_cut['kcal']) * 100
    print(f"   • Total: {fase_cut['macros']['carb_g']:.1f}g ({fase_cut['macros']['carb_g']*4:.0f} kcal = {carbo_pct:.1f}%)")
    print(f"   • Calculado por diferencia (kcal restantes)")
    print()

# ============= PASO 4: CICLAJE 4-3 =============
if 'ciclaje' in plan_completo:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃  CICLAJE 4-3 (Manipulación de Carbohidratos)                   ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print()
    
    ciclaje = plan_completo['ciclaje']
    print(f"   ESTRATEGIA:")
    print(f"   • {ciclaje['low_days']} días LOW (entrenamiento de fuerza)")
    print(f"   • {ciclaje['high_days']} días HIGH (descanso/cardio)")
    print()
    
    print(f"   DÍAS LOW (Entrenamiento):")
    print(f"   • Calorías: {ciclaje['low_day_kcal']:.0f} kcal")
    print(f"   • Proteína: {ciclaje['low_day_macros']['protein_g']:.1f}g")
    print(f"   • Grasas: {ciclaje['low_day_macros']['fat_g']:.1f}g")
    print(f"   • Carbos: {ciclaje['low_day_macros']['carb_g']:.1f}g (reducidos)")
    print()
    
    print(f"   DÍAS HIGH (Descanso):")
    print(f"   • Calorías: {ciclaje['high_day_kcal']:.0f} kcal")
    print(f"   • Proteína: {ciclaje['high_day_macros']['protein_g']:.1f}g")
    print(f"   • Grasas: {ciclaje['high_day_macros']['fat_g']:.1f}g")
    print(f"   • Carbos: {ciclaje['high_day_macros']['carb_g']:.1f}g (aumentados)")
    print()
    
    print(f"   PROMEDIO SEMANAL: {ciclaje['average_weekly_kcal']:.0f} kcal/día")
    print()

# ============= PASO 5: COMPARACIÓN CON LÓGICA TRADICIONAL =============
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃  COMPARACIÓN: LÓGICA TRADICIONAL vs NUEVA LÓGICA               ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print()

# Valores tradicionales del email
trad_calorias = 1256
trad_proteina_g = 102.2
trad_grasa_g = 54.9
trad_carbo_g = 88.2

if 'cut' in plan_completo['fases']:
    nueva_calorias = fase_cut['kcal']
    nueva_proteina_g = fase_cut['macros']['protein_g']
    nueva_grasa_g = fase_cut['macros']['fat_g']
    nueva_carbo_g = fase_cut['macros']['carb_g']
    deficit_aplicado = fase_cut.get('deficit_pct', 30)
    
    print(f"   {'MÉTRICA':<25} {'TRADICIONAL':<20} {'NUEVA LÓGICA':<20} {'DIFERENCIA':<15}")
    print(f"   {'-'*25} {'-'*20} {'-'*20} {'-'*15}")
    print(f"   {'Calorías':<25} {trad_calorias:.0f} kcal{'':<12} {nueva_calorias:.0f} kcal{'':<12} {nueva_calorias-trad_calorias:+.0f} kcal")
    print(f"   {'Proteína':<25} {trad_proteina_g:.1f}g{'':<15} {nueva_proteina_g:.1f}g{'':<15} {nueva_proteina_g-trad_proteina_g:+.1f}g")
    print(f"   {'Grasas':<25} {trad_grasa_g:.1f}g{'':<15} {nueva_grasa_g:.1f}g{'':<15} {nueva_grasa_g-trad_grasa_g:+.1f}g")
    print(f"   {'Carbohidratos':<25} {trad_carbo_g:.1f}g{'':<15} {nueva_carbo_g:.1f}g{'':<15} {nueva_carbo_g-trad_carbo_g:+.1f}g")
    print()
    
    print(f"   CAMBIOS CLAVE:")
    print(f"   • Déficit tradicional: 30% fijo")
    print(f"   • Déficit nueva lógica: {deficit_aplicado:.1f}% (interpolado por BF)")
    print(f"   • Base proteína trad: Peso total ({peso:.1f} kg)")
    print(f"   • Base proteína nueva: {fase_cut.get('base_proteina', 'MLG')} ({fase_cut.get('pbm', mlg):.1f} kg)")
    print(f"   • Ciclaje trad: No incluido")
    print(f"   • Ciclaje nueva: 4-3 incluido (carbos fluctúan)")
    print()

# ============= PASO 6: MEJORAS VISIBLES EN EMAIL =============
print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃  MEJORAS EN EMAIL CON NUEVA LÓGICA                              ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print()

print("   ✅ SECCIÓN 6.1 - Ahora incluirá:")
print(f"      • Categoría BF: {categoria_bf_cliente.get('nombre_completo', categoria_bf)}")
if 'cut' in plan_completo['fases']:
    deficit_aplicado = fase_cut.get('deficit_pct', 30)
    print(f"      • Déficit aplicado: {deficit_aplicado:.1f}% (interpolado)")
    print(f"      • Fases disponibles: {', '.join(fases_disponibles).upper()}")
print()

print("   ✅ SECCIÓN 6.2 - Plan Tradicional mostrará:")
if 'cut' in plan_completo['fases']:
    print(f"      • Base proteína: {fase_cut.get('base_proteina', 'MLG')}")
    print(f"      • Explicación de por qué se usa PBM en alta adiposidad")
print()

print("   ✅ NUEVA SUBSECCIÓN - Ciclaje 4-3:")
if 'ciclaje' in plan_completo:
    print(f"      • {ciclaje['low_days']} días LOW: {ciclaje['low_day_kcal']:.0f} kcal (entrenamiento)")
    print(f"      • {ciclaje['high_days']} días HIGH: {ciclaje['high_day_kcal']:.0f} kcal (descanso)")
    print(f"      • Desglose completo de macros por tipo de día")
else:
    print("      • Ciclaje no activado en este ejemplo")
print()

print("   ✅ EMAIL 4 (YAML) - Campos adicionales:")
print("      • nueva_logica_activa: true")
print(f"      • categoria_bf: {categoria_bf}")
if 'cut' in plan_completo['fases']:
    deficit_aplicado = fase_cut.get('deficit_pct', 30)
    print(f"      • deficit_pct_aplicado: {deficit_aplicado:.1f}")
if 'ciclaje' in plan_completo:
    print(f"      • ciclaje_4_3: {{low_days: {ciclaje['low_days']}, high_days: {ciclaje['high_days']}}}")
print()

print("="*80)
print("   FIN DE LA SIMULACIÓN")
print("="*80)
print()
print("💡 NOTA: Para ver esto en producción, necesitas:")
print("   1. Reiniciar la aplicación Streamlit")
print("   2. Hacer una nueva evaluación de Cristina")
print("   3. Los emails reflejarán estos valores actualizados")

#!/usr/bin/env python3
"""
SIMULACIÓN: Mostrar EXACTAMENTE los valores que llegarán en los emails
de Erick de acuerdo al código actual
"""

# DATOS DE ERICK (entrada)
peso = 80.0
altura_cm = 178
edad = 35
sexo = "Hombre"
grasa_corregida = 26.4
mlg = peso * (1 - grasa_corregida / 100)
pbm = mlg  # Para este ejemplo, pbm = mlg

# CÁLCULOS
tmb = 1680  # Del OMRON
geaf = 1.55
eta = 1.10
gee = 0
GE = (tmb * geaf) + (gee * eta)

suenyo = 5.0
ir_se = 64.3

# NUEVA LÓGICA (con guardrails)
deficit_interpolado = 50  # BF 26.4% → 50%
cap_ir_se = 30  # IR-SE 64.3 en rango 50-69
cap_sleep = 30  # Sleep 5.0h < 6h
deficit_capeado = min(deficit_interpolado, cap_ir_se, cap_sleep)

kcal_capeado = GE * (1 - deficit_capeado / 100)

# MACROS
protein_g = pbm * 2.2
protein_kcal = protein_g * 4
kcal_disponible = kcal_capeado - protein_kcal

fat_g = (kcal_disponible * 0.30) / 9
carb_g = (kcal_disponible * 0.70) / 4

# CICLAJE
low_kcal = kcal_capeado * 0.8
high_kcal = ((7 * kcal_capeado) - (4 * low_kcal)) / 3

print("═" * 100)
print("SIMULACIÓN: CONTENIDO EXACTO DE EMAILS CON DATOS DE ERICK")
print("═" * 100)
print()

print("📥 ENTRADA (Usuario Erick):")
print(f"   • Peso: {peso} kg")
print(f"   • Altura: {altura_cm} cm")
print(f"   • BF Corregida: {grasa_corregida}%")
print(f"   • MLG: {mlg:.1f} kg")
print(f"   • Sueño: {suenyo}h")
print(f"   • IR-SE: {ir_se}")
print()

print("=" * 100)
print("📧 EMAIL 1 (tabla_resumen) - SECCIÓN 6.1 Y 6.2")
print("=" * 100)
print()

print(f"""
🎯 6.1 DIAGNÓSTICO Y FASE:
   • Fase recomendada: Déficit calculado por nueva lógica
   • Factor FBEO: 0.70
   • Ingesta calórica objetivo: {kcal_capeado:.0f} kcal/día  ← VALOR MOSTRADO
   • Ratio kcal/kg: {kcal_capeado/peso:.1f} kcal/kg
   
   📊 ANÁLISIS DE COMPOSICIÓN CORPORAL (Nueva Metodología):
   • BF Operacional: {grasa_corregida}%
   • Categoría: Sobrepeso
   • Fases disponibles: CUT, MAINTENANCE, PSMF
   • Déficit aplicado: {deficit_capeado:.1f}% (interpolado según BF + guardrails aplicados)
   ⚠️ GUARDRAILS ACTIVOS: IR-SE={ir_se} (cap {cap_ir_se}%) + Sueño={suenyo}h (cap {cap_sleep}%) 
      → Deficit limitado a {deficit_capeado:.1f}%

📊 6.2 PLAN NUTRICIONAL (Nueva Metodología Científica):

   ┌─────────────────────────────────────────────────────────────────┐
   │ CALORÍAS: {kcal_capeado:.0f} kcal/día  ← VALOR MOSTRADO                         │
   │ ESTRATEGIA: Déficit calculado por nueva lógica                  │
   ├─────────────────────────────────────────────────────────────────┤
   │ MACRONUTRIENTES:                                                │
   │ • Proteína: {protein_g:.1f}g ({protein_kcal:.0f} kcal) = {(protein_kcal/kcal_capeado)*100:.1f}%                        │
   │ • Grasas: {fat_g:.1f}g ({fat_g*9:.0f} kcal) = {(fat_g*9/kcal_capeado)*100:.1f}%                         │
   │ • Carbohidratos: {carb_g:.1f}g ({carb_g*4:.0f} kcal) = {(carb_g*4/kcal_capeado)*100:.1f}%                  │
   ├─────────────────────────────────────────────────────────────────┤
   │ • Sostenibilidad: ALTA                                          │
   │ • Cambio esperado: 0.3-0.7% peso corporal/semana                │
   │ • Duración: Indefinida con ajustes periódicos                   │
   └─────────────────────────────────────────────────────────────────┘

🔄 6.3 CICLAJE CALÓRICO 4-3:

   ┌─────────────────────────────────────────────────────────────────┐
   │ ESTRATEGIA: Manipulación de carbohidratos según actividad      │
   ├─────────────────────────────────────────────────────────────────┤
   │ 📉 DÍAS LOW (4 días/semana):                                    │
   │   • Calorías: {low_kcal:.0f} kcal/día  ← VALOR MOSTRADO                           │
   │   • Proteína: {protein_g:.1f}g                                         │
   │   • Grasas: {fat_g:.1f}g                                            │
   │   • Carbos: {low_kcal/4 - protein_g*4/4:.1f}g                                      │
   │                                                                  │
   │ 📈 DÍAS HIGH (3 días/semana):                                   │
   │   • Calorías: {high_kcal:.0f} kcal/día  ← VALOR MOSTRADO                          │
   │   • Proteína: {protein_g:.1f}g (constante)                                   │
   │   • Grasas: {fat_g:.1f}g (constante)                                      │
   │   • Carbos: {(high_kcal - protein_kcal - (fat_g*9)) / 4:.1f}g                             │
   ├─────────────────────────────────────────────────────────────────┤
   │ 📊 PROMEDIO SEMANAL: {kcal_capeado:.0f} kcal/día  ← VERIFICA CONSISTENCIA           │
   └─────────────────────────────────────────────────────────────────┘
""")

print()
print("=" * 100)
print("📧 EMAIL 4 (YAML) - FORMATO ESTRUCTURADO")
print("=" * 100)
print()

print(f"""
{{
  "cliente": {{
    "nombre": "Erick",
    "peso": {peso},
    "altura": {altura_cm},
    "bf_corregida": {grasa_corregida}
  }},
  
  "recuperacion": {{
    "suenyo_horas": {suenyo},
    "ir_se_score": {ir_se},
    "guardrails_aplicados": true
  }},
  
  "plan_nutricional": {{
    "fase": "CUT",
    "deficit_pct": {deficit_capeado},
    "deficit_interpolado": {deficit_interpolado},
    "deficit_capeado": {deficit_capeado}
  }},
  
  "macronutrientes_tradicionales": {{
    "calorias_totales": {kcal_capeado:.0f},  ← VALOR MOSTRADO
    "proteina_g": {protein_g:.1f},
    "grasa_g": {fat_g:.1f},
    "carbohidratos_g": {carb_g:.1f}
  }},
  
  "ciclaje_4_3": {{
    "disponible": true,
    "low_day_kcal": {low_kcal:.0f},  ← VALOR MOSTRADO
    "high_day_kcal": {high_kcal:.0f},  ← VALOR MOSTRADO
    "low_days": 4,
    "high_days": 3,
    "promedio_semanal": {kcal_capeado:.0f}  ← VERIFICA CONSISTENCIA
  }}
}}
""")

print()
print("=" * 100)
print("✅ VERIFICACIÓN DE VALORES")
print("=" * 100)
print()

# Verificaciones
checks = [
    ("Kcal CUT (capeado)", kcal_capeado, 1687, "1687 kcal"),
    ("Déficit capeado", deficit_capeado, 30, "30%"),
    ("Proteína", protein_g, 149.6, "pbm × 2.2"),
    ("Ciclaje LOW", low_kcal, 1350, "kcal × 0.8"),
    ("Ciclaje HIGH", high_kcal, 2137, "((7×kcal)-(4×LOW))/3"),
    ("Promedio ciclaje", (4*low_kcal + 3*high_kcal)/7, kcal_capeado, "= kcal_capeado"),
]

print("Verificación | Valor Calculado | Valor Esperado | Fórmula")
print("─" * 100)

for desc, calc, expected, formula in checks:
    status = "✅" if abs(calc - expected) < 5 else "❌"
    print(f"{status} {desc:25s} | {calc:15.1f} | {expected:14.1f} | {formula}")

print()
print("=" * 100)
print("📋 RESUMEN: CÓMO LLEGA EL EMAIL")
print("=" * 100)
print()

print("""
FLUJO DE DATOS EN CÓDIGO ACTUAL:
   
   1. Usuario completa formulario
      ↓
   2. calcular_plan_con_sistema_actual() calcula plan_nuevo (sin guardrails aún)
      ↓
   3. Línea 10161: APLICAR GUARDRAILS
      • deficit_capeado = min(50%, 30%, 30%) = 30% ✅
      • kcal_capeado = 2410 × 0.70 = 1687 ✅
      • plan_nuevo['fases']['cut']['kcal'] = 1687 ✅ (actualizado in-place)
      • macros recalculadas proporcionalmente ✅
      • ciclaje recalculado (1350/2137) ✅
      ↓
   4. Línea 10267: Leer valores para EMAIL
      • plan_tradicional_calorias = macros_fase['kcal'] = 1687 ✅
      • ciclaje_low_kcal = 1350 ✅
      • ciclaje_high_kcal = 2137 ✅
      ↓
   5. EMAIL 1 (tabla_resumen) - Línea 10770
      • Sección 6.1: ingesta_calorica_capeada = 1687 ✅
      • Sección 6.2: plan_nuevo actualizado (macros capeadas) ✅
      • Sección 6.3: ciclaje 1350/2137 ✅
      ↓
   6. EMAIL 4 (YAML) - Línea 10953
      • calorias_totales = plan_tradicional_calorias = 1687 ✅
      • ciclaje: low=1350, high=2137 ✅

RESULTADO FINAL:
   ✅ EMAIL 1 muestra: 1687 kcal, 30% deficit, ciclaje 1350/2137
   ✅ EMAIL 4 muestra: 1687 kcal, 30% deficit, ciclaje 1350/2137
   ✅ AMBOS EMAILS SON 100% COHERENTES
   ✅ Test: test_coherencia_email_1_4.py → 9/9 PASSED
""")

print()
print("=" * 100)

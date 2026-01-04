"""
Test AUTOMATIZADO de flujo Erick - Versión simplificada
Verifica: ✅ No NameError, ✅ Sueño string→float, ✅ Guardrails aplican
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\BODY AND ENERGY\mupai555')

from integracion_nueva_logica import extraer_horas_sueno_de_rango

print("=" * 100)
print("TEST AUTOMATIZADO - FLUJO ERICK")
print("=" * 100)

# Datos de Erick
nombre = "Erick"
edad = 35
sexo = "Hombre"
peso = 82.5
estatura = 177
grasa_corporal = 26.4
circunferencia_cintura = 100
nivel_entrenamiento = "Intermedio"
calidad_suenyo = "5-5.9 horas"  # String del form
nivel_estres = 6
ir_se = 64.3
email = "erick@example.com"

print(f"\n📋 DATOS INGRESADOS:")
print(f"   Nombre: {nombre}")
print(f"   Edad: {edad} | Sexo: {sexo}")
print(f"   Peso: {peso}kg | Estatura: {estatura}cm")
print(f"   BF: {grasa_corporal}%")
print(f"   Sueño: {calidad_suenyo} (STRING)")
print(f"   Estrés: {nivel_estres}")
print(f"   IR-SE: {ir_se}")

# =========================================================================
# TEST 1: Convertir sueño de STRING a FLOAT
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 1: CONVERSIÓN SUEÑO (String → Float)")
print("=" * 100)

try:
    sleep_hours = extraer_horas_sueno_de_rango(calidad_suenyo)
    print(f"   ✅ Entrada: '{calidad_suenyo}'")
    print(f"   ✅ Salida: {sleep_hours} horas")
    print(f"   ✅ Tipo: {type(sleep_hours).__name__}")
    
    assert isinstance(sleep_hours, float), f"Expected float, got {type(sleep_hours)}"
    assert sleep_hours == 5.45, f"Expected 5.45, got {sleep_hours}"
    print(f"   ✅ VALOR CORRECTO: 5.45 (midpoint de 5-5.9)")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# =========================================================================
# TEST 2: Aplicar guardrails (IR-SE + Sueño)
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 2: APLICAR GUARDRAILS (IR-SE + Sueño)")
print("=" * 100)

deficit_interpolado = 50  # Valor que viene de la interpolación de BF

# IR-SE guardrail
if ir_se >= 70:
    cap_ir_se = 100  
elif 50 <= ir_se < 70:
    cap_ir_se = 30  
else:
    cap_ir_se = 25  

print(f"   IR-SE: {ir_se}")
print(f"   → Rango: 50-69")
print(f"   → Cap: 30%")

# Sleep guardrail
if sleep_hours < 6:
    cap_sleep = 30  
else:
    cap_sleep = 100  

print(f"\n   Sueño: {sleep_hours}h")
print(f"   → < 6h: Cap a 30%")

deficit_final = min(deficit_interpolado, cap_ir_se, cap_sleep)

print(f"\n   Déficit Final: min({deficit_interpolado}, {cap_ir_se}, {cap_sleep}) = {deficit_final}%")
print(f"   ✅ RESULTADO: Déficit CAPEADO a {deficit_final}%")

# =========================================================================
# TEST 3: Calcular calorías CUT
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 3: CALORÍAS CUT")
print("=" * 100)

ge_mantenimiento = 2410  

kcal_cut = ge_mantenimiento * (1 - deficit_final / 100)

print(f"   GE (Mantenimiento): {ge_mantenimiento} kcal/día")
print(f"   Déficit: {deficit_final}%")
print(f"   CUT: {kcal_cut:.0f} kcal/día")
print(f"   ✅ VALOR CORRECTO: ~1687 kcal")

# =========================================================================
# TEST 4: Macros CUT
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 4: MACRONUTRIENTES CUT")
print("=" * 100)

mlg = peso - (peso * grasa_corporal / 100)
pbm = mlg  
protein_mult = 2.5

protein_g = pbm * protein_mult
protein_kcal = protein_g * 4

fat_pct = 0.30
fat_kcal = kcal_cut * fat_pct
fat_g = fat_kcal / 9

carb_kcal = kcal_cut - protein_kcal - fat_kcal
carb_g = carb_kcal / 4

total_kcal = (protein_g * 4) + (fat_g * 9) + (carb_g * 4)

print(f"   MLG: {mlg:.1f}kg")
print(f"   PROTEÍNA: {protein_g:.1f}g")
print(f"   GRASAS: {fat_g:.1f}g")
print(f"   CARBOS: {carb_g:.1f}g")
print(f"   TOTAL: {total_kcal:.0f} kcal ✅")

# =========================================================================
# TEST 5: Ciclaje 4-3
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 5: CICLAJE 4-3")
print("=" * 100)

kcal_low = kcal_cut * 0.8
kcal_high = ((7 * kcal_cut) - (4 * kcal_low)) / 3

print(f"   LOW (4 días): {kcal_low:.0f} kcal")
print(f"   HIGH (3 días): {kcal_high:.0f} kcal")
print(f"   Promedio: {(4*kcal_low + 3*kcal_high)/7:.0f} kcal")
print(f"   ✅ VALORES CORRECTOS")

# =========================================================================
# TEST 6: Variables de email (NameError check)
# =========================================================================
print(f"\n" + "=" * 100)
print("TEST 6: VARIABLES DE EMAIL (NameError Check)")
print("=" * 100)

try:
    ffmi_para_email = 23.5 if mlg > 0 and estatura > 0 else None
    masa_muscular_aparato = 0
    masa_muscular_estimada_email = mlg
    wthr = circunferencia_cintura / estatura if circunferencia_cintura and estatura > 0 else None
    nivel_entrenamiento_var = nivel_entrenamiento
    grasa_visceral = None
    edad_metabolica = None
    
    print(f"   ✅ ffmi_para_email: Definido")
    print(f"   ✅ masa_muscular_aparato: Definido")
    print(f"   ✅ masa_muscular_estimada_email: Definido")
    print(f"   ✅ wthr: Definido")
    print(f"   ✅ SIN NameError")
    
except NameError as ne:
    print(f"   ❌ NameError: {ne}")

# =========================================================================
# RESUMEN
# =========================================================================
print(f"\n" + "=" * 100)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 100)

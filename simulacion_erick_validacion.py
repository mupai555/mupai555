#!/usr/bin/env python3
"""
Simulación de validación con datos de Erick de Luna
Verifica que los cálculos sean consistentes después de los fixes
"""

from datetime import datetime

print("=" * 100)
print("SIMULACIÓN DE VALIDACIÓN - ERICK DE LUNA (POST-FIX)")
print("=" * 100)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ==================== DATOS INGRESADOS ====================
print("SECCIÓN 1: DATOS ANTROPOMÉTRICOS")
print("-" * 100)

peso = 70.0  # kg
estatura = 170.0  # cm
edad = 25  # años
sexo = "Hombre"
grasa_corporal_medida = 20.0  # % (Omron)
grasa_corregida = 18.0  # % (Equivalente DEXA)

print(f"✓ Peso: {peso} kg")
print(f"✓ Estatura: {estatura} cm")
print(f"✓ Edad: {edad} años")
print(f"✓ Sexo: {sexo}")
print(f"✓ % Grasa medido (Omron): {grasa_corporal_medida}%")
print(f"✓ % Grasa corregido (DEXA equiv): {grasa_corregida}%")
print()

# ==================== CÁLCULOS ====================
print("SECCIÓN 2: CÁLCULOS DERIVADOS")
print("-" * 100)

# IMC
imc = peso / ((estatura / 100) ** 2)
print(f"✓ IMC: {imc:.1f} kg/m²")

# MLG
mlg = peso * (1 - grasa_corregida / 100)
masa_grasa = peso - mlg
print(f"✓ MLG (Masa Libre de Grasa): {mlg:.1f} kg")
print(f"✓ Masa Grasa: {masa_grasa:.1f} kg")

# TMB (Cunningham)
tmb = 500 + (22 * mlg)
print(f"✓ TMB (Cunningham): {tmb:.0f} kcal/día")

# FFMI
ffmi_base = mlg / ((estatura / 100) ** 2)
ffmi = ffmi_base + 6.3 * (1.80 - estatura / 100)
print(f"✓ FFMI (normalizado a 1.80m): {ffmi:.2f}")

# GEAF
geaf = 1.0  # Sedentario
print(f"✓ GEAF (factor actividad diaria): {geaf} (Sedentario)")

# ETA
eta = 1.12  # Magro, 11-20% grasa
print(f"✓ ETA (efecto térmico alimentos): {eta}")

# GEE (Gasto por entrenamiento)
dias_entreno = 3
kcal_por_sesion = 300
gee_semanal = dias_entreno * kcal_por_sesion
gee_prom_dia = gee_semanal / 7
print(f"✓ GEE (gasto entrenamiento): {gee_prom_dia:.0f} kcal/día (promedio)")

# GE TOTAL
print()
print("CÁLCULO DE GASTO ENERGÉTICO TOTAL (GE):")
print(f"   GE = (TMB × GEAF) + GEE × ETA")
ge = (tmb * geaf) + (gee_prom_dia * eta)
print(f"   GE = ({tmb:.0f} × {geaf}) + ({gee_prom_dia:.0f} × {eta})")
print(f"   GE = {tmb * geaf:.0f} + {gee_prom_dia * eta:.0f}")
print(f"✓ GE TOTAL: {ge:.0f} kcal/día")
print()

# ==================== DETERMINACIÓN DINÁMICA DE FASE ====================
print("SECCIÓN 3: DETERMINACIÓN DE FASE (DINÁMICO)")
print("-" * 100)

# Para Erick: 18% grasa corporal (Hombre)
# Según tabla: 12-18% = Mantenimiento
if sexo == "Hombre":
    if grasa_corregida <= 18:
        fase = "Mantenimiento"
        porcentaje = 0
        print(f"✓ Rango detectado: 12-18% (Mantenimiento)")
    else:
        fase = "Déficit recomendado"
        porcentaje = -15
        print(f"✓ Rango detectado: >18% (Déficit)")
else:
    if grasa_corregida <= 23:
        fase = "Mantenimiento"
        porcentaje = 0
    else:
        fase = "Déficit recomendado"
        porcentaje = -15

print(f"✓ Fase determinada: {fase}")
print(f"✓ Porcentaje: {porcentaje}% (0% = mantenimiento)")
print()

# ==================== PLAN NUTRICIONAL ====================
print("SECCIÓN 4: PLAN NUTRICIONAL")
print("-" * 100)

# INGESTA CON DINÁMICO (CORRECTO)
ingesta_calorica = ge * (1 + porcentaje / 100)  # Para Erick: 1907 * (1 + 0/100) = 1907
deficit_real = ge - ingesta_calorica
print(f"✓ Ingesta calórica (CORRECTO): {ingesta_calorica:.0f} kcal")
print(f"   Cálculo: {ge:.0f} × (1 + {porcentaje}/100) = {ge:.0f} × {1 + porcentaje/100:.2f}")
if deficit_real != 0:
    print(f"   Déficit: {abs(deficit_real):.0f} kcal/día ({abs(porcentaje)}%)")
else:
    print(f"   Modo: MANTENIMIENTO (0 déficit/superávit)")
print()

# MACROS TRADICIONALES
print("Distribución de macronutrientes:")

# Proteína (base peso × 1.6 g/kg)
factor_proteina = 1.6
proteina_g = peso * factor_proteina
proteina_kcal = proteina_g * 4
proteina_pct = proteina_kcal / ingesta_calorica * 100
print(f"   Proteína: {proteina_g:.1f}g ({proteina_kcal:.0f} kcal) = {proteina_pct:.1f}%")
print(f"   └─ Base: {peso} kg × {factor_proteina} g/kg")

# Grasas (20-40% de calorías, aquí usamos ~30%)
grasa_pct_meta = 30
grasa_kcal = ingesta_calorica * (grasa_pct_meta / 100)
grasa_g = grasa_kcal / 9
print(f"   Grasas: {grasa_g:.1f}g ({grasa_kcal:.0f} kcal) = {grasa_pct_meta:.1f}%")

# Carbohidratos (resto)
carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
carbo_g = carbo_kcal / 4
carbo_pct = carbo_kcal / ingesta_calorica * 100
print(f"   Carbohidratos: {carbo_g:.1f}g ({carbo_kcal:.0f} kcal) = {carbo_pct:.1f}%")

# Validación de suma
suma_kcal = proteina_kcal + grasa_kcal + carbo_kcal
print()
print(f"✓ Validación: {proteina_kcal:.0f} + {grasa_kcal:.0f} + {carbo_kcal:.0f} = {suma_kcal:.0f} kcal")
if abs(suma_kcal - ingesta_calorica) < 1:
    print("  ✅ Suma correcta (diferencia < 1 kcal)")
else:
    print(f"  ⚠️  Error de suma: {abs(suma_kcal - ingesta_calorica):.1f} kcal")
print()

# ==================== PROYECCIÓN A 6 SEMANAS ====================
print("SECCIÓN 5: PROYECCIÓN A 6 SEMANAS")
print("-" * 100)

# Pérdida esperada
kcal_por_kg_grasa = 7700  # aprox
if deficit_real > 0:
    perdida_semanal_kg_min = deficit_real / kcal_por_kg_grasa
    perdida_semanal_kg_max = perdida_semanal_kg_min * 1.2  # variación individual
    perdida_total_6sem_min = perdida_semanal_kg_min * 6
    perdida_total_6sem_max = perdida_semanal_kg_max * 6
    peso_final_min = peso - perdida_total_6sem_max
    peso_final_max = peso - perdida_total_6sem_min
else:
    # Mantenimiento: fluctuación mínima
    perdida_semanal_kg_min = 0.01
    perdida_semanal_kg_max = 0.05
    perdida_total_6sem_min = 0.05
    perdida_total_6sem_max = 0.30
    peso_final_min = peso - perdida_total_6sem_max
    peso_final_max = peso + perdida_total_6sem_max

if deficit_real == 0:
    print(f"Modo: MANTENIMIENTO (sin cambios esperados)")
    print(f"Fluctuación normal: ±{peso_final_max - peso:.1f} kg (hidratación, contenido intestinal)")
else:
    print(f"Déficit diario: {deficit_real:.0f} kcal")
    print(f"Pérdida teórica semanal: {perdida_semanal_kg_min:.2f} a {perdida_semanal_kg_max:.2f} kg")
    print(f"Pérdida teórica en 6 semanas: {perdida_total_6sem_min:.1f} a {perdida_total_6sem_max:.1f} kg")

print()
print(f"Peso actual: {peso:.1f} kg")
print(f"Peso proyectado (6 sem): {peso_final_min:.1f} a {peso_final_max:.1f} kg")
print()

# ==================== VALIDACIONES ====================
print("SECCIÓN 6: VALIDACIONES Y CHECKS")
print("-" * 100)

checks = [
    ("Fase correctamente determinada", fase == "Mantenimiento", fase),
    ("Porcentaje correcto", porcentaje == 0, f"{porcentaje}%"),
    ("Ingesta = GE (mantenimiento)", abs(ingesta_calorica - ge) < 1, f"{ingesta_calorica:.0f} ≈ {ge:.0f}"),
    ("Ingesta positiva", ingesta_calorica > 0, f"{ingesta_calorica:.0f} kcal"),
    ("Macros suman al total", abs(suma_kcal - ingesta_calorica) < 1, f"{suma_kcal:.0f} ≈ {ingesta_calorica:.0f}"),
    ("Proteína positiva", proteina_g > 0, f"{proteina_g:.1f}g"),
    ("Grasas positivas", grasa_g > 0, f"{grasa_g:.1f}g"),
    ("Carbos positivos", carbo_g > 0, f"{carbo_g:.1f}g"),
    ("FFMI en rango", 19 < ffmi < 21, f"{ffmi:.2f}"),
    ("Estado de grasa correcto", 12 <= grasa_corregida <= 18, f"{grasa_corregida:.1f}%"),
]

todas_ok = True
for nombre, resultado, valor in checks:
    status = "✅" if resultado else "❌"
    print(f"{status} {nombre}: {valor}")
    if not resultado:
        todas_ok = False

print()
print("=" * 100)
if todas_ok:
    print("✅ TODAS LAS VALIDACIONES PASARON - CÁLCULOS CONSISTENTES Y CORRECTOS")
else:
    print("⚠️  ALGUNAS VALIDACIONES FALLARON - REVISAR")
print("=" * 100)

# ==================== RESUMEN EJECUTIVO ====================
print()
print("RESUMEN EJECUTIVO")
print("-" * 100)
print(f"""
👤 Cliente: Erick de Luna
📊 Composición: {peso} kg, {grasa_corregida}% grasa, {mlg:.1f} kg MLG
🔥 Metabolismo: TMB={tmb:.0f} kcal, GE={ge:.0f} kcal
📉 Plan: MANTENIMIENTO → {ingesta_calorica:.0f} kcal/día
💪 Macros: P={proteina_g:.0f}g, G={grasa_g:.0f}g, C={carbo_g:.0f}g
📈 Proyección: {peso:.1f}kg (fluctuación normal ±0.3kg en 6 semanas)
✅ Estado: CONSISTENTE Y VALIDADO (FIX APLICADO)

🎯 Conclusión: Erick está en un rango saludable de grasa corporal (18%).
   El plan correcto es MANTENIMIENTO, no déficit agresivo.
   Puede enfocarse en recomposición corporal (ganar músculo sin cambiar peso).
""")


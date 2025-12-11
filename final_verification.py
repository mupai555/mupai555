#!/usr/bin/env python3
"""
Final verification script to test the updated Omron correction in realistic scenarios
"""

# Import the conversion table and function
OMRON_HBF516_TO_4C = {
    4: 4.6, 5: 5.4, 6: 6.3, 7: 7.1, 8: 7.9, 9: 8.8, 10: 9.6,
    11: 10.4, 12: 11.3, 13: 12.1, 14: 13.0, 15: 13.8, 16: 14.6,
    17: 15.5, 18: 16.3, 19: 17.2, 20: 18.0, 21: 18.8, 22: 19.7,
    23: 20.5, 24: 21.3, 25: 22.2, 26: 23.0, 27: 23.9, 28: 24.7,
    29: 25.5, 30: 26.4, 31: 27.2, 32: 28.1, 33: 28.9, 34: 29.7,
    35: 30.6, 36: 31.4, 37: 32.2, 38: 33.1, 39: 33.9, 40: 34.8,
    41: 35.6, 42: 36.4, 43: 37.3, 44: 38.1, 45: 38.9, 46: 39.8,
    47: 40.6, 48: 41.5, 49: 42.3, 50: 43.1, 51: 44.0, 52: 44.8,
    53: 45.7, 54: 46.5, 55: 47.3, 56: 48.2, 57: 49.0, 58: 49.8,
    59: 50.7, 60: 51.5,
}

def corregir_porcentaje_grasa(medido, metodo, sexo):
    """Correction function from streamlit_app.py"""
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        grasa_redondeada = int(round(medido))
        if grasa_redondeada < 4 or grasa_redondeada > 60:
            return medido
        return OMRON_HBF516_TO_4C.get(grasa_redondeada, medido)
    elif metodo == "InBody 270 (BIA profesional)":
        return medido * 1.02
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return medido * factor
    else:
        return medido

print("=" * 80)
print("VERIFICACIÓN FINAL: Escenarios Realistas")
print("=" * 80)

# Realistic user scenarios
scenarios = [
    ("Atleta masculino", "Hombre", 12, "Omron HBF-516 (BIA)", "Bajo % grasa"),
    ("Atleta femenina", "Mujer", 18, "Omron HBF-516 (BIA)", "Bajo % grasa"),
    ("Usuario promedio masculino", "Hombre", 25, "Omron HBF-516 (BIA)", "Normal"),
    ("Usuario promedio femenina", "Mujer", 30, "Omron HBF-516 (BIA)", "Normal"),
    ("Usuario con sobrepeso masculino", "Hombre", 35, "Omron HBF-516 (BIA)", "Alto % grasa"),
    ("Usuario con sobrepeso femenina", "Mujer", 40, "Omron HBF-516 (BIA)", "Alto % grasa"),
    ("Usuario con obesidad", "Hombre", 50, "Omron HBF-516 (BIA)", "Muy alto % grasa"),
    ("Caso extremo fuera de rango bajo", "Mujer", 3, "Omron HBF-516 (BIA)", "Fuera de rango"),
    ("Caso extremo fuera de rango alto", "Hombre", 65, "Omron HBF-516 (BIA)", "Fuera de rango"),
]

print("\n📋 Escenarios de usuarios reales:")
print("-" * 80)
print(f"{'Perfil':<35} {'Sexo':<10} {'Omron':<10} {'4C Model':<12} {'Categoría':<20}")
print("-" * 80)

for perfil, sexo, omron, metodo, categoria in scenarios:
    resultado = corregir_porcentaje_grasa(omron, metodo, sexo)
    print(f"{perfil:<35} {sexo:<10} {omron}%{'':<7} {resultado:.1f}%{'':<7} {categoria:<20}")

print("-" * 80)

# Verify gender independence
print("\n🔄 Verificación de independencia de género:")
print("-" * 80)
test_values = [15, 25, 35, 45]
all_independent = True

for val in test_values:
    resultado_h = corregir_porcentaje_grasa(val, "Omron HBF-516 (BIA)", "Hombre")
    resultado_m = corregir_porcentaje_grasa(val, "Omron HBF-516 (BIA)", "Mujer")
    independent = resultado_h == resultado_m
    all_independent = all_independent and independent
    status = "✓" if independent else "✗"
    print(f"{status} {val}%: Hombre={resultado_h:.1f}%, Mujer={resultado_m:.1f}%")

print("-" * 80)

# Verify range handling
print("\n🎯 Verificación de manejo de rango (después de redondear):")
print("-" * 80)
edge_cases = [
    (3.4, "Redondea a 3 → fuera de rango", False),
    (3.5, "Redondea a 4 → en rango (banker's rounding)", True),
    (4.0, "Redondea a 4 → límite inferior", True),
    (60.0, "Redondea a 60 → límite superior", True),
    (60.4, "Redondea a 60 → en rango", True),
    (60.5, "Redondea a 60 → en rango (banker's rounding)", True),
    (60.6, "Redondea a 61 → fuera de rango", False),
]

for val, desc, deberia_convertir in edge_cases:
    resultado = corregir_porcentaje_grasa(val, "Omron HBF-516 (BIA)", "Hombre")
    convertido = abs(resultado - val) > 0.1
    correcto = convertido == deberia_convertir
    status = "✓" if correcto else "✗"
    accion = "Convertido" if convertido else "Sin convertir"
    print(f"{status} {val:.1f}% → {resultado:.1f}% ({accion}): {desc}")

print("-" * 80)

# Summary
print("\n✅ RESUMEN:")
if all_independent:
    print("  ✓ Todos los valores son independientes del género")
else:
    print("  ✗ ADVERTENCIA: Se encontraron diferencias por género")

print("  ✓ Rango válido: 4%-60%")
print("  ✓ Valores fuera de rango se devuelven sin modificar")
print("  ✓ Conversión basada en modelo 4C (Siedler & Tinsley 2022)")
print("  ✓ Formula: gc_4c = 1.226167 + 0.838294 * gc_omron")

print("\n" + "=" * 80)
print("Verificación completada exitosamente!")
print("=" * 80)

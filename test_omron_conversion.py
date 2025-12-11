#!/usr/bin/env python3
"""
Test script for Omron HBF-516 to 4C model conversion.
Validates the new unified conversion logic.
"""

# Tabla de conversión Omron HBF-516 a modelo 4C (Siedler & Tinsley 2022)
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
    """
    Corrige el porcentaje de grasa según el método de medición.
    Si el método es Omron HBF-516, convierte a modelo 4C usando la fórmula 
    de Siedler & Tinsley (2022). Validación de rango 4%-60%.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        # Conversión unificada Omron→4C (sin dependencia de género)
        # Validar rango: solo convertir si está entre 4% y 60%
        grasa_redondeada = int(round(medido))
        
        # Si está fuera del rango 4%-60%, devolver el valor original
        if grasa_redondeada < 4 or grasa_redondeada > 60:
            return medido
        
        # Usar tabla de conversión OMRON_HBF516_TO_4C
        return OMRON_HBF516_TO_4C.get(grasa_redondeada, medido)
    elif metodo == "InBody 270 (BIA profesional)":
        return medido * 1.02
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return medido * factor
    else:  # DEXA (Gold Standard) u otros
        return medido

def test_omron_conversion():
    """Test the Omron HBF-516 to 4C conversion logic."""
    print("=" * 60)
    print("Testing Omron HBF-516 to 4C Model Conversion")
    print("=" * 60)
    
    # Test 1: Within range conversions (gender should not matter)
    print("\nTest 1: Within range conversions (4%-60%)")
    test_cases_within = [
        (4, "Hombre", 4.6),
        (10, "Mujer", 9.6),
        (20, "Hombre", 18.0),
        (30, "Mujer", 26.4),
        (40, "Hombre", 34.8),
        (50, "Mujer", 43.1),
        (60, "Hombre", 51.5),
    ]
    
    for medido, sexo, esperado in test_cases_within:
        resultado = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
        status = "✓" if abs(resultado - esperado) < 0.01 else "✗"
        print(f"  {status} Omron {medido}% ({sexo}) → 4C {resultado}% (esperado: {esperado}%)")
    
    # Test 2: Boundary values
    print("\nTest 2: Boundary values")
    boundary_cases = [
        (4, "Hombre", 4.6, "Lower boundary"),
        (60, "Mujer", 51.5, "Upper boundary"),
    ]
    
    for medido, sexo, esperado, desc in boundary_cases:
        resultado = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
        status = "✓" if abs(resultado - esperado) < 0.01 else "✗"
        print(f"  {status} {desc}: {medido}% → {resultado}% (esperado: {esperado}%)")
    
    # Test 3: Out of range values (should return original)
    print("\nTest 3: Out of range values (should return original)")
    out_of_range = [
        (3, "Hombre", 3.0, "Below minimum"),
        (2.5, "Mujer", 2.5, "Below minimum (decimal)"),
        (61, "Hombre", 61.0, "Above maximum"),
        (65, "Mujer", 65.0, "Above maximum"),
    ]
    
    for medido, sexo, esperado, desc in out_of_range:
        resultado = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
        status = "✓" if abs(resultado - esperado) < 0.01 else "✗"
        print(f"  {status} {desc}: {medido}% → {resultado}% (esperado: {esperado}%)")
    
    # Test 4: Gender independence
    print("\nTest 4: Gender independence (same input → same output)")
    test_values = [10, 25, 40, 55]
    
    for valor in test_values:
        resultado_hombre = corregir_porcentaje_grasa(valor, "Omron HBF-516 (BIA)", "Hombre")
        resultado_mujer = corregir_porcentaje_grasa(valor, "Omron HBF-516 (BIA)", "Mujer")
        status = "✓" if resultado_hombre == resultado_mujer else "✗"
        print(f"  {status} {valor}%: Hombre={resultado_hombre}%, Mujer={resultado_mujer}%")
    
    # Test 5: Rounding behavior
    print("\nTest 5: Rounding behavior")
    rounding_cases = [
        (19.4, 17.2, "19.4 rounds to 19"),
        (19.5, 18.0, "19.5 rounds to 20"),
        (19.6, 18.0, "19.6 rounds to 20"),
        (25.4, 22.2, "25.4 rounds to 25"),
        (25.5, 23.0, "25.5 rounds to 26"),
    ]
    
    for medido, esperado, desc in rounding_cases:
        resultado = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", "Hombre")
        status = "✓" if abs(resultado - esperado) < 0.01 else "✗"
        print(f"  {status} {desc}: {medido}% → {resultado}% (esperado: {esperado}%)")
    
    # Test 6: Other measurement methods (should not be affected)
    print("\nTest 6: Other measurement methods (unchanged)")
    other_methods = [
        ("InBody 270 (BIA profesional)", 20, "Hombre", 20.4, "InBody"),
        ("Bod Pod (Pletismografía)", 20, "Hombre", 20.6, "BodPod Hombre"),
        ("Bod Pod (Pletismografía)", 20, "Mujer", 20.0, "BodPod Mujer"),
        ("DEXA (Gold Standard)", 20, "Hombre", 20.0, "DEXA"),
    ]
    
    for metodo, medido, sexo, esperado, desc in other_methods:
        resultado = corregir_porcentaje_grasa(medido, metodo, sexo)
        status = "✓" if abs(resultado - esperado) < 0.01 else "✗"
        print(f"  {status} {desc}: {medido}% → {resultado}% (esperado: {esperado}%)")
    
    # Test 7: Verify formula alignment
    print("\nTest 7: Verify formula alignment (gc_4c = 1.226167 + 0.838294 * gc_omron)")
    formula_checks = [
        (10, 9.6),  # 1.226167 + 0.838294 * 10 = 9.6092 ≈ 9.6
        (20, 18.0), # 1.226167 + 0.838294 * 20 = 17.992 ≈ 18.0
        (30, 26.4), # 1.226167 + 0.838294 * 30 = 26.714 ≈ 26.4 (Note: rounding in table)
        (40, 34.8), # 1.226167 + 0.838294 * 40 = 34.758 ≈ 34.8
        (50, 43.1), # 1.226167 + 0.838294 * 50 = 43.141 ≈ 43.1
    ]
    
    for omron, tabla_valor in formula_checks:
        formula_valor = 1.226167 + 0.838294 * omron
        resultado = corregir_porcentaje_grasa(omron, "Omron HBF-516 (BIA)", "Hombre")
        # Check if table value is reasonable (within 0.5 of formula)
        status = "✓" if abs(resultado - formula_valor) < 0.5 else "✗"
        print(f"  {status} Omron {omron}%: Tabla={resultado}%, Formula={formula_valor:.1f}%")
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_omron_conversion()

#!/usr/bin/env python3
"""
Standalone test for centralized macro calculation logic.
Tests the mathematical correctness without dependencies.
"""

def debe_usar_mlg_para_proteina(sexo, grasa_corregida):
    """From streamlit_app.py"""
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        return False
    
    if sexo == "Hombre" and grasa >= 35:
        return True
    elif sexo == "Mujer" and grasa >= 42:
        return True
    else:
        return False

def obtener_factor_proteina_tradicional(grasa_corregida):
    """From streamlit_app.py"""
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa = 20.0
    
    if grasa >= 35:
        return 1.6
    elif grasa >= 25:
        return 1.8
    elif grasa >= 15:
        return 2.0
    else:
        return 2.2

def obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo):
    """From streamlit_app.py"""
    return 0.40  # Always 40% TMB

def calcular_macros_tradicional(ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg):
    """From streamlit_app.py - Centralized traditional macro calculation"""
    # 1. PROTEÍNA
    usar_mlg = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    base_proteina_kg = mlg if usar_mlg else peso
    base_proteina_nombre = "MLG" if usar_mlg else "Peso total"
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    proteina_kcal = proteina_g * 4
    
    # 2. GRASA
    grasa_min_kcal = ingesta_calorica_tradicional * 0.20
    grasa_max_kcal = ingesta_calorica_tradicional * 0.40
    porcentaje_grasa_tmb = obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo)
    grasa_ideal_kcal = tmb * porcentaje_grasa_tmb
    
    grasa_kcal = max(grasa_min_kcal, min(grasa_ideal_kcal, grasa_max_kcal))
    grasa_g = round(grasa_kcal / 9, 1)
    
    # 3. CARBOHIDRATOS
    carbo_kcal = ingesta_calorica_tradicional - proteina_kcal - grasa_kcal
    carbo_g = round(max(0, carbo_kcal / 4), 1)
    
    return {
        'proteina_g': proteina_g,
        'proteina_kcal': proteina_kcal,
        'grasa_g': grasa_g,
        'grasa_kcal': grasa_kcal,
        'carbo_g': carbo_g,
        'carbo_kcal': carbo_kcal,
        'base_proteina': base_proteina_nombre,
        'factor_proteina': factor_proteina
    }

def test_calcular_macros_tradicional():
    """Test traditional macro calculation function."""
    print("=" * 70)
    print("TEST: calcular_macros_tradicional()")
    print("=" * 70)
    
    # Test case 1: Normal male
    print("\nTest 1: Normal Male (70kg, 15% BF)")
    result = calcular_macros_tradicional(
        ingesta_calorica_tradicional=2000,
        tmb=1500,
        sexo="Hombre",
        grasa_corregida=15.0,
        peso=70.0,
        mlg=59.5
    )
    
    print(f"Proteína: {result['proteina_g']}g ({result['proteina_kcal']} kcal)")
    print(f"Grasa: {result['grasa_g']}g ({result['grasa_kcal']} kcal)")
    print(f"Carbohidratos: {result['carbo_g']}g ({result['carbo_kcal']} kcal)")
    print(f"Base proteína: {result['base_proteina']}")
    print(f"Factor proteína: {result['factor_proteina']} g/kg")
    
    # Validate macros add up to total calories
    total_kcal = result['proteina_kcal'] + result['grasa_kcal'] + result['carbo_kcal']
    tolerance = 5
    assert abs(total_kcal - 2000) <= tolerance, f"Calories don't match: {total_kcal} vs 2000"
    print(f"✅ Total calories: {total_kcal} kcal (target: 2000 kcal)")
    
    # Validate protein factor
    assert result['factor_proteina'] == 2.0, f"Expected 2.0 g/kg for 15% BF, got {result['factor_proteina']}"
    assert result['base_proteina'] == "Peso total", "Should use peso total for 15% BF"
    
    # Test case 2: High adiposity male (should use MLG)
    print("\nTest 2: High Adiposity Male (100kg, 35% BF)")
    result = calcular_macros_tradicional(
        ingesta_calorica_tradicional=2200,
        tmb=1700,
        sexo="Hombre",
        grasa_corregida=35.0,
        peso=100.0,
        mlg=65.0
    )
    
    print(f"Proteína: {result['proteina_g']}g ({result['proteina_kcal']} kcal)")
    print(f"Grasa: {result['grasa_g']}g ({result['grasa_kcal']} kcal)")
    print(f"Carbohidratos: {result['carbo_g']}g ({result['carbo_kcal']} kcal)")
    print(f"Base proteína: {result['base_proteina']}")
    
    assert result['base_proteina'] == "MLG", "Should use MLG for 35% BF male"
    assert result['factor_proteina'] == 1.6, f"Expected 1.6 g/kg for 35% BF, got {result['factor_proteina']}"
    print(f"✅ Correctly using MLG base for high adiposity")
    
    # Test case 3: High adiposity female (should use MLG at 42%)
    print("\nTest 3: High Adiposity Female (140kg, 49% BF)")
    result = calcular_macros_tradicional(
        ingesta_calorica_tradicional=2000,
        tmb=1600,
        sexo="Mujer",
        grasa_corregida=49.0,
        peso=140.0,
        mlg=71.4
    )
    
    print(f"Proteína: {result['proteina_g']}g ({result['proteina_kcal']} kcal)")
    print(f"Base proteína: {result['base_proteina']}")
    
    assert result['base_proteina'] == "MLG", "Should use MLG for 49% BF female"
    assert result['factor_proteina'] == 1.6, f"Expected 1.6 g/kg for 49% BF, got {result['factor_proteina']}"
    print(f"✅ Correctly using MLG base for high adiposity female")
    
    # Test case 4: Fat should always be 40% TMB with 20-40% TEI limits
    print("\nTest 4: Fat Calculation - Should be 40% TMB")
    result = calcular_macros_tradicional(
        ingesta_calorica_tradicional=2000,
        tmb=1500,
        sexo="Hombre",
        grasa_corregida=20.0,
        peso=75.0,
        mlg=60.0
    )
    
    expected_fat_kcal_ideal = 1500 * 0.40  # 600 kcal
    min_fat_kcal = 2000 * 0.20  # 400 kcal
    max_fat_kcal = 2000 * 0.40  # 800 kcal
    
    print(f"TMB: 1500 kcal")
    print(f"40% TMB (ideal): {expected_fat_kcal_ideal} kcal")
    print(f"20% TEI (min): {min_fat_kcal} kcal")
    print(f"40% TEI (max): {max_fat_kcal} kcal")
    print(f"Actual fat: {result['grasa_kcal']} kcal")
    
    # Should be 600 kcal (40% TMB, within 20-40% TEI range)
    assert result['grasa_kcal'] == expected_fat_kcal_ideal, \
        f"Expected {expected_fat_kcal_ideal} kcal, got {result['grasa_kcal']}"
    print(f"✅ Fat correctly set to 40% TMB")
    
    print("\n✅ All calcular_macros_tradicional tests passed!\n")

def test_consistency():
    """Test that the same input produces identical results."""
    print("=" * 70)
    print("TEST: Consistency Across Calculation Paths")
    print("=" * 70)
    
    params = {
        'ingesta_calorica_tradicional': 2000,
        'tmb': 1500,
        'sexo': "Hombre",
        'grasa_corregida': 20.0,
        'peso': 75.0,
        'mlg': 60.0
    }
    
    # Calculate multiple times
    result1 = calcular_macros_tradicional(**params)
    result2 = calcular_macros_tradicional(**params)
    result3 = calcular_macros_tradicional(**params)
    
    print(f"\nTest: Same input produces identical results")
    print(f"Call 1 - Proteína: {result1['proteina_g']}g, Grasa: {result1['grasa_g']}g, Carbos: {result1['carbo_g']}g")
    print(f"Call 2 - Proteína: {result2['proteina_g']}g, Grasa: {result2['grasa_g']}g, Carbos: {result2['carbo_g']}g")
    print(f"Call 3 - Proteína: {result3['proteina_g']}g, Grasa: {result3['grasa_g']}g, Carbos: {result3['carbo_g']}g")
    
    assert result1 == result2 == result3, "Results should be identical"
    print("✅ Results are perfectly consistent across multiple calls")
    
    print("\n✅ All consistency tests passed!\n")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CENTRALIZED MACRO CALCULATION - STANDALONE TEST")
    print("=" * 70 + "\n")
    
    try:
        test_calcular_macros_tradicional()
        test_consistency()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

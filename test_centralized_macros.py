#!/usr/bin/env python3
"""
Test suite for centralized macro calculation functions.
Ensures consistency across UI, email, and all calculation paths.
"""

import sys
import os

# Mock streamlit and other dependencies before importing
class MockStreamlit:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None
    
    class session_state:
        @classmethod
        def get(cls, key, default=None):
            return default
        
        @classmethod
        def __setattr__(cls, key, value):
            pass
    
    class secrets:
        @classmethod
        def get(cls, key, default=None):
            return default

sys.modules['streamlit'] = MockStreamlit()
sys.modules['pandas'] = type('pandas', (), {})()
sys.modules['numpy'] = type('numpy', (), {})()

sys.path.insert(0, '/home/runner/work/mupai555/mupai555')

from streamlit_app import (
    calcular_macros_tradicional,
    calcular_macros_psmf,
    calculate_psmf,
    obtener_factor_proteina_tradicional,
    obtener_porcentaje_grasa_tmb_tradicional,
    debe_usar_mlg_para_proteina
)

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
    tolerance = 5  # Allow 5 kcal tolerance for rounding
    assert abs(total_kcal - 2000) <= tolerance, f"Calories don't match: {total_kcal} vs 2000"
    print(f"✅ Total calories: {total_kcal} kcal (target: 2000 kcal)")
    
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
    print(f"✅ Correctly using MLG base for high adiposity female")
    
    print("\n✅ All calcular_macros_tradicional tests passed!\n")

def test_calcular_macros_psmf():
    """Test PSMF macro calculation function."""
    print("=" * 70)
    print("TEST: calcular_macros_psmf()")
    print("=" * 70)
    
    # Test case 1: PSMF for high adiposity female
    print("\nTest 1: PSMF for High Adiposity Female")
    psmf_recs = calculate_psmf(
        sexo="Mujer",
        peso=140.0,
        grasa_corregida=49.0,
        mlg=71.4,
        estatura_cm=164
    )
    
    result = calcular_macros_psmf(psmf_recs)
    
    print(f"PSMF Aplicable: {result['aplicable']}")
    print(f"Proteína: {result['proteina_g']}g ({result['proteina_kcal']} kcal)")
    print(f"Grasa: {result['grasa_g']}g ({result['grasa_kcal']} kcal)")
    print(f"Carbohidratos: {result['carbo_g']}g ({result['carbo_kcal']} kcal)")
    print(f"Calorías totales: {result['calorias_dia']} kcal")
    
    # Validate macros add up to total calories
    total_kcal = result['proteina_kcal'] + result['grasa_kcal'] + result['carbo_kcal']
    tolerance = 5
    assert abs(total_kcal - result['calorias_dia']) <= tolerance, \
        f"Calories don't match: {total_kcal} vs {result['calorias_dia']}"
    print(f"✅ Calories match: {total_kcal} kcal")
    
    # Test case 2: PSMF not applicable
    print("\nTest 2: PSMF Not Applicable (Low BF%)")
    psmf_recs = calculate_psmf(
        sexo="Hombre",
        peso=80.0,
        grasa_corregida=15.0,
        mlg=68.0,
        estatura_cm=180
    )
    
    result = calcular_macros_psmf(psmf_recs)
    
    print(f"PSMF Aplicable: {result['aplicable']}")
    assert not result['aplicable'], "PSMF should not be applicable for 15% BF male"
    print(f"✅ Correctly returns not applicable for low BF%")
    
    print("\n✅ All calcular_macros_psmf tests passed!\n")

def test_consistency_across_calculations():
    """Test that the same input produces identical results in all calculation paths."""
    print("=" * 70)
    print("TEST: Consistency Across Calculation Paths")
    print("=" * 70)
    
    # Define test parameters
    ingesta_cal = 2000
    tmb = 1500
    sexo = "Hombre"
    grasa_corr = 20.0
    peso = 75.0
    mlg = 60.0
    
    # Calculate using centralized function
    result1 = calcular_macros_tradicional(ingesta_cal, tmb, sexo, grasa_corr, peso, mlg)
    
    # Calculate again (simulating multiple code paths)
    result2 = calcular_macros_tradicional(ingesta_cal, tmb, sexo, grasa_corr, peso, mlg)
    
    print(f"\nTest: Same input produces identical results")
    print(f"Call 1 - Proteína: {result1['proteina_g']}g, Grasa: {result1['grasa_g']}g, Carbos: {result1['carbo_g']}g")
    print(f"Call 2 - Proteína: {result2['proteina_g']}g, Grasa: {result2['grasa_g']}g, Carbos: {result2['carbo_g']}g")
    
    assert result1['proteina_g'] == result2['proteina_g'], "Protein values don't match"
    assert result1['grasa_g'] == result2['grasa_g'], "Fat values don't match"
    assert result1['carbo_g'] == result2['carbo_g'], "Carb values don't match"
    
    print("✅ Results are consistent across multiple calls")
    
    print("\n✅ All consistency tests passed!\n")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CENTRALIZED MACRO CALCULATION - TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_calcular_macros_tradicional()
        test_calcular_macros_psmf()
        test_consistency_across_calculations()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

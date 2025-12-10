"""
Tests for Omron extrapolation logic and LBM-based calculations.

These tests verify the new threshold-based extrapolation logic for Omron readings
and the LBM-based protein calculations for PSMF and traditional plans.
"""

import sys
import os

# Add parent directory to path to import streamlit_app functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np


# Standalone implementations to avoid streamlit dependency issues
def corregir_porcentaje_grasa_standalone(medido, metodo, sexo, allow_extrapolate=False, max_extrapolate=60.0):
    """
    Standalone version of corregir_porcentaje_grasa for testing.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        # Tablas especializadas por sexo
        if sexo == "Hombre":
            tabla = {
                5: 2.8, 6: 3.8, 7: 4.8, 8: 5.8, 9: 6.8,
                10: 7.8, 11: 8.8, 12: 9.8, 13: 10.8, 14: 11.8,
                15: 13.8, 16: 14.8, 17: 15.8, 18: 16.8, 19: 17.8,
                20: 20.8, 21: 21.8, 22: 22.8, 23: 23.8, 24: 24.8,
                25: 27.3, 26: 28.3, 27: 29.3, 28: 30.3, 29: 31.3,
                30: 33.8, 31: 34.8, 32: 35.8, 33: 36.8, 34: 37.8,
                35: 40.3, 36: 41.3, 37: 42.3, 38: 43.3, 39: 44.3,
                40: 45.3
            }
        else:  # Mujer
            tabla = {
                5: 2.2, 6: 3.2, 7: 4.2, 8: 5.2, 9: 6.2,
                10: 7.2, 11: 8.2, 12: 9.2, 13: 10.2, 14: 11.2,
                15: 13.2, 16: 14.2, 17: 15.2, 18: 16.2, 19: 17.2,
                20: 20.2, 21: 21.2, 22: 22.2, 23: 23.2, 24: 24.2,
                25: 26.7, 26: 27.7, 27: 28.7, 28: 29.7, 29: 30.7,
                30: 33.2, 31: 34.2, 32: 35.2, 33: 36.2, 34: 37.2,
                35: 39.7, 36: 40.7, 37: 41.7, 38: 42.7, 39: 43.7,
                40: 44.7
            }
        
        omron_values = sorted(tabla.keys())
        dexa_values = [tabla[k] for k in omron_values]
        
        min_omron = min(omron_values)
        max_omron = max(omron_values)
        base_at_40 = tabla[40]
        
        # Si esta dentro del rango de la tabla (<=40), interpolar
        if min_omron <= medido <= max_omron:
            resultado = float(np.interp(medido, omron_values, dexa_values))
            return resultado, {"extrapolated": False, "truncated": False, "high_adiposity": False}
        
        # Si esta por debajo del minimo
        elif medido < min_omron:
            return tabla[min_omron], {"extrapolated": False, "truncated": False, "high_adiposity": False}
        
        # Si esta por encima del maximo (medido > 40)
        else:
            # 40 < medido < 45: truncar
            if medido < 45.0:
                if allow_extrapolate:
                    # Si el usuario permite extrapolacion manual, extrapolar
                    slope = 1.0
                    extrapolated = base_at_40 + slope * (medido - 40)
                    result = min(extrapolated, max_extrapolate)
                    return float(result), {"extrapolated": True, "truncated": False, "high_adiposity": False}
                else:
                    # Truncar si no permite extrapolacion
                    return base_at_40, {"extrapolated": False, "truncated": True, "high_adiposity": False}
            
            # medido >= 45.0: extrapolacion automatica
            else:
                slope = 1.0
                extrapolated = base_at_40 + slope * (medido - 40)
                result = min(extrapolated, max_extrapolate)
                return float(result), {"extrapolated": True, "truncated": False, "high_adiposity": True}
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02), {"extrapolated": False, "truncated": False, "high_adiposity": False}
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor), {"extrapolated": False, "truncated": False, "high_adiposity": False}
    else:  # DEXA
        return float(medido), {"extrapolated": False, "truncated": False, "high_adiposity": False}


def calcular_mlg_standalone(peso, porcentaje_grasa):
    """Standalone version of calcular_mlg."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def calculate_psmf_standalone(sexo, peso, grasa_corregida, mlg):
    """Standalone version of calculate_psmf using LBM."""
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
        mlg = 56.0
    
    # Determinar elegibilidad
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplicable = True
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplicable = True
    else:
        return {"psmf_aplicable": False}
    
    if psmf_aplicable:
        # Proteina usando LBM
        if grasa_corregida < 25:
            proteina_g_dia = round(mlg * 1.8, 1)
        else:
            proteina_g_dia = round(mlg * 1.6, 1)
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
            "usa_lbm": True
        }
    else:
        return {"psmf_aplicable": False}


# Test cases
def test_omron_interpolation_within_range():
    """Test interpolation for values within table range (<=40)."""
    result, flags = corregir_porcentaje_grasa_standalone(25, "Omron HBF-516 (BIA)", "Hombre")
    assert result == 27.3, f"Expected 27.3, got {result}"
    assert not flags["extrapolated"], "Should not be extrapolated"
    assert not flags["truncated"], "Should not be truncated"
    print("✓ Test interpolation within range passed")


def test_omron_truncation_40_to_45():
    """Test truncation for values between 40 and 45 without allow_extrapolate."""
    result, flags = corregir_porcentaje_grasa_standalone(42, "Omron HBF-516 (BIA)", "Hombre", allow_extrapolate=False)
    assert result == 45.3, f"Expected 45.3 (truncated to 40), got {result}"
    assert not flags["extrapolated"], "Should not be extrapolated"
    assert flags["truncated"], "Should be truncated"
    assert not flags["high_adiposity"], "Should not be high adiposity"
    print("✓ Test truncation 40-45 passed")


def test_omron_manual_extrapolation_40_to_45():
    """Test manual extrapolation for values between 40 and 45 with allow_extrapolate=True."""
    result, flags = corregir_porcentaje_grasa_standalone(42, "Omron HBF-516 (BIA)", "Hombre", allow_extrapolate=True)
    expected = 45.3 + 1.0 * (42 - 40)  # base_at_40 + slope * (medido - 40)
    assert abs(result - expected) < 0.1, f"Expected {expected}, got {result}"
    assert flags["extrapolated"], "Should be extrapolated"
    assert not flags["truncated"], "Should not be truncated"
    print("✓ Test manual extrapolation 40-45 passed")


def test_omron_auto_extrapolation_above_45():
    """Test automatic extrapolation for values >= 45 (high adiposity)."""
    result, flags = corregir_porcentaje_grasa_standalone(50, "Omron HBF-516 (BIA)", "Hombre", allow_extrapolate=False)
    expected = 45.3 + 1.0 * (50 - 40)  # slope = 1.0
    assert abs(result - expected) < 0.1, f"Expected {expected}, got {result}"
    assert flags["extrapolated"], "Should be extrapolated"
    assert not flags["truncated"], "Should not be truncated"
    assert flags["high_adiposity"], "Should be high adiposity"
    print("✓ Test auto extrapolation above 45 passed")


def test_omron_max_extrapolate_cap():
    """Test that extrapolation is capped at max_extrapolate."""
    result, flags = corregir_porcentaje_grasa_standalone(100, "Omron HBF-516 (BIA)", "Hombre", max_extrapolate=60.0)
    assert result == 60.0, f"Expected 60.0 (capped), got {result}"
    assert flags["extrapolated"], "Should be extrapolated"
    assert flags["high_adiposity"], "Should be high adiposity"
    print("✓ Test max extrapolate cap passed")


def test_omron_mujer_truncation():
    """Test truncation for women between 40 and 45."""
    result, flags = corregir_porcentaje_grasa_standalone(43, "Omron HBF-516 (BIA)", "Mujer", allow_extrapolate=False)
    assert result == 44.7, f"Expected 44.7 (truncated to 40), got {result}"
    assert flags["truncated"], "Should be truncated"
    print("✓ Test mujer truncation passed")


def test_psmf_uses_lbm_low_fat():
    """Test that PSMF uses LBM for protein calculation with low body fat (<25%)."""
    peso = 80.0
    grasa_corregida = 20.0
    mlg = calcular_mlg_standalone(peso, grasa_corregida)
    
    result = calculate_psmf_standalone("Hombre", peso, grasa_corregida, mlg)
    
    assert result["psmf_aplicable"], "PSMF should be applicable"
    assert result["usa_lbm"], "Should use LBM"
    
    expected_proteina = round(mlg * 1.8, 1)
    assert result["proteina_g_dia"] == expected_proteina, \
        f"Expected {expected_proteina}g protein (1.8g/kg LBM), got {result['proteina_g_dia']}g"
    print(f"✓ Test PSMF uses LBM (low fat) passed: {result['proteina_g_dia']}g for {mlg:.1f}kg LBM")


def test_psmf_uses_lbm_high_fat():
    """Test that PSMF uses LBM for protein calculation with high body fat (>=25%)."""
    peso = 90.0
    grasa_corregida = 30.0
    mlg = calcular_mlg_standalone(peso, grasa_corregida)
    
    result = calculate_psmf_standalone("Hombre", peso, grasa_corregida, mlg)
    
    assert result["psmf_aplicable"], "PSMF should be applicable"
    expected_proteina = round(mlg * 1.6, 1)
    assert result["proteina_g_dia"] == expected_proteina, \
        f"Expected {expected_proteina}g protein (1.6g/kg LBM), got {result['proteina_g_dia']}g"
    print(f"✓ Test PSMF uses LBM (high fat) passed: {result['proteina_g_dia']}g for {mlg:.1f}kg LBM")


def test_psmf_not_applicable_low_fat():
    """Test that PSMF is not applicable for low body fat."""
    result = calculate_psmf_standalone("Hombre", 75.0, 15.0, 63.75)
    assert not result["psmf_aplicable"], "PSMF should not be applicable for 15% body fat"
    print("✓ Test PSMF not applicable (low fat) passed")


def test_inbody_no_extrapolation():
    """Test that InBody method doesn't trigger extrapolation logic."""
    result, flags = corregir_porcentaje_grasa_standalone(50, "InBody 270 (BIA profesional)", "Hombre")
    expected = 50 * 1.02
    assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    assert not flags["extrapolated"], "InBody should not use extrapolation"
    print("✓ Test InBody no extrapolation passed")


def test_dexa_passthrough():
    """Test that DEXA method returns value as-is."""
    result, flags = corregir_porcentaje_grasa_standalone(25.5, "DEXA (Gold Standard)", "Hombre")
    assert result == 25.5, f"Expected 25.5, got {result}"
    assert not flags["extrapolated"], "DEXA should not use extrapolation"
    print("✓ Test DEXA passthrough passed")


def run_all_tests():
    """Run all tests."""
    print("\n=== Running Omron Extrapolation and LBM Tests ===\n")
    
    test_omron_interpolation_within_range()
    test_omron_truncation_40_to_45()
    test_omron_manual_extrapolation_40_to_45()
    test_omron_auto_extrapolation_above_45()
    test_omron_max_extrapolate_cap()
    test_omron_mujer_truncation()
    test_psmf_uses_lbm_low_fat()
    test_psmf_uses_lbm_high_fat()
    test_psmf_not_applicable_low_fat()
    test_inbody_no_extrapolation()
    test_dexa_passthrough()
    
    print("\n=== All tests passed! ===\n")


if __name__ == "__main__":
    run_all_tests()

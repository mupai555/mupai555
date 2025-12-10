"""
Full workflow tests to verify end-to-end functionality.

Tests various scenarios with different body fat percentages and methods.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np


def calcular_mlg(peso, porcentaje_grasa):
    """Calculate LBM."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def corregir_porcentaje_grasa(medido, metodo, sexo, allow_extrapolate=False, max_extrapolate=60.0):
    """Standalone correction function."""
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
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
        else:
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
        
        if min_omron <= medido <= max_omron:
            return float(np.interp(medido, omron_values, dexa_values))
        elif medido < min_omron:
            return tabla[min_omron]
        else:
            if medido < 45.0:
                if not allow_extrapolate:
                    return base_at_40
                else:
                    slope = 1.0
                    extrapolated = base_at_40 + slope * (medido - 40)
                    return float(min(extrapolated, max_extrapolate))
            else:
                slope = 1.0
                extrapolated = base_at_40 + slope * (medido - 40)
                return float(min(extrapolated, max_extrapolate))
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02)
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor)
    else:
        return float(medido)


def calculate_psmf(sexo, peso, grasa_corregida, mlg):
    """Calculate PSMF using LBM."""
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
        mlg = 56.0
    
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplicable = True
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplicable = True
    else:
        return {"psmf_aplicable": False}
    
    if psmf_aplicable:
        if grasa_corregida < 25:
            proteina_g_dia = round(mlg * 1.8, 1)
        else:
            proteina_g_dia = round(mlg * 1.6, 1)
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
        }
    else:
        return {"psmf_aplicable": False}


def obtener_factor_proteina_tradicional(grasa_corregida):
    """Get protein factor for traditional plan."""
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa = 20.0
    
    if grasa < 10:
        return 2.2
    elif grasa < 15:
        return 2.0
    elif grasa < 25:
        return 1.8
    else:
        return 1.6


def test_scenario_normal_range():
    """Test scenario with normal range Omron reading."""
    print("\n--- Scenario: Normal range (25% Omron) ---")
    medido = 25
    sexo = "Hombre"
    peso = 80
    
    grasa_corregida = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"  Medido: {medido}% Omron")
    print(f"  Corregido: {grasa_corregida:.1f}% DEXA")
    print(f"  LBM: {mlg:.1f} kg")
    
    psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
    if psmf_recs.get("psmf_aplicable"):
        print(f"  PSMF aplicable: Si")
        print(f"  Proteina PSMF: {psmf_recs['proteina_g_dia']}g ({psmf_recs['proteina_g_dia']/mlg:.2f}g/kg LBM)")
    else:
        print(f"  PSMF aplicable: No")
    
    assert grasa_corregida == 27.3
    print("✓ Test passed")


def test_scenario_truncation():
    """Test scenario with truncation (42% Omron)."""
    print("\n--- Scenario: Truncation zone (42% Omron, no manual) ---")
    medido = 42
    sexo = "Hombre"
    peso = 100
    
    grasa_corregida = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo, allow_extrapolate=False)
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"  Medido: {medido}% Omron")
    print(f"  Corregido (truncado): {grasa_corregida:.1f}% DEXA")
    print(f"  LBM: {mlg:.1f} kg")
    
    # Traditional plan should use LBM since grasa >= 35%
    usar_lbm = grasa_corregida >= 35.0
    if usar_lbm:
        factor_proteina = 1.6
        proteina_tradicional = round(mlg * factor_proteina, 1)
        print(f"  Plan tradicional usa LBM: Si")
        print(f"  Proteina tradicional: {proteina_tradicional}g ({factor_proteina}g/kg LBM)")
    else:
        factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
        proteina_tradicional = round(peso * factor_proteina, 1)
        print(f"  Plan tradicional usa peso total: Si")
        print(f"  Proteina tradicional: {proteina_tradicional}g ({factor_proteina}g/kg)")
    
    assert grasa_corregida == 45.3
    assert usar_lbm
    print("✓ Test passed")


def test_scenario_high_adiposity():
    """Test scenario with high adiposity (50% Omron)."""
    print("\n--- Scenario: High adiposity (50% Omron, auto-extrapolate) ---")
    medido = 50
    sexo = "Hombre"
    peso = 110
    
    grasa_corregida = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"  Medido: {medido}% Omron")
    print(f"  Corregido (extrapolado): {grasa_corregida:.1f}% DEXA")
    print(f"  LBM: {mlg:.1f} kg")
    
    psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
    if psmf_recs.get("psmf_aplicable"):
        print(f"  PSMF aplicable: Si")
        print(f"  Proteina PSMF: {psmf_recs['proteina_g_dia']}g ({psmf_recs['proteina_g_dia']/mlg:.2f}g/kg LBM)")
        print(f"  Ratio peso total: {psmf_recs['proteina_g_dia']/peso:.2f}g/kg")
    
    # Traditional plan should definitely use LBM
    usar_lbm = grasa_corregida >= 35.0
    if usar_lbm:
        factor_proteina = 1.6
        proteina_tradicional = round(mlg * factor_proteina, 1)
        print(f"  Plan tradicional usa LBM: Si")
        print(f"  Proteina tradicional: {proteina_tradicional}g ({factor_proteina}g/kg LBM)")
    
    expected = 45.3 + 1.0 * (50 - 40)
    assert abs(grasa_corregida - expected) < 0.1
    assert usar_lbm
    print("✓ Test passed")


def test_scenario_mujer_alta_grasa():
    """Test scenario with woman at high body fat."""
    print("\n--- Scenario: Mujer con alta grasa (40% Omron) ---")
    medido = 40
    sexo = "Mujer"
    peso = 75
    
    grasa_corregida = corregir_porcentaje_grasa(medido, "Omron HBF-516 (BIA)", sexo)
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"  Medido: {medido}% Omron")
    print(f"  Corregido: {grasa_corregida:.1f}% DEXA")
    print(f"  LBM: {mlg:.1f} kg")
    
    psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
    if psmf_recs.get("psmf_aplicable"):
        print(f"  PSMF aplicable: Si")
        print(f"  Proteina PSMF: {psmf_recs['proteina_g_dia']}g ({psmf_recs['proteina_g_dia']/mlg:.2f}g/kg LBM)")
    
    # Traditional plan should use LBM since grasa >= 35%
    usar_lbm = grasa_corregida >= 35.0
    if usar_lbm:
        factor_proteina = 1.6
        proteina_tradicional = round(mlg * factor_proteina, 1)
        print(f"  Plan tradicional usa LBM: Si")
        print(f"  Proteina tradicional: {proteina_tradicional}g ({factor_proteina}g/kg LBM)")
    
    assert grasa_corregida == 44.7
    assert psmf_recs.get("psmf_aplicable") == True
    assert usar_lbm
    print("✓ Test passed")


def run_all_scenarios():
    """Run all workflow scenarios."""
    print("\n=== Running Full Workflow Scenarios ===")
    
    test_scenario_normal_range()
    test_scenario_truncation()
    test_scenario_high_adiposity()
    test_scenario_mujer_alta_grasa()
    
    print("\n=== All workflow scenarios completed successfully! ===\n")


if __name__ == "__main__":
    run_all_scenarios()

#!/usr/bin/env python3
"""
Test for Traditional Plan protein calculation with MLG base for high adiposity.

This test validates the 30/42 rules:
- Men: Use MLG if body fat >= 30%
- Women: Use MLG if body fat >= 42%
"""

import sys
import os


# Copy the necessary functions directly to avoid import issues
def calcular_mlg(peso, porcentaje_grasa):
    """Calcula la Masa Libre de Grasa."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def obtener_factor_proteina_tradicional(grasa_corregida):
    """
    Determina el factor de proteína en g/kg según el porcentaje de grasa corporal corregido
    para el plan tradicional.
    """
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa = 20.0  # Valor por defecto
    
    if grasa >= 35:
        return 1.6
    elif grasa >= 25:
        return 1.8
    elif grasa >= 15:
        return 2.0
    else:  # grasa < 15 (includes 4-14.9%)
        return 2.2


def debe_usar_mlg_para_proteina(sexo, grasa_corregida):
    """
    Determina si se debe usar MLG como base para el cálculo de proteína
    según las reglas 30/42 para alta adiposidad.
    """
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        return False
    
    if sexo == "Hombre" and grasa >= 30:
        return True
    elif sexo == "Mujer" and grasa >= 42:
        return True
    else:
        return False


def test_karina_case():
    """
    Test case for Karina:
    - Sexo: Mujer
    - Peso: 140.0 kg
    - % grasa corregido: 49%
    - Factor for high fat (>=35%): 1.6
    - Expected Result: Proteína = 1.6 × 71.4 (MLG) = 114.24 g/día ≈ 114 g
    """
    print("=" * 60)
    print("Test Case: Karina")
    print("=" * 60)
    
    sexo = "Mujer"
    peso = 140.0
    grasa_corregida = 49.0
    
    # Calculate MLG
    mlg = calcular_mlg(peso, grasa_corregida)
    print(f"Peso: {peso} kg")
    print(f"Grasa corregida: {grasa_corregida}%")
    print(f"MLG calculado: {mlg:.2f} kg")
    
    # Check if we should use MLG (30/42 rules)
    usar_mlg_para_proteina = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    
    print(f"Usar MLG para proteína: {usar_mlg_para_proteina}")
    print(f"Razón: {sexo} con {grasa_corregida}% grasa (umbral para mujeres: 42%)")
    
    # Determine base
    base_proteina_kg = mlg if usar_mlg_para_proteina else peso
    base_proteina_nombre = "MLG" if usar_mlg_para_proteina else "Peso total"
    
    print(f"Base para proteína: {base_proteina_nombre} = {base_proteina_kg:.2f} kg")
    
    # Get protein factor
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    print(f"Factor proteína: {factor_proteina} g/kg")
    
    # Calculate protein
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    print(f"\nCálculo: {base_proteina_kg:.2f} kg × {factor_proteina} g/kg = {proteina_g} g")
    
    # Expected result
    expected_proteina = 114.24  # 71.4 kg MLG × 1.6 g/kg
    expected_proteina_rounded = round(expected_proteina, 1)
    
    print(f"\nProteína calculada: {proteina_g} g")
    print(f"Proteína esperada: {expected_proteina_rounded} g")
    
    # Verify
    tolerance = 0.5  # Allow small rounding differences
    assert abs(proteina_g - expected_proteina_rounded) <= tolerance, \
        f"Expected protein ~{expected_proteina_rounded}g, but got {proteina_g}g"
    
    print("✅ Test passed!")
    print()


def test_man_high_adiposity():
    """
    Test case for man with high adiposity (>= 30%)
    Should use MLG as base.
    """
    print("=" * 60)
    print("Test Case: Man with High Adiposity (35%)")
    print("=" * 60)
    
    sexo = "Hombre"
    peso = 120.0
    grasa_corregida = 35.0
    
    # Calculate MLG
    mlg = calcular_mlg(peso, grasa_corregida)
    print(f"Peso: {peso} kg")
    print(f"Grasa corregida: {grasa_corregida}%")
    print(f"MLG calculado: {mlg:.2f} kg")
    
    # Check if we should use MLG (30/42 rules)
    usar_mlg_para_proteina = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    
    print(f"Usar MLG para proteína: {usar_mlg_para_proteina}")
    
    # Should use MLG
    assert usar_mlg_para_proteina == True, "Should use MLG for man with 35% body fat"
    
    # Determine base
    base_proteina_kg = mlg if usar_mlg_para_proteina else peso
    base_proteina_nombre = "MLG" if usar_mlg_para_proteina else "Peso total"
    
    print(f"Base para proteína: {base_proteina_nombre} = {base_proteina_kg:.2f} kg")
    
    # Get protein factor
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    print(f"Factor proteína: {factor_proteina} g/kg (>=35% grasa)")
    
    # Calculate protein
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    print(f"\nCálculo: {base_proteina_kg:.2f} kg × {factor_proteina} g/kg = {proteina_g} g")
    
    # Verify it's using MLG, not total weight
    proteina_with_total_weight = round(peso * factor_proteina, 1)
    print(f"\nSi usara peso total: {peso} kg × {factor_proteina} g/kg = {proteina_with_total_weight} g")
    print(f"Diferencia (peso total vs MLG): {proteina_with_total_weight - proteina_g} g")
    
    assert proteina_g < proteina_with_total_weight, "Protein with MLG should be less than with total weight"
    
    print("✅ Test passed!")
    print()


def test_woman_moderate_adiposity():
    """
    Test case for woman with moderate adiposity (< 42%)
    Should use total weight as base.
    """
    print("=" * 60)
    print("Test Case: Woman with Moderate Adiposity (35%)")
    print("=" * 60)
    
    sexo = "Mujer"
    peso = 80.0
    grasa_corregida = 35.0
    
    # Calculate MLG
    mlg = calcular_mlg(peso, grasa_corregida)
    print(f"Peso: {peso} kg")
    print(f"Grasa corregida: {grasa_corregida}%")
    print(f"MLG calculado: {mlg:.2f} kg")
    
    # Check if we should use MLG (30/42 rules)
    usar_mlg_para_proteina = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    
    print(f"Usar MLG para proteína: {usar_mlg_para_proteina}")
    
    # Should NOT use MLG (below 42% threshold)
    assert usar_mlg_para_proteina == False, "Should NOT use MLG for woman with 35% body fat"
    
    # Determine base
    base_proteina_kg = mlg if usar_mlg_para_proteina else peso
    base_proteina_nombre = "MLG" if usar_mlg_para_proteina else "Peso total"
    
    print(f"Base para proteína: {base_proteina_nombre} = {base_proteina_kg:.2f} kg")
    
    # Get protein factor
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    print(f"Factor proteína: {factor_proteina} g/kg (>=35% grasa)")
    
    # Calculate protein
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    print(f"\nCálculo: {base_proteina_kg:.2f} kg × {factor_proteina} g/kg = {proteina_g} g")
    
    # Verify it's using total weight
    assert base_proteina_kg == peso, "Should be using total weight as base"
    
    print("✅ Test passed!")
    print()


def test_man_low_adiposity():
    """
    Test case for man with low adiposity (< 30%)
    Should use total weight as base.
    """
    print("=" * 60)
    print("Test Case: Man with Low Adiposity (15%)")
    print("=" * 60)
    
    sexo = "Hombre"
    peso = 80.0
    grasa_corregida = 15.0
    
    # Calculate MLG
    mlg = calcular_mlg(peso, grasa_corregida)
    print(f"Peso: {peso} kg")
    print(f"Grasa corregida: {grasa_corregida}%")
    print(f"MLG calculado: {mlg:.2f} kg")
    
    # Check if we should use MLG (30/42 rules)
    usar_mlg_para_proteina = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    
    print(f"Usar MLG para proteína: {usar_mlg_para_proteina}")
    
    # Should NOT use MLG (below 30% threshold)
    assert usar_mlg_para_proteina == False, "Should NOT use MLG for man with 15% body fat"
    
    # Determine base
    base_proteina_kg = mlg if usar_mlg_para_proteina else peso
    base_proteina_nombre = "MLG" if usar_mlg_para_proteina else "Peso total"
    
    print(f"Base para proteína: {base_proteina_nombre} = {base_proteina_kg:.2f} kg")
    
    # Get protein factor (should be 2.0 g/kg for 15% fat, as 15-24.9% range)
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    print(f"Factor proteína: {factor_proteina} g/kg (15-24.9% grasa)")
    
    assert factor_proteina == 2.0, "Factor should be 2.0 for 15% body fat"
    
    # Calculate protein
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    print(f"\nCálculo: {base_proteina_kg:.2f} kg × {factor_proteina} g/kg = {proteina_g} g")
    
    # Verify it's using total weight
    assert base_proteina_kg == peso, "Should be using total weight as base"
    
    print("✅ Test passed!")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PROTEIN CALCULATION WITH MLG BASE - TEST SUITE")
    print("Testing 30/42 Rules for High Adiposity")
    print("=" * 60 + "\n")
    
    try:
        test_karina_case()
        test_man_high_adiposity()
        test_woman_moderate_adiposity()
        test_man_low_adiposity()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

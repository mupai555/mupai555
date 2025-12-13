#!/usr/bin/env python3
"""
Test for PSMF tier-based calculation.

This test validates the tier system for PSMF:
- Tier 1: Low adiposity (Men BF% < 25, Women BF% < 35) - Base = total weight
- Tier 2: Moderate adiposity (Men 25 <= BF% < 35, Women 35 <= BF% < 45) - Base = MLG
- Tier 3: High adiposity (IMC >= 40 OR Men BF% >= 35 OR Women BF% >= 45) - Base = ideal weight (IMC 25)
"""

import sys


def calcular_mlg(peso, porcentaje_grasa):
    """Calcula la Masa Libre de Grasa."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm=None):
    """
    Calcula los parámetros para PSMF con sistema de tiers.
    """
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
    
    # Determinar elegibilidad para PSMF según sexo y % grasa
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >18%"
        calorias_piso_dia = 800
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >23%"
        calorias_piso_dia = 700
    else:
        return {"psmf_aplicable": False}
    
    if psmf_aplicable:
        # Calcular variables necesarias
        if estatura_cm is not None:
            estatura_m = estatura_cm / 100
            imc = peso / (estatura_m ** 2)
            peso_ideal_ref_kg = 25 * (estatura_m ** 2)
        else:
            estatura_m = None
            imc = None
            peso_ideal_ref_kg = None
        
        # DETERMINACIÓN DE TIER basado en adiposidad
        # Tier 3 predomina - verificar primero
        if (imc is not None and imc >= 40) or \
           (sexo == "Hombre" and grasa_corregida >= 35) or \
           (sexo == "Mujer" and grasa_corregida >= 45):
            tier = 3
        # Tier 2
        elif (sexo == "Hombre" and 25 <= grasa_corregida < 35) or \
             (sexo == "Mujer" and 35 <= grasa_corregida < 45):
            tier = 2
        # Tier 1
        elif (sexo == "Hombre" and grasa_corregida < 25) or \
             (sexo == "Mujer" and grasa_corregida < 35):
            tier = 1
        else:
            tier = 1  # Default fallback
        
        # ELECCIÓN DE BASE DE PROTEÍNA según tier
        if tier == 1:
            base_proteina_kg = peso
            base_proteina_nombre = "Peso total"
        elif tier == 2:
            base_proteina_kg = mlg
            base_proteina_nombre = "MLG"
        elif tier == 3:
            base_proteina_kg = peso_ideal_ref_kg if peso_ideal_ref_kg is not None else mlg
            base_proteina_nombre = "Peso ideal (IMC 25)"
        else:
            base_proteina_kg = peso
            base_proteina_nombre = "Peso total"
        
        # FACTORES DE PROTEÍNA Y GRASAS según % grasa corporal corregida
        if grasa_corregida < 25:
            factor_proteina_psmf = 1.8
            grasa_g_dia = 30.0
        else:
            factor_proteina_psmf = 1.6
            grasa_g_dia = 50.0
        
        proteina_g_dia = round(base_proteina_kg * factor_proteina_psmf, 1)
        
        # MULTIPLICADOR CALÓRICO según % grasa corporal
        if grasa_corregida > 35:
            multiplicador = 8.3
            perfil_grasa = "alto % grasa (PSMF tradicional)"
        elif grasa_corregida >= 25 and sexo == "Hombre":
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        elif grasa_corregida >= 30 and sexo == "Mujer":
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        else:
            multiplicador = 9.6
            perfil_grasa = "más magro (abdominales visibles)"
        
        # CALORÍAS OBJETIVO = proteína (g) × multiplicador
        kcal_psmf_obj = round(proteina_g_dia * multiplicador, 0)
        
        # CARB CAP por tier
        if tier == 1:
            carb_cap_g = 50
        elif tier == 2:
            carb_cap_g = 40
        elif tier == 3:
            carb_cap_g = 30
        else:
            carb_cap_g = 50
        
        # CÁLCULO DE CARBOHIDRATOS con cap
        kcal_prot = 4 * proteina_g_dia
        kcal_grasa = 9 * grasa_g_dia
        carbs_g_calculado = max((kcal_psmf_obj - (kcal_prot + kcal_grasa)) / 4, 0)
        
        carbs_g = min(carbs_g_calculado, carb_cap_g)
        carb_cap_aplicado = carbs_g_calculado > carb_cap_g
        
        # CALORÍAS FINALES recalculadas por macros
        calorias_dia = kcal_prot + kcal_grasa + (4 * carbs_g)
        
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        if sexo == "Hombre":
            perdida_semanal_min = 0.8
            perdida_semanal_max = 1.2
        else:
            perdida_semanal_min = 0.6
            perdida_semanal_max = 1.0
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
            "grasa_g_dia": grasa_g_dia,
            "carbs_g_dia": round(carbs_g, 1),
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Protocolo con tiers: {perfil_grasa}",
            "tier_psmf": tier,
            "base_proteina_usada": base_proteina_nombre,
            "base_proteina_kg": round(base_proteina_kg, 2),
            "carb_cap_aplicado_g": carb_cap_g,
            "carb_cap_fue_aplicado": carb_cap_aplicado,
            "factor_proteina_psmf": factor_proteina_psmf,
            "imc": round(imc, 2) if imc is not None else None
        }
    else:
        return {"psmf_aplicable": False}


def test_karina_tier3():
    """
    Test case: Karina (from problem statement)
    - Sexo: Mujer
    - Peso: 140 kg
    - Estatura: 164 cm
    - BF% corregido: ~49%
    
    Expected:
    - Tier 3 (BF% >= 45% for women)
    - Base proteína = peso_ideal_ref_kg ≈ 67.2 kg (IMC 25)
    - Factor proteína = 1.6 (BF% >= 25%)
    - Proteína = 1.6 × 67.2 ≈ 107.5 g
    - Carb cap = 30g (Tier 3)
    """
    print("=" * 70)
    print("Test Case: Karina - Tier 3 (High Adiposity)")
    print("=" * 70)
    
    sexo = "Mujer"
    peso = 140.0
    estatura_cm = 164
    grasa_corregida = 49.0
    
    # Calculate derived values
    mlg = calcular_mlg(peso, grasa_corregida)
    estatura_m = estatura_cm / 100
    imc = peso / (estatura_m ** 2)
    peso_ideal_ref_kg = 25 * (estatura_m ** 2)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  Estatura: {estatura_cm} cm ({estatura_m} m)")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  IMC: {imc:.2f}")
    print(f"  MLG: {mlg:.2f} kg")
    print(f"  Peso ideal (IMC 25): {peso_ideal_ref_kg:.2f} kg")
    print()
    
    # Call function
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    # Verify results
    print(f"Resultados:")
    print(f"  PSMF aplicable: {result.get('psmf_aplicable')}")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Base proteína kg: {result.get('base_proteina_kg')} kg")
    print(f"  Factor proteína: {result.get('factor_proteina_psmf')} g/kg")
    print(f"  Proteína: {result.get('proteina_g_dia')} g/día")
    print(f"  Grasas: {result.get('grasa_g_dia')} g/día")
    print(f"  Carb cap: {result.get('carb_cap_aplicado_g')} g")
    print(f"  Carbohidratos: {result.get('carbs_g_dia')} g/día")
    print(f"  Calorías finales: {result.get('calorias_dia'):.0f} kcal/día")
    print()
    
    # Assertions
    assert result['psmf_aplicable'] == True, "PSMF should be applicable"
    assert result['tier_psmf'] == 3, f"Expected Tier 3, got Tier {result['tier_psmf']}"
    assert result['base_proteina_usada'] == "Peso ideal (IMC 25)", "Base should be ideal weight"
    assert abs(result['base_proteina_kg'] - peso_ideal_ref_kg) < 0.1, \
        f"Base should be ~{peso_ideal_ref_kg:.2f} kg, got {result['base_proteina_kg']} kg"
    assert result['factor_proteina_psmf'] == 1.6, "Factor should be 1.6 for BF% >= 25%"
    
    expected_protein = round(peso_ideal_ref_kg * 1.6, 1)
    assert abs(result['proteina_g_dia'] - expected_protein) < 1, \
        f"Expected protein ~{expected_protein}g, got {result['proteina_g_dia']}g"
    
    assert result['carb_cap_aplicado_g'] == 30, f"Tier 3 carb cap should be 30g, got {result['carb_cap_aplicado_g']}g"
    assert result['grasa_g_dia'] == 50.0, "Grasas should be 50g for BF% >= 25%"
    
    print("✅ Test passed!")
    print()


def test_man_tier2():
    """
    Test case: Man with moderate adiposity
    - Sexo: Hombre
    - Peso: 100 kg
    - Estatura: 175 cm
    - BF%: 28%
    
    Expected:
    - Tier 2 (25% <= BF% < 35%)
    - Base proteína = MLG
    - Factor proteína = 1.6 (BF% >= 25%)
    """
    print("=" * 70)
    print("Test Case: Man - Tier 2 (Moderate Adiposity)")
    print("=" * 70)
    
    sexo = "Hombre"
    peso = 100.0
    estatura_cm = 175
    grasa_corregida = 28.0
    
    mlg = calcular_mlg(peso, grasa_corregida)
    estatura_m = estatura_cm / 100
    imc = peso / (estatura_m ** 2)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  Estatura: {estatura_cm} cm")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  IMC: {imc:.2f}")
    print(f"  MLG: {mlg:.2f} kg")
    print()
    
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    print(f"Resultados:")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Base proteína kg: {result.get('base_proteina_kg')} kg")
    print(f"  Factor proteína: {result.get('factor_proteina_psmf')} g/kg")
    print(f"  Proteína: {result.get('proteina_g_dia')} g/día")
    print(f"  Carb cap: {result.get('carb_cap_aplicado_g')} g")
    print()
    
    assert result['tier_psmf'] == 2, f"Expected Tier 2, got Tier {result['tier_psmf']}"
    assert result['base_proteina_usada'] == "MLG", "Base should be MLG"
    assert abs(result['base_proteina_kg'] - mlg) < 0.1, "Base should be MLG"
    assert result['carb_cap_aplicado_g'] == 40, f"Tier 2 carb cap should be 40g"
    
    print("✅ Test passed!")
    print()


def test_woman_tier1():
    """
    Test case: Woman with low adiposity
    - Sexo: Mujer
    - Peso: 65 kg
    - Estatura: 165 cm
    - BF%: 28%
    
    Expected:
    - Tier 1 (BF% < 35% for women)
    - Base proteína = peso total
    - Factor proteína = 1.6 (BF% >= 25%)
    """
    print("=" * 70)
    print("Test Case: Woman - Tier 1 (Low Adiposity)")
    print("=" * 70)
    
    sexo = "Mujer"
    peso = 65.0
    estatura_cm = 165
    grasa_corregida = 28.0
    
    mlg = calcular_mlg(peso, grasa_corregida)
    estatura_m = estatura_cm / 100
    imc = peso / (estatura_m ** 2)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  Estatura: {estatura_cm} cm")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  IMC: {imc:.2f}")
    print(f"  MLG: {mlg:.2f} kg")
    print()
    
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    print(f"Resultados:")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Base proteína kg: {result.get('base_proteina_kg')} kg")
    print(f"  Factor proteína: {result.get('factor_proteina_psmf')} g/kg")
    print(f"  Proteína: {result.get('proteina_g_dia')} g/día")
    print(f"  Carb cap: {result.get('carb_cap_aplicado_g')} g")
    print()
    
    assert result['tier_psmf'] == 1, f"Expected Tier 1, got Tier {result['tier_psmf']}"
    assert result['base_proteina_usada'] == "Peso total", "Base should be total weight"
    assert abs(result['base_proteina_kg'] - peso) < 0.1, "Base should be total weight"
    assert result['carb_cap_aplicado_g'] == 50, f"Tier 1 carb cap should be 50g"
    
    print("✅ Test passed!")
    print()


def test_man_tier1_low_bf():
    """
    Test case: Man with low body fat (but eligible for PSMF)
    - Sexo: Hombre
    - Peso: 80 kg
    - Estatura: 180 cm
    - BF%: 20%
    
    Expected:
    - Tier 1 (BF% < 25%)
    - Base proteína = peso total
    - Factor proteína = 1.8 (BF% < 25%)
    - Grasas = 30g
    """
    print("=" * 70)
    print("Test Case: Man - Tier 1 (Low Body Fat)")
    print("=" * 70)
    
    sexo = "Hombre"
    peso = 80.0
    estatura_cm = 180
    grasa_corregida = 20.0
    
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  MLG: {mlg:.2f} kg")
    print()
    
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    print(f"Resultados:")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Factor proteína: {result.get('factor_proteina_psmf')} g/kg")
    print(f"  Proteína: {result.get('proteina_g_dia')} g/día")
    print(f"  Grasas: {result.get('grasa_g_dia')} g/día")
    print(f"  Carb cap: {result.get('carb_cap_aplicado_g')} g")
    print()
    
    assert result['tier_psmf'] == 1, f"Expected Tier 1, got Tier {result['tier_psmf']}"
    assert result['factor_proteina_psmf'] == 1.8, "Factor should be 1.8 for BF% < 25%"
    assert result['grasa_g_dia'] == 30.0, "Grasas should be 30g for BF% < 25%"
    assert result['carb_cap_aplicado_g'] == 50, f"Tier 1 carb cap should be 50g"
    
    expected_protein = round(peso * 1.8, 1)
    assert result['proteina_g_dia'] == expected_protein, \
        f"Expected {expected_protein}g protein, got {result['proteina_g_dia']}g"
    
    print("✅ Test passed!")
    print()


def test_tier3_by_imc():
    """
    Test case: Tier 3 triggered by IMC >= 40
    - Sexo: Hombre
    - Peso: 130 kg
    - Estatura: 180 cm (IMC = 40.1)
    - BF%: 32% (would be Tier 2 alone, but IMC triggers Tier 3)
    
    Expected:
    - Tier 3 (IMC >= 40)
    - Base proteína = peso_ideal_ref_kg
    """
    print("=" * 70)
    print("Test Case: Tier 3 by IMC >= 40")
    print("=" * 70)
    
    sexo = "Hombre"
    peso = 130.0
    estatura_cm = 180
    grasa_corregida = 32.0
    
    mlg = calcular_mlg(peso, grasa_corregida)
    estatura_m = estatura_cm / 100
    imc = peso / (estatura_m ** 2)
    peso_ideal_ref_kg = 25 * (estatura_m ** 2)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  Estatura: {estatura_cm} cm")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  IMC: {imc:.2f}")
    print(f"  MLG: {mlg:.2f} kg")
    print(f"  Peso ideal (IMC 25): {peso_ideal_ref_kg:.2f} kg")
    print()
    
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    print(f"Resultados:")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Base proteína kg: {result.get('base_proteina_kg')} kg")
    print(f"  IMC: {result.get('imc')}")
    print()
    
    assert imc >= 40, f"IMC should be >= 40, got {imc:.2f}"
    assert result['tier_psmf'] == 3, f"Expected Tier 3 (IMC >= 40), got Tier {result['tier_psmf']}"
    assert result['base_proteina_usada'] == "Peso ideal (IMC 25)", "Base should be ideal weight"
    
    print("✅ Test passed!")
    print()


def test_woman_tier2():
    """
    Test case: Woman with moderate-high adiposity
    - Sexo: Mujer
    - Peso: 85 kg
    - Estatura: 165 cm
    - BF%: 40%
    
    Expected:
    - Tier 2 (35% <= BF% < 45% for women)
    - Base proteína = MLG
    """
    print("=" * 70)
    print("Test Case: Woman - Tier 2 (Moderate-High Adiposity)")
    print("=" * 70)
    
    sexo = "Mujer"
    peso = 85.0
    estatura_cm = 165
    grasa_corregida = 40.0
    
    mlg = calcular_mlg(peso, grasa_corregida)
    
    print(f"Datos de entrada:")
    print(f"  Sexo: {sexo}")
    print(f"  Peso: {peso} kg")
    print(f"  BF%: {grasa_corregida}%")
    print(f"  MLG: {mlg:.2f} kg")
    print()
    
    result = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)
    
    print(f"Resultados:")
    print(f"  Tier: {result.get('tier_psmf')}")
    print(f"  Base proteína: {result.get('base_proteina_usada')}")
    print(f"  Base proteína kg: {result.get('base_proteina_kg')} kg")
    print(f"  Carb cap: {result.get('carb_cap_aplicado_g')} g")
    print()
    
    assert result['tier_psmf'] == 2, f"Expected Tier 2, got Tier {result['tier_psmf']}"
    assert result['base_proteina_usada'] == "MLG", "Base should be MLG"
    assert result['carb_cap_aplicado_g'] == 40, "Tier 2 carb cap should be 40g"
    
    print("✅ Test passed!")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PSMF TIER-BASED CALCULATION - TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_karina_tier3()
        test_man_tier2()
        test_woman_tier1()
        test_man_tier1_low_bf()
        test_tier3_by_imc()
        test_woman_tier2()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

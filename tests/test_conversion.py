"""
Tests for body fat conversion and PSMF/traditional plan calculations.
Uses standalone function implementations to avoid streamlit module-level execution.
"""
import sys
import os

# Add parent directory to path to import from streamlit_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

# ==================== CONSTANTS FROM streamlit_app.py ====================
MAX_EXTRAPOLATE = 60.0
AUTO_EXTRAPOLATE_THRESHOLD = 45.0
SLOPE_LAST_SEGMENT = 1.0
PSMF_LBM_THRESHOLD = {'Hombre': 35.0, 'Mujer': 40.0}
PROTEIN_FACTOR_PSMF_LBM = 1.8
PROTEIN_FACTOR_TRAD_LBM = 1.6
CARB_MIN_G = 50.0
FAT_FLOOR_G = 20.0
TEI_MIN = {'Hombre': 1400, 'Mujer': 1200}
MAX_DEFICIT = 0.35


# ==================== STANDALONE FUNCTION IMPLEMENTATIONS ====================
def corregir_porcentaje_grasa_standalone(medido, metodo, sexo):
    """
    Standalone version of corregir_porcentaje_grasa for testing.
    Does not use streamlit session_state.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        # Tablas especializadas por sexo para conversion Omron→DEXA
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
        
        # Convertir tabla a listas ordenadas para interpolacion
        omron_values = sorted(tabla.keys())
        dexa_values = [tabla[k] for k in omron_values]
        
        min_omron = min(omron_values)
        max_omron = max(omron_values)  # max_omron = 40
        base_at_40 = tabla[max_omron]  # Valor DEXA para Omron=40
        
        # Si esta dentro del rango de la tabla (<=40), interpolar
        if min_omron <= medido <= max_omron:
            # Usar numpy.interp para interpolacion lineal
            resultado = float(np.interp(medido, omron_values, dexa_values))
            return resultado
        
        # Si esta por debajo del minimo, usar valor minimo de la tabla
        elif medido < min_omron:
            return tabla[min_omron]
        
        # Si esta por encima del maximo de la tabla (medido > 40)
        else:
            # Rango 40 < medido < 45: truncar conservador
            if 40.0 < medido < AUTO_EXTRAPOLATE_THRESHOLD:
                # Truncar al valor de Omron=40 (conservador)
                resultado = base_at_40
                return resultado
            
            # medido >= 45.0: extrapolacion automatica
            else:
                # Usar slope determinista = 1.0 (1% DEXA por 1 unidad Omron)
                slope = SLOPE_LAST_SEGMENT
                
                # Extrapolar desde Omron=40
                extrapolated = base_at_40 + slope * (medido - max_omron)
                
                # Limitar al cap maximo
                result = min(extrapolated, MAX_EXTRAPOLATE)
                
                return float(result)
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02)
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor)
    else:  # DEXA (Gold Standard) u otros
        return float(medido)


def calcular_mlg(peso, porcentaje_grasa):
    """Calcula la Masa Libre de Grasa."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def calculate_psmf_standalone(sexo, peso, grasa_corregida, mlg):
    """
    Standalone version of calculate_psmf for testing.
    Does not use streamlit session_state.
    """
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
        mlg = 56.0
    
    # Determinar elegibilidad para PSMF segun sexo y % grasa
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
        # Determinar si usar LBM en lugar de peso total
        use_lbm = False
        
        if sexo == "Hombre" and grasa_corregida >= PSMF_LBM_THRESHOLD['Hombre']:
            use_lbm = True
        elif sexo == "Mujer" and grasa_corregida >= PSMF_LBM_THRESHOLD['Mujer']:
            use_lbm = True
        
        # PROTEINA Y GRASAS: Asignacion automatica segun % grasa corporal corregida
        if use_lbm:
            # Usar LBM para calculo de proteina
            proteina_g_dia = round(mlg * PROTEIN_FACTOR_PSMF_LBM, 1)
            # Grasas segun protocolo existente
            grasa_g_dia = 50.0 if grasa_corregida >= 25 else 30.0
        else:
            # Protocolo original basado en peso total
            if grasa_corregida < 25:
                proteina_g_dia = round(peso * 1.8, 1)
                grasa_g_dia = 30.0
            else:
                proteina_g_dia = round(peso * 1.6, 1)
                grasa_g_dia = 50.0
        
        # MULTIPLICADOR CALORICO segun % grasa corporal
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
            perfil_grasa = "mas magro (abdominales visibles)"
        
        # CALORIAS = proteina (g) × multiplicador
        calorias_dia = round(proteina_g_dia * multiplicador, 0)
        
        # Verificar que no este por debajo del piso minimo
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        # Calcular rango de perdida semanal proyectada
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
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Nuevo protocolo: {perfil_grasa}",
            "lbm_based": use_lbm
        }
    else:
        return {"psmf_aplicable": False}


# ==================== TESTS ====================
def test_omron_interpolation_normal_range():
    """Test Omron interpolation for values within calibration range (<=40)."""
    print("\n=== Test: Omron Interpolation (Normal Range) ===")
    
    # Test case 1: Omron = 39 (within range, should interpolate)
    result = corregir_porcentaje_grasa_standalone(39, "Omron HBF-516 (BIA)", "Hombre")
    print(f"Omron 39% (Hombre): {result:.1f}% DEXA")
    assert 44.0 < result < 45.0, f"Expected ~44.3, got {result}"
    
    # Test case 2: Omron = 40 (exact match in table)
    result = corregir_porcentaje_grasa_standalone(40, "Omron HBF-516 (BIA)", "Hombre")
    print(f"Omron 40% (Hombre): {result:.1f}% DEXA")
    assert abs(result - 45.3) < 0.1, f"Expected 45.3, got {result}"
    
    # Test case 3: Omron = 39 for woman
    result = corregir_porcentaje_grasa_standalone(39, "Omron HBF-516 (BIA)", "Mujer")
    print(f"Omron 39% (Mujer): {result:.1f}% DEXA")
    assert 43.0 < result < 45.0, f"Expected ~43.7, got {result}"
    
    print("✓ Normal range interpolation tests passed")


def test_omron_truncation_gray_zone():
    """Test Omron truncation for values in gray zone (40 < value < 45)."""
    print("\n=== Test: Omron Truncation (Gray Zone 40-45) ===")
    
    # Test case: Omron = 43 (should truncate to value at 40)
    result = corregir_porcentaje_grasa_standalone(43, "Omron HBF-516 (BIA)", "Hombre")
    print(f"Omron 43% (Hombre): {result:.1f}% DEXA (truncated)")
    assert abs(result - 45.3) < 0.1, f"Expected 45.3 (truncated), got {result}"
    
    # Test case: Omron = 44.9 (still in gray zone)
    result = corregir_porcentaje_grasa_standalone(44.9, "Omron HBF-516 (BIA)", "Mujer")
    print(f"Omron 44.9% (Mujer): {result:.1f}% DEXA (truncated)")
    assert abs(result - 44.7) < 0.1, f"Expected 44.7 (truncated), got {result}"
    
    print("✓ Gray zone truncation tests passed")


def test_omron_auto_extrapolation():
    """Test Omron auto-extrapolation for values >= 45."""
    print("\n=== Test: Omron Auto-Extrapolation (>=45) ===")
    
    # Test case 1: Omron = 45 (exactly at threshold, should auto-extrapolate)
    result = corregir_porcentaje_grasa_standalone(45, "Omron HBF-516 (BIA)", "Hombre")
    print(f"Omron 45% (Hombre): {result:.1f}% DEXA (auto-extrapolated)")
    # Expected: 45.3 + 1.0 * (45 - 40) = 45.3 + 5 = 50.3
    assert abs(result - 50.3) < 0.1, f"Expected 50.3, got {result}"
    
    # Test case 2: Omron = 58.5 (high value, should cap at MAX_EXTRAPOLATE=60)
    result = corregir_porcentaje_grasa_standalone(58.5, "Omron HBF-516 (BIA)", "Hombre")
    print(f"Omron 58.5% (Hombre): {result:.1f}% DEXA (capped at 60%)")
    # Expected: 45.3 + 1.0 * (58.5 - 40) = 45.3 + 18.5 = 63.8, but capped at 60
    assert abs(result - 60.0) < 0.1, f"Expected 60.0 (capped), got {result}"
    
    # Test case 3: Omron = 50 for woman
    result = corregir_porcentaje_grasa_standalone(50, "Omron HBF-516 (BIA)", "Mujer")
    print(f"Omron 50% (Mujer): {result:.1f}% DEXA (auto-extrapolated)")
    # Expected: 44.7 + 1.0 * (50 - 40) = 44.7 + 10 = 54.7
    assert abs(result - 54.7) < 0.1, f"Expected 54.7, got {result}"
    
    print("✓ Auto-extrapolation tests passed")


def test_psmf_lbm_based_high_adiposity():
    """Test PSMF calculation uses LBM for high adiposity cases."""
    print("\n=== Test: PSMF LBM-based (High Adiposity) ===")
    
    # Test case: Woman with 52.8% body fat (InBody), 140kg, ~66kg LBM
    peso = 140.0
    grasa_corregida = 52.8  # Already corrected (InBody 270)
    mlg = calcular_mlg(peso, grasa_corregida)  # ~66 kg
    
    print(f"Woman: {peso}kg, {grasa_corregida:.1f}% fat, {mlg:.1f}kg LBM")
    
    result = calculate_psmf_standalone("Mujer", peso, grasa_corregida, mlg)
    
    assert result["psmf_aplicable"], "PSMF should be applicable"
    assert result["lbm_based"], "Should use LBM-based calculation"
    
    # Expected protein: 66 kg LBM * 1.8 = 118.8 g
    expected_protein = round(mlg * PROTEIN_FACTOR_PSMF_LBM, 1)
    print(f"Protein: {result['proteina_g_dia']}g/day (expected {expected_protein}g)")
    assert abs(result['proteina_g_dia'] - expected_protein) < 0.5, \
        f"Expected ~{expected_protein}g protein, got {result['proteina_g_dia']}g"
    
    # Should use high fat (>=25% body fat)
    assert result['grasa_g_dia'] == 50.0, f"Expected 50g fat, got {result['grasa_g_dia']}g"
    
    # Should use low multiplier (>35% body fat)
    assert result['multiplicador'] == 8.3, f"Expected multiplier 8.3, got {result['multiplicador']}"
    
    print(f"Calories: {result['calorias_dia']}kcal/day")
    print(f"Fat: {result['grasa_g_dia']}g/day")
    print(f"Multiplier: {result['multiplicador']} ({result['perfil_grasa']})")
    print("✓ PSMF LBM-based test passed")


def test_psmf_normal_case():
    """Test PSMF calculation for normal case (not LBM-based)."""
    print("\n=== Test: PSMF Normal Case (Weight-based) ===")
    
    # Test case: Man with 28% body fat (should use weight-based, not LBM)
    peso = 90.0
    grasa_corregida = 28.0
    mlg = calcular_mlg(peso, grasa_corregida)  # ~65 kg
    
    print(f"Man: {peso}kg, {grasa_corregida:.1f}% fat, {mlg:.1f}kg LBM")
    
    result = calculate_psmf_standalone("Hombre", peso, grasa_corregida, mlg)
    
    assert result["psmf_aplicable"], "PSMF should be applicable"
    assert not result["lbm_based"], "Should NOT use LBM-based calculation"
    
    # Expected protein: 90 kg * 1.6 = 144 g (>=25% body fat)
    expected_protein = round(peso * 1.6, 1)
    print(f"Protein: {result['proteina_g_dia']}g/day (expected {expected_protein}g)")
    assert abs(result['proteina_g_dia'] - expected_protein) < 0.5, \
        f"Expected ~{expected_protein}g protein, got {result['proteina_g_dia']}g"
    
    print("✓ PSMF normal case test passed")


def test_extreme_case_thresholds():
    """Test that extreme case thresholds work correctly."""
    print("\n=== Test: Extreme Case Detection ===")
    
    # Test case 1: Man with exactly 35% body fat (threshold)
    peso = 100.0
    grasa_corregida = 35.0
    mlg = calcular_mlg(peso, grasa_corregida)
    
    result = calculate_psmf_standalone("Hombre", peso, grasa_corregida, mlg)
    print(f"Man at 35% threshold: LBM-based = {result['lbm_based']}")
    assert result["lbm_based"], "Should use LBM at threshold (>=35%)"
    
    # Test case 2: Man just below threshold (34.9%)
    grasa_corregida = 34.9
    mlg = calcular_mlg(peso, grasa_corregida)
    
    result = calculate_psmf_standalone("Hombre", peso, grasa_corregida, mlg)
    print(f"Man at 34.9% (below threshold): LBM-based = {result['lbm_based']}")
    assert not result["lbm_based"], "Should NOT use LBM below threshold (<35%)"
    
    # Test case 3: Woman with exactly 40% body fat (threshold)
    grasa_corregida = 40.0
    mlg = calcular_mlg(peso, grasa_corregida)
    
    result = calculate_psmf_standalone("Mujer", peso, grasa_corregida, mlg)
    print(f"Woman at 40% threshold: LBM-based = {result['lbm_based']}")
    assert result["lbm_based"], "Should use LBM at threshold (>=40%)"
    
    print("✓ Extreme case threshold tests passed")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*60)
    print("RUNNING ALL TESTS FOR AUTO-EXTRAPOLATION AND LBM-BASED PSMF")
    print("="*60)
    
    try:
        test_omron_interpolation_normal_range()
        test_omron_truncation_gray_zone()
        test_omron_auto_extrapolation()
        test_psmf_lbm_based_high_adiposity()
        test_psmf_normal_case()
        test_extreme_case_thresholds()
        
        print("\n" + "="*60)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n✗✗✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗✗✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

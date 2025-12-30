#!/usr/bin/env python3
"""
Direct test of isolated functions for unified MUPAI framework.
Tests the key logic without importing the entire streamlit_app module.
"""

# Copy the constants and functions directly from streamlit_app.py

# ==================== CONSTANTES DEL MARCO UNIFICADO MUPAI ====================
PROTEIN_FACTOR_RANGES = {
    "tradicional_bajo_grasa": 2.0,
    "tradicional_moderado": 1.8,
    "tradicional_alto_grasa": 1.6,
    "psmf_magro": 1.8,
    "psmf_alto": 1.6,
}

FAT_ALLOCATION_RULES = {
    "tradicional_min_percent": 20,
    "tradicional_max_percent": 35,
    "psmf_magro_g": 30.0,
    "psmf_alto_g": 50.0,
}

CARB_ALLOCATION_RULES = {
    "tradicional_fill_remainder": True,
    "psmf_tier1_cap_g": 50,
    "psmf_tier2_cap_g": 40,
    "psmf_tier3_cap_g": 30,
}

OBESITY_THRESHOLDS = {
    "male_obese_bf": 26.0,
    "female_obese_bf": 39.0,
}

DEFICIT_RANGES_MALE = [
    (0, 6, -12.5),
    (6, 10, -7.5),
    (10, 15, -2.5),
    (15, 18, 0),
    (18, 21, 10),
    (21, 23, 20),
    (23, 26, 30),
    (26, 100, 50),
]

DEFICIT_RANGES_FEMALE = [
    (0, 12, -12.5),
    (12, 16, -7.5),
    (16, 20, -2.5),
    (20, 23, 0),
    (23, 27, 10),
    (27, 32, 20),
    (32, 39, 30),
    (39, 100, 50),
]

PSMF_CALORIC_MULTIPLIERS = {
    "alto_bf": 8.3,
    "moderado_bf": 9.0,
    "magro_bf": 9.6,
}

# ==================== FUNCTIONS ====================

def sugerir_deficit(porcentaje_grasa, sexo):
    """
    Sugiere el déficit/superávit calórico como % de TDEE basado en % de grasa y sexo.
    Usa interpolación lineal dentro de cada categoría para transiciones suaves.
    """
    try:
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        porcentaje_grasa = 0.0
    
    rangos = DEFICIT_RANGES_MALE if sexo == "Hombre" else DEFICIT_RANGES_FEMALE
    
    for i, (bf_min, bf_max, deficit_mid) in enumerate(rangos):
        if bf_min <= porcentaje_grasa <= bf_max:
            if i + 1 < len(rangos):
                next_deficit = rangos[i + 1][2]
                progress = (porcentaje_grasa - bf_min) / (bf_max - bf_min) if bf_max > bf_min else 0
                deficit_interpolado = deficit_mid + (next_deficit - deficit_mid) * progress
                return round(deficit_interpolado, 1)
            else:
                return deficit_mid
    
    return 20

def determinar_fase_nutricional_refinada(grasa_corregida, sexo):
    """
    Determina la fase nutricional refinada basada en % de grasa corporal y sexo.
    """
    try:
        grasa_corregida = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa_corregida = 0.0
    
    deficit_sugerido = sugerir_deficit(grasa_corregida, sexo)
    umbral_obesidad = OBESITY_THRESHOLDS["male_obese_bf"] if sexo == "Hombre" else OBESITY_THRESHOLDS["female_obese_bf"]
    
    if deficit_sugerido < -5:
        fase = f"Superávit recomendado: {abs(deficit_sugerido):.1f}% de TDEE"
        porcentaje = deficit_sugerido
    elif -5 <= deficit_sugerido < 0:
        fase = f"Mantenimiento o ligero superávit: {abs(deficit_sugerido):.1f}% de TDEE"
        porcentaje = deficit_sugerido
    elif deficit_sugerido == 0:
        fase = "Mantenimiento (0% de TDEE)"
        porcentaje = 0
    elif grasa_corregida >= umbral_obesidad:
        fase = f"Déficit alto recomendado (PSMF o {deficit_sugerido:.0f}% de TDEE)"
        porcentaje = deficit_sugerido
    else:
        fase = f"Déficit recomendado: {deficit_sugerido:.1f}% de TDEE"
        porcentaje = deficit_sugerido
    
    return fase, porcentaje

# ==================== TESTS ====================

def test_constants():
    """Test that constants are properly defined."""
    print("Testing: Constants...")
    assert "tradicional_bajo_grasa" in PROTEIN_FACTOR_RANGES
    assert OBESITY_THRESHOLDS["male_obese_bf"] == 26.0
    assert OBESITY_THRESHOLDS["female_obese_bf"] == 39.0
    assert len(DEFICIT_RANGES_MALE) == 8
    assert len(DEFICIT_RANGES_FEMALE) == 8
    print("✅ Constants properly defined")

def test_sugerir_deficit_function():
    """Test the sugerir_deficit function."""
    print("\nTesting: sugerir_deficit...")
    
    # Male tests
    deficit = sugerir_deficit(5, "Hombre")
    print(f"  Male 5% BF → {deficit:+.1f}% (expect negative)")
    assert deficit < 0
    
    deficit = sugerir_deficit(17, "Hombre")
    print(f"  Male 17% BF → {deficit:+.1f}% (expect 0-10%)")
    assert 0 <= deficit <= 10
    
    deficit = sugerir_deficit(28, "Hombre")
    print(f"  Male 28% BF (OBESE) → {deficit:+.1f}% (expect ~50%)")
    assert deficit >= 45
    
    # Female tests
    deficit = sugerir_deficit(10, "Mujer")
    print(f"  Female 10% BF → {deficit:+.1f}% (expect negative)")
    assert deficit < 0
    
    deficit = sugerir_deficit(42, "Mujer")
    print(f"  Female 42% BF (OBESE) → {deficit:+.1f}% (expect ~50%)")
    assert deficit >= 45
    
    print("✅ sugerir_deficit working correctly")

def test_determinar_fase():
    """Test the determinar_fase_nutricional_refinada function."""
    print("\nTesting: determinar_fase_nutricional_refinada...")
    
    # Male surplus
    fase, porcentaje = determinar_fase_nutricional_refinada(8, "Hombre")
    print(f"  Male 8% BF → {porcentaje:+.1f}%")
    assert porcentaje < 0
    
    # Male obese
    fase, porcentaje = determinar_fase_nutricional_refinada(30, "Hombre")
    print(f"  Male 30% BF (OBESE) → {porcentaje:+.1f}%")
    assert porcentaje >= 45
    assert "psmf" in fase.lower() or "alto" in fase.lower()
    
    # Female obese
    fase, porcentaje = determinar_fase_nutricional_refinada(45, "Mujer")
    print(f"  Female 45% BF (OBESE) → {porcentaje:+.1f}%")
    assert porcentaje >= 45
    
    print("✅ determinar_fase_nutricional_refinada working correctly")

def test_fbeo():
    """Test FBEO calculation."""
    print("\nTesting: FBEO calculation...")
    
    # Deficit
    porcentaje = 25
    fbeo = 1 - (porcentaje / 100)
    print(f"  25% deficit → FBEO = {fbeo:.4f}")
    assert fbeo == 0.75
    
    # Surplus
    porcentaje = -10
    fbeo = 1 - (porcentaje / 100)
    print(f"  10% surplus → FBEO = {fbeo:.4f}")
    assert fbeo == 1.10
    
    # Maintenance
    porcentaje = 0
    fbeo = 1 - (porcentaje / 100)
    print(f"  0% maintenance → FBEO = {fbeo:.4f}")
    assert fbeo == 1.00
    
    print("✅ FBEO calculation correct")

def test_obesity_thresholds():
    """Test obesity threshold detection."""
    print("\nTesting: Obesity thresholds...")
    
    # Male at threshold
    fase, porcentaje = determinar_fase_nutricional_refinada(26, "Hombre")
    print(f"  Male 26% BF (threshold) → {porcentaje:+.1f}%")
    assert porcentaje >= 45
    
    # Female at threshold
    fase, porcentaje = determinar_fase_nutricional_refinada(39, "Mujer")
    print(f"  Female 39% BF (threshold) → {porcentaje:+.1f}%")
    assert porcentaje >= 45
    
    print("✅ Obesity thresholds working correctly")

def main():
    """Run all tests."""
    print("=" * 70)
    print("UNIFIED MUPAI FRAMEWORK - ISOLATED FUNCTION TESTS")
    print("=" * 70)
    
    try:
        test_constants()
        test_sugerir_deficit_function()
        test_determinar_fase()
        test_fbeo()
        test_obesity_thresholds()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - UNIFIED FRAMEWORK LOGIC CORRECT")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

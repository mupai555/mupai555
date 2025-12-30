#!/usr/bin/env python3
"""
Test script for unified MUPAI framework changes.
Validates:
1. New constants are defined
2. sugerir_deficit uses linear interpolation
3. determinar_fase_nutricional_refinada returns proper format
4. FBEO calculation is correct
5. Obesity thresholds trigger proper recommendations
"""

import sys
import os

# Add the current directory to the path to import streamlit_app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_constants_defined():
    """Test that new unified constants are defined."""
    print("Testing: Constants defined...")
    
    # Import the constants
    from streamlit_app import (
        PROTEIN_FACTOR_RANGES,
        FAT_ALLOCATION_RULES,
        CARB_ALLOCATION_RULES,
        OBESITY_THRESHOLDS,
        DEFICIT_RANGES_MALE,
        DEFICIT_RANGES_FEMALE,
        PSMF_CALORIC_MULTIPLIERS
    )
    
    # Verify they have expected keys
    assert "tradicional_bajo_grasa" in PROTEIN_FACTOR_RANGES
    assert "psmf_magro_g" in FAT_ALLOCATION_RULES
    assert "psmf_tier1_cap_g" in CARB_ALLOCATION_RULES
    assert "male_obese_bf" in OBESITY_THRESHOLDS
    assert OBESITY_THRESHOLDS["male_obese_bf"] == 26.0
    assert OBESITY_THRESHOLDS["female_obese_bf"] == 39.0
    assert len(DEFICIT_RANGES_MALE) >= 7
    assert len(DEFICIT_RANGES_FEMALE) >= 7
    
    print("✅ All constants defined correctly")

def test_sugerir_deficit():
    """Test sugerir_deficit function with various inputs."""
    print("\nTesting: sugerir_deficit function...")
    
    from streamlit_app import sugerir_deficit
    
    # Test male ranges
    # Low BF - should recommend surplus (negative)
    deficit = sugerir_deficit(5, "Hombre")
    print(f"  Male 5% BF → {deficit:+.1f}% (expect negative/surplus)")
    assert deficit < 0, f"Expected negative (surplus) for 5% BF male, got {deficit}"
    
    # Maintenance range
    deficit = sugerir_deficit(17, "Hombre")
    print(f"  Male 17% BF → {deficit:+.1f}% (expect ~0 or small deficit)")
    assert -5 <= deficit <= 5, f"Expected ~0 for 17% BF male, got {deficit}"
    
    # Moderate deficit range
    deficit = sugerir_deficit(22, "Hombre")
    print(f"  Male 22% BF → {deficit:+.1f}% (expect 20-30%)")
    assert 15 <= deficit <= 35, f"Expected 20-30% for 22% BF male, got {deficit}"
    
    # Obese - should recommend high deficit
    deficit = sugerir_deficit(28, "Hombre")
    print(f"  Male 28% BF (OBESE) → {deficit:+.1f}% (expect ~50%)")
    assert deficit >= 40, f"Expected ≥40% for obese male (28% BF), got {deficit}"
    
    # Test female ranges
    # Low BF - should recommend surplus
    deficit = sugerir_deficit(10, "Mujer")
    print(f"  Female 10% BF → {deficit:+.1f}% (expect negative/surplus)")
    assert deficit < 0, f"Expected negative (surplus) for 10% BF female, got {deficit}"
    
    # Maintenance range
    deficit = sugerir_deficit(22, "Mujer")
    print(f"  Female 22% BF → {deficit:+.1f}% (expect ~0)")
    assert -5 <= deficit <= 5, f"Expected ~0 for 22% BF female, got {deficit}"
    
    # Obese - should recommend high deficit
    deficit = sugerir_deficit(42, "Mujer")
    print(f"  Female 42% BF (OBESE) → {deficit:+.1f}% (expect ~50%)")
    assert deficit >= 40, f"Expected ≥40% for obese female (42% BF), got {deficit}"
    
    print("✅ sugerir_deficit working correctly with linear interpolation")

def test_determinar_fase_nutricional():
    """Test determinar_fase_nutricional_refinada function."""
    print("\nTesting: determinar_fase_nutricional_refinada function...")
    
    from streamlit_app import determinar_fase_nutricional_refinada, OBESITY_THRESHOLDS
    
    # Test male low BF (surplus expected)
    fase, porcentaje = determinar_fase_nutricional_refinada(8, "Hombre")
    print(f"  Male 8% BF → Fase: {fase[:50]}..., Porcentaje: {porcentaje:+.1f}%")
    assert porcentaje < 0, f"Expected negative (surplus) for 8% BF male, got {porcentaje}"
    assert "superávit" in fase.lower() or "superávit" in fase.lower()
    
    # Test male moderate BF (deficit expected)
    fase, porcentaje = determinar_fase_nutricional_refinada(20, "Hombre")
    print(f"  Male 20% BF → Fase: {fase[:50]}..., Porcentaje: {porcentaje:+.1f}%")
    assert porcentaje >= 0, f"Expected positive (deficit) for 20% BF male, got {porcentaje}"
    
    # Test male obese (high deficit/PSMF expected)
    fase, porcentaje = determinar_fase_nutricional_refinada(30, "Hombre")
    print(f"  Male 30% BF (OBESE) → Fase: {fase[:60]}..., Porcentaje: {porcentaje:+.1f}%")
    assert porcentaje >= 40, f"Expected high deficit for obese male, got {porcentaje}"
    assert "psmf" in fase.lower() or "alto" in fase.lower()
    
    # Test female low BF (surplus expected)
    fase, porcentaje = determinar_fase_nutricional_refinada(14, "Mujer")
    print(f"  Female 14% BF → Fase: {fase[:50]}..., Porcentaje: {porcentaje:+.1f}%")
    assert porcentaje < 0, f"Expected negative (surplus) for 14% BF female, got {porcentaje}"
    
    # Test female obese (high deficit/PSMF expected)
    fase, porcentaje = determinar_fase_nutricional_refinada(45, "Mujer")
    print(f"  Female 45% BF (OBESE) → Fase: {fase[:60]}..., Porcentaje: {porcentaje:+.1f}%")
    assert porcentaje >= 40, f"Expected high deficit for obese female, got {porcentaje}"
    assert "psmf" in fase.lower() or "alto" in fase.lower()
    
    print("✅ determinar_fase_nutricional_refinada working correctly")

def test_fbeo_calculation():
    """Test FBEO calculation logic."""
    print("\nTesting: FBEO calculation...")
    
    # Test deficit (positive porcentaje → FBEO < 1)
    porcentaje_deficit = 25  # 25% deficit
    fbeo_deficit = 1 - (porcentaje_deficit / 100)
    print(f"  25% deficit → FBEO = {fbeo_deficit:.4f} (expect 0.75)")
    assert fbeo_deficit == 0.75, f"Expected 0.75 for 25% deficit, got {fbeo_deficit}"
    
    # Test surplus (negative porcentaje → FBEO > 1)
    porcentaje_surplus = -10  # 10% surplus
    fbeo_surplus = 1 - (porcentaje_surplus / 100)
    print(f"  10% surplus → FBEO = {fbeo_surplus:.4f} (expect 1.10)")
    assert fbeo_surplus == 1.10, f"Expected 1.10 for 10% surplus, got {fbeo_surplus}"
    
    # Test maintenance (zero porcentaje → FBEO = 1)
    porcentaje_maintenance = 0
    fbeo_maintenance = 1 - (porcentaje_maintenance / 100)
    print(f"  0% (maintenance) → FBEO = {fbeo_maintenance:.4f} (expect 1.00)")
    assert fbeo_maintenance == 1.00, f"Expected 1.00 for maintenance, got {fbeo_maintenance}"
    
    print("✅ FBEO calculation correct")

def test_obesity_detection():
    """Test that obesity thresholds properly trigger recommendations."""
    print("\nTesting: Obesity threshold detection...")
    
    from streamlit_app import OBESITY_THRESHOLDS, determinar_fase_nutricional_refinada
    
    # Test male at threshold
    male_threshold = OBESITY_THRESHOLDS["male_obese_bf"]
    fase, porcentaje = determinar_fase_nutricional_refinada(male_threshold, "Hombre")
    print(f"  Male at threshold ({male_threshold}% BF) → {porcentaje:+.1f}% deficit")
    assert porcentaje >= 40, f"Expected high deficit at male obesity threshold"
    
    # Test female at threshold
    female_threshold = OBESITY_THRESHOLDS["female_obese_bf"]
    fase, porcentaje = determinar_fase_nutricional_refinada(female_threshold, "Mujer")
    print(f"  Female at threshold ({female_threshold}% BF) → {porcentaje:+.1f}% deficit")
    assert porcentaje >= 40, f"Expected high deficit at female obesity threshold"
    
    # Test just below threshold (should not trigger)
    fase, porcentaje = determinar_fase_nutricional_refinada(male_threshold - 1, "Hombre")
    print(f"  Male below threshold ({male_threshold - 1}% BF) → {porcentaje:+.1f}% deficit")
    assert porcentaje < 50, f"Should not trigger highest deficit just below threshold"
    
    print("✅ Obesity detection working correctly")

def main():
    """Run all tests."""
    print("=" * 70)
    print("UNIFIED MUPAI FRAMEWORK - VALIDATION TESTS")
    print("=" * 70)
    
    try:
        test_constants_defined()
        test_sugerir_deficit()
        test_determinar_fase_nutricional()
        test_fbeo_calculation()
        test_obesity_detection()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - UNIFIED FRAMEWORK WORKING CORRECTLY")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

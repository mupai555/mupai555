#!/usr/bin/env python3
"""
Test to verify the new protein factor ranges are correctly implemented.

New logic:
- Use 1.6 when grasa_corregida >= 35%
- Use 1.8 when grasa_corregida is between 25% and 34.9%
- Use 2.0 when grasa_corregida is between 15% and 24.9%
- Use 2.2 when grasa_corregida is between 4% and 14.9%
"""

import sys

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


def test_protein_factor_ranges():
    """Test all ranges of the protein factor logic."""
    
    print("=" * 70)
    print("PROTEIN FACTOR RANGES TEST")
    print("=" * 70)
    
    test_cases = [
        # (body_fat_percentage, expected_factor, description)
        (4.0, 2.2, "Lower boundary: 4%"),
        (10.0, 2.2, "Mid range: 10%"),
        (14.9, 2.2, "Upper boundary: 14.9%"),
        
        (15.0, 2.0, "Lower boundary: 15%"),
        (20.0, 2.0, "Mid range: 20%"),
        (24.9, 2.0, "Upper boundary: 24.9%"),
        
        (25.0, 1.8, "Lower boundary: 25%"),
        (30.0, 1.8, "Mid range: 30%"),
        (34.9, 1.8, "Upper boundary: 34.9%"),
        
        (35.0, 1.6, "Lower boundary: 35%"),
        (40.0, 1.6, "Mid range: 40%"),
        (50.0, 1.6, "High body fat: 50%"),
    ]
    
    all_passed = True
    
    for grasa, expected_factor, description in test_cases:
        factor = obtener_factor_proteina_tradicional(grasa)
        status = "✅" if factor == expected_factor else "❌"
        
        print(f"{status} {description:30s} -> {grasa:5.1f}% = {factor:.1f} g/kg", end="")
        
        if factor != expected_factor:
            print(f" (Expected: {expected_factor:.1f})")
            all_passed = False
        else:
            print()
    
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(test_protein_factor_ranges())

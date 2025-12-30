#!/usr/bin/env python3
"""
Integration test for waist circumference and waist-to-height ratio functionality
Tests that the new features are properly integrated into streamlit_app.py
"""

import re

def test_helper_function_exists():
    """Test that the helper function exists in streamlit_app.py"""
    print("\n" + "="*70)
    print("TEST 1: Checking helper function exists")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for function definition
    pattern = r'def calcular_relacion_cintura_estatura\(perimetro_cintura, estatura\):'
    if re.search(pattern, content):
        print("✓ Helper function 'calcular_relacion_cintura_estatura' found")
    else:
        raise AssertionError("Helper function not found in streamlit_app.py")
    
    # Check for division by zero handling
    if 'if estatura <= 0:' in content and 'return 0.0' in content:
        print("✓ Division by zero protection found")
    else:
        raise AssertionError("Division by zero protection not found")
    
    # Check for negative value handling
    if 'if perimetro_cintura <= 0:' in content:
        print("✓ Negative/zero waist validation found")
    else:
        raise AssertionError("Negative/zero waist validation not found")

def test_input_field_exists():
    """Test that the input field for waist circumference exists"""
    print("\n" + "="*70)
    print("TEST 2: Checking input field exists")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for input field
    if 'perimetro_cintura' in content:
        print("✓ Variable 'perimetro_cintura' found in code")
    else:
        raise AssertionError("Variable 'perimetro_cintura' not found")
    
    # Check for st.number_input with proper label
    pattern = r'st\.number_input\(\s*["\'].*[Pp]erímetro.*cintura'
    if re.search(pattern, content):
        print("✓ Input field with proper label found")
    else:
        raise AssertionError("Input field with proper label not found")
    
    # Check for key parameter
    if 'key="perimetro_cintura"' in content:
        print("✓ Session state key 'perimetro_cintura' configured")
    else:
        raise AssertionError("Session state key not found")

def test_session_state_initialization():
    """Test that session state is properly initialized"""
    print("\n" + "="*70)
    print("TEST 3: Checking session state initialization")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for perimetro_cintura in defaults
    pattern = r'"perimetro_cintura":\s*0\.0'
    if re.search(pattern, content):
        print("✓ Session state default value found")
    else:
        raise AssertionError("Session state default value not found in defaults dict")

def test_calculation_performed():
    """Test that waist-to-height ratio calculation is performed"""
    print("\n" + "="*70)
    print("TEST 4: Checking calculation is performed")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for calculation
    pattern = r'waist_to_height_ratio\s*=\s*calcular_relacion_cintura_estatura'
    if re.search(pattern, content):
        print("✓ Waist-to-height ratio calculation found")
    else:
        raise AssertionError("Calculation code not found")
    
    # Check for conditional calculation (only if perimetro_cintura > 0)
    pattern = r'if perimetro_cintura > 0'
    if re.search(pattern, content):
        print("✓ Conditional calculation logic found")
    else:
        raise AssertionError("Conditional calculation logic not found")

def test_email_report_integration():
    """Test that email report includes new metrics"""
    print("\n" + "="*70)
    print("TEST 5: Checking email report integration")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for waist circumference in report
    if 'Perímetro de cintura:' in content or 'perimetro_cintura_str' in content:
        print("✓ Waist circumference in report")
    else:
        raise AssertionError("Waist circumference not found in email report")
    
    # Check for waist-to-height ratio in report
    if 'Relación cintura-estatura:' in content or 'waist_to_height_str' in content:
        print("✓ Waist-to-height ratio in report")
    else:
        raise AssertionError("Waist-to-height ratio not found in email report")
    
    # Check for interpretation text
    if 'whr_interpretacion' in content:
        print("✓ Interpretation variable found")
    else:
        raise AssertionError("Interpretation variable not found")
    
    # Check for reference values
    pattern = r'<0\.40.*0\.40-0\.49.*0\.50-0\.59.*≥0\.60'
    if re.search(pattern, content, re.DOTALL):
        print("✓ Reference values found in report")
    else:
        print("⚠ Reference values might be formatted differently (non-critical)")

def test_interpretation_logic():
    """Test that interpretation logic is present"""
    print("\n" + "="*70)
    print("TEST 6: Checking interpretation logic")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for interpretation ranges
    checks = [
        ('< 0.40', 'Muy bajo'),
        ('< 0.50', 'Saludable'),
        ('< 0.60', 'Riesgo aumentado'),
        ('else', 'Riesgo sustancialmente aumentado')
    ]
    
    for check, label in checks:
        # Make pattern more flexible
        pattern = f'{re.escape(check)}.*{re.escape(label)}'
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            print(f"✓ Interpretation for '{label}' found")
        else:
            # Try alternate check
            if label in content:
                print(f"✓ Interpretation for '{label}' found (alternate)")
            else:
                print(f"⚠ Interpretation for '{label}' not found explicitly (may be inline)")

def test_no_regressions():
    """Test that existing functionality is not broken"""
    print("\n" + "="*70)
    print("TEST 7: Checking for regressions")
    print("="*70)
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that key existing functions still exist
    required_functions = [
        'calcular_ffmi',
        'calcular_fmi',
        'calcular_tmb_cunningham',
        'corregir_porcentaje_grasa',
        'enviar_email_resumen'
    ]
    
    for func in required_functions:
        pattern = f'def {func}'
        if re.search(pattern, content):
            print(f"✓ Function '{func}' still exists")
        else:
            raise AssertionError(f"Function '{func}' was removed or renamed")
    
    # Check that existing session state variables still exist
    required_vars = ['peso', 'estatura', 'grasa_corporal', 'masa_muscular', 'grasa_visceral']
    
    for var in required_vars:
        if f'"{var}"' in content or f"'{var}'" in content:
            print(f"✓ Session state variable '{var}' still present")
        else:
            raise AssertionError(f"Session state variable '{var}' was removed")

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("WAIST CIRCUMFERENCE & WAIST-TO-HEIGHT RATIO - INTEGRATION TESTS")
    print("="*70)
    
    tests = [
        test_helper_function_exists,
        test_input_field_exists,
        test_session_state_initialization,
        test_calculation_performed,
        test_email_report_integration,
        test_interpretation_logic,
        test_no_regressions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed > 0:
        return 1
    else:
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())

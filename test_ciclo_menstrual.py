#!/usr/bin/env python3
"""
Test script to verify menstrual cycle question implementation.
Tests that the question appears only for women and data is properly stored.
"""

import sys
import re

def test_function_exists():
    """Test that formulario_ciclo_menstrual function exists."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def formulario_ciclo_menstrual(' in content:
        print("✅ formulario_ciclo_menstrual() function exists")
        return True
    else:
        print("❌ formulario_ciclo_menstrual() function NOT found")
        return False

def test_function_called():
    """Test that formulario_ciclo_menstrual is called in the main flow."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'ciclo_menstrual = formulario_ciclo_menstrual(sexo)' in content:
        print("✅ formulario_ciclo_menstrual() is called with sexo parameter")
        return True
    else:
        print("❌ formulario_ciclo_menstrual() call NOT found")
        return False

def test_menstrual_cycle_options():
    """Test that menstrual cycle options are correctly defined."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_options = [
        "Menstruación",
        "Fase folicular",
        "Ovulación",
        "Fase lútea",
        "Menopausia/Ausencia de ovulación"
    ]
    
    all_found = True
    for option in required_options:
        if option in content:
            print(f"✅ Option '{option}' found")
        else:
            print(f"❌ Option '{option}' NOT found")
            all_found = False
    
    return all_found

def test_session_state_storage():
    """Test that menstrual cycle data is stored in session state."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("st.session_state.ciclo_menstrual", "session state variable"),
        ("st.session_state.ciclo_menstrual_completado", "completion flag")
    ]
    
    all_found = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description} ({check}) found")
        else:
            print(f"❌ {description} ({check}) NOT found")
            all_found = False
    
    return all_found

def test_email_integration():
    """Test that menstrual cycle is included in email report."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check function signature update
    if 'ciclo_menstrual=None' in content and 'def enviar_email_parte2(' in content:
        print("✅ enviar_email_parte2() function signature includes ciclo_menstrual parameter")
    else:
        print("❌ enviar_email_parte2() function signature NOT updated")
        return False
    
    # Check email content includes menstrual cycle
    if 'Fase del ciclo menstrual' in content:
        print("✅ Email content includes menstrual cycle information")
    else:
        print("❌ Email content does NOT include menstrual cycle information")
        return False
    
    # Check function calls include the parameter
    if "st.session_state.get('ciclo_menstrual')" in content:
        print("✅ Function calls pass ciclo_menstrual parameter from session state")
    else:
        print("❌ Function calls do NOT pass ciclo_menstrual parameter")
        return False
    
    return True

def test_validation():
    """Test that menstrual cycle validation is included for women."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check validation in datos_completos_para_email
    if 'if sexo == "Mujer":' in content and 'ciclo_menstrual' in content:
        # More specific check
        pattern = r'if sexo == "Mujer":\s+ciclo_menstrual = st\.session_state\.get\(\'ciclo_menstrual\'\)'
        if re.search(pattern, content, re.MULTILINE):
            print("✅ Validation includes menstrual cycle check for women")
            return True
    
    print("❌ Validation for menstrual cycle NOT properly implemented")
    return False

def test_conditional_display():
    """Test that the question only appears for women."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that function returns None when not applicable
    pattern = r'if sexo != "Mujer":\s+return None'
    if re.search(pattern, content, re.MULTILINE):
        print("✅ Function returns None when sexo != 'Mujer' (conditional display)")
        return True
    else:
        print("❌ Function does NOT properly handle conditional display")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Menstrual Cycle Question Implementation")
    print("=" * 60)
    print()
    
    tests = [
        ("Function exists", test_function_exists),
        ("Function is called", test_function_called),
        ("Menstrual cycle options", test_menstrual_cycle_options),
        ("Session state storage", test_session_state_storage),
        ("Email integration", test_email_integration),
        ("Validation logic", test_validation),
        ("Conditional display", test_conditional_display)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Test: {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

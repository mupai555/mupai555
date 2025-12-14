#!/usr/bin/env python3
"""
Test script for PARTE 2 email functionality
Verifies that the secondary email function is properly implemented
"""

def test_email_parte2_function_exists():
    """Test that enviar_email_parte2 function exists in streamlit_app.py"""
    print("Test 1: Checking enviar_email_parte2 function exists...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    assert "def enviar_email_parte2(" in content, "❌ enviar_email_parte2 function not found"
    print("  ✓ enviar_email_parte2 function found")
    print("✅ Test 1 PASSED\n")

def test_email_parte2_subject():
    """Test that the subject line is correctly formatted"""
    print("Test 2: Checking PARTE 2 email subject format...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    assert "Reporte – PARTE 2 (Lectura Visual)" in content, "❌ PARTE 2 subject line not found"
    print("  ✓ PARTE 2 subject line format correct")
    print("✅ Test 2 PASSED\n")

def test_email_parte2_recipients():
    """Test that the email has correct recipients"""
    print("Test 3: Checking PARTE 2 email recipients...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Check for destination
    assert 'email_destino = "administracion@muscleupgym.fitness"' in content, "❌ Main recipient not correct"
    print("  ✓ Main recipient (administracion@muscleupgym.fitness) correct")
    
    # Check for CC to login.fitness
    assert '"login.fitness"' in content, "❌ CC to login.fitness not found"
    print("  ✓ CC to login.fitness found")
    
    print("✅ Test 3 PASSED\n")

def test_email_parte2_content_sections():
    """Test that the email contains all required sections"""
    print("Test 4: Checking PARTE 2 email content sections...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    required_sections = [
        "REPORTE – PARTE 2 (Lectura Visual)",
        "DATOS DEL CLIENTE",
        "RESUMEN DE EVALUACIÓN",
        "COMPOSICIÓN CORPORAL",
        "TABLAS METODOLÓGICAS",
        "CLASIFICACIÓN AUTOMÁTICA",
        "DETALLES FUNCIONALES",
        "NOTAS INTERPRETATIVAS",
        "DESGLOSE GLOBAL DEL NIVEL"
    ]
    
    for section in required_sections:
        assert section in content, f"❌ Section '{section}' not found in email"
        print(f"  ✓ Section '{section}' found")
    
    print("✅ Test 4 PASSED\n")

def test_email_parte2_integration():
    """Test that enviar_email_parte2 is called after main email"""
    print("Test 5: Checking PARTE 2 email is called after main email...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Find the call to enviar_email_resumen and check if enviar_email_parte2 follows
    assert "enviar_email_resumen" in content, "❌ Main email function not found"
    assert "enviar_email_parte2" in content, "❌ PARTE 2 email function call not found"
    
    # Check both send and resend buttons have the PARTE 2 call
    resumen_calls = content.count("enviar_email_resumen(tabla_resumen")
    parte2_calls = content.count("enviar_email_parte2(")
    
    # Should have at least 2 calls for parte2 (send and resend)
    assert parte2_calls >= 2, f"❌ Expected at least 2 calls to enviar_email_parte2, found {parte2_calls}"
    print(f"  ✓ Found {parte2_calls} calls to enviar_email_parte2")
    print(f"  ✓ Found {resumen_calls} calls to enviar_email_resumen")
    
    print("✅ Test 5 PASSED\n")

def test_email_parte2_cc_to_main_email():
    """Test that main email also has CC to client"""
    print("Test 6: Checking main email has CC to client...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Check that the main email function has CC field
    assert "msg['Cc'] = email_cliente" in content, "❌ CC to client not found in main email"
    print("  ✓ Main email includes CC to client")
    
    print("✅ Test 6 PASSED\n")

def test_safe_float_usage():
    """Test that safe_float is used for formatting values"""
    print("Test 7: Checking safe value handling in PARTE 2 email...")
    
    with open('streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Check that safe_float function exists globally
    assert "def safe_float(value, default=0.0):" in content, "❌ safe_float function not found"
    print("  ✓ safe_float function found")
    
    # Check that safe_float is used for optional fields in the email function
    assert "safe_float(masa_muscular" in content, "❌ safe_float not used for masa_muscular"
    print("  ✓ safe_float used for optional fields")
    
    # Check that placeholders are used when values are not available
    assert '[____]' in content, "❌ Placeholder pattern not found"
    print("  ✓ Placeholder pattern [____] found for missing values")
    
    print("✅ Test 7 PASSED\n")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING PARTE 2 EMAIL TESTS")
    print("="*60 + "\n")
    
    try:
        test_email_parte2_function_exists()
        test_email_parte2_subject()
        test_email_parte2_recipients()
        test_email_parte2_content_sections()
        test_email_parte2_integration()
        test_email_parte2_cc_to_main_email()
        test_safe_float_usage()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return False

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)

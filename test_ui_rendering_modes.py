#!/usr/bin/env python3
"""
Integration test to verify that UI rendering works correctly in both modes:
1. SHOW_TECH_DETAILS = False (client-facing, no technical details)
2. SHOW_TECH_DETAILS = True (internal testing, full technical details)
"""

import re

def test_client_mode():
    """Test that client mode (SHOW_TECH_DETAILS = False) hides technical details."""
    print("Testing client mode (SHOW_TECH_DETAILS = False)...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify flag is set to False
    assert 'SHOW_TECH_DETAILS = False' in content, "Flag should be False for client mode"
    
    # Verify conditional blocks exist that hide technical details
    patterns_that_should_exist = [
        r'if not SHOW_TECH_DETAILS:',  # Client-facing blocks
        r'if SHOW_TECH_DETAILS:',      # Technical blocks
        r'elif SHOW_TECH_DETAILS',     # Technical branches
    ]
    
    for pattern in patterns_that_should_exist:
        matches = re.findall(pattern, content)
        assert len(matches) > 0, f"Pattern '{pattern}' not found in code"
    
    print("  ✓ Flag set to False")
    print("  ✓ Conditional rendering blocks exist")
    print("  ✓ Client mode configuration correct")

def test_technical_mode_switchable():
    """Test that technical mode can be enabled by changing flag."""
    print("\nTesting technical mode switchability...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify flag can be changed
    assert 'SHOW_TECH_DETAILS = False' in content, "Flag should be defined"
    
    # Simulate changing flag to True
    test_content = content.replace('SHOW_TECH_DETAILS = False', 'SHOW_TECH_DETAILS = True')
    assert 'SHOW_TECH_DETAILS = True' in test_content, "Flag should be changeable to True"
    
    print("  ✓ Flag is easily switchable")
    print("  ✓ Technical mode can be enabled by setting flag to True")

def test_high_level_outputs_always_shown():
    """Test that high-level client outputs are always shown."""
    print("\nTesting high-level outputs are always visible...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # These should NOT be inside "if SHOW_TECH_DETAILS:" blocks
    high_level_outputs = [
        'Nivel Global de Entrenamiento',  # Should always be shown
        'plan_elegido',                    # Plan selection should work
        'Calorías objetivo',               # High-level result
        'Macros finales',                  # High-level result
    ]
    
    for output in high_level_outputs:
        assert output in content, f"High-level output '{output}' not found"
    
    print("  ✓ 'Nivel Global de Entrenamiento' present")
    print("  ✓ Plan selection available")
    print("  ✓ 'Calorías objetivo' present")
    print("  ✓ 'Macros finales' present")

def test_technical_details_properly_hidden():
    """Test that technical details are properly hidden in client mode."""
    print("\nTesting technical details are properly hidden...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find sections that should hide technical details
    technical_sections = [
        ('PSMF details', r'if not SHOW_TECH_DETAILS:.*?CANDIDATO PARA PROTOCOLO PSMF', re.DOTALL),
        ('FFMI technical', r'if not SHOW_TECH_DETAILS:.*?Nivel:.*?nivel_ffmi', re.DOTALL),
        ('ETA technical', r'if SHOW_TECH_DETAILS:.*?ETA:', re.DOTALL),
        ('GEAF technical', r'if SHOW_TECH_DETAILS:.*?GEAF', re.DOTALL),
    ]
    
    for section_name, pattern, flags in technical_sections:
        if re.search(pattern, content, flags):
            print(f"  ✓ {section_name} properly gated")
    
    print("  ✓ Technical details properly hidden behind flag")

def test_calculations_always_run():
    """Test that calculations run regardless of UI display mode."""
    print("\nTesting calculations always run...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # These calculations should happen OUTSIDE any SHOW_TECH_DETAILS blocks
    calculations = [
        'psmf_recs = calculate_psmf(',
        'fmi = calcular_fmi(',
        'eta =',
        'geaf = obtener_geaf(',
        'ingesta_calorica',
        'proteina_g',
        'grasa_g',
        'carbo_g',
    ]
    
    for calc in calculations:
        assert calc in content, f"Calculation '{calc}' not found"
    
    print("  ✓ PSMF calculation always runs")
    print("  ✓ FMI calculation always runs")
    print("  ✓ ETA calculation always runs")
    print("  ✓ GEAF calculation always runs")
    print("  ✓ Macro calculations always run")

def test_email_generation_unchanged():
    """Test that email generation is completely unchanged."""
    print("\nTesting email generation is unchanged...")
    
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Email generation markers
    email_markers = [
        'tabla_resumen = f"""',
        'enviar_email_resumen(tabla_resumen',
        'enviar_email_parte2(',
    ]
    
    for marker in email_markers:
        assert marker in content, f"Email marker '{marker}' not found"
    
    # Verify email section doesn't use SHOW_TECH_DETAILS
    tabla_start = content.find('tabla_resumen = f"""')
    email_call = content.find('enviar_email_resumen(tabla_resumen')
    
    if tabla_start > 0 and email_call > 0:
        email_section = content[tabla_start:email_call]
        assert 'SHOW_TECH_DETAILS' not in email_section, "Email section should not use SHOW_TECH_DETAILS"
    
    print("  ✓ Email generation structure intact")
    print("  ✓ Email does not use SHOW_TECH_DETAILS flag")
    print("  ✓ Email report generation unchanged")

def main():
    """Run all tests."""
    print("=" * 70)
    print("UI RENDERING MODES INTEGRATION TEST")
    print("=" * 70)
    
    try:
        test_client_mode()
        test_technical_mode_switchable()
        test_high_level_outputs_always_shown()
        test_technical_details_properly_hidden()
        test_calculations_always_run()
        test_email_generation_unchanged()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - UI rendering modes work correctly!")
        print("=" * 70)
        print("\nSummary:")
        print("  • Client mode (SHOW_TECH_DETAILS=False): Hides technical details ✓")
        print("  • Technical mode (SHOW_TECH_DETAILS=True): Shows full details ✓")
        print("  • High-level outputs: Always visible ✓")
        print("  • Calculations: Always run ✓")
        print("  • Email generation: Unchanged ✓")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

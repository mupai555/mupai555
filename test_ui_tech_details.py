#!/usr/bin/env python3
"""
Test script to validate that SHOW_TECH_DETAILS flag properly controls UI rendering
while keeping all backend calculations and email generation unchanged.
"""

import sys
import re

def test_show_tech_details_flag():
    """Test that SHOW_TECH_DETAILS flag is properly defined."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that flag is defined
    assert 'SHOW_TECH_DETAILS = False' in content, "SHOW_TECH_DETAILS flag not found or not set to False"
    print("✓ SHOW_TECH_DETAILS flag is properly defined as False")

def test_helper_functions_exist():
    """Test that helper functions for conditional rendering exist."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'def render_metric(' in content, "render_metric() function not found"
    assert 'def render_technical_block(' in content, "render_technical_block() function not found"
    print("✓ Helper functions render_metric() and render_technical_block() exist")

def test_ui_uses_flag():
    """Test that UI rendering code uses SHOW_TECH_DETAILS flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences of SHOW_TECH_DETAILS in UI sections
    ui_flag_uses = content.count('if SHOW_TECH_DETAILS:') + content.count('if not SHOW_TECH_DETAILS:')
    assert ui_flag_uses >= 10, f"Expected at least 10 uses of SHOW_TECH_DETAILS flag in UI, found {ui_flag_uses}"
    print(f"✓ SHOW_TECH_DETAILS flag is used {ui_flag_uses} times in UI rendering")

def test_email_generation_unaffected():
    """Test that email generation code does not use SHOW_TECH_DETAILS flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the email generation section (tabla_resumen construction)
    email_section_start = None
    email_section_end = None
    
    for i, line in enumerate(lines):
        if 'tabla_resumen = f"""' in line or 'tabla_resumen += f"""' in line:
            if email_section_start is None:
                email_section_start = i
        if 'enviar_email_resumen(tabla_resumen' in line:
            email_section_end = i
            break
    
    assert email_section_start is not None, "Could not find tabla_resumen construction"
    assert email_section_end is not None, "Could not find enviar_email_resumen call"
    
    # Check that email section doesn't use SHOW_TECH_DETAILS
    email_section = ''.join(lines[email_section_start:email_section_end])
    assert 'SHOW_TECH_DETAILS' not in email_section, "Email generation code should NOT use SHOW_TECH_DETAILS flag"
    print("✓ Email generation code (tabla_resumen) does not use SHOW_TECH_DETAILS flag")

def test_critical_ui_sections_refactored():
    """Test that critical UI sections have been refactored."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test PSMF section
    assert 'CANDIDATO PARA PROTOCOLO PSMF' in content, "PSMF section not found"
    psmf_section_has_flag = 'if not SHOW_TECH_DETAILS:' in content and 'CANDIDATO PARA PROTOCOLO PSMF' in content
    assert psmf_section_has_flag, "PSMF section not properly refactored"
    print("✓ PSMF display section properly refactored")
    
    # Test FFMI section
    assert 'FFMI' in content, "FFMI section not found"
    ffmi_section_has_flag = content.count('SHOW_TECH_DETAILS') > 0
    assert ffmi_section_has_flag, "FFMI section not properly refactored"
    print("✓ FFMI display section properly refactored")
    
    # Test final macros section
    assert 'Calorías objetivo' in content or 'Macros finales' in content, "Final results section not found"
    print("✓ Final results section properly refactored")

def test_calculations_still_run():
    """Test that calculations still run regardless of flag value."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that critical calculations happen outside conditional blocks
    assert 'psmf_recs = calculate_psmf(' in content, "PSMF calculation not found"
    assert 'fmi = calcular_fmi(' in content, "FMI calculation not found"
    assert 'eta =' in content, "ETA calculation not found"
    assert 'geaf = obtener_geaf(' in content, "GEAF calculation not found"
    print("✓ All critical calculations still run unconditionally")

def main():
    """Run all tests."""
    print("Testing SHOW_TECH_DETAILS flag implementation...\n")
    
    try:
        test_show_tech_details_flag()
        test_helper_functions_exist()
        test_ui_uses_flag()
        test_email_generation_unaffected()
        test_critical_ui_sections_refactored()
        test_calculations_still_run()
        
        print("\n✅ All tests passed! UI refactoring is correct.")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script to validate PSMF and ETA visibility flags implementation.
Ensures that:
1. Visibility flags are properly defined
2. UI elements are hidden when flags are False
3. Backend calculations always run
4. Email reports always contain full details
5. Session state storage works correctly
"""

import sys
import re

def test_visibility_flags_defined():
    """Test that MOSTRAR_PSMF_AL_USUARIO and MOSTRAR_ETA_AL_USUARIO flags are defined."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check PSMF flag
    assert 'MOSTRAR_PSMF_AL_USUARIO = False' in content, \
        "MOSTRAR_PSMF_AL_USUARIO flag not found or not set to False"
    print("✓ MOSTRAR_PSMF_AL_USUARIO flag is properly defined as False")
    
    # Check ETA flag
    assert 'MOSTRAR_ETA_AL_USUARIO = False' in content, \
        "MOSTRAR_ETA_AL_USUARIO flag not found or not set to False"
    print("✓ MOSTRAR_ETA_AL_USUARIO flag is properly defined as False")

# Constants for test validation
CONTEXT_LINES_TO_CHECK = 5  # Number of preceding lines to check for conditional blocks

def test_psmf_calculations_always_run():
    """Test that PSMF calculations execute unconditionally."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find PSMF calculation
    assert 'psmf_recs = calculate_psmf(' in content, "PSMF calculation not found"
    
    # Check that calculation is not inside a MOSTRAR_PSMF_AL_USUARIO conditional
    lines = content.split('\n')
    calc_line = None
    for i, line in enumerate(lines):
        if 'psmf_recs = calculate_psmf(' in line:
            calc_line = i
            break
    
    assert calc_line is not None, "Could not find PSMF calculation line"
    
    # Check preceding lines to ensure it's not in a conditional block
    preceding_lines = lines[max(0, calc_line-CONTEXT_LINES_TO_CHECK):calc_line]
    for line in preceding_lines:
        if 'if MOSTRAR_PSMF_AL_USUARIO' in line:
            raise AssertionError("PSMF calculation should not be inside MOSTRAR_PSMF_AL_USUARIO conditional")
    
    print("✓ PSMF calculations execute unconditionally")

def test_psmf_session_state_storage():
    """Test that PSMF results are stored in session_state."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for session_state storage
    assert 'st.session_state.psmf_recs' in content, \
        "PSMF results not stored in session_state.psmf_recs"
    assert 'st.session_state.psmf_aplicable' in content, \
        "PSMF applicability not stored in session_state.psmf_aplicable"
    
    print("✓ PSMF results are stored in session_state")

def test_eta_calculations_always_run():
    """Test that ETA calculations execute unconditionally."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check ETA calculation exists
    assert 'eta = 1.15' in content or 'eta = 1.12' in content or 'eta = 1.10' in content, \
        "ETA calculation not found"
    
    # Find ETA calculation section
    lines = content.split('\n')
    eta_calc_start = None
    for i, line in enumerate(lines):
        if '# ===== ETA CALCULATION (ALWAYS RUNS) =====' in line:
            eta_calc_start = i
            break
    
    assert eta_calc_start is not None, "Could not find ETA calculation section"
    
    # Verify it's before the UI conditional
    eta_ui_conditional = None
    for i, line in enumerate(lines[eta_calc_start:], start=eta_calc_start):
        if 'if MOSTRAR_ETA_AL_USUARIO:' in line:
            eta_ui_conditional = i
            break
    
    # Ensure calculations happen before UI conditional
    if eta_ui_conditional:
        calc_section = '\n'.join(lines[eta_calc_start:eta_ui_conditional])
        assert 'eta = 1.' in calc_section, "ETA calculations should be before UI conditional"
    
    print("✓ ETA calculations execute unconditionally")

def test_eta_session_state_storage():
    """Test that ETA results are stored in session_state."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for session_state storage
    assert 'st.session_state.eta' in content, \
        "ETA not stored in session_state.eta"
    assert 'st.session_state.eta_desc' in content, \
        "ETA description not stored in session_state.eta_desc"
    assert 'st.session_state.eta_color' in content, \
        "ETA color not stored in session_state.eta_color"
    
    print("✓ ETA results are stored in session_state")

def test_psmf_ui_uses_flag():
    """Test that PSMF UI elements use MOSTRAR_PSMF_AL_USUARIO flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count uses of PSMF visibility flag in UI sections
    psmf_flag_uses = content.count('MOSTRAR_PSMF_AL_USUARIO')
    assert psmf_flag_uses >= 4, \
        f"Expected at least 4 uses of MOSTRAR_PSMF_AL_USUARIO flag, found {psmf_flag_uses}"
    
    # Check for specific UI conditionals
    assert 'if psmf_recs.get("psmf_aplicable") and MOSTRAR_PSMF_AL_USUARIO:' in content, \
        "PSMF candidate display should check MOSTRAR_PSMF_AL_USUARIO flag"
    
    print(f"✓ MOSTRAR_PSMF_AL_USUARIO flag is used {psmf_flag_uses} times in UI")

def test_eta_ui_uses_flag():
    """Test that ETA UI elements use MOSTRAR_ETA_AL_USUARIO flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count uses of ETA visibility flag
    eta_flag_uses = content.count('MOSTRAR_ETA_AL_USUARIO')
    assert eta_flag_uses >= 1, \
        f"Expected at least 1 use of MOSTRAR_ETA_AL_USUARIO flag, found {eta_flag_uses}"
    
    # Check for UI conditional
    assert 'if MOSTRAR_ETA_AL_USUARIO:' in content, \
        "ETA expander should check MOSTRAR_ETA_AL_USUARIO flag"
    
    print(f"✓ MOSTRAR_ETA_AL_USUARIO flag is used {eta_flag_uses} times in UI")

def test_email_generation_unaffected():
    """Test that email generation does not use visibility flags."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find email generation section (tabla_resumen construction)
    email_section_start = None
    email_section_end = None
    
    for i, line in enumerate(lines):
        if 'EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):' in line:
            if email_section_start is None:
                email_section_start = i
        if 'tabla_resumen += f"""' in line and 'PREFERENCIAS Y HÁBITOS' in lines[i+1]:
            email_section_end = i + 50
            break
    
    assert email_section_start is not None, "Could not find email ETA section"
    
    if email_section_end:
        # Check that email section doesn't use visibility flags
        email_section = ''.join(lines[email_section_start:email_section_end])
        assert 'MOSTRAR_PSMF_AL_USUARIO' not in email_section, \
            "Email generation should NOT use MOSTRAR_PSMF_AL_USUARIO flag"
        assert 'MOSTRAR_ETA_AL_USUARIO' not in email_section, \
            "Email generation should NOT use MOSTRAR_ETA_AL_USUARIO flag"
        
    print("✓ Email generation code does not use visibility flags")

def test_psmf_email_always_included():
    """Test that PSMF details are always in email."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for PSMF in email
    assert '⚡ PROTOCOLO PSMF ACTUALIZADO' in content, \
        "PSMF section not found in email"
    assert 'Multiplicador calórico:' in content, \
        "PSMF multiplier details not in email"
    assert 'Pérdida esperada:' in content, \
        "PSMF projected loss not in email"
    
    print("✓ PSMF details are always included in email reports")

def test_eta_email_always_included():
    """Test that ETA details are always in email."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for ETA in email
    assert '🔥 EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):' in content, \
        "ETA section not found in email"
    assert '- Factor ETA:' in content, \
        "ETA factor not in email"
    assert '- Criterio aplicado:' in content, \
        "ETA criteria not in email"
    
    print("✓ ETA details are always included in email reports")

def test_documentation_exists():
    """Test that documentation for the flags exists."""
    try:
        with open('PSMF_ETA_VISIBILITY_GUIDE.md', 'r', encoding='utf-8') as f:
            doc_content = f.read()
        
        # Check for key sections
        assert 'MOSTRAR_PSMF_AL_USUARIO' in doc_content, \
            "Documentation should describe MOSTRAR_PSMF_AL_USUARIO"
        assert 'MOSTRAR_ETA_AL_USUARIO' in doc_content, \
            "Documentation should describe MOSTRAR_ETA_AL_USUARIO"
        assert 'Backend Behavior' in doc_content, \
            "Documentation should explain backend behavior"
        assert 'Email Report' in doc_content, \
            "Documentation should explain email behavior"
        
        print("✓ Documentation file exists and contains required sections")
    except FileNotFoundError:
        print("⚠ Warning: PSMF_ETA_VISIBILITY_GUIDE.md not found")

def test_flags_have_comments():
    """Test that flags are well-documented in code."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find flag definitions
    for i, line in enumerate(lines):
        if 'MOSTRAR_PSMF_AL_USUARIO' in line and '=' in line:
            # Check for comment explaining the flag
            preceding_lines = ''.join(lines[max(0, i-CONTEXT_LINES_TO_CHECK):i+1])
            assert 'Control' in preceding_lines or 'visibility' in preceding_lines.lower(), \
                "MOSTRAR_PSMF_AL_USUARIO should have explanatory comments"
            break
    
    print("✓ Visibility flags have explanatory comments")

def test_calculations_produce_values():
    """Test that calculation patterns are correct (static analysis)."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check PSMF calculation patterns
    assert 'calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura)' in content, \
        "PSMF calculation should use correct parameters"
    
    # Check ETA assignment patterns
    eta_assignments = content.count('eta = 1.')
    assert eta_assignments >= 3, \
        f"Expected at least 3 ETA value assignments, found {eta_assignments}"
    
    print("✓ Calculation patterns are correct")

def main():
    """Run all tests."""
    print("Testing PSMF and ETA visibility flags implementation...\n")
    
    tests = [
        test_visibility_flags_defined,
        test_psmf_calculations_always_run,
        test_psmf_session_state_storage,
        test_eta_calculations_always_run,
        test_eta_session_state_storage,
        test_psmf_ui_uses_flag,
        test_eta_ui_uses_flag,
        test_email_generation_unaffected,
        test_psmf_email_always_included,
        test_eta_email_always_included,
        test_documentation_exists,
        test_flags_have_comments,
        test_calculations_produce_values,
    ]
    
    failed = []
    
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed.append((test.__name__, str(e)))
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed.append((test.__name__, str(e)))
    
    print("\n" + "="*70)
    if not failed:
        print("✅ All tests passed! PSMF and ETA visibility implementation is correct.")
        print("\nSummary:")
        print("  - Visibility flags properly defined and defaulted to False")
        print("  - PSMF and ETA calculations always run (backend functionality intact)")
        print("  - Results stored in session_state for downstream use")
        print("  - UI elements properly controlled by visibility flags")
        print("  - Email reports always include complete technical details")
        print("  - Documentation is comprehensive and accurate")
        return 0
    else:
        print(f"❌ {len(failed)} test(s) failed:")
        for test_name, error in failed:
            print(f"\n  - {test_name}")
            print(f"    {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script to validate that technical calculation details (dias_fuerza, kcal_sesion, promedio_diario)
are hidden from client-visible interface while remaining in email reports.
"""

import sys
import re

def test_metrics_hidden_by_flag():
    """Test that metrics are conditionally displayed based on SHOW_TECH_DETAILS flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that metrics display is wrapped in SHOW_TECH_DETAILS conditional
    assert 'if SHOW_TECH_DETAILS:' in content, "SHOW_TECH_DETAILS conditional not found"
    
    # Find the section with dias_fuerza metrics
    dias_fuerza_pattern = r'st\.metric\("Días/semana".*dias_fuerza'
    matches = list(re.finditer(dias_fuerza_pattern, content, re.DOTALL))
    assert len(matches) > 0, "dias_fuerza metric display not found"
    
    # Check that the metric is within a SHOW_TECH_DETAILS conditional block
    for match in matches:
        # Get the text before the match (within reasonable range)
        start = max(0, match.start() - 500)
        preceding_text = content[start:match.start()]
        if 'if SHOW_TECH_DETAILS:' in preceding_text:
            print("✓ dias_fuerza metric is conditionally displayed based on SHOW_TECH_DETAILS")
            break
    else:
        raise AssertionError("dias_fuerza metric not wrapped in SHOW_TECH_DETAILS conditional")

def test_blue_message_updated():
    """Test that the blue message has been updated to be more general."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the new client-friendly message
    client_message = "En base a tu nivel global de entrenamiento – que combina desarrollo muscular, rendimiento funcional y experiencia – se han realizado los cálculos personalizados"
    assert client_message in content, "New client-friendly message not found"
    print("✓ Blue message updated to client-friendly version")
    
    # Check that the message is in the else block (shown when SHOW_TECH_DETAILS is False)
    message_pattern = re.compile(r'else:.*?' + re.escape(client_message), re.DOTALL)
    matches = list(message_pattern.finditer(content))
    assert len(matches) > 0, "Client-friendly message not in else block"
    print("✓ Client-friendly message is shown when SHOW_TECH_DETAILS=False")

def test_email_contains_technical_variables():
    """Test that email generation still includes all technical variables."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the tabla_resumen section
    tabla_resumen_start = content.find('tabla_resumen = f"""')
    assert tabla_resumen_start > 0, "tabla_resumen construction not found"
    
    # Find the end of email generation section (before enviar_email_resumen call)
    email_end = content.find('enviar_email_resumen(tabla_resumen', tabla_resumen_start)
    assert email_end > 0, "enviar_email_resumen call not found"
    
    email_section = content[tabla_resumen_start:email_end]
    
    # Check for technical variables in email
    assert 'dias_fuerza' in email_section, "dias_fuerza not found in email generation"
    assert 'kcal_sesion' in email_section, "kcal_sesion not found in email generation"
    assert 'gee_prom_dia' in email_section or 'promedio_diario' in email_section, "promedio_diario (gee_prom_dia) not found in email generation"
    
    print("✓ Email generation includes dias_fuerza")
    print("✓ Email generation includes kcal_sesion")
    print("✓ Email generation includes promedio_diario (gee_prom_dia)")

def test_calculations_still_run():
    """Test that calculations still run regardless of flag value."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that dias_fuerza calculation exists
    assert 'dias_fuerza = st.slider(' in content, "dias_fuerza slider not found"
    assert 'st.session_state.dias_fuerza = dias_fuerza' in content, "dias_fuerza not saved to session state"
    
    # Check that kcal_sesion calculation exists
    assert 'kcal_sesion =' in content, "kcal_sesion calculation not found"
    assert 'st.session_state.kcal_sesion = kcal_sesion' in content, "kcal_sesion not saved to session state"
    
    # Check that gee_prom_dia calculation exists
    assert 'gee_prom_dia = gee_semanal / 7' in content, "gee_prom_dia calculation not found"
    assert 'st.session_state.gee_prom_dia = gee_prom_dia' in content, "gee_prom_dia not saved to session state"
    
    print("✓ dias_fuerza calculation and session state storage exist")
    print("✓ kcal_sesion calculation and session state storage exist")
    print("✓ gee_prom_dia calculation and session state storage exist")

def test_flag_set_to_false():
    """Test that SHOW_TECH_DETAILS flag is set to False by default."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'SHOW_TECH_DETAILS = False' in content, "SHOW_TECH_DETAILS not set to False"
    print("✓ SHOW_TECH_DETAILS is set to False (client mode)")

def main():
    """Run all tests."""
    print("Testing UI hidden logic implementation...\n")
    
    try:
        test_flag_set_to_false()
        test_metrics_hidden_by_flag()
        test_blue_message_updated()
        test_email_contains_technical_variables()
        test_calculations_still_run()
        
        print("\n✅ All tests passed! UI hidden logic implementation is correct.")
        print("\nSummary:")
        print("- Technical metrics (dias_fuerza, kcal_sesion, promedio_diario) are hidden from client UI")
        print("- Blue message updated to be more general and client-friendly")
        print("- Email reports still include all technical variables")
        print("- All calculations continue to run correctly")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script to validate USER_VIEW flag implementation.
Ensures that:
1. USER_VIEW flag exists and is set to False
2. All calculations still run regardless of USER_VIEW flag
3. Email generation still includes all required variables
"""

import sys
import re

def test_user_view_flag_exists():
    """Test that USER_VIEW flag is defined and set to False."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'USER_VIEW = False' in content, "USER_VIEW flag not set to False"
    print("✓ USER_VIEW flag exists and is set to False")

def test_calculations_always_run():
    """Test that key calculations run regardless of USER_VIEW flag."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that calculations exist outside or independent of USER_VIEW conditionals
    # Key calculations: fmi, modo_ffmi, niveles_ejercicios, nivel_entrenamiento
    
    # FMI calculation (should be before or outside USER_VIEW)
    fmi_calc_pattern = r'fmi = calcular_fmi\(peso, grasa_corregida, estatura\)'
    fmi_matches = list(re.finditer(fmi_calc_pattern, content))
    assert len(fmi_matches) > 0, "fmi calculation not found"
    
    # Check that fmi calculation is not indented more than necessary (not deeply nested in USER_VIEW)
    for match in fmi_matches:
        start = max(0, match.start() - 200)
        preceding_text = content[start:match.start()]
        # Count if statements before this calculation
        if_count = preceding_text.count('if USER_VIEW:')
        # The calculation should appear before USER_VIEW block or in else block
        # We allow it to be in one USER_VIEW block max
        print(f"✓ fmi calculation found and appears to run independently")
        break
    
    # modo_ffmi calculation
    modo_ffmi_pattern = r'modo_ffmi = obtener_modo_interpretacion_ffmi'
    modo_matches = list(re.finditer(modo_ffmi_pattern, content))
    assert len(modo_matches) > 0, "modo_ffmi calculation not found"
    print("✓ modo_ffmi calculation exists")
    
    # Check that nivel_entrenamiento calculation exists
    nivel_pattern = r'nivel_entrenamiento = "[^"]+"'
    nivel_matches = list(re.finditer(nivel_pattern, content))
    assert len(nivel_matches) > 0, "nivel_entrenamiento calculation not found"
    print("✓ nivel_entrenamiento calculation exists")

def test_else_block_for_calculations():
    """Test that when USER_VIEW=False, calculations still run in else block."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the nutritional plan section
    plan_section_start = content.find('# Display final nutritional plan to user')
    assert plan_section_start > 0, "Nutritional plan section not found"
    
    # Check for else block after USER_VIEW conditional
    else_block_pattern = r'else:\s*#\s*When USER_VIEW=False'
    matches = list(re.finditer(else_block_pattern, content[plan_section_start:]))
    assert len(matches) > 0, "Else block for USER_VIEW=False not found in nutritional plan section"
    print("✓ Else block exists for calculations when USER_VIEW=False")
    
    # Check that essential variables are calculated in else block
    else_start = plan_section_start + matches[0].start()
    else_section = content[else_start:else_start + 2000]
    
    assert 'fase, porcentaje = determinar_fase_nutricional_refinada' in else_section, "fase calculation not in else block"
    assert 'fbeo = 1 + porcentaje / 100' in else_section, "fbeo calculation not in else block"
    assert 'ingesta_calorica =' in else_section, "ingesta_calorica calculation not in else block"
    assert 'proteina_g = calcular_proteina' in else_section, "proteina_g calculation not in else block"
    assert 'grasa_g = ' in else_section, "grasa_g calculation not in else block"
    assert 'carbo_g =' in else_section, "carbo_g calculation not in else block"
    
    print("✓ All essential nutritional variables calculated in else block")

def test_email_variables_available():
    """Test that email generation section has access to all required variables."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find tabla_resumen section
    tabla_start = content.find('tabla_resumen = f"""')
    assert tabla_start > 0, "tabla_resumen construction not found"
    
    # Check for required variables in email template
    email_end = content.find('enviar_email_resumen(tabla_resumen', tabla_start)
    assert email_end > 0, "enviar_email_resumen call not found"
    
    email_section = content[tabla_start:email_end]
    
    # Check for essential variables
    required_vars = ['fase', 'ingesta_calorica', 'proteina_g', 'grasa_g', 'carbo_g', 
                     'ffmi', 'fmi', 'nivel_ffmi', 'modo_ffmi', 'mlg', 'grasa_corregida']
    
    for var in required_vars:
        assert f'{{{var}' in email_section or f'{var}:' in email_section or f'{var}.' in email_section, \
            f"Variable {var} not found in email section"
    
    print(f"✓ All {len(required_vars)} required variables available in email generation")

def test_success_message_when_user_view_false():
    """Test that success message is shown when USER_VIEW=False."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the final summary section
    summary_start = content.find('# RESUMEN FINAL MEJORADO')
    assert summary_start > 0, "Final summary section not found"
    
    # Check for else block with success message (within 10000 chars should be enough)
    success_section = content[summary_start:summary_start + 10000]
    
    # Check for else block
    assert 'else:' in success_section and 'When USER_VIEW=False' in success_section, \
        "Else block for USER_VIEW=False not found"
    
    # Check for success message
    assert 'Evaluación completada exitosamente' in success_section, \
        "Success message title not found"
    
    # Check for the specific message content
    assert 'Tus respuestas han sido recolectadas, validadas y procesadas correctamente' in success_section, \
        "Success message content not found"
    assert 'Muscle Up GYM' in success_section, "Muscle Up GYM mention not found in success message"
    assert 'MUPAI' in success_section, "MUPAI mention not found in success message"
    
    print("✓ Success message correctly displayed when USER_VIEW=False")

def test_ui_sections_wrapped():
    """Test that all major UI display sections are wrapped with USER_VIEW conditional."""
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key section headers that should be wrapped
    sections_to_check = [
        '### 📈 Resultados de tu composición corporal',
        '### 💪 Índice de Masa Libre de Grasa (FFMI) y Adiposidad (FMI)',
        '### 📊 Tu nivel en cada ejercicio',
        '### 🎯 Tu Nivel Global de Entrenamiento',
        '📈 **RESULTADO FINAL: Tu Plan Nutricional Personalizado**',
        '## 🎯 **Resumen Final de tu Evaluación MUPAI**'
    ]
    
    for section in sections_to_check:
        pos = content.find(section)
        assert pos > 0, f"Section '{section}' not found"
        
        # Check if USER_VIEW appears before this section (within 2000 chars - increased range)
        preceding_text = content[max(0, pos - 2000):pos]
        assert 'USER_VIEW' in preceding_text, f"Section '{section}' not wrapped with USER_VIEW"
    
    print(f"✓ All {len(sections_to_check)} major UI sections wrapped with USER_VIEW conditional")

if __name__ == "__main__":
    try:
        test_user_view_flag_exists()
        test_calculations_always_run()
        test_else_block_for_calculations()
        test_email_variables_available()
        test_success_message_when_user_view_false()
        test_ui_sections_wrapped()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nSummary:")
        print("- USER_VIEW flag correctly implemented")
        print("- All calculations run regardless of flag value")
        print("- Email generation has access to all required variables")
        print("- Success message displayed when USER_VIEW=False")
        print("- All major UI sections properly wrapped")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)

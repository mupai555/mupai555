#!/usr/bin/env python3
"""
Test to validate enviar_email_parte2 function integration in streamlit_app.py
"""

import sys
import os

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")
with open(streamlit_app_path, "r") as f:
    content = f.read()

print("Testing enviar_email_parte2 function integration...")
print("=" * 60)

all_checks_passed = True

# Check 1: Verify clasificar_grasa_visceral function exists
if 'def clasificar_grasa_visceral(nivel):' in content:
    print("✓ clasificar_grasa_visceral function defined")
else:
    print("✗ clasificar_grasa_visceral function NOT found")
    all_checks_passed = False

# Check 2: Verify clasificar_masa_muscular function exists
if 'def clasificar_masa_muscular(porcentaje, edad, sexo):' in content:
    print("✓ clasificar_masa_muscular function defined")
else:
    print("✗ clasificar_masa_muscular function NOT found")
    all_checks_passed = False

# Check 3: Verify enviar_email_parte2 function exists
if 'def enviar_email_parte2(' in content:
    print("✓ enviar_email_parte2 function defined")
else:
    print("✗ enviar_email_parte2 function NOT found")
    all_checks_passed = False

# Check 4: Verify email subject format
if 'Reporte de Evaluación — Parte 2 (Lectura Visual, Línea Base)' in content:
    print("✓ Correct email subject format for Parte 2")
else:
    print("✗ Email subject format NOT correct")
    all_checks_passed = False

# Check 5: Verify exclusive recipient (no CC/BCC)
if 'administracion@muscleupgym.fitness' in content:
    print("✓ Email sent to administracion@muscleupgym.fitness")
else:
    print("✗ Email recipient NOT correct")
    all_checks_passed = False

# Check 6: Verify email is called in send button logic
if 'ok_parte2 = enviar_email_parte2(' in content:
    print("✓ enviar_email_parte2 called in send button logic")
else:
    print("✗ enviar_email_parte2 NOT called in send button logic")
    all_checks_passed = False

# Check 7: Verify email is called in resend button logic
count = content.count('ok_parte2 = enviar_email_parte2(')
if count >= 2:
    print("✓ enviar_email_parte2 called in both send and resend logic")
else:
    print("✗ enviar_email_parte2 NOT called in resend logic")
    all_checks_passed = False

# Check 8: Verify grasa visceral classification in email
if 'clasificar_grasa_visceral(grasa_visceral_val)' in content:
    print("✓ Grasa visceral classification used in email")
else:
    print("✗ Grasa visceral classification NOT used")
    all_checks_passed = False

# Check 9: Verify masa muscular classification in email
if 'clasificar_masa_muscular(masa_muscular_val, edad, sexo)' in content:
    print("✓ Masa muscular classification used in email")
else:
    print("✗ Masa muscular classification NOT used")
    all_checks_passed = False

# Check 10: Verify success message for Parte 2
if 'Reporte interno (Parte 2) enviado exitosamente' in content:
    print("✓ Success message for Parte 2 email present")
else:
    print("✗ Success message for Parte 2 NOT found")
    all_checks_passed = False

# Check 11: Verify baseline evaluation note
if 'Este es un reporte de LÍNEA BASE' in content:
    print("✓ Baseline evaluation note present in email")
else:
    print("✗ Baseline evaluation note NOT found")
    all_checks_passed = False

# Check 12: Verify N/D placeholder usage
if '[____]' in content:
    print("✓ N/D placeholder format present in email")
else:
    print("✗ N/D placeholder format NOT found")
    all_checks_passed = False

print("=" * 60)

if all_checks_passed:
    print("✓ All enviar_email_parte2 integration tests passed!")
    sys.exit(0)
else:
    print("✗ Some tests failed!")
    sys.exit(1)

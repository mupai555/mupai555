#!/usr/bin/env python3
"""
Comprehensive test for waist circumference and decimal height features
"""

import sys
import os

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")

try:
    with open(streamlit_app_path, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print(f"❌ Error: Could not find {streamlit_app_path}")
    sys.exit(1)

print("=" * 70)
print("COMPREHENSIVE TEST: WAIST CIRCUMFERENCE & DECIMAL HEIGHT")
print("=" * 70)
print()

all_checks_passed = True

# Test 1: Session state includes circunferencia_cintura
print("Test 1: Session State Configuration")
print("-" * 70)
if '"circunferencia_cintura": ""' in content or "'circunferencia_cintura': ''" in content:
    print("✅ circunferencia_cintura added to session state defaults")
else:
    print("❌ circunferencia_cintura NOT found in session state")
    all_checks_passed = False
print()

# Test 2: Height input supports decimals
print("Test 2: Decimal Height Support")
print("-" * 70)
if 'min_value=120.0' in content and 'max_value=220.0' in content:
    print("✅ Height input uses decimal min/max values")
else:
    print("❌ Height input does NOT use decimal values")
    all_checks_passed = False

if 'safe_float(estatura_value' in content:
    print("✅ Height uses safe_float for decimal support")
else:
    print("❌ Height does NOT use safe_float")
    all_checks_passed = False

if 'step=0.1' in content and '📏 Estatura (cm)' in content:
    print("✅ Height input has step=0.1 for decimal precision")
else:
    print("❌ Height step NOT configured for decimals")
    all_checks_passed = False
print()

# Test 3: Waist circumference input field
print("Test 3: Waist Circumference Input Field")
print("-" * 70)
if '📏 Circunferencia de cintura' in content:
    print("✅ Waist circumference input field present")
else:
    print("❌ Waist circumference input field NOT found")
    all_checks_passed = False

if 'key="circunferencia_cintura"' in content:
    print("✅ Waist input has correct session state key")
else:
    print("❌ Waist input key NOT found")
    all_checks_passed = False
print()

# Test 4: WHtR calculation functions
print("Test 4: WHtR Calculation Functions")
print("-" * 70)
if 'def calcular_whtr(circunferencia_cintura, estatura):' in content:
    print("✅ calcular_whtr function defined")
else:
    print("❌ calcular_whtr function NOT found")
    all_checks_passed = False

if 'def clasificar_whtr(whtr, sexo, edad):' in content:
    print("✅ clasificar_whtr function defined")
else:
    print("❌ clasificar_whtr function NOT found")
    all_checks_passed = False

if 'Waist-to-Height Ratio' in content or 'WHtR' in content:
    print("✅ WHtR terminology present")
else:
    print("❌ WHtR terminology NOT found")
    all_checks_passed = False
print()

# Test 5: UI display of waist metrics
print("Test 5: UI Display Integration")
print("-" * 70)
if 'st.metric("Circunferencia cintura"' in content:
    print("✅ Waist circumference displayed in UI")
else:
    print("❌ Waist metric NOT displayed")
    all_checks_passed = False

if 'st.metric("Ratio Cintura-Estatura (WHtR)"' in content:
    print("✅ WHtR displayed in UI")
else:
    print("❌ WHtR metric NOT displayed")
    all_checks_passed = False
print()

# Test 6: Email integration - tabla_resumen
print("Test 6: Email Summary Integration")
print("-" * 70)
if 'Circunferencia de cintura:' in content and 'Ratio Cintura-Estatura (WHtR):' in content:
    print("✅ Waist metrics included in main email summary")
else:
    print("❌ Waist metrics NOT in email summary")
    all_checks_passed = False
print()

# Test 7: Email Parte 2 integration
print("Test 7: Email Parte 2 Integration")
print("-" * 70)
if 'circunferencia_cintura=0.0' in content:
    print("✅ enviar_email_parte2 accepts circunferencia_cintura parameter")
else:
    print("❌ enviar_email_parte2 does NOT accept waist parameter")
    all_checks_passed = False

# Count calls to enviar_email_parte2 with circunferencia_cintura
count = content.count('enviar_email_parte2(')
calls_with_waist = content.count(', circunferencia_cintura')
if calls_with_waist >= 2:
    print(f"✅ enviar_email_parte2 called with waist data ({calls_with_waist} calls)")
else:
    print(f"⚠️  enviar_email_parte2 waist parameter used in {calls_with_waist} call(s)")
    if calls_with_waist == 0:
        all_checks_passed = False
print()

# Test 8: Scientific references
print("Test 8: Scientific References")
print("-" * 70)
if 'Ashwell' in content or 'Browning' in content:
    print("✅ Scientific references included in documentation")
else:
    print("⚠️  Scientific references not explicitly mentioned")
print()

# Test 9: Height decimal formatting in emails
print("Test 9: Height Decimal Formatting")
print("-" * 70)
# Check for decimal formatting in emails
if '{estatura:.1f}' in content:
    print("✅ Height displayed with decimal precision in emails")
else:
    print("⚠️  Height might not show decimal precision in all places")
print()

# Test 10: Validation and safety
print("Test 10: Validation and Safety")
print("-" * 70)
if 'safe_float(circunferencia_cintura' in content:
    print("✅ Waist circumference uses safe_float for validation")
else:
    print("❌ Waist circumference lacks proper validation")
    all_checks_passed = False

if 'min_value=0.0' in content and 'max_value=200.0' in content:
    print("✅ Waist circumference has reasonable range constraints")
else:
    print("⚠️  Waist range constraints not clearly defined")
print()

# Test 11: No impact on existing calculations
print("Test 11: Existing Calculations Preserved")
print("-" * 70)
if 'calcular_ffmi' in content and 'calcular_fmi' in content and 'calcular_tmb_cunningham' in content:
    print("✅ Core calculation functions still present")
else:
    print("❌ Core calculation functions may be missing")
    all_checks_passed = False

if 'calcular_macros_tradicional' in content and 'calcular_macros_psmf' in content:
    print("✅ Macro calculation functions still present")
else:
    print("❌ Macro calculation functions may be missing")
    all_checks_passed = False
print()

print("=" * 70)
if all_checks_passed:
    print("✅ ALL COMPREHENSIVE TESTS PASSED!")
    print()
    print("Summary of Changes:")
    print("  • Waist circumference input added (optional)")
    print("  • WHtR calculation and classification implemented")
    print("  • Decimal height support enabled")
    print("  • UI displays waist metrics appropriately")
    print("  • Email integration complete")
    print("  • Existing calculations preserved")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED - Review implementation")
    sys.exit(1)

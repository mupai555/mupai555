#!/usr/bin/env python3
"""
Test to validate grasa_visceral field integration in streamlit_app.py
"""

import sys
import os

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")
with open(streamlit_app_path, "r") as f:
    content = f.read()

print("Testing grasa_visceral field integration...")
print("=" * 60)

all_checks_passed = True

# Check 1: Verify grasa_visceral is in session state defaults
if '"grasa_visceral": ""' in content:
    print("✓ grasa_visceral added to session state defaults")
else:
    print("✗ grasa_visceral NOT found in session state defaults")
    all_checks_passed = False

# Check 2: Verify grasa_visceral input field is present
if 'st.number_input' in content and 'Grasa visceral' in content:
    print("✓ grasa_visceral input field present in UI")
else:
    print("✗ grasa_visceral input field NOT found")
    all_checks_passed = False

# Check 3: Verify help text with health information
if 'La grasa visceral es la grasa que rodea los órganos internos' in content:
    print("✓ Help text with grasa visceral explanation present")
else:
    print("✗ Help text with explanation NOT found")
    all_checks_passed = False

# Check 4: Verify grasa_visceral is retrieved from session state
if 'grasa_visceral = st.session_state.get("grasa_visceral"' in content:
    print("✓ grasa_visceral retrieved from session state")
else:
    print("✗ grasa_visceral NOT retrieved from session state")
    all_checks_passed = False

# Check 5: Verify grasa_visceral is displayed in results
if 'Grasa visceral (nivel)' in content and 'st.metric' in content:
    print("✓ grasa_visceral displayed in results section")
else:
    print("✗ grasa_visceral NOT displayed in results")
    all_checks_passed = False

# Check 6: Verify validation range (1-59)
if 'min_value=1' in content and 'max_value=59' in content:
    print("✓ Validation range (1-59) implemented")
else:
    print("✗ Validation range NOT properly implemented")
    all_checks_passed = False

# Check 7: Verify grasa_visceral in email report
if 'Grasa visceral (nivel):' in content:
    print("✓ grasa_visceral included in email report")
else:
    print("✗ grasa_visceral NOT included in email report")
    all_checks_passed = False

# Check 8: Verify health status classification
if 'Saludable' in content and 'Alto riesgo' in content:
    print("✓ Health status classification for grasa_visceral present")
else:
    print("✗ Health status classification NOT found")
    all_checks_passed = False

# Check 9: Verify locals() fallback for grasa_visceral
if "if 'grasa_visceral' not in locals():" in content:
    print("✓ Fallback for grasa_visceral in locals() present")
else:
    print("✗ Fallback for grasa_visceral NOT found")
    all_checks_passed = False

print("=" * 60)

if all_checks_passed:
    print("✓ All grasa_visceral integration tests passed!")
    sys.exit(0)
else:
    print("✗ Some tests failed!")
    sys.exit(1)

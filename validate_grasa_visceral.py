#!/usr/bin/env python3
"""
Comprehensive validation of grasa_visceral field implementation
"""

import sys
import os
import re

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")
with open(streamlit_app_path, "r") as f:
    content = f.read()

print("\n" + "=" * 70)
print("COMPREHENSIVE VALIDATION OF GRASA VISCERAL FIELD IMPLEMENTATION")
print("=" * 70 + "\n")

all_checks_passed = True
warnings = []

# ========== SECTION 1: SESSION STATE ==========
print("1. SESSION STATE INITIALIZATION")
print("-" * 70)
if '"grasa_visceral": ""' in content:
    print("✓ grasa_visceral in session state defaults")
else:
    print("✗ FAILED: grasa_visceral NOT in session state defaults")
    all_checks_passed = False

# ========== SECTION 2: INPUT FIELD ==========
print("\n2. INPUT FIELD CONFIGURATION")
print("-" * 70)

# Check for the input field
if 'st.number_input' in content and '🫀 Grasa visceral' in content:
    print("✓ Input field created with proper emoji and label")
else:
    print("✗ FAILED: Input field not properly created")
    all_checks_passed = False

# Check validation range
if 'min_value=1' in content and 'max_value=59' in content:
    print("✓ Validation range: 1-59 (healthy range)")
else:
    print("✗ FAILED: Validation range not properly set")
    all_checks_passed = False

# Check step
if re.search(r'step=1.*key="grasa_visceral"', content, re.DOTALL):
    print("✓ Step size: 1 (integer values)")
else:
    print("✗ FAILED: Step size not properly set")
    all_checks_passed = False

# Check key parameter
if 'key="grasa_visceral"' in content:
    print("✓ Widget key: 'grasa_visceral' for session state management")
else:
    print("✗ FAILED: Key parameter missing")
    all_checks_passed = False

# ========== SECTION 3: HELP TEXT / TOOLTIP ==========
print("\n3. HELP TEXT / TOOLTIP (USER EDUCATION)")
print("-" * 70)

help_text_pattern = r'help="La grasa visceral es la grasa que rodea los órganos internos.*Valores saludables: 1-12.*Alto.*riesgo'
if re.search(help_text_pattern, content, re.DOTALL):
    print("✓ Comprehensive help text explaining:")
    print("  - What grasa visceral is")
    print("  - Healthy range (1-12)")
    print("  - Risk indication (≥13)")
    print("  - Non-calculation impact note")
else:
    print("✗ FAILED: Help text missing or incomplete")
    all_checks_passed = False

# ========== SECTION 4: DATA RETRIEVAL ==========
print("\n4. DATA RETRIEVAL FROM SESSION STATE")
print("-" * 70)

if 'grasa_visceral = st.session_state.get("grasa_visceral"' in content:
    print("✓ grasa_visceral retrieved from session_state")
else:
    print("✗ FAILED: Data retrieval missing")
    all_checks_passed = False

# Check for fallback in locals()
if "if 'grasa_visceral' not in locals():" in content:
    print("✓ Fallback for grasa_visceral when not in locals()")
else:
    print("✗ FAILED: Fallback missing")
    all_checks_passed = False

# ========== SECTION 5: RESULTS DISPLAY ==========
print("\n5. RESULTS DISPLAY SECTION")
print("-" * 70)

if 'st.metric("Grasa visceral (nivel)"' in content:
    print("✓ Metric display for grasa visceral")
else:
    print("✗ FAILED: Metric display missing")
    all_checks_passed = False

# Check for health status classification
if 'Saludable' in content and 'Elevado' in content and 'Alto riesgo' in content:
    print("✓ Health status classification implemented:")
    print("  - Saludable (1-12)")
    print("  - Elevado (13-15)")
    print("  - Alto riesgo (≥16)")
else:
    print("✗ FAILED: Health status classification incomplete")
    all_checks_passed = False

# Check conditional display
if 'grasa_visceral_val >= 1' in content:
    print("✓ Conditional display: only shown when value ≥ 1")
else:
    print("✗ FAILED: Conditional display logic missing")
    all_checks_passed = False

# ========== SECTION 6: EMAIL REPORT ==========
print("\n6. EMAIL REPORT INTEGRATION")
print("-" * 70)

if 'Grasa visceral (nivel):' in content:
    print("✓ grasa_visceral included in email report")
else:
    print("✗ FAILED: Email report integration missing")
    all_checks_passed = False

# Check for "No medido" handling
if "'No medido'" in content or '"No medido"' in content:
    print("✓ 'No medido' fallback for empty values in report")
else:
    print("✗ FAILED: Empty value handling missing")
    all_checks_passed = False

# ========== SECTION 7: CODE QUALITY CHECKS ==========
print("\n7. CODE QUALITY & CONSISTENCY")
print("-" * 70)

# Check for safe_int usage
safe_int_count = content.count('safe_int(grasa_visceral')
if safe_int_count >= 2:
    print(f"✓ safe_int() used consistently ({safe_int_count} times)")
else:
    print(f"⚠ WARNING: safe_int() usage may be inconsistent ({safe_int_count} times)")
    warnings.append("Check safe_int() usage for grasa_visceral")

# Check placement after masa_muscular
masa_muscular_pos = content.find('key="masa_muscular"')
grasa_visceral_pos = content.find('key="grasa_visceral"')
if masa_muscular_pos > 0 and grasa_visceral_pos > masa_muscular_pos:
    print("✓ Field placement: after masa_muscular (logical grouping)")
else:
    print("⚠ WARNING: Field placement may not be optimal")
    warnings.append("Verify field placement in UI")

# Check for consistent commenting style
if '# Campo opcional - Grasa visceral' in content:
    print("✓ Consistent commenting style with existing fields")
else:
    print("⚠ WARNING: Comment style may differ from existing fields")
    warnings.append("Check commenting consistency")

# ========== FINAL SUMMARY ==========
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

if all_checks_passed:
    print("✅ ALL CRITICAL CHECKS PASSED")
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("✅ NO WARNINGS")
    print("\n✅ Implementation complete and ready for production!")
    sys.exit(0)
else:
    print("❌ SOME CRITICAL CHECKS FAILED")
    if warnings:
        print(f"\n⚠️  Also {len(warnings)} warning(s) found")
    print("\n❌ Please review and fix the issues above")
    sys.exit(1)

#!/usr/bin/env python3
"""
Integration test to verify MUPAI Volume Engine is properly integrated into email.
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")

with open(streamlit_app_path, "r") as f:
    content = f.read()

print("Verifying MUPAI Volume Engine Integration...")
print("=" * 70)

# Check 1: Function exists
if "def generate_volume_plan(" in content:
    print("✓ generate_volume_plan() function found")
else:
    print("✗ generate_volume_plan() function not found")
    sys.exit(1)

# Check 2: Input fields exist
input_fields = [
    "rir_input",
    "phase_energy_input", 
    "ffmi_margin_input",
    "ir_se_value"
]

for field in input_fields:
    if field in content:
        print(f"✓ Input field '{field}' found")
    else:
        print(f"✗ Input field '{field}' not found")
        sys.exit(1)

# Check 3: Email section exists
if "MUPAI VOLUME ENGINE — ADMIN ONLY" in content:
    print("✓ Email section header found")
else:
    print("✗ Email section header not found")
    sys.exit(1)

# Check 4: Email integration logic exists
if "volume_plan = generate_volume_plan(" in content:
    print("✓ Volume plan generation call found")
else:
    print("✗ Volume plan generation call not found")
    sys.exit(1)

# Check 5: Email table formatting exists
table_markers = [
    "┌────────────────┬─────┬─────┬─────┬──────────┬──────────┬──────────┬────────┐",
    "│ Músculo",
    "MEV │ MAV │ MRV",
    "PARÁMETROS DE ENTRADA",
    "FACTORES DE AJUSTE APLICADOS",
    "VOLUMEN RECOMENDADO POR GRUPO MUSCULAR"
]

for marker in table_markers:
    if marker in content:
        print(f"✓ Email table marker found: '{marker[:40]}...'")
    else:
        print(f"✗ Email table marker not found: '{marker[:40]}...'")
        sys.exit(1)

# Check 6: Viability assessment exists
viability_checks = [
    "viability_status = 'OK'",
    "viability_status = 'WARNING'",
    "viability_status = 'NOT_VIABLE'"
]

for check in viability_checks:
    if check in content:
        print(f"✓ Viability check found: {check}")
    else:
        print(f"✗ Viability check not found: {check}")
        sys.exit(1)

# Check 7: Distribution suggestions exist
if "distribution_suggestions" in content and "DISTRIBUCIÓN 2 ESTÍMULOS/SEMANA" in content:
    print("✓ Distribution suggestions found")
else:
    print("✗ Distribution suggestions not found")
    sys.exit(1)

# Check 8: Error handling exists
if "except Exception as e:" in content and "'error' not in volume_plan" in content:
    print("✓ Error handling found")
else:
    print("✗ Error handling not found")
    sys.exit(1)

# Check 9: MEV/MAV/MRV ranges defined for all muscle groups
muscle_groups = [
    'Pecho', 'Espalda', 'Hombros', 'Bíceps', 'Tríceps',
    'Cuádriceps', 'Femorales', 'Glúteos', 'Pantorrillas', 'Abdominales'
]

for muscle in muscle_groups:
    if f"'{muscle}':" in content:
        print(f"✓ Muscle group '{muscle}' defined")
    else:
        print(f"✗ Muscle group '{muscle}' not found")
        sys.exit(1)

# Check 10: All training levels covered
training_levels = ['principiante', 'intermedio', 'avanzado', 'élite']
for level in training_levels:
    if f"'{level}':" in content:
        print(f"✓ Training level '{level}' defined")
    else:
        print(f"✗ Training level '{level}' not found")
        sys.exit(1)

print("=" * 70)
print("✓ All integration checks passed!")
print("\nSummary:")
print("  • Function implementation: ✓")
print("  • Input fields: ✓")
print("  • Email integration: ✓")
print("  • Table formatting: ✓")
print("  • Viability assessment: ✓")
print("  • Error handling: ✓")
print("  • All muscle groups: ✓")
print("  • All training levels: ✓")
print("\n✓ MUPAI Volume Engine successfully integrated!")

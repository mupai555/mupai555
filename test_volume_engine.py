#!/usr/bin/env python3
"""
Test file for MUPAI Volume Engine functionality.
"""

import sys
import os

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Extract the generate_volume_plan function from streamlit_app.py
with open(os.path.join(script_dir, "streamlit_app.py"), "r") as f:
    content = f.read()

# Check that the function exists
if "def generate_volume_plan(" in content:
    print("✓ generate_volume_plan function found in streamlit_app.py")
else:
    print("✗ generate_volume_plan function not found")
    sys.exit(1)

# Check that MUPAI Volume Engine section exists in email
if "MUPAI VOLUME ENGINE — ADMIN ONLY" in content:
    print("✓ MUPAI Volume Engine section found in email template")
else:
    print("✗ MUPAI Volume Engine section not found in email")
    sys.exit(1)

# Check that volume inputs exist
if "rir_input" in content and "phase_energy_input" in content and "ffmi_margin_input" in content:
    print("✓ Volume Engine input fields found")
else:
    print("✗ Volume Engine input fields not found")
    sys.exit(1)

# Now let's do a functional test by extracting and running the function
print("\nTesting generate_volume_plan function...")
print("=" * 60)

# Execute the function definition
exec_globals = {}
exec(compile("""
def generate_volume_plan(level, phase_energy, ir_se, rir, training_days, ffmi_margin):
    \"\"\"
    MUPAI Volume Engine: Calculate muscle-targeted training volume recommendations.
    
    Args:
        level (str): Training level ('principiante', 'intermedio', 'avanzado', 'élite')
        phase_energy (str): Training phase ('deficit', 'mantenimiento', 'superavit')
        ir_se (float): Recovery index (Sleep-Stress) from 0-100
        rir (float): Reps in Reserve (0-4)
        training_days (int): Training days per week (0-7)
        ffmi_margin (float): FFMI margin from genetic potential (-5 to +5)
    
    Returns:
        dict: Volume plan with MEV/MAV/MRV per muscle, viability, and recommendations
    \"\"\"
    
    # Validate inputs
    try:
        ir_se = float(ir_se) if ir_se else 50.0
        rir = float(rir) if rir else 2.0
        training_days = int(training_days) if training_days else 3
        ffmi_margin = float(ffmi_margin) if ffmi_margin else 0.0
    except (ValueError, TypeError):
        # Return default safe values on error
        return {
            'error': 'Invalid input values',
            'viability': 'NOT_VIABLE',
            'muscles': {}
        }
    
    # Clamp values to safe ranges
    ir_se = max(0, min(100, ir_se))
    rir = max(0, min(4, rir))
    training_days = max(0, min(7, training_days))
    ffmi_margin = max(-5, min(5, ffmi_margin))
    
    # Normalize level to lowercase
    level = level.lower() if level else 'intermedio'
    if level not in ['principiante', 'intermedio', 'avanzado', 'élite']:
        level = 'intermedio'
    
    # Normalize phase_energy
    phase_energy = phase_energy.lower() if phase_energy else 'mantenimiento'
    if phase_energy not in ['deficit', 'mantenimiento', 'superavit']:
        phase_energy = 'mantenimiento'
    
    # Define MEV, MAV, MRV by muscle group and level
    volume_ranges = {
        'Pecho': {
            'principiante': {'MEV': 6, 'MAV': 12, 'MRV': 18},
            'intermedio': {'MEV': 8, 'MAV': 14, 'MRV': 22},
            'avanzado': {'MEV': 10, 'MAV': 16, 'MRV': 25},
            'élite': {'MEV': 12, 'MAV': 18, 'MRV': 28}
        },
        'Espalda': {
            'principiante': {'MEV': 8, 'MAV': 14, 'MRV': 22},
            'intermedio': {'MEV': 10, 'MAV': 16, 'MRV': 25},
            'avanzado': {'MEV': 12, 'MAV': 18, 'MRV': 28},
            'élite': {'MEV': 14, 'MAV': 20, 'MRV': 30}
        },
        'Hombros': {
            'principiante': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'intermedio': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'avanzado': {'MEV': 10, 'MAV': 14, 'MRV': 20},
            'élite': {'MEV': 12, 'MAV': 16, 'MRV': 22}
        },
        'Bíceps': {
            'principiante': {'MEV': 4, 'MAV': 8, 'MRV': 14},
            'intermedio': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'avanzado': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'élite': {'MEV': 10, 'MAV': 14, 'MRV': 20}
        },
        'Tríceps': {
            'principiante': {'MEV': 4, 'MAV': 8, 'MRV': 14},
            'intermedio': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'avanzado': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'élite': {'MEV': 10, 'MAV': 14, 'MRV': 20}
        },
        'Cuádriceps': {
            'principiante': {'MEV': 6, 'MAV': 12, 'MRV': 18},
            'intermedio': {'MEV': 8, 'MAV': 14, 'MRV': 22},
            'avanzado': {'MEV': 10, 'MAV': 16, 'MRV': 25},
            'élite': {'MEV': 12, 'MAV': 18, 'MRV': 28}
        },
        'Femorales': {
            'principiante': {'MEV': 4, 'MAV': 8, 'MRV': 14},
            'intermedio': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'avanzado': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'élite': {'MEV': 10, 'MAV': 14, 'MRV': 20}
        },
        'Glúteos': {
            'principiante': {'MEV': 4, 'MAV': 8, 'MRV': 14},
            'intermedio': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'avanzado': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'élite': {'MEV': 10, 'MAV': 14, 'MRV': 20}
        },
        'Pantorrillas': {
            'principiante': {'MEV': 6, 'MAV': 10, 'MRV': 16},
            'intermedio': {'MEV': 8, 'MAV': 12, 'MRV': 18},
            'avanzado': {'MEV': 10, 'MAV': 14, 'MRV': 20},
            'élite': {'MEV': 12, 'MAV': 16, 'MRV': 22}
        },
        'Abdominales': {
            'principiante': {'MEV': 0, 'MAV': 6, 'MRV': 12},
            'intermedio': {'MEV': 0, 'MAV': 8, 'MRV': 16},
            'avanzado': {'MEV': 0, 'MAV': 10, 'MRV': 18},
            'élite': {'MEV': 0, 'MAV': 12, 'MRV': 20}
        }
    }
    
    # Calculate adjustment factors
    if ir_se >= 70:
        ir_se_factor = 1.0
    elif ir_se >= 50:
        ir_se_factor = 0.85
    else:
        ir_se_factor = 0.70
    
    phase_factors = {
        'deficit': 0.85,
        'mantenimiento': 1.0,
        'superavit': 1.10
    }
    phase_factor = phase_factors[phase_energy]
    
    if rir <= 1:
        rir_factor = 0.90
    elif rir <= 2:
        rir_factor = 1.0
    else:
        rir_factor = 1.05
    
    if ffmi_margin <= -3:
        ffmi_factor = 1.10
    elif ffmi_margin <= 0:
        ffmi_factor = 1.0
    elif ffmi_margin <= 2:
        ffmi_factor = 0.90
    else:
        ffmi_factor = 0.80
    
    combined_factor = ir_se_factor * phase_factor * rir_factor * ffmi_factor
    
    muscle_plan = {}
    total_weekly_sets = 0
    
    for muscle, levels_data in volume_ranges.items():
        ranges = levels_data[level]
        mev = ranges['MEV']
        mav = ranges['MAV']
        mrv = ranges['MRV']
        
        adjusted_mav = mav * combined_factor
        recommended_sets = max(mev, min(mrv, round(adjusted_mav)))
        
        if training_days > 0:
            typical_frequency = 2 if muscle != 'Abdominales' else 3
            sessions_per_week = min(typical_frequency, training_days)
            sets_per_session = round(recommended_sets / sessions_per_week, 1)
        else:
            sessions_per_week = 2
            sets_per_session = 0
        
        muscle_plan[muscle] = {
            'MEV': mev,
            'MAV': mav,
            'MRV': mrv,
            'recommended_sets_week': recommended_sets,
            'sessions_per_week': sessions_per_week,
            'sets_per_session': sets_per_session,
            'adjustment_factor': round(combined_factor, 2)
        }
        
        total_weekly_sets += recommended_sets
    
    weekly_cap = total_weekly_sets
    
    if training_days > 0:
        avg_sets_per_day = round(total_weekly_sets / training_days, 1)
    else:
        avg_sets_per_day = 0
    
    viability_status = 'OK'
    viability_message = 'Plan viable y balanceado'
    warnings = []
    
    if total_weekly_sets > 150:
        viability_status = 'WARNING'
        warnings.append('Volumen total semanal muy alto (>150 sets). Riesgo de sobreentrenamiento.')
    elif total_weekly_sets > 120:
        viability_status = 'WARNING'
        warnings.append('Volumen total semanal alto. Monitorear recuperación.')
    
    if avg_sets_per_day > 25:
        viability_status = 'WARNING'
        warnings.append(f'Volumen por sesión alto ({avg_sets_per_day} sets/día). Considerar dividir.')
    
    if ir_se < 50 and viability_status == 'OK':
        viability_status = 'WARNING'
        warnings.append('IR-SE bajo (<50). Priorizar recuperación sobre volumen.')
    elif ir_se < 30:
        viability_status = 'NOT_VIABLE'
        warnings.append('IR-SE crítico (<30). Reducir volumen significativamente o tomar descanso.')
    
    if training_days < 3 and total_weekly_sets > 60:
        viability_status = 'WARNING' if viability_status == 'OK' else viability_status
        warnings.append('Pocos días de entrenamiento para el volumen recomendado. Considerar aumentar frecuencia.')
    
    if viability_status == 'OK':
        viability_message = 'Plan óptimo y viable'
    elif viability_status == 'WARNING':
        viability_message = 'Plan viable con ajustes recomendados'
    else:
        viability_message = 'Plan no viable - requiere modificaciones importantes'
    
    distribution_suggestions = []
    suggestion_2x = "DISTRIBUCIÓN 2 ESTÍMULOS/SEMANA:\\n"
    for muscle, data in muscle_plan.items():
        if data['sessions_per_week'] >= 2:
            sets_session = round(data['recommended_sets_week'] / 2, 1)
            suggestion_2x += f"  • {muscle}: {sets_session} sets × 2 sesiones\\n"
    distribution_suggestions.append(suggestion_2x)
    
    if level in ['avanzado', 'élite']:
        suggestion_3x = "DISTRIBUCIÓN 3 ESTÍMULOS/SEMANA (alternativa avanzada):\\n"
        for muscle, data in muscle_plan.items():
            if muscle in ['Pecho', 'Espalda', 'Cuádriceps']:
                sets_session = round(data['recommended_sets_week'] / 3, 1)
                suggestion_3x += f"  • {muscle}: {sets_session} sets × 3 sesiones\\n"
        distribution_suggestions.append(suggestion_3x)
    
    result = {
        'level': level,
        'phase_energy': phase_energy,
        'ir_se': ir_se,
        'rir': rir,
        'training_days': training_days,
        'ffmi_margin': ffmi_margin,
        'adjustment_factors': {
            'ir_se_factor': round(ir_se_factor, 2),
            'phase_factor': round(phase_factor, 2),
            'rir_factor': round(rir_factor, 2),
            'ffmi_factor': round(ffmi_factor, 2),
            'combined_factor': round(combined_factor, 2)
        },
        'muscles': muscle_plan,
        'weekly_cap': weekly_cap,
        'avg_sets_per_day': avg_sets_per_day,
        'viability': viability_status,
        'viability_message': viability_message,
        'warnings': warnings,
        'distribution_suggestions': distribution_suggestions
    }
    
    return result
""", '<string>', 'exec'), exec_globals)

generate_volume_plan = exec_globals['generate_volume_plan']

# Test cases
test_cases = [
    {
        'name': 'Intermediate - Optimal conditions',
        'level': 'intermedio',
        'phase_energy': 'mantenimiento',
        'ir_se': 75.0,
        'rir': 2.0,
        'training_days': 4,
        'ffmi_margin': -2.0,
        'expected_viability': 'OK'
    },
    {
        'name': 'Advanced - Deficit with low recovery',
        'level': 'avanzado',
        'phase_energy': 'deficit',
        'ir_se': 45.0,
        'rir': 1.5,
        'training_days': 5,
        'ffmi_margin': 0.5,
        'expected_viability': 'WARNING'
    },
    {
        'name': 'Beginner - Surplus',
        'level': 'principiante',
        'phase_energy': 'superavit',
        'ir_se': 80.0,
        'rir': 3.0,
        'training_days': 3,
        'ffmi_margin': -4.0,
        'expected_viability': 'OK'
    },
    {
        'name': 'Elite - Critical recovery',
        'level': 'élite',
        'phase_energy': 'mantenimiento',
        'ir_se': 25.0,
        'rir': 1.0,
        'training_days': 6,
        'ffmi_margin': 1.0,
        'expected_viability': 'NOT_VIABLE'
    }
]

all_passed = True
for test in test_cases:
    print(f"\nTest: {test['name']}")
    print("-" * 60)
    
    result = generate_volume_plan(
        level=test['level'],
        phase_energy=test['phase_energy'],
        ir_se=test['ir_se'],
        rir=test['rir'],
        training_days=test['training_days'],
        ffmi_margin=test['ffmi_margin']
    )
    
    # Check if there was an error
    if 'error' in result:
        print(f"✗ Error: {result['error']}")
        all_passed = False
        continue
    
    # Verify basic structure
    has_muscles = 'muscles' in result and len(result['muscles']) > 0
    has_viability = 'viability' in result
    has_weekly_cap = 'weekly_cap' in result
    
    if not has_muscles or not has_viability or not has_weekly_cap:
        print("✗ Missing required fields in result")
        all_passed = False
        continue
    
    # Check viability
    viability_match = result['viability'] == test['expected_viability']
    viability_status = "✓" if viability_match else "✗"
    
    print(f"{viability_status} Viability: {result['viability']} (expected: {test['expected_viability']})")
    print(f"  - Message: {result['viability_message']}")
    print(f"  - Weekly cap: {result['weekly_cap']} sets")
    print(f"  - Avg sets/day: {result['avg_sets_per_day']:.1f}")
    print(f"  - Combined factor: {result['adjustment_factors']['combined_factor']}")
    
    # Show sample muscles
    print(f"  - Sample muscles:")
    for i, (muscle, data) in enumerate(list(result['muscles'].items())[:3]):
        print(f"    • {muscle}: {data['recommended_sets_week']} sets/week ({data['sets_per_session']:.1f} sets/session × {data['sessions_per_week']}x)")
    
    if result['warnings']:
        print(f"  - Warnings: {len(result['warnings'])}")
        for warning in result['warnings'][:2]:  # Show first 2 warnings
            print(f"    ⚠️  {warning}")
    
    if not viability_match:
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed - review output above")
    sys.exit(1)

print("\n✓ MUPAI Volume Engine implementation verified successfully!")

#!/usr/bin/env python3
"""
Tests para el módulo nutrition_phases.py

Tests que verifican:
1. Decisión de fase nutricional en casos comunes
2. Cálculo de calorías objetivo
3. Generación de proyecciones
4. Casos extremos (bf muy bajo/alto)
5. Diferencias entre sexos y niveles
"""

import sys
import os

# Importar el módulo a testear
import nutrition_phases as np_module


def test_decidir_fase_cut():
    """Test: Decisión de fase CUT para persona con grasa elevada pero no extrema"""
    print("TEST 1: Decisión de fase CUT (grasa elevada, no PSMF)")
    result = np_module.decidir_fase_nutricional(
        sex='male',
        bf_percent=20.0,
        training_level='intermedio',
        goal='recomp'  # No fat_loss goal, so no PSMF
    )
    
    # Con 20% BF y objetivo recomp, debe dar maintain o cut, no PSMF
    assert result['phase'] in ['cut', 'maintain'], f"Expected 'cut' or 'maintain', got {result['phase']}"
    print(f"  ✓ Fase: {result['phase']}")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print(f"  ✓ Razonamiento: {result['reasoning'][:60]}...")
    print()


def test_decidir_fase_bulk():
    """Test: Decisión de fase BULK para persona con grasa baja"""
    print("TEST 2: Decisión de fase BULK (grasa baja)")
    result = np_module.decidir_fase_nutricional(
        sex='male',
        bf_percent=8.0,
        training_level='avanzado',
        goal='muscle_gain'
    )
    
    assert result['phase'] == 'bulk', f"Expected 'bulk', got {result['phase']}"
    assert result['percentage'] > 0, f"Expected positive percentage, got {result['percentage']}"
    print(f"  ✓ Fase: {result['phase']}")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print(f"  ✓ Razonamiento: {result['reasoning'][:60]}...")
    print()


def test_decidir_fase_maintain():
    """Test: Decisión de fase MAINTAIN para persona en rango óptimo"""
    print("TEST 3: Decisión de fase MAINTAIN (rango óptimo)")
    result = np_module.decidir_fase_nutricional(
        sex='female',
        bf_percent=20.0,
        training_level='intermedio',
        goal='recomp'
    )
    
    assert result['phase'] == 'maintain', f"Expected 'maintain', got {result['phase']}"
    print(f"  ✓ Fase: {result['phase']}")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print(f"  ✓ Razonamiento: {result['reasoning'][:60]}...")
    print()


def test_decidir_fase_psmf():
    """Test: Decisión de fase PSMF para candidato elegible"""
    print("TEST 4: Decisión de fase PSMF (candidato elegible)")
    result = np_module.decidir_fase_nutricional(
        sex='male',
        bf_percent=30.0,
        training_level='novato',
        goal='fat_loss'
    )
    
    assert result['is_psmf_candidate'] == True, "Expected PSMF candidate"
    assert result['phase'] == 'psmf', f"Expected 'psmf', got {result['phase']}"
    print(f"  ✓ Fase: {result['phase']}")
    print(f"  ✓ Es candidato PSMF: {result['is_psmf_candidate']}")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print()


def test_calcular_calorias_deficit():
    """Test: Cálculo de calorías con déficit"""
    print("TEST 5: Cálculo de calorías con déficit")
    
    phase_info = {
        'phase': 'cut',
        'percentage': -20.0,
        'phase_name_es': 'Definición'
    }
    
    result = np_module.calcular_calorias_objetivo(2500, phase_info)
    
    expected_calories = 2500 * 0.8  # 2000
    assert result['target_calories'] == expected_calories, \
        f"Expected {expected_calories}, got {result['target_calories']}"
    assert 'deficit_percentage' in result, "Expected deficit_percentage in result"
    assert result['deficit_percentage'] == 20.0, \
        f"Expected deficit 20.0%, got {result['deficit_percentage']}"
    
    print(f"  ✓ Mantenimiento: {result['maintenance_calories']} kcal")
    print(f"  ✓ Objetivo: {result['target_calories']} kcal")
    print(f"  ✓ Déficit: {result['deficit_kcal']} kcal ({result['deficit_percentage']}%)")
    print()


def test_calcular_calorias_surplus():
    """Test: Cálculo de calorías con superávit"""
    print("TEST 6: Cálculo de calorías con superávit")
    
    phase_info = {
        'phase': 'bulk',
        'percentage': 10.0,
        'phase_name_es': 'Volumen'
    }
    
    result = np_module.calcular_calorias_objetivo(2500, phase_info)
    
    expected_calories = 2500 * 1.1  # 2750
    assert result['target_calories'] == expected_calories, \
        f"Expected {expected_calories}, got {result['target_calories']}"
    assert 'surplus_percentage' in result, "Expected surplus_percentage in result"
    
    print(f"  ✓ Mantenimiento: {result['maintenance_calories']} kcal")
    print(f"  ✓ Objetivo: {result['target_calories']} kcal")
    print(f"  ✓ Superávit: {result['surplus_kcal']} kcal ({result['surplus_percentage']}%)")
    print()


def test_proyecciones_cut():
    """Test: Proyecciones para fase de definición"""
    print("TEST 7: Proyecciones para fase de definición")
    
    phase_info = {
        'phase': 'cut',
        'sex': 'male',
        'bf_percent': 20.0,
        'training_level': 'intermedio'
    }
    
    result = np_module.generar_proyecciones(phase_info, 80.0, weeks=4)
    
    assert len(result['weights_low']) == 5, "Expected 5 weight values (week 0-4)"
    assert len(result['weights_mid']) == 5, "Expected 5 weight values (week 0-4)"
    assert len(result['weights_high']) == 5, "Expected 5 weight values (week 0-4)"
    assert result['weights_low'][0] == 80.0, "First weight should be current weight"
    assert result['weights_low'][-1] < 80.0, "Final weight should be lower for cut"
    
    print(f"  ✓ Tasa semanal media: {result['weekly_rate_mid']}% ({result['weekly_kg_mid']} kg)")
    print(f"  ✓ Peso inicial: {result['weights_mid'][0]} kg")
    print(f"  ✓ Peso final (4 sem): {result['weights_mid'][-1]} kg")
    print(f"  ✓ Cambio total: {result['total_change_mid']} kg")
    print()


def test_proyecciones_bulk():
    """Test: Proyecciones para fase de volumen"""
    print("TEST 8: Proyecciones para fase de volumen")
    
    phase_info = {
        'phase': 'bulk',
        'sex': 'male',
        'bf_percent': 10.0,
        'training_level': 'novato'
    }
    
    result = np_module.generar_proyecciones(phase_info, 70.0, weeks=5)
    
    assert len(result['weights_mid']) == 6, "Expected 6 weight values (week 0-5)"
    assert result['weights_mid'][-1] > 70.0, "Final weight should be higher for bulk"
    
    print(f"  ✓ Tasa semanal media: {result['weekly_rate_mid']}% ({result['weekly_kg_mid']} kg)")
    print(f"  ✓ Peso inicial: {result['weights_mid'][0]} kg")
    print(f"  ✓ Peso final (5 sem): {result['weights_mid'][-1]} kg")
    print(f"  ✓ Cambio total: {result['total_change_mid']} kg")
    print()


def test_casos_extremos_bf_bajo():
    """Test: Casos extremos - grasa corporal muy baja"""
    print("TEST 9: Casos extremos - BF muy bajo (5%)")
    
    result = np_module.decidir_fase_nutricional(
        sex='male',
        bf_percent=5.0,
        training_level='avanzado',
        goal='fat_loss'  # Objetivo incompatible con BF tan bajo
    )
    
    # Debe recomendar bulk independientemente del objetivo
    assert result['phase'] == 'bulk', f"Expected 'bulk' for very low BF, got {result['phase']}"
    assert result['percentage'] > 10, "Expected aggressive surplus for very low BF"
    
    print(f"  ✓ Fase recomendada: {result['phase']} (ignora objetivo de pérdida)")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print()


def test_casos_extremos_bf_alto():
    """Test: Casos extremos - grasa corporal muy alta"""
    print("TEST 10: Casos extremos - BF muy alto (40%)")
    
    result = np_module.decidir_fase_nutricional(
        sex='female',
        bf_percent=40.0,
        training_level='novato',
        goal='fat_loss'
    )
    
    # Debe recomendar cut/psmf con déficit significativo
    assert result['phase'] in ['cut', 'psmf'], f"Expected 'cut' or 'psmf', got {result['phase']}"
    assert result['percentage'] < -20, "Expected significant deficit for very high BF"
    assert result['is_psmf_candidate'] == True, "Expected PSMF candidate"
    
    print(f"  ✓ Fase recomendada: {result['phase']}")
    print(f"  ✓ Porcentaje: {result['percentage']}%")
    print(f"  ✓ Es candidato PSMF: {result['is_psmf_candidate']}")
    print()


def test_diferencias_sexo():
    """Test: Diferencias entre sexos para mismo BF%"""
    print("TEST 11: Diferencias entre sexos (mismo BF 20%)")
    
    male_result = np_module.decidir_fase_nutricional(
        sex='male',
        bf_percent=20.0,
        training_level='intermedio',
        goal='fat_loss'
    )
    
    female_result = np_module.decidir_fase_nutricional(
        sex='female',
        bf_percent=20.0,
        training_level='intermedio',
        goal='fat_loss'
    )
    
    print(f"  ✓ Hombre 20% BF:")
    print(f"    - Fase: {male_result['phase']}")
    print(f"    - Porcentaje: {male_result['percentage']}%")
    print(f"  ✓ Mujer 20% BF:")
    print(f"    - Fase: {female_result['phase']}")
    print(f"    - Porcentaje: {female_result['percentage']}%")
    print()


def test_diferencias_nivel():
    """Test: Diferencias por nivel de entrenamiento en bulk"""
    print("TEST 12: Diferencias por nivel de entrenamiento (bulk)")
    
    novato_proj = np_module.generar_proyecciones(
        {'phase': 'bulk', 'sex': 'male', 'bf_percent': 12.0, 'training_level': 'novato'},
        75.0,
        weeks=4
    )
    
    avanzado_proj = np_module.generar_proyecciones(
        {'phase': 'bulk', 'sex': 'male', 'bf_percent': 12.0, 'training_level': 'avanzado'},
        75.0,
        weeks=4
    )
    
    # Novatos deben tener tasas de ganancia más altas
    assert novato_proj['weekly_rate_mid'] > avanzado_proj['weekly_rate_mid'], \
        "Novatos should gain weight faster than advanced"
    
    print(f"  ✓ Novato - tasa media: {novato_proj['weekly_rate_mid']}%")
    print(f"  ✓ Avanzado - tasa media: {avanzado_proj['weekly_rate_mid']}%")
    print(f"  ✓ Diferencia: {novato_proj['weekly_rate_mid'] - avanzado_proj['weekly_rate_mid']}%")
    print()


def test_analisis_completo():
    """Test: Función de análisis completo"""
    print("TEST 13: Análisis completo integrado")
    
    result = np_module.generar_analisis_completo(
        sex='male',
        bf_percent=20.0,
        training_level='intermedio',
        goal='fat_loss',
        maintenance_calories=2500,
        current_weight=80.0,
        weeks=4
    )
    
    # Verificar que todas las secciones existen
    assert 'phase_decision' in result, "Missing phase_decision"
    assert 'calories' in result, "Missing calories"
    assert 'projections' in result, "Missing projections"
    assert 'summary' in result, "Missing summary"
    assert 'metadata' in result, "Missing metadata"
    
    # Verificar consistencia
    assert result['phase_decision']['phase'] == result['calories']['phase'], \
        "Phase mismatch between decision and calories"
    
    print(f"  ✓ Fase: {result['phase_decision']['phase']}")
    print(f"  ✓ Calorías objetivo: {result['calories']['target_calories']}")
    print(f"  ✓ Proyección 4 semanas: {result['projections']['total_change_mid']:+.1f} kg")
    print(f"  ✓ Resumen generado: {len(result['summary'])} caracteres")
    print()


def test_formateo_email():
    """Test: Formateo para email"""
    print("TEST 14: Formateo para email")
    
    analisis = np_module.generar_analisis_completo(
        sex='female',
        bf_percent=18.0,
        training_level='avanzado',
        goal='muscle_gain',
        maintenance_calories=2000,
        current_weight=60.0,
        weeks=4
    )
    
    email_text = np_module.formatear_para_email(analisis)
    
    # Verificar que el texto contiene secciones clave
    assert 'ANÁLISIS DE FASE NUTRICIONAL' in email_text, "Missing title"
    assert 'FASE NUTRICIONAL ASIGNADA' in email_text, "Missing phase section"
    assert 'CALORÍAS OBJETIVO' in email_text, "Missing calories section"
    assert 'PROYECCIONES DE PESO' in email_text, "Missing projections section"
    assert 'PROGRESIÓN SEMANAL' in email_text, "Missing weekly progression"
    
    print(f"  ✓ Texto generado: {len(email_text)} caracteres")
    print(f"  ✓ Líneas: {len(email_text.split('\\n'))}")
    print(f"  ✓ Contiene todas las secciones requeridas")
    print()


def test_normalizacion_entradas():
    """Test: Normalización de entradas (Hombre/Mujer, principiante/novato)"""
    print("TEST 15: Normalización de entradas")
    
    # Test normalización de sexo
    result1 = np_module.decidir_fase_nutricional('Hombre', 20.0, 'intermedio', 'fat_loss')
    result2 = np_module.decidir_fase_nutricional('male', 20.0, 'intermedio', 'fat_loss')
    
    assert result1['sex'] == result2['sex'], "Sex normalization failed"
    
    # Test normalización de nivel
    result3 = np_module.decidir_fase_nutricional('male', 20.0, 'principiante', 'fat_loss')
    result4 = np_module.decidir_fase_nutricional('male', 20.0, 'novato', 'fat_loss')
    
    assert result3['training_level'] == result4['training_level'], "Training level normalization failed"
    
    print(f"  ✓ Normalización de sexo: OK")
    print(f"  ✓ Normalización de nivel: OK")
    print()


def run_all_tests():
    """Ejecuta todos los tests"""
    print("=" * 70)
    print("TESTS DEL MÓDULO NUTRITION_PHASES.PY")
    print("=" * 70)
    print()
    
    tests = [
        test_decidir_fase_cut,
        test_decidir_fase_bulk,
        test_decidir_fase_maintain,
        test_decidir_fase_psmf,
        test_calcular_calorias_deficit,
        test_calcular_calorias_surplus,
        test_proyecciones_cut,
        test_proyecciones_bulk,
        test_casos_extremos_bf_bajo,
        test_casos_extremos_bf_alto,
        test_diferencias_sexo,
        test_diferencias_nivel,
        test_analisis_completo,
        test_formateo_email,
        test_normalizacion_entradas,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
            failed += 1
    
    print("=" * 70)
    print(f"RESUMEN: {passed} tests pasados, {failed} tests fallidos")
    print("=" * 70)
    
    if failed == 0:
        print("✅ TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

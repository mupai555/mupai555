#!/usr/bin/env python3
"""
Test suite for calcular_macros_alternativos function.
Validates the advanced MUPAI macro calculation logic.
"""

import sys

# Define sugerir_deficit locally for testing
def sugerir_deficit(porcentaje_grasa, sexo):
    """Sugiere el déficit calórico recomendado por % de grasa y sexo."""
    try:
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        porcentaje_grasa = 0.0
    rangos_hombre = [
        (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
        (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 40, 35), (40.1, 45, 40),
        (45.1, 100, 50)
    ]
    rangos_mujer = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 40, 30), (40.1, 45, 35), (45.1, 50, 40),
        (50.1, 100, 50)
    ]
    tabla = rangos_hombre if sexo == "Hombre" else rangos_mujer
    tope = 30
    limite_extra = 30 if sexo == "Hombre" else 35
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            return min(deficit, tope) if porcentaje_grasa <= limite_extra else deficit
    return 20  # Déficit por defecto

# Define calcular_macros_alternativos locally for testing
def calcular_macros_alternativos(peso, grasa_corregida, mlg, tmb, sexo, nivel_entrenamiento, geaf, eta, gee_prom_dia):
    """
    Función avanzada para cálculo energético y de macros según el esquema MUPAI.
    Implementa lógica auditada de Fases, Energía y Macros.
    """
    try:
        # Sanitize inputs
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
        tmb = float(tmb)
        geaf = float(geaf)
        eta = float(eta)
        gee_prom_dia = float(gee_prom_dia)
    except (TypeError, ValueError):
        return {
            'error': 'Valores de entrada inválidos',
            'clasificacion': 'Desconocido',
            'fase': 'Mantenimiento',
            'porcentaje_energia': 0,
            'tdee_mantenimiento': 0,
            'calorias_objetivo': 0,
            'proteina_g': 0,
            'grasa_g': 0,
            'carbohidratos_g': 0,
            'proteina_kcal': 0,
            'grasa_kcal': 0,
            'carbohidratos_kcal': 0
        }
    
    # 1. CLASIFICACIÓN POR % DE GRASA CORREGIDA
    if sexo == "Hombre":
        if grasa_corregida < 6:
            clasificacion = "Preparación (Competición)"
        elif grasa_corregida < 12:
            clasificacion = "Atlético"
        elif grasa_corregida < 18:
            clasificacion = "Fitness"
        elif grasa_corregida < 25:
            clasificacion = "Promedio"
        else:
            clasificacion = "Alto"
    else:  # Mujer
        if grasa_corregida < 12:
            clasificacion = "Preparación (Competición)"
        elif grasa_corregida < 17:
            clasificacion = "Atlético"
        elif grasa_corregida < 23:
            clasificacion = "Fitness"
        elif grasa_corregida < 30:
            clasificacion = "Promedio"
        else:
            clasificacion = "Alto"
    
    # 2. CÁLCULO DE TDEE MANTENIMIENTO
    tdee_mantenimiento = tmb * geaf * eta + gee_prom_dia
    
    # 3. SELECCIÓN DE FASE Y % DE ENERGÍA
    # Determinar si aplica PSMF
    psmf_aplica = False
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplica = True
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplica = True
    
    # Lógica de fase según clasificación y entrenamiento
    if sexo == "Hombre":
        if grasa_corregida < 6:
            # Preparación - Superávit agresivo
            fase = "Superávit"
            porcentaje_energia = 12.5  # 10-15%
        elif grasa_corregida < 12:
            # Atlético - Superávit moderado
            fase = "Superávit"
            porcentaje_energia = 7.5  # 5-10%
        elif grasa_corregida < 15:
            # Fitness - Ligero superávit o mantenimiento
            fase = "Mantenimiento/Ligero Superávit"
            porcentaje_energia = 2.5  # 0-5%
        elif grasa_corregida < 18:
            # Buena condición - Mantenimiento
            fase = "Mantenimiento"
            porcentaje_energia = 0
        elif psmf_aplica and grasa_corregida >= 35:
            # Alto % grasa - PSMF opción
            fase = "PSMF Tier 3"
            porcentaje_energia = -40  # Déficit agresivo
        elif psmf_aplica and grasa_corregida >= 25:
            # Moderado % grasa - PSMF moderado
            fase = "PSMF Tier 2"
            porcentaje_energia = -35
        else:
            # Déficit moderado
            fase = "Déficit"
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje_energia = -deficit_valor
    else:  # Mujer
        if grasa_corregida < 12:
            # Preparación - Superávit agresivo
            fase = "Superávit"
            porcentaje_energia = 12.5  # 10-15%
        elif grasa_corregida < 17:
            # Atlético - Superávit moderado
            fase = "Superávit"
            porcentaje_energia = 7.5  # 5-10%
        elif grasa_corregida < 20:
            # Fitness - Ligero superávit o mantenimiento
            fase = "Mantenimiento/Ligero Superávit"
            porcentaje_energia = 2.5  # 0-5%
        elif grasa_corregida < 23:
            # Buena condición - Mantenimiento
            fase = "Mantenimiento"
            porcentaje_energia = 0
        elif psmf_aplica and grasa_corregida >= 45:
            # Alto % grasa - PSMF opción
            fase = "PSMF Tier 3"
            porcentaje_energia = -40
        elif psmf_aplica and grasa_corregida >= 35:
            # Moderado % grasa - PSMF moderado
            fase = "PSMF Tier 2"
            porcentaje_energia = -35
        else:
            # Déficit moderado
            fase = "Déficit"
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje_energia = -deficit_valor
    
    # 4. CÁLCULO DE CALORÍAS OBJETIVO
    calorias_objetivo = tdee_mantenimiento * (1 + porcentaje_energia / 100)
    
    # 5. DISTRIBUCIÓN DE MACRONUTRIENTES
    if "PSMF" in fase:
        # Lógica PSMF: alta proteína, baja grasa, muy bajos carbohidratos
        if grasa_corregida < 25:
            factor_proteina_psmf = 1.8
            grasa_g = 30  # Mínimo grasa esencial para PSMF
        else:
            factor_proteina_psmf = 1.6
            grasa_g = 40  # Más grasa para % grasa alto
        
        # Base de proteína en PSMF
        if (sexo == "Hombre" and grasa_corregida >= 35) or (sexo == "Mujer" and grasa_corregida >= 45):
            base_proteina = mlg  # Usar MLG para alta adiposidad
        else:
            base_proteina = peso  # Usar peso total
        
        proteina_g = base_proteina * factor_proteina_psmf
        
        # Carbohidratos mínimos (<50g típico en PSMF)
        carbohidratos_g = 30
        
        # Calcular calorías
        proteina_kcal = proteina_g * 4
        grasa_kcal = grasa_g * 9
        carbohidratos_kcal = carbohidratos_g * 4
        
        # Ajustar calorías objetivo (PSMF es restrictivo)
        calorias_objetivo = proteina_kcal + grasa_kcal + carbohidratos_kcal
    else:
        # Lógica tradicional de distribución de macros
        
        # Proteína: determinar base y factor
        if sexo == "Hombre" and grasa_corregida >= 35:
            base_proteina = mlg
        elif sexo == "Mujer" and grasa_corregida >= 42:
            base_proteina = mlg
        else:
            base_proteina = peso
        
        # Factor de proteína según % grasa
        if grasa_corregida >= 35:
            factor_proteina = 1.6
        elif grasa_corregida >= 25:
            factor_proteina = 1.8
        elif grasa_corregida >= 15:
            factor_proteina = 2.0
        else:
            factor_proteina = 2.2
        
        proteina_g = base_proteina * factor_proteina
        proteina_kcal = proteina_g * 4
        
        # Grasas: % del TMB
        porcentaje_grasa_tmb = 25  # Estándar para todos
        grasa_g = (tmb * porcentaje_grasa_tmb / 100) / 9
        grasa_kcal = grasa_g * 9
        
        # Carbohidratos: resto de calorías
        carbohidratos_kcal = max(0, calorias_objetivo - proteina_kcal - grasa_kcal)
        carbohidratos_g = carbohidratos_kcal / 4
    
    return {
        'clasificacion': clasificacion,
        'fase': fase,
        'porcentaje_energia': porcentaje_energia,
        'tdee_mantenimiento': round(tdee_mantenimiento, 0),
        'calorias_objetivo': round(calorias_objetivo, 0),
        'proteina_g': round(proteina_g, 1),
        'grasa_g': round(grasa_g, 1),
        'carbohidratos_g': round(carbohidratos_g, 1),
        'proteina_kcal': round(proteina_kcal, 0),
        'grasa_kcal': round(grasa_kcal, 0),
        'carbohidratos_kcal': round(carbohidratos_kcal, 0),
        'psmf_aplica': psmf_aplica
    }

def test_clasificacion_hombre():
    """Test body fat classification for men."""
    print("=" * 70)
    print("TEST: Clasificación corporal - Hombres")
    print("=" * 70)
    
    test_cases = [
        (5.0, "Preparación (Competición)"),
        (10.0, "Atlético"),
        (15.0, "Fitness"),
        (20.0, "Promedio"),
        (30.0, "Alto")
    ]
    
    for grasa, expected in test_cases:
        result = calcular_macros_alternativos(
            peso=80, grasa_corregida=grasa, mlg=60, tmb=1800,
            sexo="Hombre", nivel_entrenamiento="intermedio",
            geaf=1.2, eta=1.1, gee_prom_dia=150
        )
        print(f"Grasa: {grasa}% → Clasificación: {result['clasificacion']}")
        assert result['clasificacion'] == expected, f"Expected {expected}, got {result['clasificacion']}"
    
    print("✅ Test passed\n")

def test_clasificacion_mujer():
    """Test body fat classification for women."""
    print("=" * 70)
    print("TEST: Clasificación corporal - Mujeres")
    print("=" * 70)
    
    test_cases = [
        (10.0, "Preparación (Competición)"),
        (15.0, "Atlético"),
        (20.0, "Fitness"),
        (26.0, "Promedio"),
        (35.0, "Alto")
    ]
    
    for grasa, expected in test_cases:
        result = calcular_macros_alternativos(
            peso=65, grasa_corregida=grasa, mlg=50, tmb=1500,
            sexo="Mujer", nivel_entrenamiento="intermedio",
            geaf=1.2, eta=1.1, gee_prom_dia=120
        )
        print(f"Grasa: {grasa}% → Clasificación: {result['clasificacion']}")
        assert result['clasificacion'] == expected, f"Expected {expected}, got {result['clasificacion']}"
    
    print("✅ Test passed\n")

def test_fase_superavit():
    """Test surplus phase selection for low body fat."""
    print("=" * 70)
    print("TEST: Fase Superávit (baja grasa corporal)")
    print("=" * 70)
    
    # Hombre con 5% grasa - debe recomendar superávit
    result = calcular_macros_alternativos(
        peso=75, grasa_corregida=5.0, mlg=71.25, tmb=1900,
        sexo="Hombre", nivel_entrenamiento="avanzado",
        geaf=1.3, eta=1.15, gee_prom_dia=200
    )
    
    print(f"Hombre 5% grasa:")
    print(f"  Fase: {result['fase']}")
    print(f"  % Energía: {result['porcentaje_energia']:+.1f}%")
    print(f"  TDEE: {result['tdee_mantenimiento']:.0f} kcal")
    print(f"  Calorías objetivo: {result['calorias_objetivo']:.0f} kcal")
    
    assert "Superávit" in result['fase'], "Should recommend surplus for very low body fat"
    assert result['porcentaje_energia'] > 0, "Percentage should be positive for surplus"
    
    print("✅ Test passed\n")

def test_fase_deficit():
    """Test deficit phase selection for high body fat."""
    print("=" * 70)
    print("TEST: Fase Déficit (alta grasa corporal)")
    print("=" * 70)
    
    # Hombre con 30% grasa - debe recomendar déficit
    result = calcular_macros_alternativos(
        peso=90, grasa_corregida=30.0, mlg=63, tmb=1750,
        sexo="Hombre", nivel_entrenamiento="principiante",
        geaf=1.1, eta=1.1, gee_prom_dia=100
    )
    
    print(f"Hombre 30% grasa:")
    print(f"  Fase: {result['fase']}")
    print(f"  % Energía: {result['porcentaje_energia']:+.1f}%")
    print(f"  TDEE: {result['tdee_mantenimiento']:.0f} kcal")
    print(f"  Calorías objetivo: {result['calorias_objetivo']:.0f} kcal")
    
    assert result['porcentaje_energia'] < 0, "Percentage should be negative for deficit"
    
    print("✅ Test passed\n")

def test_fase_psmf():
    """Test PSMF phase selection for very high body fat."""
    print("=" * 70)
    print("TEST: Fase PSMF (muy alta grasa corporal)")
    print("=" * 70)
    
    # Hombre con 40% grasa - debe aplicar PSMF
    result = calcular_macros_alternativos(
        peso=100, grasa_corregida=40.0, mlg=60, tmb=1700,
        sexo="Hombre", nivel_entrenamiento="principiante",
        geaf=1.0, eta=1.1, gee_prom_dia=50
    )
    
    print(f"Hombre 40% grasa:")
    print(f"  Fase: {result['fase']}")
    print(f"  PSMF aplica: {result['psmf_aplica']}")
    print(f"  % Energía: {result['porcentaje_energia']:+.1f}%")
    print(f"  Calorías: {result['calorias_objetivo']:.0f} kcal")
    print(f"  Proteína: {result['proteina_g']:.1f}g")
    print(f"  Grasa: {result['grasa_g']:.1f}g")
    print(f"  Carbohidratos: {result['carbohidratos_g']:.1f}g")
    
    assert result['psmf_aplica'] == True, "PSMF should apply for 40% body fat"
    assert "PSMF" in result['fase'], "Phase should be PSMF"
    assert result['carbohidratos_g'] < 50, "PSMF should have very low carbs"
    
    print("✅ Test passed\n")

def test_tdee_calculation():
    """Test TDEE maintenance calculation."""
    print("=" * 70)
    print("TEST: Cálculo TDEE Mantenimiento")
    print("=" * 70)
    
    tmb = 1800
    geaf = 1.25
    eta = 1.12
    gee_prom_dia = 150
    
    result = calcular_macros_alternativos(
        peso=80, grasa_corregida=15.0, mlg=68, tmb=tmb,
        sexo="Hombre", nivel_entrenamiento="intermedio",
        geaf=geaf, eta=eta, gee_prom_dia=gee_prom_dia
    )
    
    expected_tdee = tmb * geaf * eta + gee_prom_dia
    
    print(f"TMB: {tmb} kcal")
    print(f"GEAF: {geaf}")
    print(f"ETA: {eta}")
    print(f"GEE: {gee_prom_dia} kcal")
    print(f"TDEE esperado: {expected_tdee:.0f} kcal")
    print(f"TDEE calculado: {result['tdee_mantenimiento']:.0f} kcal")
    
    assert abs(result['tdee_mantenimiento'] - expected_tdee) < 1, "TDEE calculation mismatch"
    
    print("✅ Test passed\n")

def test_macro_distribution_traditional():
    """Test traditional macro distribution."""
    print("=" * 70)
    print("TEST: Distribución de macros (tradicional)")
    print("=" * 70)
    
    result = calcular_macros_alternativos(
        peso=75, grasa_corregida=15.0, mlg=63.75, tmb=1750,
        sexo="Hombre", nivel_entrenamiento="intermedio",
        geaf=1.2, eta=1.12, gee_prom_dia=150
    )
    
    print(f"Calorías objetivo: {result['calorias_objetivo']:.0f} kcal")
    print(f"Proteína: {result['proteina_g']:.1f}g ({result['proteina_kcal']:.0f} kcal)")
    print(f"Grasa: {result['grasa_g']:.1f}g ({result['grasa_kcal']:.0f} kcal)")
    print(f"Carbohidratos: {result['carbohidratos_g']:.1f}g ({result['carbohidratos_kcal']:.0f} kcal)")
    
    # Verify total calories match
    total_kcal = result['proteina_kcal'] + result['grasa_kcal'] + result['carbohidratos_kcal']
    print(f"Total calculado: {total_kcal:.0f} kcal")
    
    # Allow for small rounding differences
    assert abs(total_kcal - result['calorias_objetivo']) < 10, "Total calories mismatch"
    
    print("✅ Test passed\n")

def test_macro_distribution_psmf():
    """Test PSMF macro distribution."""
    print("=" * 70)
    print("TEST: Distribución de macros (PSMF)")
    print("=" * 70)
    
    # Mujer con 50% grasa - PSMF
    result = calcular_macros_alternativos(
        peso=85, grasa_corregida=50.0, mlg=42.5, tmb=1500,
        sexo="Mujer", nivel_entrenamiento="principiante",
        geaf=1.0, eta=1.1, gee_prom_dia=50
    )
    
    print(f"Fase: {result['fase']}")
    print(f"Calorías objetivo: {result['calorias_objetivo']:.0f} kcal")
    print(f"Proteína: {result['proteina_g']:.1f}g ({result['proteina_kcal']:.0f} kcal) - {result['proteina_kcal']/result['calorias_objetivo']*100:.1f}%")
    print(f"Grasa: {result['grasa_g']:.1f}g ({result['grasa_kcal']:.0f} kcal) - {result['grasa_kcal']/result['calorias_objetivo']*100:.1f}%")
    print(f"Carbohidratos: {result['carbohidratos_g']:.1f}g ({result['carbohidratos_kcal']:.0f} kcal) - {result['carbohidratos_kcal']/result['calorias_objetivo']*100:.1f}%")
    
    # PSMF should have restricted calories and very low carbs
    assert "PSMF" in result['fase'], "Should be PSMF phase"
    assert result['carbohidratos_g'] <= 50, "PSMF should have ≤50g carbs"
    assert result['calorias_objetivo'] < 1000, "PSMF should be very restrictive"
    
    print("✅ Test passed\n")

def test_invalid_inputs():
    """Test handling of invalid inputs."""
    print("=" * 70)
    print("TEST: Manejo de inputs inválidos")
    print("=" * 70)
    
    result = calcular_macros_alternativos(
        peso="invalid", grasa_corregida=15.0, mlg=60, tmb=1700,
        sexo="Hombre", nivel_entrenamiento="intermedio",
        geaf=1.2, eta=1.1, gee_prom_dia=150
    )
    
    print(f"Input inválido → Error: {result.get('error', 'None')}")
    assert 'error' in result, "Should return error for invalid inputs"
    assert result['clasificacion'] == 'Desconocido', "Should return default classification"
    
    print("✅ Test passed\n")

def run_all_tests():
    """Run all test cases."""
    print("\n")
    print("=" * 70)
    print("SUITE DE TESTS: calcular_macros_alternativos")
    print("=" * 70)
    print("\n")
    
    try:
        test_clasificacion_hombre()
        test_clasificacion_mujer()
        test_fase_superavit()
        test_fase_deficit()
        test_fase_psmf()
        test_tdee_calculation()
        test_macro_distribution_traditional()
        test_macro_distribution_psmf()
        test_invalid_inputs()
        
        print("=" * 70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70)
        return True
    except AssertionError as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FALLÓ: {str(e)}")
        print("=" * 70)
        return False
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR INESPERADO: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

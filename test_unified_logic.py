#!/usr/bin/env python3
"""
Test suite for unified MUPAI macro calculation logic.
Tests all new functions added for the unified calculation system.
"""

import sys
import os

# Mock streamlit to avoid initialization issues
class MockStreamlit:
    class secrets:
        @staticmethod
        def get(key, default=None):
            return default
    
    class session_state:
        _state = {}
        @classmethod
        def get(cls, key, default=None):
            return cls._state.get(key, default)
        @classmethod
        def __setitem__(cls, key, value):
            cls._state[key] = value
        @classmethod
        def __getitem__(cls, key):
            return cls._state[key]
        @classmethod
        def __contains__(cls, key):
            return key in cls._state

sys.modules['streamlit'] = type(sys)('streamlit')
sys.modules['streamlit'].secrets = MockStreamlit.secrets
sys.modules['streamlit'].session_state = MockStreamlit.session_state()

sys.path.insert(0, '/home/runner/work/mupai555/mupai555')

# Import only the functions we need by loading the file as text and extracting them
import importlib.util
spec = importlib.util.spec_from_file_location("streamlit_app", "/home/runner/work/mupai555/mupai555/streamlit_app.py")
streamlit_app = importlib.util.module_from_spec(spec)

# Define mock variables before loading
streamlit_app.nombre = ""
streamlit_app.telefono = ""
streamlit_app.email_cliente = ""
streamlit_app.edad = 0
streamlit_app.peso = 0
streamlit_app.estatura = 0
streamlit_app.grasa_corporal = 0
streamlit_app.sexo = "Hombre"
streamlit_app.ingesta_calorica = 0
streamlit_app.proteina_g = 0
streamlit_app.grasa_g = 0
streamlit_app.carbo_g = 0
streamlit_app.proteina_kcal = 0
streamlit_app.grasa_kcal = 0
streamlit_app.carbo_kcal = 0
streamlit_app.fbeo = 1.0
streamlit_app.modo_ffmi = "GREEN"
streamlit_app.nivel_ffmi = ""
streamlit_app.ffmi_genetico_max = 0
streamlit_app.porc_potencial = 0
streamlit_app.ffmi = 0
streamlit_app.fmi = 0
streamlit_app.grasa_visceral = 0

try:
    spec.loader.exec_module(streamlit_app)
except (NameError, AttributeError) as e:
    # Some errors are expected due to streamlit-specific code
    print(f"Warning: {e}")
    pass

from streamlit_app import (
    calcular_gasto_energetico_total,
    calcular_eta,
    calcular_gee,
    calcular_fbeo,
    determinar_fase_nutricional_unificada,
    calcular_rangos_deficit_superavit,
    calcular_proteina_dinamica,
    calcular_psmf_extendida,
    calcular_ciclado_semanal,
    evaluar_micronutrientes_checklist,
    evaluar_micronutrientes_numerico,
    generar_reporte_unificado_mupai
)

def test_calcular_gasto_energetico_total():
    """Test GET calculation (TMB × GEAF)"""
    print("\n=== Testing calcular_gasto_energetico_total ===")
    
    # Test case 1: Sedentary
    tmb = 1800
    geaf = 1.00
    get = calcular_gasto_energetico_total(tmb, geaf)
    print(f"TMB: {tmb}, GEAF: {geaf} => GET: {get}")
    assert get == 1800, f"Expected 1800, got {get}"
    
    # Test case 2: Very active
    tmb = 1800
    geaf = 1.45
    get = calcular_gasto_energetico_total(tmb, geaf)
    print(f"TMB: {tmb}, GEAF: {geaf} => GET: {get}")
    assert get == 2610, f"Expected 2610, got {get}"
    
    print("✓ calcular_gasto_energetico_total passed")

def test_calcular_eta():
    """Test ETA calculation (10% of intake)"""
    print("\n=== Testing calcular_eta ===")
    
    ingesta = 2000
    eta = calcular_eta(ingesta)
    print(f"Ingesta: {ingesta} kcal => ETA: {eta} kcal")
    assert eta == 200, f"Expected 200, got {eta}"
    
    print("✓ calcular_eta passed")

def test_calcular_gee():
    """Test GEE calculation (Exercise Energy Expenditure)"""
    print("\n=== Testing calcular_gee ===")
    
    # Test sedentary
    gee = calcular_gee("Sedentario", 70)
    print(f"Sedentario, 70kg => GEE: {gee} kcal")
    assert gee == 0, f"Expected 0, got {gee}"
    
    # Test active
    gee = calcular_gee("Activo", 70)
    print(f"Activo, 70kg => GEE: {gee} kcal")
    assert gee == 300, f"Expected 300, got {gee}"
    
    # Test weight adjustment
    gee = calcular_gee("Activo", 80)
    print(f"Activo, 80kg => GEE: {gee} kcal")
    expected = 300 * (80/70)
    assert abs(gee - expected) < 1, f"Expected {expected}, got {gee}"
    
    print("✓ calcular_gee passed")

def test_calcular_fbeo():
    """Test FBEO calculation (10% of GEE)"""
    print("\n=== Testing calcular_fbeo ===")
    
    gee = 300
    fbeo = calcular_fbeo(gee)
    print(f"GEE: {gee} kcal => FBEO: {fbeo} kcal")
    assert fbeo == 30, f"Expected 30, got {fbeo}"
    
    print("✓ calcular_fbeo passed")

def test_determinar_fase_nutricional_unificada():
    """Test nutritional phase determination"""
    print("\n=== Testing determinar_fase_nutricional_unificada ===")
    
    # Test high BF% man - should recommend deficit
    fase = determinar_fase_nutricional_unificada("Hombre", 30.0)
    print(f"Hombre, 30% BF => Fase: {fase['fase']}, Ajuste: {fase['deficit_superavit_pct']}%")
    assert fase['deficit_superavit_pct'] < 0, "High BF% should recommend deficit"
    
    # Test low BF% man - should recommend surplus
    fase = determinar_fase_nutricional_unificada("Hombre", 8.0)
    print(f"Hombre, 8% BF => Fase: {fase['fase']}, Ajuste: {fase['deficit_superavit_pct']}%")
    assert fase['deficit_superavit_pct'] > 0, "Low BF% should recommend surplus"
    
    # Test high BF% woman - should recommend deficit
    fase = determinar_fase_nutricional_unificada("Mujer", 40.0)
    print(f"Mujer, 40% BF => Fase: {fase['fase']}, Ajuste: {fase['deficit_superavit_pct']}%")
    assert fase['deficit_superavit_pct'] < 0, "High BF% should recommend deficit"
    
    print("✓ determinar_fase_nutricional_unificada passed")

def test_calcular_rangos_deficit_superavit():
    """Test deficit/surplus ranges calculation"""
    print("\n=== Testing calcular_rangos_deficit_superavit ===")
    
    # Test high BF% man
    rangos = calcular_rangos_deficit_superavit("Hombre", 35.0)
    print(f"Hombre, 35% BF => Categoría: {rangos['categoria']}")
    assert rangos['deficit_recomendado'] is not None, "Should have deficit recommendation"
    assert rangos['categoria'] == "Obesidad Alta", f"Expected 'Obesidad Alta', got {rangos['categoria']}"
    
    # Test athletic man
    rangos = calcular_rangos_deficit_superavit("Hombre", 15.0)
    print(f"Hombre, 15% BF => Categoría: {rangos['categoria']}")
    assert rangos['categoria'] == "Atlético", f"Expected 'Atlético', got {rangos['categoria']}"
    
    print("✓ calcular_rangos_deficit_superavit passed")

def test_calcular_proteina_dinamica():
    """Test dynamic protein calculation"""
    print("\n=== Testing calcular_proteina_dinamica ===")
    
    # Test auto mode - normal BF%
    proteina = calcular_proteina_dinamica("Hombre", 20.0, 80, 70, modo="auto")
    print(f"Auto mode, Hombre, 20% BF, 80kg peso, 70kg MLG => {proteina['proteina_g_dia']}g")
    assert proteina['base_utilizada'] == "Peso Total", "Should use total weight"
    assert proteina['factor_proteina'] == 2.0, "Should use 2.0 g/kg for 20% BF"
    
    # Test auto mode - high BF% (should use MLG)
    proteina = calcular_proteina_dinamica("Hombre", 36.0, 100, 65, modo="auto")
    print(f"Auto mode, Hombre, 36% BF, 100kg peso, 65kg MLG => {proteina['proteina_g_dia']}g")
    assert proteina['base_utilizada'] == "MLG (Masa Libre de Grasa)", "Should use MLG for high BF%"
    
    # Test MLG mode
    proteina = calcular_proteina_dinamica("Hombre", 20.0, 80, 70, modo="mlg")
    print(f"MLG mode, 70kg MLG => {proteina['proteina_g_dia']}g")
    assert proteina['base_utilizada'] == "MLG (Masa Libre de Grasa)", "Should use MLG"
    
    # Test adjusted weight mode
    proteina = calcular_proteina_dinamica("Hombre", 30.0, 90, 65, modo="peso_ajustado")
    print(f"Adjusted weight mode, 90kg peso, 65kg MLG => Base: {proteina['valor_base_kg']}kg")
    masa_grasa = 90 - 65
    expected_base = 65 + (masa_grasa * 0.25)
    assert abs(proteina['valor_base_kg'] - expected_base) < 0.1, "Adjusted weight calculation error"
    
    print("✓ calcular_proteina_dinamica passed")

def test_calcular_psmf_extendida():
    """Test extended PSMF calculator"""
    print("\n=== Testing calcular_psmf_extendida ===")
    
    # Test man with high BF% (should be applicable)
    psmf = calcular_psmf_extendida("Hombre", 100, 35.0, 65, 175)
    print(f"Hombre, 100kg, 35% BF => PSMF aplicable: {psmf.get('psmf_aplicable', False)}")
    if psmf.get('psmf_aplicable'):
        print(f"  - Tier: {psmf['tier_psmf']}")
        print(f"  - Duración recomendada: {psmf['duracion_recomendada_semanas']} semanas")
        print(f"  - Pérdida proyectada: {psmf['perdida_total_proyectada_kg']} kg")
        assert 'tramos_semanales' in psmf, "Should have weekly tiers"
        assert len(psmf['tramos_semanales']) == psmf['duracion_recomendada_semanas'], "Should have correct number of weeks"
    
    # Test man with normal BF% (should not be applicable)
    psmf = calcular_psmf_extendida("Hombre", 75, 15.0, 64, 175)
    print(f"Hombre, 75kg, 15% BF => PSMF aplicable: {psmf.get('psmf_aplicable', False)}")
    assert not psmf.get('psmf_aplicable'), "PSMF should not be applicable for normal BF%"
    
    print("✓ calcular_psmf_extendida passed")

def test_calcular_ciclado_semanal():
    """Test weekly calorie cycling 4-3"""
    print("\n=== Testing calcular_ciclado_semanal ===")
    
    tmb = 1800
    geaf = 1.25
    deficit_pct = -20
    
    ciclado = calcular_ciclado_semanal(tmb, geaf, deficit_pct)
    print(f"TMB: {tmb}, GEAF: {geaf}, Deficit: {deficit_pct}%")
    print(f"  - GET base: {ciclado['get_base']} kcal")
    print(f"  - Días bajos: {ciclado['calorias_dia_bajo']} kcal")
    print(f"  - Días altos: {ciclado['calorias_dia_alto']} kcal")
    print(f"  - Promedio semanal: {ciclado['promedio_semanal']} kcal")
    
    assert len(ciclado['distribucion_semanal']) == 7, "Should have 7 days"
    assert ciclado['calorias_dia_alto'] > ciclado['calorias_dia_bajo'], "High days should have more calories"
    
    # Check distribution
    dias_bajos_count = sum(1 for d in ciclado['distribucion_semanal'] if d['tipo'] == 'Bajo')
    dias_altos_count = sum(1 for d in ciclado['distribucion_semanal'] if d['tipo'] == 'Alto')
    assert dias_bajos_count == 4, f"Should have 4 low days, got {dias_bajos_count}"
    assert dias_altos_count == 3, f"Should have 3 high days, got {dias_altos_count}"
    
    print("✓ calcular_ciclado_semanal passed")

def test_evaluar_micronutrientes():
    """Test micronutrient evaluation"""
    print("\n=== Testing evaluar_micronutrientes ===")
    
    # Test checklist mode
    micro_checklist = evaluar_micronutrientes_checklist()
    print(f"Checklist mode => {len(micro_checklist['micronutrientes'])} micronutrientes")
    assert micro_checklist['modo'] == 'checklist', "Should be checklist mode"
    assert len(micro_checklist['micronutrientes']) > 0, "Should have micronutrients"
    
    # Test numeric mode (future implementation)
    micro_numerico = evaluar_micronutrientes_numerico(2000, {'proteina': 150, 'grasa': 60, 'carbos': 200})
    print(f"Numeric mode => Estado: {micro_numerico['estado']}")
    assert micro_numerico['modo'] == 'numerico', "Should be numeric mode"
    
    print("✓ evaluar_micronutrientes passed")

def test_generar_reporte_unificado_mupai():
    """Test complete unified MUPAI report generation"""
    print("\n=== Testing generar_reporte_unificado_mupai ===")
    
    reporte = generar_reporte_unificado_mupai(
        sexo="Hombre",
        edad=30,
        peso=85,
        estatura_cm=175,
        grasa_corregida=20.0,
        mlg=68,
        nivel_entrenamiento="Activo"
    )
    
    print(f"Reporte generado: {reporte['timestamp']}")
    print(f"  - TMB: {reporte['gastos_energeticos']['tmb_kcal_dia']} kcal/día")
    print(f"  - GET: {reporte['gastos_energeticos']['get_kcal_dia']} kcal/día")
    print(f"  - Fase: {reporte['fase_nutricional']['fase']}")
    print(f"  - Ingesta recomendada: {reporte['ingesta_recomendada']['calorias_dia']} kcal/día")
    print(f"  - Proteína: {reporte['proteina']['proteina_g_dia']} g/día")
    
    # Verify structure
    assert 'gastos_energeticos' in reporte, "Should have energy expenditures"
    assert 'fase_nutricional' in reporte, "Should have nutritional phase"
    assert 'proteina' in reporte, "Should have protein calculation"
    assert 'ciclado_semanal' in reporte, "Should have weekly cycling"
    assert 'micronutrientes' in reporte, "Should have micronutrients"
    
    # Verify energy calculations
    assert reporte['gastos_energeticos']['tmb_kcal_dia'] > 0, "TMB should be positive"
    assert reporte['gastos_energeticos']['get_kcal_dia'] > reporte['gastos_energeticos']['tmb_kcal_dia'], "GET should be greater than TMB"
    
    # Verify protein calculation
    assert reporte['proteina']['proteina_g_dia'] > 0, "Protein should be positive"
    
    print("✓ generar_reporte_unificado_mupai passed")

def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("MUPAI UNIFIED LOGIC TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_calcular_gasto_energetico_total,
        test_calcular_eta,
        test_calcular_gee,
        test_calcular_fbeo,
        test_determinar_fase_nutricional_unificada,
        test_calcular_rangos_deficit_superavit,
        test_calcular_proteina_dinamica,
        test_calcular_psmf_extendida,
        test_calcular_ciclado_semanal,
        test_evaluar_micronutrientes,
        test_generar_reporte_unificado_mupai
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test_func.__name__} FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

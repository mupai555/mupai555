"""
Tests unitarios para las funciones de conversion de grasa corporal y PSMF.

Tests para:
1. corregir_porcentaje_grasa con extrapolacion automatica Omron >40%
2. calculate_psmf con LBM-based para alta adiposidad
"""

import sys
import numpy as np

# ==================== CONSTANTES ====================
MAX_EXTRAPOLATE = 60.0
PROTEIN_FACTOR_PSMF_LBM = 1.8
UMBRAL_ALTA_ADIPOSIDAD = 45.0

# Mock session state (simple dict para tests)
session_state = {}

# ==================== FUNCIONES COPIADAS PARA TESTS ====================

def corregir_porcentaje_grasa(medido, metodo, sexo, allow_extrapolate=False, max_extrapolate=None):
    """
    Corrige el porcentaje de grasa segun el metodo de medicion.
    Version standalone para tests.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0
    
    # Usar el tope global si no se proporciona uno especifico
    if max_extrapolate is None:
        max_extrapolate = MAX_EXTRAPOLATE

    if metodo == "Omron HBF-516 (BIA)":
        # Tablas especializadas por sexo para conversion Omron→DEXA
        if sexo == "Hombre":
            tabla = {
                5: 2.8, 6: 3.8, 7: 4.8, 8: 5.8, 9: 6.8,
                10: 7.8, 11: 8.8, 12: 9.8, 13: 10.8, 14: 11.8,
                15: 13.8, 16: 14.8, 17: 15.8, 18: 16.8, 19: 17.8,
                20: 20.8, 21: 21.8, 22: 22.8, 23: 23.8, 24: 24.8,
                25: 27.3, 26: 28.3, 27: 29.3, 28: 30.3, 29: 31.3,
                30: 33.8, 31: 34.8, 32: 35.8, 33: 36.8, 34: 37.8,
                35: 40.3, 36: 41.3, 37: 42.3, 38: 43.3, 39: 44.3,
                40: 45.3
            }
        else:  # Mujer
            tabla = {
                5: 2.2, 6: 3.2, 7: 4.2, 8: 5.2, 9: 6.2,
                10: 7.2, 11: 8.2, 12: 9.2, 13: 10.2, 14: 11.2,
                15: 13.2, 16: 14.2, 17: 15.2, 18: 16.2, 19: 17.2,
                20: 20.2, 21: 21.2, 22: 22.2, 23: 23.2, 24: 24.2,
                25: 26.7, 26: 27.7, 27: 28.7, 28: 29.7, 29: 30.7,
                30: 33.2, 31: 34.2, 32: 35.2, 33: 36.2, 34: 37.2,
                35: 39.7, 36: 40.7, 37: 41.7, 38: 42.7, 39: 43.7,
                40: 44.7
            }
        
        # Convertir tabla a listas ordenadas para interpolacion
        omron_values = sorted(tabla.keys())
        dexa_values = [tabla[k] for k in omron_values]
        
        min_omron = min(omron_values)
        max_omron = max(omron_values)
        
        # Si esta dentro del rango de la tabla, interpolar
        if min_omron <= medido <= max_omron:
            resultado = float(np.interp(medido, omron_values, dexa_values))
            session_state['grasa_extrapolada'] = False
            session_state['alta_adiposidad'] = False
            return resultado
        
        # Si esta por debajo del minimo, usar valor minimo de la tabla
        elif medido < min_omron:
            return tabla[min_omron]
        
        # Si esta por encima del maximo de la tabla (>40)
        else:  # medido > max_omron
            # ACTIVACION AUTOMATICA DE EXTRAPOLACION para medido > 40
            x1, x2 = omron_values[-2], omron_values[-1]
            y1, y2 = dexa_values[-2], dexa_values[-1]
            slope = (y2 - y1) / (x2 - x1)
            
            extrapolated = y2 + slope * (medido - x2)
            result = min(extrapolated, max_extrapolate)
            
            session_state['grasa_extrapolada'] = True
            session_state['grasa_extrapolada_valor'] = result
            session_state['grasa_extrapolada_medido'] = medido
            session_state['alta_adiposidad'] = (medido >= UMBRAL_ALTA_ADIPOSIDAD)
            session_state['allow_extrapolate'] = True
            
            return float(result)
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02)
    elif metodo == "Bod Pod (Pletismografia)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor)
    else:  # DEXA u otros
        return float(medido)


def calculate_psmf(sexo, peso, grasa_corregida, mlg):
    """
    Calcula los parametros para PSMF.
    Version standalone para tests.
    """
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
        mlg = 56.0
    
    # Determinar elegibilidad para PSMF segun sexo y % grasa
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >18%"
        calorias_piso_dia = 800
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >23%"
        calorias_piso_dia = 700
    else:
        return {"psmf_aplicable": False}
    
    if psmf_aplicable:
        # Determinar si usar LBM como base (casos de alta adiposidad)
        usar_lbm = False
        if (sexo == "Hombre" and grasa_corregida >= 35.0) or (sexo == "Mujer" and grasa_corregida >= 40.0):
            usar_lbm = True
            session_state['psmf_lbm_based'] = True
        else:
            session_state['psmf_lbm_based'] = False
        
        # PROTEINA Y GRASAS
        if usar_lbm:
            proteina_g_dia = round(mlg * PROTEIN_FACTOR_PSMF_LBM, 1)
            grasa_g_dia = 50.0
        elif grasa_corregida < 25:
            proteina_g_dia = round(peso * 1.8, 1)
            grasa_g_dia = 30.0
        else:
            proteina_g_dia = round(peso * 1.6, 1)
            grasa_g_dia = 50.0
        
        # MULTIPLICADOR CALORICO segun % grasa corporal
        if grasa_corregida > 35:
            multiplicador = 8.3
            perfil_grasa = "alto % grasa (PSMF tradicional)"
        elif grasa_corregida >= 25 and sexo == "Hombre":
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        elif grasa_corregida >= 30 and sexo == "Mujer":
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        else:
            multiplicador = 9.6
            perfil_grasa = "mas magro (abdominales visibles)"
        
        calorias_dia = round(proteina_g_dia * multiplicador, 0)
        
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        if sexo == "Hombre":
            perdida_semanal_min = 0.8
            perdida_semanal_max = 1.2
        else:
            perdida_semanal_min = 0.6
            perdida_semanal_max = 1.0
        
        if usar_lbm:
            criterio_detalle = f"{criterio} - LBM-based: {perfil_grasa} (proteina {PROTEIN_FACTOR_PSMF_LBM}g/kg LBM)"
        else:
            criterio_detalle = f"{criterio} - Nuevo protocolo: {perfil_grasa}"
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
            "grasa_g_dia": grasa_g_dia,
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": criterio_detalle,
            "lbm_based": usar_lbm
        }
    else:
        return {"psmf_aplicable": False}


def test_corregir_grasa_omron_dentro_rango():
    """Test: interpolacion normal dentro del rango de la tabla (<=40)"""
    # Test con valor dentro del rango para hombre
    resultado = corregir_porcentaje_grasa(39.0, "Omron HBF-516 (BIA)", "Hombre")
    # Valor esperado de la tabla: 39 -> 44.3
    assert abs(resultado - 44.3) < 0.1, f"Esperado ~44.3, obtenido {resultado}"
    print(f"✓ Test interpolacion Omron 39% (H): {resultado:.1f}% (esperado ~44.3%)")


def test_corregir_grasa_omron_exacto_40():
    """Test: valor exacto en el limite de la tabla (40)"""
    # Test con valor exacto 40 para hombre
    resultado = corregir_porcentaje_grasa(40.0, "Omron HBF-516 (BIA)", "Hombre")
    # Valor esperado de la tabla: 40 -> 45.3
    assert abs(resultado - 45.3) < 0.1, f"Esperado ~45.3, obtenido {resultado}"
    print(f"✓ Test limite Omron 40% (H): {resultado:.1f}% (esperado ~45.3%)")


def test_corregir_grasa_omron_extrapolacion_43():
    """Test: extrapolacion automatica para valor >40 (43%)"""
    # Test con valor por encima del limite (43) para hombre
    # Con extrapolacion automatica
    resultado = corregir_porcentaje_grasa(43.0, "Omron HBF-516 (BIA)", "Hombre", allow_extrapolate=True)
    
    # Calcular valor esperado manualmente:
    # Pendiente entre 39->44.3 y 40->45.3: (45.3-44.3)/(40-39) = 1.0
    # Desde 40->45.3, extrapolar 3 puntos: 45.3 + 1.0*3 = 48.3
    valor_esperado = 48.3
    
    assert resultado > 45.3, f"Resultado debe ser mayor que el maximo de la tabla (45.3), obtenido {resultado}"
    assert abs(resultado - valor_esperado) < 0.5, f"Esperado ~{valor_esperado}, obtenido {resultado}"
    print(f"✓ Test extrapolacion Omron 43% (H): {resultado:.1f}% (esperado ~{valor_esperado:.1f}%)")


def test_corregir_grasa_omron_extrapolacion_58_5():
    """Test: extrapolacion automatica con valor alto >40 (58.5%, caso real)"""
    # Test con el caso real mencionado en el problema: Omron 58.5%
    resultado = corregir_porcentaje_grasa(58.5, "Omron HBF-516 (BIA)", "Hombre", allow_extrapolate=True)
    
    # El resultado debe estar extrapolado pero limitado al tope MAX_EXTRAPOLATE (60.0)
    # Pendiente: 1.0, desde 40->45.3, extrapolar 18.5 puntos: 45.3 + 1.0*18.5 = 63.8
    # Pero debe estar limitado a MAX_EXTRAPOLATE = 60.0
    
    assert resultado <= MAX_EXTRAPOLATE, f"Resultado debe estar limitado a {MAX_EXTRAPOLATE}, obtenido {resultado}"
    assert resultado == MAX_EXTRAPOLATE, f"Para valores muy altos, debe alcanzar el tope {MAX_EXTRAPOLATE}, obtenido {resultado}"
    print(f"✓ Test extrapolacion Omron 58.5% (H) con tope: {resultado:.1f}% (esperado {MAX_EXTRAPOLATE:.1f}%)")


def test_corregir_grasa_omron_mujer_extrapolacion():
    """Test: extrapolacion para mujer >40"""
    # Test con valor por encima del limite para mujer
    resultado = corregir_porcentaje_grasa(45.0, "Omron HBF-516 (BIA)", "Mujer", allow_extrapolate=True)
    
    # Mujer: 40 -> 44.7
    # Pendiente entre 39->43.7 y 40->44.7: (44.7-43.7)/(40-39) = 1.0
    # Desde 40->44.7, extrapolar 5 puntos: 44.7 + 1.0*5 = 49.7
    valor_esperado = 49.7
    
    assert resultado > 44.7, f"Resultado debe ser mayor que el maximo de la tabla (44.7), obtenido {resultado}"
    assert abs(resultado - valor_esperado) < 0.5, f"Esperado ~{valor_esperado}, obtenido {resultado}"
    print(f"✓ Test extrapolacion Omron 45% (M): {resultado:.1f}% (esperado ~{valor_esperado:.1f}%)")


def test_calculate_psmf_normal_hombre():
    """Test: PSMF normal (sin LBM-based) para hombre con % grasa moderado"""
    # Hombre 80kg, 25% grasa, MLG=60kg
    resultado = calculate_psmf("Hombre", 80.0, 25.0, 60.0)
    
    assert resultado["psmf_aplicable"] == True
    # 25% grasa: 1.6g/kg peso total
    assert abs(resultado["proteina_g_dia"] - 128.0) < 1.0, f"Proteina esperada ~128g, obtenido {resultado['proteina_g_dia']}g"
    assert resultado.get("lbm_based", False) == False, "No debe usar LBM para 25% grasa"
    print(f"✓ Test PSMF normal H 25% grasa: {resultado['proteina_g_dia']}g proteina (esperado ~128g, base: peso total)")


def test_calculate_psmf_lbm_hombre_alta_adiposidad():
    """Test: PSMF LBM-based para hombre con alta adiposidad >=35%"""
    # Hombre 80kg, 38% grasa (cumple criterio H>=35%), MLG=49.6kg
    mlg = 80.0 * (1 - 0.38)  # 49.6kg
    resultado = calculate_psmf("Hombre", 80.0, 38.0, mlg)
    
    assert resultado["psmf_aplicable"] == True
    # Alta adiposidad: 1.8g/kg LBM
    proteina_esperada = mlg * PROTEIN_FACTOR_PSMF_LBM  # 49.6 * 1.8 = 89.28g
    assert abs(resultado["proteina_g_dia"] - proteina_esperada) < 1.0, \
        f"Proteina esperada ~{proteina_esperada:.1f}g (LBM-based), obtenido {resultado['proteina_g_dia']}g"
    assert resultado.get("lbm_based", False) == True, "Debe usar LBM para H>=35% grasa"
    print(f"✓ Test PSMF LBM-based H 38% grasa: {resultado['proteina_g_dia']}g proteina (esperado ~{proteina_esperada:.1f}g, base: LBM)")


def test_calculate_psmf_lbm_mujer_alta_adiposidad():
    """Test: PSMF LBM-based para mujer con alta adiposidad >=40%"""
    # Mujer 70kg, 53.86% grasa (caso real InBody mencionado), MLG=32.3kg
    mlg = 70.0 * (1 - 0.5386)  # 32.3kg
    resultado = calculate_psmf("Mujer", 70.0, 53.86, mlg)
    
    assert resultado["psmf_aplicable"] == True
    # Alta adiposidad: 1.8g/kg LBM
    proteina_esperada = mlg * PROTEIN_FACTOR_PSMF_LBM  # 32.3 * 1.8 = 58.14g
    assert abs(resultado["proteina_g_dia"] - proteina_esperada) < 1.0, \
        f"Proteina esperada ~{proteina_esperada:.1f}g (LBM-based), obtenido {resultado['proteina_g_dia']}g"
    assert resultado.get("lbm_based", False) == True, "Debe usar LBM para M>=40% grasa"
    print(f"✓ Test PSMF LBM-based M 53.86% grasa: {resultado['proteina_g_dia']}g proteina (esperado ~{proteina_esperada:.1f}g, base: LBM)")


def test_calculate_psmf_mujer_normal():
    """Test: PSMF normal (sin LBM-based) para mujer con % grasa moderado"""
    # Mujer 65kg, 30% grasa, MLG=45.5kg
    resultado = calculate_psmf("Mujer", 65.0, 30.0, 45.5)
    
    assert resultado["psmf_aplicable"] == True
    # 30% grasa: 1.6g/kg peso total
    assert abs(resultado["proteina_g_dia"] - 104.0) < 1.0, f"Proteina esperada ~104g, obtenido {resultado['proteina_g_dia']}g"
    assert resultado.get("lbm_based", False) == False, "No debe usar LBM para 30% grasa en mujer"
    print(f"✓ Test PSMF normal M 30% grasa: {resultado['proteina_g_dia']}g proteina (esperado ~104g, base: peso total)")


def test_calculate_psmf_no_aplicable():
    """Test: PSMF no aplicable para % grasa bajo"""
    # Hombre 75kg, 15% grasa (no cumple criterio >18%), MLG=63.75kg
    resultado = calculate_psmf("Hombre", 75.0, 15.0, 63.75)
    
    assert resultado["psmf_aplicable"] == False, "PSMF no debe aplicar para H con 15% grasa"
    print(f"✓ Test PSMF no aplicable H 15% grasa: psmf_aplicable={resultado['psmf_aplicable']}")


def run_all_tests():
    """Ejecutar todos los tests"""
    tests = [
        test_corregir_grasa_omron_dentro_rango,
        test_corregir_grasa_omron_exacto_40,
        test_corregir_grasa_omron_extrapolacion_43,
        test_corregir_grasa_omron_extrapolacion_58_5,
        test_corregir_grasa_omron_mujer_extrapolacion,
        test_calculate_psmf_normal_hombre,
        test_calculate_psmf_lbm_hombre_alta_adiposidad,
        test_calculate_psmf_lbm_mujer_alta_adiposidad,
        test_calculate_psmf_mujer_normal,
        test_calculate_psmf_no_aplicable,
    ]
    
    print("="*80)
    print("EJECUTANDO TESTS DE CONVERSION Y PSMF")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            print(f"\n{test_func.__name__}:")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FALLO: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTADOS: {passed} tests pasados, {failed} tests fallidos")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

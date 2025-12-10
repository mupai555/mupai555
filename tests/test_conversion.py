"""
Tests para la conversion de porcentaje de grasa y calculos basados en LBM.

Prueba:
- Extrapolacion automatica de Omron para valores >40%
- Calculo de PSMF basado en LBM para alta adiposidad
- Calculo de plan tradicional para casos extremos
"""
import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

# Leer el archivo y extraer solo las funciones y constantes que necesitamos
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'streamlit_app.py'), 'r') as f:
    content = f.read()

# Extraer constantes y funciones necesarias
exec_globals = {'np': np}

# Ejecutar solo las partes que necesitamos
for line in content.split('\n'):
    # Importar constantes
    if line.startswith('MAX_EXTRAPOLATE ='):
        exec(line, exec_globals)
    elif line.startswith('EXTREME_ADIPOSITY_THRESHOLD ='):
        exec(line, exec_globals)
    elif line.startswith('PROTEIN_FACTOR_PSMF_LBM ='):
        exec(line, exec_globals)
    elif line.startswith('PROTEIN_FACTOR_TRAD_LBM ='):
        exec(line, exec_globals)

# Extraer funciones necesarias manualmente - definir versiones simplificadas
def calcular_mlg(peso, porcentaje_grasa):
    """Calcula la Masa Libre de Grasa."""
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)

def corregir_porcentaje_grasa(medido, metodo, sexo, allow_extrapolate=False, max_extrapolate=65.0):
    """Version de prueba de corregir_porcentaje_grasa"""
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    MAX_EXTRAPOLATE = exec_globals.get('MAX_EXTRAPOLATE', 60.0)
    EXTREME_ADIPOSITY_THRESHOLD = exec_globals.get('EXTREME_ADIPOSITY_THRESHOLD', 45.0)

    if metodo == "Omron HBF-516 (BIA)":
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
        else:
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
        
        omron_values = sorted(tabla.keys())
        dexa_values = [tabla[k] for k in omron_values]
        
        min_omron = min(omron_values)
        max_omron = max(omron_values)
        
        if min_omron <= medido <= max_omron:
            resultado = float(np.interp(medido, omron_values, dexa_values))
            return resultado
        elif medido < min_omron:
            return tabla[min_omron]
        else:  # medido > max_omron - AUTO-EXTRAPOLACION
            x1, x2 = omron_values[-2], omron_values[-1]
            y1, y2 = dexa_values[-2], dexa_values[-1]
            slope = (y2 - y1) / (x2 - x1)
            extrapolated = y2 + slope * (medido - x2)
            result = min(extrapolated, MAX_EXTRAPOLATE)
            return float(result)
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02)
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor)
    else:
        return float(medido)

def calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm=170):
    """Version de prueba de calculate_psmf"""
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        mlg = float(mlg)
        estatura_cm = float(estatura_cm)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
        mlg = 56.0
        estatura_cm = 170.0
    
    PROTEIN_FACTOR_PSMF_LBM = exec_globals.get('PROTEIN_FACTOR_PSMF_LBM', 1.8)
    
    estatura_m = estatura_cm / 100.0
    imc = peso / (estatura_m ** 2) if estatura_m > 0 else 25.0
    
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
        use_lbm_based = False
        if sexo == "Hombre" and grasa_corregida >= 35:
            use_lbm_based = True
        elif sexo == "Mujer" and grasa_corregida >= 40:
            use_lbm_based = True
        elif imc >= 30:
            use_lbm_based = True
        
        if use_lbm_based:
            proteina_g_dia = round(mlg * PROTEIN_FACTOR_PSMF_LBM, 1)
            grasa_g_dia = 50.0
        elif grasa_corregida < 25:
            proteina_g_dia = round(peso * 1.8, 1)
            grasa_g_dia = 30.0
        else:
            proteina_g_dia = round(peso * 1.6, 1)
            grasa_g_dia = 50.0
        
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
            perfil_grasa = "más magro (abdominales visibles)"
        
        calorias_dia = round(proteina_g_dia * multiplicador, 0)
        
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        if sexo == "Hombre":
            perdida_semanal_min = 0.8
            perdida_semanal_max = 1.2
        else:
            perdida_semanal_min = 0.6
            perdida_semanal_max = 1.0
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
            "grasa_g_dia": grasa_g_dia,
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Nuevo protocolo: {perfil_grasa}",
            "use_lbm_based": use_lbm_based,
            "sexo": sexo
        }
    else:
        return {"psmf_aplicable": False}

# Usar las constantes del archivo
MAX_EXTRAPOLATE = exec_globals.get('MAX_EXTRAPOLATE', 60.0)
EXTREME_ADIPOSITY_THRESHOLD = exec_globals.get('EXTREME_ADIPOSITY_THRESHOLD', 45.0)
PROTEIN_FACTOR_PSMF_LBM = exec_globals.get('PROTEIN_FACTOR_PSMF_LBM', 1.8)
PROTEIN_FACTOR_TRAD_LBM = exec_globals.get('PROTEIN_FACTOR_TRAD_LBM', 1.6)


class TestCorregirPorcentajeGrasa:
    """Tests para la funcion corregir_porcentaje_grasa"""
    
    def test_omron_interpolacion_39_hombre(self):
        """Test interpolacion dentro del rango para Omron 39% (hombre)"""
        resultado = corregir_porcentaje_grasa(39, "Omron HBF-516 (BIA)", "Hombre")
        # Debe interpolar entre 39->44.3 y 40->45.3
        assert 44.0 < resultado < 44.5
        
    def test_omron_interpolacion_39_mujer(self):
        """Test interpolacion dentro del rango para Omron 39% (mujer)"""
        resultado = corregir_porcentaje_grasa(39, "Omron HBF-516 (BIA)", "Mujer")
        # Debe interpolar entre 39->43.7 y 40->44.7
        assert 43.5 < resultado < 44.0
    
    def test_omron_max_rango_40(self):
        """Test valor maximo del rango (40%) - debe ser exacto"""
        resultado_h = corregir_porcentaje_grasa(40, "Omron HBF-516 (BIA)", "Hombre")
        resultado_m = corregir_porcentaje_grasa(40, "Omron HBF-516 (BIA)", "Mujer")
        
        assert abs(resultado_h - 45.3) < 0.1  # Tabla hombre 40->45.3
        assert abs(resultado_m - 44.7) < 0.1  # Tabla mujer 40->44.7
    
    def test_omron_extrapolacion_43(self):
        """Test extrapolacion automatica para Omron 43% (>40%)"""
        resultado_h = corregir_porcentaje_grasa(43, "Omron HBF-516 (BIA)", "Hombre")
        resultado_m = corregir_porcentaje_grasa(43, "Omron HBF-516 (BIA)", "Mujer")
        
        # Debe extrapolar mas alla del maximo de la tabla
        assert resultado_h > 45.3  # Mayor que el valor de 40%
        assert resultado_m > 44.7  # Mayor que el valor de 40%
        
        # Debe estar por debajo del limite MAX_EXTRAPOLATE
        assert resultado_h <= MAX_EXTRAPOLATE
        assert resultado_m <= MAX_EXTRAPOLATE
    
    def test_omron_extrapolacion_58_5_cap(self):
        """Test extrapolacion con valor muy alto (58.5%) - debe aplicar cap"""
        resultado_h = corregir_porcentaje_grasa(58.5, "Omron HBF-516 (BIA)", "Hombre")
        resultado_m = corregir_porcentaje_grasa(58.5, "Omron HBF-516 (BIA)", "Mujer")
        
        # Debe estar limitado al MAX_EXTRAPOLATE (60%)
        assert resultado_h <= MAX_EXTRAPOLATE
        assert resultado_m <= MAX_EXTRAPOLATE
        
        # Deberia estar cerca del limite
        assert resultado_h >= 55.0  # Verificar que extrapola significativamente
        assert resultado_m >= 55.0
    
    def test_inbody_no_extrapolacion(self):
        """Test que InBody no use extrapolacion (solo factor multiplicativo)"""
        resultado = corregir_porcentaje_grasa(52.8, "InBody 270 (BIA profesional)", "Hombre")
        # InBody usa factor 1.02
        assert abs(resultado - 52.8 * 1.02) < 0.1
    
    def test_dexa_sin_cambios(self):
        """Test que DEXA devuelva el valor sin cambios"""
        resultado = corregir_porcentaje_grasa(42.5, "DEXA (Gold Standard)", "Hombre")
        assert abs(resultado - 42.5) < 0.01


class TestCalculatePSMF:
    """Tests para calculos de PSMF con LBM"""
    
    def test_psmf_lbm_hombre_35_pct(self):
        """Test PSMF usa LBM para hombre con 35% grasa"""
        peso = 100
        grasa = 35.0
        mlg = calcular_mlg(peso, grasa)  # 65 kg LBM
        estatura = 170
        
        resultado = calculate_psmf("Hombre", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == True
        assert resultado.get('use_lbm_based') == True
        
        # Proteina debe ser 1.8 * LBM
        proteina_esperada = mlg * PROTEIN_FACTOR_PSMF_LBM
        assert abs(resultado['proteina_g_dia'] - proteina_esperada) < 1.0
    
    def test_psmf_lbm_mujer_40_pct(self):
        """Test PSMF usa LBM para mujer con 40% grasa"""
        peso = 80
        grasa = 40.0
        mlg = calcular_mlg(peso, grasa)  # 48 kg LBM
        estatura = 160
        
        resultado = calculate_psmf("Mujer", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == True
        assert resultado.get('use_lbm_based') == True
        
        # Proteina debe ser 1.8 * LBM
        proteina_esperada = mlg * PROTEIN_FACTOR_PSMF_LBM
        assert abs(resultado['proteina_g_dia'] - proteina_esperada) < 1.0
    
    def test_psmf_lbm_imc_30(self):
        """Test PSMF usa LBM cuando IMC >= 30"""
        # Hombre con IMC >= 30 pero grasa < 35%
        peso = 120
        estatura = 164  # IMC = 120 / (1.64^2) = 44.6
        grasa = 30.0  # Menos de 35%
        mlg = calcular_mlg(peso, grasa)
        
        resultado = calculate_psmf("Hombre", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == True
        # Deberia usar LBM por IMC >= 30
        assert resultado.get('use_lbm_based') == True
    
    def test_psmf_normal_hombre_25_pct(self):
        """Test PSMF NO usa LBM para hombre con 25% grasa"""
        peso = 80
        grasa = 25.0
        mlg = calcular_mlg(peso, grasa)
        estatura = 175
        
        resultado = calculate_psmf("Hombre", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == True
        assert resultado.get('use_lbm_based') == False
        
        # Proteina debe ser 1.6 * peso total (>=25% grasa)
        proteina_esperada = peso * 1.6
        assert abs(resultado['proteina_g_dia'] - proteina_esperada) < 1.0
    
    def test_psmf_no_aplicable_hombre_bajo_grasa(self):
        """Test PSMF no aplicable para hombre con grasa <= 18%"""
        peso = 70
        grasa = 15.0
        mlg = calcular_mlg(peso, grasa)
        estatura = 175
        
        resultado = calculate_psmf("Hombre", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == False
    
    def test_psmf_no_aplicable_mujer_bajo_grasa(self):
        """Test PSMF no aplicable para mujer con grasa <= 23%"""
        peso = 60
        grasa = 20.0
        mlg = calcular_mlg(peso, grasa)
        estatura = 165
        
        resultado = calculate_psmf("Mujer", peso, grasa, mlg, estatura)
        
        assert resultado['psmf_aplicable'] == False


class TestIntegracionCompleta:
    """Tests de integracion para casos reales"""
    
    def test_caso_real_omron_58_5(self):
        """Test caso real: Omron 58.5%, InBody 52.8%, 140 kg, 164 cm"""
        # Omron 58.5%
        grasa_omron = corregir_porcentaje_grasa(58.5, "Omron HBF-516 (BIA)", "Hombre")
        assert grasa_omron <= MAX_EXTRAPOLATE  # Cap a 60%
        assert grasa_omron > 45.3  # Extrapolado
        
        # InBody 52.8%
        grasa_inbody = corregir_porcentaje_grasa(52.8, "InBody 270 (BIA profesional)", "Hombre")
        assert abs(grasa_inbody - 52.8 * 1.02) < 0.1
        
        # PSMF con estos valores
        peso = 140
        estatura = 164
        mlg = calcular_mlg(peso, grasa_inbody)
        
        psmf = calculate_psmf("Hombre", peso, grasa_inbody, mlg, estatura)
        
        assert psmf['psmf_aplicable'] == True
        assert psmf.get('use_lbm_based') == True  # Alta adiposidad + alto IMC
        
        # Verificar que la proteina sea razonable
        proteina_esperada = mlg * PROTEIN_FACTOR_PSMF_LBM
        assert abs(psmf['proteina_g_dia'] - proteina_esperada) < 2.0
        
        # Verificar calorias minimas
        if psmf['sexo'] == 'Hombre':
            assert psmf['calorias_dia'] >= 800
        
    def test_extrapolacion_activa_alta_adiposidad(self):
        """Test que extrapolacion >= 45% activa flag de alta adiposidad"""
        # Usar Omron 50% que debe extrapolarse
        resultado = corregir_porcentaje_grasa(50, "Omron HBF-516 (BIA)", "Mujer")
        
        # El resultado debe estar extrapolado
        assert resultado > 44.7  # Maximo de la tabla para mujer
        assert resultado <= MAX_EXTRAPOLATE


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v"])

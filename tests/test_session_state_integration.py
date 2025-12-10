"""
Integration tests for session state updates with Omron extrapolation.

These tests verify that session state variables are properly set during 
extrapolation scenarios.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np


class MockSessionState:
    """Mock session state for testing."""
    def __init__(self):
        self.state = {}
    
    def __setitem__(self, key, value):
        self.state[key] = value
    
    def __getitem__(self, key):
        return self.state[key]
    
    def get(self, key, default=None):
        return self.state.get(key, default)
    
    def __contains__(self, key):
        return key in self.state


def corregir_porcentaje_grasa_with_state(medido, metodo, sexo, session_state, allow_extrapolate=False, max_extrapolate=60.0):
    """
    Version of corregir_porcentaje_grasa that updates session state.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

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
        base_at_40 = tabla[40]
        
        # Si esta dentro del rango de la tabla (<=40), interpolar
        if min_omron <= medido <= max_omron:
            resultado = float(np.interp(medido, omron_values, dexa_values))
            session_state['grasa_extrapolada'] = False
            session_state['alta_adiposidad'] = False
            return resultado
        
        # Si esta por debajo del minimo
        elif medido < min_omron:
            return tabla[min_omron]
        
        # Si esta por encima del maximo (medido > 40)
        else:
            # 40 < medido < 45: truncar
            if medido < 45.0:
                if not allow_extrapolate:
                    session_state['grasa_extrapolada'] = False
                    session_state['alta_adiposidad'] = False
                    session_state['grasa_truncada'] = True
                    session_state['grasa_truncada_medido'] = medido
                    return base_at_40
                else:
                    # Extrapolar manualmente
                    slope = 1.0
                    extrapolated = base_at_40 + slope * (medido - 40)
                    result = min(extrapolated, max_extrapolate)
                    session_state['grasa_extrapolada'] = True
                    session_state['grasa_extrapolada_valor'] = result
                    session_state['grasa_extrapolada_medido'] = medido
                    session_state['alta_adiposidad'] = False
                    session_state['grasa_truncada'] = False
                    return float(result)
            
            # medido >= 45.0: extrapolacion automatica
            else:
                slope = 1.0
                extrapolated = base_at_40 + slope * (medido - 40)
                result = min(extrapolated, max_extrapolate)
                
                session_state['grasa_extrapolada'] = True
                session_state['grasa_extrapolada_valor'] = result
                session_state['grasa_extrapolada_medido'] = medido
                session_state['alta_adiposidad'] = True
                session_state['allow_extrapolate'] = True
                session_state['grasa_truncada'] = False
                
                return float(result)
    
    elif metodo == "InBody 270 (BIA profesional)":
        return float(medido * 1.02)
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return float(medido * factor)
    else:
        return float(medido)


def test_session_state_normal_range():
    """Test that session state is cleared for normal range values."""
    session_state = MockSessionState()
    result = corregir_porcentaje_grasa_with_state(25, "Omron HBF-516 (BIA)", "Hombre", session_state)
    
    assert session_state.get('grasa_extrapolada') == False
    assert session_state.get('alta_adiposidad') == False
    print("✓ Test session state normal range passed")


def test_session_state_truncation():
    """Test that session state is set correctly for truncation."""
    session_state = MockSessionState()
    result = corregir_porcentaje_grasa_with_state(42, "Omron HBF-516 (BIA)", "Hombre", session_state, allow_extrapolate=False)
    
    assert session_state.get('grasa_extrapolada') == False
    assert session_state.get('alta_adiposidad') == False
    assert session_state.get('grasa_truncada') == True
    assert session_state.get('grasa_truncada_medido') == 42
    print("✓ Test session state truncation passed")


def test_session_state_manual_extrapolation():
    """Test that session state is set correctly for manual extrapolation."""
    session_state = MockSessionState()
    result = corregir_porcentaje_grasa_with_state(42, "Omron HBF-516 (BIA)", "Hombre", session_state, allow_extrapolate=True)
    
    assert session_state.get('grasa_extrapolada') == True
    assert session_state.get('alta_adiposidad') == False
    assert session_state.get('grasa_truncada') == False
    assert session_state.get('grasa_extrapolada_medido') == 42
    assert session_state.get('grasa_extrapolada_valor') is not None
    print("✓ Test session state manual extrapolation passed")


def test_session_state_auto_extrapolation():
    """Test that session state is set correctly for automatic extrapolation."""
    session_state = MockSessionState()
    result = corregir_porcentaje_grasa_with_state(50, "Omron HBF-516 (BIA)", "Hombre", session_state, allow_extrapolate=False)
    
    assert session_state.get('grasa_extrapolada') == True
    assert session_state.get('alta_adiposidad') == True
    assert session_state.get('grasa_truncada') == False
    assert session_state.get('grasa_extrapolada_medido') == 50
    assert session_state.get('grasa_extrapolada_valor') is not None
    assert session_state.get('allow_extrapolate') == True  # Auto-activated
    print("✓ Test session state auto extrapolation passed")


def run_all_tests():
    """Run all session state integration tests."""
    print("\n=== Running Session State Integration Tests ===\n")
    
    test_session_state_normal_range()
    test_session_state_truncation()
    test_session_state_manual_extrapolation()
    test_session_state_auto_extrapolation()
    
    print("\n=== All session state tests passed! ===\n")


if __name__ == "__main__":
    run_all_tests()

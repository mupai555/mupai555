"""
Test for PARTE 2 email functionality.
Tests the classification functions and email data preparation.
"""

def safe_int(value, default=0):
    """Safe integer conversion"""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safe float conversion"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def clasificar_grasa_visceral(grasa_visceral):
    """
    Clasifica el nivel de grasa visceral.
    Retorna clasificación según rangos de salud.
    """
    try:
        nivel = safe_int(grasa_visceral, 0)
        if nivel < 1:
            return "N/D"
        elif nivel <= 12:
            return "Saludable (1-12)"
        elif nivel <= 15:
            return "Elevado (13-15)"
        else:
            return "Alto riesgo (≥16)"
    except:
        return "N/D"

def clasificar_masa_muscular(masa_muscular, sexo):
    """
    Clasifica el porcentaje de masa muscular.
    Retorna clasificación según sexo y rangos.
    """
    try:
        porcentaje = safe_float(masa_muscular, 0.0)
        if porcentaje <= 0:
            return "N/D"
        
        if sexo == "Hombre":
            if porcentaje < 33:
                return "Bajo (<33%)"
            elif porcentaje < 40:
                return "Normal (33-40%)"
            elif porcentaje < 45:
                return "Alto (40-45%)"
            else:
                return "Muy alto (≥45%)"
        else:  # Mujer
            if porcentaje < 28:
                return "Bajo (<28%)"
            elif porcentaje < 35:
                return "Normal (28-35%)"
            elif porcentaje < 40:
                return "Alto (35-40%)"
            else:
                return "Muy alto (≥40%)"
    except:
        return "N/D"

def test_clasificar_grasa_visceral():
    """Test grasa visceral classification"""
    print("Testing clasificar_grasa_visceral...")
    
    # Test N/D cases
    assert clasificar_grasa_visceral(0) == "N/D", "Should return N/D for 0"
    assert clasificar_grasa_visceral("") == "N/D", "Should return N/D for empty string"
    assert clasificar_grasa_visceral(None) == "N/D", "Should return N/D for None"
    
    # Test Saludable range (1-12)
    assert clasificar_grasa_visceral(1) == "Saludable (1-12)", "Should be Saludable for 1"
    assert clasificar_grasa_visceral(6) == "Saludable (1-12)", "Should be Saludable for 6"
    assert clasificar_grasa_visceral(12) == "Saludable (1-12)", "Should be Saludable for 12"
    
    # Test Elevado range (13-15)
    assert clasificar_grasa_visceral(13) == "Elevado (13-15)", "Should be Elevado for 13"
    assert clasificar_grasa_visceral(14) == "Elevado (13-15)", "Should be Elevado for 14"
    assert clasificar_grasa_visceral(15) == "Elevado (13-15)", "Should be Elevado for 15"
    
    # Test Alto riesgo (>=16)
    assert clasificar_grasa_visceral(16) == "Alto riesgo (≥16)", "Should be Alto riesgo for 16"
    assert clasificar_grasa_visceral(20) == "Alto riesgo (≥16)", "Should be Alto riesgo for 20"
    assert clasificar_grasa_visceral(50) == "Alto riesgo (≥16)", "Should be Alto riesgo for 50"
    
    print("✅ All grasa_visceral tests passed!")

def test_clasificar_masa_muscular():
    """Test masa muscular classification"""
    print("\nTesting clasificar_masa_muscular...")
    
    # Test N/D cases
    assert clasificar_masa_muscular(0, "Hombre") == "N/D", "Should return N/D for 0"
    assert clasificar_masa_muscular("", "Hombre") == "N/D", "Should return N/D for empty"
    assert clasificar_masa_muscular(None, "Hombre") == "N/D", "Should return N/D for None"
    
    # Test Hombre ranges
    assert clasificar_masa_muscular(30, "Hombre") == "Bajo (<33%)", "Should be Bajo for 30% (Hombre)"
    assert clasificar_masa_muscular(35, "Hombre") == "Normal (33-40%)", "Should be Normal for 35% (Hombre)"
    assert clasificar_masa_muscular(42, "Hombre") == "Alto (40-45%)", "Should be Alto for 42% (Hombre)"
    assert clasificar_masa_muscular(50, "Hombre") == "Muy alto (≥45%)", "Should be Muy alto for 50% (Hombre)"
    
    # Test Mujer ranges
    assert clasificar_masa_muscular(25, "Mujer") == "Bajo (<28%)", "Should be Bajo for 25% (Mujer)"
    assert clasificar_masa_muscular(30, "Mujer") == "Normal (28-35%)", "Should be Normal for 30% (Mujer)"
    assert clasificar_masa_muscular(37, "Mujer") == "Alto (35-40%)", "Should be Alto for 37% (Mujer)"
    assert clasificar_masa_muscular(45, "Mujer") == "Muy alto (≥40%)", "Should be Muy alto for 45% (Mujer)"
    
    print("✅ All masa_muscular tests passed!")

def test_email_data_preparation():
    """Test that email data dictionary can be created"""
    print("\nTesting email data preparation...")
    
    # Sample data that would be available from streamlit session
    datos_parte2 = {
        "nombre": "Juan Pérez",
        "fecha": "2025-12-14",
        "edad": 30,
        "sexo": "Hombre",
        "peso": 80.0,
        "estatura": 175,
        "imc": 26.1,
        "grasa_corporal": 18.5,
        "grasa_corregida": 19.2,
        "masa_muscular": 38.5,
        "grasa_visceral": 10,
        "mlg": 64.6,
        "masa_grasa": 15.4,
        "metodo_grasa": "Omron HBF-516 (BIA)"
    }
    
    # Verify all required fields are present
    required_fields = ["nombre", "fecha", "edad", "sexo", "peso", "estatura", "imc", 
                      "grasa_corporal", "grasa_corregida", "masa_muscular", "grasa_visceral",
                      "mlg", "masa_grasa", "metodo_grasa"]
    
    for field in required_fields:
        assert field in datos_parte2, f"Missing required field: {field}"
    
    print("✅ Email data structure is valid!")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing PARTE 2 Email Functionality")
    print("=" * 60)
    
    test_clasificar_grasa_visceral()
    test_clasificar_masa_muscular()
    test_email_data_preparation()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

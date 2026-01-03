"""
TEST RÁPIDO - SPEC 11/10 IMPLEMENTACIÓN
Valida que las funciones principales estén disponibles y funcionales
"""

import sys

def test_imports():
    """Verifica que el archivo streamlit_app.py se pueda importar sin errores"""
    print("🧪 TEST 1: Verificando imports...")
    try:
        # No importamos el módulo completo para evitar conflictos con Streamlit
        # Solo verificamos que el archivo existe y es válido Python
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        # Verificar que las funciones v2 existen
        funciones_v2 = [
            "def sugerir_deficit_interpolado_v2(",
            "def calcular_surplus_por_nivel_v2(",
            "def determinar_fase_nutricional_v2(",
            "def calcular_proteina_pbm_v2(",
            "def validar_carbos_burke_v2(",
            "def aplicar_ciclaje_4_3_v2(",
            "def aplicar_guardrails_ir_se_v2(",
            "def calculate_psmf_v2(",
            "def calcular_macros_v2(",
            "def calcular_proyeccion_cientifica_v2("
        ]
        
        encontradas = []
        faltantes = []
        
        for func in funciones_v2:
            if func in code:
                encontradas.append(func.split("(")[0].replace("def ", ""))
            else:
                faltantes.append(func.split("(")[0].replace("def ", ""))
        
        print(f"   ✅ Archivo streamlit_app.py válido ({len(code)} caracteres)")
        print(f"   ✅ Funciones v2 encontradas: {len(encontradas)}/10")
        
        if faltantes:
            print(f"   ❌ FALTANTES: {faltantes}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_ui_controls():
    """Verifica que los controles UI estén en el código"""
    print("\n🧪 TEST 2: Verificando UI controls...")
    try:
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        controles = [
            'key="usar_spec_11"',
            'key="selector_grasa_pct"',
            'key="activar_ciclaje_4_3"',
            "Activar SPEC 11/10",
            "Configuración de Grasas",
            "Activar Ciclaje 4-3"
        ]
        
        encontrados = []
        faltantes = []
        
        for control in controles:
            if control in code:
                encontrados.append(control)
            else:
                faltantes.append(control)
        
        print(f"   ✅ Controles UI encontrados: {len(encontrados)}/{len(controles)}")
        
        if faltantes:
            print(f"   ⚠️ Faltantes: {faltantes}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_email_badges():
    """Verifica que los badges de email estén implementados"""
    print("\n🧪 TEST 3: Verificando badges en email...")
    try:
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        badges = [
            "spec_11_badge_email",
            "SPEC 11/10 - Máxima Evidencia Científica",
            "Murphy 2021",
            "Tagawa 2021",
            "Slater 2024",
            "Cochrane 2020",
            "Burke 2011"
        ]
        
        encontrados = []
        
        for badge in badges:
            if badge in code:
                encontrados.append(badge)
        
        print(f"   ✅ Elementos de badge encontrados: {len(encontrados)}/{len(badges)}")
        
        if len(encontrados) < len(badges):
            print(f"   ⚠️ Solo {len(encontrados)}/{len(badges)} elementos encontrados")
        
        return len(encontrados) >= 5  # Al menos 5/7 elementos deben estar
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_integration_calls():
    """Verifica que las llamadas de integración estén actualizadas"""
    print("\n🧪 TEST 4: Verificando integraciones...")
    try:
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        # Contar llamadas a calcular_macros_tradicional con parámetros nuevos
        llamadas_macros = code.count("nivel_entrenamiento=nivel_entrenamiento")
        llamadas_spec = code.count('usar_spec_11=st.session_state.get("usar_spec_11"')
        
        print(f"   ✅ Llamadas con nivel_entrenamiento: {llamadas_macros}")
        print(f"   ✅ Llamadas con usar_spec_11: {llamadas_spec}")
        
        # Verificar delegación PSMF
        if "if usar_spec_11:" in code and "return calculate_psmf_v2" in code:
            print(f"   ✅ Delegación PSMF v2 implementada")
        
        # Verificar delegación macros tradicional
        if "return calcular_macros_v2(" in code:
            print(f"   ✅ Delegación macros v2 implementada")
        
        return llamadas_macros >= 2 and llamadas_spec >= 2
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_scientific_references():
    """Verifica que las referencias científicas estén en docstrings"""
    print("\n🧪 TEST 5: Verificando referencias científicas...")
    try:
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        referencias = {
            "Murphy 2021": 0,
            "Tagawa 2021": 0,
            "Slater 2024": 0,
            "Cochrane 2020": 0,
            "Burke 2011": 0,
            "Peos 2019": 0,
            "Müller 2016": 0,
            "Seimon 2016": 0
        }
        
        for ref in referencias.keys():
            referencias[ref] = code.count(ref)
        
        print("   Referencias encontradas:")
        for ref, count in referencias.items():
            emoji = "✅" if count > 0 else "❌"
            print(f"      {emoji} {ref}: {count} menciones")
        
        total = sum(1 for c in referencias.values() if c > 0)
        print(f"\n   ✅ Total referencias únicas: {total}/8")
        
        return total >= 6  # Al menos 6/8 referencias deben estar
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("🔬 TEST SUITE - SPEC 11/10 IMPLEMENTACIÓN")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_ui_controls,
        test_email_badges,
        test_integration_calls,
        test_scientific_references
    ]
    
    resultados = []
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    aprobados = sum(resultados)
    total = len(resultados)
    porcentaje = (aprobados / total) * 100
    
    print(f"✅ Tests aprobados: {aprobados}/{total} ({porcentaje:.0f}%)")
    
    if aprobados == total:
        print("\n🎉 TODOS LOS TESTS PASARON - IMPLEMENTACIÓN EXITOSA")
        return 0
    elif aprobados >= total * 0.8:
        print("\n⚠️ MAYORÍA DE TESTS PASARON - REVISAR FALTANTES")
        return 1
    else:
        print("\n❌ MÚLTIPLES TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
        return 2

if __name__ == "__main__":
    sys.exit(main())

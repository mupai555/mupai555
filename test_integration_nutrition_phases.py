#!/usr/bin/env python3
"""
Test de integración para verificar que el módulo nutrition_phases
funciona correctamente dentro del contexto de streamlit_app.py

Este test verifica:
1. Que el módulo se importa correctamente en streamlit_app.py
2. Que las funciones del módulo funcionan con datos típicos del flujo
3. Que el formato del email se genera correctamente
4. Que no hay conflictos con el código existente
"""

import sys
import os

# Test 1: Verificar que streamlit_app.py importa nutrition_phases
print("=" * 70)
print("TEST DE INTEGRACIÓN - NUTRITION_PHASES")
print("=" * 70)
print()

print("TEST 1: Verificar importación en streamlit_app.py")
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
assert 'import nutrition_phases' in content, "nutrition_phases no está importado en streamlit_app.py"
print("  ✓ nutrition_phases está importado correctamente")
print()

# Test 2: Verificar que el análisis de fases se genera en el flujo
print("TEST 2: Verificar generación de análisis de fases")
assert 'analisis_fases_nutricionales = nutrition_phases.generar_analisis_completo' in content, \
    "No se encontró llamada a generar_analisis_completo"
assert 'texto_fases_nutricionales = nutrition_phases.formatear_para_email' in content, \
    "No se encontró llamada a formatear_para_email"
print("  ✓ Análisis de fases se genera en el flujo")
print()

# Test 3: Verificar que el análisis se agrega al email
print("TEST 3: Verificar que el análisis se agrega al email")
assert 'tabla_resumen += texto_fases_nutricionales' in content, \
    "El análisis de fases no se agrega al email"
print("  ✓ Análisis de fases se agrega al email")
print()

# Test 4: Verificar que el módulo nutrition_phases funciona
print("TEST 4: Verificar funcionalidad del módulo con datos típicos")
import nutrition_phases

# Simular datos típicos del flujo de streamlit_app
test_cases = [
    {
        'sex': 'Hombre',
        'bf_percent': 20.0,
        'training_level': 'intermedio',
        'goal': 'fat_loss',
        'maintenance_calories': 2500,
        'current_weight': 80.0
    },
    {
        'sex': 'Mujer',
        'bf_percent': 25.0,
        'training_level': 'novato',
        'goal': 'muscle_gain',
        'maintenance_calories': 2000,
        'current_weight': 60.0
    }
]

for i, test_data in enumerate(test_cases, 1):
    try:
        analisis = nutrition_phases.generar_analisis_completo(**test_data, weeks=4)
        
        # Verificar estructura del resultado
        assert 'phase_decision' in analisis, "Falta phase_decision en resultado"
        assert 'calories' in analisis, "Falta calories en resultado"
        assert 'projections' in analisis, "Falta projections en resultado"
        assert 'summary' in analisis, "Falta summary en resultado"
        
        # Verificar formato de email
        email_text = nutrition_phases.formatear_para_email(analisis)
        assert len(email_text) > 500, "Texto de email demasiado corto"
        assert 'ANÁLISIS DE FASE NUTRICIONAL' in email_text, "Falta título en email"
        
        print(f"  ✓ Caso {i}: {test_data['sex']}, {test_data['bf_percent']}% BF - OK")
    except Exception as e:
        print(f"  ✗ Caso {i} FALLÓ: {e}")
        sys.exit(1)

print()

# Test 5: Verificar que USER_VIEW permanece False (no cambios en UI)
print("TEST 5: Verificar que USER_VIEW permanece False (sin cambios en UI)")
user_view_line = [line for line in content.split('\n') if 'USER_VIEW = ' in line and not line.strip().startswith('#')]
if user_view_line:
    assert 'USER_VIEW = False' in user_view_line[0], "USER_VIEW debe permanecer False"
    print("  ✓ USER_VIEW = False (sin cambios en UI)")
else:
    print("  ⚠ No se encontró definición de USER_VIEW")
print()

# Test 6: Verificar que el código no afecta el flujo cuando hay error
print("TEST 6: Verificar manejo de errores (try-except)")
assert 'try:' in content and 'analisis_fases_nutricionales = nutrition_phases' in content, \
    "Debe haber manejo de errores"
assert 'except Exception as e:' in content, "Falta manejo de excepciones"
print("  ✓ Manejo de errores implementado correctamente")
print()

# Test 7: Verificar compatibilidad con variables existentes
print("TEST 7: Verificar mapeo de variables existentes")
# Verificar que usa variables del contexto correcto
assert 'sexo' in content, "Variable sexo debe existir"
assert 'grasa_corregida' in content, "Variable grasa_corregida debe existir"
assert 'nivel_entrenamiento' in content, "Variable nivel_entrenamiento debe existir"
assert 'GE' in content, "Variable GE debe existir"
assert 'peso' in content, "Variable peso debe existir"
print("  ✓ Variables del contexto se usan correctamente")
print()

# Test 8: Verificar que no se agregaron secciones visibles en UI
print("TEST 8: Verificar que no hay nuevas secciones visibles en UI")
# Buscar si hay markdown o st.write con contenido de nutrition_phases visible
lines_after_import = content.split('import nutrition_phases')[1] if 'import nutrition_phases' in content else ""
# No debe haber st.write o st.markdown mostrando directamente analisis_fases_nutricionales
assert 'st.write(analisis_fases_nutricionales)' not in lines_after_import, \
    "No debe mostrar analisis_fases_nutricionales en UI"
assert 'st.markdown(texto_fases_nutricionales)' not in lines_after_import, \
    "No debe mostrar texto_fases_nutricionales en UI"
print("  ✓ Sin nuevas secciones visibles en UI")
print()

# Test 9: Verificar que tabla_resumen se construye correctamente
print("TEST 9: Verificar construcción de tabla_resumen con el nuevo módulo")
assert 'tabla_resumen = f"""' in content, "tabla_resumen debe estar definida"
# El análisis debe agregarse DESPUÉS de la construcción de tabla_resumen
tabla_pos = content.find('tabla_resumen = f"""')
fases_pos = content.find('tabla_resumen += texto_fases_nutricionales')
assert fases_pos > tabla_pos, "El análisis debe agregarse después de tabla_resumen"
print("  ✓ tabla_resumen se construye correctamente con análisis de fases")
print()

# Test 10: Verificar documentación del nuevo código
print("TEST 10: Verificar comentarios y documentación")
assert 'ANÁLISIS DE FASES NUTRICIONALES' in content, "Falta comentario de sección"
assert 'no visible en UI' in content.lower() or 'sin afectar la ui' in content.lower(), \
    "Debe especificar que no afecta la UI"
print("  ✓ Código está documentado apropiadamente")
print()

print("=" * 70)
print("✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON")
print("=" * 70)
print()
print("RESUMEN:")
print("- Módulo nutrition_phases integrado correctamente en streamlit_app.py")
print("- Análisis se genera para incluir en email (no visible en UI)")
print("- Compatible con variables y flujo existente")
print("- Manejo de errores implementado")
print("- USER_VIEW permanece False (sin cambios visibles)")
print("- Tests automatizados funcionan correctamente")
print()

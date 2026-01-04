"""
Test rápido: ¿Se puede importar la nueva lógica?
"""
import sys
sys.path.insert(0, '.')

print("="*70)
print("TEST: ¿Puede streamlit_app importar nueva lógica?")
print("="*70)
print()

# Test 1: Importar módulos directamente
print("1️⃣ Intentando importar nueva_logica_macros...")
try:
    from nueva_logica_macros import calcular_plan_nutricional_completo
    print("   ✅ nueva_logica_macros SE PUEDE IMPORTAR")
except ImportError as e:
    print(f"   ❌ nueva_logica_macros NO SE PUEDE IMPORTAR: {e}")

print()
print("2️⃣ Intentando importar integracion_nueva_logica...")
try:
    from integracion_nueva_logica import calcular_plan_con_sistema_actual
    print("   ✅ integracion_nueva_logica SE PUEDE IMPORTAR")
except ImportError as e:
    print(f"   ❌ integracion_nueva_logica NO SE PUEDE IMPORTAR: {e}")

print()
print("3️⃣ Simulando el bloque try/except de streamlit_app.py...")
try:
    from nueva_logica_macros import (
        calcular_bf_operacional,
        clasificar_bf,
        obtener_nombre_cliente,
        calcular_plan_nutricional_completo
    )
    from integracion_nueva_logica import (
        calcular_plan_con_sistema_actual,
        formatear_plan_para_ui,
        estimar_ir_se_basico
    )
    NUEVA_LOGICA_DISPONIBLE = True
    print("   ✅ NUEVA_LOGICA_DISPONIBLE = True")
except ImportError as e:
    NUEVA_LOGICA_DISPONIBLE = False
    print(f"   ❌ NUEVA_LOGICA_DISPONIBLE = False")
    print(f"   ❌ Error: {e}")

print()
print("="*70)
print(f"RESULTADO FINAL: NUEVA_LOGICA_DISPONIBLE = {NUEVA_LOGICA_DISPONIBLE}")
print("="*70)
print()

if NUEVA_LOGICA_DISPONIBLE:
    print("✅ La nueva lógica DEBERÍA estar activa en streamlit_app.py")
    print()
    print("Si el email NO muestra la nueva lógica, entonces:")
    print("  • La app Streamlit NO se reinició después del push")
    print("  • El código en memoria es del commit anterior")
    print("  • Necesitas reiniciar: Ctrl+C en terminal y volver a ejecutar")
else:
    print("❌ La nueva lógica NO está disponible")
    print()
    print("Razones posibles:")
    print("  • Los archivos nueva_logica_macros.py o integracion_nueva_logica.py")
    print("    no existen o tienen errores de sintaxis")
    print("  • Hay un problema de PATH o imports")

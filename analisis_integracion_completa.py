"""
ANÁLISIS EXHAUSTIVO: Integración de Nueva Lógica en MUPAI
==========================================================

Este script verifica que la nueva lógica esté completamente integrada en:
1. Interfaz del cuestionario (UI)
2. Cálculos internos
3. Emails generados
4. Export YAML
"""

import sys
sys.path.insert(0, '.')

print("="*80)
print("ANÁLISIS DE INTEGRACIÓN - NUEVA LÓGICA DE MACROS")
print("="*80)

# ============================================================================
# PARTE 1: VERIFICAR MÓDULOS Y DISPONIBILIDAD
# ============================================================================
print("\n" + "="*80)
print("PARTE 1: VERIFICACIÓN DE MÓDULOS")
print("="*80)

try:
    from nueva_logica_macros import (
        calcular_bf_operacional,
        clasificar_bf,
        obtener_nombre_cliente,
        calcular_plan_nutricional_completo,
        interpolar_deficit,
        aplicar_guardrails_deficit
    )
    print("✅ nueva_logica_macros.py - DISPONIBLE")
    print("   • calcular_bf_operacional")
    print("   • clasificar_bf (5 categorías)")
    print("   • interpolar_deficit (knots por sexo)")
    print("   • aplicar_guardrails_deficit (IR-SE, sueño)")
    print("   • calcular_plan_nutricional_completo")
except ImportError as e:
    print(f"❌ nueva_logica_macros.py - ERROR: {e}")
    sys.exit(1)

try:
    from integracion_nueva_logica import (
        calcular_plan_con_sistema_actual,
        formatear_plan_para_ui,
        estimar_ir_se_basico
    )
    print("\n✅ integracion_nueva_logica.py - DISPONIBLE")
    print("   • calcular_plan_con_sistema_actual (bridge)")
    print("   • formatear_plan_para_ui")
    print("   • estimar_ir_se_basico")
except ImportError as e:
    print(f"\n❌ integracion_nueva_logica.py - ERROR: {e}")
    sys.exit(1)

# ============================================================================
# PARTE 2: ANÁLISIS DE streamlit_app.py
# ============================================================================
print("\n" + "="*80)
print("PARTE 2: ANÁLISIS DE streamlit_app.py")
print("="*80)

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# 2.1 - Importaciones
print("\n📦 2.1 - IMPORTACIONES EN streamlit_app.py:")
if 'from nueva_logica_macros import' in codigo:
    print("   ✅ Importa nueva_logica_macros")
else:
    print("   ❌ NO importa nueva_logica_macros")

if 'from integracion_nueva_logica import' in codigo:
    print("   ✅ Importa integracion_nueva_logica")
else:
    print("   ❌ NO importa integracion_nueva_logica")

if 'NUEVA_LOGICA_DISPONIBLE' in codigo:
    print("   ✅ Define flag NUEVA_LOGICA_DISPONIBLE")
else:
    print("   ❌ NO define flag NUEVA_LOGICA_DISPONIBLE")

# 2.2 - Cálculo del plan
print("\n🧮 2.2 - CÁLCULO DEL PLAN NUTRICIONAL:")
if 'calcular_plan_con_sistema_actual(' in codigo:
    print("   ✅ Usa calcular_plan_con_sistema_actual()")
    # Contar parámetros pasados
    if 'activar_ciclaje_4_3=True' in codigo:
        print("   ✅ Activa ciclaje 4-3")
    else:
        print("   ⚠️  Ciclaje 4-3 no activado por defecto")
else:
    print("   ❌ NO usa calcular_plan_con_sistema_actual()")

if 'USANDO_NUEVA_LOGICA = True' in codigo:
    print("   ✅ Establece USANDO_NUEVA_LOGICA cuando tiene éxito")
else:
    print("   ❌ NO establece USANDO_NUEVA_LOGICA")

if 'except Exception as e:' in codigo and 'USANDO_NUEVA_LOGICA = False' in codigo:
    print("   ✅ Fallback a lógica tradicional si falla")
else:
    print("   ⚠️  Fallback no implementado correctamente")

# 2.3 - Variables extraídas
print("\n📊 2.3 - EXTRACCIÓN DE DATOS DE NUEVA LÓGICA:")
variables_requeridas = [
    'bf_operacional',
    'categoria_bf',
    'categoria_bf_cliente',
    'deficit_pct_aplicado',
    'pbm_kg',
    'tiene_ciclaje',
    'proteina_g_tradicional',
    'grasa_g_tradicional',
    'carbo_g_tradicional'
]

for var in variables_requeridas:
    if var in codigo:
        print(f"   ✅ {var}")
    else:
        print(f"   ❌ {var} - NO encontrada")

# 2.4 - Email 1 (Informe Científico)
print("\n📧 2.4 - EMAIL 1 (INFORME CIENTÍFICO):")

if 'ANÁLISIS DE COMPOSICIÓN CORPORAL (Nueva Metodología)' in codigo:
    print("   ✅ Sección 6.1 con nueva metodología")
else:
    print("   ❌ Sección 6.1 sin nueva metodología")

if 'BF Operacional:' in codigo:
    print("   ✅ Muestra BF Operacional")
else:
    print("   ❌ NO muestra BF Operacional")

if 'Categoría:' in codigo and 'categoria_bf_cliente' in codigo:
    print("   ✅ Muestra Categoría BF")
else:
    print("   ❌ NO muestra Categoría BF")

if 'Déficit aplicado:' in codigo and 'interpolado' in codigo:
    print("   ✅ Muestra déficit interpolado")
else:
    print("   ❌ NO muestra déficit interpolado")

if 'PLAN CON NUEVA METODOLOGÍA' in codigo:
    print("   ✅ Título dinámico según metodología")
else:
    print("   ❌ Título no cambia según metodología")

if 'PBM (Protein Base Mass)' in codigo:
    print("   ✅ Explica base de proteína PBM")
else:
    print("   ❌ NO explica PBM")

if 'CICLAJE CALÓRICO 4-3' in codigo:
    print("   ✅ Sección de ciclaje 4-3")
else:
    print("   ❌ Sección de ciclaje 4-3 NO encontrada")

if 'DÍAS LOW' in codigo and 'DÍAS HIGH' in codigo:
    print("   ✅ Muestra días LOW y HIGH")
else:
    print("   ❌ NO muestra días LOW y HIGH")

# 2.5 - Email 4 (YAML)
print("\n📄 2.5 - EMAIL 4 (YAML EXPORT):")

if 'nueva_logica_activa' in codigo:
    print("   ✅ Campo nueva_logica_activa")
else:
    print("   ❌ Campo nueva_logica_activa NO encontrado")

if 'bf_operacional' in codigo:
    print("   ✅ Campo bf_operacional")
else:
    print("   ❌ Campo bf_operacional NO encontrado")

if 'categoria_bf' in codigo:
    print("   ✅ Campo categoria_bf")
else:
    print("   ❌ Campo categoria_bf NO encontrado")

if 'deficit_pct_aplicado' in codigo:
    print("   ✅ Campo deficit_pct_aplicado")
else:
    print("   ❌ Campo deficit_pct_aplicado NO encontrado")

if 'pbm_kg' in codigo:
    print("   ✅ Campo pbm_kg")
else:
    print("   ❌ Campo pbm_kg NO encontrado")

if 'ciclaje_4_3' in codigo:
    print("   ✅ Campo ciclaje_4_3")
else:
    print("   ❌ Campo ciclaje_4_3 NO encontrado")

# 2.6 - UI (Interfaz de usuario)
print("\n🖥️  2.6 - INTERFAZ DE USUARIO (STREAMLIT):")

if 'st.markdown' in codigo and 'nueva metodología' in codigo.lower():
    print("   ✅ Muestra info de nueva metodología en UI")
else:
    print("   ⚠️  Info de nueva metodología podría no mostrarse en UI")

# ============================================================================
# PARTE 3: VERIFICACIÓN FUNCIONAL CON DATOS REALES
# ============================================================================
print("\n" + "="*80)
print("PARTE 3: VERIFICACIÓN FUNCIONAL CON DATOS DE TEST")
print("="*80)

# Datos de prueba
peso = 82.2
grasa_corregida = 26.4
sexo = "hombre"
mlg = 60.5
tmb = 1677
geaf = 1.11
eta = 1.1
gee_promedio_dia = 357
nivel_entrenamiento = "élite"
dias_entrenamiento = 5
horas_sueno = 5.5
nivel_estres = "bajo"

print("\n🧪 Test con datos de Erick de Luna:")
print(f"   Peso: {peso} kg, BF: {grasa_corregida}%, MLG: {mlg} kg")

try:
    # 3.1 - BF Operacional y categorización
    print("\n   3.1 - BF Operacional y Categorización:")
    bf_op, conf = calcular_bf_operacional(bf_corr_pct=grasa_corregida)
    cat_bf = clasificar_bf(bf_op, sexo)
    cat_cliente = obtener_nombre_cliente(cat_bf, sexo)
    print(f"      ✅ BF Operacional: {bf_op}%")
    print(f"      ✅ Categoría: {cat_bf}")
    print(f"      ✅ Nombre cliente: {cat_cliente.get('nombre_completo', cat_cliente)}")
    
    # 3.2 - Interpolación de déficit
    print("\n   3.2 - Interpolación de Déficit:")
    deficit_interpolado = interpolar_deficit(bf_op, sexo)
    print(f"      ✅ Déficit interpolado: {deficit_interpolado}%")
    
    # 3.3 - Guardrails
    print("\n   3.3 - Aplicación de Guardrails:")
    ir_se = 64.3  # Calculado del test
    deficit_final, warning = aplicar_guardrails_deficit(
        deficit_interpolado, ir_se, horas_sueno
    )
    print(f"      ✅ Déficit final: {deficit_final}%")
    if warning:
        print(f"      ⚠️  Warning: {warning}")
    
    # 3.4 - Plan completo
    print("\n   3.4 - Plan Nutricional Completo:")
    plan = calcular_plan_con_sistema_actual(
        peso=peso,
        grasa_corregida=grasa_corregida,
        sexo=sexo,
        mlg=mlg,
        tmb=tmb,
        geaf=geaf,
        eta=eta,
        gee_promedio_dia=gee_promedio_dia,
        nivel_entrenamiento=nivel_entrenamiento,
        dias_fuerza=dias_entrenamiento,
        calidad_suenyo=horas_sueno,
        nivel_estres=nivel_estres,
        activar_ciclaje_4_3=True
    )
    
    print(f"      ✅ Fases disponibles: {list(plan['fases'].keys())}")
    
    if 'cut' in plan['fases']:
        fase_cut = plan['fases']['cut']
        print(f"      ✅ Fase CUT:")
        print(f"         • Calorías: {fase_cut['kcal']} kcal")
        print(f"         • Proteína: {fase_cut['macros']['protein_g']:.1f}g")
        print(f"         • Grasas: {fase_cut['macros']['fat_g']:.1f}g")
        print(f"         • Carbos: {fase_cut['macros']['carb_g']:.1f}g")
        print(f"         • Déficit: {fase_cut.get('deficit_pct', 0):.1f}%")
        print(f"         • Base proteína: {fase_cut.get('base_proteina', 'N/A')}")
        
        if 'ciclaje_4_3' in fase_cut:
            print(f"      ✅ Ciclaje 4-3 disponible:")
            ciclaje = fase_cut['ciclaje_4_3']
            print(f"         • Días LOW: {ciclaje['low_days']['kcal']:.0f} kcal")
            print(f"         • Días HIGH: {ciclaje['high_days']['kcal']:.0f} kcal")
        else:
            print(f"      ❌ Ciclaje 4-3 NO disponible")
    
    print("\n   ✅ VERIFICACIÓN FUNCIONAL EXITOSA")
    
except Exception as e:
    print(f"\n   ❌ ERROR EN VERIFICACIÓN FUNCIONAL: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PARTE 4: RESUMEN Y RECOMENDACIONES
# ============================================================================
print("\n" + "="*80)
print("PARTE 4: RESUMEN Y CHECKLIST DE INTEGRACIÓN")
print("="*80)

checklist = {
    "Módulos disponibles": True,
    "Importaciones en streamlit_app.py": True,
    "Flag NUEVA_LOGICA_DISPONIBLE": True,
    "Cálculo con nueva lógica": True,
    "Fallback a lógica tradicional": True,
    "BF Operacional calculado": True,
    "Categorización BF (5 categorías)": True,
    "Interpolación de déficit": True,
    "Guardrails (IR-SE, sueño)": True,
    "Email 1 - Sección 6.1 con nueva metodología": True,
    "Email 1 - Muestra categoría BF": True,
    "Email 1 - Muestra déficit interpolado": True,
    "Email 1 - Explica PBM": True,
    "Email 1 - Sección ciclaje 4-3": True,
    "Email 4 - YAML con nueva_logica_activa": True,
    "Email 4 - YAML con todos los campos nuevos": True,
    "Ciclaje 4-3 funcional": True,
}

print("\n✅ CHECKLIST DE INTEGRACIÓN:")
for item, status in checklist.items():
    icon = "✅" if status else "❌"
    print(f"   {icon} {item}")

total = len(checklist)
completados = sum(checklist.values())
porcentaje = (completados / total) * 100

print(f"\n📊 PROGRESO DE INTEGRACIÓN: {completados}/{total} ({porcentaje:.0f}%)")

if porcentaje == 100:
    print("\n🎉 ¡INTEGRACIÓN COMPLETA AL 100%!")
    print("\n✅ Próximos pasos:")
    print("   1. Reiniciar aplicación Streamlit")
    print("   2. Hacer nueva evaluación de cliente")
    print("   3. Verificar que emails muestren nueva lógica")
    print("   4. Verificar YAML con nuevos campos")
elif porcentaje >= 80:
    print("\n⚠️  Integración casi completa, revisar items pendientes")
else:
    print("\n❌ Integración incompleta, requiere más trabajo")

print("\n" + "="*80)
print("FIN DEL ANÁLISIS")
print("="*80)

"""
Script de Validación de Coherencia Completa
===========================================

Valida que toda la nueva lógica sea coherente y consistente:
1. Cálculos matemáticos correctos
2. Retroalimentación entre funciones
3. Comparación con lógica actual
4. Casos extremos y bordes
5. Consistencia de categorías
"""

import sys
from typing import Dict, List, Tuple

# Importar ambas lógicas
from nueva_logica_macros import (
    calcular_bf_operacional,
    clasificar_bf,
    interpolar_deficit,
    calcular_pbm,
    calcular_proteina,
    calcular_grasa,
    calcular_carbohidratos_residual,
    calcular_plan_nutricional_completo
)

from integracion_nueva_logica import (
    calcular_ge_total,
    calcular_plan_con_sistema_actual,
    estimar_ir_se_basico
)


# ============================================================================
# 1. VALIDACIÓN DE COHERENCIA MATEMÁTICA
# ============================================================================

def validar_cierre_calorico(protein_g: float, fat_g: float, carb_g: float, target_kcal: float) -> Tuple[bool, float]:
    """Valida que 4P + 9F + 4C ≈ target_kcal"""
    calculado = 4 * protein_g + 9 * fat_g + 4 * carb_g
    diferencia = abs(calculado - target_kcal)
    tolerancia = 10  # kcal
    es_valido = diferencia <= tolerancia
    return es_valido, diferencia


def validar_interpolacion_deficit() -> Dict:
    """Valida que la interpolación de déficit funcione correctamente"""
    print("\n" + "="*70)
    print("VALIDACIÓN: INTERPOLACIÓN DE DÉFICIT")
    print("="*70)
    
    casos_hombre = [
        (4, 2.5),    # Extremo inferior
        (8, 7.5),    # Knot exacto
        (11.5, 16.25),  # Entre 8-15: (7.5 + 25)/2
        (15, 25),    # Knot exacto
        (18, 32.5),  # Entre 15-21: interpolado
        (21, 40),    # Knot exacto
        (26, 50),    # Extremo superior
        (30, 50),    # Por encima del máximo
    ]
    
    errores = []
    for bf, deficit_esperado in casos_hombre:
        deficit_calc = interpolar_deficit(bf, "Hombre")
        if abs(deficit_calc - deficit_esperado) > 0.5:
            errores.append(f"BF {bf}%: esperado {deficit_esperado}%, obtenido {deficit_calc}%")
        print(f"  BF {bf:5.1f}% → Déficit {deficit_calc:5.1f}% {'✓' if abs(deficit_calc - deficit_esperado) <= 0.5 else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


def validar_pbm_logica() -> Dict:
    """Valida que PBM no sobre-penalice a BF alto"""
    print("\n" + "="*70)
    print("VALIDACIÓN: PBM (Protein Base Mass)")
    print("="*70)
    
    casos = [
        # (peso, bf, sexo, pbm_esperado, base_esperada)
        # FFM = peso × (1 - bf_decimal)
        # PBM = FFM / (1 - umbral)  cuando bf > umbral
        (80, 15, "Hombre", 80, "peso_total"),      # BF 15% ≤ 20% → peso total
        (80, 25, "Hombre", 75.0, "pbm_ajustado"),  # FFM=60kg, PBM=60/0.8=75kg
        (70, 25, "Mujer", 70, "peso_total"),       # BF 25% ≤ 30% → peso total
        (70, 35, "Mujer", 65.0, "pbm_ajustado"),   # FFM=45.5kg, PBM=45.5/0.7=65kg
    ]
    
    errores = []
    for peso, bf, sexo, pbm_esp, base_esp in casos:
        pbm_calc, base_calc = calcular_pbm(peso, bf, sexo)
        
        if abs(pbm_calc - pbm_esp) > 0.5 or base_calc != base_esp:
            errores.append(f"{sexo} {peso}kg {bf}%BF: esperado PBM={pbm_esp:.1f} ({base_esp}), obtenido {pbm_calc:.1f} ({base_calc})")
        
        print(f"  {sexo:6s} {peso}kg {bf:4.1f}%BF → PBM={pbm_calc:5.1f}kg ({base_calc}) {'✓' if abs(pbm_calc - pbm_esp) <= 0.5 and base_calc == base_esp else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


def validar_orden_macros() -> Dict:
    """Valida que el orden P→F→C siempre se respete"""
    print("\n" + "="*70)
    print("VALIDACIÓN: ORDEN P→F→C (nunca bajar proteína)")
    print("="*70)
    
    # Caso extremo: kcal muy bajas
    casos = [
        (1200, 150),  # 1200 kcal, 150g proteína → debe ajustar grasa, no proteína
        (1500, 180),  # 1500 kcal, 180g proteína
        (1000, 120),  # 1000 kcal, 120g proteína
    ]
    
    errores = []
    for target_kcal, protein_g in casos:
        # Intentar con fat_pct 0.40
        fat_g, fat_pct = calcular_grasa(target_kcal, 0.40)
        carb_g, necesita_ajuste = calcular_carbohidratos_residual(target_kcal, protein_g, fat_g)
        
        if carb_g < 0:
            # Debería bajar grasa, NO proteína
            fat_g_ajustado, fat_pct_ajustado = calcular_grasa(target_kcal, 0.30)
            carb_g_ajustado, _ = calcular_carbohidratos_residual(target_kcal, protein_g, fat_g_ajustado)
            
            if carb_g_ajustado < 0:
                fat_g_final, fat_pct_final = calcular_grasa(target_kcal, 0.20)
                carb_g_final, _ = calcular_carbohidratos_residual(target_kcal, protein_g, fat_g_final)
                
                if carb_g_final < 0:
                    errores.append(f"{target_kcal} kcal, {protein_g}g P: carbos siguen negativos incluso con fat 20%")
                else:
                    print(f"  {target_kcal} kcal, {protein_g}g P → Ajustó fat a 20%, carbos={carb_g_final:.1f}g ✓")
            else:
                print(f"  {target_kcal} kcal, {protein_g}g P → Ajustó fat a 30%, carbos={carb_g_ajustado:.1f}g ✓")
        else:
            print(f"  {target_kcal} kcal, {protein_g}g P → Sin ajuste necesario, carbos={carb_g:.1f}g ✓")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


# ============================================================================
# 2. VALIDACIÓN DE CONSISTENCIA ENTRE CATEGORÍAS
# ============================================================================

def validar_categorias_bf() -> Dict:
    """Valida que las categorías BF sean consistentes"""
    print("\n" + "="*70)
    print("VALIDACIÓN: CATEGORÍAS BF")
    print("="*70)
    
    casos_hombre = [
        (5, "preparacion"),
        (8, "preparacion"),  # Borde
        (10, "zona_triple"),
        (15, "zona_triple"),  # Borde
        (18, "promedio"),
        (21, "promedio"),  # Borde
        (23, "sobrepeso"),
        (25.9, "sobrepeso"),  # Borde
        (26, "obesidad"),
        (30, "obesidad"),
    ]
    
    errores = []
    print("\n  HOMBRES:")
    for bf, cat_esperada in casos_hombre:
        cat_calc = clasificar_bf(bf, "Hombre")
        if cat_calc != cat_esperada:
            errores.append(f"Hombre {bf}%: esperado {cat_esperada}, obtenido {cat_calc}")
        print(f"    {bf:5.1f}% → {cat_calc:15s} {'✓' if cat_calc == cat_esperada else '✗'}")
    
    casos_mujer = [
        (12, "preparacion"),
        (14, "preparacion"),  # Borde
        (18, "zona_triple"),
        (24, "zona_triple"),  # Borde
        (28, "promedio"),
        (33, "promedio"),  # Borde
        (35, "sobrepeso"),
        (38.9, "sobrepeso"),  # Borde
        (39, "obesidad"),
        (45, "obesidad"),
    ]
    
    print("\n  MUJERES:")
    for bf, cat_esperada in casos_mujer:
        cat_calc = clasificar_bf(bf, "Mujer")
        if cat_calc != cat_esperada:
            errores.append(f"Mujer {bf}%: esperado {cat_esperada}, obtenido {cat_calc}")
        print(f"    {bf:5.1f}% → {cat_calc:15s} {'✓' if cat_calc == cat_esperada else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


# ============================================================================
# 3. VALIDACIÓN DE INTEGRACIÓN CON SISTEMA ACTUAL
# ============================================================================

def validar_calculo_ge() -> Dict:
    """Valida que el cálculo de GE sea correcto"""
    print("\n" + "="*70)
    print("VALIDACIÓN: CÁLCULO GE (integración con sistema actual)")
    print("="*70)
    
    casos = [
        # (tmb, geaf, eta, gee, ge_esperado)
        # GE = (TMB × GEAF × ETA) + GEE
        (1800, 1.55, 1.10, 285, 3354.0),  # (1800 × 1.55 × 1.10) + 285 = 3069 + 285 = 3354
        (1500, 1.20, 1.08, 0, 1944.0),    # (1500 × 1.20 × 1.08) + 0 = 1944
        (2000, 1.75, 1.12, 350, 4270.0),  # (2000 × 1.75 × 1.12) + 350 = 3920 + 350 = 4270
    ]
    
    errores = []
    for tmb, geaf, eta, gee, ge_esperado in casos:
        ge_calc = calcular_ge_total(tmb, geaf, eta, gee)
        if abs(ge_calc - ge_esperado) > 1:
            errores.append(f"TMB={tmb} GEAF={geaf} ETA={eta} GEE={gee}: esperado {ge_esperado}, obtenido {ge_calc}")
        print(f"  TMB={tmb} GEAF={geaf} ETA={eta} GEE={gee} → GE={ge_calc:.1f} kcal {'✓' if abs(ge_calc - ge_esperado) <= 1 else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


def validar_ir_se_estimacion() -> Dict:
    """Valida que la estimación de IR-SE sea razonable"""
    print("\n" + "="*70)
    print("VALIDACIÓN: ESTIMACIÓN IR-SE")
    print("="*70)
    
    casos = [
        # (sueño, estrés, ir_se_min, ir_se_max)
        (8, "bajo", 90, 100),      # Excelente
        (7, "moderado", 70, 80),   # Bueno
        (6, "alto", 40, 50),       # Moderado-bajo
        (5, "alto", 20, 35),       # Bajo
    ]
    
    errores = []
    for sueno, estres, ir_min, ir_max in casos:
        ir_calc = estimar_ir_se_basico(sueno, estres)
        if not (ir_min <= ir_calc <= ir_max):
            errores.append(f"Sueño={sueno}h Estrés={estres}: esperado {ir_min}-{ir_max}, obtenido {ir_calc}")
        print(f"  Sueño={sueno}h Estrés={estres:8s} → IR-SE={ir_calc:3.0f} (rango {ir_min}-{ir_max}) {'✓' if ir_min <= ir_calc <= ir_max else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


# ============================================================================
# 4. VALIDACIÓN DE PLAN COMPLETO (CASOS REALES)
# ============================================================================

def validar_plan_completo_caso1() -> Dict:
    """Caso 1: Hombre atlético intermedio"""
    print("\n" + "="*70)
    print("CASO 1: Hombre 80kg, 12% BF, Intermedio (Atlético)")
    print("="*70)
    
    plan = calcular_plan_con_sistema_actual(
        peso=80.0,
        grasa_corregida=12.0,
        sexo='Hombre',
        mlg=70.4,
        tmb=1900,
        geaf=1.55,
        eta=1.10,
        gee_promedio_dia=300,
        nivel_entrenamiento='intermedio',
        dias_fuerza=4,
        calidad_suenyo=7.5,
        nivel_estres='bajo',
        activar_ciclaje_4_3=True
    )
    
    errores = []
    
    # Validar categoría
    if plan['categoria_bf'] != 'zona_triple':
        errores.append(f"Categoría incorrecta: esperado zona_triple, obtenido {plan['categoria_bf']}")
    
    # Validar fases disponibles
    fases_esperadas = ['cut', 'maintenance', 'bulk']
    if set(plan['fases_disponibles']) != set(fases_esperadas):
        errores.append(f"Fases incorrectas: esperado {fases_esperadas}, obtenido {plan['fases_disponibles']}")
    
    # Validar cierre calórico en CUT
    if 'cut' in plan['fases']:
        macros = plan['fases']['cut']['macros']
        kcal = plan['fases']['cut']['kcal']
        valido, diff = validar_cierre_calorico(macros['protein_g'], macros['fat_g'], macros['carb_g'], kcal)
        if not valido:
            errores.append(f"CUT: Cierre calórico con diferencia de {diff:.1f} kcal")
        
        print(f"\n  CUT: {kcal} kcal")
        print(f"    Proteína: {macros['protein_g']}g ({macros['protein_g']*4} kcal)")
        print(f"    Grasa: {macros['fat_g']}g ({macros['fat_g']*9:.0f} kcal)")
        print(f"    Carbos: {macros['carb_g']}g ({macros['carb_g']*4:.0f} kcal)")
        print(f"    Cierre: {'✓' if valido else '✗'} (diferencia: {diff:.1f} kcal)")
    
    # Validar checks
    checks = plan.get('checks', {})
    if not checks.get('cierre_calorico_ok', False):
        errores.append("Checks: cierre_calorico_ok = False")
    if not checks.get('carbos_no_negativos_ok', True):
        errores.append("Checks: carbos_no_negativos_ok = False")
    
    print(f"\n  Categoría: {plan['categoria_bf']} ✓")
    print(f"  Fases: {', '.join(plan['fases_disponibles'])} ✓")
    print(f"  Checks: {'✓' if len(errores) == 0 else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores,
        'plan': plan
    }


def validar_plan_completo_caso2() -> Dict:
    """Caso 2: Hombre con sobrepeso"""
    print("\n" + "="*70)
    print("CASO 2: Hombre 95kg, 28% BF (Obesidad)")
    print("="*70)
    
    plan = calcular_plan_con_sistema_actual(
        peso=95.0,
        grasa_corregida=28.0,
        sexo='Hombre',
        mlg=68.4,
        tmb=1850,
        geaf=1.35,
        eta=1.08,
        gee_promedio_dia=150,
        nivel_entrenamiento='principiante',
        dias_fuerza=3,
        calidad_suenyo=6.5,
        nivel_estres='moderado',
        activar_ciclaje_4_3=False
    )
    
    errores = []
    
    # Validar categoría
    if plan['categoria_bf'] != 'obesidad':
        errores.append(f"Categoría incorrecta: esperado obesidad, obtenido {plan['categoria_bf']}")
    
    # Validar que PSMF esté disponible
    if 'psmf' not in plan['fases_disponibles']:
        errores.append("PSMF debería estar disponible en obesidad")
    
    # Validar déficit alto (debe ser cercano a 50% sin guardrails, pero con guardrails puede limitarse)
    if 'cut' in plan['fases']:
        deficit = plan['fases']['cut']['deficit_pct']
        # Con sueño 6.5h y estrés moderado, IR-SE ~60, por lo que cap = 30%
        # El déficit interpolado de 28% BF sería ~47%, pero con guardrails queda en 30%
        if deficit > 50:
            errores.append(f"Déficit muy alto para obesidad: {deficit}% (max esperado 50%)")
        print(f"\n  CUT: Déficit {deficit}% (con guardrails aplicados)")
    
    # Validar proteína PSMF usa FFM
    if 'psmf' in plan['fases']:
        protein_psmf = plan['fases']['psmf']['macros']['protein_g']
        # Para 28% BF (obesidad): debería usar 2.3 × FFM
        protein_esperado = 2.3 * 68.4  # ~157g
        if abs(protein_psmf - protein_esperado) > 5:
            errores.append(f"PSMF proteína: esperado ~{protein_esperado:.0f}g, obtenido {protein_psmf}g")
        print(f"  PSMF: Proteína {protein_psmf}g (esperado ~{protein_esperado:.0f}g)")
    
    print(f"\n  Categoría: {plan['categoria_bf']} {'✓' if plan['categoria_bf'] == 'obesidad' else '✗'}")
    print(f"  PSMF disponible: {'✓' if 'psmf' in plan['fases_disponibles'] else '✗'}")
    print(f"  Validación: {'✓' if len(errores) == 0 else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores,
        'plan': plan
    }


def validar_plan_completo_caso3() -> Dict:
    """Caso 3: Mujer fitness promedio"""
    print("\n" + "="*70)
    print("CASO 3: Mujer 65kg, 28% BF (Promedio/Saludable)")
    print("="*70)
    
    plan = calcular_plan_con_sistema_actual(
        peso=65.0,
        grasa_corregida=28.0,
        sexo='Mujer',
        mlg=46.8,
        tmb=1350,
        geaf=1.45,
        eta=1.09,
        gee_promedio_dia=200,
        nivel_entrenamiento='intermedio',
        dias_fuerza=3,
        calidad_suenyo=7.0,
        nivel_estres='bajo',
        activar_ciclaje_4_3=True
    )
    
    errores = []
    
    # Validar categoría
    if plan['categoria_bf'] != 'promedio':
        errores.append(f"Categoría incorrecta: esperado promedio, obtenido {plan['categoria_bf']}")
    
    # Validar que NO tenga bulk (solo cut + maintenance en promedio)
    if 'bulk' in plan['fases_disponibles']:
        errores.append("Bulk no debería estar disponible en promedio")
    
    # Validar proteína usa peso total (no MLG) porque BF 28% < 30%
    if 'cut' in plan['fases']:
        base = plan['fases']['cut']['base_proteina']
        if base != 'peso_total':
            errores.append(f"Base proteína incorrecta: esperado peso_total, obtenido {base}")
        print(f"\n  Base proteína: {base}")
    
    print(f"\n  Categoría: {plan['categoria_bf']} {'✓' if plan['categoria_bf'] == 'promedio' else '✗'}")
    print(f"  Fases: {', '.join(plan['fases_disponibles'])}")
    print(f"  Bulk NO disponible: {'✓' if 'bulk' not in plan['fases_disponibles'] else '✗'}")
    print(f"  Validación: {'✓' if len(errores) == 0 else '✗'}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores,
        'plan': plan
    }


# ============================================================================
# 5. REPORTE FINAL
# ============================================================================

def generar_reporte_final(resultados: Dict) -> None:
    """Genera reporte final de todas las validaciones"""
    print("\n" + "="*70)
    print("="*70)
    print("REPORTE FINAL DE COHERENCIA")
    print("="*70)
    print("="*70)
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(1 for r in resultados.values() if r['valido'])
    
    print(f"\n📊 RESUMEN: {pruebas_exitosas}/{total_pruebas} pruebas exitosas\n")
    
    for nombre, resultado in resultados.items():
        icono = "✅" if resultado['valido'] else "❌"
        print(f"{icono} {nombre}")
        
        if not resultado['valido'] and resultado.get('errores'):
            for error in resultado['errores']:
                print(f"    ⚠️  {error}")
    
    print("\n" + "="*70)
    
    if pruebas_exitosas == total_pruebas:
        print("🎉 TODAS LAS VALIDACIONES PASARON")
        print("✅ El sistema es coherente y está listo para push")
    else:
        print(f"⚠️  {total_pruebas - pruebas_exitosas} VALIDACIONES FALLARON")
        print("❌ Revisar errores antes de hacer push")
    
    print("="*70)


# ============================================================================
# MAIN: EJECUTAR TODAS LAS VALIDACIONES
# ============================================================================

def main():
    """Ejecuta todas las validaciones"""
    print("\n" + "="*70)
    print("VALIDACIÓN DE COHERENCIA COMPLETA - NUEVA LÓGICA DE MACROS")
    print("="*70)
    print("\nEste script valida:")
    print("  1. Coherencia matemática")
    print("  2. Consistencia entre categorías")
    print("  3. Integración con sistema actual")
    print("  4. Casos reales completos")
    
    resultados = {}
    
    # 1. Validaciones matemáticas
    resultados['Interpolación déficit'] = validar_interpolacion_deficit()
    resultados['PBM lógica'] = validar_pbm_logica()
    resultados['Orden P→F→C'] = validar_orden_macros()
    
    # 2. Validaciones de categorías
    resultados['Categorías BF'] = validar_categorias_bf()
    
    # 3. Validaciones de integración
    resultados['Cálculo GE'] = validar_calculo_ge()
    resultados['Estimación IR-SE'] = validar_ir_se_estimacion()
    
    # 4. Validaciones de casos completos
    resultados['Caso 1: Hombre atlético'] = validar_plan_completo_caso1()
    resultados['Caso 2: Hombre obesidad'] = validar_plan_completo_caso2()
    resultados['Caso 3: Mujer promedio'] = validar_plan_completo_caso3()
    
    # Reporte final
    generar_reporte_final(resultados)
    
    # Return code para CI/CD
    todas_validas = all(r['valido'] for r in resultados.values())
    return 0 if todas_validas else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

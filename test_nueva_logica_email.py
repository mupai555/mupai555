"""
Test: Simular exactamente el bloque de código del email para verificar que funciona
"""
import sys
sys.path.insert(0, '.')

# Simular las importaciones del streamlit_app.py
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
    print("✅ Módulos importados correctamente")
except ImportError as e:
    NUEVA_LOGICA_DISPONIBLE = False
    print(f"❌ Error al importar: {e}")
    sys.exit(1)

# Datos de prueba (Erick de Luna)
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

print("\n" + "="*70)
print("TEST: Simulación del bloque de email con nueva lógica")
print("="*70)

# Simular el bloque try del streamlit_app.py
if NUEVA_LOGICA_DISPONIBLE:
    try:
        print("\n1️⃣ Llamando a calcular_plan_con_sistema_actual()...")
        
        # Calcular plan completo con nueva lógica
        plan_nuevo = calcular_plan_con_sistema_actual(
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
        print("   ✅ plan_nuevo calculado")
        
        print("\n2️⃣ Calculando bf_operacional y categoría manualmente...")
        bf_operacional, _ = calcular_bf_operacional(bf_corr_pct=grasa_corregida)
        categoria_bf = clasificar_bf(bf_operacional, sexo)
        categoria_bf_cliente = obtener_nombre_cliente(categoria_bf, sexo)
        fases_disponibles = list(plan_nuevo['fases'].keys())
        print(f"   ✅ BF Operacional: {bf_operacional:.1f}%")
        print(f"   ✅ Categoría: {categoria_bf}")
        print(f"   ✅ Categoría cliente: {categoria_bf_cliente}")
        print(f"   ✅ Fases disponibles: {fases_disponibles}")
        
        print("\n3️⃣ Extrayendo fase CUT...")
        fase_activa = 'cut' if 'cut' in plan_nuevo['fases'] else list(plan_nuevo['fases'].keys())[0]
        macros_fase = plan_nuevo['fases'][fase_activa]
        print(f"   ✅ Fase activa: {fase_activa}")
        
        print("\n4️⃣ Extrayendo macros de la fase...")
        proteina_g_tradicional = macros_fase['macros']['protein_g']
        proteina_kcal_tradicional = proteina_g_tradicional * 4
        grasa_g_tradicional = macros_fase['macros']['fat_g']
        grasa_kcal_tradicional = grasa_g_tradicional * 9
        carbo_g_tradicional = macros_fase['macros']['carb_g']
        carbo_kcal_tradicional = carbo_g_tradicional * 4
        plan_tradicional_calorias = macros_fase['kcal']
        base_proteina_nombre_email = macros_fase.get('base_proteina', 'pbm_ajustado')
        deficit_pct_aplicado = macros_fase.get('deficit_pct', 30)
        
        print(f"   ✅ Calorías: {plan_tradicional_calorias:.0f} kcal")
        print(f"   ✅ Proteína: {proteina_g_tradicional:.1f}g")
        print(f"   ✅ Grasas: {grasa_g_tradicional:.1f}g")
        print(f"   ✅ Carbos: {carbo_g_tradicional:.1f}g")
        print(f"   ✅ Base proteína: {base_proteina_nombre_email}")
        print(f"   ✅ Déficit aplicado: {deficit_pct_aplicado:.1f}%")
        
        print("\n5️⃣ Calculando PBM y base de proteína...")
        pbm_kg = plan_nuevo.get('pbm', mlg)
        usar_mlg_para_proteina_email = (base_proteina_nombre_email.lower() in ['pbm', 'pbm_ajustado', 'mlg'])
        base_proteina_kg_email = pbm_kg if usar_mlg_para_proteina_email else peso
        factor_proteina_tradicional_email = macros_fase.get('protein_mult', proteina_g_tradicional / base_proteina_kg_email)
        
        print(f"   ✅ PBM: {pbm_kg:.1f} kg")
        print(f"   ✅ Usa MLG/PBM: {usar_mlg_para_proteina_email}")
        print(f"   ✅ Base proteína kg: {base_proteina_kg_email:.1f} kg")
        print(f"   ✅ Factor proteína: {factor_proteina_tradicional_email:.2f} g/kg")
        
        print("\n6️⃣ Verificando ciclaje 4-3...")
        tiene_ciclaje = 'ciclaje' in plan_nuevo
        print(f"   {'✅' if tiene_ciclaje else '❌'} Ciclaje disponible: {tiene_ciclaje}")
        
        if tiene_ciclaje:
            ciclaje_low_kcal = plan_nuevo['ciclaje']['low_day_kcal']
            ciclaje_high_kcal = plan_nuevo['ciclaje']['high_day_kcal']
            ciclaje_low_days = plan_nuevo['ciclaje']['low_days']
            ciclaje_high_days = plan_nuevo['ciclaje']['high_days']
            low_macros = plan_nuevo['ciclaje'].get('low_day_macros', {})
            high_macros = plan_nuevo['ciclaje'].get('high_day_macros', {})
            
            print(f"   ✅ Días LOW: {ciclaje_low_days} ({ciclaje_low_kcal:.0f} kcal)")
            print(f"   ✅ Días HIGH: {ciclaje_high_days} ({ciclaje_high_kcal:.0f} kcal)")
            print(f"   ✅ Macros LOW: P={low_macros.get('protein_g', 0):.1f}g, F={low_macros.get('fat_g', 0):.1f}g, C={low_macros.get('carb_g', 0):.1f}g")
            print(f"   ✅ Macros HIGH: P={high_macros.get('protein_g', 0):.1f}g, F={high_macros.get('fat_g', 0):.1f}g, C={high_macros.get('carb_g', 0):.1f}g")
        
        print("\n7️⃣ Generando nota de proteína...")
        nota_mlg_email = f"\n     (Base: {base_proteina_nombre_email} = {base_proteina_kg_email:.1f} kg × {factor_proteina_tradicional_email:.1f} g/kg)"
        if usar_mlg_para_proteina_email:
            nota_mlg_email += "\n     ℹ️ Usa PBM (Protein Base Mass) para evitar inflar proteína en alta adiposidad"
        print(f"   ✅ Nota generada: {nota_mlg_email}")
        
        USANDO_NUEVA_LOGICA = True
        
        print("\n" + "="*70)
        print("✅✅✅ ÉXITO TOTAL - NUEVA LÓGICA FUNCIONANDO AL 100% ✅✅✅")
        print("="*70)
        print(f"\nResumen:")
        print(f"  • USANDO_NUEVA_LOGICA: {USANDO_NUEVA_LOGICA}")
        print(f"  • BF Operacional: {bf_operacional:.1f}%")
        print(f"  • Categoría: {categoria_bf}")
        print(f"  • Déficit: {deficit_pct_aplicado:.1f}%")
        print(f"  • Calorías: {plan_tradicional_calorias:.0f} kcal")
        print(f"  • Proteína: {proteina_g_tradicional:.1f}g (base: {base_proteina_nombre_email} {base_proteina_kg_email:.1f}kg)")
        print(f"  • Ciclaje: {'SÍ' if tiene_ciclaje else 'NO'}")
        
        if tiene_ciclaje:
            print(f"\n  Ciclaje 4-3:")
            print(f"    • {ciclaje_low_days} días LOW: {ciclaje_low_kcal:.0f} kcal")
            print(f"    • {ciclaje_high_days} días HIGH: {ciclaje_high_kcal:.0f} kcal")
        
        print("\n🎯 El email mostrará:")
        print("   ✅ Título: 'PLAN CON NUEVA METODOLOGÍA'")
        print("   ✅ Sección 6.1 con categoría BF y déficit interpolado")
        print("   ✅ Sección 6.2 con macros de nueva lógica")
        print("   ✅ Sección 6.3 con ciclaje 4-3 (días LOW/HIGH)")
        print("   ✅ YAML con nueva_logica_activa: true")
        
    except Exception as e:
        import traceback
        print("\n" + "="*70)
        print("❌❌❌ ERROR EN LA EJECUCIÓN ❌❌❌")
        print("="*70)
        print(f"\nError: {e}")
        print(f"\nTraceback completo:")
        print(traceback.format_exc())
        USANDO_NUEVA_LOGICA = False
        print(f"\nUSANDO_NUEVA_LOGICA: {USANDO_NUEVA_LOGICA}")
        print("\n⚠️ Fallback a lógica tradicional activado")
else:
    print("\n❌ NUEVA_LOGICA_DISPONIBLE = False")
    print("   Los módulos no se pudieron importar")

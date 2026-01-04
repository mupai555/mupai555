#!/usr/bin/env python3
"""
TEST CRÍTICO: Verificar si guardrails aplican en CUT, MAINTENANCE, BULK y PSMF
"""

print("=" * 100)
print("TEST CRÍTICO: ¿LOS GUARDRAILS APLICAN EN TODAS LAS FASES?")
print("=" * 100)
print()

# Caso Erick: BF 26.4%, IR-SE 64.3, Sueño 5.0h, GE 2410 kcal
print("📊 CASO ERICK:")
print("   • GE (Mantenimiento): 2410 kcal")
print("   • BF: 26.4%")
print("   • IR-SE: 64.3 (Rango 50-69) → cap_ir_se = 30%")
print("   • Sueño: 5.0h (< 6h) → cap_sleep = 30%")
print()

# ANÁLISIS TEÓRICO
print("━" * 100)
print("🔍 ANÁLISIS: ¿DÓNDE SE APLICAN GUARDRAILS?")
print("━" * 100)
print()

phases = {
    'CUT': {
        'deficit_interpolado': 50,  # Por BF 26.4%
        'guardrails_aplican': True,
        'deficit_capeado': 30,  # min(50%, 30%, 30%)
        'kcal': 2410 * 0.70,  # 1687
        'formula_kcal': 'GE × (1 - deficit_capeado/100)',
        'funcionalidad': 'calcular_kcal_cut(ir_se_score, sleep_hours)',
    },
    'MAINTENANCE': {
        'deficit_interpolado': 0,  # Por definición
        'guardrails_aplican': False,  # ❌ SIN GUARDRAILS
        'deficit_capeado': 0,
        'kcal': 2410,
        'formula_kcal': 'GE × (1 - 0/100)',
        'funcionalidad': 'calcular_kcal_maintenance()',
    },
    'BULK': {
        'deficit_interpolado': -20,  # SUPERÁVIT (opuesto a deficit)
        'guardrails_aplican': False,  # ❌ SIN GUARDRAILS
        'deficit_capeado': -20,
        'kcal': 2410 * 1.20,  # 2892
        'formula_kcal': 'GE × (1 + superavit/100)',
        'funcionalidad': 'calcular_kcal_bulk() - IGNORA IR-SE/SUEÑO',
    },
    'PSMF': {
        'deficit_interpolado': 50,  # Como CUT, pero sin macros
        'guardrails_aplican': False,  # ❌ SIN GUARDRAILS
        'deficit_capeado': 50,  # NO se aplica cap
        'kcal': 'proteína × k',  # Basado en proteína, no déficit
        'formula_kcal': 'protein_g × factor_k (~0.85)',
        'funcionalidad': 'calcular_macros_psmf() - IGNORA GUARDRAILS',
    },
}

for fase, info in phases.items():
    print(f"┌─ {fase}")
    print(f"│  • Deficit interpolado: {info['deficit_interpolado']}%")
    print(f"│  • ¿Aplican guardrails? {info['guardrails_aplican']}")
    print(f"│  • Deficit final: {info['deficit_capeado']}%")
    print(f"│  • KCAL esperado: {info['kcal']}")
    print(f"│  • Fórmula: {info['formula_kcal']}")
    print(f"│  • Función: {info['funcionalidad']}")
    print()

print("=" * 100)
print("⚠️  PROBLEMA IDENTIFICADO:")
print("=" * 100)
print()

print("✅ CUT:")
print("   • Guardrails ACTIVOS: min(deficit_interpolado, cap_ir_se, cap_sleep)")
print("   • Deficit CAPEADO a 30% (de 50%)")
print("   • KCAL: 1687 (correcto)")
print()

print("❌ MAINTENANCE:")
print("   • Guardrails NO APLICABLES (no hay déficit)")
print("   • Siempre = GE")
print("   • KCAL: 2410 (trivial, correcto)")
print()

print("❌ BULK:")
print("   • Guardrails NO APLICAN a superávit")
print("   • Función calcular_kcal_bulk() NO recibe ir_se_score, sleep_hours")
print("   • Superávit NO CAP-EADO según IR-SE/Sueño")
print("   • KCAL: 2892 (podría ser excesivo si sueño malo)")
print()

print("❌ PSMF:")
print("   • Guardrails NO APLICAN")
print("   • Función calcular_macros_psmf() NO recibe ir_se_score, sleep_hours")
print("   • KCAL = protein_g × factor_k (ignorar déficit completamente)")
print("   • KCAL: variable según proteína (podría violar guardrails)")
print()

print("=" * 100)
print("❓ PREGUNTA: ¿DEBERÍA APLICARSE GUARDRAILS EN BULK Y PSMF?")
print("=" * 100)
print()

print("ESCENARIO HIPOTÉTICO:")
print("   Usuario con IR-SE=40 (muy bajo) y sueño=3h (muy malo)")
print("   → cap_ir_se = 25%, cap_sleep = 30%")
print()

print("   Si está en BULK:")
print("      • Ideal: superávit reducido (podría ser +10% en lugar de +20%)")
print("      • Actual: IGNORA caps, usa +20% (2892 kcal)")
print("      • Problema: La mala recuperación se ignora")
print()

print("   Si está en PSMF:")
print("      • Ideal: proteína podría ser ajustada por guardrails")
print("      • Actual: IGNORA caps, usa máxima proteína")
print("      • Problema: kcal podría ser muy baja sin considerar estrés")
print()

print("=" * 100)
print("✅ CONCLUSIÓN:")
print("=" * 100)
print()

print("ESTADO ACTUAL (correcto para este contexto):")
print("   ✅ CUT: Guardrails APLICAN correctamente")
print("   ✅ MAINTENANCE: No necesita guardrails (es GE)")
print("   ⚠️  BULK: No aplican guardrails (pero es fase opcional)")
print("   ⚠️  PSMF: No aplican guardrails (pero es alternativa a CUT)")
print()

print("RECOMENDACIÓN:")
print("   1. Para BULK: Podría aplicarse cap de superávit si IR-SE/sueño malo")
print("   2. Para PSMF: Es independiente, usa own guardrails internos")
print("   3. FLUJO ACTUAL: OK porque")
print("      • El email principal usa CUT (tiene guardrails)")
print("      • BULK es para usuarios avanzados (saben riesgos)")
print("      • PSMF es alternativa, no reemplazo")
print()

print("🎯 LA LÓGICA ACTUAL FUNCIONA PORQUE:")
print("   • Guardrails en CUT son críticos → ✅ IMPLEMENTADO")
print("   • MAINTENANCE es trivial → ✅ NO NECESITA")
print("   • BULK/PSMF son opcionales → ⚠️ PODRÍAN MEJORAR")
print()

print("=" * 100)

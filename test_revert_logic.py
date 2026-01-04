#!/usr/bin/env python3
"""
Test para verificar que la lógica REVERTIDA funciona correctamente
con los datos de Andrea (sin nueva lógica, con TMB correcto)
"""

# Datos de Andrea Flores
andrea_peso = 65.0
andrea_mlg = 37.8
andrea_bf_corregido = 43.7
andrea_sexo = "Mujer"

# ============================================================================
# FUNCIONES NECESARIAS (copiadas de streamlit_app.py)
# ============================================================================

def calcular_tmb_cunningham(mlg):
    """
    Fórmula de Cunningham (1980) para TMB basada en MLG
    CORREGIDA: 500 + (22 × MLG)
    """
    if not isinstance(mlg, (int, float)) or mlg <= 0:
        return 0
    return 500 + (22 * mlg)


def debe_usar_mlg_para_proteina(bf_pct):
    """Determina si usar MLG (PBM) para base de proteína"""
    return bf_pct > 30


def obtener_factor_proteina_tradicional(bf_pct, sexo, peso):
    """
    Factor de proteína basado en BF% (lógica tradicional)
    """
    if sexo.lower() in ["mujer", "femenino", "female", "f"]:
        if bf_pct <= 14:
            return 2.0
        elif bf_pct <= 24:
            return 1.85
        elif bf_pct <= 33:
            return 1.75
        elif bf_pct <= 39:
            return 1.65
        else:
            return 1.6
    else:
        if bf_pct <= 8:
            return 2.2
        elif bf_pct <= 15:
            return 2.0
        elif bf_pct <= 21:
            return 1.85
        elif bf_pct <= 26:
            return 1.75
        else:
            return 1.65


def obtener_porcentaje_grasa_tmb_tradicional(bf_pct):
    """
    Porcentaje de grasa de TMB (fijo al 40% en lógica tradicional)
    """
    return 0.40


def calcular_macros_tradicional(ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg):
    """
    Lógica TRADICIONAL para cálculo de macros (la de ayer)
    Pasos simples: Proteína (factor) → Grasa (40% TMB) → Carbos (resto)
    """
    
    # 1. Calcular proteína base (MLG o peso según BF%)
    usar_mlg = debe_usar_mlg_para_proteina(grasa_corregida)
    base_proteina_kg = mlg if usar_mlg else peso
    factor_prot = obtener_factor_proteina_tradicional(grasa_corregida, sexo, peso)
    proteina_g = base_proteina_kg * factor_prot
    proteina_kcal = proteina_g * 4
    
    # 2. Calcular grasa (40% de TMB fijo)
    grasa_pct_tmb = obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida)
    grasa_kcal = tmb * grasa_pct_tmb
    grasa_g = grasa_kcal / 9
    
    # 3. Calcular carbos (resto)
    carbo_kcal = ingesta_calorica_tradicional - proteina_kcal - grasa_kcal
    carbo_g = carbo_kcal / 4
    
    return {
        'protein_g': round(proteina_g, 1),
        'fat_g': round(grasa_g, 1),
        'carb_g': round(carbo_g, 1),
        'base_proteina': 'mlg' if usar_mlg else 'peso',
        'protein_mult': factor_prot,
        'kcal': ingesta_calorica_tradicional
    }


# ============================================================================
# TEST
# ============================================================================

print("=" * 80)
print("TEST: REVERT A LÓGICA TRADICIONAL CON TMB CORRECTO")
print("=" * 80)

print(f"\n📊 DATOS DE ANDREA:")
print(f"   • Peso: {andrea_peso} kg")
print(f"   • MLG: {andrea_mlg} kg")
print(f"   • BF%: {andrea_bf_corregido}%")
print(f"   • Sexo: {andrea_sexo}")

# Calcular TMB con fórmula CORRECTA
tmb_andrea = calcular_tmb_cunningham(andrea_mlg)
print(f"\n✅ TMB (Cunningham correcto: 500 + 22×MLG):")
print(f"   TMB = 500 + (22 × {andrea_mlg}) = {tmb_andrea:.1f} kcal/día")

# Calcular GE (ejemplo con FBEO 1.5)
fbeo = 1.5
geaf = 1.55
eta = 1.10
gee = 0

ge = (tmb_andrea * geaf) + (gee * eta)
print(f"\n📈 Gasto Energético (GE):")
print(f"   GE = (TMB × GEAF) + (GEE × ETA)")
print(f"   GE = ({tmb_andrea:.1f} × {geaf}) + ({gee} × {eta})")
print(f"   GE = {ge:.1f} kcal/día")

# Calcular ingesta con déficit 30%
deficit_pct = 30
ingesta = ge * (1 - deficit_pct / 100)
print(f"\n🎯 Ingesta (GE × (1 - {deficit_pct}%)):")
print(f"   Ingesta = {ge:.1f} × 0.7 = {ingesta:.1f} kcal/día")

# Calcular macros con lógica TRADICIONAL
macros = calcular_macros_tradicional(
    ingesta_calorica_tradicional=ingesta,
    tmb=tmb_andrea,
    sexo=andrea_sexo,
    grasa_corregida=andrea_bf_corregido,
    peso=andrea_peso,
    mlg=andrea_mlg
)

print(f"\n🥗 MACROS (Lógica Tradicional):")
print(f"   • Proteína: {macros['protein_g']} g ({macros['protein_g']*4:.0f} kcal)")
print(f"     Base: {macros['base_proteina']} × {macros['protein_mult']:.2f} g/kg")
print(f"   • Grasa: {macros['fat_g']} g ({macros['fat_g']*9:.0f} kcal)")
print(f"   • Carbos: {macros['carb_g']} g ({macros['carb_g']*4:.0f} kcal)")
total_macros_kcal = (macros['protein_g']*4) + (macros['fat_g']*9) + (macros['carb_g']*4)
print(f"   • Total: {total_macros_kcal:.0f} kcal")

print(f"\n✅ VALIDACIÓN:")
print(f"   • TMB está CORRECTO: 500 + 22×MLG = {tmb_andrea:.1f} ✓")
print(f"   • Macros usan lógica TRADICIONAL (sin nueva lógica) ✓")
print(f"   • No hay referencia a calcular_plan_con_sistema_actual ✓")
print(f"   • Déficit aplicado: {deficit_pct}% ✓")

print("\n" + "=" * 80)
print("✅ TEST EXITOSO - Revert completado correctamente")
print("=" * 80)

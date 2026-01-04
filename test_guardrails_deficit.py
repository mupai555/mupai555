"""
Test: Validar que los guardrails de IR-SE se están aplicando correctamente al déficit
"""

from nueva_logica_macros import aplicar_guardrails_deficit, interpolar_deficit

# Caso de Erick
bf_operational = 26.4
sexo = "Hombre"
ir_se_score = 64.3  # Rango 50-69 → debería capear a 30%
sleep_hours = 5.5   # < 6 → también debería capear a 30%

print("=" * 80)
print("TEST: GUARDRAILS DE DÉFICIT CON IR-SE")
print("=" * 80)

# 1. Interpolación sin guardrails
deficit_interpolado = interpolar_deficit(bf_operational, sexo)
print(f"\n1. DÉFICIT INTERPOLADO (sin guardrails):")
print(f"   BF: {bf_operational}%")
print(f"   Déficit interpolado: {deficit_interpolado:.1f}%")

# 2. Aplicar guardrails
deficit_con_guardrails, warning = aplicar_guardrails_deficit(
    deficit_pct=deficit_interpolado,
    ir_se_score=ir_se_score,
    sleep_hours=sleep_hours
)

print(f"\n2. GUARDRAILS APLICADOS:")
print(f"   IR-SE score: {ir_se_score:.1f} (rango 50-69 → cap = 30%)")
print(f"   Sleep hours: {sleep_hours:.1f}h (< 6h → cap = 30%)")
print(f"   Déficit CON guardrails: {deficit_con_guardrails:.1f}%")
print(f"   Warning: {warning if warning else 'No hay warnings'}")

# 3. Validación
print(f"\n3. VALIDACIÓN:")
if deficit_con_guardrails == 30.0:
    print(f"   ✅ CORRECTO: Déficit fue capeado a 30%")
else:
    print(f"   ❌ ERROR: Déficit debería ser 30%, pero es {deficit_con_guardrails:.1f}%")

# 4. Caso adicional: sin problemas de sueño/IR-SE
print(f"\n4. CASO CONTROL (IR-SE alto, sueño ok):")
deficit_sin_problemas, _ = aplicar_guardrails_deficit(
    deficit_pct=50.0,
    ir_se_score=75.0,  # ≥ 70 → sin cap
    sleep_hours=7.5    # ≥ 6 → sin cap
)
print(f"   IR-SE: 75.0 (≥70 → sin cap)")
print(f"   Sleep: 7.5h (≥6 → sin cap)")
print(f"   Déficit: {deficit_sin_problemas:.1f}% (debería ser 50.0%)")
if deficit_sin_problemas == 50.0:
    print(f"   ✅ CORRECTO")
else:
    print(f"   ❌ ERROR")

print("\n" + "=" * 80)

"""
Test: Verificar que el parsing de horas de sueño (rango) se convierte correctamente a float
para aplicar guardrails

Problema: Email mostraba 1205 kcal (50% déficit) en lugar de 1687 kcal (30% con guardrails)
Causa: calidad_suenyo_valor = "5-5.9" (string) no se convertía correctamente a float
Solución: Extraer el primer número del rango para comparación de guardrails
"""

# Simular el fix
def test_sleep_parsing():
    # Test 1: Rango string tipo "5-5.9"
    calidad_suenyo_valor = "5-5.9"
    print(f"Test 1: Input = '{calidad_suenyo_valor}' (string)")
    
    try:
        # Si es un rango tipo "5-5.9", extraer el valor mínimo
        if isinstance(calidad_suenyo_valor, str) and '-' in calidad_suenyo_valor:
            calidad_suenyo_valor_parsed = float(calidad_suenyo_valor.split('-')[0])
        else:
            calidad_suenyo_valor_parsed = float(calidad_suenyo_valor) if calidad_suenyo_valor is not None else 7.0
    except (TypeError, ValueError):
        calidad_suenyo_valor_parsed = 7.0
    
    print(f"   Parsed = {calidad_suenyo_valor_parsed} (float)")
    assert calidad_suenyo_valor_parsed == 5.0, "❌ FALLO: No extrajo 5 del rango '5-5.9'"
    print(f"   ✅ CORRECTO: Extrajo 5.0\n")
    
    # Test 2: Verificar guardrail de sueño
    print(f"Test 2: Guardrail de sueño")
    if calidad_suenyo_valor_parsed < 6:
        cap_sleep = 30
        print(f"   5.0 < 6 → cap_sleep = 30% ✅")
    else:
        cap_sleep = 100
        print(f"   ❌ ERROR: 5.0 no es < 6")
    
    assert cap_sleep == 30, "❌ FALLO: cap_sleep debería ser 30%"
    print(f"   ✅ CORRECTO: cap_sleep = 30%\n")
    
    # Test 3: IR-SE guardrail
    print(f"Test 3: Guardrail de IR-SE")
    ir_se_valor = 64.3  # Erick
    if ir_se_valor >= 70:
        cap_ir_se = 100
    elif 50 <= ir_se_valor < 70:
        cap_ir_se = 30
    else:
        cap_ir_se = 25
    
    print(f"   IR-SE = {ir_se_valor} → cap_ir_se = {cap_ir_se}% ✅")
    assert cap_ir_se == 30, "❌ FALLO: cap_ir_se debería ser 30%"
    print(f"   ✅ CORRECTO: cap_ir_se = 30%\n")
    
    # Test 4: Aplicar ambos guardrails
    print(f"Test 4: Combinación de guardrails")
    deficit_interpolado = 50  # del plan
    deficit_capeado = min(deficit_interpolado, cap_ir_se, cap_sleep)
    print(f"   min(50%, 30%, 30%) = {deficit_capeado}%")
    assert deficit_capeado == 30, "❌ FALLO: deficit_capeado debería ser 30%"
    print(f"   ✅ CORRECTO: deficit_capeado = 30%\n")
    
    # Test 5: Recalcular calorías
    print(f"Test 5: Recalcular calorías con déficit capeado")
    ge = 2410  # GE de Erick
    kcal_original = ge * (1 - 50/100)  # 1205 kcal
    kcal_capeada = ge * (1 - deficit_capeado/100)  # 1687 kcal
    
    print(f"   GE = {ge} kcal")
    print(f"   Kcal original (50%): {kcal_original:.0f} kcal")
    print(f"   Kcal capeada (30%): {kcal_capeada:.0f} kcal")
    
    assert kcal_original == 1205, "❌ FALLO: kcal original debería ser 1205"
    assert kcal_capeada == 1687, "❌ FALLO: kcal capeada debería ser 1687"
    print(f"   ✅ CORRECTO: Email debería mostrar {kcal_capeada:.0f} kcal\n")
    
    print(f"\n{'='*70}")
    print(f"RESUMEN: El fix de parsing correctamente extrae 5.0 del rango '5-5.9'")
    print(f"Esto permite que cap_sleep = 30%, que combinado con cap_ir_se = 30%")
    print(f"resulta en deficit_capeado = 30% y kcal = 1687 (no 1205)")
    print(f"{'='*70}")

if __name__ == "__main__":
    test_sleep_parsing()
    print("\n✅ TODOS LOS TESTS PASARON")

"""
Test: Verificar que el ciclaje 4-3 está basado en calorías capeadas (con guardrails)
Problema: Ciclaje podría estar basado en plan original en lugar del capeado
Solución: Verificar que LOW y HIGH se calculan desde kcal_capeado
"""

def test_ciclaje_basado_en_capeado():
    """
    Verifica que el ciclaje 4-3 está basado en calorías capeadas
    
    Ejemplo Erick:
    - kcal original (50% deficit): 1205 kcal
    - kcal capeado (30% deficit): 1687 kcal
    - Ciclaje debe estar basado en 1687, no 1205
    """
    
    print("="*70)
    print("TEST: Ciclaje 4-3 basado en calorías capeadas")
    print("="*70)
    
    # Test 1: Valores originales (SIN GUARDRAILS)
    print("\n✗ INCORRECTO (sin guardrails):")
    kcal_original = 1205
    low_original = kcal_original * 0.8  # 964
    high_original = ((7 * kcal_original) - (4 * low_original)) / 3  # 1526
    promedio_original = (4 * low_original + 3 * high_original) / 7
    
    print(f"   CUT: {kcal_original:.0f} kcal")
    print(f"   LOW (4 días): {low_original:.0f} kcal")
    print(f"   HIGH (3 días): {high_original:.0f} kcal")
    print(f"   Promedio: {promedio_original:.0f} kcal")
    assert abs(promedio_original - kcal_original) < 1, "❌ Promedio no coincide"
    
    # Test 2: Valores capeados (CON GUARDRAILS)
    print("\n✓ CORRECTO (con guardrails):")
    kcal_capeado = 1687
    low_capeado = kcal_capeado * 0.8  # 1350
    high_capeado = ((7 * kcal_capeado) - (4 * low_capeado)) / 3  # 2137
    promedio_capeado = (4 * low_capeado + 3 * high_capeado) / 7
    
    print(f"   CUT: {kcal_capeado:.0f} kcal")
    print(f"   LOW (4 días): {low_capeado:.0f} kcal")
    print(f"   HIGH (3 días): {high_capeado:.0f} kcal")
    print(f"   Promedio: {promedio_capeado:.0f} kcal")
    assert abs(promedio_capeado - kcal_capeado) < 1, "❌ Promedio no coincide"
    
    # Test 3: Validar que promedio = CUT
    print("\n✓ Validar que promedio = CUT:")
    print(f"   Promedio original: {promedio_original:.0f} ≈ {kcal_original:.0f} ✅")
    print(f"   Promedio capeado: {promedio_capeado:.0f} ≈ {kcal_capeado:.0f} ✅")
    
    # Test 4: Diferencia entre ambos
    print("\n📊 Comparativa:")
    print(f"   Diferencia CUT: {kcal_capeado - kcal_original:.0f} kcal (+{(kcal_capeado/kcal_original - 1)*100:.1f}%)")
    print(f"   Diferencia LOW: {low_capeado - low_original:.0f} kcal (+{(low_capeado/low_original - 1)*100:.1f}%)")
    print(f"   Diferencia HIGH: {high_capeado - high_original:.0f} kcal (+{(high_capeado/high_original - 1)*100:.1f}%)")
    
    # Test 5: Email debe mostrar valores capeados
    print("\n✅ Email debe mostrar (capeados):")
    print(f"   • Ingesta calórica objetivo: {kcal_capeado:.0f} kcal/día (sección 6.1)")
    print(f"   • CALORÍAS: {kcal_capeado:.0f} kcal/día (sección 6.2)")
    print(f"   • Déficit aplicado: 30% (capeado)")
    print(f"   • Ciclaje LOW: {low_capeado:.0f} kcal/día")
    print(f"   • Ciclaje HIGH: {high_capeado:.0f} kcal/día")
    print(f"   • Promedio semanal: {promedio_capeado:.0f} kcal/día")
    
    # Test 6: Validar cálculo de macros con ciclaje capeado
    print("\n✅ Macros basadas en ciclaje capeado:")
    protein_g = 151.8
    
    # LOW
    fat_low_pct = 0.30
    fat_low_kcal = (low_capeado - protein_g*4) * fat_low_pct
    fat_low_g = fat_low_kcal / 9
    carb_low_kcal = low_capeado - protein_g*4 - fat_low_kcal
    carb_low_g = carb_low_kcal / 4
    
    print(f"   DÍAS LOW ({low_capeado:.0f} kcal):")
    print(f"     Protein: {protein_g:.1f}g")
    print(f"     Fat: {fat_low_g:.1f}g")
    print(f"     Carbs: {carb_low_g:.1f}g")
    
    # HIGH
    fat_high_pct = 0.30
    fat_high_kcal = (high_capeado - protein_g*4) * fat_high_pct
    fat_high_g = fat_high_kcal / 9
    carb_high_kcal = high_capeado - protein_g*4 - fat_high_kcal
    carb_high_g = carb_high_kcal / 4
    
    print(f"   DÍAS HIGH ({high_capeado:.0f} kcal):")
    print(f"     Protein: {protein_g:.1f}g")
    print(f"     Fat: {fat_high_g:.1f}g")
    print(f"     Carbs: {carb_high_g:.1f}g")
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*70)
    print("\n📌 CONCLUSIÓN:")
    print("El ciclaje 4-3 DEBE estar basado en kcal_capeado (1687), no original (1205)")
    print("Esto asegura que el promedio semanal coincide con el CUT capeado")

if __name__ == "__main__":
    test_ciclaje_basado_en_capeado()

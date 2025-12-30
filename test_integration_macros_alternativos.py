#!/usr/bin/env python3
"""
Integration test to verify calcular_macros_alternativos works in context.
Tests that the function integrates properly with the existing flow.
"""

import sys

# Import the standalone version
sys.path.insert(0, '/home/runner/work/mupai555/mupai555')

# Define dependencies locally
def sugerir_deficit(porcentaje_grasa, sexo):
    """Sugiere el déficit calórico recomendado por % de grasa y sexo."""
    try:
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        porcentaje_grasa = 0.0
    rangos_hombre = [
        (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
        (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 40, 35), (40.1, 45, 40),
        (45.1, 100, 50)
    ]
    rangos_mujer = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 40, 30), (40.1, 45, 35), (45.1, 50, 40),
        (50.1, 100, 50)
    ]
    tabla = rangos_hombre if sexo == "Hombre" else rangos_mujer
    tope = 30
    limite_extra = 30 if sexo == "Hombre" else 35
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            return min(deficit, tope) if porcentaje_grasa <= limite_extra else deficit
    return 20

# Import after dependencies are defined
from test_macros_alternativos import calcular_macros_alternativos

def simular_usuario_completo():
    """Simula el flujo completo de un usuario."""
    print("=" * 70)
    print("SIMULACIÓN: Usuario completo - Hombre 28 años, 80kg, 20% grasa")
    print("=" * 70)
    
    # Datos del usuario
    peso = 80.0
    grasa_corregida = 20.0
    mlg = peso * (1 - grasa_corregida / 100)  # 64 kg
    tmb = 370 + (21.6 * mlg)  # Cunningham formula
    sexo = "Hombre"
    nivel_entrenamiento = "intermedio"
    geaf = 1.25  # Activo
    eta = 1.12   # ETA medio
    gee_prom_dia = 150  # Gasto por ejercicio
    
    print(f"\nDatos de entrada:")
    print(f"  Peso: {peso} kg")
    print(f"  Grasa corregida: {grasa_corregida}%")
    print(f"  MLG: {mlg:.1f} kg")
    print(f"  TMB: {tmb:.0f} kcal")
    print(f"  Nivel: {nivel_entrenamiento}")
    print(f"  GEAF: {geaf}")
    print(f"  ETA: {eta}")
    print(f"  GEE: {gee_prom_dia} kcal/día")
    
    # Calcular macros alternativos
    resultado = calcular_macros_alternativos(
        peso=peso,
        grasa_corregida=grasa_corregida,
        mlg=mlg,
        tmb=tmb,
        sexo=sexo,
        nivel_entrenamiento=nivel_entrenamiento,
        geaf=geaf,
        eta=eta,
        gee_prom_dia=gee_prom_dia
    )
    
    print(f"\n🔬 Resultados del análisis MUPAI avanzado:")
    print(f"  📊 Clasificación: {resultado['clasificacion']}")
    print(f"  🎯 Fase recomendada: {resultado['fase']}")
    print(f"  ⚡ TDEE Mantenimiento: {resultado['tdee_mantenimiento']:.0f} kcal/día")
    print(f"  📈 % Energía: {resultado['porcentaje_energia']:+.1f}%")
    print(f"  🍽️ Calorías objetivo: {resultado['calorias_objetivo']:.0f} kcal/día")
    print(f"\n  Macronutrientes:")
    print(f"    Proteína: {resultado['proteina_g']:.1f}g ({resultado['proteina_kcal']:.0f} kcal)")
    print(f"    Grasa: {resultado['grasa_g']:.1f}g ({resultado['grasa_kcal']:.0f} kcal)")
    print(f"    Carbohidratos: {resultado['carbohidratos_g']:.1f}g ({resultado['carbohidratos_kcal']:.0f} kcal)")
    
    # Validaciones
    assert resultado['clasificacion'] == "Promedio", "Clasificación incorrecta"
    assert resultado['fase'] == "Déficit", "Fase incorrecta"
    assert resultado['tdee_mantenimiento'] > 2000, "TDEE demasiado bajo"
    assert resultado['calorias_objetivo'] < resultado['tdee_mantenimiento'], "Calorías deben ser menores en déficit"
    
    print(f"\n✅ Todas las validaciones pasaron")
    return resultado

def simular_usuario_psmf():
    """Simula un usuario candidato para PSMF."""
    print("\n" + "=" * 70)
    print("SIMULACIÓN: Usuario PSMF - Mujer 35 años, 90kg, 45% grasa")
    print("=" * 70)
    
    # Datos del usuario
    peso = 90.0
    grasa_corregida = 45.0
    mlg = peso * (1 - grasa_corregida / 100)  # 49.5 kg
    tmb = 370 + (21.6 * mlg)
    sexo = "Mujer"
    nivel_entrenamiento = "principiante"
    geaf = 1.0  # Sedentario
    eta = 1.1
    gee_prom_dia = 50
    
    print(f"\nDatos de entrada:")
    print(f"  Peso: {peso} kg")
    print(f"  Grasa corregida: {grasa_corregida}%")
    print(f"  MLG: {mlg:.1f} kg")
    print(f"  TMB: {tmb:.0f} kcal")
    
    resultado = calcular_macros_alternativos(
        peso=peso,
        grasa_corregida=grasa_corregida,
        mlg=mlg,
        tmb=tmb,
        sexo=sexo,
        nivel_entrenamiento=nivel_entrenamiento,
        geaf=geaf,
        eta=eta,
        gee_prom_dia=gee_prom_dia
    )
    
    print(f"\n🔬 Resultados del análisis MUPAI avanzado:")
    print(f"  📊 Clasificación: {resultado['clasificacion']}")
    print(f"  🎯 Fase recomendada: {resultado['fase']}")
    print(f"  ⚠️ PSMF aplicable: {resultado['psmf_aplica']}")
    print(f"  ⚡ TDEE: {resultado['tdee_mantenimiento']:.0f} kcal/día")
    print(f"  🍽️ Calorías: {resultado['calorias_objetivo']:.0f} kcal/día")
    print(f"  📉 Déficit: {abs(resultado['porcentaje_energia']):.0f}%")
    print(f"\n  Macronutrientes PSMF:")
    print(f"    Proteína: {resultado['proteina_g']:.1f}g ({resultado['proteina_kcal']:.0f} kcal)")
    print(f"    Grasa: {resultado['grasa_g']:.1f}g ({resultado['grasa_kcal']:.0f} kcal)")
    print(f"    Carbohidratos: {resultado['carbohidratos_g']:.1f}g ({resultado['carbohidratos_kcal']:.0f} kcal)")
    
    # Validaciones
    assert "PSMF" in resultado['fase'], "Debe ser PSMF"
    assert resultado['psmf_aplica'] == True, "PSMF debe aplicar"
    assert resultado['carbohidratos_g'] <= 50, "Carbs deben ser muy bajos en PSMF"
    assert resultado['calorias_objetivo'] < 1000, "PSMF debe ser muy restrictivo"
    
    print(f"\n✅ Todas las validaciones pasaron")
    return resultado

def simular_usuario_superavit():
    """Simula un atleta magro que necesita superávit."""
    print("\n" + "=" * 70)
    print("SIMULACIÓN: Atleta magro - Hombre 25 años, 75kg, 8% grasa")
    print("=" * 70)
    
    peso = 75.0
    grasa_corregida = 8.0
    mlg = peso * (1 - grasa_corregida / 100)
    tmb = 370 + (21.6 * mlg)
    sexo = "Hombre"
    nivel_entrenamiento = "avanzado"
    geaf = 1.45  # Muy activo
    eta = 1.15   # ETA alto (magro)
    gee_prom_dia = 250
    
    print(f"\nDatos de entrada:")
    print(f"  Peso: {peso} kg")
    print(f"  Grasa corregida: {grasa_corregida}%")
    print(f"  MLG: {mlg:.1f} kg")
    print(f"  Nivel: {nivel_entrenamiento}")
    
    resultado = calcular_macros_alternativos(
        peso=peso,
        grasa_corregida=grasa_corregida,
        mlg=mlg,
        tmb=tmb,
        sexo=sexo,
        nivel_entrenamiento=nivel_entrenamiento,
        geaf=geaf,
        eta=eta,
        gee_prom_dia=gee_prom_dia
    )
    
    print(f"\n🔬 Resultados del análisis MUPAI avanzado:")
    print(f"  📊 Clasificación: {resultado['clasificacion']}")
    print(f"  🎯 Fase recomendada: {resultado['fase']}")
    print(f"  ⚡ TDEE: {resultado['tdee_mantenimiento']:.0f} kcal/día")
    print(f"  🍽️ Calorías: {resultado['calorias_objetivo']:.0f} kcal/día")
    print(f"  📈 Superávit: +{resultado['porcentaje_energia']:.1f}%")
    print(f"\n  Macronutrientes:")
    print(f"    Proteína: {resultado['proteina_g']:.1f}g")
    print(f"    Grasa: {resultado['grasa_g']:.1f}g")
    print(f"    Carbohidratos: {resultado['carbohidratos_g']:.1f}g")
    
    # Validaciones
    assert resultado['clasificacion'] == "Atlético", "Clasificación incorrecta"
    assert "Superávit" in resultado['fase'], "Debe recomendar superávit"
    assert resultado['porcentaje_energia'] > 0, "Porcentaje debe ser positivo en superávit"
    assert resultado['calorias_objetivo'] > resultado['tdee_mantenimiento'], "Calorías deben ser mayores en superávit"
    
    print(f"\n✅ Todas las validaciones pasaron")
    return resultado

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST DE INTEGRACIÓN: calcular_macros_alternativos")
    print("=" * 70)
    
    try:
        # Test 1: Usuario promedio con déficit
        r1 = simular_usuario_completo()
        
        # Test 2: Usuario con alta grasa (PSMF)
        r2 = simular_usuario_psmf()
        
        # Test 3: Atleta magro (superávit)
        r3 = simular_usuario_superavit()
        
        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        print("=" * 70)
        print("\nResumen:")
        print(f"  - Usuario promedio: {r1['fase']} ({r1['calorias_objetivo']:.0f} kcal)")
        print(f"  - Usuario PSMF: {r2['fase']} ({r2['calorias_objetivo']:.0f} kcal)")
        print(f"  - Atleta magro: {r3['fase']} ({r3['calorias_objetivo']:.0f} kcal)")
        
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR EN INTEGRACIÓN: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)

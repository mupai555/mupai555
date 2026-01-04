"""
Script de prueba para validar datos de Erick en la interfaz
Usamos datos del CALCULO_CORRECTO_ERICK.py
"""

# Datos de Erick (de CALCULO_CORRECTO_ERICK.py)
erick_data = {
    "nombre": "Erick",
    "edad": 35,  # Estimado
    "sexo": "Hombre",
    "peso": 82.5,
    "estatura": 177,  # Estimado (IMC ~26.4)
    "grasa_corporal": 26.4,
    "bf_de": 25.0,  # Diferencia estimada
    "mlg_esperada": 60.7,
    "circunferencia_cintura": 100,  # Estimado
    "nivel_entrenamiento": "Intermedio",
    "dias_fuerza": 4,
    "kcal_sesion": 300,
    "calidad_suenyo": 5,  # 5-5.9 horas
    "nivel_estres": 6,
    "ir_se": 64.3,
    "peso_antes": 82.5,
    "email": "erick@example.com",
    "telefono": "123456789"
}

# Valores esperados del cálculo:
expected = {
    "kcal_cut": 1687,  # 2410 × (1 - 0.30)
    "protein_g": 151.8,  # 60.7 × 2.5
    "fat_g": 56.2,  # ~30% de kcal
    "carb_g": 143.4,  # Residual
    "ciclaje_low_kcal": 1350,  # 0.8 × 1687
    "ciclaje_high_kcal": 2136,  # (7×1687 - 4×1350) / 3
    "deficit_pct": 30,  # Capeado por guardrails
}

print("=" * 80)
print("DATOS DE PRUEBA - ERICK")
print("=" * 80)
print("\nDatos del usuario:")
for key, value in erick_data.items():
    print(f"  {key:30s}: {value}")

print("\n\nValores esperados:")
for key, value in expected.items():
    print(f"  {key:30s}: {value}")

print("\n" + "=" * 80)
print("Para testear en la interfaz, ingresa estos datos en el formulario")
print("=" * 80)
print(f"""
1. Sección Personal:
   - Nombre: {erick_data['nombre']}
   - Edad: {erick_data['edad']}
   - Sexo: {erick_data['sexo']}
   - Email: {erick_data['email']}
   - Teléfono: {erick_data['telefono']}

2. Composición Corporal:
   - Peso: {erick_data['peso']} kg
   - Estatura: {erick_data['estatura']} cm
   - % Grasa: {erick_data['grasa_corporal']}%
   - BF Diferencial: {erick_data['bf_de']}%

3. Entrenamiento:
   - Nivel: {erick_data['nivel_entrenamiento']}
   - Días Fuerza: {erick_data['dias_fuerza']}
   - Kcal/Sesión: {erick_data['kcal_sesion']}

4. Recuperación:
   - Calidad Sueño: {erick_data['calidad_suenyo']} (5-5.9 horas)
   - Nivel Estrés: {erick_data['nivel_estres']} (medio)

5. Medidas:
   - Circunferencia Cintura: {erick_data['circunferencia_cintura']} cm

ESPERADO EN EMAIL:
   ✓ CUT: {expected['kcal_cut']} kcal
   ✓ Proteína: {expected['protein_g']}g
   ✓ Grasas: {expected['fat_g']}g
   ✓ Carbos: {expected['carb_g']}g
   ✓ Ciclaje LOW: {expected['ciclaje_low_kcal']} kcal
   ✓ Ciclaje HIGH: {expected['ciclaje_high_kcal']} kcal
   ✓ Déficit: {expected['deficit_pct']}%
""")

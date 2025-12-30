# Módulo de Fases Nutricionales - Documentación

## Descripción General

El módulo `nutrition_phases.py` implementa todas las reglas de fases nutricionales (Definición, Mantenimiento, Volumen y PSMF) de manera modular y desacoplada de la interfaz de usuario de Streamlit.

**Propósito:** Generar cálculos y estructuras detalladas para enviar reportes por correo, sin exponer estos detalles explícitamente en la interfaz.

## Características Principales

### 1. Decisión de Fase Nutricional

El módulo decide automáticamente la fase nutricional óptima basándose en:

- **Sexo** (`sex`): `'male'` / `'female'` (también acepta `'Hombre'` / `'Mujer'`)
- **Porcentaje de grasa corporal** (`bf_percent`): valor float
- **Nivel de entrenamiento** (`training_level`): `'novato'`, `'intermedio'`, `'avanzado'`, `'élite'`
- **Objetivo** (`goal`): `'fat_loss'`, `'muscle_gain'`, `'recomp'`, `'performance'`

**Fases posibles:**
- `'cut'` - Definición (déficit calórico)
- `'maintain'` - Mantenimiento
- `'bulk'` - Volumen (superávit calórico)
- `'psmf'` - Protein Sparing Modified Fast (déficit agresivo)

### 2. Cálculo de Calorías Objetivo

Calcula las calorías objetivo basadas en:
- Calorías de mantenimiento (TMB × GEAF × ETA + GEE)
- Fase nutricional decidida
- Porcentaje de déficit o superávit

**Fórmulas:**
- Definición: `kcal = mantenimiento × (1 - déficit%/100)`
- Mantenimiento: `kcal = mantenimiento`
- Volumen: `kcal = mantenimiento × (1 + superávit%/100)`

### 3. Proyecciones de Peso

Genera proyecciones de 4-5 semanas con tres escenarios:
- **Conservador** (low): Tasa baja de cambio
- **Medio** (mid): Tasa recomendada
- **Agresivo** (high): Tasa alta de cambio

**Tasas de cambio:**

**En Definición (cut):**
- Basadas en % de grasa corporal
- Rango: -0.3% a -2.0% del peso corporal por semana
- Más grasa = mayor tasa de pérdida segura

**En Volumen (bulk):**
- Basadas en nivel de entrenamiento
- Novatos: 0.2% - 0.5% por semana
- Intermedios: 0.15% - 0.4% por semana
- Avanzados: 0.1% - 0.25% por semana (más cualitativo)

**En Mantenimiento:**
- Fluctuaciones mínimas: ±0.1%

## Funciones Principales

### `decidir_fase_nutricional(sex, bf_percent, training_level, goal=None)`

Decide la fase nutricional óptima.

**Ejemplo:**
```python
import nutrition_phases as np

resultado = np.decidir_fase_nutricional(
    sex='male',
    bf_percent=20.0,
    training_level='intermedio',
    goal='fat_loss'
)

print(resultado['phase'])  # 'cut' o 'psmf'
print(resultado['percentage'])  # -15.0 o -30.0
print(resultado['reasoning'])  # Explicación detallada
```

**Retorna:**
```python
{
    'phase': 'cut',  # 'cut', 'maintain', 'bulk', o 'psmf'
    'phase_name_es': 'Definición (Déficit)',
    'percentage': -15.0,
    'reasoning': 'Grasa corporal elevada...',
    'is_psmf_candidate': False,
    'bf_percent': 20.0,
    'sex': 'male',
    'training_level': 'intermedio',
    'goal': 'fat_loss'
}
```

### `calcular_calorias_objetivo(maintenance_calories, phase_info)`

Calcula las calorías objetivo basadas en el mantenimiento y la fase.

**Ejemplo:**
```python
phase = np.decidir_fase_nutricional('male', 20.0, 'intermedio', 'fat_loss')
calorias = np.calcular_calorias_objetivo(2500, phase)

print(calorias['target_calories'])  # 2125.0
print(calorias['deficit_kcal'])  # 375
```

**Retorna:**
```python
{
    'target_calories': 2125.0,
    'maintenance_calories': 2500.0,
    'percentage': -15.0,
    'phase': 'cut',
    'deficit_percentage': 15.0,  # Solo para cut/psmf
    'deficit_kcal': 375.0
}
```

### `generar_proyecciones(phase_info, current_weight, weeks=4)`

Genera proyecciones de peso para 4-5 semanas.

**Ejemplo:**
```python
phase = np.decidir_fase_nutricional('male', 20.0, 'intermedio', 'fat_loss')
proyecciones = np.generar_proyecciones(phase, 80.0, weeks=4)

print(proyecciones['weekly_rate_mid'])  # -1.0%
print(proyecciones['weights_mid'])  # [80.0, 79.2, 78.4, 77.6, 76.8]
print(proyecciones['total_change_mid'])  # -3.2 kg
```

**Retorna:**
```python
{
    'weekly_rate_low': -0.7,
    'weekly_rate_mid': -1.0,
    'weekly_rate_high': -1.5,
    'weekly_kg_low': -0.56,
    'weekly_kg_mid': -0.8,
    'weekly_kg_high': -1.2,
    'weights_low': [80.0, 79.44, 78.88, 78.32, 77.76],
    'weights_mid': [80.0, 79.2, 78.4, 77.6, 76.8],
    'weights_high': [80.0, 78.8, 77.6, 76.4, 75.2],
    'total_change_low': -2.24,
    'total_change_mid': -3.2,
    'total_change_high': -4.8,
    'explanation': 'En rango óptimo. Pérdida conservadora...',
    'weeks': 4
}
```

### `generar_analisis_completo(...)`

**Función de más alto nivel** que orquesta todo el análisis.

**Ejemplo:**
```python
analisis = np.generar_analisis_completo(
    sex='male',
    bf_percent=20.0,
    training_level='intermedio',
    goal='fat_loss',
    maintenance_calories=2500,
    current_weight=80.0,
    weeks=4
)

print(analisis['phase_decision']['phase'])  # 'cut' o 'psmf'
print(analisis['calories']['target_calories'])  # 2125.0
print(analisis['projections']['total_change_mid'])  # -3.2
print(analisis['summary'])  # Resumen ejecutivo completo
```

**Retorna:**
```python
{
    'phase_decision': {...},  # Resultado de decidir_fase_nutricional
    'calories': {...},  # Resultado de calcular_calorias_objetivo
    'projections': {...},  # Resultado de generar_proyecciones
    'summary': '...',  # Resumen ejecutivo en texto
    'metadata': {...}  # Metadatos del análisis
}
```

### `formatear_para_email(analisis_completo)`

Formatea el análisis completo para incluir en el cuerpo del email.

**Ejemplo:**
```python
analisis = np.generar_analisis_completo(...)
texto_email = np.formatear_para_email(analisis)

# Incluir texto_email en el cuerpo del correo
contenido_email = base_email + texto_email
enviar_email(contenido_email)
```

## Integración en streamlit_app.py

El módulo está integrado de la siguiente manera:

1. **Importación** (línea ~15):
   ```python
   import nutrition_phases
   ```

2. **Generación del análisis** (después del cálculo de macros):
   ```python
   analisis_fases_nutricionales = nutrition_phases.generar_analisis_completo(
       sex=sexo,
       bf_percent=grasa_corregida,
       training_level=nivel_entrenamiento,
       goal=objetivo_fase,
       maintenance_calories=GE,
       current_weight=peso,
       weeks=4
   )
   
   texto_fases_nutricionales = nutrition_phases.formatear_para_email(
       analisis_fases_nutricionales
   )
   ```

3. **Inclusión en el email** (al final de `tabla_resumen`):
   ```python
   tabla_resumen += texto_fases_nutricionales
   ```

**Importante:** El análisis NO se muestra en la interfaz de usuario (USER_VIEW = False). Solo se incluye en el reporte enviado por correo.

## Tests

### Tests Unitarios (`test_nutrition_phases.py`)

Incluye 15 tests que verifican:
1. Decisión de fase CUT
2. Decisión de fase BULK
3. Decisión de fase MAINTAIN
4. Decisión de fase PSMF
5. Cálculo de calorías con déficit
6. Cálculo de calorías con superávit
7. Proyecciones para definición
8. Proyecciones para volumen
9. Casos extremos - BF muy bajo
10. Casos extremos - BF muy alto
11. Diferencias entre sexos
12. Diferencias por nivel de entrenamiento
13. Análisis completo integrado
14. Formateo para email
15. Normalización de entradas

**Ejecutar tests:**
```bash
python test_nutrition_phases.py
```

### Tests de Integración (`test_integration_nutrition_phases.py`)

Verifica:
1. Importación correcta en streamlit_app.py
2. Generación del análisis en el flujo
3. Inclusión en el email
4. Funcionalidad con datos típicos
5. USER_VIEW permanece False
6. Manejo de errores
7. Mapeo de variables
8. Sin cambios visibles en UI
9. Construcción correcta de tabla_resumen
10. Documentación apropiada

**Ejecutar tests de integración:**
```bash
python test_integration_nutrition_phases.py
```

## Criterios de Decisión de Fase

### PSMF (Protein Sparing Modified Fast)
- **Criterios:**
  - Hombres: >18% grasa corporal + objetivo `fat_loss`
  - Mujeres: >23% grasa corporal + objetivo `fat_loss`
- **Déficit:** 30% agresivo
- **Propósito:** Pérdida rápida preservando músculo

### CUT (Definición)
- **Criterios:**
  - Grasa corporal elevada (>18% hombres, >23% mujeres)
  - O en rango óptimo con objetivo `fat_loss`
- **Déficit:** 10-30% según nivel de grasa
- **Propósito:** Pérdida sostenible de grasa

### MAINTAIN (Mantenimiento)
- **Criterios:**
  - Rango óptimo sin objetivo específico
  - O objetivo `recomp` / `performance`
- **Porcentaje:** 0-2.5% (ligero superávit para recomp)
- **Propósito:** Recomposición corporal

### BULK (Volumen)
- **Criterios:**
  - Grasa corporal baja (<10% hombres, <16% mujeres)
  - O rango óptimo con objetivo `muscle_gain`
- **Superávit:** 5-12.5% según nivel de grasa
- **Propósito:** Ganancia muscular controlada

## Compatibilidad

- ✅ Compatible con Python 3.6+
- ✅ Sin dependencias externas (solo biblioteca estándar)
- ✅ Desacoplado de Streamlit
- ✅ Compatible con el flujo existente de streamlit_app.py
- ✅ Manejo de errores robusto
- ✅ Normalización automática de entradas

## Ejemplo de Salida en Email

```
=====================================
ANÁLISIS DE FASE NUTRICIONAL
=====================================
Módulo: Nutrition Phases v1.0
Generado por: MUPAI System

📊 FASE NUTRICIONAL ASIGNADA:
-------------------------------------
Fase: Definición (Déficit Moderado)
Tipo técnico: CUT
Porcentaje: -15.0%

📝 JUSTIFICACIÓN:
Grasa corporal elevada (20.0%). Déficit calórico para reducir 
grasa y mejorar salud metabólica.

🔥 CALORÍAS OBJETIVO:
-------------------------------------
- Mantenimiento (TMB × GEAF × ETA + GEE): 2500 kcal/día
- Objetivo nutricional: 2125 kcal/día
- Diferencia: -375 kcal/día
- Déficit aplicado: 15.0% (375 kcal)

📈 PROYECCIONES DE PESO (4 SEMANAS):
-------------------------------------
Peso inicial: 80.0 kg

ESCENARIO CONSERVADOR:
  • Tasa semanal: -0.7% (-0.56 kg/semana)
  • Peso final: 77.8 kg
  • Cambio total: -2.2 kg

ESCENARIO MEDIO (RECOMENDADO):
  • Tasa semanal: -1.0% (-0.80 kg/semana)
  • Peso final: 76.8 kg
  • Cambio total: -3.2 kg

ESCENARIO AGRESIVO:
  • Tasa semanal: -1.5% (-1.20 kg/semana)
  • Peso final: 75.2 kg
  • Cambio total: -4.8 kg

📊 PROGRESIÓN SEMANAL (ESCENARIO MEDIO):
  Semana 0 (inicial): 80.0 kg
  Semana 1: 79.2 kg (-0.8 kg)
  Semana 2: 78.4 kg (-0.8 kg)
  Semana 3: 77.6 kg (-0.8 kg)
  Semana 4: 76.8 kg (-0.8 kg)

💡 INTERPRETACIÓN:
-------------------------------------
Grasa elevada. Pérdida moderada es segura y efectiva.

⚠️ NOTAS IMPORTANTES:
-------------------------------------
• Las proyecciones son estimaciones basadas en datos científicos
• Se recomienda seguimiento cada 1-2 semanas
• Mantener ingesta de proteína alta durante déficit
• Hidratación adecuada (35-40 ml/kg/día) es crucial
```

## Notas de Desarrollo

### Principios de Diseño

1. **Modularidad:** Funciones independientes y reutilizables
2. **Desacoplamiento:** No depende de Streamlit ni de la UI
3. **Robustez:** Manejo de errores y normalización de entradas
4. **Documentación:** Docstrings detallados en todas las funciones
5. **Testing:** Cobertura completa con tests unitarios e integración
6. **Transparencia:** No afecta la UI del usuario final

### Limitaciones Conocidas

- Las proyecciones son estimaciones teóricas
- No considera factores individuales como adaptación metabólica
- Casos avanzados se tratan de forma más cualitativa
- Requiere datos precisos de entrada para mejores resultados

### Futuras Mejoras Posibles

- [ ] Agregar proyecciones a más largo plazo (12 semanas)
- [ ] Incluir gráficos de progreso proyectado
- [ ] Considerar historial de peso del usuario
- [ ] Ajustes dinámicos basados en tasa de progreso real
- [ ] Integración con fotos de progreso

## Soporte

Para preguntas o problemas:
1. Revisar la documentación completa en este archivo
2. Ejecutar los tests para verificar funcionamiento
3. Consultar los ejemplos en `nutrition_phases.py` (sección `if __name__ == "__main__"`)

## Licencia

© 2025 MUPAI - Muscle Up GYM
Digital Training Science

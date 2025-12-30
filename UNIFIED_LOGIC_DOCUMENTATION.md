# MUPAI - Unified Macro Distribution Logic

## Overview

This document describes the unified advanced logic implemented in `streamlit_app.py` for comprehensive macro and micronutrient calculation. The implementation follows the requirements for a complete nutrition assessment system integrating multiple calculation methodologies.

## Implementation Date
2025-12-30

## Core Principle

**All unified calculations are HIDDEN from the user interface** (respecting `USER_VIEW = False` flag) but **ALWAYS INCLUDED in administrative email reports** (`enviar_email_parte2`).

## Calculation Flow

The unified system follows this calculation path:

```
TMB (Katch-McArdle) → GEAF → GET → ETA → GEE → FBEO
         ↓
   Phase Selection (Deficit/Maintenance/Surplus/PSMF)
         ↓
   Caloric Intake Calculation
         ↓
   Dynamic Protein Calculation
         ↓
   Weekly Cycling 4-3
         ↓
   Micronutrient Assessment
```

## New Functions Implemented

### 1. Energy Expenditure Calculations

#### `calcular_gasto_energetico_total(tmb, geaf)`
Calculates total energy expenditure (GET).
- **Formula:** GET = TMB × GEAF
- **Input:** TMB (kcal/day), GEAF factor (1.00-1.45)
- **Output:** GET in kcal/day

#### `calcular_eta(ingesta_calorica)`
Calculates Thermal Effect of Food (ETA).
- **Formula:** ETA = Intake × 0.10
- **Input:** Caloric intake (kcal/day)
- **Output:** ETA in kcal/day (10% of intake)

#### `calcular_gee(nivel_entrenamiento, peso)`
Calculates Exercise Energy Expenditure (GEE).
- **Base values:**
  - Sedentario: 0 kcal/day
  - Moderadamente-activo: 150 kcal/day
  - Activo: 300 kcal/day
  - Muy-activo: 500 kcal/day
- **Adjustment:** Scaled by weight (70kg reference)
- **Input:** Activity level, body weight (kg)
- **Output:** GEE in kcal/day

#### `calcular_fbeo(gee)`
Calculates post-exercise oxygen consumption (FBEO/EPOC).
- **Formula:** FBEO = GEE × 0.10
- **Input:** GEE (kcal/day)
- **Output:** FBEO in kcal/day (10% of GEE)

### 2. Nutritional Phase Determination

#### `determinar_fase_nutricional_unificada(sexo, grasa_corregida, objetivo_usuario=None)`
Determines nutritional phase based on body composition.

**Returns:**
- `fase`: Phase name
- `deficit_superavit_pct`: Percentage adjustment (-deficit, +surplus, 0=maintenance)
- `rango_min`, `rango_max`: Percentage range
- `descripcion`: Phase description

**Phase Categories (Men):**
- >35% BF: PSMF / Very High Deficit (-40 to -50%)
- >25% BF: High Deficit (-25 to -35%)
- >18% BF: Moderate Deficit (-15 to -25%)
- >15% BF: Maintenance / Light Deficit (-15 to 0%)
- >10% BF: Maintenance / Light Surplus (0 to 10%)
- ≤10% BF: Moderate Surplus (10 to 20%)

**Phase Categories (Women):**
- >45% BF: PSMF / Very High Deficit (-40 to -50%)
- >35% BF: High Deficit (-25 to -35%)
- >28% BF: Moderate Deficit (-15 to -25%)
- >23% BF: Maintenance / Light Deficit (-15 to 0%)
- >18% BF: Maintenance / Light Surplus (0 to 10%)
- ≤18% BF: Moderate Surplus (10 to 20%)

#### `calcular_rangos_deficit_superavit(sexo, grasa_corregida)`
Calculates concrete deficit/surplus ranges by body composition category.

**Returns:**
- `categoria`: Body composition category
- `grasa_corporal`: BF percentage
- `deficit_recomendado`: Recommended deficit range
- `superavit_recomendado`: Recommended surplus range
- `notas`: Recommendations

**Categories:** Obesidad Alta, Sobrepeso, Fitness, Atlético, Muy Definido, Competición

### 3. Dynamic Protein Calculation

#### `calcular_proteina_dinamica(sexo, grasa_corregida, peso, mlg, modo="auto")`
Calculates protein with dynamic base selection.

**Modes:**
- `"auto"`: Automatic selection using 35/42 rule
  - Men ≥35% BF → Use MLG
  - Women ≥42% BF → Use MLG
  - Otherwise → Use total weight
- `"peso_total"`: Always use total body weight
- `"mlg"`: Always use lean mass (MLG)
- `"peso_ajustado"`: Use adjusted weight = MLG + (Fat Mass × 0.25)

**Protein Factors:**
- ≥35% BF: 1.6 g/kg
- 25-34.9% BF: 1.8 g/kg
- 15-24.9% BF: 2.0 g/kg
- <15% BF: 2.2 g/kg

**Returns:**
- `base_utilizada`: Base used for calculation
- `valor_base_kg`: Base value in kg
- `factor_proteina`: Factor applied (g/kg)
- `proteina_g_dia`: Protein in grams per day
- `modo_aplicado`: Mode that was applied

### 4. Extended PSMF Calculator

#### `calcular_psmf_extendida(sexo, peso, grasa_corregida, mlg, estatura_cm, objetivo_dias=None)`
Extended PSMF calculator with energy allocation tiers.

**Features:**
- Weekly tier allocation (Phase 1-3)
- Projected weight loss by weeks
- Duration recommendations based on tier
- Caloric adjustments per phase
- Transition preparation

**Tier System:**
- **Tier 1:** Low adiposity (base = total weight)
- **Tier 2:** Moderate adiposity (base = MLG)
- **Tier 3:** High adiposity (base = ideal weight at BMI 25)

**Duration Guidelines:**
- Tier 3: 12 weeks recommended (42-90 days)
- Tier 2: 8 weeks recommended (28-60 days)
- Tier 1: 4 weeks recommended (14-35 days)

**Returns:**
- All fields from `calculate_psmf()` plus:
- `psmf_extendida`: True
- `duracion_recomendada_semanas`: Recommended weeks
- `perdida_total_proyectada_kg`: Total projected loss
- `peso_proyectado_final_kg`: Final projected weight
- `tramos_semanales`: Array of weekly tiers with:
  - Week number
  - Phase (Adaptación inicial, Pérdida sostenida, Transición preparatoria)
  - Calories per day
  - Start/end weight
  - Estimated loss

### 5. Weekly Calorie Cycling

#### `calcular_ciclado_semanal(tmb, geaf, deficit_superavit_pct, dias_bajos=4, dias_altos=3)`
Implements 4-3 weekly calorie cycling (low/high energy days).

**Pattern:**
- 4 low-calorie days (base deficit/surplus)
- 3 high-calorie days (refeed - 10-15% increase)

**For Deficit:**
- Low days: Maintain base deficit
- High days: +10% increase (conservative refeed)

**For Surplus/Maintenance:**
- Low days: Maintain base level
- High days: +15% increase

**Returns:**
- `get_base`: Base total energy expenditure
- `calorias_dia_bajo`: Calories on low days
- `calorias_dia_alto`: Calories on high days
- `promedio_semanal`: Weekly average calories
- `distribucion_semanal`: Array of 7 days with:
  - Day name
  - Type (Bajo/Alto)
  - Calories
  - Description

**Suggested Distribution:**
- Low days: Monday-Thursday
- High days: Friday-Sunday
- Recommend high days coincide with intense training

### 6. Micronutrition Assessment

#### `evaluar_micronutrientes_checklist()`
Checklist-based micronutrient evaluation (current implementation).

**Returns:**
- `modo`: 'checklist'
- `micronutrientes`: Array of 7 essential micronutrients:
  - Vitamin D (1000-4000 IU/day)
  - Vitamin B12 (2.4 μg/day)
  - Iron (8-18 mg/day)
  - Calcium (1000-1200 mg/day)
  - Magnesium (310-420 mg/day)
  - Zinc (8-11 mg/day)
  - Omega-3 (250-500 mg EPA+DHA/day)
- `recomendaciones_generales`: General recommendations

#### `evaluar_micronutrientes_numerico(ingesta_calorica, macros)`
Numeric micronutrient evaluation (future implementation).

**Status:** Prepared for future integration with nutritional database.

**Returns:**
- `modo`: 'numerico'
- `estado`: 'no_implementado'
- Ready for quantitative analysis when database is available

### 7. Unified Report Generator

#### `generar_reporte_unificado_mupai(sexo, edad, peso, estatura_cm, grasa_corregida, mlg, nivel_entrenamiento, objetivo_usuario=None)`
Generates complete unified MUPAI report integrating all calculations.

**Integrates:**
1. Energy expenditures (TMB, GEAF, GET, ETA, GEE, FBEO)
2. Nutritional phase
3. Recommended intake
4. Composition ranges
5. Dynamic protein
6. Extended PSMF (if applicable)
7. Weekly cycling
8. Micronutrients

**Returns:** Complete dictionary with all calculations and recommendations.

## Email Integration

### Modified Function: `enviar_email_parte2()`

**New parameter:** `nivel_entrenamiento` (optional)

**New sections added:**

1. **"MUPAI - Distribución de calorías, macros y micros"**
   - Energy expenditures breakdown
   - Nutritional phase recommendation
   - Recommended caloric intake
   - Dynamic protein calculation
   - Weekly cycling 4-3
   - Micronutrition checklist

2. **"Calculadora PSMF Extendida"** (when applicable)
   - PSMF protocol details
   - Daily macros
   - Temporal projection
   - Weekly tiers with weight projections
   - Recommendations

**Error Handling:**
If unified report generation fails, includes error message but continues with traditional baseline report.

## Usage in Code

### Calling the unified report:

```python
reporte_unificado = generar_reporte_unificado_mupai(
    sexo="Hombre",
    edad=30,
    peso=85,
    estatura_cm=175,
    grasa_corregida=20.0,
    mlg=68,
    nivel_entrenamiento="Activo"
)

# Access components:
print(reporte_unificado['gastos_energeticos']['get_kcal_dia'])
print(reporte_unificado['fase_nutricional']['fase'])
print(reporte_unificado['proteina']['proteina_g_dia'])
```

### Email integration:

```python
ok_parte2 = enviar_email_parte2(
    nombre, fecha, edad, sexo, peso, estatura,
    imc, grasa_corregida, masa_muscular, grasa_visceral, mlg, tmb,
    progress_photos,
    nivel_entrenamiento=nivel_actividad_text  # NEW PARAMETER
)
```

## UI Visibility

**Important:** All unified calculations respect the `USER_VIEW` and `SHOW_TECH_DETAILS` flags:

- `USER_VIEW = False` (default): Calculations hidden from UI
- `SHOW_TECH_DETAILS = False` (default): Technical details hidden from UI
- Email reports: **ALWAYS include full details** regardless of flags

This ensures:
1. Clean user experience (no overwhelming technical data)
2. Complete professional reports for administrators
3. Proprietary methodology protection

## Debug and Audit

All functions include comprehensive docstrings and can be tested independently:

```python
# Test energy calculations
get = calcular_gasto_energetico_total(1800, 1.25)
eta = calcular_eta(2000)
gee = calcular_gee("Activo", 75)
fbeo = calcular_fbeo(gee)

# Test phase determination
fase = determinar_fase_nutricional_unificada("Hombre", 20.0)
print(fase['fase'], fase['deficit_superavit_pct'])

# Test protein calculation
proteina = calcular_proteina_dinamica("Hombre", 20.0, 80, 70, modo="auto")
print(proteina['proteina_g_dia'], proteina['base_utilizada'])
```

## Testing

Comprehensive standalone tests available in `test_unified_logic_standalone.py`:
- All calculation functions validated
- Edge cases covered
- Logic verified for all paths

Run tests:
```bash
python3 test_unified_logic_standalone.py
```

## Future Enhancements

1. **Numeric Micronutrient Mode:**
   - Integration with nutritional database
   - Quantitative micronutrient analysis
   - Food-specific recommendations

2. **Advanced PSMF Protocols:**
   - Category-specific refeeds
   - Metabolic adaptations
   - Reverse dieting protocols

3. **Machine Learning Integration:**
   - Personalized response prediction
   - Adaptive cycling patterns
   - Outcome optimization

4. **Real-time Adjustments:**
   - Progress tracking integration
   - Auto-adjustment based on results
   - Adherence scoring

## References

### Scientific Basis:
- Katch-McArdle BMR equation
- GEAF standardization (Institute of Medicine)
- Thermic effect of food (Westerterp, 2004)
- EPOC research (Børsheim & Bahr, 2003)
- PSMF protocols (Blackburn, 1977; McDonald, 2005)
- Protein requirements (Phillips & Van Loon, 2011)
- Calorie cycling (Davoodi et al., 2014)

### Implementation Standards:
- Modular design principles
- Single Responsibility Principle
- DRY (Don't Repeat Yourself)
- Comprehensive error handling
- Full documentation

## Support

For questions or issues with the unified logic:
1. Check function docstrings in `streamlit_app.py`
2. Review test cases in `test_unified_logic_standalone.py`
3. Consult this documentation

## Version History

- **v1.0 (2025-12-30):** Initial implementation
  - All core functions implemented
  - Email integration complete
  - Testing suite added
  - Documentation created

# MUPAI Advanced Macros Implementation

## Overview

This implementation adds an advanced macro calculation system to MUPAI that provides an alternative analysis method based on the audited MUPAI methodology for Phases, Energy, and Macros.

## Key Features

### 1. Advanced Classification System
- **Body Fat Categories**: Preparación, Atlético, Fitness, Promedio, Alto
- **Sex-Specific Ranges**: Different thresholds for men and women
- **Scientific Basis**: Based on validated body composition research

### 2. Automated Phase Selection
The system automatically determines the optimal nutritional phase:
- **Surplus** (10-15%): For very lean individuals (competition prep recovery)
- **Moderate Surplus** (5-10%): For athletic individuals looking to build
- **Maintenance** (0%): For optimal body composition
- **Deficit** (variable): Based on body fat percentage and goals
- **PSMF** (35-40%): For high body fat percentages requiring aggressive fat loss

### 3. TDEE Maintenance Calculation
```
TDEE = TMB × GEAF × ETA + GEE_daily
```
Where:
- TMB: Basal Metabolic Rate (Cunningham formula)
- GEAF: Physical Activity Factor
- ETA: Thermic Effect of Food
- GEE: Exercise Energy Expenditure

### 4. Macronutrient Distribution

#### Traditional Distribution
- **Protein**: Based on body composition (MLG for high adiposity, body weight otherwise)
  - Factor ranges from 1.6-2.2 g/kg depending on body fat %
- **Fat**: Fixed at 25% of TMB
- **Carbohydrates**: Remaining calories after protein and fat

#### PSMF Distribution
- **Protein**: 1.6-1.8 g/kg (based on MLG for very high body fat)
- **Fat**: 30-40g (essential fats only)
- **Carbohydrates**: 30g (fibrous vegetables only)

## Implementation Details

### Function: `calcular_macros_alternativos`

**Location**: `streamlit_app.py` (line ~2165)

**Parameters**:
- `peso`: Body weight in kg
- `grasa_corregida`: DEXA-corrected body fat percentage
- `mlg`: Fat-free mass in kg
- `tmb`: Basal metabolic rate in kcal
- `sexo`: "Hombre" or "Mujer"
- `nivel_entrenamiento`: "principiante", "intermedio", "avanzado", "élite"
- `geaf`: Physical activity factor (1.0-1.45)
- `eta`: Thermic effect factor (1.1-1.15)
- `gee_prom_dia`: Daily average exercise expenditure in kcal

**Returns**: Dictionary with:
- `clasificacion`: Body composition classification
- `fase`: Recommended nutritional phase
- `porcentaje_energia`: Energy adjustment percentage
- `tdee_mantenimiento`: Maintenance TDEE in kcal
- `calorias_objetivo`: Target calories
- `proteina_g`, `grasa_g`, `carbohidratos_g`: Macros in grams
- `proteina_kcal`, `grasa_kcal`, `carbohidratos_kcal`: Macros in kcal
- `psmf_aplica`: Boolean indicating PSMF applicability

### Integration Points

#### 1. Calculation Integration (line ~5304)
Called after traditional macro calculations:
```python
macros_alternativos = calcular_macros_alternativos(
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
st.session_state.macros_alternativos = macros_alternativos
```

#### 2. Administrative Summary (line ~5935)
Results included in email report only (not visible to users):
```python
if 'macros_alternativos' in st.session_state:
    alt = st.session_state.macros_alternativos
    # ... detailed reporting logic
```

## Visibility Controls

**User Interface**: HIDDEN
- The alternative calculations are NOT shown to end users
- UI remains unchanged for user experience

**Administrative Reports**: VISIBLE
- Full analysis included in email reports
- Provides internal team with complete data
- Enables validation and protocol refinement

## Testing

### Unit Tests
**File**: `test_macros_alternativos.py`

Tests cover:
- ✅ Body fat classification (men and women)
- ✅ Phase selection (surplus, deficit, PSMF)
- ✅ TDEE calculation accuracy
- ✅ Macronutrient distribution
- ✅ Invalid input handling

**Run**: `python test_macros_alternativos.py`

### Integration Tests
**File**: `test_integration_macros_alternativos.py`

Scenarios tested:
- ✅ Average user with deficit needs
- ✅ High body fat user (PSMF candidate)
- ✅ Lean athlete (surplus needs)

**Run**: `python test_integration_macros_alternativos.py`

## Benefits

1. **Validation**: Cross-reference with traditional calculations
2. **Research**: Continuous protocol improvement based on alternative methodology
3. **Transparency**: Full data for internal analysis
4. **Flexibility**: Alternative approach ready if needed
5. **Quality**: Audited methodology provides additional confidence

## Usage Example

The function is automatically called during the normal flow. For administrative review:

```python
# Access from session state in email generation
if 'macros_alternativos' in st.session_state:
    alt = st.session_state.macros_alternativos
    print(f"Classification: {alt['clasificacion']}")
    print(f"Phase: {alt['fase']}")
    print(f"TDEE: {alt['tdee_mantenimiento']} kcal")
    print(f"Target: {alt['calorias_objetivo']} kcal")
```

## Maintenance Notes

- Function is self-contained and modular
- No dependencies on UI visibility flags
- Results stored in session_state for later use
- Can be easily extended with new classification ranges
- PSMF logic mirrors existing PSMF implementation

## Future Enhancements

Potential improvements:
- Add training volume adjustment factors
- Include metabolic adaptation considerations
- Personalized macronutrient timing recommendations
- Integration with progress tracking
- A/B testing between methodologies

## References

This implementation is based on the MUPAI audited methodology for:
- Body composition classification
- Energy expenditure calculation
- Macronutrient distribution
- Phase-specific recommendations

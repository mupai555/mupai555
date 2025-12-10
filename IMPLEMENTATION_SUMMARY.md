# Implementation Summary: Auto-Extrapolation Omron & LBM-Based PSMF

## Overview

This implementation adds two critical features for handling high adiposity cases in the MUPAI body composition calculator.

## Feature 1: Auto-Extrapolation for Omron >40%

### Before
- Omron readings >40% were truncated at the table maximum (40% → 45.3% DEXA for men)
- Required manual checkbox activation to enable extrapolation
- No clear warning about reliability for high readings
- Not user-friendly for high adiposity cases

### After
- **Automatic activation:** Readings >40% trigger extrapolation automatically
- **Linear extrapolation:** Uses slope from last two calibration points (39→44.3%, 40→45.3%)
- **Safety cap:** Limited to 60% maximum (configurable via `MAX_EXTRAPOLATE`)
- **Clear UI:** 
  - Checkbox shows as checked and disabled with explanation
  - Warning banner for extrapolated values
  - Special alert for readings >= 45%
- **Transparency:** Both raw Omron and corrected DEXA values displayed

### Technical Implementation

**Constants Added:**
```python
MAX_EXTRAPOLATE = 60.0              # Maximum cap for extrapolation
UMBRAL_ALTA_ADIPOSIDAD = 45.0       # Threshold for high adiposity warning
```

**Function Updated:** `corregir_porcentaje_grasa()`
- Auto-activates extrapolation when `medido > 40` (max_omron)
- Calculates slope: `(45.3 - 44.3) / (40 - 39) = 1.0` (for men)
- Extrapolates: `45.3 + 1.0 * (medido - 40)`
- Caps result at `MAX_EXTRAPOLATE`
- Sets session_state flags: `grasa_extrapolada`, `grasa_extrapolada_valor`, `grasa_extrapolada_medido`, `alta_adiposidad`

**Example Results:**
```
Omron 39% (H) → DEXA 44.3% (interpolation, no extrapolation)
Omron 40% (H) → DEXA 45.3% (table boundary, no extrapolation)
Omron 43% (H) → DEXA 48.3% (extrapolated: 45.3 + 1.0*3)
Omron 58.5% (H) → DEXA 60.0% (extrapolated but capped at MAX_EXTRAPOLATE)
```

## Feature 2: LBM-Based PSMF for High Adiposity

### Before
- All PSMF protein calculations based on total body weight
- For high adiposity: `protein = weight * factor` (1.6 or 1.8 g/kg)
- Could result in excessive protein requirements
- Example: Man 140kg, 38% fat → 224g protein/day

### After
- **Smart switching:** Auto-detects high adiposity and switches to LBM-based calculation
- **Criteria:**
  - Men: Body fat >= 35%
  - Women: Body fat >= 40%
- **Factor:** 1.8 g/kg LBM (configurable via `PROTEIN_FACTOR_PSMF_LBM`)
- **Maintains existing logic** for normal body fat ranges
- Example: Man 140kg, 38% fat (LBM 86.8kg) → 156.2g protein/day

### Technical Implementation

**Constant Added:**
```python
PROTEIN_FACTOR_PSMF_LBM = 1.8       # g/kg LBM for high adiposity cases
```

**Function Updated:** `calculate_psmf()`
```python
# Determine if LBM-based calculation should be used
usar_lbm = False
if (sexo == "Hombre" and grasa_corregida >= 35.0) or \
   (sexo == "Mujer" and grasa_corregida >= 40.0):
    usar_lbm = True
    proteina_g_dia = round(mlg * PROTEIN_FACTOR_PSMF_LBM, 1)
    st.session_state['psmf_lbm_based'] = True
else:
    # Original logic for normal ranges
    if grasa_corregida < 25:
        proteina_g_dia = round(peso * 1.8, 1)
    else:
        proteina_g_dia = round(peso * 1.6, 1)
    st.session_state['psmf_lbm_based'] = False
```

**Example Comparison:**

| Case | Weight | BF% | LBM | Old Method | New Method | Reduction |
|------|--------|-----|-----|------------|------------|-----------|
| Man | 140kg | 38% | 86.8kg | 224.0g/day (1.6 × 140) | 156.2g/day (1.8 × 86.8) | 67.8g (30.2%) |
| Man | 80kg | 25% | 60kg | 128.0g/day (1.6 × 80) | 128.0g/day (1.6 × 80) | None (normal range) |
| Woman | 70kg | 53.86% | 32.3kg | 112.0g/day (1.6 × 70) | 58.1g/day (1.8 × 32.3) | 53.9g (48.1%) |
| Woman | 70kg | 30% | 49kg | 112.0g/day (1.6 × 70) | 112.0g/day (1.6 × 70) | None (normal range) |

## Scientific Rationale

### Extrapolation
While extrapolation is inherently less precise than interpolation within the calibration range, it provides:
1. **More realistic estimates** than truncating at 40%
2. **Clear warnings** about reduced reliability
3. **Transparency** in calculations
4. **User guidance** toward more accurate measurement methods

The 60% cap prevents unrealistic extrapolations while covering the vast majority of real-world cases.

### LBM-Based PSMF
For individuals with very high adiposity:
1. **Adipose tissue has minimal protein requirements** - it's primarily storage
2. **Lean mass drives protein needs** - muscle, organs, connective tissue
3. **Using total weight overestimates** protein requirements significantly
4. **LBM-based calculation**:
   - More physiologically appropriate
   - Prevents excessive protein intake
   - More sustainable for compliance
   - Still preserves muscle mass during aggressive fat loss

The factor of 1.8 g/kg LBM is conservative and appropriate for:
- Preserving lean mass during caloric restriction
- Maximizing satiety
- Supporting metabolic health

## Testing

### Unit Tests Created
File: `tests/test_conversion.py`

**10 comprehensive tests, all passing:**
1. ✓ Interpolation within range (Omron 39%)
2. ✓ Exact table boundary (Omron 40%)
3. ✓ Extrapolation above range (Omron 43%)
4. ✓ Extreme extrapolation with cap (Omron 58.5%)
5. ✓ Female extrapolation (Omron 45%)
6. ✓ Normal PSMF man (25% BF)
7. ✓ LBM-based PSMF man (38% BF)
8. ✓ LBM-based PSMF woman (53.86% BF)
9. ✓ Normal PSMF woman (30% BF)
10. ✓ PSMF not applicable (15% BF)

**Run tests:**
```bash
python tests/test_conversion.py
```

## UI Changes

### Checkbox Behavior
**Before:** Always interactive, requires manual activation
**After:** 
- If reading >40: Checked and disabled with clear explanation
- If reading <=40: Interactive (manual control preserved)

### Warning Messages
1. **High Adiposity Banner** (>= 45%):
   ```
   🚨 ALTA ADIPOSIDAD DETECTADA - Lectura Omron >= 45%
   Se recomienda encarecidamente usar un metodo de medicion mas preciso
   (DEXA o InBody) para estos niveles de grasa corporal.
   Los calculos PSMF se ajustan automaticamente para usar masa libre
   de grasa (LBM) como base.
   ```

2. **Extrapolation Warning** (>40%):
   ```
   ⚠️ Valor EXTRAPOLADO (menos fiable): El valor medido de Omron
   (XX.X%) esta por encima del rango de la tabla de calibracion
   (max 40%). El valor corregido equivalente DEXA (XX.X%) se obtuvo
   mediante EXTRAPOLACION LINEAL, limitada a un maximo de 60%.
   ```

## Files Modified

1. **streamlit_app.py** (main application)
   - Added constants: `MAX_EXTRAPOLATE`, `PROTEIN_FACTOR_PSMF_LBM`, `UMBRAL_ALTA_ADIPOSIDAD`
   - Updated `corregir_porcentaje_grasa()` function
   - Updated `calculate_psmf()` function
   - Modified UI checkbox logic
   - Enhanced warning messages
   - Added session_state flags

2. **README.md** (documentation)
   - New section documenting features
   - Examples and usage
   - Configuration constants
   - Test instructions

3. **tests/test_conversion.py** (NEW)
   - Comprehensive unit test suite
   - 10 test cases covering all scenarios
   - Standalone functions for isolated testing

## Backward Compatibility

✅ **No breaking changes**
- Existing functionality preserved for normal ranges
- `allow_extrapolate` parameter maintained for testing
- All previous tests remain valid
- Session state structure expanded (no conflicts)

## Configuration

All behavior is configurable via constants:

```python
# In streamlit_app.py
MAX_EXTRAPOLATE = 60.0                # Change to 55.0 or other value if desired
PROTEIN_FACTOR_PSMF_LBM = 1.8         # Adjust protein factor for LBM-based PSMF
UMBRAL_ALTA_ADIPOSIDAD = 45.0         # Adjust high adiposity warning threshold
```

## Real-World Example

**User Profile (from problem statement):**
- Weight: 140 kg
- Height: 164 cm
- Omron reading: 58.5%
- InBody reading: 52.8%

**Before Implementation:**
- Omron 58.5% → Truncated to 45.3% DEXA (incorrect)
- PSMF: 140kg × 1.6 = 224g protein/day (excessive)

**After Implementation:**
- Omron 58.5% → 60.0% DEXA (extrapolated, capped, with warning)
- Banner shown: "ALTA ADIPOSIDAD DETECTADA"
- LBM = 140 × (1 - 0.60) = 56kg
- PSMF: 56kg × 1.8 = 100.8g protein/day (LBM-based)
- UI clearly indicates: "proteina 1.8g/kg LBM"

**Benefits:**
1. More realistic body fat estimate (60% vs 45.3%)
2. More appropriate protein target (100.8g vs 224g)
3. Clear warnings about measurement precision
4. Guidance toward better measurement methods
5. Sustainable and physiologically appropriate PSMF protocol

## Conclusion

These changes provide:
- ✅ Better handling of high adiposity cases
- ✅ More accurate and physiologically appropriate calculations
- ✅ Clear user communication and transparency
- ✅ Comprehensive test coverage
- ✅ Backward compatibility
- ✅ Configurable behavior
- ✅ Scientific basis for all decisions

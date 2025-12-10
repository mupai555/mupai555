# Auto-extrapolation Omron (>40%) and LBM-based PSMF for high adiposity; cap=60%

## Summary

This PR implements automatic extrapolation for Omron BIA readings exceeding 40% body fat (outside the calibration table range) and introduces LBM-based protein calculations for PSMF and traditional plans in cases of high adiposity. These changes optimize muscle retention during weight loss for individuals with elevated body fat percentages while maintaining safe caloric and macronutrient floors.

## Scientific Justification

### BIA Limitations at High Adiposity
Bioelectrical Impedance Analysis (BIA) devices like the Omron HBF-516 have calibration tables that typically extend to 40% body fat. Beyond this threshold, accuracy decreases significantly. The implemented linear extrapolation provides a reasonable estimate when more accurate methods (DEXA, InBody) are unavailable, while capping at 60% to prevent unrealistic values.

### LBM-based Protein Rationale
For individuals with high body fat percentages (≥35% men, ≥40% women, or BMI ≥30), calculating protein requirements based on total body weight can result in excessive protein intake. Using Lean Body Mass (LBM) for protein calculations:
- Optimizes muscle protein synthesis without excess
- Reduces metabolic burden
- Makes caloric targets more achievable and sustainable
- Aligns with established PSMF and clinical weight loss protocols

## Changes Made

### 1. Configuration Constants Added
```python
MAX_EXTRAPOLATE = 60.0                    # Extrapolation cap (%)
PROTEIN_FACTOR_PSMF_LBM = 1.8            # PSMF protein factor based on LBM
PROTEIN_FACTOR_TRAD_LBM = 1.6            # Traditional plan protein factor based on LBM
EXTREME_ADIPOSITY_THRESHOLD = 45.0        # Threshold for extreme adiposity (%)
CARB_MIN_G = 50                           # Minimum carbohydrates (g)
FAT_FLOOR_G = 20                          # Minimum fats (g)
TEI_MIN_WOMAN = 1200                      # Minimum calories for women
TEI_MIN_MAN = 1400                        # Minimum calories for men
MAX_DEFICIT = 0.35                        # Maximum deficit (35%)
```

### 2. Auto-extrapolation for Omron >40%
- **Function:** `corregir_porcentaje_grasa()`
- **Behavior:** When Omron reading > 40%, automatically extrapolate linearly using last two table points
- **Cap:** Results limited to MAX_EXTRAPOLATE (60%) for safety
- **Flags Set:**
  - `grasa_extrapolada = True`
  - `grasa_extrapolada_valor` = extrapolated result
  - `grasa_extrapolada_medido` = original reading
  - `alta_adiposidad = True` if reading >= 45%
  - `allow_extrapolate = True` for transparency

### 3. UI Checkbox Behavior
- **When medido > 40%:** Checkbox shown as checked and disabled with explanatory text
- **When medido ≤ 40%:** Normal manual checkbox behavior maintained
- Clear messaging about automatic activation for transparency

### 4. PSMF with LBM-based Calculations
- **Function:** `calculate_psmf()`
- **Triggers:** 
  - Men: `grasa_corregida >= 35%` OR `BMI >= 30`
  - Women: `grasa_corregida >= 40%` OR `BMI >= 30`
- **Calculation:** Protein = LBM × 1.8 g/kg
- **Flag:** `psmf_lbm_based = True` stored in session_state
- **UI:** Shows protein ratio as "g/kg LBM" instead of "g/kg peso total"

### 5. Traditional Plan for Extreme Cases
- **Trigger:** `grasa_corregida >= 45%` OR `grasa_extrapolada_medido >= 45%`
- **Changes:**
  - Protein based on LBM: LBM × 1.6 g/kg
  - Minimum carbs: 50g (configurable)
  - Fat floor: 20g (configurable)
  - Deficit capped at 35%
  - TEI minimums: 1200 kcal (women), 1400 kcal (men)
- **Flag:** `trad_protein_lbm_used = True` stored in session_state
- **UI:** Info message explaining the LBM-based adjustment

### 6. Session State Flags
New flags added to defaults initialization:
- `alta_adiposidad: bool` - High adiposity detected
- `psmf_lbm_based: bool` - PSMF using LBM calculations
- `trad_protein_lbm_used: bool` - Traditional plan using LBM calculations

### 7. UI Messages and Traceability
- Warning when extrapolation is used
- Error alert for high adiposity cases (>= 45%)
- LBM-based calculation indicators in PSMF display
- Info message in traditional plan for extreme cases
- All text without accents to prevent encoding issues

## Test Coverage

Comprehensive test suite in `tests/test_conversion.py` with 15 tests:

### Omron Conversion Tests (7 tests)
- ✅ Interpolation at 39% (men and women)
- ✅ Exact value at 40% boundary
- ✅ Extrapolation at 43% (auto-activated)
- ✅ Extrapolation at 58.5% with cap verification
- ✅ InBody (no extrapolation, factor-based)
- ✅ DEXA (passthrough, no changes)

### PSMF Calculation Tests (6 tests)
- ✅ LBM-based for men at 35% body fat
- ✅ LBM-based for women at 40% body fat
- ✅ LBM-based triggered by BMI >= 30
- ✅ Normal (bodyweight-based) at 25% body fat
- ✅ Not applicable for men <= 18% body fat
- ✅ Not applicable for women <= 23% body fat

### Integration Tests (2 tests)
- ✅ Real-world scenario: Omron 58.5%, InBody 52.8%, 140kg, 164cm
- ✅ High adiposity flag activation at >= 45%

**Test Results:** All 15 tests passing ✅

## Examples

### Example 1: Omron 58.5%, Male, 140kg, 164cm
**Before:**
- Omron 58.5% capped at 45.3% (table max)
- Protein: 140kg × 1.6 = 224g/day

**After:**
- Omron 58.5% extrapolated to ~60% (capped at MAX_EXTRAPOLATE)
- High adiposity detected
- Protein: 56kg LBM × 1.8 = 100.8g/day (PSMF)
- More sustainable and physiologically appropriate

### Example 2: InBody 52.8%, Male, 140kg, 164cm
**Before:**
- Protein: 140kg × 1.6 = 224g/day

**After:**
- BMI = 52.1 (>= 30, triggers LBM-based)
- Body fat ~54% corrected
- LBM = 64.4kg
- Protein: 64.4kg × 1.8 = 115.9g/day (PSMF)
- Calorie target more achievable

## Files Changed

- ✅ `streamlit_app.py` - Core implementation
- ✅ `requirements.txt` - Added pytest
- ✅ `tests/test_conversion.py` - Comprehensive test suite (new)
- ✅ `tests/__init__.py` - Test package init (new)
- ✅ `README.md` - Complete changelog and documentation

## How to Test

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run test suite:
   ```bash
   python -m pytest tests/test_conversion.py -v
   ```

3. Manual testing scenarios:
   - Omron reading 39% → Should interpolate normally
   - Omron reading 40% → Exact table value
   - Omron reading 43% → Auto-extrapolate, checkbox disabled
   - Omron reading 58.5% → Auto-extrapolate with cap at 60%
   - Man with 35% body fat → PSMF should use LBM
   - Woman with 40% body fat → PSMF should use LBM
   - Man with BMI >= 30 → PSMF should use LBM even if body fat < 35%
   - Traditional plan with 45%+ body fat → Should use LBM with info message

## Backwards Compatibility

- ✅ All existing functionality preserved
- ✅ Default behavior unchanged for readings <= 40%
- ✅ InBody, BodPod, and DEXA conversions unchanged
- ✅ Traditional plan behavior for body fat < 45% unchanged
- ✅ Session state flags are additive (no breaking changes)

## Safety Features

- Maximum extrapolation cap of 60% to prevent unrealistic values
- Minimum calorie floors: 1200 kcal (women), 1400 kcal (men)
- Minimum macronutrient floors: 50g carbs, 20g fats
- Maximum deficit cap of 35%
- Clear UI warnings when using extrapolation or special calculations

## Documentation

Complete documentation added to README.md including:
- Feature descriptions
- Configuration constants
- Scientific justification
- Test instructions
- Usage examples

## Future Considerations

- Monitor user feedback on extrapolation accuracy
- Consider adjusting MAX_EXTRAPOLATE cap based on real-world data
- Potentially add more granular LBM-based thresholds for different populations
- Consider adding medical professional review flag for extreme cases

## Notes for Reviewers

- All tests passing (15/15) ✅
- No syntax errors ✅
- Configuration values are based on conservative, evidence-based recommendations
- UI text avoids accents to prevent encoding issues (following codebase pattern)
- Session state flags enable future feature tracking and reporting enhancements

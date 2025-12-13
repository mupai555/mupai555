# PSMF Tier-Based Implementation

## Overview
This document describes the tier-based PSMF (Protein Sparing Modified Fast) protocol implementation that replaces the previous single-formula approach with a more sophisticated adiposity-based tier system.

## Changes Made

### 1. Tier System Implementation

The new system categorizes users into three tiers based on their adiposity levels:

#### Tier 1 - Low Adiposity
- **Men:** BF% < 25%
- **Women:** BF% < 35%
- **Protein Base:** Total body weight (peso_kg)
- **Carb Cap:** 50g/day

#### Tier 2 - Moderate Adiposity
- **Men:** 25% ≤ BF% < 35%
- **Women:** 35% ≤ BF% < 45%
- **Protein Base:** Lean Body Mass (MLG_kg)
- **Carb Cap:** 40g/day

#### Tier 3 - High Adiposity (predominates over other tiers)
- **Triggered by ANY of:**
  - IMC (BMI) ≥ 40, OR
  - Men: BF% ≥ 35%, OR
  - Women: BF% ≥ 45%
- **Protein Base:** Ideal weight at BMI 25 (peso_ideal_ref_kg = 25 × estatura_m²)
- **Carb Cap:** 30g/day

### 2. Protein Calculation

Protein is calculated using:
```
proteina_g = factor_proteina_psmf × base_proteina_kg
```

Where:
- **factor_proteina_psmf:**
  - 1.8 g/kg if BF% < 25%
  - 1.6 g/kg if BF% ≥ 25%
- **base_proteina_kg:** Depends on tier (see above)

### 3. Fat Allocation (unchanged)

- **30g/day** if BF% < 25%
- **50g/day** if BF% ≥ 25%

### 4. Calorie Multipliers (unchanged)

Based on body fat percentage:
- **BF% > 35%:** multiplier = 8.3 (high body fat)
- **BF% ≥ 25% (Men) or ≥ 30% (Women):** multiplier = 9.0 (moderate)
- **BF% < 25% (Men) or < 30% (Women):** multiplier = 9.6 (lean)

### 5. Carbohydrate Calculation with Cap

```python
kcal_prot = 4 × proteina_g
kcal_grasa = 9 × grasas_g
carbs_g_calculado = max((kcal_psmf_obj - (kcal_prot + kcal_grasa)) / 4, 0)
carbs_g = min(carbs_g_calculado, carb_cap_g)
kcal_psmf_final = kcal_prot + kcal_grasa + 4 × carbs_g
```

If the calculated carbs exceed the tier's carb cap, the cap is applied and a note is displayed to the user.

### 6. Explainability Fields

New fields added to PSMF calculation results:
- `tier_psmf`: The tier classification (1, 2, or 3)
- `base_proteina_usada`: Description of protein base ("Peso total", "MLG", or "Peso ideal (IMC 25)")
- `base_proteina_kg`: Numeric value of the protein base used
- `carb_cap_aplicado_g`: The carb cap limit applied
- `carb_cap_fue_aplicado`: Boolean indicating if the cap was actually applied
- `factor_proteina_psmf`: The protein factor used (1.6 or 1.8)

## Example: Karina Case

### Input Data
- **Sex:** Mujer (Woman)
- **Weight:** 140 kg
- **Height:** 164 cm
- **Body Fat %:** 49%

### Calculations
1. **IMC:** 140 / (1.64²) = 52.05
2. **MLG:** 140 × (1 - 0.49) = 71.4 kg
3. **Peso ideal (BMI 25):** 25 × (1.64²) = 67.24 kg

### Tier Determination
- Woman with BF% = 49% (≥ 45%) → **Tier 3**
- Base: Peso ideal = 67.24 kg

### Macros
- **Protein:** 1.6 × 67.24 = 107.6 g/day
- **Fat:** 50 g/day (BF% ≥ 25%)
- **Carb cap:** 30 g (Tier 3)
- **Carbs calculated:** 3.2 g/day (after applying cap)
- **Total calories:** 893 kcal/day

## Modified Files

### streamlit_app.py
1. Updated `calculate_psmf()` function signature to include `estatura_cm` parameter
2. Implemented tier determination logic
3. Added protein base selection based on tier
4. Implemented carb cap calculation
5. Added explainability fields to return dictionary
6. Updated function call at line 2495 to pass estatura
7. Updated display sections (lines 2496-2518, 3338-3354, 3363-3402) to show tier information

### test_psmf_tiers.py (new file)
Comprehensive test suite with 6 test cases:
1. Karina - Tier 3 (high adiposity by BF%)
2. Man - Tier 2 (moderate adiposity)
3. Woman - Tier 1 (low adiposity)
4. Man - Tier 1 (low body fat with 1.8 factor)
5. Tier 3 triggered by IMC ≥ 40
6. Woman - Tier 2 (moderate-high adiposity)

All tests validate:
- Correct tier classification
- Appropriate protein base selection
- Correct protein factor and fat allocation
- Proper carb cap application
- Accurate final calorie calculation

## Testing Results

All existing tests continue to pass:
- ✅ test_ffmi_acceptance.py
- ✅ test_ffmi_mode.py
- ✅ test_integration.py
- ✅ test_omron_conversion.py
- ✅ test_protein_mlg.py
- ✅ test_psmf_tiers.py (new)

## Benefits

1. **More Personalized:** Protein recommendations are tailored to adiposity level
2. **Safer for Obese Individuals:** Tier 3 uses ideal weight to avoid excessive protein loads
3. **Better Adherence:** Different carb caps provide flexibility based on metabolic needs
4. **Transparent:** Users can see exactly which tier they're in and why
5. **Consistent:** Maintains existing fat allocation and multiplier logic

## Notes

- PSMF eligibility remains unchanged (Men: BF% > 18%, Women: BF% > 23%)
- Minimum calorie floors remain enforced (800 kcal men, 700 kcal women)
- Traditional Plan protein calculation (30/42 rules) remains unchanged
- All safety warnings and recommendations remain in place

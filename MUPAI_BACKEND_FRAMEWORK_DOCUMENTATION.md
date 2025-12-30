# MUPAI Backend Framework - Complete Documentation

## Overview

This document describes the comprehensive backend calculation framework implemented in the MUPAI (Muscle Up Performance Assessment Intelligence) system. All calculations run invisibly in the backend, regardless of UI visibility settings, ensuring complete and accurate evaluations while maintaining a clean user interface.

## Implementation Status: ✅ COMPLETE

All requirements from the problem statement have been successfully implemented and documented.

---

## 1. Invisible Backend Calculations

### 1.1 TDEE Calculation (Total Daily Energy Expenditure)

The TDEE represents the complete daily energy expenditure and is calculated using a multi-component approach:

#### Formula:
```
TDEE = (TMB × GEAF × ETA) + GEE
```

#### Components:

**TMB (Tasa Metabólica Basal) - Cunningham Equation**
- Function: `calcular_tmb_cunningham(mlg)`
- Formula: `TMB = 370 + (21.6 × MLG)`
- Uses fat-free mass for precision in athletic populations
- More accurate than Harris-Benedict or Mifflin-St Jeor for trained individuals

**GEAF (Gasto Energético por Actividad Física)**
- Function: `obtener_geaf(nivel)`
- Values: 1.00 (Sedentario), 1.11 (Moderadamente-activo), 1.25 (Activo), 1.45 (Muy-activo)
- Represents daily activity EXCLUDING structured exercise
- Based on step count and job physical demands

**ETA (Efecto Térmico de los Alimentos)**
- Calculated inline in main flow (lines 4832-4860)
- Values: 1.10 (standard), 1.12 (medium), 1.15 (high)
- Adjusted by body composition and sex
- Higher for leaner individuals (better metabolic efficiency)
- Men: ≤10% BF = 1.15, 11-20% = 1.12, >20% = 1.10
- Women: ≤20% BF = 1.15, 21-30% = 1.12, >30% = 1.10

**GEE (Gasto Energético por Ejercicio)**
- Calculated based on training frequency and intensity
- Depends on training level (principiante/intermedio/avanzado/élite)
- Averaged daily from weekly training sessions

### 1.2 Deficit/Surplus Percentages Based on Body Fat

#### Phase Determination Function
- Function: `determinar_fase_nutricional_refinada(grasa_corregida, sexo)`
- Returns: (phase_description, percentage_adjustment)

#### Logic by Sex and Body Fat:

**For Men:**
- <6% BF: Surplus 10-15% (competition lean, needs mass gain)
- 6-10% BF: Surplus 5-10% (athletic, can build muscle)
- 10-15% BF: Slight surplus 0-5% (optimal for muscle gain)
- 15-18% BF: Maintenance 0% (good condition, recomposition)
- >18% BF: Deficit (variable, see deficit table)

**For Women:**
- <12% BF: Surplus 10-15% (competition lean, needs mass gain)
- 12-16% BF: Surplus 5-10% (athletic, can build muscle)
- 16-20% BF: Slight surplus 0-5% (optimal for muscle gain)
- 20-23% BF: Maintenance 0% (good condition, recomposition)
- >23% BF: Deficit (variable, see deficit table)

#### Deficit Calculation Function
- Function: `sugerir_deficit(porcentaje_grasa, sexo)`
- Returns graduated deficit based on adiposity level
- Range: 3% (very lean) to 50% (severe obesity)
- Safety limit: 30% max for non-obese individuals
- Protects muscle mass while allowing fat loss

**Men's Deficit Table:**
| Body Fat % | Deficit % | Rationale |
|------------|-----------|-----------|
| 0-8% | 3% | Minimal - preserve muscle |
| 8-10.5% | 5% | Very lean, conservative |
| 10.6-13% | 10% | Athletic range |
| 13.1-15.5% | 15% | Fitness lower |
| 15.6-18% | 20% | Fitness |
| 18.1-20.5% | 25% | Average low |
| 20.6-23% | 27% | Average |
| 23.1-25.5% | 29% | Average high |
| 25.6-30% | 30% | Overweight (safety cap) |
| 30.1-32.5% | 35% | Overweight high |
| 32.6-40% | 35% | Obesity class I |
| 40.1-45% | 40% | Obesity class II |
| >45.1% | 50% | Severe obesity |

**Women's Deficit Table:** (Similar structure, adjusted thresholds)

### 1.3 Macro Allocation

#### Traditional Plan Macros
- Function: `calcular_macros_tradicional(ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg)`

**Protein Calculation:**
- Factor: 1.6-2.2 g/kg (varies by body fat %)
- Base: MLG if male ≥35% BF or female ≥42% BF, otherwise total weight
- Rationale: Prevents protein inflation in high adiposity

**Protein Factors by Body Fat:**
- ≥35%: 1.6 g/kg
- 25-34.9%: 1.8 g/kg
- 15-24.9%: 2.0 g/kg
- 4-14.9%: 2.2 g/kg

**Fat Calculation:**
- ALWAYS 40% of TMB
- Restricted to 20-40% of total calories (TEI)
- Based on scientific evidence for optimal hormonal function

**Carbohydrate Calculation:**
- Remainder after protein and fat
- Formula: `(Total Calories - Protein Calories - Fat Calories) / 4`
- Minimum: 0g (cannot be negative)

#### PSMF (Protein Sparing Modified Fast) Macros
- Function: `calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm)`
- Only applicable: Men >18% BF, Women >23% BF

**Tier-Based System:**

**Tier 1 - Low Adiposity:**
- Men: <25% BF
- Women: <35% BF
- Protein base: Total weight
- Carb cap: 50g/day

**Tier 2 - Moderate Adiposity:**
- Men: 25-34.9% BF
- Women: 35-44.9% BF
- Protein base: Fat-free mass (MLG)
- Carb cap: 40g/day

**Tier 3 - High Adiposity:**
- Men: ≥35% BF OR BMI ≥40
- Women: ≥45% BF OR BMI ≥40
- Protein base: Ideal weight (BMI 25)
- Carb cap: 30g/day

**Protein Factors:**
- <25% BF: 1.8 g/kg × base
- ≥25% BF: 1.6 g/kg × base

**Fat Amounts:**
- <25% BF: 30g/day
- ≥25% BF: 50g/day

**Calorie Target:**
- Formula: Protein (g) × Multiplier
- Multipliers: 8.3 (high BF), 9.0 (moderate), 9.6 (lean)

**Expected Weight Loss:**
- Men: 0.8-1.2 kg/week
- Women: 0.6-1.0 kg/week
- Duration: 6-8 weeks maximum
- Requires medical supervision

---

## 2. Email Reporting System

### 2.1 Email Structure

The system generates comprehensive email reports that include ALL calculation details, regardless of UI visibility settings.

#### Primary Email Function
- Function: `enviar_email_resumen(contenido, nombre_cliente, email_cliente, fecha, edad, telefono, progress_photos)`
- Destination: administracion@muscleupgym.fitness
- Includes progress photos as attachments

#### Report Sections (Complete List)

1. **Client Data**
   - Full name, age, sex, phone, email, assessment date

2. **Anthropometry and Body Composition**
   - Weight, height, BMI
   - Body fat % (measured and DEXA-corrected)
   - Muscle mass %, visceral fat level
   - Fat-free mass (MLG), fat mass

3. **Metabolic Indices**
   - TMB (Cunningham)
   - FFMI (Fat-Free Mass Index) with detailed calculation
   - FMI (Fat Mass Index)
   - Metabolic age

4. **TDEE Complete Breakdown** ✅ NEW ENHANCED SECTION
   - TMB calculation with formula
   - GEAF factor with activity level
   - ETA factor with scientific justification
   - GEE from training
   - Complete TDEE formula with step-by-step calculation
   - Example: `TDEE = (1800 × 1.11 × 1.12) + 300 = 2540 kcal`

5. **Nutritional Phase Recommendation**
   - Current phase (deficit/maintenance/surplus)
   - FBEO factor
   - Target calorie intake
   - Calorie/kg ratio

6. **Macro Distribution**
   - Protein: grams, calories, percentage
   - Fat: grams, calories, percentage
   - Carbs: grams, calories, percentage

7. **6-Week Scientific Projection**
   - Weekly weight change range (kg and %)
   - Total projected change
   - Before/after weight projection
   - Scientific explanation

8. **Training Experience and Functional Assessment**
   - Self-reported experience level
   - All functional exercise results with levels
   - Overall training level calculation

9. **Comparative Nutritional Plans**
   - Traditional plan (always shown)
   - PSMF plan (when applicable, with full details)
   - Side-by-side comparison of strategies
   - Sustainability and adherence analysis

10. **Recovery State (Sleep + Stress)**
    - Sleep quality scores
    - Stress level scores
    - IR-SE index (Recovery Index)
    - Alert flags and recommendations

11. **Personal Goals**
    - Medium and long-term objectives
    - Analysis and considerations

12. **Additional Preferences and Habits**
    - Body fat measurement method
    - Metabolic age vs chronological age
    - Recommended supplementation

13. **Warnings and Recommendations**
    - Medical supervision requirements
    - Re-evaluation schedule
    - Tracking metrics
    - Hydration requirements

### 2.2 Email Generation Flow

```
User completes questionnaire
    ↓
All backend calculations run
    ↓
tabla_resumen string assembled with ALL data
    ↓
Progress photos attached (if available)
    ↓
Email sent to administration
    ↓
Secondary internal report (Part 2) sent
```

**Key Points:**
- Email ALWAYS contains complete technical details
- UI visibility flags (USER_VIEW, SHOW_TECH_DETAILS, etc.) do NOT affect email content
- Email serves as complete professional report for internal use
- Users receive minimal UI but professionals receive full data

---

## 3. UI Integration (Minimal Display)

### 3.1 Visibility Control Flags

```python
SHOW_TECH_DETAILS = False       # Hide technical calculations from UI
MOSTRAR_PSMF_AL_USUARIO = False  # Hide PSMF details from UI
MOSTRAR_ETA_AL_USUARIO = False   # Hide ETA details from UI
USER_VIEW = False                # Hide detailed results from UI
```

### 3.2 Flow Control System

- Function: `get_flow_phase()` returns current phase
- Phases: 'intake' (data collection), 'review' (future), 'final' (results)
- Decorators control what users see:
  - `@render_user_safe` - Always visible (basic inputs)
  - `@render_if_final` - Only in final phase (technical details)
  - `@hide_during_intake` - Hidden during intake

### 3.3 What Users See (When USER_VIEW = False)

**During Assessment:**
- Data input forms
- Progress indicators
- Validation messages

**After Completion:**
- Simple completion message
- Generic success confirmation
- No detailed calculations or results

**What Users DON'T See:**
- TDEE breakdown
- FFMI/FMI calculations
- Macro distribution details
- PSMF analysis
- Technical factors and formulas

**Important:** Even though users don't see these details, ALL calculations run completely in the backend and are captured in the email report.

---

## 4. Code Alignment and Documentation

### 4.1 Code Organization Principles

**Centralized Calculation Functions:**
- All key calculations in dedicated, well-documented functions
- No duplication of logic across UI and email generation
- Single source of truth for each calculation

**Clear Abstraction Layers:**
- Input validation layer
- Calculation layer (pure functions)
- Presentation layer (UI)
- Reporting layer (email)

**Consistent Naming Conventions:**
- `calcular_*` for calculation functions (Spanish)
- `obtener_*` for getter functions (Spanish)
- Clear, descriptive variable names
- Type hints where appropriate

### 4.2 Documentation Standards

Each major function now includes:
- **Purpose:** What the function does
- **Backend Calculation Context:** Its role in MUPAI framework
- **Scientific Rationale:** Why the calculation is done this way
- **Formula/Algorithm:** Step-by-step math
- **Parameters:** What inputs are needed
- **Returns:** What outputs are generated
- **Examples:** Practical usage demonstrations
- **References:** Scientific papers when applicable

**Example - Enhanced Documentation Structure:**
```python
def calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm=None):
    """
    Calcula los parámetros para PSMF (Protein Sparing Modified Fast).
    
    BACKEND CALCULATION - PSMF Special Protocol
    ============================================
    PSMF es un protocolo de dieta muy baja en calorías (VLCD) diseñado para
    maximizar la pérdida de grasa mientras se minimiza la pérdida de masa muscular
    mediante alta ingesta proteica.
    
    [... extensive documentation continues ...]
    """
```

### 4.3 Key Documentation Additions

**Module-Level Documentation:**
- Comprehensive overview at file top
- Explains all 6 core calculation modules
- Documents calculation flow
- Lists all visibility control mechanisms

**Function-Level Documentation:**
- `calcular_tmb_cunningham()` - Complete TMB explanation
- `calcular_mlg()` - Body composition fundamentals
- `obtener_geaf()` - Activity factor details
- ETA calculation section - Thermic effect science
- `sugerir_deficit()` - Graduated deficit system
- `determinar_fase_nutricional_refinada()` - Phase logic
- `calcular_macros_tradicional()` - Traditional macro allocation
- `calculate_psmf()` - PSMF tier system (180+ line docstring)
- `calcular_proyeccion_cientifica()` - Weekly projections

---

## 5. Testing and Validation

### 5.1 Existing Test Suite

**Tests Run Successfully:**
- ✅ `test_centralized_macros_standalone.py` - Macro calculation consistency
- ✅ `test_psmf_tiers.py` - PSMF tier system validation
- ✅ All calculations verified with multiple test cases

### 5.2 Validation Approach

**Input Validation:**
- Name: 2+ words, letters only
- Phone: Exactly 10 digits
- Email: Valid format
- Numeric fields: Range validation
- Required fields: Completeness check

**Calculation Validation:**
- Safe type conversion with fallbacks
- Division by zero protection
- Range limiting where appropriate
- Consistent rounding rules

**Output Validation:**
- Email size limits (15MB attachment limit)
- Photo format validation
- Report completeness checks

---

## 6. Security and Best Practices

### 6.1 Data Handling

- No sensitive data in version control
- Credentials managed via Streamlit secrets
- Email communication over TLS
- Input sanitization for all user data

### 6.2 Error Handling

- Try-except blocks around calculations
- Graceful degradation with fallback values
- User-friendly error messages
- Detailed error logging for debugging

### 6.3 Code Quality

- Clear separation of concerns
- DRY principle (Don't Repeat Yourself)
- Functions with single responsibility
- Comprehensive inline documentation

---

## 7. Scientific References

The MUPAI framework is built on peer-reviewed scientific literature:

### Metabolic Calculations
- Cunningham, J. J. (1980). Cunningham equation for BMR
- Institute of Medicine (2005). Dietary Reference Intakes for Energy
- FAO/WHO/UNU (2001). Human energy requirements

### Body Composition
- Siedler & Tinsley (2022). Omron HBF-516 to 4C model conversion
- Heymsfield et al. Various FFMI research

### Deficit/Surplus Strategy
- Hall, K. D. (2008). Energy deficit per unit weight loss
- Helms, E. R. et al. (2014). Natural bodybuilding nutrition

### PSMF Protocol
- Blackburn, G. L., et al. (1973). Protein-sparing fast effects
- McDonald, L. (2005). Rapid Fat Loss Handbook
- Sours, H. E., et al. (1981). VLCD safety considerations

### Macronutrient Distribution
- Phillips, S. M., & Van Loon, L. J. (2011). Dietary protein for athletes
- Aragon, A. A., & Schoenfeld, B. J. (2013). Nutrient timing
- Burke et al. (2011). Nutritional strategies for athletes

---

## 8. Conclusion

The MUPAI backend framework is now comprehensively documented with:

✅ **Complete invisible calculations** running regardless of UI visibility
✅ **Detailed TDEE breakdown** with all components explained
✅ **Phase suggestions** with scientific deficit/surplus percentages
✅ **Macro allocations** for both traditional and PSMF plans
✅ **Weekly projections** with realistic ranges
✅ **Comprehensive email reports** containing all technical details
✅ **Minimal UI** for end users (controlled by visibility flags)
✅ **Extensive inline documentation** for all major functions
✅ **Validated calculations** with passing test suite
✅ **Clear code organization** following best practices

**All requirements from the problem statement have been met:**

1. ✅ Invisible Calculations - TMB, GEAF, ETA, GEE, deficits, macros, PSMF
2. ✅ Email Reporting - Complete structured report with all data
3. ✅ UI Integration - Minimal display, calculations run invisibly
4. ✅ Code Alignment - Clear abstraction, comprehensive documentation

The system is production-ready and fully documented for maintenance and future enhancements.

---

**Document Version:** 1.0  
**Date:** 2025-12-30  
**System:** MUPAI v2.0 - Muscle Up Performance Assessment Intelligence

# PSMF and ETA Visibility Control Guide

## Overview

This guide documents the visibility control flags for PSMF (Protein Sparing Modified Fast) and ETA (Thermal Effect of Food) methodologies. These flags allow the application to protect proprietary calculation methodologies by hiding them from the user interface while maintaining full backend functionality and administrative reporting capabilities.

## Purpose

The visibility flags serve to:
1. **Protect Intellectual Property**: Hide proprietary methodologies from end users
2. **Maintain Backend Functionality**: Ensure all calculations continue to run for downstream processing
3. **Enable Administrative Reporting**: Include complete technical details in internal reports and emails
4. **Provide Flexible Control**: Allow selective visibility of specific methodologies

## Visibility Flags

### Location
The flags are defined at the top of `streamlit_app.py` (lines 20-27):

```python
# Visibility flags for specific methodologies - Control display to end users
# These flags protect proprietary methodologies while maintaining backend functionality
# When False: Hide methodology details from user UI (calculations still run, emails include details)
# When True: Show methodology details to users
# Note: All calculations always run; email reports always include full details
MOSTRAR_PSMF_AL_USUARIO = False  # Controls PSMF (Protein Sparing Modified Fast) UI visibility
MOSTRAR_ETA_AL_USUARIO = False   # Controls ETA (Thermal Effect of Food) UI visibility
```

### MOSTRAR_PSMF_AL_USUARIO

**Purpose**: Controls the visibility of PSMF (Protein Sparing Modified Fast) related UI elements.

**Default Value**: `False` (hidden from users)

**When False (Production Mode)**:
- PSMF candidate warning box is **hidden**
- PSMF plan selection option is **hidden**
- PSMF comparison details are **hidden**
- PSMF warnings and safety information are **hidden**
- PSMF tier, multiplier, and calculation details are **hidden**
- All mentions of PSMF in final summary are **hidden**

**When True (Testing/Internal Mode)**:
- All PSMF UI elements are visible
- Users can see and select PSMF protocol
- Complete PSMF methodology is displayed

**Backend Behavior** (always, regardless of flag):
- `calculate_psmf()` function **always runs**
- PSMF calculations are **always performed**
- Results stored in `st.session_state.psmf_recs`
- PSMF applicability stored in `st.session_state.psmf_aplicable`
- Email reports **always include** complete PSMF details
- Administrative reports **always contain** full PSMF methodology

**UI Elements Affected**:
1. PSMF candidate notification (lines ~2930-2974)
2. Plan selection radio button including PSMF option (lines ~3759-3829)
3. PSMF-specific warnings and safety information (lines ~3864-3888)
4. PSMF note in final evaluation summary (line ~4124)

### MOSTRAR_ETA_AL_USUARIO

**Purpose**: Controls the visibility of ETA (Thermal Effect of Food / Efecto Térmico de los Alimentos) related UI elements.

**Default Value**: `False` (hidden from users)

**When False (Production Mode)**:
- ETA calculation expander is **completely hidden**
- ETA factor values are **not displayed**
- ETA methodology explanation is **hidden**
- Technical ETA details are **hidden**

**When True (Testing/Internal Mode)**:
- ETA expander section is visible
- Users can see ETA factor (1.10, 1.12, or 1.15)
- Complete ETA calculation methodology is displayed

**Backend Behavior** (always, regardless of flag):
- ETA calculations **always run** (lines ~3527-3549)
- ETA value computed based on body fat % and sex
- Results stored in `st.session_state.eta`
- ETA description stored in `st.session_state.eta_desc`
- ETA color stored in `st.session_state.eta_color`
- ETA used in GE (Total Energy Expenditure) calculation
- Email reports **always include** complete ETA details
- Administrative reports **always contain** full ETA methodology

**UI Elements Affected**:
1. ETA expander section (lines ~3551-3576)
2. ETA factor display and explanation
3. Technical ETA calculation details

## Calculation Logic

### PSMF Calculations

**Always Execute** (regardless of MOSTRAR_PSMF_AL_USUARIO):
```python
# Line ~2928
psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura)
st.session_state.psmf_recs = psmf_recs
st.session_state.psmf_aplicable = psmf_recs.get("psmf_aplicable", False)
```

**PSMF Calculation Details**:
- Determines eligibility based on body fat percentage
- Calculates tier of adiposity (1, 2, or 3)
- Computes protein requirements (1.6-1.8g/kg)
- Determines fat allowance (30-50g based on BF%)
- Applies carbohydrate caps (30-50g based on tier)
- Calculates total daily calories
- Projects weekly weight loss
- Determines multiplier and calorie floor

**Data Stored in session_state**:
- `psmf_recs`: Complete PSMF recommendation dictionary
- `psmf_aplicable`: Boolean indicating PSMF eligibility
- Contains: calories, protein, fat, carbs, tier, multiplier, projected loss, etc.

### ETA Calculations

**Always Execute** (regardless of MOSTRAR_ETA_AL_USUARIO):
```python
# Lines ~3527-3549
if grasa_corregida <= 10 and sexo == "Hombre":
    eta = 1.15
    eta_desc = "ETA alto (muy magro, ≤10% grasa)"
elif grasa_corregida <= 20 and sexo == "Mujer":
    eta = 1.15
    eta_desc = "ETA alto (muy magra, ≤20% grasa)"
elif grasa_corregida <= 20 and sexo == "Hombre":
    eta = 1.12
    eta_desc = "ETA medio (magro, 11-20% grasa)"
elif grasa_corregida <= 30 and sexo == "Mujer":
    eta = 1.12
    eta_desc = "ETA medio (normal, 21-30% grasa)"
else:
    eta = 1.10
    eta_desc = f"ETA estándar (>{20 if sexo == 'Hombre' else 30}% grasa)"

st.session_state.eta = eta
st.session_state.eta_desc = eta_desc
st.session_state.eta_color = eta_color
```

**ETA Calculation Details**:
- Based on body fat percentage and biological sex
- Three levels: High (1.15), Medium (1.12), Standard (1.10)
- Higher ETA for leaner individuals (more muscle = more thermic effect)
- Used in Total Energy Expenditure calculation: `GE = TMB * GEAF * ETA + GEE`

**Data Stored in session_state**:
- `eta`: Numeric ETA factor (1.10, 1.12, or 1.15)
- `eta_desc`: Human-readable description of ETA level
- `eta_color`: UI color indicator (success/info/warning)

## Email Report Generation

**CRITICAL**: Email report generation (`tabla_resumen`) is **COMPLETELY UNAFFECTED** by these flags.

### PSMF in Email Reports

Email reports **always include** (lines ~4552-4579):
```
⚡ PROTOCOLO PSMF ACTUALIZADO (APLICABLE/NO APLICABLE):
- Calorías: X kcal/día
- Criterio de aplicabilidad: ...
- Proteína: Xg (X kcal) = X%
- Grasas: Xg (X kcal) = X%
- Carbohidratos: Xg (X kcal) = X% (solo vegetales fibrosos)
- Multiplicador calórico: X (perfil: ...)
- Déficit estimado: ~X%
- Pérdida esperada: X-X kg/semana
- Sostenibilidad: BAJA - Máximo 6-8 semanas
- Duración recomendada: 6-8 semanas con supervisión médica obligatoria
- Suplementación necesaria: Multivitamínico, omega-3, electrolitos, magnesio
- Monitoreo requerido: Análisis de sangre regulares
```

### ETA in Email Reports

Email reports **always include** (lines ~4486-4489):
```
🔥 EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):
- Factor ETA: X.XX
- Criterio aplicado: ETA alto/medio/estándar
- Justificación: Basado en % grasa corporal (X.X%) y sexo (...)
```

### Email Recipients

Reports are sent to:
- Primary: User's email address
- CC/Administrative: `administracion@muscleupgym.fitness`
- Additional CC: `login.fitness` (for PARTE 2)

## Usage Examples

### Production Deployment (Hide from Users)

```python
# streamlit_app.py (top of file)
MOSTRAR_PSMF_AL_USUARIO = False  # Hide PSMF from users
MOSTRAR_ETA_AL_USUARIO = False   # Hide ETA from users
```

**Result**:
- Users see simplified interface
- No PSMF protocol option
- No ETA technical details
- Calculations still run
- Emails contain full details
- Backend processing unaffected

### Internal Testing (Show Everything)

```python
# streamlit_app.py (top of file)
MOSTRAR_PSMF_AL_USUARIO = True   # Show PSMF to users
MOSTRAR_ETA_AL_USUARIO = True    # Show ETA to users
```

**Result**:
- Complete methodology visible
- Users can select PSMF
- ETA calculations displayed
- Full technical details shown
- Useful for validation and testing

### Selective Visibility

```python
# Example: Show ETA but hide PSMF
MOSTRAR_PSMF_AL_USUARIO = False
MOSTRAR_ETA_AL_USUARIO = True

# Example: Show PSMF but hide ETA
MOSTRAR_PSMF_AL_USUARIO = True
MOSTRAR_ETA_AL_USUARIO = False
```

## Testing

### Test Suite

Run the comprehensive test to validate implementation:

```bash
# Test PSMF and ETA visibility flags
python test_psmf_eta_visibility.py

# Test integration with existing functionality
python test_ui_tech_details.py
python test_psmf_tiers.py
python test_integration.py
```

### Manual Testing Checklist

**With MOSTRAR_PSMF_AL_USUARIO = False**:
- [ ] No PSMF warning box appears for eligible users
- [ ] No PSMF plan selection option available
- [ ] No PSMF technical details displayed
- [ ] Plan defaults to "Tradicional"
- [ ] PSMF calculations still run (check session_state)
- [ ] Email contains full PSMF details

**With MOSTRAR_ETA_AL_USUARIO = False**:
- [ ] ETA expander section is completely hidden
- [ ] No ETA factor displayed to user
- [ ] ETA calculations still run (check session_state)
- [ ] GE calculation uses ETA correctly
- [ ] Email contains full ETA details

**With Both Flags = False**:
- [ ] Clean, simplified user interface
- [ ] No proprietary methodology visible
- [ ] All calculations work correctly
- [ ] Final calorie recommendations accurate
- [ ] Email reports complete and detailed

## Relationship with SHOW_TECH_DETAILS

These flags work **independently** from `SHOW_TECH_DETAILS`:

| Flag Combination | User Sees |
|-----------------|-----------|
| `MOSTRAR_PSMF_AL_USUARIO = False`<br>`SHOW_TECH_DETAILS = False` | No PSMF UI at all |
| `MOSTRAR_PSMF_AL_USUARIO = False`<br>`SHOW_TECH_DETAILS = True` | No PSMF UI at all |
| `MOSTRAR_PSMF_AL_USUARIO = True`<br>`SHOW_TECH_DETAILS = False` | PSMF UI shown (simplified) |
| `MOSTRAR_PSMF_AL_USUARIO = True`<br>`SHOW_TECH_DETAILS = True` | PSMF UI shown (full details) |

Same logic applies to `MOSTRAR_ETA_AL_USUARIO`.

**Design Principle**: The methodology-specific flags (`MOSTRAR_PSMF_AL_USUARIO`, `MOSTRAR_ETA_AL_USUARIO`) control **whether** content is shown. The general flag (`SHOW_TECH_DETAILS`) controls **how much detail** is shown if content is visible.

## Implementation Principles

1. **Separation of Concerns**: Calculations are independent from UI display
2. **Backend First**: All calculations execute before UI decisions
3. **Session State Storage**: Results always stored for downstream use
4. **Email Independence**: Reports never affected by UI flags
5. **Single Point of Control**: One flag per methodology for easy management
6. **Fail-Safe Defaults**: Default to hidden (False) for production safety
7. **Clear Documentation**: Extensive comments in code explaining behavior

## Security and IP Protection

These flags provide:
- **Methodology Protection**: Users cannot see proprietary formulas
- **Competitive Advantage**: Calculation methods remain confidential
- **Professional Presentation**: Clean interface without overwhelming details
- **Administrative Transparency**: Full details available to authorized personnel
- **Audit Trail**: Complete records in email reports

## Troubleshooting

### Issue: PSMF still showing to users

**Diagnosis**:
```bash
grep "MOSTRAR_PSMF_AL_USUARIO = " streamlit_app.py
```

**Solution**:
- Verify flag is set to `False` at top of file (line ~25)
- Restart Streamlit app to reload changes
- Clear browser cache

### Issue: ETA still visible

**Diagnosis**:
```bash
grep "MOSTRAR_ETA_AL_USUARIO = " streamlit_app.py
```

**Solution**:
- Verify flag is set to `False` at top of file (line ~26)
- Restart Streamlit app
- Check that ETA expander is properly wrapped in conditional

### Issue: Calculations not working

**Diagnosis**:
```python
# Check session_state in Streamlit
import streamlit as st
st.write(st.session_state.get('psmf_recs'))
st.write(st.session_state.get('eta'))
```

**Solution**:
- Verify calculations are outside conditional blocks
- Check that session_state storage always executes
- Run test suite to identify specific issue

### Issue: Email missing details

**Diagnosis**:
```bash
# Check email generation doesn't use visibility flags
grep -A 100 "tabla_resumen = " streamlit_app.py | grep "MOSTRAR_"
# Should return no results in email section
```

**Solution**:
- Email section should NOT check visibility flags
- Verify `tabla_resumen` construction is unconditional
- Review lines 4480-4620 for any flag usage

## Future Enhancements

Potential improvements:
1. **Dynamic Flag Control**: Store flags in Streamlit secrets for remote toggling
2. **Role-Based Access**: Show details to admin users, hide from regular users
3. **Gradual Reveal**: Allow users to "unlock" methodologies after certain milestones
4. **Analytics Tracking**: Log when hidden methodologies would have been applicable
5. **A/B Testing**: Compare user engagement with/without methodology visibility

## Code Review Points

When reviewing changes:
1. ✓ Verify flags are only used in UI rendering code
2. ✓ Ensure calculations happen unconditionally
3. ✓ Confirm email generation doesn't use flags
4. ✓ Check session_state storage always executes
5. ✓ Validate test coverage
6. ✓ Verify default values are False (hidden)
7. ✓ Ensure flag combinations work correctly

## Related Documentation

- `SHOW_TECH_DETAILS_GUIDE.md`: General technical detail visibility
- `PSMF_TIER_IMPLEMENTATION.md`: PSMF calculation methodology
- `FFMI_MODE_IMPLEMENTATION.md`: FFMI calculation and modes
- `FLOW_STATE_IMPLEMENTATION.md`: Application flow control

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-16 | Initial implementation of PSMF and ETA visibility flags |

---

**Maintained By**: Development Team  
**Last Updated**: 2025-12-16  
**Status**: Active / Production Ready

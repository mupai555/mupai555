# Step 4 Placeholder Implementation

## Overview
This document describes the implementation of the Step 4 placeholder that is shown when `MOSTRAR_ETA_AL_USUARIO` is set to `False`.

## Problem Statement
When `MOSTRAR_ETA_AL_USUARIO = False`, the UI was jumping from "Paso 3" directly to "Paso 5", causing potential customer confusion about the flow sequencing.

## Solution
A placeholder for "Paso 4" is now displayed when `MOSTRAR_ETA_AL_USUARIO = False`, maintaining consistent step numbering (3, 4, 5) in the UI.

## Implementation Details

### Code Structure
The implementation uses an if/else structure:

```python
if MOSTRAR_ETA_AL_USUARIO:
    # Show full ETA details (when flag is True)
    with st.expander("🍽️ **Paso 4: Efecto Térmico de los Alimentos (ETA)**", expanded=True):
        # ... full ETA details ...
else:
    # Show placeholder (when flag is False)
    with st.expander("📊 **Paso 4: Cálculo Automático de Factores Metabólicos**", expanded=False):
        # ... generic placeholder message ...
```

### Placeholder Properties

#### Title
- **Text**: "📊 **Paso 4: Cálculo Automático de Factores Metabólicos**"
- **Does NOT** explicitly mention "ETA" to avoid revealing proprietary methodology
- Maintains "Paso 4" numbering for consistency

#### Expander State
- **Collapsed** (`expanded=False`) to minimize visual prominence
- Users can still expand it to see the generic message if curious

#### Progress Indicators
- Progress bar: 70% (same as original Step 4)
- Progress text: "Paso 4 de 5: Procesamiento automático"

#### Message Content
```
ℹ️ **Este paso se calcula automáticamente en función de los datos que has proporcionado.**

Nuestro sistema procesa tu información de composición corporal y nivel de actividad para 
ajustar de manera precisa tus requerimientos energéticos totales.
```

**Key Characteristics:**
- Generic and informative
- Avoids technical jargon
- Does NOT mention "ETA" or "Efecto Térmico de los Alimentos"
- Explains that the step is calculated automatically
- References data already provided by the user

## Backend Behavior (Unchanged)

### ETA Calculations
The backend ETA calculations **ALWAYS run** regardless of the `MOSTRAR_ETA_AL_USUARIO` flag setting:

```python
# ===== ETA CALCULATION (ALWAYS RUNS) =====
# ETA calculations ALWAYS run regardless of UI visibility flag
# ...
if grasa_corregida <= 10 and sexo == "Hombre":
    eta = 1.15
    # ...
# Store ETA results in session_state for downstream use
st.session_state.eta = eta
st.session_state.eta_desc = eta_desc
st.session_state.eta_color = eta_color
```

**This ensures:**
- ETA values are available for downstream calorie calculations
- Backend processing continues normally
- Email reports include full ETA details
- No impact on calculation accuracy

## Step Sequence Consistency

### UI Flow
| Step | Title | When Shown |
|------|-------|-----------|
| Paso 3 | Nivel de Actividad Física Diaria | Always |
| Paso 4 | Cálculo Automático de Factores Metabólicos | When `MOSTRAR_ETA_AL_USUARIO = False` |
| Paso 4 | Efecto Térmico de los Alimentos (ETA) | When `MOSTRAR_ETA_AL_USUARIO = True` |
| Paso 5 | Gasto Energético del Ejercicio (GEE) | Always |

### Benefits
1. **No numerical jumps**: Users always see Paso 3 → Paso 4 → Paso 5
2. **Reduced confusion**: Consistent step numbering maintains flow clarity
3. **Methodology protection**: ETA details hidden while maintaining UX
4. **Transparency**: Users informed that automatic processing occurs

## Testing

### Test Coverage
The implementation includes comprehensive tests in `test_step4_placeholder.py`:

1. ✅ MOSTRAR_ETA_AL_USUARIO flag is set to False
2. ✅ if/else structure exists for ETA visibility
3. ✅ Placeholder maintains 'Paso 4' numbering
4. ✅ Placeholder avoids explicit 'ETA' reference in title
5. ✅ Placeholder contains generic automatic calculation message
6. ✅ Placeholder uses collapsed expander (expanded=False)
7. ✅ Backend ETA calculations remain unchanged and unconditional
8. ✅ Placeholder updates progress bar to 70 (Step 4)
9. ✅ Step 5 follows Step 4 placeholder, maintaining sequence

### Existing Tests (No Regressions)
- ✅ `test_psmf_eta_visibility.py` - All tests pass
- ✅ `test_ui_tech_details.py` - All tests pass
- ✅ `test_step4_placeholder.py` - All tests pass

## Visual Comparison

### When MOSTRAR_ETA_AL_USUARIO = False (Current Default)
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Paso 4: Cálculo Automático de Factores Metabólicos    ▼ │  (Collapsed)
└─────────────────────────────────────────────────────────────┘
```

If user expands:
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Paso 4: Cálculo Automático de Factores Metabólicos    ▲ │
├─────────────────────────────────────────────────────────────┤
│ ℹ️ Este paso se calcula automáticamente en función de      │
│ los datos que has proporcionado.                           │
│                                                             │
│ Nuestro sistema procesa tu información de composición      │
│ corporal y nivel de actividad para ajustar de manera       │
│ precisa tus requerimientos energéticos totales.            │
└─────────────────────────────────────────────────────────────┘
```

### When MOSTRAR_ETA_AL_USUARIO = True (For Internal Use)
```
┌─────────────────────────────────────────────────────────────┐
│ 🍽️ Paso 4: Efecto Térmico de los Alimentos (ETA)       ▲ │  (Expanded)
├─────────────────────────────────────────────────────────────┤
│ [Full ETA calculation details and technical information]   │
│ [FFMI factors, body composition analysis, etc.]            │
└─────────────────────────────────────────────────────────────┘
```

## Compliance with Requirements

✅ **Requirement 1**: The `MOSTRAR_ETA_AL_USUARIO` flag continues hiding the ETA details from the UI.
- Implementation: When False, the placeholder is shown instead of ETA details.

✅ **Requirement 2**: Introduce a placeholder message indicating automatic calculation, avoiding explicit 'ETA' reference.
- Implementation: Placeholder title is "Cálculo Automático de Factores Metabólicos" (no "ETA" mention).

✅ **Requirement 3**: The numbered step sequence remains consistent (Step 3, Step 4, Step 5) without numerical jumps.
- Implementation: Placeholder labeled as "Paso 4", maintaining sequence.

✅ **Requirement 4**: Add placeholder only when `MOSTRAR_ETA_AL_USUARIO` is `False`.
- Implementation: Uses if/else structure; placeholder in else clause.

✅ **Requirement 5**: All related backend calculations for ETA remain functional and unaffected.
- Implementation: ETA calculations always run before the if/else UI block; session_state stores values for downstream use.

## Maintainability

### To Show ETA to Users in Future
Simply change the flag at line 27:
```python
MOSTRAR_ETA_AL_USUARIO = True   # Show ETA details to users
```

### To Modify Placeholder Message
Edit the `st.info()` message in the else clause (around line 3597-3602).

### Design Principles
1. **Separation of concerns**: Backend calculations separated from UI display
2. **Flag-based control**: Single flag controls visibility behavior
3. **Consistent patterns**: Follows same pattern as PSMF visibility control
4. **User-friendly**: Generic message doesn't confuse non-technical users

## Related Files
- `streamlit_app.py`: Main implementation (lines 3521-3602)
- `test_step4_placeholder.py`: Comprehensive test suite
- `test_psmf_eta_visibility.py`: Tests for ETA visibility flag behavior
- `PSMF_ETA_VISIBILITY_GUIDE.md`: Guide for visibility flag patterns

## Summary
The Step 4 placeholder successfully maintains UI flow consistency while protecting proprietary ETA methodology. Backend functionality remains unchanged, ensuring calculation accuracy and email report completeness.

# Step 4 Placeholder Implementation

## Overview

This document describes the implementation of a Step 4 placeholder in the MUPAI questionnaire to maintain visual consistency in step numbering when the ETA (Thermal Effect of Food) step is hidden from users.

## Problem Statement

When `MOSTRAR_ETA_AL_USUARIO = False`, the ETA step was completely hidden from the user interface. This caused a visual discontinuity where users would see:

**Before this change:**
```
Paso 1: Composición Corporal ✓
Paso 2: Evaluación Funcional ✓
Paso 3: Nivel de Actividad Física ✓
[Step 4 missing - ETA hidden]
Paso 5: Gasto Energético del Ejercicio ✓
```

This jump from Step 3 to Step 5 was confusing for users.

## Solution

A placeholder expander has been added that appears **only when** `MOSTRAR_ETA_AL_USUARIO = False`. This maintains the numerical sequence while keeping the ETA methodology details hidden.

**After this change:**
```
Paso 1: Composición Corporal ✓
Paso 2: Evaluación Funcional ✓
Paso 3: Nivel de Actividad Física ✓
Paso 4: ETA (collapsed placeholder with informational message) ✓
Paso 5: Gasto Energético del Ejercicio ✓
```

## Implementation Details

### Code Location
File: `streamlit_app.py`, lines 3591-3602

### Code Structure
```python
if MOSTRAR_ETA_AL_USUARIO:
    # Full ETA expander with detailed calculations
    # Note: Uses 🍽️ (food) icon to indicate interactive content
    with st.expander("🍽️ **Paso 4: Efecto Térmico de los Alimentos (ETA)**", expanded=True):
        # ... detailed ETA display ...
else:
    # Placeholder expander (NEW)
    # Note: Uses ℹ️ (info) icon to indicate informational/automatic content
    with st.expander("ℹ️ **Paso 4: Efecto Térmico de los Alimentos (ETA)**", expanded=False):
        st.info("""
        **Paso 4: Calculado automáticamente según la información proporcionada por ti.**
        
        El efecto térmico de los alimentos (ETA) representa la energía que tu cuerpo gasta 
        en digerir y procesar los alimentos. Este valor se calcula automáticamente en función 
        de tu composición corporal y se integra en tus resultados finales.
        """)
```

**Icon Distinction**: The full ETA display uses 🍽️ (food/plate) to indicate interactive content with detailed calculations, while the placeholder uses ℹ️ (information symbol) to signal that this is informational/automatic content requiring no user input.

### Key Features

1. **Conditional Display**: Placeholder shown only when `MOSTRAR_ETA_AL_USUARIO = False`
2. **Collapsed by Default**: Uses `expanded=False` to minimize visual clutter
3. **Informational Icon**: Uses ℹ️ emoji instead of 🍽️ to indicate informational nature
4. **Clear Message**: Informs users that the calculation happens automatically
5. **Consistent Numbering**: Maintains "Paso 4" label to preserve sequence

## Visual Comparison

### When MOSTRAR_ETA_AL_USUARIO = False (Current Configuration)

#### Expander List View:
```
📊 Paso 1: Composición Corporal y Antropometría [expanded]
💪 Paso 2: Evaluación Funcional y Nivel de Entrenamiento [expanded]
🚶 Paso 3: Nivel de Actividad Física Diaria [expanded]
ℹ️ Paso 4: Efecto Térmico de los Alimentos (ETA) [collapsed] ← NEW PLACEHOLDER
🏋️ Paso 5: Gasto Energético del Ejercicio (GEE) [expanded]
```

#### Placeholder Content (when clicked):
```
┌─────────────────────────────────────────────────────────────┐
│ ℹ️ Paso 4: Calculado automáticamente según la información   │
│    proporcionada por ti.                                    │
│                                                             │
│ El efecto térmico de los alimentos (ETA) representa la     │
│ energía que tu cuerpo gasta en digerir y procesar los      │
│ alimentos. Este valor se calcula automáticamente en        │
│ función de tu composición corporal y se integra en tus     │
│ resultados finales.                                         │
└─────────────────────────────────────────────────────────────┘
```

### When MOSTRAR_ETA_AL_USUARIO = True

#### Expander List View:
```
📊 Paso 1: Composición Corporal y Antropometría [expanded]
💪 Paso 2: Evaluación Funcional y Nivel de Entrenamiento [expanded]
🚶 Paso 3: Nivel de Actividad Física Diaria [expanded]
🍽️ Paso 4: Efecto Térmico de los Alimentos (ETA) [expanded] ← FULL DETAILS
🏋️ Paso 5: Gasto Energético del Ejercicio (GEE) [expanded]
```

## Backend Behavior (Unchanged)

The implementation is **purely a UI change**. Backend behavior remains intact:

1. **ETA Calculations**: Always run unconditionally, regardless of the flag
2. **Session State**: ETA results always stored in `st.session_state.eta`
3. **Email Reports**: Always include complete ETA technical details
4. **Downstream Usage**: GE and other calculations can always access ETA values

## Testing

### Test Coverage

A comprehensive test suite (`test_step4_placeholder.py`) validates:

1. ✅ Placeholder exists as else clause to `MOSTRAR_ETA_AL_USUARIO`
2. ✅ Placeholder is properly conditional
3. ✅ Placeholder is labeled as "Paso 4"
4. ✅ Placeholder contains appropriate informational message
5. ✅ Step sequence is maintained (no skip from 3 to 5)
6. ✅ Both conditional branches have "Paso 4"
7. ✅ Placeholder expander is collapsed by default
8. ✅ ETA calculations still run unconditionally

### Regression Testing

All existing tests continue to pass:
- ✅ `test_psmf_eta_visibility.py` (13/13 tests passed)
- ✅ `test_step4_placeholder.py` (8/8 tests passed)

## Design Rationale

### Why a Placeholder?

1. **User Experience**: Avoids confusion from skipped step numbers
2. **Transparency**: Users know something happens at Step 4
3. **Consistency**: Maintains expected sequence 1→2→3→4→5
4. **Minimal Disclosure**: Doesn't reveal proprietary methodology details

### Why Collapsed by Default?

1. **Non-intrusive**: Doesn't distract from main flow
2. **Optional Detail**: Users can expand if curious
3. **Visual Hierarchy**: Expanded steps are interactive, collapsed are informational

### Why Keep "ETA" in the Title?

1. **Consistency**: Matches the full expander title when flag is True
2. **Search/Find**: Users can Ctrl+F for "ETA" in both modes
3. **Semantic Meaning**: Title explains what's being calculated

## Migration Notes

### Breaking Changes
**None.** This is a purely additive change.

### Flag Behavior
No changes to flag behavior:
- `MOSTRAR_ETA_AL_USUARIO = False`: Hide detailed ETA UI (show placeholder)
- `MOSTRAR_ETA_AL_USUARIO = True`: Show detailed ETA UI (hide placeholder)

### Email Reports
**No changes.** Email reports always include full ETA details regardless of UI flags.

## Maintenance

### Future Considerations

1. **Message Updates**: If the placeholder message needs updating, modify lines 3595-3601
2. **Icon Changes**: Currently uses ℹ️, can be changed to any emoji/icon
3. **Expansion Default**: Currently `expanded=False`, can be changed if needed
4. **Additional Flags**: This pattern can be applied to other hidden methodologies

### Related Files

- **Implementation**: `streamlit_app.py` (lines 3591-3602)
- **Tests**: `test_step4_placeholder.py`
- **Documentation**: This file (`STEP4_PLACEHOLDER_IMPLEMENTATION.md`)
- **Related**: `PSMF_ETA_VISIBILITY_GUIDE.md` (overall visibility system)

## Summary

This implementation successfully:
- ✅ Maintains visual step numbering continuity
- ✅ Provides user transparency without revealing methodology details
- ✅ Preserves all backend calculation logic
- ✅ Passes all tests (existing + new)
- ✅ Requires zero configuration changes
- ✅ Is minimal and surgical (12 lines of code)

The placeholder ensures users see a complete sequence from Step 1 to Step 5, avoiding confusion while maintaining the proprietary nature of the ETA methodology.

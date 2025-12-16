# UI Hidden Logic Implementation Guide

## Overview

This document describes the implementation of hiding technical calculation details (`dias_fuerza`, `kcal_sesion`, `promedio_diario`) from the client-visible interface while maintaining their presence in internal email reports.

## Problem Statement

The aim was to enhance the user interface of `streamlit_app.py` so that important calculation-related logic, including variables like `dias_fuerza`, `kcal_sesion`, and `promedio_diario`, remains intact and hidden from the client's visible interface.

### Requirements

1. **No interruption to existing email functionality** - Email reports must continue to include these variables in reports sent internally
2. **Client-friendly messaging** - Modify the blue message to be more general without revealing technical details
3. **Debugging capability** - Maintain ability to show technical details via `SHOW_TECH_DETAILS` toggle for internal review

## Implementation

### Changes Made

#### 1. Hidden Metrics Display (Lines 3650-3674)

**Before:**
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Días/semana", f"{dias_fuerza} días", ...)
with col2:
    st.metric("Gasto/sesión", f"{kcal_sesion} kcal", ...)
with col3:
    st.metric("Promedio diario", f"{gee_prom_dia:.0f} kcal/día", ...)

st.markdown(f"""
    <div>... Technical message with {nivel_gee} and {current_level} ...</div>
""")
```

**After:**
```python
# Display metrics conditionally based on SHOW_TECH_DETAILS flag
if SHOW_TECH_DETAILS:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Días/semana", f"{dias_fuerza} días", ...)
    with col2:
        st.metric("Gasto/sesión", f"{kcal_sesion} kcal", ...)
    with col3:
        st.metric("Promedio diario", f"{gee_prom_dia:.0f} kcal/día", ...)
    
    st.markdown(f"""
        <div>... Technical message with {nivel_gee} and {current_level} ...</div>
    """)
else:
    # Client-friendly message without technical details
    st.markdown("""
        <div>💡 <strong>Cálculo personalizado:</strong> En base a tu nivel global 
        de entrenamiento – que combina desarrollo muscular, rendimiento funcional 
        y experiencia – se han realizado los cálculos personalizados.</div>
    """)
```

#### 2. Email Report Verification

Verified that email generation (lines 4378-4545) continues to include all technical variables:

```python
tabla_resumen += f"""
...
- Días entreno/semana: {dias_fuerza}
- Gasto por sesión: {kcal_sesion} kcal
- GEE promedio diario: {gee_prom_dia:.0f} kcal
...
"""
```

**Result:** ✅ Email functionality unchanged - all technical variables remain in reports.

### What Clients See (SHOW_TECH_DETAILS = False)

**Visible:**
- Training frequency slider (input remains visible for data collection)
- General client-friendly message about personalized calculations

**Hidden:**
- Technical metrics (días/semana, gasto/sesión, promedio diario)
- Detailed technical explanations with specific values
- Technical terminology and calculation details

### What Internal Testing Sees (SHOW_TECH_DETAILS = True)

**Visible:**
- All technical metrics with values
- Detailed technical explanations
- Specific calculation details (nivel_gee, current_level)
- Complete debugging information

### Client-Friendly Message

**Old message (technical):**
```
Tu gasto por sesión (350 kcal/sesión) se basa en tu nivel global de 
entrenamiento (Intermedio), que combina desarrollo muscular, rendimiento 
funcional y experiencia. Esto proporciona una estimación más precisa de 
tu gasto energético real.
```

**New message (client-friendly):**
```
En base a tu nivel global de entrenamiento – que combina desarrollo 
muscular, rendimiento funcional y experiencia – se han realizado los 
cálculos personalizados.
```

**Improvements:**
- ✅ No specific technical values revealed
- ✅ Still explains the methodology at high level
- ✅ Professional and informative tone
- ✅ Focuses on the benefit (personalized calculations) rather than technical details

## Testing

### Test Suite

Created `test_ui_hidden_logic.py` to validate:

1. ✅ Metrics are conditionally displayed based on SHOW_TECH_DETAILS flag
2. ✅ Blue message updated to client-friendly version
3. ✅ Email generation includes all technical variables
4. ✅ Calculations continue to run correctly
5. ✅ Flag is set to False by default

### Test Results

```bash
$ python test_ui_hidden_logic.py
Testing UI hidden logic implementation...

✓ SHOW_TECH_DETAILS is set to False (client mode)
✓ dias_fuerza metric is conditionally displayed based on SHOW_TECH_DETAILS
✓ Blue message updated to client-friendly version
✓ Client-friendly message is shown when SHOW_TECH_DETAILS=False
✓ Email generation includes dias_fuerza
✓ Email generation includes kcal_sesion
✓ Email generation includes promedio_diario (gee_prom_dia)
✓ dias_fuerza calculation and session state storage exist
✓ kcal_sesion calculation and session state storage exist
✓ gee_prom_dia calculation and session state storage exist

✅ All tests passed!
```

### Integration Tests

All existing tests continue to pass:
- ✅ `test_ui_tech_details.py` - SHOW_TECH_DETAILS implementation
- ✅ `test_ui_rendering_modes.py` - UI rendering modes
- ✅ `test_flow_state.py` - Flow state management

## Verification Checklist

- [x] Technical metrics hidden from client UI when SHOW_TECH_DETAILS=False
- [x] Blue message updated to be more general and client-friendly
- [x] Email reports include all technical variables (dias_fuerza, kcal_sesion, gee_prom_dia)
- [x] Calculations continue to run correctly in background
- [x] Session state properly stores all values
- [x] SHOW_TECH_DETAILS toggle works for internal debugging
- [x] All existing tests pass
- [x] New test created and passing (test_ui_hidden_logic.py)
- [x] Documentation updated (SHOW_TECH_DETAILS_GUIDE.md)

## Usage

### For Production (Client-Facing)
```python
SHOW_TECH_DETAILS = False  # Default setting
```

### For Internal Testing
```python
SHOW_TECH_DETAILS = True  # Set this temporarily for debugging
```

## Files Modified

1. **streamlit_app.py** (Lines 3650-3674)
   - Added conditional display of metrics
   - Updated blue message with client-friendly version

2. **SHOW_TECH_DETAILS_GUIDE.md**
   - Added documentation for hidden training frequency metrics
   - Updated recent changes section

3. **test_ui_hidden_logic.py** (New file)
   - Created comprehensive test suite for hidden logic implementation

## Benefits

1. **Client Experience**
   - Cleaner, less technical interface
   - Focus on actionable information
   - Professional presentation without overwhelming details

2. **Maintainability**
   - Single toggle controls all technical details
   - Easy to debug with SHOW_TECH_DETAILS=True
   - Clear separation between client UI and backend logic

3. **Compliance**
   - Email reports maintain all technical details for contractual obligations
   - Internal documentation preserved
   - Complete audit trail maintained

## Future Considerations

Potential enhancements:
- Add more variables to conditional display as needed
- Implement multiple detail levels (DETAIL_LEVEL = 0/1/2/3)
- Create admin panel for dynamic flag control
- Add logging to track which mode is active

---

**Version:** 1.0  
**Implementation Date:** 2025-12-16  
**Status:** ✅ Complete and Tested  
**Maintained By:** Development Team

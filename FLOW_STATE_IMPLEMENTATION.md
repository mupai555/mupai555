# Flow State Management Implementation

## Overview

This document describes the flow state management system implemented in `streamlit_app.py` to conditionally render technical outputs based on the application's flow phase.

## Purpose

Prevent exposure of intermediate outputs and technical reasoning to users during the intake phase, while maintaining all calculations in the background for downstream logic.

## Flow Phases

The application supports three flow phases:

1. **`intake`** (default) - Initial data collection phase
   - User inputs personal information
   - Technical outputs are hidden
   - Calculations still run in background

2. **`review`** (reserved for future enhancement)
   - Intermediate review phase
   - Not currently used in application flow
   - Available for future multi-phase workflows

3. **`final`** - Complete evaluation phase
   - All technical outputs are displayed
   - Full FFMI/FMI classifications shown
   - ETA/GEAF calculation details visible
   - Plan comparison breakdowns available

## Current Flow Transition

```
[intake] ---> User clicks "COMENZAR EVALUACIÓN" ---> [final]
```

The application currently transitions directly from `intake` to `final` phase when the user completes the intake form and clicks the "COMENZAR EVALUACIÓN" button.

## API Reference

### Core Functions

#### `get_flow_phase()`
Returns the current flow phase from session state.
- **Returns**: `str` - One of: 'intake', 'review', 'final'
- **Default**: 'intake' if undefined

#### `set_flow_phase(phase)`
Sets the current flow phase with validation.
- **Parameters**: 
  - `phase` (str): Must be 'intake', 'review', or 'final'
- **Raises**: `ValueError` if invalid phase provided

### Helper Functions

#### `should_render_technical()`
Check if technical outputs should be displayed.
- **Returns**: `bool` - True only in 'final' phase
- **Use case**: Inline conditional checks

```python
if should_render_technical():
    st.write("Technical details...")
```

#### `should_hide_during_intake()`
Check if output should be hidden during intake.
- **Returns**: `bool` - True if NOT in 'intake' phase
- **Use case**: Inline conditional checks

```python
if should_hide_during_intake():
    st.write("Review phase content...")
```

### Wrapper Decorators

#### `@render_user_safe`
Components that are **always** safe to show to users.

**Use for:**
- Basic user inputs and forms
- High-level summaries and recommendations
- Non-technical metrics (weight, height, age, etc.)

**Example:**
```python
@render_user_safe
def show_basic_info():
    st.write("Your weight:", weight)
    st.write("Your height:", height)
```

#### `@render_if_final`
**TECHNICAL/PRO-ONLY** components shown only in 'final' phase.

**Use for:**
- FFMI detailed calculations and classifications
- FMI technical metrics and formulas
- ETA calculation methodology and factors
- GEAF detailed breakdowns
- Technical plan comparisons with formulas
- Implementation details and reasoning

**Example:**
```python
@render_if_final
def show_ffmi_technical_details():
    st.write("FFMI calculation formula:")
    st.write("FFMI = (MLG / height²) + 6.3 * (1.8 - height)")
    st.write("Your FFMI:", ffmi)
```

#### `@hide_during_intake`
Components hidden **only** during 'intake' phase.

**Use for:**
- Future: Intermediate results during review
- Future: Summary metrics visible during review but not intake

**Note:** Currently reserved for future enhancement as application doesn't use 'review' phase.

**Example:**
```python
@hide_during_intake
def show_intermediate_results():
    st.write("Intermediate calculation:", value)
```

## Implementation Pattern

### Critical Pattern: Separate Calculation from Display

**✅ CORRECT:**
```python
# Calculation ALWAYS runs (outside conditional)
eta = 1.15 if grasa_corregida <= 10 else 1.10
st.session_state.eta = eta

# Display is CONDITIONAL
if should_render_technical():
    st.write(f"ETA Factor: {eta}")
    st.write("Methodology: Based on body fat percentage...")
```

**❌ INCORRECT:**
```python
# Don't wrap calculations inside conditional
if should_render_technical():
    eta = 1.15 if grasa_corregida <= 10 else 1.10
    st.session_state.eta = eta  # ❌ Won't run during intake!
    st.write(f"ETA Factor: {eta}")
```

### Why This Matters

Calculations must always run because:
1. Downstream logic depends on calculated values (e.g., calorie calculations need ETA)
2. Session state needs to be populated for other components
3. Only the *display* of technical details should be suppressed, not the calculations themselves

## Refactored Sections

The following output sections have been wrapped with conditional rendering:

### 1. FFMI Metrics and Classifications
**Location:** Lines 2360-2463

**What's Conditional:**
- FFMI mode interpretation badges (GREEN/AMBER/RED)
- Detailed FFMI formula and calculation steps
- Classification explanations by sex
- Progress bars and development percentages
- Reference ranges and thresholds
- Biological differences between sexes

**What Always Runs:**
- FFMI calculation (`calcular_ffmi()`)
- Mode determination (`obtener_modo_interpretacion_ffmi()`)
- Classification logic (`clasificar_ffmi()`)

### 2. FMI and Classifications
**Location:** Lines 2510-2562

**What's Conditional:**
- FMI classification badges (Bajo/Normal/Elevado/Muy elevado)
- Reference ranges by sex
- Technical explanation of FMI
- Additional mode explanations

**What Always Runs:**
- FMI calculation (`calcular_fmi()`)
- Value storage in variables

### 3. ETA (Efecto Térmico) Calculations
**Location:** Lines 3208-3257

**What's Conditional:**
- "Determinación automática del ETA" heading
- ETA factor display and badge
- Technical explanation ("¿Qué es el ETA?")
- Percentage increase display

**What Always Runs:**
- ETA value calculation based on body fat and sex
- Session state updates (eta, eta_desc, eta_color)

### 4. GEAF Factor Display
**Location:** Lines 3196-3202

**What's Conditional:**
- Success message showing GEAF factor
- Multiplier explanation
- Percentage increase calculation

**What Always Runs:**
- GEAF calculation (`obtener_geaf()`)
- Session state updates

### 5. Plan Comparisons (Traditional vs PSMF)
**Location:** Lines 3463-3507

**What's Conditional:**
- "Comparativa de planes" heading
- Side-by-side plan cards
- Detailed metrics (deficit %, calories, loss rate)
- Tier information and technical parameters
- Protein/fat/carb breakdowns with multipliers

**What Always Runs:**
- All plan calculations
- PSMF tier determination
- Calorie and macro calculations

## Testing

### Test Suite: `test_flow_state.py`

Comprehensive test coverage with 18 tests:

**Test Categories:**
1. Flow State Management (5 tests)
   - Default phase initialization
   - Phase transitions
   - Invalid phase validation
   
2. Helper Functions (6 tests)
   - `should_render_technical()` behavior across phases
   - `should_hide_during_intake()` behavior across phases
   
3. Conditional Rendering Wrappers (4 tests)
   - `@render_user_safe` always renders
   - `@render_if_final` only in final phase
   - `@hide_during_intake` hides only in intake
   - Wrapper with function arguments
   
4. Fallback Behavior (1 test)
   - Undefined flow phase defaults to 'intake'
   
5. Real-World Scenarios (2 tests)
   - Complete intake-to-final workflow
   - Calculations persist across phases

**Running Tests:**
```bash
python test_flow_state.py
```

**Expected Output:**
```
Test Results: 18/18 passed
✅ All tests passed!
```

## Migration Guide

### Adding New Conditional Outputs

When adding new technical outputs to the application:

1. **Identify if output is technical or user-facing**
   - Technical: Implementation details, formulas, calculation steps
   - User-facing: Basic results, high-level recommendations

2. **Choose appropriate pattern:**

   **For technical outputs:**
   ```python
   if should_render_technical():
       st.write("Technical explanation...")
       st.write("Formula: x = y + z")
   ```

   **For user-facing outputs:**
   ```python
   # No wrapper needed - always show
   st.write("Your result:", value)
   ```

3. **Ensure calculations run unconditionally:**
   ```python
   # ✅ Calculation outside conditional
   result = calculate_something(params)
   st.session_state.result = result
   
   # Display is conditional
   if should_render_technical():
       st.write("Result:", result)
   ```

### Future Enhancement: Adding Review Phase

To implement a review phase:

1. **Add transition button:**
   ```python
   if st.button("Review Results"):
       set_flow_phase("review")
   ```

2. **Use `@hide_during_intake` wrapper:**
   ```python
   @hide_during_intake
   def show_review_content():
       st.write("Review phase content")
   ```

3. **Add final transition:**
   ```python
   if st.button("Complete Assessment"):
       set_flow_phase("final")
   ```

## Best Practices

1. ✅ **Always separate calculation from display**
2. ✅ **Use `should_render_technical()` for inline checks**
3. ✅ **Document why outputs are conditional**
4. ✅ **Test across all phases**
5. ✅ **Store calculated values in session_state**
6. ❌ **Don't wrap calculations in conditionals**
7. ❌ **Don't skip phase validation**
8. ❌ **Don't assume phase exists**

## Troubleshooting

### Issue: Technical outputs not showing

**Solution:**
```python
# Check current phase
current_phase = get_flow_phase()
print(f"Current phase: {current_phase}")

# Ensure transition happened
if current_phase != "final":
    set_flow_phase("final")
```

### Issue: Calculations not available downstream

**Problem:** Calculation wrapped inside conditional

**Solution:** Move calculation outside:
```python
# ❌ WRONG
if should_render_technical():
    value = calculate()  # Won't run during intake!

# ✅ CORRECT
value = calculate()  # Always runs
if should_render_technical():
    st.write(value)  # Display is conditional
```

### Issue: ValueError on phase transition

**Cause:** Invalid phase name

**Solution:**
```python
# ❌ WRONG
set_flow_phase("complete")  # Not valid!

# ✅ CORRECT
set_flow_phase("final")  # Use 'intake', 'review', or 'final'
```

## Performance Impact

**Minimal to None:**
- Calculations run regardless of phase (no change)
- Only display code is conditional (negligible overhead)
- Boolean checks are O(1) operations
- No database queries or external API calls affected

## Security Considerations

**Information Flow Control:**
- Prevents premature exposure of technical reasoning
- Users only see appropriate level of detail for their phase
- No sensitive calculation details leaked during intake
- Professional outputs reserved for final phase

**Data Integrity:**
- All calculations persist in session state
- No data loss from conditional rendering
- Downstream logic unaffected by display suppression

## Future Enhancements

1. **Multi-step Review Phase**
   - Add intermediate review step
   - Show partial results for validation
   - Allow corrections before final output

2. **Role-Based Display**
   - Different phases for different user roles
   - Admin sees all technical details
   - Regular users see simplified output

3. **Progressive Disclosure**
   - Gradual reveal of complexity
   - "Show more details" expansion
   - Adaptive to user expertise level

4. **Phase History Tracking**
   - Log phase transitions
   - Analytics on user flow
   - Identify drop-off points

## References

- **Implementation:** `streamlit_app.py` lines 203-327
- **Tests:** `test_flow_state.py`
- **Examples:** FFMI section (2360-2463), ETA section (3208-3257)
- **Problem Statement:** Issue requirements for conditional output rendering

## Support

For questions or issues with the flow state system:
1. Check this documentation
2. Review test cases in `test_flow_state.py`
3. Examine existing implementations (FFMI, FMI, ETA, GEAF sections)
4. Run tests to validate behavior: `python test_flow_state.py`

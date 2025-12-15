# SHOW_TECH_DETAILS Flag Guide

## Overview

The `SHOW_TECH_DETAILS` global flag controls the visibility of technical details in the Streamlit UI while keeping all backend calculations and email report generation completely unchanged.

## Location

The flag is defined at the top of `streamlit_app.py`:

```python
# Global flag to control visibility of technical details in UI
# When False: Hide technical calculations, formulas, factors, and detailed breakdowns
# When True: Show all technical details for internal testing and validation
# Note: Email report generation is ALWAYS unaffected by this flag
SHOW_TECH_DETAILS = False
```

## Usage

### For Client-Facing Deployment (Production)
**Set:** `SHOW_TECH_DETAILS = False`

**What is hidden:**
- PSMF technical details:
  - Tier numbers and base protein calculations
  - Protein/fat/carb gram amounts and formulas
  - Multipliers, thresholds, and carb caps
  - Technical calculations and intermediate values
  
- Traditional Plan technical details:
  - Detailed macro breakdown with formulas
  - Percentage calculations and base protein sources
  - MLG vs total weight technical explanations
  - Detailed calorie/macro distribution tables

- FFMI/FMI technical details:
  - Detailed FFMI calculations and formulas
  - Mode interpretations (GREEN/AMBER/RED)
  - FMI values and classifications
  - Technical thresholds and potential calculations

- ETA (Thermic Effect) technical details:
  - ETA factor values (1.10, 1.12, 1.15)
  - Threshold ranges and criteria
  - Technical explanations of calculation

- GEAF (Activity Factor) technical details:
  - GEAF factor values
  - Multiplier details

**What remains visible:**
- Nivel global de entrenamiento (training level)
- Plan selection (Tradicional vs PSMF)
- Calorías objetivo (target calories)
- Macros finales (P/F/C) in simple format
- General warnings and safety recommendations
- High-level health classifications

### For Internal Testing/Validation
**Set:** `SHOW_TECH_DETAILS = True`

**What is shown:**
- All technical details and calculations
- Detailed formulas and intermediate values
- Classification thresholds and criteria
- Technical explanations and methodology
- Detailed macro breakdowns with percentages
- All factors and multipliers

## Email Report

**IMPORTANT:** The email report generation (`tabla_resumen`) is **COMPLETELY UNAFFECTED** by this flag. 

All technical details are ALWAYS included in the email sent to administrators, regardless of the flag value. This ensures:
- Contractual obligations are maintained
- Complete technical documentation is preserved
- Internal records remain comprehensive

## Testing

Run the test suite to validate the implementation:

```bash
# Basic validation test
python test_ui_tech_details.py

# Comprehensive integration test
python test_ui_rendering_modes.py

# Verify existing functionality
python test_ffmi_mode.py
python test_psmf_tiers.py
```

All tests should pass in both modes (flag = True and flag = False).

## Helper Functions

Two helper functions are available for conditional rendering:

### render_metric()
```python
render_metric(label, value, delta=None, help_text=None)
```
Conditionally renders a Streamlit metric based on the flag.

**Example:**
```python
render_metric("FFMI", f"{ffmi:.2f}", help_text="Fat-Free Mass Index")
# Only displays when SHOW_TECH_DETAILS = True
```

### render_technical_block()
```python
render_technical_block(render_func)
```
Conditionally renders a block of technical content.

**Example:**
```python
render_technical_block(lambda: st.markdown("### Technical Details..."))
# Only executes when SHOW_TECH_DETAILS = True
```

## Implementation Principles

1. **Separation of Concerns:** UI display logic is separated from calculation logic
2. **Calculations Always Run:** All calculations execute regardless of flag value
3. **Email Unchanged:** Email report generation is never affected
4. **Single Point of Control:** One flag controls all conditional UI rendering
5. **Easy Toggle:** Change flag value to switch between modes instantly

## Verification Checklist

Before deployment, verify:
- [ ] `SHOW_TECH_DETAILS = False` is set
- [ ] All tests pass (`test_ui_tech_details.py`, `test_ui_rendering_modes.py`)
- [ ] App runs without errors
- [ ] Client-facing UI shows only high-level results
- [ ] Email report still contains all technical details
- [ ] Calculations produce correct results in both modes

## Troubleshooting

**Issue:** Technical details still showing
- **Solution:** Verify `SHOW_TECH_DETAILS = False` at top of file
- **Solution:** Restart Streamlit app to reload changes

**Issue:** Calculations not working
- **Solution:** Check that calculations are outside conditional blocks
- **Solution:** Run tests to identify the issue

**Issue:** Email missing details
- **Solution:** Verify email generation doesn't use the flag (it shouldn't)
- **Solution:** Check `tabla_resumen` construction is unchanged

## Code Review Points

When reviewing changes:
1. Verify SHOW_TECH_DETAILS is only used in UI rendering code
2. Ensure calculations happen unconditionally
3. Confirm email generation section doesn't use the flag
4. Check that high-level outputs remain visible
5. Validate test coverage

## Future Enhancements

Potential future improvements:
- Add flag to Streamlit secrets for remote control
- Create admin panel to toggle flag dynamically
- Add logging to track which mode is active
- Implement different levels of detail (e.g., DETAIL_LEVEL = 0/1/2)

---

**Version:** 1.0  
**Last Updated:** 2025-12-15  
**Maintained By:** Development Team

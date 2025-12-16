# PSMF and ETA Visibility Comparison

This document shows what users see vs. what administrators receive in the email reports.

## With Flags Set to False (Production Mode)

### User Interface (What Users See)

**PSMF Section:**
- ❌ No PSMF candidate warning box
- ❌ No PSMF plan selection option
- ❌ No PSMF technical details (tier, multiplier, protein/fat/carb calculations)
- ❌ No PSMF comparison chart
- ❌ No PSMF warnings
- ✅ Only see "Plan Tradicional" option

**ETA Section:**
- ❌ No ETA expander section visible
- ❌ No ETA factor display (1.10, 1.12, 1.15)
- ❌ No ETA methodology explanation
- ✅ Calculations still run in background

**Result:**
- Clean, simplified interface
- No proprietary methodology visible
- Focus on final recommendations only

### Email Report (What Administrators Receive)

**PSMF Section in Email:**
```
⚡ PROTOCOLO PSMF ACTUALIZADO (APLICABLE/NO APLICABLE):
- Calorías: 1200 kcal/día
- Criterio de aplicabilidad: PSMF recomendado por % grasa >23%
- Proteína: 120.0g (480 kcal) = 40.0%
- Grasas: 50.0g (450 kcal) = 37.5%
- Carbohidratos: 30.0g (120 kcal) = 10.0% (solo vegetales fibrosos)
- Multiplicador calórico: 8.3 (perfil: alto % grasa)
- Déficit estimado: ~50%
- Pérdida esperada: 0.8-1.2 kg/semana
- Sostenibilidad: BAJA - Máximo 6-8 semanas
- Duración recomendada: 6-8 semanas con supervisión médica obligatoria
- Suplementación necesaria: Multivitamínico, omega-3, electrolitos, magnesio
- Monitoreo requerido: Análisis de sangre regulares
```

**ETA Section in Email:**
```
🔥 EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):
- Factor ETA: 1.12
- Criterio aplicado: ETA medio (magro, 11-20% grasa)
- Justificación: Basado en % grasa corporal (15.5%) y sexo (Hombre)
```

**Result:**
- Complete technical details
- Full methodology visible
- All calculation parameters included
- Comprehensive audit trail

## With Flags Set to True (Testing Mode)

### User Interface (What Users See)

**PSMF Section:**
- ✅ PSMF candidate warning box visible
- ✅ Can select between "Plan Tradicional" and "Protocolo PSMF"
- ✅ See tier of adiposity
- ✅ See protein, fat, carb calculations
- ✅ See multiplier and projected weight loss
- ✅ See full technical details

**ETA Section:**
- ✅ ETA expander visible
- ✅ See ETA factor (1.10, 1.12, or 1.15)
- ✅ See ranges and thresholds
- ✅ See methodology explanation

**Result:**
- Full methodology visible to users
- Can select PSMF protocol
- Complete transparency
- Useful for testing and validation

### Email Report
- Same as with flags False
- Always contains complete details

## Comparison Table

| Element | Flags = False (User Sees) | Flags = False (Email) | Flags = True (User Sees) | Flags = True (Email) |
|---------|---------------------------|----------------------|-------------------------|---------------------|
| PSMF Candidate Warning | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| PSMF Plan Selection | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| PSMF Tier Info | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| PSMF Multiplier | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| PSMF Macros Detail | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| ETA Expander | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| ETA Factor | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| ETA Ranges | ❌ Hidden | ✅ Included | ✅ Visible | ✅ Included |
| Backend Calculations | ✅ Run | ✅ Run | ✅ Run | ✅ Run |
| Session State Storage | ✅ Stored | ✅ Stored | ✅ Stored | ✅ Stored |

## Key Points

1. **Flags = False (Production)**:
   - Users see simplified interface
   - Methodology is protected
   - Administrators get full details via email
   - Backend continues to work normally

2. **Flags = True (Testing)**:
   - Complete transparency for validation
   - Users can see and select PSMF
   - Useful for internal testing
   - Email reports unchanged

3. **Backend Behavior (Always)**:
   - PSMF calculations always run
   - ETA calculations always run
   - Results stored in session_state
   - Available for downstream processing
   - Used in calorie recommendations

4. **Email Reports (Always)**:
   - Never affected by visibility flags
   - Always contain complete technical details
   - Full PSMF methodology included
   - Full ETA methodology included
   - Maintain audit trail

## Usage Scenarios

### Scenario 1: Production Deployment
```python
MOSTRAR_PSMF_AL_USUARIO = False
MOSTRAR_ETA_AL_USUARIO = False
```
- Protect IP from end users
- Clean user interface
- Full admin visibility via email

### Scenario 2: Internal Testing
```python
MOSTRAR_PSMF_AL_USUARIO = True
MOSTRAR_ETA_AL_USUARIO = True
```
- Validate calculations
- Test user experience with PSMF
- Debug methodology issues

### Scenario 3: Selective Visibility
```python
# Show ETA but hide PSMF
MOSTRAR_PSMF_AL_USUARIO = False
MOSTRAR_ETA_AL_USUARIO = True

# Or vice versa
MOSTRAR_PSMF_AL_USUARIO = True
MOSTRAR_ETA_AL_USUARIO = False
```
- Granular control
- Progressive feature rollout
- A/B testing possibilities

## Verification Checklist

Before deploying to production, verify:

- [ ] Flags are set to `False` in streamlit_app.py (lines 25-26)
- [ ] Run `python test_psmf_eta_visibility.py` - all tests pass
- [ ] Test UI manually - no PSMF/ETA details visible
- [ ] Check backend: `st.session_state.psmf_recs` is populated
- [ ] Check backend: `st.session_state.eta` is set correctly
- [ ] Generate test email - verify full PSMF details present
- [ ] Generate test email - verify full ETA details present
- [ ] Verify calorie recommendations are accurate
- [ ] Confirm macros calculation uses correct values

## Troubleshooting

**Issue**: PSMF/ETA still showing to users
- **Check**: Verify flags = False in lines 25-26
- **Fix**: Restart Streamlit app after changing flags

**Issue**: Calculations not working
- **Check**: Run tests to verify calculations execute
- **Fix**: Ensure calculations are outside conditional blocks

**Issue**: Email missing details
- **Check**: Email section should NOT use visibility flags
- **Fix**: Verify tabla_resumen construction (lines 4480-4620)

---

**Version**: 1.0  
**Date**: 2025-12-16  
**Status**: Production Ready

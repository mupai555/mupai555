# Visual Guide: Waist Circumference & Decimal Height Features

## Before vs After Comparison

### 1. Height Input Field

#### BEFORE:
```
📏 Estatura (cm)
[  170  ]  ⬆️⬇️
(Integer only, e.g., 170)
```

#### AFTER:
```
📏 Estatura (cm)
[  170.5  ]  ⬆️⬇️
(Allows decimals, e.g., 165.5)
Help: Medida sin zapatos (permite decimales, ej: 165.5)
```

---

### 2. New Waist Circumference Input

#### ADDED:
```
📏 Circunferencia de cintura (cm, opcional)
[  85.0  ]  ⬆️⬇️
Range: 0.0 - 200.0 cm
Step: 0.1 cm

Help: Medida de la circunferencia de cintura a la altura del ombligo. 
Este dato se usa para calcular el Ratio Cintura-Estatura (WHtR), 
un indicador de salud metabólica. Se guarda y se incluye en el 
reporte, pero no afecta los cálculos de calorías/macros.
```

---

### 3. UI Metrics Display

#### BEFORE (only showing existing optional metrics):
```
┌─────────────────────┬─────────────────────┐
│ Masa muscular (%)   │ Grasa visceral      │
│     42.5%           │    8 (Saludable)    │
└─────────────────────┴─────────────────────┘
```

#### AFTER (with waist data entered):
```
┌─────────────┬────────────────┬──────────────────┬─────────────────────┐
│ Masa        │ Grasa          │ Circunferencia   │ Ratio Cintura-      │
│ muscular    │ visceral       │ cintura          │ Estatura (WHtR)     │
├─────────────┼────────────────┼──────────────────┼─────────────────────┤
│  42.5%      │  8             │  85.0 cm         │  0.500              │
│             │  (Saludable)   │                  │  Saludable          │
│             │                │                  │  (bajo riesgo)      │
└─────────────┴────────────────┴──────────────────┴─────────────────────┘
```

---

### 4. Email Summary (Main Report)

#### BEFORE:
```
=====================================
ANTROPOMETRÍA Y COMPOSICIÓN:
=====================================
- Peso: 75 kg
- Estatura: 170 cm
- IMC: 25.9 kg/m²
- % Grasa corregido (DEXA): 18.5%
- % Masa muscular: 42.5%
- Grasa visceral (nivel): 8
- Masa Libre de Grasa: 61.1 kg
- Masa Grasa: 13.9 kg
```

#### AFTER:
```
=====================================
ANTROPOMETRÍA Y COMPOSICIÓN:
=====================================
- Peso: 75 kg
- Estatura: 170.0 cm                           ← Shows decimal
- IMC: 25.9 kg/m²
- % Grasa corregido (DEXA): 18.5%
- % Masa muscular: 42.5%
- Grasa visceral (nivel): 8
- Circunferencia de cintura: 85.0 cm          ← NEW
- Ratio Cintura-Estatura (WHtR): 0.500        ← NEW
  (Riesgo incrementado)                        ← NEW
- Masa Libre de Grasa: 61.1 kg
- Masa Grasa: 13.9 kg
```

---

### 5. Email Parte 2 (Internal Report)

#### BEFORE:
```
📊 INDICADORES OPCIONALES MEDIDOS:
   • % Masa muscular: 42.5%
     → Clasificación: Normal
     
   • Grasa visceral (nivel): 8
     → Clasificación: Saludable
```

#### AFTER:
```
📊 INDICADORES OPCIONALES MEDIDOS:
   • % Masa muscular: 42.5%
     → Clasificación: Normal
     
   • Grasa visceral (nivel): 8
     → Clasificación: Saludable
     
   • Circunferencia de cintura: 85.0 cm              ← NEW
     → Ratio Cintura-Estatura (WHtR): 0.500          ← NEW
     → Clasificación WHtR: Riesgo incrementado       ← NEW
     → Interpretación: WHtR < 0.5 indica bajo        ← NEW
        riesgo metabólico                            ← NEW
```

---

## WHtR Risk Classification Visual

```
┌─────────────────────────────────────────────────────────────┐
│                 WAIST-TO-HEIGHT RATIO (WHtR)                │
│                     Risk Classification                      │
├─────────────┬────────────────────────────────────────────────┤
│   < 0.4     │ 🔵 Extremadamente bajo (verificar medición)   │
├─────────────┼────────────────────────────────────────────────┤
│ 0.4 - 0.5   │ 🟢 Saludable (bajo riesgo)                    │
├─────────────┼────────────────────────────────────────────────┤
│ 0.5 - 0.6   │ 🟡 Riesgo incrementado                        │
├─────────────┼────────────────────────────────────────────────┤
│  ≥ 0.6      │ 🔴 Riesgo alto                                │
└─────────────┴────────────────────────────────────────────────┘

Example: Waist 85cm, Height 170cm → WHtR = 0.500 → 🟡 Riesgo incrementado
```

---

## Example User Flows

### Flow 1: User with healthy waist
```
Input Form:
├─ Height: 170.0 cm
├─ Waist: 80.0 cm
└─ Result: WHtR = 0.471

UI Display:
├─ Circunferencia cintura: 80.0 cm
└─ Ratio Cintura-Estatura (WHtR): 0.471 🟢 Saludable (bajo riesgo)

Email:
├─ Includes all waist data
├─ Classification: Saludable
└─ Interpretation: Low metabolic risk
```

### Flow 2: User with high-risk waist
```
Input Form:
├─ Height: 165.5 cm (decimal!)
├─ Waist: 105.0 cm
└─ Result: WHtR = 0.634

UI Display:
├─ Circunferencia cintura: 105.0 cm
└─ Ratio Cintura-Estatura (WHtR): 0.634 🔴 Riesgo alto

Email:
├─ Includes all waist data
├─ Classification: Riesgo alto
└─ Interpretation: High metabolic risk
```

### Flow 3: User skips waist measurement
```
Input Form:
├─ Height: 175.3 cm (decimal works!)
├─ Waist: [not entered]
└─ Result: No WHtR calculated

UI Display:
├─ Waist metrics NOT shown
└─ Other metrics display normally

Email:
├─ Circunferencia de cintura: No medido
├─ Ratio Cintura-Estatura (WHtR): No calculado
└─ All other data included normally
```

---

## Technical Details Visualization

### Data Flow Diagram
```
┌─────────────────┐
│  User Input     │
│  - Height (cm)  │
│  - Waist (cm)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │
│  - safe_float() │
│  - Range check  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Calculation    │
│  WHtR = W / H   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classification  │
│  - < 0.4: 🔵   │
│  - < 0.5: 🟢   │
│  - < 0.6: 🟡   │
│  - ≥ 0.6: 🔴   │
└────────┬────────┘
         │
         ├─────────────┬─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌────────┐   ┌────────┐
    │   UI   │   │ Email  │   │ Email  │
    │ Display│   │ Main   │   │ Parte2 │
    └────────┘   └────────┘   └────────┘
```

### Session State Structure
```javascript
st.session_state = {
    // ... existing fields ...
    "peso": 75.0,
    "estatura": 170.5,              // ← Now supports decimals
    "grasa_corporal": 18.5,
    "masa_muscular": 42.5,
    "grasa_visceral": 8,
    "circunferencia_cintura": 85.0, // ← NEW optional field
    // ... other fields ...
}
```

---

## Code Examples

### Height Input (Before vs After)
```python
# BEFORE
estatura = st.number_input(
    "📏 Estatura (cm)",
    min_value=120,        # Integer
    max_value=220,        # Integer
    value=safe_int(estatura_value, estatura_default),
    key="estatura",
    help="Medida sin zapatos"
)

# AFTER
estatura = st.number_input(
    "📏 Estatura (cm)",
    min_value=120.0,      # Float
    max_value=220.0,      # Float
    value=safe_float(estatura_value, estatura_default),
    step=0.1,             # Decimal precision
    key="estatura",
    help="Medida sin zapatos (permite decimales, ej: 165.5)"
)
```

### WHtR Calculation
```python
def calcular_whtr(circunferencia_cintura, estatura):
    """Calculate Waist-to-Height Ratio"""
    if circunferencia_cintura <= 0 or estatura <= 0:
        return 0.0
    return circunferencia_cintura / estatura

# Example usage
whtr = calcular_whtr(85.0, 170.0)  # Returns 0.500
```

### WHtR Classification
```python
def clasificar_whtr(whtr, sexo, edad):
    """Classify WHtR health risk"""
    if whtr <= 0:
        return "N/D"
    
    if whtr < 0.4:
        return "Extremadamente bajo (verificar medición)"
    elif whtr < 0.5:
        return "Saludable (bajo riesgo)"
    elif whtr < 0.6:
        return "Riesgo incrementado"
    else:
        return "Riesgo alto"

# Example usage
classification = clasificar_whtr(0.500, "Hombre", 30)
# Returns: "Riesgo incrementado"
```

---

## Benefits Summary

### For Users
✅ More precise height input (decimals)
✅ Additional health metric (WHtR)
✅ Evidence-based risk assessment
✅ Clear visual feedback
✅ Comprehensive email reports

### For Administrators
✅ Complete anthropometric data
✅ Scientific risk indicators
✅ Better client tracking
✅ Professional reports
✅ Minimal training needed

### For System
✅ No breaking changes
✅ Backward compatible
✅ Optional feature
✅ No performance impact
✅ Secure and validated

---

## Quick Reference Card

### Input Ranges
| Field | Min | Max | Step | Optional |
|-------|-----|-----|------|----------|
| Height | 120.0 cm | 220.0 cm | 0.1 | No |
| Waist | 0.0 cm | 200.0 cm | 0.1 | Yes |

### WHtR Thresholds
| Range | Classification | Color |
|-------|----------------|-------|
| < 0.4 | Extremely low | 🔵 Blue |
| 0.4-0.5 | Healthy | 🟢 Green |
| 0.5-0.6 | Increased risk | 🟡 Yellow |
| ≥ 0.6 | High risk | 🔴 Red |

### Key Functions
- `calcular_whtr(waist, height)` - Calculate ratio
- `clasificar_whtr(whtr, sex, age)` - Classify risk
- `safe_float(value, default)` - Safe conversion

---

**Implementation Date:** December 30, 2025
**Status:** ✅ Production Ready
**Version:** MUPAI v2.0+

# 📧 CÓMO LLEGA EL EMAIL CON DATOS DE ERICK - ARQUITECTURA ACTUAL

## 🎯 FLUJO COMPLETO (De Usuario a Email)

```
1️⃣ USUARIO ERICK COMPLETA FORMULARIO
   ├─ Peso: 80 kg
   ├─ Altura: 178 cm
   ├─ BF Omron: 31.2%
   ├─ Sueño: 5.0h ⚠️ (malo)
   └─ IR-SE: 64.3 ⚠️ (elevado)

2️⃣ SISTEMA CALCULA PARÁMETROS BASALES
   ├─ TMB (Omron): 1,680 kcal
   ├─ GEAF: 1.55
   ├─ ETA: 1.10
   ├─ GEE: 0 kcal
   └─ GE TOTAL: 2,410 kcal/día

3️⃣ NUEVA LÓGICA - SIN GUARDRAILS AÚN (Línea 10146)
   ├─ BF corregida: 26.4%
   ├─ Interpolar deficit por BF → 50%
   ├─ KCAL inicial: 2410 × 0.70 = 1,205 kcal
   ├─ Macros iniciales calculadas
   └─ plan_nuevo = {
        'fases': {'cut': {
          'kcal': 1205,      ← ANTES DE GUARDRAILS
          'deficit_pct': 50,
          'macros': {...},
          'ciclaje_4_3': {...}
        }}
      }

4️⃣ APLICAR GUARDRAILS (Línea 10161) 🔧 PUNTO CRÍTICO
   ├─ Extraer deficit_interpolado: 50%
   │
   ├─ Cap IR-SE:
   │  └─ IR-SE 64.3 en rango [50-70) → cap_ir_se = 30%
   │
   ├─ Cap Sueño:
   │  └─ Sueño 5.0h < 6h → cap_sleep = 30%
   │
   ├─ Aplicar mínimo:
   │  └─ deficit_capeado = min(50%, 30%, 30%) = 30% ✅
   │
   ├─ Recalcular KCAL:
   │  └─ kcal_capeado = 2410 × (1 - 30/100) = 1,687 kcal ✅
   │
   ├─ Recalcular MACROS proporcionalmente:
   │  ├─ Proteína: pbm × 2.2 = 150g (CONSTANTE)
   │  ├─ Grasas: (1687 - 600) × 30% / 9 = 36g
   │  └─ Carbos: (1687 - 600) × 70% / 4 = 191g
   │
   ├─ Recalcular CICLAJE:
   │  ├─ LOW: 1687 × 0.8 = 1,350 kcal
   │  └─ HIGH: ((7×1687) - (4×1350)) / 3 = 2,137 kcal
   │
   └─ ACTUALIZAR plan_nuevo IN-PLACE:
      └─ plan_nuevo['fases']['cut'] = {
           'kcal': 1687,      ← DESPUÉS DE GUARDRAILS ✅
           'deficit_pct': 30, ← DESPUÉS DE GUARDRAILS ✅
           'macros': {...},   ← RECALCULADAS ✅
           'ciclaje_4_3': {   ← RECALCULADO ✅
             'low_day_kcal': 1350,
             'high_day_kcal': 2137
           }
         }

5️⃣ LEER VALORES PARA EMAIL (Línea 10267)
   └─ macros_fase = plan_nuevo['fases']['cut']
      ├─ plan_tradicional_calorias = 1687 ✅
      ├─ ciclaje_low_kcal = 1350 ✅
      └─ ciclaje_high_kcal = 2137 ✅

6️⃣ EMAIL 1 (tabla_resumen) - Línea 10770
   
   Sección 6.1:
   ├─ ingesta_calorica_capeada = 1687 ✅
   └─ Muestra: "Ingesta calórica objetivo: 1,687 kcal/día"
   
   Sección 6.2:
   ├─ plan_tradicional_calorias = 1687 ✅
   ├─ proteina_g_tradicional = 150g ✅
   ├─ grasa_g_tradicional = 36g ✅
   ├─ carbo_g_tradicional = 191g ✅
   └─ Muestra tabla completa
   
   Sección 6.3 (Ciclaje):
   ├─ ciclaje_low_kcal = 1350 ✅
   ├─ ciclaje_high_kcal = 2137 ✅
   ├─ Macros LOW y HIGH recalculadas
   └─ Muestra ciclaje completo

7️⃣ EMAIL 4 (YAML) - Línea 10953
   
   Construcción datos_completos_yaml (Línea 10888):
   ├─ 'calorias_totales': plan_tradicional_calorias = 1687 ✅
   ├─ 'proteina_g': 150 ✅
   ├─ 'grasa_g': 36 ✅
   ├─ 'carbo_g': 191 ✅
   │
   ├─ ciclaje_4_3:
   │  ├─ 'low_day_kcal': 1350 ✅
   │  ├─ 'high_day_kcal': 2137 ✅
   │  └─ Macros asociados
   │
   └─ Envío a cliente (formato JSON)

8️⃣ RESULTADO FINAL EN EMAIL
   
   ✅ EMAIL 1 MUESTRA:
   ├─ Sección 6.1: 1,687 kcal
   ├─ Sección 6.2: 150g P / 36g F / 191g C
   ├─ Sección 6.3: LOW 1,350 / HIGH 2,137
   └─ NOTA GUARDRAILS: "Déficit aplicado: 30.0% (guardrails activos)"
   
   ✅ EMAIL 4 MUESTRA (YAML):
   ├─ "calorias_totales": 1687
   ├─ "proteina_g": 150
   ├─ "ciclaje_4_3": {"low_day_kcal": 1350, "high_day_kcal": 2137}
   └─ Formato estructurado para integración
```

---

## 🔄 FLUJO DE VARIABLES CLAVE

### Antes de Guardrails (Línea 10146)
```
GE = 2410
deficit_interpolado = 50%
kcal_sin_guardrails = 1205
```

### Después de Guardrails (Línea 10161-10228)
```
cap_ir_se = 30%
cap_sleep = 30%
deficit_capeado = min(50%, 30%, 30%) = 30%
kcal_capeado = 2410 × 0.70 = 1687 ✅

plan_nuevo['fases']['cut']['kcal'] = 1687 ✅
plan_nuevo['fases']['cut']['deficit_pct'] = 30 ✅
plan_nuevo['fases']['cut']['macros'] = {...} ✅
plan_nuevo['fases']['cut']['ciclaje_4_3'] = {...} ✅
```

### Para EMAIL (Línea 10267-10289)
```
macros_fase = plan_nuevo['fases']['cut']

plan_tradicional_calorias = macros_fase['kcal'] = 1687 ✅
ciclaje_low_kcal = 1350 ✅
ciclaje_high_kcal = 2137 ✅
```

---

## 📊 VALORES QUE LLEGAN EN EMAILS

| Parámetro | Valor | Origen | Email 1 | Email 4 |
|---|---|---|---|---|
| **Kcal CUT** | 1,687 | plan_nuevo capeado | Sección 6.1 ✅ | YAML ✅ |
| **Déficit** | 30% | guardrails | Sección 6.1 ✅ | YAML ✅ |
| **Proteína** | 150g | pbm × 2.2 | Sección 6.2 ✅ | YAML ✅ |
| **Grasas** | 36g | 30% de restante | Sección 6.2 ✅ | YAML ✅ |
| **Carbos** | 191g | 70% de restante | Sección 6.2 ✅ | YAML ✅ |
| **Ciclaje LOW** | 1,350 | kcal × 0.8 | Sección 6.3 ✅ | YAML ✅ |
| **Ciclaje HIGH** | 2,137 | ((7×kcal)-(4×LOW))/3 | Sección 6.3 ✅ | YAML ✅ |

---

## ✅ VERIFICACIONES DE COHERENCIA

```
1. Macros suman correcto:
   150g×4 + 36g×9 + 191g×4 = 600 + 324 + 764 = 1,688 ✅ ≈ 1,687

2. Ciclaje promedio = kcal:
   (4×1350 + 3×2137) / 7 = (5400 + 6411) / 7 = 1,687 ✅

3. EMAIL 1 y EMAIL 4 tienen mismos valores:
   Ambos usan plan_nuevo actualizado ✅

4. Test de coherencia:
   test_coherencia_email_1_4.py: 9/9 PASSED ✅
```

---

## 🎯 RESPUESTA TEXTUAL: "¿CÓMO LLEGA EL EMAIL?"

**EMAIL 1 (tabla_resumen)** llega con:
```
═══════════════════════════════════════════════════════════════════════
SECCIÓN 6: PLAN NUTRICIONAL
═══════════════════════════════════════════════════════════════════════

🎯 6.1 DIAGNÓSTICO Y FASE:
   • Fase recomendada: Déficit calculado por nueva lógica
   • Ingesta calórica objetivo: 1,687 kcal/día
   • Déficit aplicado: 30.0% (interpolado según BF + guardrails aplicados)
   ⚠️ GUARDRAILS ACTIVOS: IR-SE=64.3 (cap 30%) + Sueño=5.0h (cap 30%)

📊 6.2 PLAN NUTRICIONAL:
   ┌──────────────────────────────────────┐
   │ CALORÍAS: 1,687 kcal/día             │
   │ • Proteína: 150g (35.4%)             │
   │ • Grasas: 36g (19.4%)                │
   │ • Carbohidratos: 191g (45.2%)        │
   └──────────────────────────────────────┘

🔄 6.3 CICLAJE 4-3:
   📉 DÍAS LOW (4 días): 1,350 kcal
   📈 DÍAS HIGH (3 días): 2,137 kcal
   📊 PROMEDIO: 1,687 kcal/día
```

**EMAIL 4 (YAML)** llega con:
```json
{
  "macronutrientes_tradicionales": {
    "calorias_totales": 1687,
    "proteina_g": 150,
    "grasa_g": 36,
    "carbohidratos_g": 191
  },
  "ciclaje_4_3": {
    "low_day_kcal": 1350,
    "high_day_kcal": 2137,
    "promedio_semanal": 1687
  }
}
```

**Ambos emails son 100% coherentes** porque ambos leen de `plan_nuevo['fases']['cut']` que fue actualizado una única vez con guardrails aplicados.

---

## 📝 NOTAS TÉCNICAS

- **Punto de entrada de guardrails**: Línea 10161 en streamlit_app.py
- **Actualización in-place**: Plan se modifica directamente, no se crea copia
- **Fuente única de verdad**: `plan_nuevo['fases']['cut']`
- **Tests de verificación**: 
  - `test_coherencia_email_1.py`: 9/9 PASSED
  - `test_coherencia_email_1_4.py`: 9/9 PASSED
  - `test_estabilidad_logica.py`: 6/6 PASSED
- **Commits relacionados**:
  - `0e9bbff`: Apply guardrails
  - `939c766`: Use capped calories in email
  - `eb64b6e`: Mark legacy logic as fallback
  - `1a4305e`: Document architecture
  - `c764434`: Textual email examples

---

## 🏁 CONCLUSIÓN

**Con los datos de Erick**, el flujo es:

```
2410 kcal GE
    ↓
Guardrails: sueño 5h + IR-SE 64.3 → cap 30%
    ↓
1687 kcal CUT (no 1205)
    ↓
150g P / 36g F / 191g C
    ↓
Ciclaje: 1350 LOW / 2137 HIGH
    ↓
EMAIL 1 + EMAIL 4: Ambos muestran 1687/150/36/191/1350/2137
```

**El email llega CORRECTO, COHERENTE y COMPLETAMENTE CONSISTENTE** ✅

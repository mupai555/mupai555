# 🏗️ ARQUITECTURA FINAL: KCAL → MACROS → CICLAJE

## 📊 FLUJO GENERAL (Erick: BF 26.4%, IR-SE 64.3, Sueño 5.0h)

```
ENTRADA: grasa_corregida = 26.4%
          ↓
    ╔═════════════════════════════════════════════════════════════════╗
    ║              FLUJO C: CÁLCULO INICIAL (sin guardrails)          ║
    ╚═════════════════════════════════════════════════════════════════╝
          ↓
    1️⃣  Interpolar deficit por BF (tabla)
        BF 26.4% → deficit = 50% (sin guardrails)
          ↓
    2️⃣  Calcular KCAL INICIAL
        GE = 2410 kcal
        KCAL_INICIAL = 2410 × (1 - 50/100) = 1205 kcal
          ↓
    3️⃣  Calcular MACROS INICIALES
        Proteína: pbm × 2.2 g/kg = constante
        Grasas + Carbos: distribuir 1205 kcal restante
          ↓
    ┌─────────────────────────────────────────────────────────────────┐
    │         plan_nuevo['fases']['cut'] ACTUALIZADO CON:             │
    │         • deficit_pct = 50%                                     │
    │         • kcal = 1205                                           │
    │         • macros = {protein_g, fat_g, carb_g}                   │
    │         • ciclaje_4_3 = {low/high días y kcal}                 │
    └─────────────────────────────────────────────────────────────────┘
          ↓
    ╔═════════════════════════════════════════════════════════════════╗
    ║              FLUJO D: APLICAR GUARDRAILS (Línea 10161)          ║
    ╚═════════════════════════════════════════════════════════════════╝
          ↓
    ⚠️  GUARDRAILS ACTIVOS:
        • Cap IR-SE:  IR-SE 64.3 (rango 50-69) → cap = 30%
        • Cap Sueño:  Sleep 5.0h < 6h → cap = 30%
          ↓
    🔧 APLICAR DÉFICIT CAPEADO:
        deficit_capeado = min(50%, 30%, 30%) = 30% ✅
          ↓
    💰 RECALCULAR KCAL:
        kcal_capeado = 2410 × (1 - 30/100) = 1687 kcal ✅
          ↓
    ┌─────────────────────────────────────────────────────────────────┐
    │         plan_nuevo['fases']['cut']['kcal'] = 1687               │
    │         (ACTUALIZADO IN-PLACE EN GUARDRAILS)                    │
    │                                                                   │
    │         ⚠️  OJO: 1687 ≠ 1205 (el cambio es significativo)       │
    └─────────────────────────────────────────────────────────────────┘
          ↓
    ╔═════════════════════════════════════════════════════════════════╗
    ║        FLUJO E: RECALCULAR MACROS CON KCAL CAPEADO (Línea 10215)║
    ╚═════════════════════════════════════════════════════════════════╝
          ↓
    1️⃣  PROTEÍNA: Se mantiene CONSTANTE
        protein_g = base_proteina_kg × 2.2 g/kg = X gramos
        protein_kcal = X × 4
          ↓
    2️⃣  DISTRIBUCIÓN RESTANTE (1687 - protein_kcal = Y kcal disponibles):
        • Grasas: 30% de Y
        • Carbohidratos: 70% de Y
          ↓
    EJEMPLO NUMÉRICO:
        • Proteína: 150g (pbm ~68kg × 2.2) = 600 kcal
        • Kcal disponible: 1687 - 600 = 1087 kcal
        • Grasas: 1087 × 30% = 326 kcal = 36g
        • Carbos: 1087 × 70% = 761 kcal = 190g
          ↓
    ┌─────────────────────────────────────────────────────────────────┐
    │         plan_nuevo['fases']['cut']['macros'] ACTUALIZADO:       │
    │         • protein_g = 150                                        │
    │         • fat_g = 36                                             │
    │         • carb_g = 190                                           │
    └─────────────────────────────────────────────────────────────────┘
          ↓
    ╔═════════════════════════════════════════════════════════════════╗
    ║      FLUJO F: RECALCULAR CICLAJE CON KCAL CAPEADO (Línea 10230) ║
    ╚═════════════════════════════════════════════════════════════════╝
          ↓
    📋 CICLAJE 4-3:
        • 4 días LOW (menor kcal)
        • 3 días HIGH (mayor kcal)
        • Promedio = 1687 kcal
          ↓
    FÓRMULAS:
        LOW_kcal = kcal_capeado × 0.8
                 = 1687 × 0.8
                 = 1349.6 ≈ 1350 kcal ✅
          ↓
        HIGH_kcal = ((7 × kcal_capeado) - (4 × LOW_kcal)) / 3
                  = ((7 × 1687) - (4 × 1349.6)) / 3
                  = (11809 - 5398.4) / 3
                  = 2137.2 ≈ 2137 kcal ✅
          ↓
    VERIFICACIÓN (promedio semanal):
        (4 × 1350) + (3 × 2137) = 5400 + 6411 = 11811
        11811 / 7 = 1687 ✅ (matches kcal_capeado)
          ↓
    ┌─────────────────────────────────────────────────────────────────┐
    │   plan_nuevo['fases']['cut']['ciclaje_4_3'] ACTUALIZADO:        │
    │   • low_day_kcal = 1350                                          │
    │   • high_day_kcal = 2137                                         │
    │   • low_macros = {protein_g, fat_g, carb_g} para LOW             │
    │   • high_macros = {protein_g, fat_g, carb_g} para HIGH           │
    └─────────────────────────────────────────────────────────────────┘
          ↓
    ╔═════════════════════════════════════════════════════════════════╗
    ║             LEER VALORES PARA EMAILS (Línea 10267)              ║
    ╚═════════════════════════════════════════════════════════════════╝
          ↓
    📧 EMAIL 1 (tabla_resumen):
        • ingesta_calorica_capeada = 1687 (seccion 6.1) ✅
        • plan_nuevo['fases']['cut'] = contiene macros capeadas ✅
        • ciclaje_low_kcal = 1350, ciclaje_high_kcal = 2137 ✅
          ↓
    📧 EMAIL 4 (YAML):
        • plan_tradicional_calorias = macros_fase['kcal'] = 1687 ✅
        • ciclaje_low_kcal = 1350, ciclaje_high_kcal = 2137 ✅
          ↓
    ✅ AMBOS EMAILS COHERENTES
```

---

## 🔑 VARIABLES CLAVE EN streamlit_app.py

### 1️⃣ KCAL (Líneas indicadas)

| Variable | Línea | Valor | Propósito |
|----------|-------|-------|----------|
| `GE` | 9000+ | 2410 | Gasto Energético Total (input) |
| `deficit_interpolado` | 10157 | 50% | Deficit por BF (tabla) |
| `cap_ir_se` | 10165-169 | 30% | Cap guardrail IR-SE |
| `cap_sleep` | 10172-176 | 30% | Cap guardrail Sueño |
| `deficit_capeado` | 10178 | 30% | Min(50%, 30%, 30%) |
| `kcal_capeado` | 10190 | 1687 | GE × (1 - 30/100) |
| `plan_nuevo['fases']['cut']['kcal']` | 10197 | 1687 | ACTUALIZADO en guardrails |
| `ingesta_calorica_capeada` | 10161/10192 | 1687 | Variable para email sección 6.1 |
| `plan_tradicional_calorias` | 10267 | 1687 | Lee de plan_nuevo actualizado |

### 2️⃣ MACROS (Proteína + Grasas + Carbos)

| Variable | Línea | Cálculo | Propósito |
|----------|-------|---------|----------|
| `protein_g` | 10213 | pbm × 2.2 | Proteína (CONSTANTE) |
| `protein_kcal` | 10214 | protein_g × 4 | Kcal proteína |
| `kcal_disponible` | 10217 | 1687 - protein_kcal | Para grasas + carbos |
| `grasa_g_nueva` | 10226 | (kcal_disponible × 30%) / 9 | Grasas |
| `carbo_g_nueva` | 10230 | (kcal_disponible × 70%) / 4 | Carbohidratos |
| `plan_nuevo['fases']['cut']['macros']` | 10227-228 | {protein_g, fat_g, carb_g} | ACTUALIZADO en guardrails |

### 3️⃣ CICLAJE 4-3

| Variable | Línea | Cálculo | Propósito |
|----------|-------|---------|----------|
| `kcal_low_nuevo` | 10235 | 1687 × 0.8 | 1350 kcal LOW |
| `kcal_high_nuevo` | 10236 | ((7×1687)-(4×1350))/3 | 2137 kcal HIGH |
| `plan_nuevo['fases']['cut']['ciclaje_4_3']` | 10237+ | {low_day_kcal, high_day_kcal, ...} | ACTUALIZADO en guardrails |
| `ciclaje_low_kcal` | 10288 | Lee de plan_nuevo actualizado | Para EMAIL |
| `ciclaje_high_kcal` | 10289 | Lee de plan_nuevo actualizado | Para EMAIL |

---

## 🎯 PUNTOS CRÍTICOS

### ✅ LO QUE ESTÁ BIEN

1. **Una única fuente de verdad:**
   - `plan_nuevo['fases']['cut']` es actualizado UNA SOLA VEZ en guardrails
   - Todos los downstream lees usan este valor actualizado
   - No hay duplicación ni inconsistencias

2. **Guardrails aplicados correctamente:**
   - Antes: deficit = 50%, kcal = 1205 (sin guardrails)
   - Después: deficit = 30%, kcal = 1687 (con guardrails) ✅
   - La diferencia es SIGNIFICATIVA y CORRECTA

3. **Macros se recalculan proporcionalmente:**
   - Proteína se mantiene constante (CRÍTICO para dieta)
   - Grasas y carbos se ajustan al nuevo kcal
   - Ratio grasas/carbos se mantiene (30/70)

4. **Ciclaje mantiene promedio:**
   - (4×1350 + 3×2137) / 7 = 1687 ✅
   - Promedio semanal = kcal promedio
   - Esto asegura adherencia a déficit

5. **Emails son coherentes:**
   - EMAIL 1: Usa valores capeados en todas secciones
   - EMAIL 4: Usa valores capeados en YAML
   - 9/9 checks PASSED

### ⚠️ PUNTOS A VIGILAR

1. **Variables legacy que NO se usan en emails:**
   - `ingesta_calorica_tradicional` = 1205 (SOLO para UI fallback)
   - `fbeo` (factor antigua lógica) = SOLO para UI
   - Comentarios added en líneas 9132-9140, 9162-9167

2. **Múltiples asignaciones de `plan_tradicional_calorias`:**
   - Línea 9816: Inicialización fallback = 1205
   - Línea 10267: Asignación REAL = 1687 ✅
   - La línea 10267 SOBREESCRIBE la línea 9816, así que está bien

3. **Ciclaje solo disponible si existe:**
   - Línea 10235: IF existe `ciclaje_4_3` en plan
   - Si no existe, las vars no se definen
   - En emails: tienen checks `if 'tiene_ciclaje'`

---

## 📧 RESUMEN EMAILS

### EMAIL 1: tabla_resumen (Línea 10770)

```
SECCIÓN 6.1: Calorías Objetivo (Línea 10303)
├─ ingesta_calorica_objetivo = ingesta_calorica_capeada
├─ Valor: 1687 kcal ✅
└─ Origen: Guardrails

SECCIÓN 6.2: Detalles Nutricionales
├─ Macros: protein_g_tradicional, grasa_g_tradicional, carbo_g_tradicional
├─ Estos vienen de plan_nuevo['fases']['cut']['macros'] actualizado ✅
└─ Valor: 150g proteína, 36g grasas, 190g carbos

SECCIÓN 6.3: Ciclaje 4-3
├─ LOW: ciclaje_low_kcal = 1350 ✅
├─ HIGH: ciclaje_high_kcal = 2137 ✅
└─ Origen: plan_nuevo['fases']['cut']['ciclaje_4_3'] actualizado
```

### EMAIL 4: YAML (Línea 10953)

```
macronutrientes_tradicionales:
├─ calorias_totales: plan_tradicional_calorias = 1687 ✅
└─ protein_g, fat_g, carb_g de plan_nuevo actualizado

ciclaje_4_3:
├─ low_day_kcal: ciclaje_low_kcal = 1350 ✅
├─ high_day_kcal: ciclaje_high_kcal = 2137 ✅
└─ Origen: plan_nuevo actualizado
```

---

## 🔄 VERIFICACIÓN: ¿Cómo sé que está correcto?

```python
# Test run:
python test_coherencia_email_1_4.py

RESULTADO:
✅ V1: EMAIL 1 y 4: Mismo déficit capeado (30%)
✅ V2: EMAIL 1 y 4: Mismo kcal CUT (1687)
✅ V3: EMAIL 1 y 4: Mismo ciclaje LOW (1350)
✅ V4: EMAIL 1 y 4: Mismo ciclaje HIGH (2137)
✅ V5: YAML usa plan_tradicional_calorias capeado (no 1205)
✅ V6: EMAIL 1 sección 6.1 usa ingesta_calorica_capeada
✅ V7: EMAIL 1 sección 6.2 usa plan_nuevo actualizado
✅ V8: EMAIL 1 sección 6.3 ciclaje basado en capeado
✅ V9: Una fuente de verdad (guardrails)

=== 9/9 CHECKS PASSED ===
```

---

## 🎓 EJEMPLO CÁLCULO COMPLETO (Erick)

```
ENTRADA:
  grasa_corregida = 26.4%
  GE = 2410 kcal
  IR-SE = 64.3
  Sueño = 5.0h
  pbm = 68 kg

PASO 1 - DÉFICIT INTERPOLADO:
  BF 26.4% en tabla → 50% deficit
  
PASO 2 - APLICAR GUARDRAILS:
  cap_ir_se = 30% (IR-SE 64.3 en rango 50-69)
  cap_sleep = 30% (sleep 5.0h < 6h)
  deficit_capeado = min(50%, 30%, 30%) = 30%
  
PASO 3 - KCAL CAPEADO:
  kcal_capeado = 2410 × (1 - 0.30) = 1687 kcal
  
PASO 4 - MACROS:
  protein_g = 68 × 2.2 = 150g = 600 kcal
  kcal_restante = 1687 - 600 = 1087 kcal
  fat_g = (1087 × 0.30) / 9 = 36g
  carb_g = (1087 × 0.70) / 4 = 190g
  
PASO 5 - CICLAJE:
  low_kcal = 1687 × 0.8 = 1350 kcal
  high_kcal = ((7×1687) - (4×1350)) / 3 = 2137 kcal
  promedio = (4×1350 + 3×2137) / 7 = 1687 ✅
  
SALIDA (EMAILS):
  EMAIL 1: 1687 kcal, 30%, 150/36/190, ciclaje 1350/2137
  EMAIL 4: 1687 kcal, 30%, 150/36/190, ciclaje 1350/2137
```

---

## 📋 CHECKLIST DE CONFIANZA

- ✅ `grasa_corregida` es única fuente de verdad para déficit
- ✅ Guardrails aplicados ANTES de calcular macros/ciclaje
- ✅ `plan_nuevo` actualizado in-place, no duplicado
- ✅ Macros recalculados proporcionalmente
- ✅ Ciclaje mantiene promedio correcto
- ✅ EMAIL 1 y EMAIL 4 coherentes (9/9 checks)
- ✅ Variables legacy marcadas como "fallback/UI only"
- ✅ Toda la lógica documentada en código
- ✅ Tests confirman correctitud

**LA LÓGICA ESTÁ CORRECTA Y COMPLETA** ✅

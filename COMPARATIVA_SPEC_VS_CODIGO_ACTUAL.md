# ============================================================================
# COMPARATIVA: SPEC YAML vs CÓDIGO ACTUAL (streamlit_app.py)
# Sistema MUPAI v2.0 - Análisis de Divergencias
# ============================================================================

## METODOLOGÍA

He analizado:
1. **SPEC YAML** (tu especificación documentada)
2. **streamlit_app.py** (código actual implementado)

Esta comparativa identifica:
- ✅ Elementos implementados correctamente
- ⚠️ Divergencias significativas
- ❌ Ausencias críticas

---

## 1. DÉFICITS CUT - INTERPOLACIÓN LINEAL

### SPEC YAML:
```yaml
knots:
  hombres: [[4, 2.5], [8, 7.5], [15, 25], [21, 40], [26, 50]]
  mujeres: [[8, 2.5], [14, 7.5], [24, 25], [33, 40], [39, 50]]
```
**Método**: Interpolación lineal pura entre puntos ancla

### CÓDIGO ACTUAL (líneas 2633-2660):
```python
rangos_hombre = [
    (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
    (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
    (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 40, 35), (40.1, 45, 40),
    (45.1, 100, 50)
]
rangos_mujer = [
    (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
    (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
    (31.6, 35, 30), (35.1, 40, 30), (40.1, 45, 35), (45.1, 50, 40),
    (50.1, 100, 50)
]
```
**Método**: Tabla estática con rangos fijos

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Método** | Interpolación lineal | Tabla estática | ❌ **DIFERENTE** |
| **Granularidad** | 5 puntos | 13 rangos (H), 13 rangos (M) | ⚠️ **MÁS COMPLEJO** |
| **BF 15% (H)** | 25% déficit | 15.6-18% → 20% | ⚠️ **DIVERGENCIA** |
| **BF 21% (H)** | 40% déficit | 20.6-23% → 27% | ⚠️ **DIVERGENCIA** |
| **BF 26% (H)** | 50% déficit | 25.6-30% → 30% | ❌ **CRÍTICO** |

**PROBLEMA CRÍTICO:**
```
SPEC: BF 26% (H) → 50% déficit
Código: BF 26% (H) → 30% déficit (con cap)

Código tiene límite adicional:
tope = 30
limite_extra = 30 (H) / 35 (M)
return min(deficit, tope) if porcentaje_grasa <= limite_extra else deficit
```

**DIVERGENCIA MAYOR:**  
El código **NUNCA alcanza 50% déficit** porque:
1. Cap de 30% aplica hasta BF 30% (H)
2. Tabla máxima es 35% (no 50%)

---

## 2. SUPERÁVITS BULK

### SPEC YAML:
```yaml
surplus_pct_ranges_by_training_level:
  novato: [5, 15]
  intermedio: [2, 7]
  avanzado: [1, 3]
  elite: [1, 3]
```

### CÓDIGO ACTUAL (líneas 2663-2800):
```python
# Función: determinar_fase_nutricional_refinada()

if sexo == "Hombre":
    if grasa_corregida < 6:
        fase = "Superávit recomendado: 10-15%"
        porcentaje = 12.5
    elif grasa_corregida <= 10:
        fase = "Superávit recomendado: 5-10%"
        porcentaje = 7.5
    elif grasa_corregida <= 15:
        fase = "Superávit recomendado: 3-7%"
        porcentaje = 5.0
    elif grasa_corregida <= 20:
        fase = "Déficit moderado: -10% a -15%"
        porcentaje = -12.5
    # ... etc
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Criterio** | Nivel entrenamiento | % Grasa corporal | ❌ **COMPLETAMENTE DIFERENTE** |
| **Novato** | 5-15% | NO EXISTE CONCEPTO | ❌ **AUSENTE** |
| **Intermedio** | 2-7% | NO EXISTE CONCEPTO | ❌ **AUSENTE** |
| **Avanzado** | 1-3% | NO EXISTE CONCEPTO | ❌ **AUSENTE** |
| **Elite** | 1-3% | NO EXISTE CONCEPTO | ❌ **AUSENTE** |

**PROBLEMA CRÍTICO:**  
El código **NO implementa superávits por nivel de entrenamiento**.  
En su lugar, usa **solo % grasa corporal** con rangos fijos:
- BF <6%: 10-15%
- BF 6-10%: 5-10%
- BF 10-15%: 3-7%

**AUSENCIA TOTAL** de la variable `training_level` en cálculo de bulk.

---

## 3. PROTEÍNA - PBM + MULTIPLICADORES

### SPEC YAML:
```yaml
protein:
  pbm:
    thresholds_overweight:
      hombre: 0.20
      mujer: 0.30
    formula:
      - "Si BF <= BF_threshold: PBM = BW"
      - "Si BF > BF_threshold: PBM = FFM / (1 - BF_threshold)"
  multipliers:
    maintenance: 1.6
    bulk: 1.6
    bulk_robustez_explicita: 1.8
    cut_base: 1.8
    cut_deficit_ge_30: 2.0
    cut_preparacion: 2.0
  psmf_rules:
    - "Si overweight: protein_g = round(2.3 * FFM)"
    - "Si NO overweight: protein_g = round(1.8 * BW)"
```

### CÓDIGO ACTUAL (líneas 2950-3050):

#### A) PROTEÍNA PLAN TRADICIONAL:
```python
def debe_usar_mlg_para_proteina(sexo, grasa_corregida):
    """Determina si se debe usar MLG o peso total para el cálculo de proteína."""
    if sexo == "Hombre":
        return grasa_corregida > 20.0  # Threshold 20%
    else:  # Mujer
        return grasa_corregida > 30.0  # Threshold 30%

def obtener_factor_proteina_tradicional(grasa_corregida):
    """Retorna el factor de proteína (g/kg) según % de grasa corporal."""
    if grasa_corregida <= 10:
        return 2.2  # Alto
    elif grasa_corregida <= 15:
        return 2.0  # Moderado-alto
    elif grasa_corregida <= 20:
        return 1.8  # Moderado
    elif grasa_corregida <= 25:
        return 1.6  # Moderado-bajo
    elif grasa_corregida <= 30:
        return 1.5  # Bajo
    else:
        return 1.4  # Muy bajo
```

#### B) PROTEÍNA PSMF (líneas 2470-2580):
```python
def calculate_psmf():
    # ...
    if grasa_corregida < 25:
        factor_proteina = 1.8  # g/kg
        grasa_g_dia = 30
        multiplicador = 9.5  # Para calcular kcal objetivo
    else:
        factor_proteina = 1.6  # g/kg
        grasa_g_dia = 50
        multiplicador = 8.3  # Para calcular kcal objetivo
    
    proteina_g_dia = round(base_proteina_kg * factor_proteina, 1)
    kcal_psmf_obj = round(proteina_g_dia * multiplicador, 0)
    # ...
```

### EVALUACIÓN:

#### TRADICIONAL:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Threshold (H)** | 20% | 20% | ✅ **CORRECTO** |
| **Threshold (M)** | 30% | 30% | ✅ **CORRECTO** |
| **PBM Formula** | FFM/(1-threshold) | Directa MLG vs BW | ⚠️ **DIFERENTE (resultado similar)** |
| **Maintenance mult** | 1.6 | N/A (no existe fase) | ❌ **NO IMPLEMENTADO** |
| **Bulk mult** | 1.6 | N/A (no existe fase) | ❌ **NO IMPLEMENTADO** |
| **Cut base mult** | 1.8 | Varía 1.4-2.2 por BF% | ⚠️ **LÓGICA DIFERENTE** |

**PROBLEMA:**  
Código usa **% grasa como único criterio**, no fases (cut/maintenance/bulk):
```
BF ≤10%: 2.2 g/kg
BF 10-15%: 2.0 g/kg
BF 15-20%: 1.8 g/kg
BF 20-25%: 1.6 g/kg
BF 25-30%: 1.5 g/kg
BF >30%: 1.4 g/kg
```

SPEC dice:
```
Maintenance: 1.6 × PBM (siempre)
Cut base: 1.8 × PBM
Cut agresivo: 2.0 × PBM
```

**NO HAY ALINEACIÓN** entre SPEC y código.

#### PSMF:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Overweight (>threshold)** | 2.3 × FFM | 1.8 × base (si BF<25%) | ❌ **DIFERENTE** |
| **Lean (<threshold)** | 1.8 × BW | 1.6 × base (si BF≥25%) | ⚠️ **DIVERGENCIA** |
| **Factor k** | 9.7/9.0/8.6/8.3 | 9.5 (BF<25) / 8.3 (BF≥25) | ⚠️ **SIMPLIFICADO** |

**PROBLEMA:**  
Código PSMF usa **threshold en 25% de grasa**, no en 20% (H) / 30% (M).

---

## 4. GRASAS

### SPEC YAML:
```yaml
fat_normal_phases:
  selector_fat_pct: [0.20, 0.30, 0.40]
  default_fat_pct: 0.30
psmf_distribution:
  fat_share_rest: 0.70
```

### CÓDIGO ACTUAL:

#### PLAN TRADICIONAL (líneas 2840-2860):
```python
def obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo):
    """
    Retorna el porcentaje del TMB que debe destinarse a grasas.
    Nueva lógica científica: SIEMPRE 40% del TMB para grasas.
    """
    return 0.40  # 40% TMB (aplicable a todos)
```

Luego en `calcular_macros_tradicional()`:
```python
grasa_min_kcal = ingesta_calorica_tradicional * 0.20  # Mínimo 20% TEI
grasa_max_kcal = ingesta_calorica_tradicional * 0.40  # Máximo 40% TEI
grasa_ideal_kcal = tmb * 0.40  # 40% TMB
grasa_kcal = max(grasa_min_kcal, min(grasa_ideal_kcal, grasa_max_kcal))
```

#### PSMF (líneas 2550):
```python
if grasa_corregida < 25:
    grasa_g_dia = 30
else:
    grasa_g_dia = 50
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Selector 20/30/40%** | Sí (3 opciones) | NO (fijo 40% TMB) | ❌ **NO IMPLEMENTADO** |
| **Default 30%** | Sí | NO (40% TMB capped 20-40% TEI) | ⚠️ **LÓGICA DIFERENTE** |
| **PSMF fat_share_rest** | 0.70 (70% resto) | Fijo 30g o 50g | ❌ **COMPLETAMENTE DIFERENTE** |
| **PSMF clamp 20-60g** | Sí | NO (30g o 50g fijos) | ❌ **NO IMPLEMENTADO** |

**PROBLEMA CRÍTICO:**  
Código NO permite **selector 20/30/40%**.  
Usa lógica fija: 40% TMB con límites 20-40% TEI.

PSMF: Grasa fija (30g o 50g), no calcula desde `fat_share_rest`.

---

## 5. CARBOHIDRATOS

### SPEC YAML:
```yaml
carbs_residual:
  formula:
    - "carb_g = round((target_kcal - (4*protein_g + 9*fat_g)) / 4)"
  guardrail_if_negative:
    - "Si carb_g < 0: bajar fat_pct un nivel (0.40→0.30→0.20)"
```

### CÓDIGO ACTUAL (líneas 2990-3010):
```python
def calcular_macros_tradicional():
    # ...
    # 3. CARBOHIDRATOS: Calorías restantes
    carbo_kcal = ingesta_calorica_tradicional - proteina_kcal - grasa_kcal
    carbo_g = round(max(0, carbo_kcal / 4), 1)
    # ...
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Método residual** | Sí | Sí | ✅ **CORRECTO** |
| **Guardrail si <0** | Bajar fat_pct | max(0, ...) | ⚠️ **IMPLEMENTACIÓN DIFERENTE** |

**NOTA:**  
Código usa `max(0, ...)` para evitar negativos.  
NO implementa ajuste iterativo de fat_pct como SPEC indica.

---

## 6. CICLAJE 4-3

### SPEC YAML:
```yaml
weekly_cycle_4_3:
  enabled_by_default: true
  pattern:
    low_days: [Mon, Tue, Wed, Thu]
    high_days: [Fri, Sat, Sun]
  low_factor_by_phase:
    cut: 0.80
    maintenance: 0.90
    bulk: 0.95
  caps_high:
    cut: "kcal_high <= 1.05 * maintenance_kcal"
    maintenance: "kcal_high <= 1.10 * maintenance_kcal"
    bulk: "kcal_high <= 1.20 * maintenance_kcal"
```

### CÓDIGO ACTUAL:
```bash
❌ NO ENCONTRADO
```

**BÚSQUEDA REALIZADA:**
```
grep_search: "ciclaje|cycle_4_3|low_factor|weekly_cycle"
Resultado: No matches found
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Ciclaje 4-3** | Documentado completo | NO EXISTE | ❌ **AUSENTE TOTAL** |
| **LOW factors** | 0.80/0.90/0.95 | N/A | ❌ **NO IMPLEMENTADO** |
| **HIGH caps** | 1.05/1.10/1.20 | N/A | ❌ **NO IMPLEMENTADO** |
| **Proteína constante** | Sí | N/A | ❌ **NO IMPLEMENTADO** |

**PROBLEMA CRÍTICO:**  
**CICLAJE 4-3 NO ESTÁ IMPLEMENTADO EN EL CÓDIGO.**

---

## 7. GUARDRAILS IR-SE

### SPEC YAML:
```yaml
guardrails:
  recovery_index_ir_se:
    - "IR-SE >= 70: permitir lógica estándar"
    - "IR-SE 50–69: cap déficit cut = 30%"
    - "IR-SE < 50: cap déficit = 25%"
  sleep:
    - "Si sleep_hours < 6: aplicar cap de IR-SE 50–69"
```

### CÓDIGO ACTUAL:

**CÁLCULO IR-SE EXISTE** (líneas 6289+):
```python
# Calcular IR-SE (Índice de Recuperación Sueño-Estrés)
ir_se = (sleep_score * 0.6) + (stress_score * 0.4)
```

**PERO NO HAY IMPLEMENTACIÓN DE CAPS:**
```bash
❌ NO ENCONTRADO caps o límites basados en IR-SE
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Cálculo IR-SE** | Sí | Sí | ✅ **IMPLEMENTADO** |
| **Cap déficit IR-SE 50-69** | 30% | NO APLICADO | ❌ **NO IMPLEMENTADO** |
| **Cap déficit IR-SE <50** | 25% | NO APLICADO | ❌ **NO IMPLEMENTADO** |
| **Cap sueño <6h** | Como IR-SE 50-69 | NO APLICADO | ❌ **NO IMPLEMENTADO** |
| **PSMF condicional IR-SE** | Solo si IR-SE ≥50 | NO VALIDADO | ❌ **NO IMPLEMENTADO** |

**PROBLEMA:**  
IR-SE se **calcula y reporta**, pero **NO modifica lógica** de déficits/PSMF.

---

## 8. PSMF K-FACTOR

### SPEC YAML:
```yaml
psmf:
  k_factor_rules_text:
    - "Set energy intake at 8.3 × protein intake"
    - "If you have abs, don't go lower than 9.7 × PRO"
  k_by_zone:
    preparacion: 9.7
    zona_triple: 9.0
    promedio: 8.6
    sobrepeso_obesidad: 8.3
```

### CÓDIGO ACTUAL (líneas 2520-2580):
```python
if grasa_corregida < 25:
    multiplicador = 9.5
else:
    multiplicador = 8.3

kcal_psmf_obj = round(proteina_g_dia * multiplicador, 0)
```

### EVALUACIÓN:
| Aspecto | SPEC | Código | Estado |
|---------|------|--------|--------|
| **Preparación k=9.7** | Sí | NO (usa 9.5) | ⚠️ **SIMPLIFICADO** |
| **Zona triple k=9.0** | Sí | NO | ❌ **NO IMPLEMENTADO** |
| **Promedio k=8.6** | Sí | NO | ❌ **NO IMPLEMENTADO** |
| **Sobrepeso k=8.3** | Sí | Sí (BF≥25%) | ✅ **PARCIAL** |

**PROBLEMA:**  
Código usa **solo 2 valores** (9.5 / 8.3) con threshold en 25%.  
SPEC usa **4 valores** (9.7/9.0/8.6/8.3) según zona BF.

---

## 9. SALIDAS MACHINE-READABLE

### SPEC YAML:
```yaml
output_schemas:
  implementation_json:
    schema_example: |
      {
        "kcal_targets": {...},
        "macros_avg": {...},
        "kcal_views": {
          "linear_7d": {...},
          "cycle_4_3": {...}
        },
        ...
      }
  kcal_macros_clipboard_json:
    rule: "JSON mínimo con SOLO kcal y macros"
```

### CÓDIGO ACTUAL:
```bash
❌ NO ENCONTRADO
```

**NO HAY FUNCIONES** que generen JSON estructurado según schema SPEC.

---

## RESUMEN EJECUTIVO

### RATING DE IMPLEMENTACIÓN:

| Componente | SPEC Definido | Código Implementado | Alineación |
|-----------|--------------|-------------------|-----------|
| **1. Déficits Cut** | ✅ Interpolación lineal 5 puntos | ⚠️ Tabla estática 13 rangos | 40% |
| **2. Superávits Bulk** | ✅ Por nivel entrenamiento | ❌ Por % grasa (sin nivel) | 0% |
| **3. Proteína PBM** | ✅ Formula (FFM/threshold) | ⚠️ MLG vs BW directo | 60% |
| **4. Proteína Multiplicadores** | ✅ Por fase (1.6-2.0) | ⚠️ Por % grasa (1.4-2.2) | 30% |
| **5. Grasas Selector** | ✅ 20/30/40% opciones | ❌ Fijo 40% TMB | 0% |
| **6. Carbos Residuales** | ✅ Con guardrail fat_pct | ⚠️ Con max(0,...) | 70% |
| **7. Ciclaje 4-3** | ✅ Completo con caps | ❌ NO EXISTE | 0% |
| **8. Guardrails IR-SE** | ✅ Caps por nivel | ⚠️ Calcula pero no aplica | 20% |
| **9. PSMF K-factors** | ✅ 4 zonas (9.7-8.3) | ⚠️ 2 valores (9.5/8.3) | 40% |
| **10. JSON Output** | ✅ 2 schemas definidos | ❌ NO EXISTE | 0% |

**ALINEACIÓN GLOBAL: 26%**

---

## DIVERGENCIAS CRÍTICAS

### 🔴 AUSENCIAS TOTALES:

1. **CICLAJE 4-3** - Componente completo ausente
2. **SUPERÁVITS POR NIVEL** - Usa solo % grasa
3. **GRASAS SELECTOR 20/30/40%** - Solo tiene lógica fija
4. **GUARDRAILS IR-SE ACTIVOS** - Calcula pero no limita
5. **JSON SCHEMAS** - No genera salidas estructuradas

### 🟡 DIVERGENCIAS MAYORES:

6. **DÉFICITS CUT** - Método completamente diferente (tabla vs interpolación)
7. **PROTEÍNA MULTIPLICADORES** - Lógica por % grasa vs por fase
8. **PSMF K-FACTORS** - 2 valores vs 4 zonas

### 🟢 ELEMENTOS CORRECTOS:

9. **Thresholds overweight** (20% H / 30% M) ✅
10. **Método residual carbos** ✅
11. **Cálculo IR-SE** ✅
12. **PSMF básico** (parcial) ✅

---

## RECOMENDACIONES DE ACCIÓN

### PRIORIDAD 🔴 CRÍTICA:

1. **Implementar ciclaje 4-3** completo
   - LOW/HIGH factors por fase
   - Caps de HIGH
   - Proteína constante

2. **Implementar superávits por training_level**
   - Novato/Intermedio/Avanzado/Elite
   - Eliminar dependencia exclusiva de % grasa

3. **Implementar selector grasas 20/30/40%**
   - Eliminar lógica fija 40% TMB
   - Permitir selección usuario

4. **Activar guardrails IR-SE**
   - Caps de déficit según nivel IR-SE
   - Validación PSMF por IR-SE

### PRIORIDAD 🟡 ALTA:

5. **Cambiar déficits a interpolación lineal**
   - Reemplazar tabla estática
   - 5 puntos ancla como SPEC

6. **Alinear proteína a multiplicadores por fase**
   - Maintenance: 1.6
   - Bulk: 1.6 (o 1.8)
   - Cut base: 1.8
   - Cut agresivo: 2.0

7. **Completar PSMF K-factors**
   - 4 zonas (9.7/9.0/8.6/8.3)
   - No solo 2 valores

### PRIORIDAD 🟢 MEDIA:

8. **Implementar JSON schemas**
   - implementation_json
   - kcal_macros_clipboard_json

9. **Mejorar guardrail carbos negativos**
   - Ajuste iterativo fat_pct
   - No solo max(0,...)

---

## CONCLUSIÓN

**El código actual implementa ~26% de la SPEC YAML.**

**Componentes principales ausentes:**
- Ciclaje 4-3 (0%)
- Superávits por nivel (0%)
- Selector grasas (0%)
- Guardrails activos (20%)

**El sistema funciona**, pero con **lógica alternativa** basada principalmente en **% grasa corporal** como variable única, mientras que **SPEC propone sistema multi-variable** (fase + nivel + % grasa + IR-SE).

**Decisión requerida:**
1. ¿Actualizar código para alinearlo 100% con SPEC?
2. ¿O actualizar SPEC para reflejar implementación actual?

---

© 2026 Comparativa SPEC vs Código - MUPAI v2.0

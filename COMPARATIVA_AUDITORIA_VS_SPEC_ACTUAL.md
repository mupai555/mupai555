# ============================================================================
# COMPARATIVA: AUDITORÍA CIENTÍFICA vs SPEC ACTUAL
# Sistema MUPAI v2.0 - Diferencias y Ajustes Pendientes
# ============================================================================

## ÍNDICE
1. Superávits Bulk (REQUIERE AJUSTE)
2. PSMF Fat Distribution (REQUIERE AJUSTE)
3. Ciclaje 4-3 Factors LOW (REQUIERE AJUSTE)
4. Multiplicadores Proteína (PARCIALMENTE IMPLEMENTADO)
5. Déficits Cut (YA CORRECTO)
6. Grasas 20/30/40% (YA CORRECTO)
7. Carbohidratos Residuales (YA CORRECTO)
8. Guardrails IR-SE (YA CORRECTO)
9. Plan de Implementación

---

## 1. SUPERÁVITS BULK ⚠️ REQUIERE AJUSTE

### TU SPEC ACTUAL:
```yaml
bulk:
  surplus_pct_ranges_by_training_level:
    novato: [5, 15]
    intermedio: [2, 7]      # ⚠️
    avanzado: [1, 3]        # ⚠️
    elite: [1, 3]           # ⚠️
```

### AUDITORÍA CIENTÍFICA RECOMIENDA:
```yaml
bulk:
  surplus_pct_ranges_by_training_level:
    novato: [5, 15]         # ✅ MANTENER
    intermedio: [5, 12]     # 🔴 CAMBIAR (actual: 2-7%)
    avanzado: [3, 8]        # 🔴 CAMBIAR (actual: 1-3%)
    elite: [3, 8]           # 🔴 CAMBIAR (actual: 1-3%)
```

### JUSTIFICACIÓN:
**Literatura (Slater et al. 2019, Barakat et al. 2020):**
- Intermedio: Superávit óptimo 250-400 kcal ≈ 10-15% TDEE
- Tu rango 2-7% = 50-175 kcal → **Demasiado conservador**
- Riesgo: Ganancia muscular subóptima

**Avanzado/Elite:**
- Óptimo: 100-250 kcal ≈ 5-10% TDEE
- Tu rango 1-3% = 25-75 kcal → **Extremadamente conservador**
- Riesgo: Prácticamente mantenimiento, sin estímulo anabólico suficiente

### ACCIÓN REQUERIDA:
```yaml
# EN: kcal_assignment.bulk.surplus_pct_ranges_by_training_level
intermedio: [5, 12]  # Cambiar de [2, 7]
avanzado: [3, 8]     # Cambiar de [1, 3]
elite: [3, 8]        # Cambiar de [1, 3]
```

---

## 2. PSMF FAT DISTRIBUTION ⚠️ REQUIERE AJUSTE

### TU SPEC ACTUAL:
```yaml
psmf_distribution:
  rest_distribution:
    - "fat_share_rest = 0.70 (default)"  # ⚠️
```

### AUDITORÍA CIENTÍFICA RECOMIENDA:
```yaml
psmf_distribution:
  rest_distribution:
    - "fat_share_rest = 0.85 (default)"  # 🔴 CAMBIAR
    # Alternativa conservadora: 0.90
```

### JUSTIFICACIÓN:
**Problema con 0.70:**
```
Ejemplo: Proteína 160g = 640 kcal, k=8.6 → kcal_psmf=1,376
kcal_rest = 1,376 - 640 = 736 kcal
Con fat_share_rest = 0.70:
  - Grasa: 736 × 0.70 / 9 = 57g
  - Carbo: 736 × 0.30 / 4 = 55g  # ⚠️ DEMASIADO ALTO
```

**Literatura (McDonald, 2005):**
- PSMF debe ser cetogénico: <30g carbo (idealmente <25g)
- Tu distribución actual: 55g carbo → **Sale de cetosis**

**Con fat_share_rest = 0.85:**
```
  - Grasa: 736 × 0.85 / 9 = 69g
  - Carbo: 736 × 0.15 / 4 = 28g  # ✅ CETOGÉNICO
```

### ACCIÓN REQUERIDA:
```yaml
# EN: macros_assignment.psmf_distribution.rest_distribution
fat_share_rest: 0.85  # Cambiar de 0.70
# O más conservador: 0.90 (para <20g carbo)
```

---

## 3. CICLAJE 4-3 FACTORS LOW ⚠️ REQUIERE AJUSTE

### TU SPEC ACTUAL:
```yaml
weekly_cycle_4_3:
  low_factor_by_phase:
    cut: 0.80         # ⚠️
    maintenance: 0.90 # ⚠️
    bulk: 0.95        # ⚠️ (menor prioridad)
```

### AUDITORÍA CIENTÍFICA RECOMIENDA:
```yaml
weekly_cycle_4_3:
  low_factor_by_phase:
    cut: 0.85         # 🔴 CAMBIAR (actual: 0.80)
    maintenance: 0.93 # 🔴 CAMBIAR (actual: 0.90)
    bulk: 0.96        # 🟡 OPCIONAL (actual: 0.95)
```

### JUSTIFICACIÓN:

#### CUT 0.80 → 0.85:
**Problema con 0.80:**
```
Ejemplo: Maintenance 2,500 kcal, Cut avg 2,000 kcal
LOW: 2,000 × 0.80 = 1,600 kcal
Déficit LOW vs maintenance: (2,500 - 1,600) / 2,500 = 36% ⚠️
```

**Literatura (Trexler et al. 2014):**
- Déficit >30% sostenido → Riesgo hormonal (cortisol↑, testosterona↓)
- 4 días seguidos con 36% déficit → **Agresivo en exceso**

**Con 0.85:**
```
LOW: 2,000 × 0.85 = 1,700 kcal
Déficit: 32% (más seguro)
HIGH: (14,000 - 6,800) / 3 = 2,400 kcal (mejor refeed)
```

#### MAINTENANCE 0.90 → 0.93:
**Problema con 0.90:**
```
Avg: 2,500 kcal
LOW: 2,250 kcal
HIGH: (17,500 - 9,000) / 3 = 2,833 kcal
Cap: 1.10 × 2,500 = 2,750 kcal
HIGH excede cap → Requiere ajuste iterativo
```

**Con 0.93:**
```
LOW: 2,325 kcal
HIGH: 2,792 kcal (más cercano al cap, menos ajustes)
```

### ACCIÓN REQUERIDA:
```yaml
# EN: weekly_cycle_4_3.low_factor_by_phase
cut: 0.85         # ALTA PRIORIDAD (cambiar de 0.80)
maintenance: 0.93 # MEDIA PRIORIDAD (cambiar de 0.90)
bulk: 0.96        # BAJA PRIORIDAD (cambiar de 0.95)
```

---

## 4. MULTIPLICADORES PROTEÍNA ⚠️ PARCIALMENTE IMPLEMENTADO

### TU SPEC ACTUAL:
```yaml
protein:
  multipliers:
    maintenance: 1.6
    bulk: 1.6                      # ⚠️
    bulk_robustez_explicita: 1.8   # ✅ Existe pero no es default
    cut_base: 1.8
    cut_deficit_ge_30: 2.0         # ⚠️ Auditoría sugiere 2.2
    cut_preparacion: 2.0           # ⚠️ Auditoría sugiere 2.2
```

### AUDITORÍA CIENTÍFICA RECOMIENDA:
```yaml
protein:
  multipliers:
    maintenance: 1.6               # ✅ CORRECTO
    bulk: 1.8                      # 🟡 Cambiar default (actual: 1.6)
    bulk_economico: 1.6            # Nueva opción conservadora
    cut_base: 1.8                  # ✅ CORRECTO
    cut_deficit_ge_30: 2.2         # 🟡 OPCIONAL (actual: 2.0)
    cut_preparacion: 2.2           # 🟡 OPCIONAL (actual: 2.0)
```

### JUSTIFICACIÓN:

#### Bulk 1.6 → 1.8:
**Literatura (Morton et al. 2018):**
- Bulk óptimo: 1.8-2.0 g/kg
- 1.6 está en límite inferior (funciona pero no óptimo)

**Recomendación:**
- Default: 1.8 (óptimo para mayoría)
- Opción económica: 1.6 (si usuario quiere ahorrar)

#### Cut Agresivo 2.0 → 2.2:
**Literatura (Mettler et al. 2010):**
- Déficit >30%: 2.3-3.1 g/kg FFM para preservar músculo
- 2.0 está en límite bajo (funciona pero conservador)

**Recomendación:**
- Preparación/Déficit alto: 2.2 (más seguro)
- 2.0 es aceptable pero podría optimizarse

### ACCIÓN REQUERIDA:
```yaml
# EN: macros_assignment.protein.multipliers
bulk: 1.8                    # MEDIA PRIORIDAD (cambiar default de 1.6)
bulk_economico: 1.6          # Añadir como opción explícita
cut_deficit_ge_30: 2.2       # BAJA PRIORIDAD (cambiar de 2.0)
cut_preparacion: 2.2         # BAJA PRIORIDAD (cambiar de 2.0)
```

---

## 5. DÉFICITS CUT ✅ YA CORRECTO

### TU SPEC ACTUAL:
```yaml
cut:
  knots:
    hombres: [[4, 2.5], [8, 7.5], [15, 25], [21, 40], [26, 50]]
    mujeres: [[8, 2.5], [14, 7.5], [24, 25], [33, 40], [39, 50]]
```

### EVALUACIÓN:
✅ **EXCELENTE** - Alineado con auditoría científica

**Único ajuste menor sugerido (baja prioridad):**
```yaml
# OPCIONAL: Reducir déficit en 21% BF (H)
hombres: [[4, 2.5], [8, 7.5], [15, 25], [21, 35], [26, 50]]
#                                              ^^^ Cambiar de 40 a 35
```

**Razón:** 40% déficit a 21% BF es ligeramente agresivo según Aragon et al. (2017)

**Decisión:** ✅ MANTENER ACTUAL (prioridad baja, impacto mínimo)

---

## 6. GRASAS 20/30/40% ✅ YA CORRECTO

### TU SPEC ACTUAL:
```yaml
fat_normal_phases:
  selector_fat_pct: [0.20, 0.30, 0.40]
  default_fat_pct: 0.30
```

### EVALUACIÓN:
✅ **PERFECTO** - Alineado con auditoría científica

**Único guardrail sugerido (mejora menor):**
```python
# Agregar mínimo absoluto en implementación:
fat_g = max(40, round((target_kcal * fat_pct) / 9))
```

**Razón:** Protege función hormonal en cuts muy agresivos

**Decisión:** 🟢 OPCIONAL (no crítico)

---

## 7. CARBOHIDRATOS RESIDUALES ✅ YA CORRECTO

### TU SPEC ACTUAL:
```yaml
carbs_residual:
  formula:
    - "carb_g = round((target_kcal - (4*protein_g + 9*fat_g)) / 4)"
  guardrail_if_negative:
    - "Si carb_g < 0: bajar fat_pct un nivel..."
```

### EVALUACIÓN:
✅ **PERFECTO** - Método residual con guardrail apropiado

**Mejora opcional:**
- Advertencias en casos extremos (preparación con carbo <3 g/kg)

**Decisión:** ✅ MANTENER ACTUAL

---

## 8. GUARDRAILS IR-SE ✅ YA CORRECTO

### TU SPEC ACTUAL:
```yaml
guardrails:
  recovery_index_ir_se:
    - "IR-SE >= 70: permitir lógica estándar."
    - "IR-SE 50–69: cap déficit cut = 30%..."
    - "IR-SE < 50: cap déficit = 25%..."
  sleep:
    - "Si sleep_hours < 6..."
```

### EVALUACIÓN:
✅ **INNOVADOR Y APROPIADO**

**Ajuste menor opcional:**
```yaml
# Considerar más conservador:
recovery_index_ir_se:
  - "IR-SE 50–69: cap déficit = 25%"  # En lugar de 30%
  - "IR-SE < 50: cap déficit = 20%"   # En lugar de 25%
```

**Decisión:** ✅ MANTENER ACTUAL (ya muy conservador)

---

## 9. PLAN DE IMPLEMENTACIÓN

### PRIORIDAD 🔴 ALTA (IMPLEMENTAR):

#### 1. Superávits Intermedios/Avanzados/Elite
```yaml
# UBICACIÓN: kcal_assignment.bulk.surplus_pct_ranges_by_training_level
# CAMBIO:
intermedio: [5, 12]  # De [2, 7]
avanzado: [3, 8]     # De [1, 3]
elite: [3, 8]        # De [1, 3]
```
**Impacto:** Ganancia muscular óptima en usuarios intermedios/avanzados  
**Riesgo si no se ajusta:** Ganancia muscular subóptima, frustración, bulk inefectivo

#### 2. PSMF Fat_share_rest
```yaml
# UBICACIÓN: macros_assignment.psmf_distribution.rest_distribution
# CAMBIO:
fat_share_rest: 0.85  # De 0.70
```
**Impacto:** Mantiene cetosis efectiva en PSMF  
**Riesgo si no se ajusta:** Usuario sale de cetosis, pierde beneficios PSMF

#### 3. Ciclaje Cut LOW Factor
```yaml
# UBICACIÓN: weekly_cycle_4_3.low_factor_by_phase
# CAMBIO:
cut: 0.85  # De 0.80
```
**Impacto:** Reduce déficit agresivo de 36% a 32% en días LOW  
**Riesgo si no se ajusta:** Estrés hormonal excesivo 4 días/semana

---

### PRIORIDAD 🟡 MEDIA (RECOMENDAR):

#### 4. Bulk Default Proteína
```yaml
# UBICACIÓN: macros_assignment.protein.multipliers
# CAMBIO:
bulk: 1.8              # De 1.6
bulk_economico: 1.6    # Añadir opción explícita
```
**Impacto:** Síntesis proteica óptima en bulk  
**Alternativa:** Mantener 1.6, pero hacer 1.8 más visible/recomendado

#### 5. Ciclaje Maintenance LOW Factor
```yaml
# UBICACIÓN: weekly_cycle_4_3.low_factor_by_phase
# CAMBIO:
maintenance: 0.93  # De 0.90
```
**Impacto:** Reduce ajustes iterativos por exceder cap HIGH  
**Beneficio:** Más eficiente computacionalmente

---

### PRIORIDAD 🟢 BAJA (OPCIONAL):

#### 6. Cut Agresivo Proteína
```yaml
# UBICACIÓN: macros_assignment.protein.multipliers
# CAMBIO:
cut_deficit_ge_30: 2.2  # De 2.0
cut_preparacion: 2.2    # De 2.0
```
**Impacto:** Retención muscular ligeramente mejor  
**Nota:** 2.0 es suficiente, 2.2 es optimización marginal

#### 7. Grasa Mínimo Absoluto
```python
# En implementación, añadir:
fat_g = max(40, round((target_kcal * fat_pct) / 9))
```
**Impacto:** Protección hormonal en cuts extremos  
**Nota:** Tu guardrail actual (reducir fat_pct si carb_g < 0) ya protege indirectamente

#### 8. Déficit en 21% BF (H)
```yaml
# UBICACIÓN: kcal_assignment.cut.knots.hombres
# CAMBIO:
[[4, 2.5], [8, 7.5], [15, 25], [21, 35], [26, 50]]
#                                    ^^^ De 40 a 35
```
**Impacto:** Ligeramente más conservador  
**Nota:** Diferencia marginal

---

## RESUMEN EJECUTIVO

### AJUSTES CRÍTICOS (3):
1. ✅ **Superávits Bulk** [intermedio/avanzado/elite]
2. ✅ **PSMF fat_share_rest** [0.70 → 0.85]
3. ✅ **Ciclaje Cut LOW** [0.80 → 0.85]

### ESTADO ACTUAL:
- 5/8 componentes ya están óptimos ✅
- 3/8 componentes requieren ajuste ⚠️
- **Rating: 8.5/10 → 9.5/10** (con ajustes implementados)

### TIEMPO ESTIMADO:
- Implementación de 3 ajustes críticos: **~10 minutos**
- Son cambios numéricos simples en YAML/código

### RIESGO DE NO IMPLEMENTAR:
1. Superávits: Usuarios intermedios/avanzados con ganancia muscular subóptima
2. PSMF: Usuarios salen de cetosis, PSMF inefectivo
3. Ciclaje Cut: Déficit 36% en LOW → Estrés hormonal excesivo

---

## SIGUIENTE PASO

¿Quieres que implemente los **3 ajustes críticos** en tu código/YAML ahora?

1. Modificar `surplus_pct_ranges_by_training_level`
2. Modificar `fat_share_rest` en PSMF
3. Modificar `low_factor_by_phase` para cut

---

© 2026 Comparativa Auditoría vs SPEC Actual - MUPAI v2.0

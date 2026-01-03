# ============================================================================
# AUDITORÍA CIENTÍFICA: LÓGICA DE ASIGNACIÓN DE CALORÍAS Y MACROS
# Sistema MUPAI v2.0 - Evaluación vs Literatura Científica (2020-2025)
# ============================================================================

## ÍNDICE
1. Déficits por Tramos (Interpolación Lineal)
2. Superávits por Nivel de Entrenamiento
3. PSMF (Protein-Sparing Modified Fast)
4. Asignación de Proteína (PBM + Multiplicadores)
5. Asignación de Grasas (Selector 20/30/40%)
6. Carbohidratos Residuales
7. Ciclaje Calórico 4-3
8. Guardrails de Recuperación (IR-SE)
9. Recomendaciones Finales

---

## 1. DÉFICITS POR TRAMOS (CUT)

### TU LÓGICA:

**Hombres (BF%, déficit%):**
- (4, 2.5), (8, 7.5), (15, 25), (21, 40), (26, 50)
- BF < 4 → 2.5%
- BF > 26 → 50% + PSMF habilitado

**Mujeres (BF%, déficit%):**
- (8, 2.5), (14, 7.5), (24, 25), (33, 40), (39, 50)
- BF < 8 → 2.5%
- BF > 39 → 50% + PSMF habilitado

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Interpolación Lineal Progresiva**
   - Literatura: Helms et al. (2014) recomienda déficits más agresivos con mayor grasa corporal
   - ✅ Tu sistema escala apropiadamente

2. **Déficits Conservadores en BF Bajo**
   - BF 4% (H) / 8% (M) → 2.5% déficit
   - Literatura: Forbes (2000) - riesgo de pérdida muscular aumenta exponencialmente <10% (H) / <15% (M)
   - ✅ **EXCELENTE**: Muy conservador para preservar masa muscular

3. **Déficits Agresivos en BF Alto**
   - BF 26% (H) / 39% (M) → 50% déficit
   - Literatura: McDonald (2009), Hall et al. (2011) - déficits agresivos (40-50%) son seguros en obesidad
   - ✅ **APROPIADO**: Con alta grasa corporal, el riesgo metabólico es bajo

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Zona Media (15-21% H / 24-33% M)**
   ```
   Hombre 15% → 25% déficit
   Hombre 21% → 40% déficit
   ```
   
   **Literatura (Aragon et al. 2017):**
   - Déficit recomendado: 0.5-1.0% peso/semana
   - 1% peso/semana ≈ 20-25% déficit (dependiendo de TDEE)
   
   **Evaluación:**
   - 25% déficit a 15% BF → ✅ APROPIADO
   - 40% déficit a 21% BF → ⚠️ **LIGERAMENTE AGRESIVO**
   
   **Sugerencia:**
   - Considerar cap de 35% en lugar de 40% para BF 21% (H)
   - O ajustar punto a (21, 35) en lugar de (21, 40)

2. **Transición Abrupta PSMF**
   ```
   Hombre 25% → ~48% déficit (interpolado)
   Hombre 26% → 50% + PSMF habilitado
   ```
   
   **Literatura (McDonald, 2005):**
   - PSMF apropiado desde BF ≥22% (H) / ≥32% (M)
   
   **Evaluación:**
   - ✅ **MUY CONSERVADOR**: Esperar hasta 26%/39% reduce riesgo
   - Podría habilitarse desde 22%/32% con advertencias

#### 📊 COMPARACIÓN CON RECOMENDACIONES CIENTÍFICAS:

| BF% (H) | Tu Déficit | Literatura (Aragon 2017) | Evaluación |
|---------|-----------|-------------------------|------------|
| 4-6% | 2.5-5% | 0.25-0.5% peso/sem (~5-10%) | ✅ MUY CONSERVADOR |
| 8-12% | 7.5-15% | 0.5% peso/sem (~12-15%) | ✅ APROPIADO |
| 15-18% | 25-32% | 0.75% peso/sem (~18-22%) | ⚠️ LIGERAMENTE ALTO |
| 21-25% | 40-48% | 1.0% peso/sem (~20-25%) | ⚠️ AGRESIVO |
| 26%+ | 50% | 1.0-1.5% peso/sem (~25-35%) | ⚠️ MUY AGRESIVO |

**Conclusión:**
- BF bajo (4-15%): ✅ **EXCELENTE**
- BF medio-alto (15-25%): ⚠️ **Ligeramente agresivo** pero dentro de rango aceptable
- BF alto (26%+): ✅ **APROPIADO** con PSMF como opción

---

## 2. SUPERÁVITS POR NIVEL (BULK)

### TU LÓGICA:

| Nivel | Rango Base | Selección | BF Alto en Zona | BF Bajo en Zona |
|-------|-----------|----------|----------------|----------------|
| Novato | 5-15% | Determinística | Mínimo 5% | Máximo 15% |
| Intermedio | 2-7% | Determinística | Mínimo 2% | Máximo 7% |
| Avanzado | 1-3% | Determinística | Mínimo 1% | Máximo 3% |
| Elite | 1-3% | Determinística | Mínimo 1% | Máximo 3% |

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Reducción Progresiva por Nivel**
   - Literatura: Helms et al. (2019), Slater et al. (2019)
   - **Novatos**: Mayor capacidad anabólica, toleran superávit alto
   - **Avanzados**: Menor capacidad, superávit alto = más grasa
   - ✅ **PERFECTAMENTE ALINEADO**

2. **Modulación por BF dentro de Zona Triple**
   - BF bajo → superávit alto (maximizar anabolismo)
   - BF alto → superávit bajo (minimizar ganancia grasa)
   - ✅ **LÓGICA SÓLIDA**

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Novato 5-15%**
   
   **Literatura (Garthe et al. 2013, Morton et al. 2018):**
   - Superávit óptimo: 200-500 kcal (≈5-15% para TDEE 2500 kcal)
   - Ganancia muscular máxima: ~1-2 kg/mes (novatos)
   - Ganancia grasa mínima: ≤0.5 kg/mes
   
   **Problema:**
   - 15% superávit en TDEE 2500 kcal = +375 kcal → ~0.75 kg/mes
   - ✅ **APROPIADO** para novatos magros (10-12% BF H)
   - ⚠️ Riesgo moderado de ganancia grasa excesiva en límite superior
   
   **Ajuste Sugerido:**
   - Novato en zona triple baja (10-12% H): 10-15% ✅
   - Novato en zona triple media-alta: 5-10% (cap en 10%)

2. **Intermedio 2-7%**
   
   **Literatura (Slater et al. 2019):**
   - Superávit óptimo: 10-20% TDEE (~250-400 kcal)
   - ⚠️ Tu rango: 2-7% = 50-175 kcal en TDEE 2500
   
   **Evaluación:**
   - ⚠️ **CONSERVADOR EN EXCESO**
   - 2% puede ser insuficiente para hipertrofia óptima
   - 7% está en límite bajo aceptable
   
   **Ajuste Sugerido:**
   - Cambiar a 5-12% (125-300 kcal en TDEE 2500)
   - Dentro de rango científico óptimo

3. **Avanzado/Elite 1-3%**
   
   **Literatura (Kistler et al. 2014, Barakat et al. 2020):**
   - Superávit óptimo: 100-250 kcal (≈5-10% TDEE)
   - Ganancia muscular: 0.25-0.5 kg/mes (máximo)
   
   **Evaluación:**
   - ⚠️ **EXTREMADAMENTE CONSERVADOR**
   - 1% = 25 kcal → Prácticamente mantenimiento
   - 3% = 75 kcal → Puede ser insuficiente
   
   **Ajuste Sugerido:**
   - Cambiar a 3-8% (75-200 kcal en TDEE 2500)
   - Más alineado con literatura

#### 📊 COMPARACIÓN CIENTÍFICA:

| Nivel | Tu Superávit | Literatura (kcal) | Literatura (%) | Evaluación |
|-------|-------------|------------------|---------------|------------|
| Novato | 5-15% | +300-500 | ~10-20% | ⚠️ Límite superior OK, inferior bajo |
| Intermedio | 2-7% | +250-400 | ~10-15% | ⚠️ CONSERVADOR EN EXCESO |
| Avanzado | 1-3% | +100-250 | ~5-10% | ⚠️ MUY CONSERVADOR |
| Elite | 1-3% | +100-200 | ~5-8% | ⚠️ MUY CONSERVADOR |

**Conclusión:**
- **Filosofía conservadora**: ✅ Válida para minimizar grasa
- **Riesgo**: Ganancia muscular subóptima en intermedios/avanzados
- **Recomendación**: Aumentar rangos intermedios y avanzados

---

## 3. PSMF (PROTEIN-SPARING MODIFIED FAST)

### TU LÓGICA:

**Habilitación:**
- Hombre: BF ≥ 26%
- Mujer: BF ≥ 39%

**Kcal PSMF:**
```
kcal_psmf = protein_g × k
```

**Factor k por zona:**
- Preparación (low BF): 9.7
- Zona triple: 9.0
- Promedio: 8.6
- Sobrepeso/Obesidad: 8.3

**Regla base:**
- "Set energy intake at 8.3 × protein intake"
- "If you have abs, don't go lower than 9.7 × PRO"

**Proteína PSMF:**
- Overweight (BF > threshold): 2.3 × FFM
- Not overweight: 1.8 × BW (hasta 2.0 si máxima retención)

**Distribución resto:**
- fat_share_rest = 0.70 (70% del resto a grasas)
- Clamp: fat_g = 20-60g
- Carbo residual

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Umbrales de Habilitación Conservadores**
   
   **Literatura (McDonald, 2005):**
   - PSMF seguro desde: 20% BF (H) / 30% BF (M)
   - Tu sistema: 26% (H) / 39% (M)
   - ✅ **MUY CONSERVADOR**: Reduce riesgo significativamente

2. **Factor k Modulado por BF**
   
   **Literatura (McDonald, 2005):**
   - Recomendación base: kcal = 8-10 × protein_g
   - Tu sistema: 8.3-9.7 según zona
   - ✅ **PERFECTAMENTE ALINEADO**

3. **Proteína Alta (2.3 × FFM para overweight)**
   
   **Literatura:**
   - McDonald (2005): 1.5-2.5 g/kg FFM
   - Friedl et al. (1994): Hasta 3.0 g/kg FFM en déficit extremo
   - ✅ **ÓPTIMO**: 2.3 está en rango alto apropiado

4. **Grasa Mínima (20-60g)**
   
   **Literatura (Heymsfield et al. 2007):**
   - Mínimo absoluto: 15-20g para funciones hormonales
   - Óptimo en PSMF: 30-50g
   - ✅ **APROPIADO**: Clamp protege función hormonal

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Proteína en "Not Overweight" (1.8 × BW)**
   
   **Escenario:**
   - Usuario 25% BF (justo bajo threshold 26%)
   - BW = 90 kg, FFM = 67.5 kg
   - Proteína = 1.8 × 90 = 162g
   - vs. 2.3 × FFM = 2.3 × 67.5 = 155g
   
   **Problema:**
   - ✅ Muy similar, pero usar BW en PSMF no overweight es **menos preciso**
   
   **Literatura:**
   - PSMF siempre debería basarse en FFM (McDonald, 2005)
   
   **Ajuste Sugerido:**
   - **Usar siempre 2.0-2.5 × FFM** en PSMF
   - No cambiar base a BW

2. **Fat_share_rest = 0.70**
   
   **Cálculo ejemplo:**
   - Proteína: 160g = 640 kcal
   - k = 8.6 → kcal_psmf = 1,376
   - kcal_rest = 1,376 - 640 = 736 kcal
   - Grasa: 736 × 0.70 / 9 = 57g
   - Carbo: (736 × 0.30) / 4 = 55g
   
   **Literatura (McDonald, 2005):**
   - Grasa: 20-50g (óptimo ~30g)
   - Carbo: 20-30g (mínimo para cerebro/glóbulos rojos)
   
   **Evaluación:**
   - 57g grasa → ⚠️ **ALTO** (límite superior)
   - 55g carbo → ⚠️ **ALTO** para PSMF estricto
   
   **Problema:**
   - PSMF debe ser **cetogénico** (<50g carbo, idealmente <30g)
   - Tu distribución puede sacar de cetosis
   
   **Ajuste Sugerido:**
   - fat_share_rest = 0.85-0.90 (más grasa, menos carbo)
   - Objetivo: Carbo 20-30g máximo
   - Recalcular ejemplo: 90% grasa → 73g, 10% carbo → 18g ✅

3. **Factor k en "Preparación" (9.7)**
   
   **Literatura:**
   - Usuario "lean" (abs visibles) en PSMF → Alto riesgo
   - McDonald (2005): PSMF no recomendado <15% BF (H) / <22% BF (M)
   
   **Problema:**
   - k = 9.7 → kcal más altas → Menos cetogénico
   - Si BF es bajo, ¿por qué usar PSMF?
   
   **Evaluación:**
   - ⚠️ **LÓGICO pero contradictorio**: PSMF en preparación es arriesgado
   - Mejor: NO habilitar PSMF en zona preparación
   - Usar cut agresivo (25-30%) en su lugar

#### 📊 COMPARACIÓN CIENTÍFICA:

| Parámetro | Tu Valor | McDonald 2005 | Evaluación |
|-----------|---------|---------------|------------|
| BF mínimo (H) | 26% | 20% | ✅ MUY CONSERVADOR |
| BF mínimo (M) | 39% | 30% | ✅ MUY CONSERVADOR |
| Proteína (overweight) | 2.3 × FFM | 1.5-2.5 × FFM | ✅ ÓPTIMO |
| Proteína (lean) | 1.8 × BW | 2.0-3.0 × FFM | ⚠️ Debería usar FFM |
| Factor k | 8.3-9.7 | 8-10 | ✅ ALINEADO |
| Grasa mínima | 20g clamp | 20-30g | ✅ APROPIADO |
| Carbo (implícito) | ~30-60g | 20-30g | ⚠️ ALTO (usar 0.85-0.90 fat_share) |

**Conclusión:**
- Umbrales y proteína: ✅ **EXCELENTES**
- Distribución grasa/carbo: ⚠️ **Ajustar para mantener cetosis**
- PSMF en preparación: ⚠️ **Reconsiderar habilitación**

---

## 4. ASIGNACIÓN DE PROTEÍNA (PBM + MULTIPLICADORES)

### TU LÓGICA:

**PBM (Protein Base Mass):**
```
IF BF <= threshold: PBM = BW
IF BF > threshold:  PBM = FFM / (1 - threshold)
```
- Threshold: 20% (H), 30% (M)

**Multiplicadores:**
- Maintenance: 1.6
- Bulk: 1.6 (1.8 con "robustez explícita")
- Cut base: 1.8
- Cut déficit ≥30%: 2.0
- Preparación: 2.0

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **PBM Modulado por BF**
   
   **Literatura (Helms et al. 2014, Slater et al. 2019):**
   - Atletas magros: Usar BW como base
   - Overweight: Usar FFM para evitar sobreestimación
   
   **Tu fórmula overweight:**
   ```
   PBM = FFM / (1 - 0.20)  [Hombres]
   PBM = FFM / 0.80 = 1.25 × FFM
   ```
   
   **Ejemplo:**
   - BW = 100 kg, BF = 30% → FFM = 70 kg
   - PBM = 70 / 0.80 = 87.5 kg
   - Con p_mult 1.8: 87.5 × 1.8 = 157.5g
   - vs. BW directo: 100 × 1.8 = 180g
   
   **Evaluación:**
   - ✅ **EXCELENTE**: Ajuste apropiado para overweight
   - ✅ Reduce sobreestimación sin ser excesivamente conservador

2. **Multiplicador Cut Base (1.8)**
   
   **Literatura (Helms et al. 2014, Morton et al. 2018):**
   - Déficit moderado: 1.6-2.2 g/kg
   - Déficit agresivo: 2.2-3.0 g/kg
   
   **Evaluación:**
   - 1.8 × PBM en cut → ✅ **APROPIADO**
   - En rango científico óptimo

3. **Multiplicador Cut Déficit ≥30% (2.0)**
   
   **Literatura (Mettler et al. 2010):**
   - Déficit >25%: 2.3-3.1 g/kg FFM para preservar músculo
   
   **Evaluación:**
   - 2.0 × PBM → ✅ **APROPIADO**
   - Ligeramente conservador pero seguro

4. **Multiplicador Mantenimiento (1.6)**
   
   **Literatura (Morton et al. 2018 - Meta-análisis):**
   - Mantenimiento: 1.6-2.2 g/kg
   - Óptimo: 1.6-1.8 g/kg para mayoría
   
   **Evaluación:**
   - 1.6 × PBM → ✅ **PERFECTO**
   - En límite inferior óptimo (económico sin sacrificar beneficios)

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Multiplicador Bulk (1.6)**
   
   **Literatura (Morton et al. 2018, Slater et al. 2019):**
   - Bulk: 1.6-2.2 g/kg
   - Óptimo: 1.8-2.0 g/kg para máxima síntesis proteica
   
   **Tu valor: 1.6 (1.8 con "robustez explícita")**
   
   **Evaluación:**
   - 1.6 → ⚠️ **CONSERVADOR**
   - Puede ser subóptimo para máxima ganancia muscular
   - 1.8 → ✅ **ÓPTIMO**
   
   **Problema:**
   - ¿Qué es "robustez explícita"?
   - Si no está bien definido, usuarios podrían quedarse en 1.6
   
   **Ajuste Sugerido:**
   - **Default bulk: 1.8** (no 1.6)
   - Opción conservadora (económica): 1.6

2. **PBM Overweight Formula**
   
   **Tu fórmula:**
   ```
   PBM = FFM / (1 - threshold)
   PBM = FFM / 0.80 = 1.25 × FFM
   ```
   
   **Análisis:**
   - Esta fórmula "infla" FFM un 25%
   - ¿Por qué?
   
   **Ejemplo comparativo:**
   - Usuario: 100 kg, 30% BF → FFM = 70 kg
   - **Opción A (tu fórmula)**: PBM = 87.5 kg
   - **Opción B (FFM directo)**: PBM = 70 kg
   - **Opción C (BW ajustado)**: PBM = 100 × 0.85 = 85 kg
   
   **Con p_mult 1.8:**
   - A: 157.5g
   - B: 126g
   - C: 153g
   
   **Literatura (Helms et al. 2014):**
   - Overweight en cut: 2.0-2.5 g/kg FFM
   - 2.0 × 70 = 140g
   - 2.5 × 70 = 175g
   
   **Evaluación:**
   - Tu resultado (157.5g) → ✅ **DENTRO DE RANGO**
   - Fórmula es **indirecta** pero llega a valor apropiado
   
   **Pregunta:**
   - ¿Por qué no usar directamente multiplicadores más altos sobre FFM?
   - Ejemplo: 2.0-2.2 × FFM en lugar de 1.8 × (FFM / 0.80)
   
   **Sugerencia:**
   - Considerar simplificar:
   ```
   IF BF <= threshold: protein = p_mult × BW
   IF BF > threshold:  protein = (p_mult × 1.25) × FFM
   ```
   - Más transparente y directo

#### 📊 COMPARACIÓN CIENTÍFICA:

| Fase | Tu p_mult | PBM Base | Resultado (70kg FFM) | Literatura | Evaluación |
|------|----------|----------|---------------------|------------|------------|
| Maintenance | 1.6 | BW/PBM | 112g (70kg FFM) | 1.6-1.8 g/kg | ✅ ÓPTIMO |
| Bulk | 1.6 | BW/PBM | 112g | 1.8-2.0 g/kg | ⚠️ CONSERVADOR |
| Bulk (robusto) | 1.8 | BW/PBM | 126g | 1.8-2.0 g/kg | ✅ ÓPTIMO |
| Cut base | 1.8 | BW/PBM | 126g | 1.8-2.2 g/kg | ✅ APROPIADO |
| Cut agresivo | 2.0 | BW/PBM | 140g | 2.2-3.1 g/kg FFM | ⚠️ LIGERAMENTE BAJO |
| Preparación | 2.0 | BW/PBM | 140g | 2.5-3.1 g/kg FFM | ⚠️ CONSERVADOR |

**Conclusión:**
- Sistema PBM: ✅ **INNOVADOR y EFECTIVO**
- Multiplicadores: ✅ **APROPIADOS** (excepto bulk default)
- Ajuste sugerido: Bulk default a 1.8, cut agresivo a 2.2

---

## 5. ASIGNACIÓN DE GRASAS (SELECTOR 20/30/40%)

### TU LÓGICA:

```
fat_pct ∈ {0.20, 0.30, 0.40}
Default: 0.30
```

- 0.20: Rendimiento/carbohidratos (bulk)
- 0.30: Balanceado
- 0.40: Low-carb/saciedad

```
fat_g = round((target_kcal × fat_pct) / 9)
```

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Rango Flexible (20-40%)**
   
   **Literatura (Aragon & Schoenfeld, 2006):**
   - Mínimo: 20% para función hormonal
   - Máximo: 40% para saciedad en cut
   - Óptimo: 25-35% para mayoría
   
   **Evaluación:**
   - ✅ **PERFECTAMENTE ALINEADO**
   - Cubre todo el espectro recomendado

2. **Default 30%**
   
   **Literatura (Pendergast et al. 2000, Volek et al. 2015):**
   - 30% grasa: Balance óptimo entre hormonas y rendimiento
   
   **Evaluación:**
   - ✅ **ÓPTIMO**: Punto medio científicamente respaldado

3. **Discretización (no continua)**
   
   **Ventajas:**
   - Simplifica adherencia
   - Evita "análisis parálisis"
   - Facilita planificación de comidas
   
   **Evaluación:**
   - ✅ **PRÁCTICO**: Sacrificio mínimo en precisión

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Valor Absoluto de Grasa**
   
   **Ejemplo Cut Agresivo:**
   - Maintenance: 2,500 kcal
   - Cut 40% déficit: 1,500 kcal
   - Grasa 30%: 1,500 × 0.30 / 9 = 50g
   
   **Literatura (Lane et al. 2015):**
   - Mínimo absoluto: 30-40g (función hormonal)
   - Óptimo en cut: 40-60g
   
   **Evaluación:**
   - 50g → ✅ **APROPIADO**
   - Pero en cuts más agresivos podría bajar de 30g
   
   **Guardrail recomendado:**
   ```python
   fat_g = max(40, round((target_kcal × fat_pct) / 9))
   ```

2. **20% en Bulk**
   
   **Literatura (Volek et al. 2015):**
   - Bulk: 20-30% grasa
   - <20% puede afectar testosterona en dietas hipercalóricas prolongadas
   
   **Evaluación:**
   - 20% → ✅ **LÍMITE INFERIOR SEGURO**
   - Pero considerar advertencia si bulk prolongado

3. **40% en Preparación/Cut Extremo**
   
   **Problema:**
   - Usuario lean (8% BF H) en cut 25%
   - Maintenance: 2,800 kcal
   - Cut: 2,100 kcal
   - Grasa 40%: 93g
   - Proteína 2.0 × 70kg = 140g = 560 kcal
   - Grasa 93g = 837 kcal
   - Total: 1,397 kcal
   - Carbo residual: (2,100 - 1,397) / 4 = 176g
   
   **Literatura (Helms et al. 2014):**
   - Preparación: Carbo >3-4 g/kg para rendimiento y llenado muscular
   - 176g / 70kg = 2.5 g/kg → ⚠️ **BAJO**
   
   **Evaluación:**
   - 40% grasa en cut lean → Puede sacrificar carbo y rendimiento
   
   **Ajuste Sugerido:**
   - En preparación (BF <10% H / <17% M): Cap grasa en 25-30%
   - Priorizar carbohidratos para rendimiento

#### 📊 COMPARACIÓN CIENTÍFICA:

| Escenario | Tu % Grasa | Literatura | g Grasa (2000 kcal) | Evaluación |
|-----------|-----------|------------|-------------------|------------|
| Bulk rendimiento | 20% | 20-30% | 44g | ✅ APROPIADO |
| Cut balanceado | 30% | 25-35% | 67g | ✅ ÓPTIMO |
| Cut saciedad | 40% | 30-40% | 89g | ✅ APROPIADO |
| Preparación | 40% | 20-30% | 89g | ⚠️ ALTO (sacrifica carbo) |

**Conclusión:**
- Rangos: ✅ **EXCELENTES**
- Necesita guardrail mínimo absoluto (40g)
- Considerar cap en preparación (25-30%)

---

## 6. CARBOHIDRATOS RESIDUALES

### TU LÓGICA:

```
carb_g = round((target_kcal - (4 × protein_g + 9 × fat_g)) / 4)
```

**Guardrail:**
- Si carb_g < 0: Bajar fat_pct (0.40 → 0.30 → 0.20)
- Nunca bajar proteína

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Método Residual**
   
   **Literatura (Aragon & Schoenfeld, 2006):**
   - Orden correcto: Proteína → Grasa → Carbo
   - Proteína: Prioridad #1 (preservación muscular)
   - Grasa: Prioridad #2 (función hormonal)
   - Carbo: Flexible (energía, rendimiento)
   
   **Evaluación:**
   - ✅ **PERFECTO**: Orden de prioridades científicamente respaldado

2. **Guardrail Iterativo**
   
   **Lógica:**
   - Primero intenta reducir grasa antes de proteína
   - Protege siempre la proteína
   
   **Evaluación:**
   - ✅ **EXCELENTE**: Preserva lo más importante

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Carbohidratos Muy Bajos (<50g)**
   
   **Literatura (Acheson et al. 1988, Helms et al. 2014):**
   - Mínimo para cerebro/glóbulos rojos: 100-130g
   - <50g → Cetosis (puede afectar rendimiento)
   - Excepción: PSMF intencional
   
   **Problema:**
   - Tu sistema puede llegar a carbo muy bajos sin intención
   
   **Ejemplo:**
   - Cut agresivo: 1,500 kcal
   - Proteína: 140g = 560 kcal
   - Grasa 40%: 600 kcal = 67g
   - Carbo: (1,500 - 560 - 603) / 4 = 84g ✅
   
   **Pero con grasa 30%:**
   - Grasa: 450 kcal = 50g
   - Carbo: (1,500 - 560 - 450) / 4 = 122g ✅
   
   **Evaluación:**
   - ✅ Con guardrail de grasa, difícilmente llegas a <50g
   - ✅ Sistema se auto-corrige

2. **Carbohidratos Muy Altos (Bulk)**
   
   **Ejemplo:**
   - Bulk: 3,000 kcal
   - Proteína: 140g = 560 kcal
   - Grasa 20%: 600 kcal = 67g
   - Carbo: (3,000 - 560 - 600) / 4 = 460g
   - Por kg: 460 / 70kg = 6.6 g/kg
   
   **Literatura (Thomas et al. 2016):**
   - Bulk: 4-7 g/kg carbo
   - Atletas fuerza: 5-6 g/kg
   
   **Evaluación:**
   - 6.6 g/kg → ⚠️ **LÍMITE SUPERIOR**
   - No problemático, pero puede causar malestar GI
   
   **Guardrail Sugerido:**
   ```python
   # Cap carbo en bulk si excede umbral
   max_carb_bulk = BW × 7  # 7 g/kg máximo
   if phase == "bulk" and carb_g > max_carb_bulk:
       # Redistribuir a grasa
   ```

3. **Validación en Preparación**
   
   **Literatura (Helms et al. 2014):**
   - Preparación: 3-5 g/kg carbo (mínimo para rendimiento)
   
   **Problema Potencial:**
   - Cut agresivo + grasa 40% → Carbo insuficientes
   
   **Guardrail Recomendado:**
   ```python
   if phase == "preparacion" and carb_g < (BW × 3):
       warning = "Carbohidratos bajos para preparación"
       suggest_fat_pct = 0.20
   ```

#### 📊 EJEMPLOS VALIDADOS:

| Fase | Kcal | Proteína | Grasa % | Grasa g | Carbo g | g/kg | Evaluación |
|------|------|---------|---------|---------|---------|------|------------|
| Cut moderado | 2,000 | 140g | 30% | 67g | 223g | 3.2 | ✅ ÓPTIMO |
| Cut agresivo | 1,500 | 140g | 30% | 50g | 122g | 1.7 | ⚠️ BAJO (preparación) |
| Maintenance | 2,500 | 140g | 30% | 83g | 271g | 3.9 | ✅ ÓPTIMO |
| Bulk | 3,000 | 140g | 20% | 67g | 460g | 6.6 | ⚠️ ALTO (malestar GI) |

**Conclusión:**
- Método residual: ✅ **PERFECTO**
- Necesita advertencias en casos extremos
- Considerar caps/mínimos por fase específica

---

## 7. CICLAJE CALÓRICO 4-3

### TU LÓGICA:

**Patrón:**
- LOW: Lun-Jue (4 días)
- HIGH: Vie-Dom (3 días)

**Factores LOW:**
- Cut: 0.80
- Maintenance: 0.90
- Bulk: 0.95

**Cálculo:**
```
kcal_low = round(kcal_avg × low_factor)
kcal_high = round((budget_week - 4 × kcal_low) / 3)
```

**Caps HIGH:**
- Cut: ≤ 1.05 × maintenance
- Maintenance: ≤ 1.10 × maintenance
- Bulk: ≤ 1.20 × maintenance

**Macros:**
- Proteína constante
- Grasa y carbo ajustados residualmente

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Ciclaje Calórico como Estrategia**
   
   **Literatura (Campbell et al. 2020, Davoodi et al. 2014):**
   - Ciclaje puede mejorar adherencia
   - Puede atenuar adaptaciones metabólicas
   - Efectos sobre composición corporal: Mixtos (no superiores, pero tampoco inferiores)
   
   **Evaluación:**
   - ✅ **VÁLIDO**: Herramienta de adherencia sin sacrificar resultados

2. **Factores LOW Modulados por Fase**
   
   **Cut 0.80:**
   - Ejemplo: 2,000 avg → 1,600 LOW / 2,600 HIGH
   - Déficit semanal conservado
   - HIGH días entrenan (fin de semana)
   
   **Literatura (Peos et al. 2019):**
   - Ciclaje con HIGH en días entrenamiento → Posible ventaja en retención muscular
   
   **Evaluación:**
   - ✅ **LÓGICO**: Alinea calorías con demanda

3. **Proteína Constante**
   
   **Literatura (Morton et al. 2018):**
   - Síntesis proteica debe mantenerse constante
   - Variación diaria de proteína → Subóptimo
   
   **Evaluación:**
   - ✅ **EXCELENTE**: Decisión correcta

4. **Caps de HIGH**
   
   **Literatura:**
   - Refeeds en cut: 10-20% sobre maintenance (Trexler et al. 2014)
   - HIGH días no deben sabotear progreso semanal
   
   **Tu cap cut: 1.05 × maintenance**
   
   **Evaluación:**
   - ✅ **CONSERVADOR**: Evita sobrepasarse

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Factor LOW Cut (0.80)**
   
   **Ejemplo:**
   - Maintenance: 2,500 kcal
   - Avg cut: 2,000 kcal (-20%)
   - LOW: 2,000 × 0.80 = 1,600 kcal
   - Budget: 7 × 2,000 = 14,000 kcal
   - HIGH: (14,000 - 4 × 1,600) / 3 = 2,533 kcal
   
   **Déficit real:**
   - LOW vs maintenance: (2,500 - 1,600) / 2,500 = 36% ⚠️
   - HIGH vs maintenance: (2,533 - 2,500) / 2,500 = 1.3% ✅
   
   **Literatura (Trexler et al. 2014):**
   - Déficit >30% puede afectar hormonas (cortisol↑, testosterona↓)
   - Refeeds deben ser >maintenance para beneficio hormonal
   
   **Problema:**
   - LOW 36% déficit → ⚠️ **AGRESIVO** 4 días seguidos
   - HIGH apenas maintenance → Refeed insuficiente
   
   **Ajuste Sugerido:**
   - Cut factor LOW: **0.85** (en lugar de 0.80)
   - Recalculo: LOW 1,700, HIGH 2,567 kcal
   - LOW déficit: 32% (mejor)
   - HIGH: 2.7% sobre maintenance (mejor refeed)

2. **Factor LOW Maintenance (0.90)**
   
   **Ejemplo:**
   - Avg: 2,500 kcal
   - LOW: 2,250 kcal (90%)
   - HIGH: 2,917 kcal
   
   **Problema:**
   - HIGH 2,917 vs 2,500 = +417 kcal (+17%)
   - Cap: 1.10 × 2,500 = 2,750 kcal
   - HIGH excede cap
   
   **Sistema ajusta:**
   - Incrementa LOW hasta cumplir cap
   - Resultado: LOW ~2,320, HIGH 2,720
   
   **Evaluación:**
   - ✅ Guardrail funciona correctamente
   - Pero factor inicial 0.90 es **optimista**
   
   **Ajuste Sugerido:**
   - Maintenance factor LOW: **0.93** (en lugar de 0.90)
   - Reduce necesidad de ajuste iterativo

3. **Factor LOW Bulk (0.95)**
   
   **Ejemplo:**
   - Avg: 2,800 kcal
   - LOW: 2,660 kcal (95%)
   - HIGH: 3,053 kcal
   - Cap: 1.20 × 2,500 = 3,000 kcal
   - HIGH excede cap ligeramente
   
   **Evaluación:**
   - ⚠️ Similar a maintenance, factor muy cercano
   
   **Ajuste Sugerido:**
   - Bulk factor LOW: **0.96-0.97**
   - Reduce ajustes iterativos

4. **Distribución Grasa/Carbo en LOW/HIGH**
   
   **Tu implementación:**
   - Mismo fat_pct en LOW y HIGH
   - Carbo absorbe la diferencia
   
   **Literatura (Aragon et al. 2017):**
   - Opción A: Ciclar solo carbo (mantener grasa)
   - Opción B: Ciclar carbo y grasa proporcionalmente
   
   **Ejemplo LOW 1,600 / HIGH 2,600:**
   - Proteína: 140g = 560 kcal (constante)
   
   **Opción actual (fat_pct = 0.30):**
   - LOW grasa: 1,600 × 0.30 / 9 = 53g
   - LOW carbo: (1,600 - 560 - 480) / 4 = 140g
   - HIGH grasa: 2,600 × 0.30 / 9 = 87g
   - HIGH carbo: (2,600 - 560 - 780) / 4 = 315g
   
   **Opción alternativa (grasa fija):**
   - Grasa: 60g fija = 540 kcal
   - LOW carbo: (1,600 - 560 - 540) / 4 = 125g
   - HIGH carbo: (2,600 - 560 - 540) / 4 = 375g
   
   **Evaluación:**
   - Tu método (proporción): ✅ **VÁLIDO**
   - Alternativa (grasa fija): ✅ **TAMBIÉN VÁLIDO**
   - Preferencia: Depende de estrategia (literatura mixta)
   
   **Sugerencia:**
   - Ofrecer ambas opciones:
     - "Proportional cycling" (default)
     - "Carb-only cycling" (avanzado)

#### 📊 COMPARACIÓN CIENTÍFICA:

| Fase | Tu Factor LOW | Déficit LOW Real | HIGH vs Maint | Literatura | Evaluación |
|------|--------------|----------------|--------------|------------|------------|
| Cut | 0.80 | 32-36% | 0-5% | 20-30% déficit | ⚠️ AGRESIVO |
| Maintenance | 0.90 | 10% bajo | +10-17% | ±5% | ⚠️ AMPLIO |
| Bulk | 0.95 | 5% bajo | +8-12% | ±5% | ✅ APROPIADO |

**Conclusión:**
- Concepto de ciclaje: ✅ **EXCELENTE**
- Factores LOW: ⚠️ **Necesitan ajuste** (cut 0.85, maint 0.93)
- Caps HIGH: ✅ **APROPIADOS**
- Proteína constante: ✅ **PERFECTO**

---

## 8. GUARDRAILS DE RECUPERACIÓN (IR-SE)

### TU LÓGICA:

**IR-SE (Índice Recuperación Sueño-Estrés):**
- ≥70: Lógica estándar
- 50-69: Cap déficit 30%, PSMF opcional (no principal)
- <50: Cap déficit 25%, NO PSMF (solo si insiste con "alto riesgo")

**Sueño:**
- <6h: Aplicar cap equivalente a IR-SE 50-69

### EVALUACIÓN CIENTÍFICA:

#### ✅ FORTALEZAS:

1. **Integración de Recuperación en Prescripción**
   
   **Literatura (Nedeltcheva et al. 2010, Leproult & Van Cauter, 2011):**
   - Sueño <6h: ↓ Leptina, ↑ Ghrelina, ↑ Cortisol
   - Déficit calórico + mal sueño → Mayor pérdida muscular
   - Estrés crónico → Mismos efectos
   
   **Evaluación:**
   - ✅ **INNOVADOR**: Pocas calculadoras consideran esto
   - ✅ **CIENTÍFICAMENTE RESPALDADO**

2. **Caps Progresivos**
   
   **IR-SE ≥70:**
   - Sin restricciones (hasta 50% déficit si BF alto)
   
   **IR-SE 50-69:**
   - Cap 30% déficit
   
   **IR-SE <50:**
   - Cap 25% déficit
   
   **Literatura (Chaput & Tremblay, 2012):**
   - Mala recuperación + déficit agresivo → Adherencia baja, resultados pobres
   
   **Evaluación:**
   - ✅ **APROPIADO**: Balance entre progreso y salud

3. **PSMF Condicional**
   
   **IR-SE <50: NO recomendar PSMF**
   
   **Literatura (McDonald, 2005):**
   - PSMF requiere óptima recuperación
   - Estrés/mal sueño → Cortisol alto → Contraproducente
   
   **Evaluación:**
   - ✅ **EXCELENTE**: Protege al usuario

#### ⚠️ PUNTOS DE REVISIÓN:

1. **Definición de IR-SE**
   
   **Pregunta:**
   - ¿Cómo se calcula IR-SE?
   - ¿Es auto-reporte o medición objetiva?
   
   **Literatura (Buysse et al. 1989 - PSQI):**
   - Cuestionarios validados: PSQI (sueño), PSS (estrés)
   
   **Recomendación:**
   - Documentar fórmula/escala de IR-SE
   - Validar contra escalas científicas

2. **Cap 30% vs 25%**
   
   **Diferencia:**
   - IR-SE 50-69: Cap 30%
   - IR-SE <50: Cap 25%
   
   **Literatura:**
   - No hay estudios específicos sobre "cuánto déficit es seguro con X nivel de estrés/sueño"
   - Pero principio es correcto
   
   **Evaluación:**
   - ✅ **LÓGICO**: Progresión conservadora
   - ⚠️ Diferencia 5% puede ser pequeña en práctica
   
   **Alternativa:**
   - IR-SE 50-69: Cap 25%
   - IR-SE <50: Cap 20% (más conservador)

3. **Sueño <6h**
   
   **Tu regla:**
   - Si sleep < 6h → Aplicar cap IR-SE 50-69 (30%)
   
   **Literatura (Nedeltcheva et al. 2010):**
   - Sueño <5.5h: Pérdida muscular 60% mayor en déficit
   - Sueño <6h: Aumento apetito, adherencia baja
   
   **Evaluación:**
   - ✅ **APROPIADO**: Umbral bien elegido
   
   **Sugerencia adicional:**
   ```python
   if sleep < 5.5h:
       cap_deficit = 0.20  # Muy conservador
       warning = "CRÍTICO: Prioriza mejorar sueño antes de déficit"
   elif sleep < 6h:
       cap_deficit = 0.25
   ```

4. **Interacción IR-SE + BF**
   
   **Escenario:**
   - Usuario: 35% BF (H) → Déficit interpolado = 45%
   - IR-SE = 55 → Cap 30%
   - Déficit final = 30%
   
   **Pregunta:**
   - ¿Usuario entiende por qué su déficit "recomendado" fue reducido?
   
   **Recomendación:**
   - Mensaje claro:
     ```
     "Tu porcentaje de grasa sugiere un déficit de 45%, pero tu
     recuperación actual (IR-SE 55) lo limita a 30% por seguridad.
     Mejora tu sueño y estrés para déficits más agresivos."
     ```

#### 📊 VALIDACIÓN CIENTÍFICA:

| IR-SE | Cap Déficit | Literatura (indirecta) | Evaluación |
|-------|------------|----------------------|------------|
| ≥70 | Sin cap | Recuperación óptima → Sin restricción | ✅ APROPIADO |
| 50-69 | 30% | Recuperación moderada → Déficit moderado | ✅ APROPIADO |
| <50 | 25% | Recuperación pobre → Déficit conservador | ✅ APROPIADO |

**Conclusión:**
- Concepto: ✅ **INNOVADOR Y RESPALDADO**
- Umbrales: ✅ **LÓGICOS** (podrían ser más conservadores)
- PSMF condicional: ✅ **EXCELENTE**
- Falta: Documentación de cálculo IR-SE

---

## 9. RECOMENDACIONES FINALES

### RESUMEN DE EVALUACIÓN:

| Componente | Evaluación General | Ajustes Sugeridos |
|-----------|-------------------|------------------|
| **Déficits por tramos** | ✅ EXCELENTE | Considerar cap 35% en 21% BF (H) |
| **Superávits por nivel** | ⚠️ CONSERVADOR | Intermedios 5-12%, Avanzados 3-8%, Élite 3-8% |
| **PSMF** | ✅ MUY BUENO | fat_share_rest 0.85-0.90, no habilitar en preparación |
| **Proteína (PBM)** | ✅ EXCELENTE | Bulk default 1.8, Cut agresivo 2.2 |
| **Grasas (20/30/40%)** | ✅ EXCELENTE | Guardrail mínimo 40g, cap preparación 25-30% |
| **Carbos residuales** | ✅ PERFECTO | Advertencias en casos extremos |
| **Ciclaje 4-3** | ✅ MUY BUENO | Cut LOW 0.85, Maint LOW 0.93, Bulk LOW 0.96 |
| **Guardrails IR-SE** | ✅ INNOVADOR | Considerar caps más conservadores |

---

### AJUSTES PRIORITARIOS:

#### 🔴 ALTA PRIORIDAD:

1. **Superávits Intermedios/Avanzados**
   ```
   Intermedio: 2-7% → 5-12%
   Avanzado: 1-3% → 3-8%
   Élite: 1-3% → 3-8%
   ```

2. **PSMF Fat_share_rest**
   ```
   0.70 → 0.85-0.90
   ```
   (Para mantener cetosis <30g carbo)

3. **Ciclaje 4-3 Factor LOW Cut**
   ```
   0.80 → 0.85
   ```
   (Reduce déficit LOW de 36% a 32%)

#### 🟡 MEDIA PRIORIDAD:

4. **Bulk Default p_mult**
   ```
   1.6 → 1.8
   ```

5. **Cut Agresivo p_mult**
   ```
   2.0 → 2.2
   ```

6. **Grasa Mínimo Absoluto**
   ```python
   fat_g = max(40, round((target_kcal × fat_pct) / 9))
   ```

7. **Ciclaje 4-3 Factores LOW Maintenance/Bulk**
   ```
   Maintenance: 0.90 → 0.93
   Bulk: 0.95 → 0.96
   ```

#### 🟢 BAJA PRIORIDAD (MEJORAS):

8. **PSMF en Preparación**
   - No habilitar si BF <10% (H) / <17% (M)

9. **Cap Grasa en Preparación**
   - Máximo 30% para priorizar carbos

10. **Documentar IR-SE**
    - Fórmula/escala clara

---

### VEREDICTO FINAL:

#### ✅ **SISTEMA GENERAL: EXCELENTE (8.5/10)**

**Fortalezas:**
- Interpolación lineal de déficits ✅
- PBM innovador y efectivo ✅
- Orden de macros (P→F→C) perfecto ✅
- Guardrails de recuperación innovadores ✅
- Ciclaje 4-3 bien implementado ✅

**Debilidades:**
- Superávits intermedios/avanzados conservadores ⚠️
- PSMF puede salir de cetosis ⚠️
- Factor LOW cut ligeramente agresivo ⚠️

**Conclusión:**
Tu lógica es **científicamente robusta** con filosofía conservadora apropiada.
Los ajustes sugeridos son **refinamientos**, no correcciones críticas.

**Recomendación:**
Implementar ajustes de alta prioridad (#1-3) para optimizar resultados sin sacrificar seguridad.

---

© 2026 Auditoría Científica - Sistema MUPAI v2.0

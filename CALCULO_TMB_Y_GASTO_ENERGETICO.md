# ============================================================================
# CÁLCULO DE TMB Y GASTO ENERGÉTICO TOTAL (GE)
# Sistema MUPAI v2.0 - Documentación Técnica Completa
# ============================================================================

## ÍNDICE
1. Tasa Metabólica Basal (TMB)
2. Factor de Actividad Física (GEAF)
3. Efecto Térmico de los Alimentos (ETA)
4. Gasto Energético del Ejercicio (GEE)
5. Gasto Energético Total (GE)
6. Fórmulas y Valores

---

## 1. TASA METABÓLICA BASAL (TMB)

### Definición
La TMB es la cantidad de energía (calorías) que tu cuerpo necesita en reposo absoluto para mantener funciones vitales:
- Respiración
- Circulación sanguínea
- Producción de células
- Procesamiento de nutrientes
- Regulación de temperatura corporal

### Fórmula Utilizada: **CUNNINGHAM (1980)**

```
TMB = 370 + (21.6 × MLG)
```

Donde:
- **TMB** = Tasa Metabólica Basal en kcal/día
- **MLG** = Masa Libre de Grasa en kg
- **370** = Constante base (gasto mínimo)
- **21.6** = Factor de gasto por kg de MLG

### Ejemplo de Cálculo

**Caso Hombre:**
- Peso: 82.5 kg
- Grasa corporal: 18.5%
- MLG = 82.5 × (1 - 0.185) = 67.24 kg

```
TMB = 370 + (21.6 × 67.24)
TMB = 370 + 1,452.38
TMB = 1,822.38 kcal/día
```

**Caso Mujer:**
- Peso: 68.0 kg
- Grasa corporal: 28.3%
- MLG = 68.0 × (1 - 0.283) = 48.76 kg

```
TMB = 370 + (21.6 × 48.76)
TMB = 370 + 1,053.22
TMB = 1,423.22 kcal/día
```

### ¿Por qué Cunningham y no Harris-Benedict?

La fórmula de Cunningham es **MÁS PRECISA** porque:
1. Se basa en la **Masa Libre de Grasa (MLG)**, no en el peso total
2. La MLG es metabólicamente activa (consume calorías)
3. La grasa corporal es metabólicamente pasiva (consume muy pocas calorías)
4. Elimina el sesgo de edad y sexo que puede sobrestimar/subestimar

---

## 2. FACTOR DE ACTIVIDAD FÍSICA (GEAF)

### Definición
El GEAF multiplica el TMB para reflejar el nivel de actividad diaria FUERA del ejercicio estructurado (caminar, trabajar, tareas domésticas, NEAT - Non-Exercise Activity Thermogenesis).

### Niveles y Valores

| Nivel | GEAF | Descripción |
|-------|------|-------------|
| **Sedentario** | 1.00 | Sin ejercicio, trabajo de oficina, poca movilidad diaria |
| **Moderadamente activo** | 1.11 | Trabajo que requiere estar de pie, caminar regularmente |
| **Activo** | 1.25 | Trabajo físico ligero, movimiento constante durante el día |
| **Muy activo** | 1.45 | Trabajo físico demandante, alta actividad diaria |

### ⚠️ IMPORTANTE
El GEAF **NO INCLUYE** el entrenamiento estructurado (gym, deporte). Eso se calcula aparte en el GEE.

### Ejemplo de Aplicación

**Usuario sedentario:**
```
Gasto por actividad diaria = TMB × GEAF
Gasto por actividad diaria = 1,822 × 1.00 = 1,822 kcal
```

**Usuario muy activo:**
```
Gasto por actividad diaria = TMB × GEAF
Gasto por actividad diaria = 1,822 × 1.45 = 2,642 kcal
```

---

## 3. EFECTO TÉRMICO DE LOS ALIMENTOS (ETA)

### Definición
El ETA (también llamado Termogénesis Inducida por la Dieta - TID) es la energía que tu cuerpo gasta para:
- Digerir alimentos
- Absorber nutrientes
- Procesar y almacenar energía

### Valores por Macronutriente

| Macronutriente | ETA (% de calorías consumidas) |
|----------------|--------------------------------|
| **Proteína** | 20-30% |
| **Carbohidratos** | 5-10% |
| **Grasas** | 0-3% |

### Valor Promedio Utilizado

```
ETA = 1.10 (10% adicional al gasto energético)
```

Esto significa que si consumes 2,000 kcal, tu cuerpo gasta ~200 kcal solo en procesar esos alimentos.

### Ejemplo de Aplicación

```
Gasto con termogénesis = (TMB × GEAF) × ETA
Gasto con termogénesis = (1,822 × 1.25) × 1.10
Gasto con termogénesis = 2,277.5 × 1.10
Gasto con termogénesis = 2,505.25 kcal
```

---

## 4. GASTO ENERGÉTICO DEL EJERCICIO (GEE)

### Definición
El GEE es la energía que gastas específicamente durante el **entrenamiento estructurado** (gym, deportes, cardio planificado).

### Cálculo Basado en Nivel de Entrenamiento

El sistema calcula el GEE según tu **nivel global de entrenamiento** (que combina FFMI, experiencia y rendimiento funcional):

| Nivel de Entrenamiento | GEE por Sesión | Justificación |
|------------------------|----------------|---------------|
| **Principiante** | 300 kcal | Menor intensidad, menor volumen, menor EPOC |
| **Intermedio** | 350 kcal | Intensidad moderada, volumen medio, EPOC moderado |
| **Avanzado** | 400 kcal | Alta intensidad, alto volumen, EPOC significativo |
| **Élite** | 500 kcal | Muy alta intensidad, muy alto volumen, máximo EPOC |

### Fórmula de Cálculo

```
GEE semanal = Días de entrenamiento × kcal por sesión
GEE promedio diario = GEE semanal ÷ 7
```

### Ejemplo de Cálculo

**Usuario intermedio que entrena 4 días/semana:**

```
GEE por sesión = 350 kcal
GEE semanal = 4 días × 350 kcal = 1,400 kcal/semana
GEE promedio diario = 1,400 ÷ 7 = 200 kcal/día
```

### ¿Por qué promedio diario?

El GEE se distribuye entre los 7 días para calcular una ingesta calórica **consistente** diaria. Esto:
- Simplifica la adherencia (mismas calorías cada día)
- Mejora la recuperación (nutrición constante)
- Facilita el seguimiento

### Componentes del GEE

El GEE incluye:
1. **Gasto durante el ejercicio** (levantar pesas, correr, etc.)
2. **EPOC** (Excess Post-Exercise Oxygen Consumption)
   - Consumo elevado de oxígeno post-ejercicio
   - Duración: 24-48 horas después del entrenamiento
   - Mayor en entrenamientos intensos
   - Contribuye 6-15% del total del GEE

---

## 5. GASTO ENERGÉTICO TOTAL (GE)

### Fórmula Completa

```
GE = (TMB × GEAF × ETA) + GEE promedio diario
```

### Desglose de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                   GASTO ENERGÉTICO TOTAL                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. TMB (Tasa Metabólica Basal)                            │
│     └─ Funciones vitales en reposo                         │
│                                                             │
│  2. ACTIVIDAD FÍSICA DIARIA (TMB × GEAF)                   │
│     └─ NEAT, trabajo, movimiento no estructurado           │
│                                                             │
│  3. TERMOGÉNESIS (TMB × GEAF × ETA)                        │
│     └─ Digestión, absorción, procesamiento                 │
│                                                             │
│  4. EJERCICIO ESTRUCTURADO (GEE)                           │
│     └─ Gym, cardio, deportes + EPOC                        │
│                                                             │
│  TOTAL = (TMB × GEAF × ETA) + GEE                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. EJEMPLOS COMPLETOS

### EJEMPLO 1: HOMBRE, NIVEL INTERMEDIO, ACTIVO

**Datos:**
- Peso: 82.5 kg
- Grasa: 18.5%
- MLG: 67.24 kg
- Nivel GEAF: Moderadamente activo (1.11)
- Días entrenamiento: 4 días/semana
- Nivel entrenamiento: Intermedio

**Cálculos paso a paso:**

```
1. TMB
   TMB = 370 + (21.6 × 67.24)
   TMB = 1,822.38 kcal/día

2. ACTIVIDAD FÍSICA DIARIA
   Gasto actividad = TMB × GEAF
   Gasto actividad = 1,822.38 × 1.11
   Gasto actividad = 2,022.84 kcal

3. TERMOGÉNESIS
   Gasto con ETA = (TMB × GEAF) × ETA
   Gasto con ETA = 2,022.84 × 1.10
   Gasto con ETA = 2,225.13 kcal

4. EJERCICIO
   GEE por sesión = 350 kcal (nivel intermedio)
   GEE semanal = 4 × 350 = 1,400 kcal
   GEE promedio diario = 1,400 ÷ 7 = 200 kcal/día

5. GASTO ENERGÉTICO TOTAL
   GE = (TMB × GEAF × ETA) + GEE
   GE = 2,225.13 + 200
   GE = 2,425.13 kcal/día
```

**Resumen:**
- TMB: 1,822 kcal (75.2%)
- Actividad diaria: 200 kcal (8.2%)
- Termogénesis: 202 kcal (8.3%)
- Ejercicio: 200 kcal (8.3%)
- **TOTAL: 2,425 kcal/día**

---

### EJEMPLO 2: MUJER, NIVEL PRINCIPIANTE, SEDENTARIA

**Datos:**
- Peso: 68.0 kg
- Grasa: 28.3%
- MLG: 48.76 kg
- Nivel GEAF: Sedentario (1.00)
- Días entrenamiento: 3 días/semana
- Nivel entrenamiento: Principiante

**Cálculos paso a paso:**

```
1. TMB
   TMB = 370 + (21.6 × 48.76)
   TMB = 1,423.22 kcal/día

2. ACTIVIDAD FÍSICA DIARIA
   Gasto actividad = TMB × GEAF
   Gasto actividad = 1,423.22 × 1.00
   Gasto actividad = 1,423.22 kcal

3. TERMOGÉNESIS
   Gasto con ETA = (TMB × GEAF) × ETA
   Gasto con ETA = 1,423.22 × 1.10
   Gasto con ETA = 1,565.54 kcal

4. EJERCICIO
   GEE por sesión = 300 kcal (nivel principiante)
   GEE semanal = 3 × 300 = 900 kcal
   GEE promedio diario = 900 ÷ 7 = 128.57 kcal/día

5. GASTO ENERGÉTICO TOTAL
   GE = (TMB × GEAF × ETA) + GEE
   GE = 1,565.54 + 128.57
   GE = 1,694.11 kcal/día
```

**Resumen:**
- TMB: 1,423 kcal (84.0%)
- Actividad diaria: 0 kcal (0%)
- Termogénesis: 142 kcal (8.4%)
- Ejercicio: 129 kcal (7.6%)
- **TOTAL: 1,694 kcal/día**

---

## 7. DISTRIBUCIÓN TÍPICA DEL GASTO ENERGÉTICO

### Usuario Promedio:

```
┌───────────────────────────────────────┐
│   DISTRIBUCIÓN DEL GASTO CALÓRICO     │
├───────────────────────────────────────┤
│                                       │
│  TMB (60-75%)        ████████████████ │
│  NEAT/GEAF (15-30%)  ██████           │
│  ETA (8-15%)         ████             │
│  Ejercicio (5-15%)   ███              │
│                                       │
└───────────────────────────────────────┘
```

### Puntos Clave:

1. **El TMB es el mayor componente** (60-75% del gasto total)
   - Por eso es crucial calcularlo bien (usamos Cunningham)

2. **NEAT/Actividad diaria es muy variable** (15-30%)
   - Puede marcar gran diferencia entre personas
   - Un trabajo activo > sedentario puede ser +500 kcal/día

3. **Ejercicio estructurado es menor de lo que se piensa** (5-15%)
   - No puedes "quemar" una mala dieta con ejercicio
   - Pero sí es importante para composición corporal

4. **ETA es relativamente constante** (8-15%)
   - Mayor en dietas altas en proteína

---

## 8. AJUSTES Y CONSIDERACIONES

### Ajuste por Porcentaje (FBEO)

Una vez calculado el GE (gasto de mantenimiento), aplicamos un **Factor de Balance Energético** según el objetivo:

```
Ingesta calórica = GE × FBEO
```

| Objetivo | Porcentaje | FBEO | Ingesta (si GE = 2,400 kcal) |
|----------|-----------|------|------------------------------|
| Déficit agresivo | -20% | 0.80 | 1,920 kcal |
| Déficit moderado | -15% | 0.85 | 2,040 kcal |
| Déficit ligero | -10% | 0.90 | 2,160 kcal |
| Mantenimiento | 0% | 1.00 | 2,400 kcal |
| Superávit ligero | +5% | 1.05 | 2,520 kcal |
| Superávit moderado | +10% | 1.10 | 2,640 kcal |

### Factores que Afectan el Gasto Energético:

1. **Composición corporal**
   - Más músculo = Mayor TMB
   - Menos grasa = Menor peso, menor TMB

2. **Edad**
   - Pérdida de masa muscular con la edad
   - Reducción de TMB ~2-3% por década después de los 30

3. **Sexo**
   - Hombres: Mayor MLG, mayor TMB
   - Mujeres: Menor MLG, menor TMB
   - Fluctuaciones hormonales (ciclo menstrual)

4. **Clima**
   - Frío extremo: +5-10% TMB
   - Calor extremo: Ligero aumento

5. **Estrés y sueño**
   - Mal sueño: -5-10% TMB
   - Estrés crónico: Puede reducir o aumentar según tipo

6. **Genética**
   - Variación individual de ±10-15%

---

## 9. VALIDACIÓN DE CÁLCULOS

### ¿Cómo saber si el cálculo es correcto?

**Método de seguimiento (2-4 semanas):**

1. Consume las calorías calculadas consistentemente
2. Pésate diariamente (misma hora, condiciones)
3. Calcula promedio semanal
4. Observa tendencia:
   - Peso estable → GE correcto
   - Pérdida de peso → GE sobrestimado
   - Ganancia de peso → GE subestimado

**Ajuste:**
```
GE real = GE calculado × (Peso actual / Peso esperado)
```

---

## 10. REFERENCIAS CIENTÍFICAS

1. **Cunningham JJ (1980)** - Body composition as a determinant of energy expenditure
2. **Mifflin et al. (1990)** - A new predictive equation for resting energy expenditure
3. **Levine JA (2002)** - Non-exercise activity thermogenesis (NEAT)
4. **Borsheim & Bahr (2003)** - Effect of exercise intensity and duration on EPOC
5. **Tappy L (1996)** - Thermic effect of food and sympathetic nervous system activity

---

## RESUMEN EJECUTIVO

```
GE TOTAL = (TMB × GEAF × ETA) + GEE

Donde:
  TMB = 370 + (21.6 × MLG)           [kcal/día]
  GEAF = 1.00 - 1.45                 [multiplicador]
  ETA = 1.10                          [multiplicador]
  GEE = (Días × kcal/sesión) ÷ 7     [kcal/día]
```

**Este es el gasto energético de mantenimiento diario completo.**
**Para objetivos específicos, se multiplica por FBEO (0.80 - 1.10).**

---

© 2026 MUPAI v2.0 - Sistema de Cálculo Nutricional Personalizado

## 🔀 Choque de Lógicas en el Código

### Problema Identificado

El código tiene **4 flujos de lógica paralelos** que pueden entrar en conflicto:

```
FLUJO A (Usuarios "en rango óptimo" - Líneas 9059-9115)
├─ Lógica: Interactiva (selectbox usuario)
├─ Aplica: Porcentajes manuales
└─ Impacto: NINGUNO (solo para UI, no emails)

FLUJO B (Usuarios "fuera de rango" - Línea 9135)
├─ Lógica: determinar_fase_nutricional_refinada()
├─ Aplica: Tabla fija de déficits
├─ Ejemplo: 26.4% → 30% déficit
└─ Ruta: streamlit_app.py línea 2677

FLUJO C (Nueva Lógica - Línea 10134)
├─ Lógica: calcular_plan_con_sistema_actual()
├─ Aplica: Interpolación de déficit
├─ Ejemplo: 26.4% → 50% déficit (SIN guardrails)
└─ Ruta: integracion_nueva_logica.py línea 218

FLUJO D (Guardrails - Línea 10147)
├─ Lógica: Caps por IR-SE + Sueño
├─ Aplica: min(50%, 30%, 30%) = 30%
├─ Ejemplo: 50% → 30% (capeado)
└─ Modifica: plan_nuevo['fases']['cut']
```

---

## 📍 Localización Exacta

### FLUJO B: Vieja Lógica (Línea 9135)
```python
# streamlit_app.py línea 9049-9135
if USER_VIEW:
    if en_rango_optimo:
        # FLUJO A: Usuario selecciona manualmente
        objetivo_seleccionado = st.selectbox(...)
        porcentaje = [-10 o 2.5 o 7.5]  # Manual
    else:
        # FLUJO B: Lógica automática
        fase, porcentaje = determinar_fase_nutricional_refinada(grasa_corregida, sexo)
        # Ejemplo Erick: 26.4% → porcentaje = -30
```

**Definida en**: `streamlit_app.py` línea 2677
```python
def determinar_fase_nutricional_refinada(grasa_corregida, sexo):
    rangos_hombre = [
        ...
        (25.6, 30, 30),  # ← ERICK aquí: -30%
        ...
    ]
    tabla = rangos_hombre if sexo == "Hombre" else rangos_mujer
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            return min(deficit, tope) ...
```

**Variables generadas**:
- `fase` = "Déficit recomendado: 30%"
- `porcentaje` = -30
- `fbeo` = 1 + (-30/100) = 0.70

**Impacto**:
- ✅ Se usa en UI para mostrar sugerencias
- ❌ **NO se usa en email** (emails usan nueva lógica)

---

### FLUJO C: Nueva Lógica (Línea 10134)
```python
# streamlit_app.py línea 10134-10151
plan_nuevo = calcular_plan_con_sistema_actual(
    peso=peso,
    grasa_corregida=grasa_corregida,  # 26.4%
    sexo=sexo,
    ...
    activar_ciclaje_4_3=True
)
# Retorna plan con deficit_pct = 50% (sin guardrails)
```

**Definida en**: `integracion_nueva_logica.py` línea 218
```python
def calcular_plan_con_sistema_actual(grasa_corregida, ...):
    plan = calcular_plan_nutricional_completo(
        bf_corr_pct=grasa_corregida,  # 26.4%
        ...
    )
    # Dentro calcula deficit interpolado = 50%
    return plan
```

**Variables generadas**:
- `plan_nuevo['fases']['cut']['deficit_pct']` = 50%
- `plan_nuevo['fases']['cut']['kcal']` = 1205 kcal
- `plan_nuevo['fases']['cut']['macros']` = {P, F, C según 1205}

**Impacto**:
- ✅ Se usa en guardrails (línea 10147)
- ✅ Se usa en email (línea 10300+)
- ❌ Valores son inconsistentes (50% vs 30% de la vieja lógica)

---

### FLUJO D: Guardrails (Línea 10147)
```python
# streamlit_app.py línea 10147-10228
if 'plan_nuevo' in locals() and plan_nuevo and 'fases' in plan_nuevo:
    fase_cut = plan_nuevo['fases'].get('cut')
    if fase_cut:
        deficit_interpolado = fase_cut.get('deficit_pct', 30)  # = 50%
        
        # Calcula caps
        if ir_se_valor >= 70:
            cap_ir_se = 100
        elif 50 <= ir_se_valor < 70:  # ← ERICK: 64.3
            cap_ir_se = 30
        
        if calidad_suenyo_valor < 6:  # ← ERICK: 5.0
            cap_sleep = 30
        
        # Aplica cap más restrictivo
        deficit_capeado = min(deficit_interpolado, cap_ir_se, cap_sleep)
        # = min(50%, 30%, 30%) = 30% ✅
        
        # ACTUALIZA plan_nuevo
        fase_cut['deficit_pct'] = deficit_capeado  # 30%
        fase_cut['kcal'] = kcal_capeado  # 1687 kcal
        # También recalcula macros y ciclaje
```

**Variables generadas**:
- `deficit_capeado` = 30%
- `kcal_capeado` = 1687 kcal
- `ingesta_calorica_capeada` = 1687 kcal (Commit 939c766)
- Modifica `plan_nuevo['fases']['cut']` IN-PLACE

**Impacto**:
- ✅ Corrige plan_nuevo ANTES del email
- ✅ Email debe usar estos valores capeados
- ⚠️ Si guardrails NO se ejecutan (if falla), email usa valores originales

---

### FLUJO E: Email (Línea 10300+)
```python
# streamlit_app.py línea 10243-10380
macros_fase = plan_nuevo['fases'][fase_activa]  # Usa plan_nuevo ACTUALIZADO

# Sección 6.1
ingesta_calorica_objetivo = ingesta_calorica_capeada  # ← Commit 939c766
# Debería ser 1687 kcal (capeado) ✅

# Sección 6.2
deficit_pct_aplicado = macros_fase.get('deficit_pct', 30)
# Debería ser 30% (capeado) ✅

plan_tradicional_calorias = macros_fase['kcal']
# Debería ser 1687 kcal (capeado) ✅

# Ciclaje 4-3
ciclaje_low_kcal = ciclaje_info['low_days']['kcal']
# Debería ser 1350 kcal (capeado) ✅
```

**Email ANTES de fix 939c766**:
```
6.1: Ingesta calórica objetivo: 1205 kcal (❌ INCORRECTO - vieja ingesta_calorica)
6.2: CALORÍAS: 1205 kcal (❌ INCORRECTO - plan_nuevo sin actualizar)
     Ciclaje LOW: 964 kcal (❌ INCORRECTO - basado en 1205)
```

**Email DESPUÉS de fix 939c766**:
```
6.1: Ingesta calórica objetivo: 1687 kcal (✅ CORRECTO - ingesta_calorica_capeada)
6.2: CALORÍAS: 1687 kcal (✅ CORRECTO - plan_nuevo actualizado)
     Ciclaje LOW: 1350 kcal (✅ CORRECTO - basado en 1687)
```

---

## 🎯 El Choque: Por Qué Pasaba

### Escenario Erick:

1. **Vieja Lógica (9135)**: 
   - `grasa_corregida = 26.4%`
   - `determinar_fase_nutricional_refinada()` → Tabla: 25.6-30% → **30% déficit**
   - `fbeo = 0.70`
   - `ingesta_calorica_tradicional = 2410 × 0.70 = 1687 kcal`

2. **Nueva Lógica (10134)**:
   - `calcular_plan_con_sistema_actual(26.4%)` → Interpola → **50% déficit**
   - `plan_nuevo['fases']['cut']['kcal'] = 2410 × 0.50 = 1205 kcal`

3. **Guardrails (10147)**:
   - `deficit_interpolado = 50%` (del plan_nuevo)
   - `cap_ir_se = 30%` (IR-SE 64.3)
   - `cap_sleep = 30%` (Sueño 5.0h)
   - `deficit_capeado = min(50%, 30%, 30%) = 30%`
   - **Actualiza** `plan_nuevo['fases']['cut']['kcal'] = 1687 kcal`

4. **Email (10300+)** - ANTES del fix:
   - Línea 10303: `ingesta_calorica_objetivo = ingesta_calorica_tradicional = 1687` ✅
   - Línea 10255: `plan_tradicional_calorias = macros_fase['kcal']`
   - Pero `macros_fase` se lee **DESPUÉS de actualizar**, así que debería tener 1687...
   - ❌ PROBLEMA: Había bug en parsing de sueño, `cap_sleep = 100` (sin cap), entonces `deficit_capeado = 50%`, entonces `kcal = 1205`

---

## ✅ Soluciones Implementadas

### Commit 0b0bddb (Sleep Parsing)
```
Problema: "5-5.9" (string) → float() fallaba
Solución: Extraer primer número → float(5.0)
Impacto: cap_sleep se aplica correctamente
```

### Commit 939c766 (Ingesta Capeada)
```
Problema: Sección 6.1 usaba ingesta_calorica de vieja lógica
Solución: Usar ingesta_calorica_capeada (calculada en guardrails)
Impacto: Email 100% consistente (1687 en ambas secciones)
```

---

## 🚀 Recomendación: Consolidar Lógicas

Para evitar futuros choques, se podría:

1. **Eliminar FLUJO B** (vieja lógica) de email
   - Mantener solo para UI/FFMI display
   - No generar `fbeo` ni `ingesta_calorica_tradicional`

2. **Usar SOLO FLUJO C+D** para email
   - Nueva lógica + guardrails
   - Una única fuente de verdad

3. **Código limpio**:
   ```
   ✅ NUEVO:
   plan = calcular_plan_con_sistema_actual(grasa_corregida)
   aplicar_guardrails(plan, ir_se, sleep)
   generar_email(plan)  # Una sola lógica
   
   ❌ VIEJO:
   fbeo = vieja_logica()
   plan = nueva_logica()
   guardrails(plan)
   email_mezcla(fbeo, plan)  # Conflictos
   ```

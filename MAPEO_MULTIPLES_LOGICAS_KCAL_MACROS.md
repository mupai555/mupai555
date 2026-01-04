# 🗺️ MAPEO COMPLETO: MÚLTIPLES LÓGICAS DE KCAL Y MACROS

## RESUMEN EJECUTIVO

**Problema:** El código tiene **3 SISTEMAS DIFERENTES** para calcular KCAL y MACROS:

| Sistema | Ubicación | Propósito | Estado |
|---------|-----------|----------|--------|
| **1. NUEVA LÓGICA** | `nueva_logica_macros.py` | Cálculo científico completo (BF operacional, guardrails, PBM) | ✅ Principal, oficial |
| **2. LÓGICA TRADICIONAL** | `streamlit_app.py` (líneas ~4000+) | Sistema heredado (factor proteína simple, sin guardrails) | ⚠️ Fallback/Legacy |
| **3. CALCULAR_PLAN_CON_SISTEMA_ACTUAL** | `integracion_nueva_logica.py` + `streamlit_app.py` (línea ~10105) | Envoltorio que llama a `nueva_logica_macros.py` | ✅ En uso actualmente |

---

## 1. NUEVA LÓGICA (Principal) ✅

### 📍 Ubicación
- **Archivo:** `nueva_logica_macros.py` (1200+ líneas)
- **Función principal:** `calcular_plan_nutricional_completo()`

### 🔧 Características
```python
calcular_plan_nutricional_completo(
    peso: float,
    grasa_corregida: float,
    sexo: str,
    mlg: float,
    maintenance_kcal: float,
    nivel_entrena: str,
    dias_entrena: int,
    calidad_suenyo: float = 7.0,
    ir_se_score: float = 60.0,
    # ... más params
) -> Dict
```

### 📊 Proceso (Paso a Paso)

#### 1️⃣ KCAL por Fase
```python
# CUT: Aplica déficit + guardrails
kcal_cut, deficit_pct, warning = calcular_kcal_cut(
    maintenance_kcal=GE,
    bf_operational=BF,
    sexo=sexo,
    ir_se_score=ir_se_valor,      # ← GUARDRAILS
    sleep_hours=calidad_suenyo_valor  # ← GUARDRAILS
)
# Resultado: 1687 kcal (capeado a 30% déficit para Erick)

# MAINTENANCE: GE trivial
kcal_maint = calcular_kcal_maintenance(GE)
# Resultado: 2410 kcal (igual a GE)

# BULK: Superávit sin guardrails
kcal_bulk, surplus_pct = calcular_kcal_bulk(
    maintenance_kcal=GE,
    bf_operational=BF,
    sexo=sexo
)
# Resultado: ~2700 kcal (sin límite de guardrails)

# PSMF: Protocolo alternativo
# Ignora KCAL, usa k × protein_g
```

#### 2️⃣ MACROS (Orden P→F→C)
```python
# Función central: calcular_macros_fase_nueva()
# Entrada: kcal_fase, protein_g (base), sexo, grasa_corregida

# PASO 1: PROTEÍNA (fijo)
protein_g = base_proteina_kg * factor_proteina
# Para CUT Erick: 130g (2.2 × 59g MLG)

# PASO 2: GRASA (30% kcal)
fat_kcal = kcal_cut * 0.30  # 36g kcal
fat_g = fat_kcal / 9        # 36.5g

# PASO 3: CARBOHIDRATOS (resto)
carb_kcal = kcal_cut - protein_kcal - fat_kcal
carb_g = carb_kcal / 4  # 228g
```

#### 3️⃣ CICLAJE (si activado)
```python
# Función: calcular_ciclaje_4_3()
# LOW days (4 días): 0.8 × kcal_cut
# HIGH days (3 días): ((7×kcal) - (4×LOW)) / 3
# Promedio: = kcal_cut ✅

kcal_low = 1350
kcal_high = 2137
promedio = (4*1350 + 3*2137) / 7 = 1687 ✅
```

### 🎯 Salida
```python
plan_nuevo = {
    'bf_operational': 26.4,
    'categoria_bf': 'Alto',
    'pbm': 59.0,
    'fases': {
        'cut': {
            'kcal': 1687,
            'deficit_pct': 30,
            'warning': '⚠️ IR-SE capeado a 30%',
            'macros': {
                'protein_g': 130,
                'fat_g': 36.5,
                'carb_g': 228
            },
            'ciclaje_4_3': {
                'low_days': {'kcal': 1350, 'macros': {...}},
                'high_days': {'kcal': 2137, 'macros': {...}}
            },
            'base_proteina': 'pbm_ajustado',
            'protein_mult': 2.2
        },
        # ... maintenance, bulk, psmf
    }
}
```

### ✅ Ventajas
- ✅ Guardrails (IR-SE, sueño) integrados
- ✅ BF operacional (sin visual)
- ✅ PBM (Protein Base Mass)
- ✅ 5 categorías BF
- ✅ Orden estricto P→F→C
- ✅ Ciclaje proporcional
- ✅ PSMF con k dinámico

### ⚠️ Dónde se Usa
1. **streamlit_app.py línea ~10105:** `plan_nuevo = calcular_plan_con_sistema_actual(...)`
   - Llamada directa en lógica principal
   - Resultado guardado en `plan_nuevo`
   - Se aplican guardrails AQUÍ (línea 10161-10228)
   - Se recalculan macros después (línea 10213-236)
2. **Emails:** Leen desde `plan_nuevo['fases'][fase_activa]`

---

## 2. LÓGICA TRADICIONAL (Legacy) ⚠️

### 📍 Ubicación
- **Archivo:** `streamlit_app.py` (definiciones funciones ~líneas 4000-5000)
- **Funciones clave:**
  - `obtener_factor_proteina_tradicional(grasa_corregida)`
  - `debe_usar_mlg_para_proteina(sexo, grasa_corregida)`
  - `obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo)`
  - `calcular_macros_tradicional(ingesta, tmb, sexo, grasa, peso, mlg)`

### 🔧 Cálculo KCAL
```python
# NO hay cálculo de KCAL en lógica tradicional
# Simplemente recibe `ingesta_calorica_tradicional` como parámetro

# NUNCA calcula GE (gasto energético)
# NUNCA aplica guardrails
# NUNCA calcula déficit
```

### 🔧 Cálculo MACROS
```python
def calcular_macros_tradicional(ingesta, tmb, sexo, grasa, peso, mlg):
    
    # 1. PROTEÍNA
    usar_mlg = debe_usar_mlg_para_proteina(sexo, grasa)
    # Regla: Hombre ≥35% o Mujer ≥42% → usar MLG
    
    base_kg = mlg if usar_mlg else peso
    factor = obtener_factor_proteina_tradicional(grasa)
    # 15% BF → 2.0 g/kg
    # 20% BF → 1.8 g/kg
    # 30% BF → 1.6 g/kg
    # 40% BF → 1.4 g/kg
    # 50%+ BF → 1.2 g/kg
    
    protein_g = round(base_kg * factor)
    protein_kcal = protein_g * 4
    
    # 2. GRASA
    grasa_min_kcal = ingesta * 0.20      # Mín 20% TEI
    grasa_ideal_kcal = tmb * 0.40         # Ideal 40% TMB
    grasa_max_kcal = ingesta * 0.40       # Máx 40% TEI
    
    grasa_kcal = max(grasa_min_kcal, min(grasa_ideal_kcal, grasa_max_kcal))
    grasa_g = round(grasa_kcal / 9)
    
    # 3. CARBOHIDRATOS (resto)
    carbo_kcal = ingesta - protein_kcal - grasa_kcal
    carbo_g = round(max(0, carbo_kcal / 4))
    
    return {
        'proteina_g': protein_g,
        'grasa_g': grasa_g,
        'carbo_g': carbo_g,
        'base_proteina': 'MLG' if usar_mlg else 'Peso total',
        # ...
    }
```

### 🎯 Salida
```python
{
    'proteina_g': 130,
    'proteina_kcal': 520,
    'grasa_g': 60,
    'grasa_kcal': 540,
    'carbo_g': 180,
    'carbo_kcal': 720,
    'base_proteina': 'MLG',
    'factor_proteina': 2.0
}
```

### ⚠️ Limitaciones
- ⚠️ No calcula GE (gasto energético)
- ⚠️ No aplica guardrails
- ⚠️ No hace BF operacional
- ⚠️ No usa PBM
- ⚠️ Factor proteína muy simple
- ⚠️ Grasa: 40% TMB (fijo, sin considerar actividad)

### 📍 Dónde Aún Se Usa
1. **Fallback en tests:** Si `nueva_logica_macros.py` no está disponible
2. **Emails antiguos:** Algunos emails PODRÍAN usar esto (pero lo correcto es usar `plan_nuevo`)
3. **Historial:** Código heredado que no se ha refactorizado completamente

---

## 3. CALCULAR_PLAN_CON_SISTEMA_ACTUAL (Integración)

### 📍 Ubicación
- **Definición:** `integracion_nueva_logica.py` líneas ~100-250
- **Llamada:** `streamlit_app.py` línea ~10105

### 🔧 Qué Hace
```python
def calcular_plan_con_sistema_actual(
    peso, grasa_corregida, sexo, mlg,
    geaf, eta, gee_prom_dia,
    calidad_suenyo, nivel_estres, ir_se,
    nivel_entrena, dias_entrena,
    **kwargs
) -> Dict:
    """
    Envoltorio que:
    1. Calcula GE = (TMB × GEAF) + GEE × ETA
    2. Llama a calcular_plan_nutricional_completo()
    3. Aplica guardrails (línea 10161 en streamlit_app.py)
    4. Recalcula macros proporcionalmente (línea 10213)
    """
    
    # Paso 1: Calcular GE (aquí)
    tmb = 500 + 22 * mlg
    ge = (tmb * geaf) + (gee_prom_dia * eta)
    
    # Paso 2: Llamar a nueva lógica
    plan = calcular_plan_nutricional_completo(
        peso=peso,
        grasa_corregida=grasa_corregida,
        sexo=sexo,
        mlg=mlg,
        maintenance_kcal=ge,  # ← Pasa GE aquí
        # ...
    )
    
    # Paso 3 y 4: Se hacen en streamlit_app.py líneas 10161+
    # (Fuera de esta función)
    
    return plan
```

### 🎯 Resultado
- Retorna `plan_nuevo` (estructura completa)
- Luego en streamlit_app.py:
  - Se aplican guardrails (línea 10161)
  - Se recalculan macros (línea 10213)
  - Se recalcula ciclaje (línea 10236)
  - Se actualiza `plan_nuevo` IN-PLACE

---

## 4. FLUJO ACTUAL EN STREAMLIT_APP.PY (CORRIENTE)

```
LÍNEA ~10105: Llamar calcular_plan_con_sistema_actual()
    ↓
    Retorna plan_nuevo (sin guardrails aún)
    ↓
LÍNEA ~10161: Aplicar guardrails
    • Leer deficit_interpolado de plan
    • Calcular cap_ir_se, cap_sleep
    • deficit_capeado = min(deficit_interp, cap_ir_se, cap_sleep)
    • kcal_capeado = GE × (1 - deficit_capeado/100)
    • plan_nuevo['fases']['cut']['kcal'] = kcal_capeado ← ACTUALIZA IN-PLACE
    ↓
LÍNEA ~10213: Recalcular macros proporcionalmente
    • protein_g: IGUAL (fijo)
    • fat_g: (kcal_capeado × 0.30) / 9
    • carb_g: (kcal_capeado × 0.70) / 4
    • plan_nuevo['fases']['cut']['macros'] = nuevos ← ACTUALIZA IN-PLACE
    ↓
LÍNEA ~10236: Recalcular ciclaje
    • kcal_low = kcal_capeado × 0.8
    • kcal_high = ((7×kcal_capeado) - (4×kcal_low)) / 3
    • plan_nuevo['ciclaje_4_3'] = actualizado ← ACTUALIZA IN-PLACE
    ↓
LÍNEA ~10267: Leer para emails
    macros_fase = plan_nuevo['fases']['cut']  ← Lee valores CAPEADOS
    ↓
LÍNEA ~10770: EMAIL 1
LÍNEA ~10953: EMAIL 4
```

### ✅ DISEÑO CORRECTO
- **Fuente única de verdad:** `plan_nuevo`
- **Actualización:** IN-PLACE en memoria
- **Lectura:** Siempre desde `plan_nuevo` actualizado
- **Emails:** Consistentes porque leen desde `plan_nuevo`

---

## 5. COMPARATIVA DE CÁLCULOS

### Ejemplo: Erick (80kg, 26.4% BF, Hombre)

#### Sistema: NUEVA LÓGICA (streamlit_app.py actual)
```
calcular_plan_nutricional_completo()
├─ bf_operacional = 26.4
├─ GE = 2410 kcal (parámetro entrada)
├─ deficit_interpolado = 50%
├─ CUT KCAL SIN GUARDRAILS = 2410 × 0.50 = 1205
├─ GUARDRAILS APLICADOS (línea 10161)
│  ├─ cap_ir_se = 30% (IR-SE 64.3 → rango 50-69)
│  ├─ cap_sleep = 30% (sueño 5.0h < 6h)
│  ├─ deficit_capeado = min(50%, 30%, 30%) = 30%
│  └─ CUT KCAL CON GUARDRAILS = 2410 × 0.70 = 1687 ✅
├─ MACROS SIN GUARDRAILS = {150g P, 40g F, 191g C}
├─ MACROS RECALCULADOS (línea 10213) = {150g P, 36g F, 228g C} ✅
├─ CICLAJE RECALCULADO (línea 10236)
│  ├─ LOW = 1687 × 0.8 = 1350
│  └─ HIGH = ((7×1687) - (4×1350))/3 = 2137
└─ PROMEDIO = (4×1350 + 3×2137)/7 = 1687 ✅
```

#### Sistema: LÓGICA TRADICIONAL (si se hubiera usado)
```
calcular_macros_tradicional(
    ingesta_calorica_tradicional=1205,  # ← Valor SIN guardrails
    tmb=1847,
    sexo="Hombre",
    grasa_corregida=26.4,
    peso=80,
    mlg=59
)
├─ Proteína = 59 × 2.2 = 130g
├─ Grasa = max(241, min(738, 482)) = 482 kcal = 53.5g
├─ Carbohidratos = 1205 - 520 - 482 = 203g
└─ RESULTADO: {130g P, 53.5g F, 203g C} ❌ DIFERENTE
```

**Diferencia clave:**
- Nueva lógica: Grasa 30% kcal = 36g F (proporcional a KCAL capeado)
- Tradicional: Grasa 40% TMB = 53.5g F (siempre 40% TMB, sin considerar kcal capeado)

---

## 6. DÓNDE SE ENCUENTRAN CADA LÓGICA EN EL CÓDIGO

### 📄 nueva_logica_macros.py
```
Línea 211:    def calcular_kcal_cut() ← CUT KCAL con guardrails
Línea 232:    def calcular_kcal_maintenance()
Línea 239:    def calcular_kcal_bulk()
Línea 554:    def calcular_macros_psmf()
Línea 708:    def calcular_ciclaje_4_3()
Línea 785:    def calcular_plan_nutricional_completo() ← PRINCIPAL
```

### 📄 streamlit_app.py
```
Línea ~4000-4500:   Definiciones de funciones tradicionales
Línea ~10105:       plan_nuevo = calcular_plan_con_sistema_actual(...)
Línea ~10161-10228: GUARDRAILS APLICADOS AQUÍ ⭐
Línea ~10213-10236: RECALCULAR MACROS Y CICLAJE ⭐
Línea ~10267:       Leer macros_fase = plan_nuevo['fases'][...]
Línea ~10770:       enviar_email_resumen() ← EMAIL 1
Línea ~10953:       enviar_email_yaml() ← EMAIL 4
```

### 📄 integracion_nueva_logica.py
```
Línea ~100-250:     Función wrapper calcular_plan_con_sistema_actual()
```

---

## 7. ESTADO DE SINCRONIZACIÓN

### ✅ Sincronizado (Correcto)
- **Nueva lógica** → **plan_nuevo** → **Emails**
- Secuencia: Nueva lógica → Guardrails → Macros → Ciclaje → Lectura para emails
- Todos los emails leen desde `plan_nuevo` actualizado

### ⚠️ Potencialmente Asincronizado (Revisar)
- **Lógica tradicional** en streamlit_app.py: Podría estar desactualizada
- Se mantiene por **compatibilidad/fallback** pero NO se usa en flujo principal

### ❌ **NO DEBEN COEXISTIR**
- Si en algún lugar se llama `calcular_macros_tradicional()` DIRECTAMENTE:
  - Daría KCAL sin guardrails
  - Daría MACROS con 40% TMB (no proporcionales)
  - Inconsistente con emails

---

## 8. MATRIZ DE DECISIÓN: ¿QUÉ LÓGICA USAR?

| Escenario | Usar | Razón |
|-----------|------|-------|
| **Cálculo completo (KCAL+MACROS+CICLAJE)** | Nueva lógica | ✅ Completa, científica |
| **Solo cálculo de MACROS dado KCAL** | `calcular_macros_tradicional()` | ⚠️ Legacy, pero funciona |
| **Guardrails IR-SE/sueño** | Nueva lógica (línea 10161) | ✅ Única que los implementa |
| **Emails** | Leer desde `plan_nuevo` | ✅ Garantiza consistencia |
| **PSMF** | Nueva lógica (`calcular_macros_psmf()`) | ✅ Única que lo implementa |

---

## 9. RECOMENDACIÓN: CONSOLIDACIÓN

### 🚀 Próximo Paso
**Limpiar código:** Remover `calcular_macros_tradicional()` y usar SOLO nueva lógica.

**Por qué:**
1. Evita duplicación
2. Garantiza consistencia
3. Mantiene guardrails
4. Un solo sistema a mantener

**Pasos:**
1. Confirmar que 100% del código usa `plan_nuevo`
2. Remover funciones tradicionales
3. Deprecar `integracion_nueva_logica.py` (simplificar a nueva lógica directa)
4. Tests que verifiquen NO hay paths alternativos

---

## 10. CHECKLIST: ¿ESTÁ BIEN AHORA?

- [ ] Nueva lógica genera `plan_nuevo`
- [ ] Guardrails aplicados línea 10161
- [ ] Macros recalculadas línea 10213 (con kcal_capeado)
- [ ] Ciclaje recalculado línea 10236
- [ ] Emails leen desde `plan_nuevo['fases'][fase_activa]`
- [ ] NO hay paths que usen `calcular_macros_tradicional()` directamente
- [ ] Tests comprueban consistencia entre todas las partes

---

**Creado:** 4 Enero 2026  
**Estado:** 🔍 ANÁLISIS COMPLETO - Listo para consolidación

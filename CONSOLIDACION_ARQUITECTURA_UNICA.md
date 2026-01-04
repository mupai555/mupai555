# 🏗️ CONSOLIDACIÓN: UNA SOLA LÓGICA ESTABLE PARA TODOS

## El Problema

**ANTES (Caótico):**
```
┌─────────────────────────────────────────────────────────────┐
│  Usuario 1 (Andrea)  →  Función A → Resultado X            │
│  Usuario 2 (Erick)   →  Función B → Resultado Y (¿igual?)  │
│  Usuario 3 (Cristina) → Función C → Resultado Z (¿igual?)   │
│                                                             │
│  ❌ Diferentes funciones = resultados inconsistentes        │
│  ❌ Cambios necesitan edición en múltiples lugares          │
│  ❌ Tests complejos: múltiples paths                        │
└─────────────────────────────────────────────────────────────┘
```

**DESPUÉS (Propuesto):**
```
┌─────────────────────────────────────────────────────────────┐
│  Todos los usuarios → FUNCIÓN ÚNICA → Resultado consistente │
│                                                             │
│  ✅ Una sola función para cada paso                         │
│  ✅ Cambios en UN lugar = consistencia inmediata            │
│  ✅ Tests simples: un path                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. MAPEO DE FUNCIONES ACTUALES (DUPLICADAS)

### A. Funciones de CÁLCULO BÁSICO

#### FFMI (¡DUPLICADA!)
```
Ubicación 1: streamlit_app.py línea 2077
  def calcular_ffmi(mlg, estatura_cm):
      ...

Ubicación 2: streamlit_app.py línea 2174
  def calcular_ffmi(mlg, estatura_cm):  ← DUPLICADA
      ...

❌ PROBLEMA: Dos funciones idénticas o muy similares
✅ SOLUCIÓN: Mantener UNA sola
```

#### TMB
```
Ubicación: streamlit_app.py línea 2025
  def calcular_tmb_cunningham(mlg):
      return 500 + (22 * mlg)  ← CORREGIDO

✅ ÚNICA: Una sola función
```

#### MLG
```
Ubicación: streamlit_app.py línea 2033
  def calcular_mlg(peso, porcentaje_grasa):
      ...

✅ ÚNICA: Una sola función
```

#### FMI
```
Ubicación: streamlit_app.py línea 2343
  def calcular_fmi(peso, grasa_corregida, estatura_cm):
      ...

✅ ÚNICA: Una sola función
```

---

### B. Funciones de GASTO ENERGÉTICO

#### GEAF
```
Ubicación: streamlit_app.py línea 2753
  def obtener_geaf(nivel):
      ...

✅ ÚNICA: Una sola función
```

#### GEE (Gasto por Entrenamiento)
```
Ubicación: ¿? (buscar dónde se calcula)
  Parece estar inline en streamlit_app.py línea ~9000

❌ PROBLEMA: No existe como función, está hardcodeado
✅ SOLUCIÓN: Crear función centralizada
```

#### ETA (Efecto Térmico)
```
Ubicación: streamlit_app.py línea ~?
  
❌ PROBLEMA: ¿Dónde se define exactamente?
✅ SOLUCIÓN: Crear función centralizada clara
```

---

### C. Funciones de MACROS (CONFLICTIVAS)

#### `calcular_macros_tradicional()`
```
Ubicación: streamlit_app.py línea 2957
  def calcular_macros_tradicional(ingesta, tmb, sexo, grasa, peso, mlg):
      # Proteína basada en factor
      # Grasa: 40% TMB
      # Carbos: resto

❌ PROBLEMA: "Tradicional" = deprecada, pero aún existe
✅ SOLUCIÓN: Remover completamente (usar NUEVA lógica)
```

#### `calcular_macros_psmf()`
```
Ubicación: streamlit_app.py línea 3024
  def calcular_macros_psmf(psmf_recs):
      ...

✅ ESTADO: Es wrapper, puede mantenerse
```

#### NUEVA LÓGICA (en nueva_logica_macros.py)
```
Ubicación: nueva_logica_macros.py línea 785
  def calcular_plan_nutricional_completo(peso, grasa, sexo, mlg, ...):
      # BF operacional
      # Déficit interpolado
      # Guardrails
      # Macros P→F→C
      # Ciclaje 4-3

✅ ESTADO: Oficial, completa, científica
```

---

## 2. EL FLUJO ACTUAL (LÍNEA 10146+ en streamlit_app.py)

```
INPUT: peso, grasa_corregida, sexo, mlg, tmb, geaf, eta, gee_prom_dia, ...
  ↓
[LÍNEA 10146] plan_nuevo = calcular_plan_con_sistema_actual(
    peso, grasa_corregida, sexo, mlg, 
    tmb, geaf, eta, gee_prom_dia,
    nivel_entrenamiento, días_fuerza,
    calidad_suenyo, nivel_estres, ir_se,
    activar_ciclaje_4_3=True
)
  ↓
[LÍNEA 10167] Aplicar guardrails (IR-SE + sueño)
  ↓
[LÍNEA 10202] Recalcular macros proporcionalmente
  ↓
[LÍNEA 10236] Recalcular ciclaje
  ↓
[LÍNEA 10267] Leer macros_fase = plan_nuevo['fases']['cut']
  ↓
[LÍNEA 10770] EMAIL 1 (tabla_resumen)
[LÍNEA 10953] EMAIL 4 (YAML)

OUTPUT: Emails consistentes ✅
```

---

## 3. ARQUITECTURA ÚNICA PROPUESTA

### PASO 1: CÁLCULOS BÁSICOS (Sin cambios, funcionan bien)

```python
# streamlit_app.py líneas 2020-2350 (consolidadas)

def calcular_tmb_cunningham(mlg: float) -> float:
    """TMB = 500 + (22 × MLG)"""
    return 500 + (22 * mlg)

def calcular_mlg(peso: float, grasa_pct: float) -> float:
    """MLG = Peso × (1 - %grasa/100)"""
    return peso * (1 - grasa_pct / 100)

def calcular_ffmi(mlg: float, estatura_cm: float) -> float:
    """FFMI Base = MLG / altura²"""
    estatura_m = estatura_cm / 100
    return mlg / (estatura_m ** 2)

def calcular_fmi(grasa_total: float, estatura_cm: float) -> float:
    """FMI = Masa grasa / altura²"""
    estatura_m = estatura_cm / 100
    return grasa_total / (estatura_m ** 2)

def obtener_geaf(nivel_actividad: str) -> float:
    """Factor de actividad diaria: 1.0 a 1.9"""
    # Sedentario: 1.0, Poco activo: 1.1, etc.

def calcular_gee(dias_entrena: int, kcal_por_sesion: float) -> float:
    """GEE diario = (días × kcal_sesion) / 7"""
    return (dias_entrena * kcal_por_sesion) / 7

def obtener_eta(grasa_pct: float, sexo: str) -> float:
    """Factor térmico de los alimentos: 1.05 a 1.15"""
    # Basado en composición y sexo

def calcular_ge(tmb: float, geaf: float, gee: float, eta: float) -> float:
    """GE = (TMB × GEAF) + (GEE × ETA)"""
    return (tmb * geaf) + (gee * eta)

# ✅ RESULTADO: Funciones simples, una entrada, una salida, sin dependencias
```

### PASO 2: PLAN NUTRICIONAL (ÚNICA FUENTE DE VERDAD)

```python
# nueva_logica_macros.py línea 785

def calcular_plan_nutricional_completo(
    peso: float,
    grasa_corregida: float,
    sexo: str,
    mlg: float,
    maintenance_kcal: float,  # ← Este es GE calculado en PASO 1
    nivel_entrena: str,
    dias_entrena: int,
    calidad_suenyo: float,
    ir_se_score: float,
    # ... otros params
) -> Dict:
    """
    FUNCIÓN ÚNICA que calcula TODOS los planes:
    - CUT (con guardrails)
    - MAINTENANCE
    - BULK
    - PSMF
    
    Retorna: plan_nuevo con todas las fases
    """
    
    # BF operacional
    bf_op = calcular_bf_operacional(grasa_corregida)
    
    # Déficit por interpolación
    deficit_interp = interpolar_deficit(bf_op, sexo)
    
    # Guardrails aplicados DENTRO
    deficit_capeado, warning = aplicar_guardrails_deficit(
        deficit_interp, ir_se_score, calidad_suenyo
    )
    
    # CUT: KCAL con guardrails
    kcal_cut = maintenance_kcal * (1 - deficit_capeado / 100)
    
    # Macros CUT: orden P→F→C
    protein_g = calcular_proteina(mlg, grasa_corregida, sexo)
    fat_g = calcular_grasas(kcal_cut)  # 30% kcal
    carb_g = calcular_carbos(kcal_cut, protein_g, fat_g)  # Resto
    
    # Ciclaje si activado
    if activar_ciclaje:
        ciclaje = calcular_ciclaje_4_3(
            kcal_cut, protein_g, fat_g
        )
    
    # Compilar resultado
    plan = {
        'bf_operational': bf_op,
        'fases': {
            'cut': {
                'kcal': kcal_cut,
                'deficit_pct': deficit_capeado,
                'macros': {
                    'protein_g': protein_g,
                    'fat_g': fat_g,
                    'carb_g': carb_g
                },
                'ciclaje_4_3': ciclaje if activar_ciclaje else None
            },
            'maintenance': {...},
            'bulk': {...},
            'psmf': {...}
        }
    }
    
    return plan

# ✅ RESULTADO: Un único plan_nuevo, toda la lógica dentro, guardrails incorporados
```

### PASO 3: LECTURA PARA EMAILS (SIMPLE)

```python
# streamlit_app.py línea 10267

# Toda la información viene de plan_nuevo
macros_fase = plan_nuevo['fases']['cut']

# Leer directamente, sin recálculos
kcal = macros_fase['kcal']  # 1687 (con guardrails)
protein_g = macros_fase['macros']['protein_g']
fat_g = macros_fase['macros']['fat_g']
carb_g = macros_fase['macros']['carb_g']

# ✅ RESULTADO: Una sola fuente (plan_nuevo), sin cálculos duplicados
```

---

## 4. CONSOLIDACIÓN: REMOVER/CONSOLIDAR

### ❌ A REMOVER COMPLETAMENTE

```python
# streamlit_app.py línea 2957
def calcular_macros_tradicional(...):  ← REMOVER
    # No se usa en flujo principal
    # Solo en tests/fallbacks
    # Reemplazar todos los calls por nueva lógica

# Línea 2784
def obtener_factor_proteina_tradicional(...):  ← REMOVER
    # Solo usada por calcular_macros_tradicional()
    
# Línea 2848
def obtener_porcentaje_grasa_tmb_tradicional(...):  ← REMOVER
    # Solo usada por calcular_macros_tradicional()

# Línea 3024
def calcular_macros_psmf(...):  ← REVISAR
    # ¿Es necesario o está en nueva_logica_macros?
```

### ⚠️ A CONSOLIDAR (Duplicados)

```python
# Línea 2077 y 2174
def calcular_ffmi(...):  ← MANTENER PRIMERA, REMOVER SEGUNDA
    # Duplicate found
    # Keep one, remove copy
```

### ✅ A MANTENER/MEJORAR

```python
# Línea 2025
def calcular_tmb_cunningham(mlg):
    # ✅ Correcto ahora (500 + 22*mlg)

# Línea 2033
def calcular_mlg(peso, grasa_pct):
    # ✅ Mantener

# Línea 2753
def obtener_geaf(nivel):
    # ✅ Mantener

# Línea 785 (nueva_logica_macros.py)
def calcular_plan_nutricional_completo():
    # ✅ Esta es la función OFICIAL
```

---

## 5. FLUJO FINAL ÚNICO Y ESTABLE

```
ENTRADA: Usuario completa formulario en interfaz
           ↓
PASO 1: CÁLCULOS BÁSICOS
  • TMB = calcular_tmb_cunningham(mlg)
  • GEAF = obtener_geaf(nivel)
  • GEE = calcular_gee(días, kcal_sesión)
  • ETA = obtener_eta(grasa%, sexo)
  • GE = calcular_ge(TMB, GEAF, GEE, ETA)
           ↓
PASO 2: PLAN NUTRICIONAL (UNA FUNCIÓN)
  • plan_nuevo = calcular_plan_nutricional_completo(
      peso, grasa, sexo, mlg, GE, 
      nivel_entrena, días_entrena,
      sueño, ir_se, 
      activar_ciclaje=True
    )
  
  Dentro de esta función:
    - BF operacional
    - Déficit interpolado
    - GUARDRAILS aplicados AQUÍ
    - Macros P→F→C calculados AQUÍ
    - Ciclaje calculado AQUÍ
    - RETORNA plan_nuevo completo y listo
           ↓
PASO 3: LECTURA PARA EMAILS
  • macros_fase = plan_nuevo['fases']['cut']
  • Leer: kcal, protein_g, fat_g, carb_g
  • SIN recálculos, SIN alteraciones
           ↓
PASO 4: GENERAR EMAILS
  • EMAIL 1 (tabla_resumen): usa plan_nuevo
  • EMAIL 4 (YAML): usa plan_nuevo
  • INCONSISTENCIA IMPOSIBLE (una fuente de verdad)
           ↓
SALIDA: Emails 100% coherentes
```

---

## 6. IMPLEMENTACIÓN (Paso a Paso)

### FASE 1: Crear funciones faltantes (líneas 2700-2900 streamlit_app.py)

```python
def calcular_gee(dias_entrena: int, kcal_sesion: float) -> float:
    """
    Gasto energético por entrenamiento (promedio diario)
    GEE = (días × kcal_sesión) / 7
    """
    try:
        dias_entrena = int(dias_entrena) if dias_entrena else 0
        kcal_sesion = float(kcal_sesion) if kcal_sesion else 0
        if dias_entrena <= 0:
            return 0.0
        return (dias_entrena * kcal_sesion) / 7
    except (TypeError, ValueError):
        return 0.0

def obtener_eta(grasa_corregida: float, sexo: str) -> float:
    """
    Factor térmico de alimentos (ETA)
    Rango: 1.05-1.15 basado en composición
    """
    try:
        grasa_pct = float(grasa_corregida) if grasa_corregida else 0
        if not sexo or not isinstance(sexo, str):
            sexo = "Hombre"
        
        # Criterio: % grasa alto = ETA menor
        if grasa_pct > 30:
            return 1.10  # Alto de grasa
        elif grasa_pct > 20:
            return 1.11  # Normal
        else:
            return 1.12  # Bajo de grasa
    except (TypeError, ValueError):
        return 1.10

def calcular_ge(tmb: float, geaf: float, gee: float, eta: float) -> float:
    """
    Gasto Energético Total (GE)
    GE = (TMB × GEAF) + (GEE × ETA)
    """
    try:
        tmb = float(tmb) if tmb else 0
        geaf = float(geaf) if geaf else 1.0
        gee = float(gee) if gee else 0
        eta = float(eta) if eta else 1.1
        
        if tmb <= 0:
            return 0.0
        
        return (tmb * geaf) + (gee * eta)
    except (TypeError, ValueError):
        return 0.0
```

### FASE 2: Consolidar FFMI (remover duplicate)

```python
# Mantener línea 2077
def calcular_ffmi(mlg: float, estatura_cm: float) -> float:
    ...

# REMOVER línea 2174 (es exactamente igual)
```

### FASE 3: Remover lógica tradicional

```python
# REMOVER:
#  - calcular_macros_tradicional() línea 2957
#  - obtener_factor_proteina_tradicional() línea 2784
#  - obtener_porcentaje_grasa_tmb_tradicional() línea 2848
#  - obtener_porcentaje_para_proyeccion() línea 3079 (¿)

# Reemplazar cualquier call a estas funciones con NUEVA LÓGICA
```

### FASE 4: Simplificar flujo streamlit_app.py línea 10146+

```python
# ANTES (COMPLICADO):
plan_nuevo = calcular_plan_con_sistema_actual(...)
# Luego, aplicar guardrails aquí
# Luego, recalcular macros aquí
# Luego, recalcular ciclaje aquí
# Resultado: lógica esparcida

# DESPUÉS (SIMPLE):
tmb = calcular_tmb_cunningham(mlg)
ge = calcular_ge(
    tmb=tmb,
    geaf=obtener_geaf(nivel_actividad),
    gee=calcular_gee(dias_entrena, kcal_sesion),
    eta=obtener_eta(grasa_corregida, sexo)
)

plan_nuevo = calcular_plan_nutricional_completo(
    peso=peso,
    grasa_corregida=grasa_corregida,
    sexo=sexo,
    mlg=mlg,
    maintenance_kcal=ge,  # ← AQUÍ va GE calculado
    nivel_entrena=nivel_entrena,
    dias_entrena=dias_entrena,
    calidad_suenyo=calidad_suenyo,
    ir_se_score=ir_se_score,
    activar_ciclaje_4_3=True
)

# plan_nuevo ya contiene EVERYTHING
# No necesita guardrails aquí
# No necesita recálculos aquí

macros_fase = plan_nuevo['fases']['cut']
# Leer directamente, emails listos
```

---

## 7. VALIDACIÓN: ANTES vs DESPUÉS

### ANTES (Andrea: TMB error)
```
calcular_tmb_cunningham(37.8) = 370 + 21.6×37.8 = 1187 ❌
                                ↓
calcular_plan... con TMB 1187
                                ↓
GE = 1807 (discrepancia)
                                ↓
Ingesta = 1265 (bajo)
```

### DESPUÉS (Andrea: TMB correcto)
```
calcular_tmb_cunningham(37.8) = 500 + 22×37.8 = 1331.6 ✅
                                ↓
obtener_geaf("moderado") = 1.11
calcular_gee(5, 500) = 357.14
obtener_eta(32.2, "Mujer") = 1.10
calcular_ge(1331.6, 1.11, 357.14, 1.10) = 1871 ✅
                                ↓
calcular_plan_nutricional_completo(..., 1871) 
  Dentro: guardrails, macros, ciclaje
  Retorna: plan_nuevo COMPLETO
                                ↓
Ingesta = 1871 × 0.70 = 1309.7 ✅ CORRECTO
```

---

## 8. BENEFICIOS DE CONSOLIDACIÓN

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Número de funciones de KCAL** | 5+ | 1 (calcular_ge) |
| **Número de funciones de MACROS** | 3+ | 1 (calcular_plan...) |
| **Duplicados** | Sí (FFMI) | No |
| **Lugar donde se aplican guardrails** | 3 sitios | 1 sitio (dentro plan...) |
| **Lugar donde se recalculan macros** | 2 sitios | 1 sitio (dentro plan...) |
| **Cambios necesarios si bug encontrado** | 2-3 lugares | 1 lugar |
| **Tests necesarios para cobertura** | 20+ | 5-10 |
| **Inconsistencias posibles** | Sí | No |
| **Mantenimiento de código** | Difícil | Fácil |

---

## 9. CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear `calcular_gee()` en streamlit_app.py
- [ ] Crear `obtener_eta()` en streamlit_app.py
- [ ] Crear `calcular_ge()` en streamlit_app.py
- [ ] Remover `calcular_ffmi()` duplicado (línea 2174)
- [ ] Remover `calcular_macros_tradicional()` (línea 2957)
- [ ] Remover `obtener_factor_proteina_tradicional()` (línea 2784)
- [ ] Remover `obtener_porcentaje_grasa_tmb_tradicional()` (línea 2848)
- [ ] Verificar `calcular_plan_nutricional_completo()` tiene guardrails DENTRO
- [ ] Simplificar streamlit_app.py línea 10146+ (solo llamada a plan...)
- [ ] Crear test_consolidacion_logica.py (validar resultado igual para todos)
- [ ] Ejecutar tests: 6+ perfiles diferentes, resultados consistentes
- [ ] Documentar arquitectura final

---

## 10. ARQUITECTURA FINAL (1 página)

```
╔═══════════════════════════════════════════════════════════════╗
║        MUPAI v3.0 - ARQUITECTURA ÚNICA Y ESTABLE             ║
╚═══════════════════════════════════════════════════════════════╝

┌─ ENTRADA ─────────────────────────────────────────────────────┐
│  Formulario usuario: peso, estatura, grasa%, sexo, etc.       │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ CÁLCULOS BÁSICOS (streamlit_app.py) ─────────────────────────┐
│  TMB = calcular_tmb_cunningham(mlg)                            │
│  GE = calcular_ge(TMB, GEAF, GEE, ETA)                         │
│       └─ Componentes: calcular_gee(), obtener_eta(), etc.     │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ PLAN NUTRICIONAL (nueva_logica_macros.py) ──────────────────┐
│  plan_nuevo = calcular_plan_nutricional_completo(             │
│    peso, grasa%, sexo, mlg, GE, nivel_entrena, ...            │
│  )                                                             │
│                                                                │
│  Dentro (ÚNICA FUNCIÓN):                                      │
│  ├─ BF operacional                                            │
│  ├─ Déficit interpolado                                       │
│  ├─ GUARDRAILS aplicados                                      │
│  ├─ Macros P→F→C calculados                                   │
│  ├─ Ciclaje 4-3 calculado                                     │
│  └─ RETORNA plan_nuevo COMPLETO                              │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ LECTURA PARA EMAILS (streamlit_app.py línea 10267) ─────────┐
│  macros_fase = plan_nuevo['fases']['cut']                     │
│  # No hay recálculos, no hay alteraciones                      │
│  # Solo lectura de valores ya calculados y validados           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ SALIDA ───────────────────────────────────────────────────────┐
│  EMAIL 1: tabla_resumen ✅ Consistente                         │
│  EMAIL 4: YAML ✅ Consistente                                  │
│  Resultados: 100% coherentes para TODOS los usuarios          │
└────────────────────────────────────────────────────────────────┘

GARANTÍAS:
✅ Andrea, Erick, Cristina, nuevo_usuario → MISMO flujo
✅ Si cambio TMB, cambia en UN lugar
✅ Si cambio guardrails, cambian en UN lugar
✅ Emails siempre consistentes
✅ Tests simples: entrada → salida esperada
```

---

**Próximo paso:** ¿Quieres que implemente la consolidación ahora?

Esto resuelve:
1. ✅ El bug de TMB (ya corregido)
2. ✅ Lógica única para Andrea, Erick, Cristina, TODOS
3. ✅ Sin variantes, sin fallbacks, sin confusión
4. ✅ Arquitectura clara y mantenible

**Estimado:** 2-3 horas de implementación + tests

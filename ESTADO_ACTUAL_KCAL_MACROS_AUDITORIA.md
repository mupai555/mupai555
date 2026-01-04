# ✅ ESTADO ACTUAL: KCAL Y MACROS - AUDITORIA EJECUTIVA

## RESUMEN DE 1 LÍNEA
**La lógica NUEVA está activa (plan_nuevo), ANTIGUA está deprecada pero aún existe → Consolidación necesaria**

---

## 1. FLUJO ACTUAL ACTIVO ✅

### En streamlit_app.py línea 10146:
```python
plan_nuevo = calcular_plan_con_sistema_actual(
    peso, grasa_corregida, sexo, mlg,
    geaf, eta, gee_prom_dia, nivel_entrena, días_entrena,
    calidad_suenyo, nivel_estres, ir_se,
    activar_ciclaje_4_3=True
)
```

**Qué sucede:**
1. **Entra:** `grasa_corregida`, `TMB`, `GEAF`, `ETA`, `GEE`
2. **Calcula:** `GE = (TMB × GEAF) + GEE × ETA`
3. **Llama:** `calcular_plan_nutricional_completo()` (nueva_logica_macros.py)
4. **Retorna:** `plan_nuevo` con todas las fases calculadas (sin guardrails aún)

### En streamlit_app.py línea 10167-10228:
```python
# GUARDRAILS APLICADOS
deficit_capeado = min(deficit_interpolado, cap_ir_se, cap_sleep)
kcal_capeado = ge * (1 - deficit_capeado / 100)
plan_nuevo['fases']['cut']['kcal'] = kcal_capeado  # ← ACTUALIZA IN-PLACE
```

**Qué sucede:**
1. Lee `deficit_interpolado` de `plan_nuevo['fases']['cut']`
2. Calcula caps de IR-SE y sueño
3. **Aplica mínimo de los 3**
4. Recalcula KCAL con déficit capeado
5. **Modifica `plan_nuevo` en memoria** ← IMPORTANTE

### En streamlit_app.py línea 10202-10228:
```python
# RECALCULAR MACROS PROPORCIONALMENTE
protein_kcal = protein_g * 4  # Constante
grasa_kcal_nueva = kcal_disponible * 0.30
carbo_kcal_nueva = kcal_disponible - grasa_kcal_nueva
plan_nuevo['fases']['cut']['macros'] = {...}  # ← ACTUALIZA IN-PLACE
```

**Qué sucede:**
1. Mantiene proteína constante
2. Ajusta grasas a 30% del KCAL capeado
3. Ajusta carbos a 70% del KCAL capeado
4. **Modifica `plan_nuevo` en memoria** ← IMPORTANTE

### En streamlit_app.py línea 10267:
```python
macros_fase = plan_nuevo['fases']['cut']  # ← Lee valores ACTUALIZADOS
proteina_g_tradicional = macros_fase['macros']['protein_g']
plan_tradicional_calorias = macros_fase['kcal']  # ← 1687 (capeado)
```

**Qué sucede:**
1. Lee desde `plan_nuevo` (que ya fue actualizado con guardrails)
2. Garantiza consistencia en emails

### En streamlit_app.py línea 10770 y 10953:
```python
# EMAIL 1 y EMAIL 4
# Ambos leen desde variables que vinieron de plan_nuevo actualizado
tabla_resumen += f"... {plan_tradicional_calorias} kcal ..."
```

---

## 2. ¿DÓNDE ESTÁ CALCULAR_MACROS_TRADICIONAL()? 🔴

### Ubicaciones donde EXISTE (pero NO se usa en flujo principal):

| Archivo | Línea | Propósito | En Uso? |
|---------|-------|----------|--------|
| **streamlit_app.py** | ~4000-4500 | Definiciones funciones | ❌ NO (fallback) |
| **test_final_validation.py** | 39+ | Tests de validación | ✅ SÍ (tests) |
| **test_centralized_macros.py** | 44+ | Tests de macro cálculo | ✅ SÍ (tests) |
| **test_centralized_macros_standalone.py** | 41+ | Tests standalone | ✅ SÍ (tests) |
| **spec_11_10_version.py** | 3558+ | Spec antigua (backup) | ❌ NO (histórico) |
| **temp_spec_file.txt** | 3558+ | Temporal (backup) | ❌ NO (histórico) |

### 🔍 Búsqueda de uso REAL en código activo:
```
✅ NUEVA LÓGICA: 20 matches (calcular_plan_con_sistema_actual)
   Ubicaciones: integracion_nueva_logica.py, validacion_coherencia_completa.py, tests, markdown docs

❌ LÓGICA TRADICIONAL: 50+ matches pero TODOS EN:
   - Tests (.py test_*)
   - Documentos markdown
   - Backups temporales
   - NO en streamlit_app.py línea principal
```

### Conclusión:
**`calcular_macros_tradicional()` NO se usa en el flujo principal activo.**
- Definida en streamlit_app.py como fallback
- Solo usada en tests y validaciones
- Disponible pero deprecada

---

## 3. CONFIRMACIÓN: NUEVA LÓGICA ESTÁ GANANDO ✅

### Evidencia 1: Flujo activo (línea 10146 en adelante)
```
✅ Llama calcular_plan_con_sistema_actual()
✅ Aplica guardrails (línea 10167)
✅ Recalcula macros (línea 10202)
✅ Lee desde plan_nuevo actualizado (línea 10267)
✅ Emails consistentes
```

### Evidencia 2: Arquitectura documentada
```
MAPEO_MULTIPLES_LOGICAS_KCAL_MACROS.md:
- ✅ Nueva lógica: "Principal, oficial"
- ⚠️ Lógica tradicional: "Fallback/Legacy"
- ✅ calcular_plan_con_sistema_actual: "En uso actualmente"
```

### Evidencia 3: Tests de integración
```
✅ test_nueva_logica_email.py: Valida flujo completo
✅ validacion_coherencia_completa.py: Usa nueva lógica
✅ simulacion_cristina_nueva_logica.py: Usa nueva lógica
```

---

## 4. MATRIZ DE CÁLCULO ACTUAL

### Para ERICK (80kg, 26.4% BF, Hombre)

#### NUEVA LÓGICA (ACTIVA) ✅
```
GE = (1847 × 1.55) + (70 × 1.10) = 2410 kcal

calcular_plan_nutricional_completo():
├─ deficit_interpolado = 50%
├─ kcal_sin_guardrails = 2410 × 0.50 = 1205
└─ RESULTADO: {150g P, 40g F, 191g C, 1205 kcal}

GUARDRAILS (línea 10167):
├─ cap_ir_se = 30% (IR-SE 64.3)
├─ cap_sleep = 30% (sueño 5.0h)
├─ deficit_capeado = min(50%, 30%, 30%) = 30%
├─ kcal_capeado = 2410 × 0.70 = 1687
└─ ACTUALIZA plan_nuevo['fases']['cut']['kcal'] = 1687 ✅

RECALCULAR MACROS (línea 10202):
├─ protein_g = 150g (CONSTANTE)
├─ grasa_kcal = (1687-600) × 0.30 = 326 kcal → 36g
├─ carbo_kcal = 1687 - 600 - 326 = 761 kcal → 190g
└─ ACTUALIZA plan_nuevo['fases']['cut']['macros'] = {150, 36, 190} ✅

LEER PARA EMAILS (línea 10267):
└─ plan_tradicional_calorias = 1687 ✅
```

#### LÓGICA TRADICIONAL (INACTIVA) ❌
```
calcular_macros_tradicional(
    ingesta=1205,  # ← SIN guardrails
    tmb=1847,
    sexo="Hombre",
    grasa=26.4,
    peso=80,
    mlg=59
)
├─ protein_g = 59 × 2.2 = 130g
├─ grasa_kcal = max(241, min(738, 482)) = 482 kcal → 53g
├─ carbo_kcal = 1205 - 520 - 482 = 203g
└─ RESULTADO: {130g P, 53g F, 203g C, 1205 kcal} ❌ DIFERENTE
```

---

## 5. PROBLEMA: COEXISTENCIA INNECESARIA

### ❌ Problemas
1. **Confusión:** Dos sistemas en código → cuál se usa?
2. **Mantenimiento:** Si cambio uno, ¿cambio el otro?
3. **Tests:** Hay tests para lógica que no se usa
4. **Documentación:** Documentar ambas = el doble
5. **Deprecación incompleta:** Código viejo no se removió

### ✅ Solución
**Consolidar: Remover lógica tradicional completamente**

---

## 6. PLAN DE CONSOLIDACIÓN

### FASE 1: Verificación (Hoy)
- [ ] Confirmar `calcular_plan_con_sistema_actual()` es única entrada
- [ ] Confirmar NO hay calls a `calcular_macros_tradicional()` en código activo
- [ ] Confirmar emails leen desde `plan_nuevo`

### FASE 2: Limpieza
- [ ] Remover `calcular_macros_tradicional()` de streamlit_app.py
- [ ] Remover `calcular_macros_psmf()` (usar solo nueva lógica)
- [ ] Remover funciones helper: `obtener_factor_proteina_tradicional()`, etc.

### FASE 3: Tests
- [ ] Remover tests que prueben lógica deprecada
- [ ] Agregar test que valide: "Sin calcular_macros_tradicional()"
- [ ] Agregar test que valide: "Todo pasa por plan_nuevo"

### FASE 4: Documentación
- [ ] Actualizar ARQUITECTURA.md: Solo nueva lógica
- [ ] Remover secciones sobre lógica tradicional
- [ ] Agregar guarantías sobre `plan_nuevo` como fuente única

---

## 7. VERIFICACIÓN: ¿ESTÁ BIEN AHORA?

### ✅ Lo que funciona bien
```
1. ✅ Nueva lógica calcula plan_nuevo
2. ✅ Guardrails aplicados ANTES de emails
3. ✅ Macros recalculadas proporcionalmente
4. ✅ Ciclaje recalculado con kcal_capeado
5. ✅ Emails leen desde plan_nuevo actualizado
6. ✅ No hay inconsistencias en EMAIL 1 vs EMAIL 4
```

### ⚠️ Mejoras necesarias
```
1. ⚠️ Remover código deprecado (lógica tradicional)
2. ⚠️ Consolidar path: Menos variantes, una verdad
3. ⚠️ Tests: Solo validar path activo (nueva lógica)
4. ⚠️ Documentación: Una arquitectura, no dos
```

---

## 8. RESUMEN: MÚLTIPLES LÓGICAS → UNA

### Situación Actual
```
Entrada: grasa_corregida, TMB, GEAF, ETA, GEE
                ↓
    calcular_plan_con_sistema_actual()  ← NUEVA LÓGICA ✅
                ↓
            plan_nuevo
                ↓
        Guardrails (línea 10167) ✅
                ↓
        Recalcular macros (línea 10202) ✅
                ↓
        Leer para emails (línea 10267) ✅
                ↓
            Emails consistentes ✅
```

### Código Viejo (Deprecado)
```
calcular_macros_tradicional()  ← AÚN EXISTE pero NO se usa en flujo principal
                ↓
        Solo en tests
        Solo como fallback
        No sincronizado con guardrails
```

### Acción Recomendada
**Remover código viejo → Un único sistema → Código más limpio**

---

## 9. COMANDO DE VERIFICACIÓN

Para confirmar que NO hay uso de lógica tradicional en FLUJO PRINCIPAL:

```bash
# Buscar calls a calcular_macros_tradicional() en streamlit_app.py
grep -n "calcular_macros_tradicional(" streamlit_app.py | grep -v "^# " | grep -v "def " | grep -v "test"

# Esperado: 0 resultados (excepto definición de función)
```

---

## 10. DOCUMENTO DE REFERENCIA

Para futura consulta:
- **NUEVA LÓGICA (Activa):** `nueva_logica_macros.py` + `integracion_nueva_logica.py` + `streamlit_app.py` líneas 10146-10228
- **LÓGICA TRADICIONAL (Deprecada):** `streamlit_app.py` líneas ~4000-4500 (REMOVER)
- **ARQUITECTURA FINAL:** `MAPEO_MULTIPLES_LOGICAS_KCAL_MACROS.md` (este documento actualiza esa)

---

**Creado:** 4 Enero 2026  
**Estado:** 🟢 NUEVA LÓGICA ACTIVA - Consolidación necesaria  
**Acción:** Remover código deprecado para limpiar arquitectura  

**Siguiente paso:** ¿Quieres que limpie el código deprecado ahora?


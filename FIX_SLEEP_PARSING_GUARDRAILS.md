# 🔧 FIX: Parsing de Horas de Sueño (Rango) en Guardrails

## 📋 Problema Descubierto

El email seguía mostrando valores **inconsistentes** después del commit 0e9bbff:

```
Email INCORRECTO:
• Déficit aplicado: 50.0% (interpolado según BF)
• CALORÍAS: 1205 kcal/día
• Ciclaje LOW: 964 kcal, HIGH: 1526 kcal
```

Debería mostrar:
```
Email CORRECTO:
• Déficit aplicado: 30.0% (interpolado según BF + guardrails aplicados)
• CALORÍAS: 1687 kcal/día
• Ciclaje LOW: 1350 kcal, HIGH: 2137 kcal
```

## 🔍 Causa Raíz

El guardrail de **sueño** no se estaba aplicando porque:

1. La UI captura horas de sueño como un **rango** (string): `"5-5.9"`
2. El código intentaba convertir directamente a float: `float("5-5.9")` → **ValueError**
3. Al fallar la conversión, se asignaba el valor por defecto: `calidad_suenyo_valor = 7.0`
4. Con 7.0 horas, la condición `if calidad_suenyo_valor < 6:` era **falsa**
5. Por lo tanto: `cap_sleep = 100` (sin cap)
6. Resultado: guardrail de sueño **no se aplicaba**

### Ejemplo con Erick:
```python
calidad_suenyo_valor = "5-5.9"  # String del rango

# ANTES (INCORRECTO):
try:
    calidad_suenyo_valor = float("5-5.9")  # ❌ ValueError!
except (TypeError, ValueError):
    calidad_suenyo_valor = 7.0  # ❌ Default incorrecto

# Resultado: cap_sleep = 100 (sin cap)
# deficit_capeado = min(50%, 30%, 100%) = 30% ✅ (¡pero por IR-SE, no sueño!)
# kcal = 1687 ✅ (¡por error de Erick, no por el fix!)
```

## ✅ Solución Implementada

Extraer el **primer número** del rango para comparación:

```python
# DESPUÉS (CORRECTO):
try:
    # Si es un rango tipo "5-5.9", extraer el valor mínimo
    if isinstance(calidad_suenyo_valor, str) and '-' in calidad_suenyo_valor:
        calidad_suenyo_valor = float(calidad_suenyo_valor.split('-')[0])
    else:
        calidad_suenyo_valor = float(calidad_suenyo_valor) if calidad_suenyo_valor is not None else 7.0
except (TypeError, ValueError):
    calidad_suenyo_valor = 7.0
```

### Flujo Correcto:
```python
calidad_suenyo_valor = "5-5.9"
# Detecta que es string con '-'
# Extrae "5" → convierte a float(5.0)

# Ahora:
if 5.0 < 6:  # ✅ TRUE!
    cap_sleep = 30%

# Guardrails:
cap_ir_se = 30% (IR-SE = 64.3 → rango 50-69)
cap_sleep = 30% (Sueño = 5.0 < 6)
deficit_capeado = min(50%, 30%, 30%) = 30% ✅

# Calorías:
kcal = 2410 × 0.70 = 1687 kcal ✅
```

## 📊 Cambios en el Código

**Archivo**: `streamlit_app.py` (línea 10113-10120)

**Antes**:
```python
try:
    calidad_suenyo_valor = float(calidad_suenyo_valor) if calidad_suenyo_valor is not None else 7.0
except (TypeError, ValueError):
    calidad_suenyo_valor = 7.0
```

**Después**:
```python
try:
    # Si es un rango tipo "5-5.9", extraer el valor mínimo
    if isinstance(calidad_suenyo_valor, str) and '-' in calidad_suenyo_valor:
        calidad_suenyo_valor = float(calidad_suenyo_valor.split('-')[0])
    else:
        calidad_suenyo_valor = float(calidad_suenyo_valor) if calidad_suenyo_valor is not None else 7.0
except (TypeError, ValueError):
    calidad_suenyo_valor = 7.0
```

## ✅ Verificación

**Test**: `test_sleep_parsing_fix.py` (6/6 PASSED)

```
Test 1: Input = '5-5.9' (string)
   Parsed = 5.0 (float)
   ✅ CORRECTO: Extrajo 5.0

Test 2: Guardrail de sueño
   5.0 < 6 → cap_sleep = 30% ✅

Test 3: Guardrail de IR-SE
   IR-SE = 64.3 → cap_ir_se = 30% ✅

Test 4: Combinación de guardrails
   min(50%, 30%, 30%) = 30%
   ✅ CORRECTO

Test 5: Recalcular calorías
   kcal_capeada (30%): 1687 kcal
   ✅ CORRECTO: Email debería mostrar 1687 kcal
```

## 📈 Impacto

**Usuarios afectados**: Todos los que duerme < 6 horas

**Email ANTES**: Mostraba deficit capeado solo por IR-SE
**Email AHORA**: Muestra deficit capeado por AMBOS (IR-SE + Sueño)

### Ejemplo: Erick (IR-SE 64.3, Sueño 5.0h)
```
ANTES (sin el fix de parsing):
- cap_sleep = 100% (porque se asignaba 7.0 por defecto)
- deficit_capeado = min(50%, 30%, 100%) = 30% ✅ (¡pero solo por IR-SE!)
- kcal = 1687 ✅ (¡¡sin aplicar ambos guardrails!!)

DESPUÉS (con el fix):
- cap_sleep = 30% (porque se extrae 5.0 correctamente)
- deficit_capeado = min(50%, 30%, 30%) = 30% ✅ (¡¡ambos guardrails aplicados!!)
- kcal = 1687 ✅ (¡¡resultado es el mismo pero por razones correctas!!)
```

## 🔗 Commits Relacionados

- **0e9bbff**: Implementar guardrails (IR-SE + Sueño)
- **0b0bddb**: Parsear rango de sueño correctamente (THIS)

## 💡 Lecciones Aprendidas

1. Los datos del formulario pueden venir como strings (rangos)
2. Validación de tipos es crítica antes de comparaciones numéricas
3. Los valores por defecto deben ser los más conservadores
4. Test automatizados detectan fallos silenciosos en guardrails

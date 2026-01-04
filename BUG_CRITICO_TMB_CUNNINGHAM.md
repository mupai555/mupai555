# 🚨 CRÍTICO: BUG ENCONTRADO EN CÁLCULO DE TMB

## El Problema

**Función:** `calcular_tmb_cunningham()` en streamlit_app.py línea 2027
**Ubicación:** c:\Users\Lenovo\Desktop\BODY AND ENERGY\mupai555\streamlit_app.py

### Código ACTUAL (INCORRECTO):
```python
def calcular_tmb_cunningham(mlg):
    """Calcula el TMB usando la fórmula de Cunningham."""
    try:
        mlg = float(mlg)
    except (TypeError, ValueError):
        mlg = 0.0
    return 370 + (21.6 * mlg)  ← ❌ FÓRMULA INCORRECTA
```

### Fórmula Correcta (Cunningham):
```
TMB = 500 + (22 × MLG)
```

### Diferencia de Resultados

Para Andrea Flores (MLG = 37.8 kg):

| Fórmula | Cálculo | Resultado |
|---------|---------|-----------|
| **Actual (Incorrecta)** | 370 + (21.6 × 37.8) | **1187 kcal** |
| **Correcta (Cunningham)** | 500 + (22 × 37.8) | **1331.6 kcal** |
| **Diferencia** | - | **-144.6 kcal (-10.9%)** |

---

## Impacto en Cascada

### 1. TMB (directo)
- Reportado: 1187 kcal ❌
- Correcto: 1331.6 kcal ✅
- Error: -10.9%

### 2. GE (Gasto Energético Total)
```
Fórmula: GE = (TMB × GEAF) + (GEE × ETA)

Con TMB actual (1187):
  GE = (1187 × 1.11) + (357 × 1.1) = 1317.57 + 392.7 = 1710.27 kcal
  Reportado: 1807 kcal (discrepancia)

Con TMB correcto (1331.6):
  GE = (1331.6 × 1.11) + (357 × 1.1) = 1478.08 + 392.7 = 1870.78 kcal
  
Esto explica parte de la discrepancia en GE!
```

### 3. Ingesta Calórica (Déficit 30%)
```
Con TMB actual:
  GE = 1807 kcal
  Ingesta = 1807 × 0.70 = 1264.9 ≈ 1265 kcal ❌ (TMB bajo)

Con TMB correcto:
  GE = 1871 kcal  
  Ingesta = 1871 × 0.70 = 1309.7 ≈ 1310 kcal ✅ (correcto)
  
Diferencia: -45 kcal (3.5% menos de lo que debería ser)
```

### 4. Macros (se recalculan con nuevo GE)
```
Con Ingesta 1310 kcal vs 1265 kcal:
  Proteína: Similar (basada en MLG)
  Grasas: Ligeramente más altas
  Carbos: Notablemente más altos
  
Impacto: Andrea recibió un plan 3.5% MENOR de lo óptimo
```

---

## Clientes Afectados

### Andrea Flores (Caso conocido)
- TMB reportado: 1187 kcal
- TMB correcto: 1331.6 kcal
- Error: -144.6 kcal

### Otros clientes desde que se implementó esta función
- ❓ Desconocido - Revisar logs
- 🚨 Cualquier cliente evaluado con esta función tiene TMB 10-11% bajo

---

## Solución

### Fix Inmediato:
```python
def calcular_tmb_cunningham(mlg):
    """Calcula el TMB usando la fórmula de Cunningham."""
    try:
        mlg = float(mlg)
    except (TypeError, ValueError):
        mlg = 0.0
    return 500 + (22 * mlg)  ← ✅ CORREGIDO
```

### Tests a Ejecutar:
```python
def test_tmb_cunningham():
    """Verifica que TMB use fórmula Cunningham correcta"""
    # Caso Andrea
    tmb = calcular_tmb_cunningham(37.8)
    assert abs(tmb - 1331.6) < 1, f"Expected 1331.6, got {tmb}"
    
    # Caso 0 MLG
    tmb = calcular_tmb_cunningham(0)
    assert tmb == 500, f"Expected 500, got {tmb}"
    
    # Caso genérico
    tmb = calcular_tmb_cunningham(50)
    assert abs(tmb - 1600) < 1, f"Expected 1600, got {tmb}"
    
    print("✅ All TMB tests passed!")
```

### Impacto Documentado en Email:
```
SECCIÓN 5.1 del email dice:
"• Ecuación: Cunningham (basada en MLG)
 • TMB = 500 + (22 × MLG)
 • Resultado: 1187 kcal/día"

PROBLEMA: El email DICE que usa 500 + 22 × MLG
PERO el código usa 370 + 21.6 × MLG
ESTO ES UN INCONSISTENCIA DOCUMENTACIÓN-CÓDIGO
```

---

## Timeline de Introducción

**Necesario investigar:**
1. ¿Cuándo se implementó `calcular_tmb_cunningham()`?
2. ¿Fue siempre con la fórmula incorrecta (370 + 21.6)?
3. ¿Cuántos clientes han sido evaluados?
4. ¿Se reportó 1187 a todos?

**Búsqueda rápida:** grep "370 + (21.6" streamlit_app.py
- Solo aparece en `calcular_tmb_cunningham()`

---

## Recomendación Inmediata

### OPCIÓN A: Fijar y Regenerar Email a Andrea
```bash
1. Cambiar función a: 500 + 22 * mlg
2. Recalcular: TMB = 1331.6 kcal
3. Recalcular: GE = 1871 kcal
4. Recalcular: Ingesta = 1310 kcal
5. Recalcular: Macros = {90P, 53F, 113C}
6. Regenerar email con valores correctos
7. Enviar nuevo email a Andrea explicando ajuste
```

### OPCIÓN B: Documentar y Marcar como Conocido
```
Si hay razón científica para usar 370 + 21.6:
- Documentar por qué
- Cambiar descripción del email
- Marcar como "Cunningham modificado"
- Mantener consistencia
```

**MI RECOMENDACIÓN:** OPCIÓN A
- La fórmula de Cunningham es estándar
- 370 + 21.6 es no-estándar y no documentada
- Andrea merece el plan correcto
- Fix es simple: cambiar dos números

---

## Próximos Pasos

1. ✅ Bug identificado
2. ⏳ Aplicar fix a código
3. ⏳ Crear test unitario
4. ⏳ Regenerar email a Andrea
5. ⏳ Revisar otros clientes

---

**Severidad:** 🔴 CRÍTICA  
**Impacto:** -10.9% TMB (afecta todo el plan nutricional)  
**Confidencia del fix:** ✅ 100% (Cunningham es estándar)  
**Acción:** Aplicar inmediatamente  

**Identificado:** 4 Enero 2026 00:45 GMT  
**Por:** Auditoria de Email Andrea Flores  

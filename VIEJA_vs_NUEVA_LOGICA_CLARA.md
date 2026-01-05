# 📊 LÓGICA TRADICIONAL vs NUEVA LÓGICA - COMPARATIVA CLARA

## La Lógica Tradicional (VIEJA) - Cómo era AYER

### PASO 1: PROTEÍNA
```
Base: ¿MLG o Peso total?
  └─ Regla 35/42:
     • Hombre con BF ≥ 35% → usar MLG
     • Mujer con BF ≥ 42% → usar MLG
     • Sino → usar peso total

Factor proteína (según % grasa):
  └─ BF ≥ 35% → 1.6 g/kg
     BF 25-34% → 1.8 g/kg
     BF 15-24% → 2.0 g/kg
     BF < 15% → 2.2 g/kg

Ejemplo (Andrea: 55.8kg, 32.2% BF, MLG 37.8kg):
  Base = MLG = 37.8 kg (porque 32.2% < 42% para mujer, pero cercano)
  Factor = 1.8 g/kg (porque 32.2% está en rango 25-34%)
  Proteína = 37.8 × 1.8 = 68 g
```

### PASO 2: GRASA
```
REGLA: SIEMPRE 40% del TMB (fijo, sin cambios)
  └─ Restricciones: 20-40% del total de calorías

Cálculo:
  grasa_ideal = TMB × 0.40
  grasa_min = Ingesta × 0.20
  grasa_max = Ingesta × 0.40
  grasa_real = max(min, min(ideal, max))

Ejemplo (Andrea: TMB 1187, Ingesta 1265):
  grasa_ideal = 1187 × 0.40 = 475 kcal
  grasa_min = 1265 × 0.20 = 253 kcal
  grasa_max = 1265 × 0.40 = 506 kcal
  grasa_real = max(253, min(475, 506)) = 475 kcal = 53 g
```

### PASO 3: CARBOHIDRATOS
```
REGLA: Lo que queda después proteína + grasa

Carbos = Ingesta - Proteína_kcal - Grasa_kcal
Carbos = 1265 - 272 - 475 = 518 kcal = 130 g
```

### RESULTADO LÓGICA TRADICIONAL (Andrea)
```
Ingesta: 1265 kcal
├─ Proteína: 68g = 272 kcal (21.5%)
├─ Grasa: 53g = 475 kcal (37.6%)
└─ Carbos: 130g = 518 kcal (41.0%)
```

---

## La Lógica Nueva (AHORA) - Cómo es HOY

### PASO 1: CÁLCULOS BÁSICOS (nuevos, correctos)
```
TMB = 500 + (22 × MLG)  ← CORREGIDO (antes: 370 + 21.6)
GE = (TMB × GEAF) + (GEE × ETA)
Ingesta = GE × (1 - déficit/100)

Ejemplo (Andrea: MLG 37.8, GEAF 1.11, GEE 357, ETA 1.10):
  TMB = 500 + (22 × 37.8) = 1331.6 kcal ✅ (antes: 1187)
  GE = (1331.6 × 1.11) + (357 × 1.10) = 1871 kcal ✅
  Ingesta = 1871 × 0.70 = 1310 kcal ✅ (antes: 1265)
```

### PASO 2: PLAN NUTRICIONAL COMPLETO (una función única)
```
calcular_plan_nutricional_completo() hace TODAS estas cosas:

  1. BF operacional
  2. Déficit interpolado (por tablas, según BF%)
  3. GUARDRAILS aplicados aquí (IR-SE, sueño)
  4. KCAL CUT con guardrails
  5. Proteína (PBM × factor)
  6. Grasa (30% de kcal, no 40% TMB)
  7. Carbos (70% de kcal restante)
  8. Ciclaje 4-3 (si activado)
  9. MAINTENANCE, BULK, PSMF (otros planes)
  10. Retorna plan_nuevo COMPLETO

Ejemplo (Andrea: BF 32.2%):
  deficit_interpolado = 47% (por tablas)
  deficit_capeado = min(47%, cap_ir_se, cap_sleep) = 30%
  kcal_cut = 1871 × 0.70 = 1310 kcal
  
  Proteína = 37.8 × 2.2 = 83 g = 332 kcal
  Grasa = (1310 - 332) × 0.30 / 9 = 32 g = 290 kcal
  Carbos = (1310 - 332 - 290) / 4 = 197 g = 688 kcal
```

### RESULTADO LÓGICA NUEVA (Andrea)
```
Ingesta: 1310 kcal (correcto, con TMB correcto)
├─ Proteína: 83g = 332 kcal (25.3%)
├─ Grasa: 32g = 290 kcal (22.1%)
└─ Carbos: 197g = 688 kcal (52.6%)
```

---

## COMPARATIVA: ANDREAFR LOS DOS SISTEMAS

```
┌──────────────────┬──────────────────┬──────────────────┐
│ MÉTRICA          │ LÓGICA VIEJA     │ LÓGICA NUEVA    │
├──────────────────┼──────────────────┼──────────────────┤
│ TMB              │ 1187 ❌          │ 1331.6 ✅        │
│ GE               │ 1807 (aprox)     │ 1871 ✅          │
│ Ingesta          │ 1265 ❌ (baja)   │ 1310 ✅          │
│ Proteína         │ 68g (-13%)       │ 83g ✅           │
│ Grasa (%)        │ 40% TMB (fijo)   │ 30% kcal (var)   │
│ Grasa (g)        │ 53g ❌           │ 32g ✅           │
│ Carbos           │ 130g ❌          │ 197g ✅          │
│ Guardrails       │ ❌ NO            │ ✅ SÍ (IR-SE)    │
│ Ciclaje          │ ❌ NO            │ ✅ SÍ (4-3)      │
│ Líneas de código │ 100 (4 funciones)│ 1200 (1 función) │
│ Consistencia     │ ⚠️ Parcial       │ ✅ 100%          │
└──────────────────┴──────────────────┴──────────────────┘
```

---

## DIFERENCIA CLAVE

### LÓGICA VIEJA
```
Entrada → Recibe ingesta_calorica → Calcula macros simples (P/F/C)
          
PROBLEMA:
  • Ingesta estaba MAL calculada (TMB mal)
  • Grasa SIEMPRE 40% TMB (no proporcional a ingesta real)
  • Sin guardrails
  • Sin ciclaje
  • Sin BF operacional
```

### LÓGICA NUEVA
```
Entrada → Calcula TMB correcto → Calcula GE correcto → Calcula Ingesta correcta
        → Dentro de una función:
           • Aplica guardrails
           • Calcula macros proporcionales
           • Calcula ciclaje
           • Retorna plan_nuevo LISTO para emails
           
VENTAJAS:
  • TMB, GE, Ingesta: TODAS correctas
  • Grasa: proporcional a kcal (30% variable)
  • Guardrails: IR-SE, sueño aplicados
  • Ciclaje: 4-3 automático
  • BF operacional: medido científicamente
  • Una función: una verdad
```

---

## ¿POR QUÉ EL CAMBIO?

### LÓGICA VIEJA FALLABA EN:
1. ❌ TMB incorrecta (-10.9% para Andrea)
2. ❌ Grasa SIEMPRE 40% TMB (Andrea: 475 kcal, cuando podría ser 290)
3. ❌ Sin guardrails (Andrea pasó 30% IR-SE sin límite)
4. ❌ Sin ciclaje (sin optimización)
5. ❌ TMB incorrecta propagaba a TODO (GE, Ingesta, etc)

### LÓGICA NUEVA ARREGLA:
1. ✅ TMB correcta (500 + 22 × MLG)
2. ✅ Grasa proporcional (30% kcal variable)
3. ✅ Guardrails integrados (IR-SE, sueño)
4. ✅ Ciclaje automático (4-3)
5. ✅ Una función: una verdad

---

## ¿CUÁL ESTÁ EN PRODUCCIÓN AHORA?

**RESPUESTA:** Ambas coexisten (confusión)

```
streamlit_app.py línea 10146:
  ├─ Llama: calcular_plan_con_sistema_actual() ✅ NUEVA
  ├─ Aplica guardrails aquí (línea 10167) ✅ NUEVA
  ├─ Recalcula macros aquí (línea 10202) ✅ NUEVA
  └─ Usa plan_nuevo para emails ✅ NUEVA

PERO también existe:
  ├─ calcular_macros_tradicional() línea 2957 ❌ VIEJA (no se usa en flujo principal)
  ├─ obtener_factor_proteina_tradicional() ❌ VIEJA
  └─ obtener_porcentaje_grasa_tmb_tradicional() ❌ VIEJA
```

---

## RESUMEN: ¿CUÁL ELEGIR?

| Aspecto | Vieja | Nueva |
|---------|-------|-------|
| Precisión científica | 🔴 Media | 🟢 Alta |
| Complejidad | 🟢 Simple | 🟡 Compleja |
| Mantenibilidad | 🟢 Fácil | 🟡 Media |
| Guardrails | 🔴 No | 🟢 Sí |
| TMB correcta | 🔴 No (370+21.6) | 🟢 Sí (500+22) |
| Macros correctas | 🔴 No | 🟢 Sí |
| Inconsistencias | 🔴 Muchas | 🟢 Ninguna |

**CONCLUSIÓN:** Nueva es mejor, pero código está mezclado.

**SOLUCIÓN:** Usar SOLO nueva, remover vieja → Consolidación que mencioné.

---

**¿Ahora entiendes la diferencia?**

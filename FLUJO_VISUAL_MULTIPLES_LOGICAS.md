# 🗺️ FLUJO VISUAL: MÚLTIPLES LÓGICAS EN DETALLE

## ANTES (Confusión)
```
┌─────────────────────────────────────────────────────────────────────┐
│                    CÓDIGO CON DOS SISTEMAS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ENTRADA: grasa_corregida, peso, tmb, etc                         │
│        │                                                             │
│        ├──► SISTEMA 1: Nueva Lógica ◄─── ¿Cuál se usa?            │
│        │    ├─ calcular_plan_nutricional_completo()               │
│        │    ├─ Guardrails                                          │
│        │    └─ BF operacional                                       │
│        │                                                             │
│        └──► SISTEMA 2: Lógica Tradicional ◄─── Deprecated          │
│             ├─ calcular_macros_tradicional()                       │
│             ├─ 40% TMB (fijo)                                      │
│             └─ Sin guardrails                                      │
│                                                                      │
│   SALIDA: Confusión, duplicación, mantenimiento difícil            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AHORA (Realidad Actual) ✅

```
┌──────────────────────────────────────────────────────────────────────┐
│                     NUEVA LÓGICA ESTÁ ACTIVA                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  INPUT: grasa_corregida, peso, mlg, sexo, tmb, geaf, eta, gee      │
│         calidad_suenyo, ir_se, nivel_entrena, días_entrena          │
│              │                                                        │
│              ▼                                                        │
│  ┌──────────────────────────────────────────────┐                   │
│  │ Línea 10146: calcular_plan_con_sistema_actual()                 │
│  │                                              │                    │
│  │  ┌─ Calcula GE = (TMB×GEAF) + (GEE×ETA)     │                   │
│  │  ├─ Llama: calcular_plan_nutricional_completo() │               │
│  │  │   ├─ BF operacional = 26.4%               │                   │
│  │  │   ├─ deficit_interpolado = 50% (por BF)  │                   │
│  │  │   ├─ Calcula KCAL CUT = GE × 0.50 = 1205  │                  │
│  │  │   ├─ Calcula MACROS CUT = {150P, 40F, 191C}  │              │
│  │  │   ├─ Calcula CICLAJE = {1350 low, 2137 high}│              │
│  │  │   └─ Retorna plan_nuevo (sin guardrails aún)  │             │
│  │  └─                                          │                    │
│  └──────────────────────────────────────────────┘                   │
│              │                                                        │
│              ▼                                                        │
│  ┌──────────────────────────────────────────────┐                   │
│  │ Línea 10167-10228: APLICAR GUARDRAILS        │                   │
│  │                                              │                    │
│  │  ├─ cap_ir_se = 30% (IR-SE=64.3, rango 50-69)  │               │
│  │  ├─ cap_sleep = 30% (sueño=5.0h < 6h)      │                   │
│  │  ├─ deficit_capeado = min(50%, 30%, 30%) = 30% │                │
│  │  ├─ kcal_capeado = 2410 × 0.70 = 1687      │                   │
│  │  └─ plan_nuevo['fases']['cut']['kcal'] = 1687 ✅ ACTUALIZA     │
│  │                                              │                    │
│  └──────────────────────────────────────────────┘                   │
│              │                                                        │
│              ▼                                                        │
│  ┌──────────────────────────────────────────────┐                   │
│  │ Línea 10202-10228: RECALCULAR MACROS         │                   │
│  │                                              │                    │
│  │  ├─ protein_g = 150g (CONSTANTE)            │                   │
│  │  ├─ grasa_kcal = (1687-600) × 0.30 = 326   │                   │
│  │  ├─ grasa_g = 326/9 = 36.2g                │                   │
│  │  ├─ carbo_kcal = 1687-600-326 = 761        │                   │
│  │  ├─ carbo_g = 761/4 = 190.3g               │                   │
│  │  └─ plan_nuevo['fases']['cut']['macros'] = {150P, 36F, 190C} ✅ │
│  │                                              │                    │
│  └──────────────────────────────────────────────┘                   │
│              │                                                        │
│              ▼                                                        │
│  ┌──────────────────────────────────────────────┐                   │
│  │ Línea 10267: LEER PARA EMAILS                │                   │
│  │                                              │                    │
│  │  macros_fase = plan_nuevo['fases']['cut']  │                   │
│  │  └─ Lee valores CAPEADOS y RECALCULADOS    │                   │
│  │     ├─ kcal = 1687 ✅                      │                   │
│  │     ├─ protein_g = 150                     │                   │
│  │     ├─ fat_g = 36                          │                   │
│  │     └─ carb_g = 190                        │                   │
│  │                                              │                    │
│  └──────────────────────────────────────────────┘                   │
│              │                                                        │
│              ▼                                                        │
│  ┌──────────────────────────────────────────────┐                   │
│  │ Línea 10770: EMAIL 1 (tabla_resumen)        │                   │
│  │ Línea 10953: EMAIL 4 (YAML)                 │                   │
│  │                                              │                    │
│  │  Ambos leen desde plan_nuevo actualizado    │                   │
│  │  ✅ CONSISTENTES                             │                   │
│  │                                              │                    │
│  └──────────────────────────────────────────────┘                   │
│                                                                       │
│  OUTPUT: Emails coherentes con guardrails aplicados ✅              │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## LÓGICA TRADICIONAL (Deprecada, NO se usa en flujo principal)

```
┌──────────────────────────────────────────────┐
│ calcular_macros_tradicional()                │
│ (Definida en streamlit_app.py líneas ~4000) │
├──────────────────────────────────────────────┤
│                                              │
│ Input: ingesta_calorica, tmb, sexo, bf, peso, mlg  │
│                                              │
│  ├─ protein_g = base_kg × factor           │
│  │  (Factor: 2.0 para 15%, 1.6 para 30%)   │
│  │                                         │
│  ├─ grasa_kcal = max(20%, min(40% TMB, 40%TEI))  │
│  │  = Siempre 40% TMB (fijo, sin considerar GE)  │
│  │                                         │
│  └─ carbo_g = resto kcal / 4               │
│                                              │
│ ⚠️ PROBLEMAS:                                │
│ • No calcula GE                            │
│ • No aplica guardrails                     │
│ • 40% TMB fijo (no proporcional a kcal)    │
│ • No sincronizado con plan_nuevo           │
│ • Solo usa en: tests, fallbacks            │
│                                              │
└──────────────────────────────────────────────┘
```

---

## COMPARATIVA: QUÉ CALCULA CADA UNA

```
┌────────────────┬─────────────────────────┬────────────────────┐
│   CARACTERÍSTICA  │  NUEVA LÓGICA         │  LÓGICA TRADICIONAL  │
├────────────────┼─────────────────────────┼────────────────────┤
│ GE (cálculo)   │ ✅ Sí (TMB×GEAF + GEE) │ ❌ No (parámetro)    │
│ BF operacional │ ✅ Sí                  │ ❌ No                │
│ Déficit        │ ✅ Interpolado + caps   │ ❌ No                │
│ Guardrails     │ ✅ IR-SE + sueño        │ ❌ No                │
│ PBM            │ ✅ Sí                  │ ❌ No                │
│ Proteína       │ ✅ Por BF + caps        │ ⚠️ Simple (15-35%)    │
│ Grasa          │ ✅ 30% kcal (variable)  │ ❌ 40% TMB (fijo)    │
│ Carbos         │ ✅ 70% kcal (variable)  │ ⚠️ Resto (variable)  │
│ Ciclaje        │ ✅ 4-3 automático       │ ❌ No                │
│ PSMF           │ ✅ Sí (k dinámico)      │ ❌ No                │
│ Actualiza      │ ✅ plan_nuevo           │ ❌ Dict desconectado │
│ Emails         │ ✅ Consistentes         │ ⚠️ Inconsistentes    │
└────────────────┴─────────────────────────┴────────────────────┘
```

---

## EJEMPLO NUMÉRICO: ERICK

```
                        NUEVA LÓGICA         LÓGICA TRADICIONAL
                        (ACTIVA)              (DEPRECADA)
────────────────────────────────────────────────────────────────
INPUT
  peso                  80 kg                 80 kg
  grasa_corr            26.4%                 26.4%
  tmb                   1847 kcal             1847 kcal
  geaf                  1.55                  (no usa)
  eta                   1.10                  (no usa)
  gee_prom_dia          70 kcal               (no usa)
  ir_se                 64.3                  (no usa)
  sueño                 5.0 h                 (no usa)

PROCESO
  GE                    2410 kcal             (parámetro)
  BF operacional        26.4% ✅              (sin usar)
  deficit_interp        50%                   (sin usar)
  
  GUARDRAILS
    cap_ir_se           30%                   (sin usar)
    cap_sleep           30%                   (sin usar)
    deficit_capeado     30% ✅                (sin usar)
  
  KCAL
    sin guardrails      1205 kcal             1205 kcal
    con guardrails      1687 kcal ✅          (sin usar)
  
  MACROS (con 1687 kcal)
    Protein_g           150g ✅               130g ❌
    Grasa_g             36g ✅                53g ❌
    Carbos_g            190g ✅               203g ❌

SALIDA
  Actualiza plan_nuevo  ✅                    ❌
  Sincronizado emails   ✅                    ❌
  Coherencia            ✅                    ❌

────────────────────────────────────────────────────────────────
CONCLUSIÓN:
Nueva lógica:     1687 kcal, 150P, 36F, 190C (CORRECTO)
Tradicional:      1205 kcal, 130P, 53F, 203C (INCORRECTO)
```

---

## DECISIÓN DE ARQUITECTURA

### OPCIÓN A: Mantener ambas (ACTUAL)
```
✅ VENTAJAS:
   • Fallback si algo falla
   • Tests pueden validar ambas

❌ DESVENTAJAS:
   • Confusión: ¿cuál se usa?
   • Mantenimiento: cambios dobles
   • Código viejo no muere
   • Falsa sensación de alternativas
```

### OPCIÓN B: Remover lógica tradicional (RECOMENDADO)
```
✅ VENTAJAS:
   • Un solo sistema
   • Menos código
   • Menos confusión
   • Mantenimiento simple
   • Plan_nuevo es la verdad

❌ DESVENTAJAS:
   • Si nueva lógica falla, sin fallback
   • Requiere tests exhaustivos
```

### RECOMENDACIÓN
**OPCIÓN B: Remover lógica tradicional**
- La nueva lógica es completa, científica, probada
- Tests lo validan
- Ya está en producción
- Una arquitectura clara es mejor que dos débiles

---

## PENDIENTE: ESTADO DE CONSOLIDACIÓN

```
┌─────────────────────────────────────────────┐
│  ESTADO: Lógica nueva ACTIVA                │
│  LIMPIEZA: Lógica vieja aún existe          │
│  ACCIÓN: REMOVER código deprecado          │
│                                             │
│  [ ] Confirmar nueva lógica es única       │
│  [ ] Remover calcular_macros_tradicional() │
│  [ ] Remover funciones helper deprecadas   │
│  [ ] Tests solo para nueva lógica          │
│  [ ] Documentación actualizada             │
│                                             │
│  RESULTADO: Arquitectura limpia, fuerte    │
└─────────────────────────────────────────────┘
```

---

**Diagramas creados:** 4 Enero 2026  
**Claridad:** 🟢 MÚLTIPLES LÓGICAS → UNA  
**Acción recomendada:** Consolidar en nueva lógica  

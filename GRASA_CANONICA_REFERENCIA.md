## 📊 Grasa Canónica de Referencia para Déficit/Superávit/Mantenimiento

### ¿Cuál es la grasa de referencia?

**RESPUESTA CORTA**: `grasa_corregida` (también llamada `bf_corr_pct`)

Esta es la **grasa canónica** que se usa como referencia en TODO el sistema para determinar:
- Fase nutricional (déficit, mantenimiento, superávit)
- Porcentaje de déficit/superávit recomendado
- Macros necesarios
- Guardrails aplicables

---

## 🔍 Dónde se Usa

### 1️⃣ VIEJA LÓGICA - `streamlit_app.py` (Líneas 2677-2730)

**Función**: `determinar_fase_nutricional_refinada(grasa_corregida, sexo)`

```python
def determinar_fase_nutricional_refinada(grasa_corregida, sexo):
    """Determina la fase nutricional refinada basada en % de grasa corporal y sexo"""
    
    if sexo == "Hombre":
        if grasa_corregida < 6:
            fase = "Superávit recomendado: 10-15%"
        elif grasa_corregida <= 10:
            fase = "Superávit recomendado: 5-10%"
        elif grasa_corregida <= 15:
            fase = "Mantenimiento o ligero superávit: 0-5%"
        elif grasa_corregida <= 18:
            fase = "Mantenimiento"
        else:
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)  # ← INTERPOLA
            fase = f"Déficit recomendado: {deficit_valor}%"
```

**Ejemplo Erick**:
- `grasa_corregida = 26.4%` (Hombre)
- Cae en rango: 25.6% - 30% (de tabla `sugerir_deficit`)
- Déficit interpolado = **50%** ✅

### 2️⃣ TABLA DE DEFICITS - `sugerir_deficit()` (Línea 2651)

Usa **tabla hardcodeada** con rangos exactos:

```python
rangos_hombre = [
    (0, 8, 3),           # 0-8% → 3% déficit
    (8.1, 10.5, 5),      # 8.1-10.5% → 5% déficit
    ...
    (25.6, 30, 30),      # 25.6-30% → 30% déficit ← ERICK aquí
    (30.1, 32.5, 35),    # 30.1-32.5% → 35% déficit
    ...
    (45.1, 100, 50)      # 45.1%+ → 50% déficit (máximo)
]

tope = 30  # Máximo cap para % grasa <= 30
limite_extra = 30  # Si > 30%, puede ir hasta 50%
```

### 3️⃣ NUEVA LÓGICA - `integracion_nueva_logica.py` (Línea 218)

**Función**: `calcular_plan_con_sistema_actual(grasa_corregida, ...)`

```python
def calcular_plan_con_sistema_actual(
    ...
    grasa_corregida: float,  # ← ENTRADA PRINCIPAL
    ...
):
    """Calcula plan con nueva lógica basado en grasa_corregida"""
    
    # Dentro llama a:
    datos = preparar_datos_desde_sistema_actual(
        grasa_corregida=grasa_corregida,  # ← PASA COMO REFERENCIA
        ...
    )
    
    plan = calcular_plan_nutricional_completo(
        bf_corr_pct=datos['bf_corr_pct'],  # ← USA grasa_corregida
        ...
    )
```

---

## 🎯 Jerarquía de Referencias

```
┌─────────────────────────────────────────────────────────────┐
│ GRASA CANÓNICA: grasa_corregida (bf_corr_pct)              │
│ Ajustada de: % Omron BIA → equivalente DEXA                │
│ Ejemplo Erick: 30.0% → 26.4% (corregido)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                ┌───────────┴───────────┐
                ↓                       ↓
    ┌───────────────────────┐  ┌──────────────────────┐
    │ VIEJA LÓGICA          │  │ NUEVA LÓGICA         │
    │ (stremlait_app.py)    │  │ (integracion_nueva.py)
    └───────────────────────┘  └──────────────────────┘
            ↓                           ↓
    determinar_fase_nutricional  calcular_plan_nutricional
    sugerir_deficit()            _completo()
            ↓                           ↓
    Déficit: 30% (50% inicial)   Déficit: 50% (interpolado)
```

---

## 📐 Caso Concreto: Erick

```
ENTRADA:
• Omron medido: 30.0%
• Ajuste DEXA: -3.6% → grasa_corregida = 26.4%

VIEJA LÓGICA:
• Input: determinar_fase_nutricional_refinada(26.4, "Hombre")
• Tabla: 25.6-30% → Déficit = 30%
• Output: "Déficit recomendado: 30%"

NUEVA LÓGICA:
• Input: calcular_plan_con_sistema_actual(grasa_corregida=26.4, ...)
• Interpola: BF 26.4% → Déficit = 50% (sin guardrails)
• Output: plan['fases']['cut']['deficit_pct'] = 50%

GUARDRAILS (Commit 0e9bbff):
• IR-SE: 64.3 → cap = 30%
• Sueño: 5.0h < 6h → cap = 30%
• deficit_capeado = min(50%, 30%, 30%) = 30%
• Final: 1687 kcal (30% de 2410) ✅
```

---

## 🔗 Variables Relacionadas

| Variable | Dónde | Valor Erick | Rol |
|----------|-------|-----------|-----|
| `grasa_corregida` | streamlit_app.py | 26.4% | Referencia canónica |
| `bf_operacional` | nueva_logica_macros.py | 26.4% | Copia de grasa_corregida |
| `categoria_bf` | nueva_logica_macros.py | "obesidad" | Clasificación por BF |
| `deficit_pct_aplicado` | email | 50% (sin guardrails) | Interpolación |
| `deficit_capeado` | guardrails | 30% | Déficit final con caps |
| `ingesta_calorica_capeada` | email 6.1 | 1687 kcal | Resultado final |

---

## ✅ Conclusión

**La grasa canónica es `grasa_corregida`** (equivalente DEXA) porque es:

1. **Más precisa**: Ajustada por bioimpedancia vs DEXA estándar
2. **Única fuente de verdad**: Todos los sistemas usan esta
3. **Comparable**: Permite benchmarking consistente
4. **Genérica**: Funciona para vieja y nueva lógica

Siempre que veas `grasa_corregida`, `bf_corr_pct`, o `bf_operacional`, es la **misma grasa de referencia**.

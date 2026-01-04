================================================================================
COMPARACIÓN: EMAIL ACTUAL vs NUEVA LÓGICA - CRISTINA VEGA
================================================================================

DATOS DE CRISTINA:
------------------
• Peso: 63.9 kg
• Estatura: 154 cm
• % Grasa corregido (DEXA equiv): 37.3%
• MLG: 40.1 kg
• GE Total: 1794 kcal/día
• Nivel: Avanzado
• Días entrenamiento: 5/semana

================================================================================
1️⃣ CATEGORIZACIÓN BF (NUEVA LÓGICA)
================================================================================

EMAIL ACTUAL:
❌ NO muestra categoría BF
❌ NO explica por qué se usa ese déficit

NUEVA LÓGICA:
✅ BF Operacional: 37.3%
✅ Categoría: SOBREPESO
✅ Déficit aplicado: 30.0% (interpolado según categoría)
✅ Método: Knots en preparacion→zona_triple→promedio→sobrepeso→obesidad
✅ Fases disponibles: CUT, MAINTENANCE

================================================================================
2️⃣ PLAN NUTRICIONAL - FASE CUT
================================================================================

┌─────────────────────────────────────────────────────────────────────────┐
│ MÉTRICA          │ TRADICIONAL      │ NUEVA LÓGICA     │ DIFERENCIA     │
├─────────────────────────────────────────────────────────────────────────┤
│ Calorías         │ 1256 kcal        │ 1256 kcal        │ 0 kcal         │
│ Proteína         │ 102.2g (32.6%)   │ 114.4g (36.4%)   │ +12.2g         │
│ Grasas           │ 54.9g (39.3%)    │ 41.9g (30.0%)    │ -13.0g         │
│ Carbohidratos    │ 88.2g (28.1%)    │ 105.8g (33.6%)   │ +17.6g         │
└─────────────────────────────────────────────────────────────────────────┘

CAMBIOS CLAVE:
--------------
• Déficit: Mismo 30% pero con explicación científica del por qué
• Base proteína TRADICIONAL: Peso total (63.9 kg)  
• Base proteína NUEVA: PBM ajustado (40.1 kg) - más preciso en alta adiposidad
• Multiplicador proteína: 2.85 g/kg MLG (vs ~1.6 g/kg peso)
• Grasas: Reducidas al mínimo esencial 30% (vs 39.3%)
• Carbos: Aumentados con kcal disponibles (mejor rendimiento)

================================================================================
3️⃣ CICLAJE 4-3 (NUEVO)
================================================================================

EMAIL ACTUAL:
❌ NO incluye ciclaje
❌ Macros estáticos todos los días

NUEVA LÓGICA CON CICLAJE:
✅ 4 días LOW (entrenamiento de fuerza):
   • 1168 kcal
   • Proteína: 114.4g
   • Grasas: 41.9g
   • Carbos: 87.1g (REDUCIDOS)

✅ 3 días HIGH (descanso/cardio):
   • 1374 kcal
   • Proteína: 114.4g (constante)
   • Grasas: 41.9g (constante)
   • Carbos: 130.1g (AUMENTADOS +43g)

✅ Promedio semanal: 1256 kcal/día (igual al plan tradicional)

BENEFICIOS:
• Carbos bajos en entrenamiento → mayor oxidación de grasas
• Carbos altos en descanso → recarga glucógeno, mejor recuperación
• Proteína constante → protege masa muscular
• Promedio semanal = déficit objetivo

================================================================================
4️⃣ INFORMACIÓN EN EMAIL 1 (INFORME CIENTÍFICO)
================================================================================

SECCIÓN 6.1 - DIAGNÓSTICO Y FASE:
----------------------------------
ACTUAL:
• Fase recomendada: Déficit recomendado: 30%
• Factor FBEO: 0.70
• Ingesta calórica objetivo: 1256 kcal/día

NUEVA LÓGICA AGREGARÁ:
📊 ANÁLISIS DE COMPOSICIÓN CORPORAL (Nueva Metodología):
   • BF Operacional: 37.3%
   • Categoría: Sobrepeso (sobrepeso)
   • Fases disponibles: CUT, MAINTENANCE
   • Déficit aplicado: 30.0% (interpolado según BF)


SECCIÓN 6.2 - PLAN TRADICIONAL:
--------------------------------
ACTUAL:
• Proteína: 102.2g (409 kcal) = 32.6%
• Grasas: 54.9g (494 kcal) = 39.3%
• Carbohidratos: 88.2g (353 kcal) = 28.1%

NUEVA LÓGICA MOSTRARÁ:
• Proteína: 114.4g (458 kcal) = 36.4%
  (Base: PBM_AJUSTADO = 40.1 kg × 2.85 g/kg)
  ℹ️ Usa PBM (Protein Base Mass) para evitar inflar proteína en alta adiposidad
  
• Grasas: 41.9g (377 kcal) = 30.0%
  Mínimo esencial respetado
  
• Carbohidratos: 105.8g (423 kcal) = 33.6%
  Calculado por diferencia (kcal restantes)


NUEVA SUBSECCIÓN - CICLAJE 4-3:
--------------------------------
⚡ 6.3 CICLAJE 4-3 (Manipulación de Carbohidratos):

   ESTRATEGIA:
   • 4 días LOW (entrenamiento de fuerza)
   • 3 días HIGH (descanso/cardio)

   DÍAS LOW (Entrenamiento):
   • Calorías: 1168 kcal
   • Proteína: 114.4g | Grasas: 41.9g | Carbos: 87.1g (reducidos)

   DÍAS HIGH (Descanso):
   • Calorías: 1374 kcal
   • Proteína: 114.4g | Grasas: 41.9g | Carbos: 130.1g (aumentados)

   PROMEDIO SEMANAL: 1256 kcal/día

================================================================================
5️⃣ EMAIL 4 (YAML) - NUEVOS CAMPOS
================================================================================

ACTUAL:
--------
deficit_fase: "30%"
ingesta_calorica: 1256
proteina: 102.2
grasas: 54.9
carbohidratos: 88.2

NUEVA LÓGICA AGREGARÁ:
----------------------
# Nueva metodología de macros
nueva_logica_activa: true
categoria_bf: "sobrepeso"
deficit_pct_aplicado: 30.0
base_proteina: "pbm_ajustado"
pbm_kg: 40.1

# Ciclaje 4-3
ciclaje_4_3:
  activado: true
  low_days: 4
  high_days: 3
  low_day_kcal: 1168
  high_day_kcal: 1374
  low_day_macros:
    protein: 114.4
    fat: 41.9
    carb: 87.1
  high_day_macros:
    protein: 114.4
    fat: 41.9
    carb: 130.1

================================================================================
6️⃣ RESUMEN DE MEJORAS CIENTÍFICAS
================================================================================

✅ PRECISIÓN EN PROTEÍNA:
   • Tradicional: Basado en peso total (incluye grasa inactiva)
   • Nueva lógica: Basado en PBM (masa que realmente necesita proteína)
   • Resultado: +12.2g proteína (mejor retención muscular)

✅ OPTIMIZACIÓN DE GRASAS:
   • Tradicional: 39.3% (muy alto para déficit)
   • Nueva lógica: 30.0% (mínimo esencial, libera kcal para carbos)
   • Resultado: -13g grasa, +17.6g carbos (mejor rendimiento)

✅ DÉFICIT INTELIGENTE:
   • Tradicional: 30% sin explicación
   • Nueva lógica: 30% interpolado por categoría BF + guardrails IR-SE
   • Resultado: Mismo déficit pero con justificación científica

✅ CICLAJE ESTRATÉGICO:
   • Tradicional: Macros estáticos
   • Nueva lógica: Manipulación de carbos según día (4-3)
   • Resultado: Mejor adherencia, oxidación de grasa, recuperación

✅ TRANSPARENCIA:
   • Tradicional: "Plan recomendado"
   • Nueva lógica: Categoría BF → Interpolación → Guardrails → Resultado
   • Resultado: Cliente entiende el PORQUÉ de cada número

================================================================================
7️⃣ ¿POR QUÉ NO VES ESTO EN EL EMAIL ACTUAL?
================================================================================

El email que recibiste (2026-01-04 04:38:49) se generó con la app Streamlit
que estaba en memoria ANTES de nuestros pushes.

SOLUCIÓN:
1. Reiniciar aplicación Streamlit completamente
2. Hacer nueva evaluación de Cristina
3. El nuevo email mostrará toda esta información actualizada

COMMITS RELEVANTES:
• 6d1c4a9 (2026-01-03 21:57): Integración nueva lógica en emails
• ccacb0e (2026-01-03 22:53): Bugfixes (TypeError + Gmail MIME)

================================================================================
FIN DEL REPORTE
================================================================================

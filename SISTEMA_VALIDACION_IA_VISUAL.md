# 🤖 SISTEMA DE VALIDACIÓN IA + ANÁLISIS VISUAL

**Objetivo:** Validar coherencia entre datos YAML del email parte 4, fotos visuales, y factores contextuales usando IA.

---

## 📋 FLUJO DEL SISTEMA

```
Usuario completa evaluación MUPAI 2.0
    ↓
Sistema genera YAML completo (email parte 4)
    ↓
Usuario sube FOTOS (4 ángulos: frente, espalda, lado, abdomen)
    ↓
IA ANALIZA:
    1. % Grasa visual vs % grasa OMRON
    2. Coherencia balance energético
    3. Factores contextuales (ciclo menstrual, estrés, sueño)
    4. Coherencia proyecciones vs estado actual
    ↓
REPORTE IA:
    - Validación coherencia (PASS/WARN/FAIL)
    - Ajustes recomendados
    - Alertas contextuales
```

---

## 📦 ESTRUCTURA YAML INPUT PARA IA

### Formato Completo Email Parte 4

```yaml
# ═══════════════════════════════════════════════════════════════
# MUPAI 2.0 - AUDITORÍA COMPLETA PARA VALIDACIÓN IA
# ═══════════════════════════════════════════════════════════════

metadata:
  fecha_evaluacion: "2026-01-03"
  sistema: "MUPAI 2.0"
  version_spec: "11/10"  # "tradicional" o "11/10"
  usuario_id: "CM2026003"

# ───────────────────────────────────────────────────────────────
# 1. DATOS PERSONALES
# ───────────────────────────────────────────────────────────────
persona:
  nombre: "Carlos Méndez"
  edad: 28
  sexo: "hombre"  # "hombre" o "mujer"
  email: "carlos.mendez@email.com"
  telefono: "+52-555-1234"

# ───────────────────────────────────────────────────────────────
# 2. ANTROPOMETRÍA
# ───────────────────────────────────────────────────────────────
antropometria:
  peso_kg: 78.0
  altura_cm: 175.0
  imc: 25.5
  circunferencia_cintura_cm: 82.0
  wthr: 0.469
  wthr_clasificacion: "Bajo riesgo cardiometabólico"

# ───────────────────────────────────────────────────────────────
# 3. COMPOSICIÓN CORPORAL
# ───────────────────────────────────────────────────────────────
composicion:
  metodo_medicion: "OMRON BF511"
  grasa_pct: 18.0
  grasa_pct_modo: "GREEN"  # GREEN/AMBER/RED
  mlg_kg: 64.0
  grasa_visceral_nivel: 4
  grasa_visceral_clasificacion: "Normal"
  
  # FFMI
  ffmi:
    valor: 20.9
    clasificacion: "BUENO"
    modo: "GREEN"
    potencial_pct: 75
    ffmi_max_genetico: 25.2
    interpretacion: "Buen desarrollo muscular. Puedes seguir mejorando."

# ───────────────────────────────────────────────────────────────
# 4. NIVEL DE ACTIVIDAD Y ENTRENAMIENTO
# ───────────────────────────────────────────────────────────────
actividad:
  pal_categoria: "Moderadamente Activo"
  pal_factor: 1.55
  geaf: 1.55
  
  experiencia:
    anos_entrenamiento: "3-4 años"
    nivel_mupai: "INTERMEDIO"
    puntaje_total: 75
    
  capacidad_funcional:
    sentadilla_kg: 117
    sentadilla_ratio: 1.5
    press_banca_kg: 78
    press_banca_ratio: 1.0
    peso_muerto_kg: 136.5
    peso_muerto_ratio: 1.75
    dominadas_reps: 10
    
  frecuencia_semanal: 5
  gee_promedio_dia: 285

# ───────────────────────────────────────────────────────────────
# 5. GASTO ENERGÉTICO
# ───────────────────────────────────────────────────────────────
gasto_energetico:
  tmb:
    ecuacion: "Cunningham"
    valor_kcal: 1847
    base_mlg_kg: 64.0
  
  geaf_factor: 1.55
  gee_kcal_dia: 285
  eta_factor: 1.10
  eta_criterio: "ETA estándar (grasa 18%, hombre)"
  
  ge_total_kcal: 3437
  calculo: "(TMB × GEAF × ETA) + GEE = (1847 × 1.55 × 1.10) + 285"

# ───────────────────────────────────────────────────────────────
# 6. OBJETIVO Y FASE NUTRICIONAL
# ───────────────────────────────────────────────────────────────
objetivo:
  tipo: "CUT"  # CUT/BULK/MANTENIMIENTO/PSMF
  descripcion: "Definición / Pérdida de grasa"
  
  fase_nutricional:
    nombre: "DÉFICIT MODERADO"
    fbeo: 0.85
    deficit_pct: 15.0
    metodo: "Murphy 2021 interpolación"  # si SPEC 11/10
    evidencia: "Murphy 2021 (n=1,474)"
    racional: "18% grasa → déficit 15% óptimo (preservar masa)"
  
  calorias:
    ge_total: 3437
    ingesta_objetivo: 2921
    deficit_semanal_kcal: 3612
    perdida_estimada_kg_sem: 0.45

# ───────────────────────────────────────────────────────────────
# 7. PLAN NUTRICIONAL
# ───────────────────────────────────────────────────────────────
plan_nutricional:
  tipo: "TRADICIONAL"  # TRADICIONAL/PSMF
  spec_11_activo: true
  
  macros:
    proteina:
      gramos: 160.0
      kcal: 640
      pct_total: 21.9
      ratio: "2.5 g/kg MLG"
      metodo: "PBM Tagawa 2021"
      evidencia: "Tagawa 2021 (n=2,214, BJSM IF 18.4)"
      racional: "Proteína elevada preserva masa en déficit"
    
    grasas:
      gramos: 61.6
      kcal: 554
      pct_total: 19.0
      config: "30% TMB"
      metodo: "Cochrane 2020"
      evidencia: "Cochrane Review 2020 (n=71,790)"
      rango_optimo: "20-35%"
      racional: "Balance hormonal óptimo"
    
    carbohidratos:
      gramos: 431.8
      kcal: 1727
      pct_total: 59.1
      ratio: "5.5 g/kg peso"
      minimo_burke: "3-5 g/kg (intermedio)"
      cumple_burke: true
      evidencia: "Burke 2011 (IOC Chair, h-index 110)"
      racional: "Combustible entrenamiento calidad"
  
  ciclaje_4_3:
    activo: true
    evidencia: "Peos 2019 (n=479)"
    dias_low: 4
    carbos_low_g: 367
    carbos_low_pct: 85
    dias_high: 3
    carbos_high_g: 432
    carbos_high_pct: 100
    ventaja: "Mejor adherencia, misma pérdida grasa"

# ───────────────────────────────────────────────────────────────
# 8. PROYECCIÓN 6 SEMANAS
# ───────────────────────────────────────────────────────────────
proyeccion:
  metodo: "Murphy 2021 + Slater 2024"  # si SPEC 11/10
  
  semanal:
    perdida_pct_min: -0.50
    perdida_pct_max: -0.75
    perdida_kg_min: -0.39
    perdida_kg_max: -0.58
    velocidad: "MODERADA"
  
  total_6_semanas:
    peso_inicial: 78.0
    peso_final_min: 76.7
    peso_final_max: 75.5
    perdida_total_min: -1.3
    perdida_total_max: -2.5
    grasa_pura_min_kg: 1.8
    grasa_pura_max_kg: 2.7
  
  escenarios:
    conservador:
      perdida_sem: -0.39
      semana_1: 77.6
      semana_3: 76.8
      semana_6: 76.7
    
    agresivo:
      perdida_sem: -0.58
      semana_1: 77.4
      semana_3: 76.2
      semana_6: 75.5
  
  interpretacion_murphy:
    - "Pérdida principalmente grasa (85-90%)"
    - "Preservación masa muscular (proteína alta PBM)"
    - "Sostenibilidad alta (adherencia 6-8 semanas)"
    - "Recomposición posible (intermedio + déficit moderado)"

# ───────────────────────────────────────────────────────────────
# 9. FACTORES CONTEXTUALES (CRÍTICO PARA IA)
# ───────────────────────────────────────────────────────────────
contexto:
  
  # MUJERES: Ciclo menstrual
  ciclo_menstrual:
    aplica: false  # true si mujer
    fase_actual: null  # "folicular"/"ovulatoria"/"lutea"/"menstrual"
    dias_desde_inicio: null
    sintomas_spm: []
    retencion_esperada_kg: null
    ajuste_deficit_recomendado: null
  
  # Estrés y cortisol
  estres:
    nivel: "MODERADO"  # BAJO/MODERADO/ALTO
    fuentes: ["trabajo", "estudios"]
    puntaje: 5  # 0-10
    impacto_deficit: "MEDIO"  # BAJO/MEDIO/ALTO
    recomendacion: "Monitorear adherencia, considerar semana descanso cada 6-8 sem"
  
  # Calidad de sueño
  sueno:
    horas_promedio: 7.0
    calidad: "BUENA"  # MALA/REGULAR/BUENA/EXCELENTE
    problemas: []  # ["insomnio", "despertares", "apnea"]
    impacto_recuperacion: "BAJO"
    recomendacion: "Mantener rutina consistente"
  
  # Adherencia nutricional
  adherencia:
    historico_dietas_previas: 2
    exito_previo: true
    tiempo_max_adherencia_meses: 4
    factores_abandono: ["eventos sociales", "estrés laboral"]
    prediccion_adherencia: "ALTA"
  
  # Medicamentos/suplementos
  medicamentos:
    - nombre: "Ninguno"
      tipo: null
      impacto_metabolico: null
  
  suplementos:
    - "Proteína whey"
    - "Creatina 5g/día"
    - "Vitamina D"
    - "Omega-3"
  
  # Restricciones/preferencias
  restricciones:
    alergias: []
    intolerancias: []
    preferencias: ["evita lácteos AM"]
    estilo_alimentacion: "flexible"  # flexible/vegetariano/vegano/keto/etc

# ───────────────────────────────────────────────────────────────
# 10. IR-SE (Indicador Riesgo - Situación Energética)
# ───────────────────────────────────────────────────────────────
ir_se:
  valor: 1.47
  zona: "VERDE"  # VERDE/AMARILLA/ROJA
  clasificacion: "Equilibrio saludable"
  guardrails_muller_2016:
    activo: true
    umbral_amarillo: 1.35
    umbral_rojo: 1.20
    alerta: null
    recomendacion: "Mantener monitoreo. Sin restricciones adicionales."

# ───────────────────────────────────────────────────────────────
# 11. FOTOS PARA ANÁLISIS VISUAL (PATHS)
# ───────────────────────────────────────────────────────────────
fotos:
  fecha_captura: "2026-01-03"
  condiciones:
    iluminacion: "natural indirecta"
    hora: "08:00 AM"
    estado: "ayunas"
    hidratacion: "normal"
  
  paths:
    frente: "uploads/CM2026003_frente.jpg"
    espalda: "uploads/CM2026003_espalda.jpg"
    lado: "uploads/CM2026003_lado.jpg"
    abdomen: "uploads/CM2026003_abdomen.jpg"
  
  # Metadatos para IA
  metadata_visual:
    postura: "erecta"
    tension_muscular: "relajada"
    iluminacion_calidad: "buena"
    resolucion_min_px: 1920

# ───────────────────────────────────────────────────────────────
# 12. HISTORIAL (si existe)
# ───────────────────────────────────────────────────────────────
historial:
  evaluaciones_previas: 0
  ultima_evaluacion: null
  
  progreso:
    peso_cambio_6sem: null
    grasa_cambio_6sem: null
    adherencia_real_pct: null
    desviacion_proyeccion: null

# ═══════════════════════════════════════════════════════════════
# VALIDACIONES REQUERIDAS (PARA IA)
# ═══════════════════════════════════════════════════════════════
validaciones_ia:
  - tipo: "coherencia_grasa_visual_vs_omron"
    descripcion: "Comparar % grasa OMRON (18%) con análisis visual fotos"
    tolerancia_pct: 3.0
    
  - tipo: "coherencia_balance_energetico"
    descripcion: "Validar que GE total (3437 kcal) sea coherente con nivel actividad y composición"
    rango_esperado_kcal: [3200, 3600]
    
  - tipo: "coherencia_proyeccion"
    descripcion: "Validar que proyección (-0.39 a -0.58 kg/sem) sea realista para déficit 15% y nivel intermedio"
    referencia: "Murphy 2021 + Slater 2024"
    
  - tipo: "factores_contextuales"
    descripcion: "Evaluar impacto estrés (MODERADO) y sueño (7h BUENA) en adherencia proyectada"
    ajuste_recomendado: true
    
  - tipo: "coherencia_macros"
    descripcion: "Validar que macros SPEC 11/10 sean apropiados para objetivo CUT nivel intermedio"
    checks:
      - proteina_suficiente: "≥2.2 g/kg MLG"
      - grasas_optimas: "20-35% TEI"
      - carbos_minimos: "≥3 g/kg nivel intermedio"
```

---

## 🤖 PROMPT PARA IA (GPT-4 Vision / Claude Sonnet 3.5)

### Prompt Maestro Validación

```markdown
# ROL: Experto en Evaluación de Composición Corporal y Nutrición Deportiva

Eres un evaluador científico especializado en:
- Análisis visual de composición corporal
- Validación de balance energético
- Contextualización de factores fisiológicos (ciclo menstrual, estrés, sueño)
- Interpretación de protocolos científicos (Murphy 2021, Tagawa 2021, Slater 2024, etc.)

## TAREA

Analiza el YAML de evaluación MUPAI 2.0 y las 4 fotos adjuntas del usuario, luego:

1. **VALIDACIÓN % GRASA VISUAL:**
   - Estima % grasa corporal por análisis visual (4 fotos: frente, espalda, lado, abdomen)
   - Compara con % grasa OMRON reportado
   - Identifica coherencia o discrepancias
   - Tolerancia: ±3%

2. **VALIDACIÓN BALANCE ENERGÉTICO:**
   - Revisa GE total calculado (TMB × GEAF × ETA + GEE)
   - Valida coherencia con:
     * Nivel actividad reportado
     * Composición corporal (MLG, % grasa)
     * Experiencia entrenamiento
   - Detecta sobreestimaciones o subestimaciones

3. **ANÁLISIS FACTORES CONTEXTUALES:**
   - **Ciclo menstrual** (si mujer):
     * Fase actual y su impacto en retención líquidos
     * Ajustes recomendados para proyecciones
   - **Estrés:**
     * Nivel actual y su impacto en cortisol
     * Riesgo de adherencia reducida
   - **Sueño:**
     * Calidad y su impacto en recuperación
     * Riesgo de estancamiento si deficiente

4. **VALIDACIÓN PROYECCIONES:**
   - Revisa proyección 6 semanas
   - Valida coherencia con:
     * % grasa actual
     * Nivel entrenamiento
     * Déficit/surplus aplicado
     * Evidencia científica (Murphy 2021, Slater 2024)

5. **COHERENCIA MACROS:**
   - Valida proteína (PBM Tagawa 2021)
   - Valida grasas (Cochrane 2020)
   - Valida carbohidratos (Burke 2011)
   - Detecta desbalances

## INPUT

### YAML Completo
[PEGAR YAML AQUÍ]

### Fotos (4)
- Foto 1: Frente (postura erecta, brazos a los lados)
- Foto 2: Espalda (postura erecta, brazos a los lados)
- Foto 3: Lateral (postura erecta, brazos a los lados)
- Foto 4: Abdomen (acercamiento para definición)

**Condiciones fotos:** Iluminación natural indirecta, 08:00 AM, ayunas, hidratación normal

## OUTPUT REQUERIDO

Genera un reporte estructurado en este formato:

---

# 🤖 REPORTE VALIDACIÓN IA - MUPAI 2.0

**Usuario:** [nombre]  
**Fecha:** [fecha]  
**Evaluación ID:** [id]  
**SPEC 11/10:** [activo/desactivado]

---

## 1️⃣ VALIDACIÓN % GRASA VISUAL

### Análisis Visual (4 fotos)
**% Grasa Estimado Visual:** XX.X%  
**% Grasa OMRON Reportado:** XX.X%  
**Diferencia:** ±X.X%  
**Estado:** ✅ COHERENTE / ⚠️ DISCREPANCIA MENOR / ❌ DISCREPANCIA MAYOR

**Observaciones:**
- [Descripción visual: definición muscular, vascularización, acumulación grasa]
- [Áreas clave: abdomen, oblicuos, espalda baja, cuádriceps]
- [Comparación con referencias Jackson-Pollock visual]

**Conclusión:**
[COHERENTE: Las fotos validan el % grasa OMRON ±2%]
[DISCREPANCIA: Fotos sugieren X% pero OMRON reporta Y%, posible error medición]

---

## 2️⃣ VALIDACIÓN BALANCE ENERGÉTICO

### GE Total Calculado
**Valor:** X,XXX kcal/día  
**Fórmula:** (TMB × GEAF × ETA) + GEE  
**Estado:** ✅ COHERENTE / ⚠️ REVISAR / ❌ INCOHERENTE

**Análisis por Componente:**

**TMB (Cunningham):** X,XXX kcal
- Base MLG: XX kg
- Validación: [coherente con % grasa visual]

**GEAF (Factor Actividad):** X.XX
- Nivel reportado: [Moderadamente Activo]
- Coherencia con lifestyle: [COHERENTE / SOBREESTIMADO / SUBESTIMADO]

**GEE (Ejercicio):** XXX kcal/día
- Frecuencia: X días/sem
- Intensidad: [Moderada-Alta]
- Coherencia: [COHERENTE / SOBREESTIMADO / SUBESTIMADO]

**ETA (Efecto Térmico):** X.XX
- Criterio usado: [correcto para % grasa y sexo]

**Conclusión:**
[GE total coherente con composición corporal y nivel actividad]
[AJUSTE RECOMENDADO: +/- XXX kcal por [razón]]

---

## 3️⃣ ANÁLISIS FACTORES CONTEXTUALES

### A) Ciclo Menstrual (si aplica)
**Fase Actual:** [Folicular/Ovulatoria/Lútea/Menstrual]  
**Días desde inicio:** XX  
**Impacto Proyectado:**
- Retención líquidos: +X.X kg esperado
- Ajuste pesaje: Promediar últimos 7 días
- Déficit aparente: Puede variar ±X% por fase

**Recomendación:**
- [No hacer ajustes drásticos durante fase lútea/menstrual]
- [Monitorear tendencia mensual, no semanal]

### B) Estrés
**Nivel:** [BAJO/MODERADO/ALTO]  
**Fuentes:** [trabajo, estudios, etc.]  
**Impacto en Adherencia:** [BAJO/MEDIO/ALTO]  

**Riesgo:**
- Cortisol elevado puede reducir pérdida grasa XX%
- Mayor riesgo atracones si estrés sostenido
- Recuperación comprometida

**Recomendación:**
- [Monitorear adherencia semanalmente]
- [Considerar semana descanso (dieta inversa) cada 6-8 sem]
- [Técnicas manejo estrés: meditación, caminatas]

### C) Sueño
**Horas promedio:** X.X h  
**Calidad:** [MALA/REGULAR/BUENA/EXCELENTE]  
**Impacto en Recuperación:** [BAJO/MEDIO/ALTO]

**Riesgo:**
- Sueño <7h aumenta grelina, reduce leptina
- Recuperación muscular comprometida si <6h
- Mayor riesgo pérdida masa magra en déficit

**Recomendación:**
- [CRÍTICO: Aumentar a 7-8h/noche]
- [Mantener horario consistente]
- [Evitar pantallas 1h antes dormir]

---

## 4️⃣ VALIDACIÓN PROYECCIONES 6 SEMANAS

### Proyección Actual
**Rango Semanal:** -X.XX a -X.XX kg/sem  
**Total 6 semanas:** -X.X a -X.X kg  
**Método:** [Murphy 2021 + Slater 2024 / Tradicional]  
**Estado:** ✅ REALISTA / ⚠️ OPTIMISTA / ❌ IRREALISTA

**Análisis:**
- % Grasa actual (XX%): [Déficit apropiado XX%]
- Nivel entrenamiento: [INTERMEDIO validado por capacidad funcional]
- Déficit aplicado: XX% [CONSERVADOR/MODERADO/AGRESIVO]
- Proteína PBM: XX g/kg MLG [SUFICIENTE para preservar masa]

**Factores Moderadores:**
- Estrés [MODERADO]: Puede reducir velocidad XX%
- Sueño [BUENA]: Sin impacto negativo
- Ciclo menstrual (si aplica): Variabilidad ±X kg por fase

**Proyección Ajustada IA:**
**Conservador:** -X.XX kg/sem → -X.X kg en 6 sem  
**Realista:** -X.XX kg/sem → -X.X kg en 6 sem  
**Óptimo:** -X.XX kg/sem → -X.X kg en 6 sem

**Conclusión:**
[Proyección MUPAI coherente con evidencia Murphy 2021]
[AJUSTE RECOMENDADO: Considerar [razón] → nuevo rango -X.XX a -X.XX kg/sem]

---

## 5️⃣ COHERENCIA MACROS

### Proteína
**Asignada:** XXX g (X.X g/kg MLG)  
**Método:** [PBM Tagawa 2021 / Tradicional]  
**Estado:** ✅ ÓPTIMA / ⚠️ BAJA / ❌ INSUFICIENTE

**Análisis:**
- Objetivo CUT + Nivel INTERMEDIO requiere: ≥2.2 g/kg MLG
- Asignación actual: [CUMPLE / NO CUMPLE]
- Evidencia Tagawa 2021: 2.2-2.7 g/kg MLG óptimo

**Recomendación:**
[Mantener / Aumentar a XXX g para preservación masa]

### Grasas
**Asignadas:** XX g (XX% TMB / XX% TEI)  
**Configuración:** [20%/30%/40% TMB]  
**Estado:** ✅ ÓPTIMA / ⚠️ REVISAR / ❌ FUERA RANGO

**Análisis:**
- Rango Cochrane 2020: 20-35% TEI
- Asignación actual: XX% TEI [DENTRO/FUERA rango]
- Balance hormonal: [ÓPTIMO / COMPROMETIDO]

**Recomendación:**
[Mantener / Ajustar a XX% TMB]

### Carbohidratos
**Asignados:** XXX g (X.X g/kg peso)  
**Mínimo Burke 2011:** X-X g/kg (nivel [intermedio])  
**Estado:** ✅ CUMPLE / ⚠️ JUSTO / ❌ INSUFICIENTE

**Análisis:**
- Burke 2011 recomienda: 3-5 g/kg para nivel intermedio
- Asignación: X.X g/kg [CUMPLE / NO CUMPLE]
- Rendimiento esperado: [ÓPTIMO / COMPROMETIDO]

**Recomendación:**
[Mantener / Aumentar a XXX g si rendimiento baja]

---

## 6️⃣ IR-SE (Müller 2016 Guardrails)

**Valor:** X.XX  
**Zona:** [VERDE/AMARILLA/ROJA]  
**Estado:** ✅ SEGURO / ⚠️ MONITOREAR / ❌ RIESGO

**Interpretación:**
- VERDE (≥1.35): Equilibrio saludable, sin restricciones
- AMARILLA (1.20-1.35): Monitoreo cercano, considerar refeed
- ROJA (<1.20): CRÍTICO - Alto riesgo adaptación metabólica

**Recomendación:**
[Continuar como planeado / Reducir déficit / PAUSA OBLIGATORIA]

---

## ✅ RESUMEN EJECUTIVO

### COHERENCIA GLOBAL: [ALTA/MEDIA/BAJA] - [XX%]

✅ **VALIDACIONES PASADAS:**
- [Componente 1]
- [Componente 2]

⚠️ **ADVERTENCIAS:**
- [Componente 3]
- [Componente 4]

❌ **FALLAS CRÍTICAS:**
- [Si existen]

### AJUSTES RECOMENDADOS:

1. **Calorías:** [Mantener XXX kcal / Ajustar a XXX kcal]
2. **Proteína:** [Mantener XXX g / Aumentar a XXX g]
3. **Grasas:** [Mantener XX g / Ajustar a XX g]
4. **Carbohidratos:** [Mantener XXX g / Ajustar si rendimiento baja]
5. **Proyección:** [Mantener rango / Ajustar a -X.XX a -X.XX kg/sem]

### FACTORES CRÍTICOS MONITOREAR:

1. **[Factor 1]:** [Descripción y frecuencia monitoreo]
2. **[Factor 2]:** [Descripción y frecuencia monitoreo]
3. **[Factor 3]:** [Descripción y frecuencia monitoreo]

### NIVEL CONFIANZA IA: [XX%]

Basado en:
- Calidad fotos: [ALTA/MEDIA/BAJA]
- Coherencia datos: [ALTA/MEDIA/BAJA]
- Contexto completo: [SÍ/PARCIAL/NO]

---

**Generado por:** Sistema Validación IA MUPAI 2.0  
**Fecha análisis:** [timestamp]  
**Modelo:** GPT-4 Vision / Claude Sonnet 3.5  
**Versión:** 1.0

---
```

## SIGUIENTE EVALUACIÓN

**Recomendación:** Re-analizar en 6 semanas con:
- Nuevas fotos (mismo protocolo)
- Peso real vs proyectado
- Adherencia reportada
- Ajustes necesarios

**Objetivo:** Validar precisión proyecciones y ajustar modelo predictivo

---
```

---

## 🛠️ IMPLEMENTACIÓN TÉCNICA

### Opción 1: API OpenAI GPT-4 Vision

```python
import openai
import yaml
import base64

def validar_evaluacion_ia(yaml_path, fotos_paths):
    """
    Valida evaluación MUPAI 2.0 usando GPT-4 Vision
    
    Args:
        yaml_path: Path al archivo YAML completo
        fotos_paths: Dict con paths a 4 fotos {frente, espalda, lado, abdomen}
    
    Returns:
        dict: Reporte validación IA estructurado
    """
    # Cargar YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Codificar fotos en base64
    imagenes_base64 = {}
    for angulo, path in fotos_paths.items():
        with open(path, 'rb') as img:
            imagenes_base64[angulo] = base64.b64encode(img.read()).decode('utf-8')
    
    # Construir prompt
    prompt = f"""
    {PROMPT_MAESTRO_VALIDACION}
    
    ## YAML EVALUACIÓN:
    ```yaml
    {yaml.dump(yaml_data, allow_unicode=True)}
    ```
    """
    
    # Llamada API GPT-4 Vision
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "Eres un experto en composición corporal y nutrición deportiva."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagenes_base64['frente']}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagenes_base64['espalda']}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagenes_base64['lado']}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagenes_base64['abdomen']}"
                        }
                    }
                ]
            }
        ],
        max_tokens=4000,
        temperature=0.3  # Baja temperatura para respuestas consistentes
    )
    
    reporte_ia = response.choices[0].message.content
    
    return {
        "reporte_markdown": reporte_ia,
        "yaml_original": yaml_data,
        "timestamp": datetime.now().isoformat()
    }
```

### Opción 2: API Anthropic Claude 3.5 Sonnet

```python
import anthropic
import yaml
import base64

def validar_evaluacion_claude(yaml_path, fotos_paths):
    """
    Valida evaluación MUPAI 2.0 usando Claude Sonnet 3.5
    """
    client = anthropic.Anthropic(api_key="tu-api-key")
    
    # Cargar YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Codificar fotos
    imagenes_base64 = {}
    for angulo, path in fotos_paths.items():
        with open(path, 'rb') as img:
            imagenes_base64[angulo] = base64.standard_b64encode(img.read()).decode('utf-8')
    
    # Construir mensaje
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.3,
        system="Eres un experto en evaluación de composición corporal y nutrición deportiva científica.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""{PROMPT_MAESTRO_VALIDACION}
                        
                        ## YAML EVALUACIÓN:
                        ```yaml
                        {yaml.dump(yaml_data, allow_unicode=True)}
                        ```
                        """
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": imagenes_base64['frente']
                        }
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": imagenes_base64['espalda']
                        }
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": imagenes_base64['lado']
                        }
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": imagenes_base64['abdomen']
                        }
                    }
                ]
            }
        ]
    )
    
    return {
        "reporte_markdown": message.content[0].text,
        "yaml_original": yaml_data,
        "timestamp": datetime.now().isoformat(),
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens
    }
```

---

## 📊 CASOS DE USO ESPECÍFICOS

### CASO 1: Mujer en Fase Lútea

```yaml
contexto:
  ciclo_menstrual:
    aplica: true
    fase_actual: "lutea"
    dias_desde_inicio: 21
    sintomas_spm: ["hinchazón", "retención_líquidos", "antojos"]
    retencion_esperada_kg: 1.5
    ajuste_deficit_recomendado: "Mantener plan, no hacer ajustes por peso temporal"
```

**Validación IA esperada:**
- ✅ Peso estancado o +1-2 kg es NORMAL en esta fase
- ⚠️ NO ajustar calorías basado en peso esta semana
- ✅ Monitorear tendencia mensual completa (folicular a menstrual)
- ✅ Antojos manejables con ciclaje 4-3 (días HIGH estratégicos)

### CASO 2: Usuario con Estrés Alto

```yaml
contexto:
  estres:
    nivel: "ALTO"
    fuentes: ["trabajo 60h/sem", "estudios masters", "problemas familiares"]
    puntaje: 8
    impacto_deficit: "ALTO"
```

**Validación IA esperada:**
- ⚠️ Cortisol elevado puede reducir pérdida grasa 20-30%
- ⚠️ Mayor riesgo atracones compensatorios
- ❌ CRÍTICO: Déficit agresivo contraindicado
- ✅ Recomendación: Reducir déficit a 10% o considerar mantenimiento 2 semanas

### CASO 3: Discrepancia % Grasa Visual vs OMRON

**OMRON reporta:** 22%  
**IA estima visual:** 16%

**Validación IA:**
- ❌ DISCREPANCIA MAYOR: 6% diferencia (>3% tolerancia)
- Posibles causas:
  1. OMRON descalibrado
  2. Hidratación anormal durante medición
  3. Usuario confundió lecturas (grasa visceral vs % grasa)
- ✅ Recomendación: Repetir medición OMRON + considerar pliegues cutáneos

---

## 🚀 PRÓXIMOS PASOS IMPLEMENTACIÓN

1. **Generar función export YAML** en streamlit_app.py
2. **Crear endpoint API** para recibir YAML + fotos
3. **Integrar llamada IA** (GPT-4 Vision o Claude Sonnet)
4. **Mostrar reporte validación** en UI o email parte 5
5. **Almacenar histórico** para validación longitudinal

¿Quieres que implemente alguna de estas partes primero?

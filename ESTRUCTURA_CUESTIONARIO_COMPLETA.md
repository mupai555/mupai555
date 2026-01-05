# 📋 ESTRUCTURA COMPLETA DEL CUESTIONARIO - MUPAI

## 🎯 FLUJO GENERAL DEL FORMULARIO

```
┌─────────────────────────────────────────────────────────────────┐
│                   INICIO - BIENVENIDA                            │
│              (Validación: Términos + Descargo)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  ¿Datos Personales Completos?      │
         │  (Nombre, Teléfono, Email)         │
         └─────────────────┬──────────────────┘
                           │
        ┌──────────────────┴───────────────────┐
        │  ¿Acepto Términos + Descargo?        │
        │  (Obligatorio: SÍ/NO)                │
        └──────────────────┬───────────────────┘
                           │
                    ✅ DESBLOQUEA PASOS
                           │
         ┌─────────────────┴──────────────────┐
         │   PASO 1: DATOS PERSONALES          │
         │   (📝 Nombre, Edad, Sexo, Email)   │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 2: COMPOSICIÓN CORPORAL       │
         │  (⚖️  Peso, Estatura, % Grasa)     │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 3: SUEÑO + ESTRÉS            │
         │  (🌙 Calidad Sueño, Estrés, IR-SE)│
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 4: EVALUACIÓN FUNCIONAL      │
         │  (💪 Experiencia, Rendimiento)     │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 5: ACTIVIDAD DIARIA          │
         │  (🚶 Nivel de Actividad)           │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 6: ANÁLISIS METABÓLICO       │
         │  (⚡ ETA - Termogénesis)           │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  PASO 7: ENTRENAMIENTO FUERZA      │
         │  (🏋️  GEE - Gasto por Ejercicio)  │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  METAS PERSONALES                  │
         │  (🎯 Objetivos a Mediano/Largo)    │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  FOTOGRAFÍAS DE PROGRESO           │
         │  (📸 Frontal, Lateral, Posterior)  │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │  RESULTADO FINAL                   │
         │  (📈 Plan Nutricional + Emails)    │
         └─────────────────────────────────────┘
```

---

## 📝 DETALLE DE CADA PASO

### PASO 1: DATOS PERSONALES ✓
**Ubicación**: Línea ~7350  
**Estado**: Siempre expandido  
**Validación**: Obligatorio

**Campos:**
```
├─ Nombre (texto)
├─ Teléfono (texto - formato validado)
├─ Email (texto - formato validado)
├─ Edad (número: 15-100)
├─ Sexo (select: Hombre/Mujer)
├─ Aceptar términos MUPAI (checkbox) ✓
└─ Aceptar descargo responsabilidad (checkbox) ✓
```

**Datos guardados**: `st.session_state.nombre`, `.telefono`, `.email_cliente`, `.sexo`, `.edad`  
**Validación**: Todas obligatorias. Desbloquea paso 2 solo si están completas.

---

### PASO 2: COMPOSICIÓN CORPORAL ✓
**Ubicación**: Línea ~7713  
**Estado**: Expandido después de Paso 1  
**Validación**: Obligatorio

**Campos:**
```
├─ Peso corporal (kg) - Rango: 30-200
├─ Estatura (cm) - Rango: 120-220
│
├─ MÉTODO 1: Grasa por Porcentaje (simple)
│  └─ % Grasa corporal - Rango: 2-90%
│     (Validación automática según sexo)
│
├─ MÉTODO 2: Grasa por Medidas (DEXA/BIA)
│  ├─ Masa Libre de Grasa - MLG (kg)
│  └─ Porcentaje Grasa calculado
│
└─ MÉTODO 3: Conversión de Equipos
   ├─ Equipo BIA (Omron, InBody, etc)
   │  └─ Valor directo → convierte a %
   └─ Otra medida
      └─ Ingresa manualmente

** CÁLCULOS DERIVADOS (automáticos):
├─ IMC (Índice Masa Corporal)
├─ MLG (Masa Libre Grasa) - si no se ingresa
├─ Grasa corporal % - si no se ingresa
├─ BF Corregido (ajuste por validez)
├─ BF Operacional (para decisiones)
└─ Categoría BF (5 niveles: prep, atlético, saludable, sobrepeso, obesidad)
```

**Datos guardados**: 
- `st.session_state.peso`
- `st.session_state.estatura`
- `st.session_state.grasa` (%)
- `st.session_state.mlg` (si se calcula)
- `st.session_state.metodo_grasa` (cuál se usó)

**Validación**:
- Peso: 30-200 kg
- Estatura: 120-220 cm
- Grasa%: 2-90% (validación según sexo)
- MLG > 0 si se ingresa
- Consistencia: grasa% + mlg debe coincidir con peso

---

### PASO 3: SUEÑO + ESTRÉS ✓
**Ubicación**: Línea ~8256  
**Estado**: Expandido después de Paso 2  
**Validación**: Obligatorio

**Sección A: Calidad del Sueño 🌙**
```
├─ Horas de sueño promedio
│  └─ Rango: 3-12 horas (o "sin dato")
│
├─ Consistencia de horarios
│  └─ Escala: 1-5 (muy irregular a muy regular)
│
└─ Calidad general sueño
   └─ Escala: 1-5 (muy mala a excelente)
```

**Sección B: Nivel de Estrés 🧠**
```
├─ Estrés percibido
│  └─ Escala: 1-5 (nulo a muy alto)
│
├─ Nivel de ansiedad
│  └─ Escala: 1-5 (sin ansiedad a ansiedad severa)
│
└─ Presión laboral/académica
   └─ Escala: 1-5 (muy baja a muy alta)
```

**Cálculo Automático: IR-SE**
```
IR-SE = (Sueño + Regularidad + Estrés percibido + Ansiedad) / Presión_laboral
Rango: 0-100
├─ <30: Recuperación muy baja ⚠️
├─ 30-50: Recuperación baja
├─ 50-70: Recuperación media
└─ >70: Recuperación buena ✓
```

**Datos guardados**: `st.session_state.suenyo_estres_data`  
**Impacto**: Modifica guardrails de déficit calórico

---

### PASO 4: EVALUACIÓN FUNCIONAL 💪
**Ubicación**: Línea ~8273  
**Estado**: Expandido  
**Validación**: Obligatorio

**Sección A: Experiencia de Entrenamiento**
```
├─ ¿Cuántos años llevas entrenando?
│  └─ Opciones: 0-1, 1-2, 2-5, 5-10, >10 años
│
├─ ¿Actualmente sigues rutina estructurada?
│  └─ Sí/No
│
└─ Frecuencia de entrenamiento
   └─ Opciones: <1x/sem, 2-3x/sem, 4-5x/sem, 6+x/sem
```

**Sección B: Rendimiento Funcional (1RM o máximo)**
```
├─ Sentadilla (kg)
├─ Press Banca (kg)
├─ Peso Muerto (kg)
├─ Flex Brazo (kg)
├─ Prensa de Piernas (kg)
├─ Press Militar (kg)
└─ Dominadas (repeticiones máx)
```

**Cálculo Derivado**:
```
├─ Wilks Score (total pound effort)
├─ Relative Strength (kg / peso corporal)
├─ Category: Novice / Intermediate / Advanced / Elite
└─ Recomendaciones según nivel
```

**Datos guardados**: `st.session_state.nivel_entrena`, `.rendimiento_funcional`

---

### PASO 5: ACTIVIDAD FÍSICA DIARIA 🚶
**Ubicación**: Línea ~8904  
**Estado**: Expandido  
**Validación**: Obligatorio

**Selección de Nivel** (Mutuamente excluyentes):
```
1. Sedentario
   └─ Trabajo de oficina, <5,000 pasos/día
   └─ GEAF: 1.4

2. Moderadamente-activo
   └─ Trabajo mixto, 5,000-10,000 pasos/día
   └─ GEAF: 1.55

3. Activo
   └─ Trabajo físico, 10,000-12,500 pasos/día
   └─ GEAF: 1.65

4. Muy-activo
   └─ Trabajo muy físico, >12,500 pasos/día
   └─ GEAF: 1.8
```

**Impacto**: Modifica GEAF (Gasto Energético Asociado a Actividad)

**Datos guardados**: `st.session_state.nivel_actividad`

---

### PASO 6: ANÁLISIS METABÓLICO ⚡
**Ubicación**: Línea ~9021  
**Estado**: Expandido o Automático  
**Validación**: AUTO-CALCULADO

**Cálculos Internos** (sin entrada de usuario):
```
├─ TMB (Tasa Metabólica Basal)
│  └─ Fórmula: 500 + (22 × MLG) [Cunningham corregido]
│
├─ ETA (Efecto Térmico de Alimentos)
│  └─ Rango: 0.5-1.5 (según composición)
│  └─ Cálculo: 10% aprox de ingesta
│
├─ GEAF (Gasto por Actividad Diaria)
│  └─ De Paso 5 (1.4 a 1.8)
│
├─ GEE (Gasto Energético del Ejercicio)
│  └─ De Paso 7 (cuánto gasta por entrenar)
│
└─ GE TOTAL (Gasto Energético Total)
   └─ GE = (TMB × GEAF) + (GEE × ETA)
```

**Datos guardados**: Calculados automáticamente, mostrados en emails

---

### PASO 7: ENTRENAMIENTO FUERZA 🏋️
**Ubicación**: Línea ~9065  
**Estado**: Expandido  
**Validación**: Obligatorio

**Frecuencia de Entrenamiento**
```
├─ Días por semana de fuerza (entrenamiento)
│  └─ Rango: 0-7 días
│
└─ Duración promedio por sesión
   └─ Rango: 30 min - 3 horas
```

**Cálculo Derivado: GEE**
```
GEE = (Duración × Intensidad × Factor_Corporal)

donde:
├─ Duración: minutos de entrenamiento/día
├─ Intensidad: High (6 kcal/min), Medium (4 kcal/min), Low (2.5 kcal/min)
└─ Factor_Corporal: Ajustado por peso y composición
```

**Impacto**: Aumenta gasto energético total (GE)

**Datos guardados**: `st.session_state.dias_entrenamiento`, `.gee_prom_dia`

---

### METAS PERSONALES 🎯
**Ubicación**: Línea ~6472 (antes de fotos)  
**Estado**: Expandido  
**Validación**: Obligatorio (mínimo 50 caracteres)

**Campo Único**:
```
Texto libre (500 caracteres máx)
└─ Describe tus metas personales:
   ├─ Objetivos de composición corporal
   ├─ Objetivos de rendimiento
   ├─ Objetivos de salud/bienestar
   ├─ Consideraciones personales
   └─ Cualquier otra información relevante
```

**Datos guardados**: `st.session_state.metas_personales`  
**Incluido en**: EMAIL 1, EMAIL 4 (sección "Metas del Cliente")

---

### FOTOGRAFÍAS DE PROGRESO 📸
**Ubicación**: Línea ~7167  
**Estado**: Expandido  
**Validación**: Obligatorio (3 fotos mínimo)

**Fotos Requeridas** (OBLIGATORIAS):
```
1. Frontal - Relajado
   └─ Pose: De frente, brazos al costado
   └─ Formato: PNG/JPG, <15 MB

2. Lateral Derecho - Relajado
   └─ Pose: Perfil derecho, brazos al costado
   └─ Formato: PNG/JPG, <15 MB

3. Posterior - Relajado
   └─ Pose: De espaldas, brazos al costado
   └─ Formato: PNG/JPG, <15 MB
```

**Fotos Opcionales** (extra):
```
4. Pose Libre
   └─ La que quieras (con pose, flexión, etc)
   └─ Formato: PNG/JPG, <15 MB
```

**Validación**:
- Mínimo 3 obligatorias (frontal, lateral, posterior)
- Máximo 15 MB por archivo
- Solo PNG/JPG
- Se adjuntan al reporte (hasta 15 MB total)

**Datos guardados**: `st.session_state.progress_photos_data` (diccionario con keys: "front_relaxed", "side_relaxed_right", "back_relaxed", "pose_libre")

---

### RESULTADO FINAL 📈
**Ubicación**: Línea ~9145  
**Estado**: Expandido (auto-collapse si hay errores)  
**Validación**: Todos pasos deben estar completos

**Salida**:
```
DIAGNÓSTICO VISUAL:
├─ Categoría BF (5 niveles)
├─ Recomendaciones de fase (cut, maintenance, bulk, psmf)
├─ Índices de rendimiento (Wilks, FFMI, etc)
└─ Advertencias de salud

PLAN NUTRICIONAL:
├─ Gasto energético completo (TMB, GEAF, GEE, ETA)
├─ Ingesta calórica recomendada
├─ Macros (Proteína, Grasa, Carbos)
├─ Distribución de comidas
└─ Consideraciones especiales

PROYECCIÓN A 6 SEMANAS:
├─ Rango de pérdida/ganancia esperada
├─ Cambios estimados en composición
└─ Benchmark con objetivos

EMAILS GENERADOS:
├─ EMAIL 1: Análisis detallado + recomendaciones
├─ EMAIL 2: Nutrición específica
├─ EMAIL 3: Entrenamiento (si aplica)
├─ EMAIL 4: Plan completo + fotos
└─ Adjuntos: Progress photos compiladas
```

---

## 🔄 FLUJO DE DATOS

```
PASO 1 (Personales)
    ↓ (Nombre, Edad, Sexo, Email)
    ↓
PASO 2 (Composición)
    ↓ (Peso, Est, %Grasa, MLG)
    ↓ → TMB = 500 + 22×MLG
    ↓
PASO 3 (Sueño/Estrés)
    ↓ (Horas_sleep, Estrés, IR-SE)
    ↓ → Guardrails deficit
    ↓
PASO 4 (Funcional)
    ↓ (Experiencia, 1RM)
    ↓ → Wilks Score, Categoría
    ↓
PASO 5 (Actividad)
    ↓ (Nivel_actividad)
    ↓ → GEAF = 1.4-1.8
    ↓
PASO 6 (Metabólico - AUTO)
    ↓ → GE = (TMB × GEAF) + (GEE × ETA)
    ↓
PASO 7 (Entrenamiento)
    ↓ (Días, Duración)
    ↓ → GEE kcal
    ↓
METAS PERSONALES
    ↓ (Texto libre)
    ↓ → Incluir en emails
    ↓
FOTOS PROGRESO
    ↓ (3 obligatorias + 1 opcional)
    ↓ → Compilar en archivo
    ↓
CÁLCULOS FINALES
    ├─ Ingesta = GE × (1 - deficit%)
    ├─ Macros = calcular_macros_tradicional()
    ├─ PSMF (si aplica)
    └─ Proyección 6 semanas
    ↓
GENERAR EMAILS
    ├─ EMAIL 1: Reporte ejecutivo
    ├─ EMAIL 2-4: Detalles nutricionales
    └─ Adjuntos: Fotos compiladas
```

---

## 📊 VALIDACIONES POR PASO

| Paso | Campo | Validación | Error |
|------|-------|-----------|-------|
| 1 | Nombre | No vacío | "Campo requerido" |
| 1 | Email | Formato válido | "Email inválido" |
| 1 | Teléfono | Formato válido | "Formato incorrecto" |
| 1 | Edad | 15-100 | "Edad fuera de rango" |
| 2 | Peso | 30-200 kg | "Peso inválido" |
| 2 | Estatura | 120-220 cm | "Estatura inválida" |
| 2 | Grasa% | 2-90% | "Grasa% fuera de rango" |
| 2 | Consistencia | Peso ≈ MLG + (Peso × Grasa%) | "No coinciden" |
| 3 | Horas sueño | 3-12 o "sin dato" | "Rango inválido" |
| 4 | 1RM | >0 o 0 si no aplica | "Valor debe ser ≥0" |
| 5 | Actividad | Una opción | "Selecciona una" |
| 7 | Días entrena | 0-7 | "0-7 días" |
| Metas | Texto | 50-500 chars | "Mínimo 50 caracteres" |
| Fotos | Frontal | OBLIGATORIA | "Foto requerida" |
| Fotos | Lateral | OBLIGATORIA | "Foto requerida" |
| Fotos | Posterior | OBLIGATORIA | "Foto requerida" |

---

## 🎯 RESUMEN VISUAL

```
         ENTRADA                    PROCESAMIENTO              SALIDA
    ┌──────────────┐           ┌─────────────────┐       ┌──────────────┐
    │ 7 Pasos +    │           │ Cálculos Auto   │       │ 4 Emails +   │
    │ 2 Extras     │ ──────►   │ Validaciones    │ ──►   │ Fotos + Plan │
    │ (10 secciones)           │ Guardrails      │       │ Nutricional  │
    └──────────────┘           └─────────────────┘       └──────────────┘

    PASOS:                      CÁLCULOS:                 OUTPUTS:
    ├─ Personales              ├─ TMB                    ├─ Reporte ejecutivo
    ├─ Composición             ├─ GE total               ├─ Ingesta calórica
    ├─ Sueño/Estrés            ├─ Macros                 ├─ Macros desglosadas
    ├─ Funcional               ├─ Proyección             ├─ Fotos compiladas
    ├─ Actividad               ├─ Categorías             ├─ Recomendaciones
    ├─ Metabólico (AUTO)       ├─ Wilks Score            ├─ Advertencias
    ├─ Entrenamiento           └─ Deficits               └─ Plan de acción
    ├─ Metas                                        
    ├─ Fotos                                        
    └─ Resultado Final                              
```

---

## ✅ CHECKLIST DE COMPLETITUD

Para generar reporte final, se requiere:

- [ ] Paso 1: Todos datos personales + términos
- [ ] Paso 2: Peso + Estatura + Grasa%
- [ ] Paso 3: Sueño y Estrés (ambos)
- [ ] Paso 4: Experiencia funcional (puede ser 0 en 1RM)
- [ ] Paso 5: Nivel de actividad (obligatorio)
- [ ] Paso 6: Auto-calculado ✓
- [ ] Paso 7: Días entrenamiento (puede ser 0)
- [ ] Metas: Texto mínimo 50 chars
- [ ] Fotos: 3 obligatorias (frontal, lateral, posterior)

**Cuando TODO está completo → Botón "GENERAR REPORTE" se activa → Envía 4 emails**

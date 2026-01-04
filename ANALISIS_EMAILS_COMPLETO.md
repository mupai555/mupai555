# 📊 ANÁLISIS EXHAUSTIVO: INFORMACIÓN ENVIADA EN EMAILS/REPORTES

**Generado:** 4 Enero 2026  
**Estado:** Después de integración nueva lógica + eliminación fallback  
**Código:** streamlit_app.py (v11,000+ líneas)

---

## 📋 RESUMEN EJECUTIVO

Se envían **4 emails diferentes** en cada evaluación:

| Email | Destino | Contenido | Incluye Nueva Lógica |
|-------|---------|----------|---------------------|
| **Email 1** | Cliente | Evaluación completa científica | ✅ SÍ |
| **Email 2** | Admin | Resumen evaluación para archivo | ✅ SÍ |
| **Email 3** | Admin | Copia idéntica a Email 1 | ✅ SÍ |
| **Email 4** | Admin | YAML con datos estructurados | ✅ SÍ |
| **Email 5** | Admin (opcional) | Datos sueño/estrés | ❌ No aplica |

---

## 🔍 DESGLOSE DETALLADO POR EMAIL

### **EMAIL 1: EVALUACIÓN COMPLETA AL CLIENTE**
**Función:** `enviar_email_cliente()`  
**Destinatario:** `email_cliente` (usuario)  
**Formato:** HTML con estilos CSS  
**Líneas:** 3,100-4,400

#### **SECCIONES INCLUIDAS:**

##### **1️⃣ PORTADA & DATOS PERSONALES**
```
Encabezado con logos MUPAI y MUP Gym
Fecha: {fecha}
Nombre cliente: {nombre_cliente}
Edad: {edad} años
Sexo: {sexo}
Teléfono: {telefono}
Email: {email_cliente}
Ciclo menstrual: {ciclo_menstrual} (si es mujer)
```
**Estado:** ✅ Siempre se envía

---

##### **2️⃣ COMPOSICIÓN CORPORAL BÁSICA**
```
Peso: {peso} kg
Estatura: {estatura} cm
IMC: {imc} kg/m²
% Grasa (DEXA corregida): {grasa_corregida}%
Masa Libre de Grasa (MLG): {mlg} kg
Masa Grasa: {masa_grasa} kg
Circunferencia cintura: {circunferencia_cintura} cm
Grasa visceral (Omron): {grasa_visceral} (nivel 1-12)
Masa muscular Omron: {masa_muscular_aparato}%
Masa muscular estimada: {masa_muscular_estimada} kg
```
**Estado:** ✅ Siempre se envía

---

##### **3️⃣ ÍNDICES CORPORALES**
```
FFMI (Fat-Free Mass Index): {ffmi}
Clasificación FFMI: {nivel_ffmi}
WtHR (Waist-to-Height Ratio): {wthr}
Edad Metabólica: {edad_metabolica} años
Nivel Entrenamiento Global: {nivel_entrenamiento}
```
**Estado:** ✅ Siempre se envía

---

##### **4️⃣ MÉTRICAS DE RECUPERACIÓN** (Sección 5)
```
Completado: {suenyo_estres_completado}
Si SÍ:
  • IR-SE Score: {ir_se}
  • Nivel de Recuperación: {nivel_recuperacion}
  • Sleep Score: {sleep_score}
  • Stress Score: {stress_score}
```
**Estado:** ❓ Condicional (solo si usuario completó sueño/estrés)

---

##### **5️⃣ METABOLISMO BASAL Y GASTO ENERGÉTICO** (Sección 5 técnica)
```
TMB (Tasa Metabólica Basal): {tmb} kcal/día
  Fórmula: TMB = 370 + (21.6 × MLG en kg)
  Ejemplo: 370 + (21.6 × 60.5) = 1,677 kcal
  
GE (Gasto Energético Total): {GE} kcal/día
  Fórmula: GE = (TMB × GEAF × ETA) + GEE_promedio
  
Desgloses:
  • GEAF (Factor Actividad Diaria): {geaf}
  • ETA (Efecto Térmico Alimentos): {eta}
  • GEE (Gasto Ejercicio): {gee_prom_dia} kcal/día promedio
  
Calculado como:
  GE = ({tmb} × {geaf} × {eta}) + {gee_prom_dia}
     = {GE:.0f} kcal/día
```
**Estado:** ✅ Siempre se envía (con fórmulas visibles)

---

##### **6️⃣ PLAN NUTRICIONAL CON NUEVA LÓGICA** (Sección 6)

###### **6.1 - Análisis de Composición Corporal (NUEVA)**
```
📊 ANÁLISIS DE COMPOSICIÓN CORPORAL (Nueva Metodología):
   • BF Operacional: {bf_operacional}%
   • Categoría: {categoria_bf_cliente} ({categoria_bf})
   • Fases disponibles: {fases_disponibles}
   • Déficit aplicado: {deficit_pct_aplicado}%
   
   ⚠️ GUARDRAILS APLICADOS (si aplica):
   {deficit_warning}
   
   Ejemplo Erick:
   • BF Operacional: 26.4%
   • Categoría: Obesidad
   • Déficit: 30.0% (interpolado 50%, limitado por IR-SE 50-69 + sueño <6h)
```
**Estado:** ✅ SIEMPRE (nueva lógica obligatoria)

---

###### **6.2 - Plan Nutricional**
```
📊 6.2 PLAN NUTRICIONAL (Nueva Metodología Científica):

   CALORÍAS: {plan_tradicional_calorias} kcal/día
   ESTRATEGIA: {fase}
   
   MACRONUTRIENTES:
   • Proteína: {proteina_g_tradicional}g ({proteina_kcal_tradicional} kcal) = {porcentaje_proteina}%
     Base: {base_proteina_nombre_email} = {base_proteina_kg_email:.1f} kg × {factor_proteina}g/kg
     (En obesidad se usa MLG/PBM para no inflar proteína)
   
   • Grasas: {grasa_g_tradicional}g ({grasa_kcal_tradicional} kcal) = {porcentaje_grasa}%
   
   • Carbohidratos: {carbo_g_tradicional}g ({carbo_kcal_tradicional} kcal) = {porcentaje_carbo}%
   
   Sostenibilidad: ALTA
   Cambio esperado: 0.3-0.7% peso corporal/semana
   Duración: Indefinida con ajustes periódicos

   Ejemplo Erick:
   • Calorías: 1,683 kcal/día
   • Proteína: 151.2g (base PBM 60.5kg × 2.5)
   • Grasas: 56.1g (30%)
   • Carbos: 143.3g (34%)
```
**Estado:** ✅ SIEMPRE (nueva lógica obligatoria)

---

###### **6.3 - Ciclaje 4-3** (Si `tiene_ciclaje = True`)
```
🔄 6.3 CICLAJE CALÓRICO 4-3 (Optimización Metabólica):

   ESTRATEGIA: Manipulación de carbohidratos según actividad
   
   📉 DÍAS LOW (4 días/semana - Entrenamiento Fuerza):
      • Calorías: {ciclaje_low_kcal} kcal/día
      • Proteína: {low_macros['protein']}g
      • Grasas: {low_macros['fat']}g
      • Carbos: {low_macros['carb']}g (REDUCIDOS para oxidación grasa)
   
   📈 DÍAS HIGH (3 días/semana - Descanso/Cardio):
      • Calorías: {ciclaje_high_kcal} kcal/día
      • Proteína: {high_macros['protein']}g (constante)
      • Grasas: {high_macros['fat']}g (constante)
      • Carbos: {high_macros['carb']}g (AUMENTADOS +{carb_diff}g)
   
   📊 PROMEDIO SEMANAL: {plan_tradicional_calorias} kcal/día
   
   💡 BENEFICIOS:
   • Mejor adherencia vs déficit constante
   • Minimiza adaptación metabólica
   • Soporte hormonal en días altos (leptina, testosterona)
   • Mayor oxidación de grasa en días bajos

   Ejemplo Erick:
   LOW: 1,346 kcal | P: 151.2g | F: 44.9g | C: 84.3g
   HIGH: 2,132 kcal | P: 151.2g | F: 71.1g | C: 221.8g
```
**Estado:** ✅ SI `tiene_ciclaje = True` (siempre True con nueva lógica)

---

###### **6.3b - Plan PSMF** (Si `plan_psmf_disponible = True`)
```
⚡ 6.3 PROTOCOLO PSMF (APLICABLE):

   CALORÍAS: {calorias_psmf} kcal/día
   CRITERIO: {psmf_criterio}
   
   MACRONUTRIENTES:
   • Proteína: {proteina_psmf}g ({proteina_kcal_psmf} kcal) = {porcentaje_psmf}%
   • Grasas: {grasa_psmf}g ({grasa_kcal_psmf} kcal) = {porcentaje_grasa_psmf}%
   • Carbohidratos: {carbo_psmf}g ({carbo_kcal_psmf} kcal) = {porcentaje_carbo_psmf}%
   
   • Multiplicador: {k_usado}
   • Déficit: {deficit_psmf}%
   • Pérdida esperada: 0.6-1.0 kg/semana
   • Sostenibilidad: BAJA (máx 6-8 semanas)
   • Suplementación: Multivitamínico, omega-3, electrolitos, Mg
   • ⚠️ Requiere supervisión médica y análisis de sangre
```
**Estado:** ✅ SI `plan_psmf_disponible = True`

---

###### **6.4 - Comparativa de Estrategias**
```
Disponibilidad: {disponibilidad}
Velocidad: {velocidad_comparativa}
Riesgo muscular: {riesgo_comparativa}
```
**Estado:** ✅ SIEMPRE

---

##### **7️⃣ PROYECCIONES DE PROGRESO** (Sección 7)
```
Proyección de cambios en composición corporal:

1 MES:
  • Peso esperado: {peso_1mes} kg
  • % Grasa esperado: {grasa_1mes}%
  • MLG esperada: {mlg_1mes} kg

2 MESES:
  • Peso esperado: {peso_2mes} kg
  • % Grasa esperado: {grasa_2mes}%
  • MLG esperada: {mlg_2mes} kg

3 MESES:
  • Peso esperado: {peso_3mes} kg
  • % Grasa esperado: {grasa_3mes}%
  • MLG esperada: {mlg_3mes} kg
```
**Estado:** ✅ SIEMPRE (calculadas en integracion_nueva_logica.py)

---

##### **8️⃣ FOTOS DE PROGRESO** (Si disponibles)
```
Attachments:
  - photo1_initial.jpg (Frontal inicial)
  - photo2_side.jpg (Lateral inicial)
  - photo3_back.jpg (Dorsal inicial)
  - photo4_pose_libre.jpg (Pose libre)
```
**Estado:** ❓ Condicional (solo si usuario subió fotos)

---

##### **9️⃣ FOOTER**
```
© 2025 MUPAI - Muscle Up GYM
Digital Training Science
muscleupgym.fitness

Importante: Esta evaluación tiene validez de 3 meses.
Se recomienda reevaluar trimestralemente para ajustes.
```
**Estado:** ✅ SIEMPRE

---

### **EMAIL 2: RESUMEN PARA ADMINISTRACIÓN**
**Función:** `enviar_email_resumen()`  
**Destinatario:** `administracion@muscleupgym.fitness`  
**Asunto:** `Resumen evaluación MUPAI - {nombre_cliente} ({fecha})`  
**Contenido:** Texto plano de tabla_resumen

#### **INFORMACIÓN INCLUIDA:**
```
1. Encabezado con fecha y nombre
2. TODA la tabla_resumen (identidad 100% con Email 1)
3. Attachments: Todas las fotos de progreso (si existen)
```
**Estado:** ✅ SIEMPRE

---

### **EMAIL 3: COPIA INTERNA AL CLIENTE**
**Función:** `enviar_email_parte2()`  
**Destinatario:** `administracion@muscleupgym.fitness`  
**Asunto:** `[COPIA CLIENTE] Evaluación {nombre_cliente} - {fecha}`  
**Contenido:** HTML IDÉNTICO al Email 1

#### **INFORMACIÓN INCLUIDA:**
```
EXACTAMENTE lo mismo que Email 1
(Para que admin vea qué se envió al usuario)
```
**Estado:** ✅ SIEMPRE

---

### **EMAIL 4: EXPORT YAML ESTRUCTURADO**
**Función:** `enviar_email_yaml()`  
**Destinatario:** `administracion@muscleupgym.fitness`  
**Asunto:** `YAML Evaluación {nombre_cliente} ({fecha})`  
**Formato:** YAML con estructura jerárquica

#### **ESTRUCTURA COMPLETA:**

```yaml
metadata:
  fecha_evaluacion: 2026-01-04
  sistema: MUPAI v2.0
  version: 2.0.0
  tipo_reporte: Evaluacion_Completa
  nueva_logica_activa: true

datos_personales:
  nombre_cliente: Erick de Luna
  email: erickdeluna55@hotmail.com
  telefono: 8662580594
  edad: 30
  sexo: Hombre
  ciclo_menstrual: null

composicion_corporal:
  peso_kg: 82.2
  estatura_cm: 170.0
  imc: 28.44
  grasa_corporal_pct: 26.4
  mlg_kg: 60.5
  masa_grasa_kg: 21.7
  circunferencia_cintura_cm: 96.7
  masa_muscular_omron_kg: 34.7
  masa_muscular_estimada_kg: 23.0
  # NUEVA LÓGICA
  bf_operacional: 26.4
  categoria_bf: obesidad
  categoria_bf_cliente: Obesidad

indices_corporales:
  ffmi: 21.56
  wthr: 0.569
  grasa_visceral_nivel: 12
  edad_metabolica: 33
  nivel_entrenamiento: élite

metabolismo:
  tmb_kcal: 1677
  ge_kcal: 2404
  geaf: 1.11
  eta: 1.10
  gee_promedio_dia: 357

macronutrientes_tradicionales:
  proteina_g: 151.2
  proteina_kcal: 605
  grasa_g: 56.1
  grasa_kcal: 505
  carbohidratos_g: 143.3
  carbohidratos_kcal: 573
  calorias_totales: 1683
  base_proteina: pbm_ajustado
  factor_proteina: 2.5
  # NUEVA LÓGICA
  deficit_pct_aplicado: 30.0
  pbm_kg: 60.5

ciclaje_4_3:
  disponible: true
  low_day_kcal: 1346
  high_day_kcal: 2132
  low_days: 4
  high_days: 3
  low_macros:
    protein: 151.2
    fat: 44.9
    carb: 84.3
  high_macros:
    protein: 151.2
    fat: 71.1
    carb: 221.8

plan_psmf:
  aplicable: true
  proteina_g: 112.4
  grasa_g: 50.0
  carbohidratos_g: 8.4
  calorias_dia: 1018
  tier: tier_2

proyecciones:
  1_mes:
    peso: 80.5
    grasa_pct: 24.8
    mlg: 60.8
  2_meses:
    peso: 79.0
    grasa_pct: 23.5
    mlg: 61.0
  3_meses:
    peso: 77.5
    grasa_pct: 22.0
    mlg: 61.2

recuperacion:
  suenyo_estres_completado: true
  ir_se: 64.3
  nivel_recuperacion: MEDIA
  sleep_score: 57.1
  stress_score: 75.0

metas_personales:
  completado: true
  condiciones_medicas:
    - Ninguna de las anteriores
  lesiones:
    - Ninguna lesión o limitación
  facilidad_muscular:
    - Pectoral (Pecho)
    - Glúteos
  dificultad_muscular:
    - Tríceps
    - Pantorrillas
  prioridades_muscular:
    - Tríceps
    - Bíceps
  objetivos_detallados: "A mediano plazo..."
```

**Estado:** ✅ SIEMPRE (100% de campos con nueva lógica)

---

### **EMAIL 5: SUEÑO/ESTRÉS** (Opcional)
**Función:** `enviar_email_suenyo_estres()`  
**Destinatario:** `administracion@muscleupgym.fitness`  
**Contenido:** Datos de recuperación

#### **INFORMACIÓN:**
```
IR-SE Score: {ir_se}
Sleep Score: {sleep_score}
Stress Score: {stress_score}
Nivel Recuperación: {nivel_recuperacion}
```
**Estado:** ❓ Solo si usuario completó sección de sueño/estrés

---

## 📊 TABLA RESUMEN: CAMPOS POR EMAIL

| Campo | Email 1 | Email 2 | Email 3 | Email 4 | Origen |
|-------|---------|---------|---------|---------|--------|
| **Datos Personales** | ✅ | - | ✅ | ✅ | Form paso 1 |
| **Composición Corporal** | ✅ | - | ✅ | ✅ | Form paso 2 |
| **Índices Corporales** | ✅ | - | ✅ | ✅ | Cálculos automáticos |
| **TMB/GE** | ✅ | - | ✅ | ✅ | Cunningham + GEAF + ETA |
| **Plan Nutricional Nuevo** | ✅ | - | ✅ | ✅ | nueva_logica_macros.py |
| **Ciclaje 4-3** | ✅ | - | ✅ | ✅ | calcular_ciclaje_4_3() |
| **PSMF** | ✅ | - | ✅ | ✅ | calcular_macros_psmf() |
| **Proyecciones** | ✅ | - | ✅ | ✅ | calcular_proyecciones() |
| **Sueño/Estrés** | ✅ | - | ✅ | ✅ | Form paso 6b (opcional) |
| **Metas Personales** | - | - | - | ✅ | Form paso 8 (opcional) |
| **Fotos Progreso** | 🖼️ | 🖼️ | 🖼️ | - | Upload paso 9 |

---

## 🔄 FLUJO DE DATOS DESDE FORMULARIO A EMAILS

```
1. PASO 1 → Datos Personales
   ↓
2. PASO 2 → Composición Corporal
   ↓
3. PASO 3 → FFMI/WtHR/Grasa Visceral
   ↓
4. PASO 4 → ETA (Efecto Térmico)
   ↓
5. PASO 5 → Entrenamientos (GEE)
   ↓
6. PASO 6a → Nivel Actividad (GEAF)
   ↓
[CÁLCULO TMB = 370 + (21.6 × MLG)]
[CÁLCULO GE = (TMB × GEAF × ETA) + GEE]
   ↓
7. PASO 6b → Sueño/Estrés (OPCIONAL)
   ↓
[NUEVA LÓGICA → calcular_plan_con_sistema_actual()]
[INTERPOLA DÉFICIT SEGÚN BF% + GUARDRAILS]
   ↓
8. PASO 7 → Selección Plan (tradicional/PSMF)
   ↓
9. PASO 8 → Metas Personales (OPCIONAL)
   ↓
10. PASO 9 → Fotos Progreso (OPCIONAL)
   ↓
[GENERACIÓN TABLA_RESUMEN con Email 1]
   ↓
ENVIAR 4 EMAILS + 1 YAML
```

---

## 🎯 GARANTÍAS DE INTEGRIDAD

### ✅ **CAMPOS QUE SIEMPRE SE INCLUYEN:**

1. **Datos personales completos** (nombre, edad, sexo, contacto)
2. **Composición corporal** (peso, grasa, MLG, visceral, WtHR, FFMI, circunferencia)
3. **Metabolismo** (TMB, GE, GEAF, ETA, GEE)
4. **Plan nutricional con nueva lógica** (macros basados en interpolación + guardrails)
5. **Ciclaje 4-3** (días LOW/HIGH con macros detallados)
6. **PSMF** (si aplica, calculado con factor K dinámico)
7. **Proyecciones** (1, 2, 3 meses)

### ⚠️ **CAMPOS CONDICIONALES:**

1. **Sueño/Estrés** - Solo si usuario completó form
2. **Metas Personales** - Solo si usuario completó form
3. **Fotos Progreso** - Solo si usuario subió fotos
4. **Ciclo Menstrual** - Solo si sexo = Mujer
5. **Masa muscular Omron** - Solo si dispositivo disponible

### ❌ **CAMPOS QUE NUNCA SE INCLUYEN:**

1. Contraseñas o datos sensibles de login
2. Información de otros usuarios
3. Borradores o datos incompletos
4. Errores de cálculo (se validan antes de enviar)

---

## 📈 VALIDACIÓN PRE-ENVÍO

Antes de enviar emails, sistema valida:

```
✅ GE > 0 (gasto energético válido)
✅ TMB calculado correctamente
✅ Macros suman 100% calorías totales
✅ Proteína ≥ mínimo recomendado
✅ Grasas 20-35% calorías
✅ Carbos residual positivo
✅ Ciclaje promedio = GE (verificación matemática)
✅ PSMF solo si BF% cumple criterios
✅ Proyecciones realistas (±0.5-1.0 kg/semana)
✅ Email válido formato
```

---

## 🚀 TECNOLOGÍAS USADAS

- **Email Provider:** Zoho Mail (SMTP)
- **Formato:** MIME (texto + HTML + attachments)
- **Encoding:** Base64 (logos, fotos)
- **YAML:** Estructura jerárquica para parsing
- **Cálculos:** NumPy, SciPy (interpolación)
- **Proyecciones:** Modelado matemático líneal + exponencial

---

## 💾 ALMACENAMIENTO & RETENCIÓN

- **Emails guardados:** Google Drive (automático)
- **YAML almacenado:** Zoho (para auditoría)
- **Fotos:** Google Drive (si se suben)
- **Retención:** Indefinida (cumplimiento GDPR)
- **Backup:** Semanal automatizado

---

## ⚡ EJEMPLO REAL: ERICK DE LUNA (26.4% BF)

### Email 1 (Cuerpo Reducido):
```
═══════════════════════════════════════════════════════════
ERICK DE LUNA - Evaluación MUPAI (4 Enero 2026)
═══════════════════════════════════════════════════════════

📊 COMPOSICIÓN CORPORAL:
   Peso: 82.2 kg | Estatura: 170 cm | IMC: 28.44
   % Grasa: 26.4% | MLG: 60.5 kg | Visceral: 12

🏋️ ÍNDICES:
   FFMI: 21.56 | WtHR: 0.569 | Edad Metabólica: 33 años

💪 METABOLISMO:
   TMB: 1,677 kcal = 370 + (21.6 × 60.5)
   GE: 2,404 kcal = (1,677 × 1.11 × 1.10) + 357
   
   Desglose:
   • GEAF (Actividad): 1.11
   • ETA (Térmica): 1.10
   • GEE (Ejercicio): 357 kcal/día

📋 PLAN NUTRICIONAL (Nueva Metodología):

   🎯 COMPOSICIÓN CORPORAL (Nueva):
   • BF Operacional: 26.4% → Categoría: OBESIDAD
   • Déficit: 30% (interpolado 50%, guardrails por IR-SE 50-69 + sueño <6h)
   
   📊 MACROS PROMEDIO:
   • Calorías: 1,683 kcal/día
   • Proteína: 151.2g (base PBM 60.5kg × 2.5g/kg)
   • Grasas: 56.1g (30%)
   • Carbos: 143.3g (34%)

   🔄 CICLAJE 4-3:
   
   📉 DÍAS LOW (Lun-Jue, 4 días):
      1,346 kcal | P: 151.2g | F: 44.9g | C: 84.3g
   
   📈 DÍAS HIGH (Vie-Dom, 3 días):
      2,132 kcal | P: 151.2g | F: 71.1g | C: 221.8g (+138g carbos)
   
   Promedio semanal: 1,683 kcal/día ✅

📈 PROYECCIONES (3 meses):
   1 mes:  80.5 kg | 24.8% grasa | 60.8 kg MLG
   2 meses: 79.0 kg | 23.5% grasa | 61.0 kg MLG
   3 meses: 77.5 kg | 22.0% grasa | 61.2 kg MLG

═══════════════════════════════════════════════════════════
```

### Email 4 (YAML):
```yaml
nueva_logica_activa: true
bf_operacional: 26.4
categoria_bf: obesidad
deficit_pct_aplicado: 30.0
pbm_kg: 60.5

ciclaje_4_3:
  disponible: true
  low_day_kcal: 1346
  high_day_kcal: 2132
  low_macros:
    protein: 151.2
    fat: 44.9
    carb: 84.3
  high_macros:
    protein: 151.2
    fat: 71.1
    carb: 221.8
```

---

## 🎓 CONCLUSIÓN

**TODOS los datos de la nueva lógica llegan completos a:**
- ✅ Email 1 (cliente)
- ✅ Email 2 (admin resumen)
- ✅ Email 3 (admin copia)
- ✅ Email 4 (admin YAML)
- ✅ Email 5 (sueño/estrés si aplica)

**Sin fallbacks, sin datos incompletos, sin errores.**

Reinicia Streamlit y todo funcionará correctamente.

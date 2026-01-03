# ============================================================================
# DOCUMENTACIÓN: ESTRUCTURA YAML PARA MACHINE LEARNING
# Sistema MUPAI v2.0 - Input para Generación de Planes Personalizados
# ============================================================================

## PROPÓSITO
Este documento describe la estructura del Email 4 (formato YAML) que sirve como
input para sistemas de Machine Learning destinados a generar planes de 
entrenamiento y nutrición completamente personalizados.

## ARCHIVOS DE EJEMPLO
- ejemplo_yaml_hombre.yaml  → Caso de hombre de 28 años, nivel intermedio
- ejemplo_yaml_mujer.yaml   → Caso de mujer de 32 años, con condiciones médicas

## ESTRUCTURA COMPLETA DEL YAML

### 1. METADATA (información del sistema)
```yaml
metadata:
  fecha_evaluacion: str     # Fecha de la evaluación (YYYY-MM-DD)
  sistema: str              # Nombre del sistema (MUPAI v2.0)
  version: str              # Versión del sistema
  tipo_reporte: str         # Tipo de reporte generado
```

### 2. DATOS_PERSONALES (información demográfica)
```yaml
datos_personales:
  nombre_cliente: str       # Nombre completo del cliente
  email: str                # Email de contacto
  telefono: str             # Teléfono (opcional)
  edad: int                 # Edad en años
  sexo: str                 # "Hombre" o "Mujer"
  ciclo_menstrual: str      # Solo para mujeres, null para hombres
```

**Valores posibles de ciclo_menstrual:**
- "Estoy en mi periodo (menstruando actualmente)"
- "Terminé mi periodo hace 1-7 días (semana después del periodo)"
- "Estoy a mitad de ciclo - días 12-16 (semana en medio del ciclo)"
- "Estoy en la segunda mitad del ciclo - días 17-28 (1-2 semanas antes del siguiente periodo)"
- "No tengo ciclo menstrual (menopausia, embarazo, condición médica, o anticonceptivos sin regla)"

### 3. COMPOSICION_CORPORAL (métricas corporales)
```yaml
composicion_corporal:
  peso_kg: float            # Peso corporal en kilogramos
  estatura_cm: float        # Estatura en centímetros
  imc: float                # Índice de Masa Corporal
  grasa_corporal_pct: float # Porcentaje de grasa corporal
  mlg_kg: float             # Masa Libre de Grasa en kg
  masa_grasa_kg: float      # Masa grasa en kg
  circunferencia_cintura_cm: float  # Cintura en cm (puede ser null)
  masa_muscular_omron_kg: float     # De báscula Omron (puede ser null)
  masa_muscular_estimada_kg: float  # Estimación científica
```

### 4. INDICES_CORPORALES (índices de salud y composición)
```yaml
indices_corporales:
  ffmi: float               # Fat-Free Mass Index
  wthr: float               # Waist-to-Height Ratio
  grasa_visceral_nivel: int # Nivel de grasa visceral (1-30)
  edad_metabolica: int      # Edad metabólica calculada
  nivel_entrenamiento: str  # Nivel de experiencia
```

**Valores posibles de nivel_entrenamiento:**
- "principiante"
- "principiante-intermedio"
- "intermedio"
- "intermedio-avanzado"
- "avanzado"

### 5. METABOLISMO (gasto energético)
```yaml
metabolismo:
  tmb_kcal: float           # Tasa Metabólica Basal
  ge_kcal: float            # Gasto Energético Total
  geaf: float               # Factor de Actividad Física
```

### 6. MACRONUTRIENTES_TRADICIONALES (plan nutricional base)
```yaml
macronutrientes_tradicionales:
  proteina_g: float         # Proteína en gramos/día
  proteina_kcal: float      # Calorías de proteína
  grasa_g: float            # Grasa en gramos/día
  grasa_kcal: float         # Calorías de grasa
  carbohidratos_g: float    # Carbohidratos en gramos/día
  carbohidratos_kcal: float # Calorías de carbohidratos
  calorias_totales: float   # Calorías totales/día
  base_proteina: str        # Base de cálculo proteína
  factor_proteina: float    # Multiplicador usado
```

**Valores posibles de base_proteina:**
- "Peso Corporal Total"
- "MLG (Masa Libre de Grasa)"

### 7. PLAN_PSMF (plan cetogénico agresivo - solo casos específicos)
```yaml
plan_psmf:
  aplicable: bool           # true/false si aplica PSMF
  proteina_g: float         # null si no aplica
  grasa_g: float            # null si no aplica
  carbohidratos_g: float    # null si no aplica
  calorias_dia: float       # null si no aplica
  tier: str                 # null si no aplica
```

**Valores posibles de tier (cuando aplica):**
- "Tier 1"
- "Tier 2"
- "Tier 3"
- "Tier 4"

### 8. PROYECCIONES (cambios esperados en el tiempo)
```yaml
proyecciones:
  1_mes:
    peso_inicial_kg: float
    peso_proyectado_kg: float
    cambio_kg: float        # Negativo = pérdida, Positivo = ganancia
    cambio_pct: float
    grasa_proyectada_pct: float
  2_meses: { ... }          # Misma estructura
  3_meses: { ... }          # Misma estructura
```

### 9. RECUPERACION (calidad de sueño y estrés)
```yaml
recuperacion:
  suenyo_estres_completado: bool  # Si se completó el cuestionario
  ir_se: float              # Índice de Recuperación Sueño-Estrés (0-1)
  nivel_recuperacion: str   # Clasificación textual
  sleep_score: float        # Puntuación de sueño (0-10)
  stress_score: float       # Puntuación de estrés (0-10)
```

**Valores posibles de nivel_recuperacion:**
- "Excelente recuperación"
- "Buena recuperación"
- "Recuperación moderada - necesita mejora"
- "Recuperación deficiente - prioridad alta"
- "Recuperación crítica - intervención urgente"

### 10. METAS_PERSONALES (objetivos y consideraciones del cliente)
```yaml
metas_personales:
  completado: bool          # Si se completó toda la sección
  
  # CONDICIONES MÉDICAS
  condiciones_medicas:      # Lista de strings
    - str
    - str
  condiciones_otras: str    # Texto adicional (puede ser '')
  
  # LESIONES/LIMITACIONES
  lesiones:                 # Lista de strings
    - str
    - str
  lesiones_otras: str       # Texto adicional (puede ser '')
  
  # PREFERENCIAS MUSCULARES
  facilidad_muscular:       # Lista de strings (grupos que se desarrollan fácil)
    - str
    - str
  dificultad_muscular:      # Lista de strings (grupos difíciles de desarrollar)
    - str
    - str
  prioridades_muscular:     # Lista de strings (grupos a priorizar)
    - str
    - str
  limitacion_muscular:      # Lista de strings (grupos a no enfatizar)
    - str
    - str
  
  # OBJETIVOS DETALLADOS
  objetivos_detallados: str # Texto largo con objetivos a mediano/largo plazo
```

### OPCIONES DISPONIBLES EN METAS_PERSONALES

#### Condiciones Médicas/Fisiológicas:
- "Diabetes Tipo 1"
- "Diabetes Tipo 2"
- "Hipertensión arterial"
- "Hipotiroidismo"
- "Hipertiroidismo"
- "Síndrome de ovario poliquístico (SOP)"
- "Resistencia a la insulina"
- "Enfermedad cardiovascular"
- "Embarazo"
- "Lactancia"
- "Ninguna de las anteriores"

#### Lesiones/Limitaciones:
- "Lesión de hombro (manguito rotador, tendinitis, etc.)"
- "Lesión de codo (epicondilitis, tendinitis, etc.)"
- "Lesión de muñeca/mano"
- "Lesión de espalda baja (lumbar)"
- "Lesión de espalda alta (torácica)"
- "Lesión de rodilla (menisco, ligamentos, tendinitis, etc.)"
- "Lesión de tobillo/pie"
- "Lesión de cadera"
- "Hernia discal"
- "Escoliosis o desviaciones posturales"
- "Ninguna lesión o limitación"

#### Grupos Musculares (aplica a todas las categorías):
- "Pectoral (Pecho)"
- "Deltoide anterior (Hombro frontal)"
- "Deltoide medial (Hombro lateral)"
- "Trapecio medio, romboides y deltoide posterior (Espalda alta y hombro trasero)"
- "Dorsal ancho (Espalda ancha / 'Alas')"
- "Tríceps (Parte trasera del brazo)"
- "Bíceps (braquial, braquiorradial, músculos de los antebrazos) (Parte frontal del brazo y antebrazos)"
- "Recto abdominal (Abdomen frontal / 'Six pack')"
- "Oblicuos (Costados del abdomen)"
- "Cuádriceps (Parte frontal del muslo)"
- "Isquiotibiales (Parte trasera del muslo / Femorales)"
- "Glúteos (Glúteos / Pompis)"
- "Sóleo y gastrocnemio (Pantorrillas)"
- "Aductores (Parte interna del muslo)"

Opciones especiales:
- Facilidad/Dificultad: "Ninguno en particular"
- Prioridades: "Desarrollo equilibrado (sin prioridades específicas)"
- Limitación: "Ninguno (quiero desarrollar todos por igual)"

## CASOS DE USO PARA MACHINE LEARNING

### 1. Personalización de Ejercicios
- **Entrada**: `metas_personales.lesiones` + `metas_personales.lesiones_otras`
- **Salida**: Ejercicios que eviten zonas lesionadas

### 2. Volumen de Entrenamiento
- **Entrada**: `nivel_entrenamiento` + `recuperacion.ir_se`
- **Salida**: Frecuencia, volumen e intensidad apropiados

### 3. Distribución de Grupos Musculares
- **Entrada**: `metas_personales.prioridades_muscular` + `metas_personales.facilidad_muscular`
- **Salida**: División de entrenamiento enfocada

### 4. Plan Nutricional
- **Entrada**: `macronutrientes_tradicionales` + `condiciones_medicas`
- **Salida**: Plan nutricional adaptado a condiciones médicas

### 5. Timing y Frecuencia
- **Entrada**: `ciclo_menstrual` + `recuperacion.sleep_score`
- **Salida**: Ajuste de intensidad según fase hormonal y recuperación

### 6. Objetivos a Largo Plazo
- **Entrada**: `objetivos_detallados` + `proyecciones`
- **Salida**: Plan progresivo con hitos intermedios

## EJEMPLO DE PIPELINE ML

```python
import yaml

# Cargar YAML
with open('cliente_data.yaml', 'r', encoding='utf-8') as f:
    cliente = yaml.safe_load(f)

# Extraer features clave
edad = cliente['datos_personales']['edad']
sexo = cliente['datos_personales']['sexo']
grasa_pct = cliente['composicion_corporal']['grasa_corporal_pct']
nivel = cliente['indices_corporales']['nivel_entrenamiento']
lesiones = cliente['metas_personales']['lesiones']
prioridades = cliente['metas_personales']['prioridades_muscular']

# Generar plan personalizado
plan_entrenamiento = generar_plan(
    edad=edad,
    sexo=sexo,
    nivel=nivel,
    lesiones=lesiones,
    prioridades=prioridades
)

plan_nutricion = generar_nutricion(
    proteina_g=cliente['macronutrientes_tradicionales']['proteina_g'],
    carbohidratos_g=cliente['macronutrientes_tradicionales']['carbohidratos_g'],
    grasa_g=cliente['macronutrientes_tradicionales']['grasa_g'],
    condiciones=cliente['metas_personales']['condiciones_medicas']
)
```

## NOTAS IMPORTANTES

1. **Todos los campos numéricos pueden ser `null`** si no están disponibles
2. **Las listas pueden estar vacías** `[]` si no se seleccionó nada
3. **Los strings de texto pueden ser vacíos** `''` si no se proporcionó información
4. **El campo `ciclo_menstrual` es null para hombres**
5. **El campo `plan_psmf` suele tener todos los valores null** excepto en casos de grasa corporal alta
6. **Encoding UTF-8** para caracteres especiales (tildes, eñes, etc.)

## VALIDACIÓN RECOMENDADA

Antes de procesar el YAML con ML, validar:
- `completado: true` en `metas_personales`
- Valores numéricos dentro de rangos fisiológicos
- Al menos 1 elemento en listas de preferencias musculares
- `objetivos_detallados` con mínimo 50 caracteres

## CONTACTO
Sistema: MUPAI v2.0
Documentación: 2026-01-02

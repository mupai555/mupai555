# Cuestionario de Sueño + Estrés - Documentación de Implementación

## Resumen

Se ha implementado un cuestionario independiente para evaluar el "Estado de Recuperación (Sueño + Estrés)" en el archivo `streamlit_app.py`. Esta funcionalidad es completamente modular y no afecta la lógica existente de la aplicación.

## Ubicación en el Código

- **Definición de funciones**: Líneas 2245-2695 de `streamlit_app.py`
  - `formulario_suenyo_estres()`: Función principal del cuestionario
  - `enviar_email_suenyo_estres()`: Función para envío de correo

- **Integración en el flujo**: Línea 2976-2994 de `streamlit_app.py`
  - Se ejecuta inmediatamente después de completar los datos personales
  - Antes de cualquier cálculo complejo de la aplicación

## Características Implementadas

### 1. Preguntas del Cuestionario

#### Sección de Sueño (4 preguntas):
- **Horas de sueño**: ≥8h, 7-7.9h, 6-6.9h, 5-5.9h, <5h
  - Puntuación: 0-4 puntos
- **Tiempo para conciliar**: <15min, 15-30min, 30-60min, >60min
  - Puntuación: 0-3 puntos
- **Despertares nocturnos**: Ninguna, 1 vez, 2 veces, 3+ veces
  - Puntuación: 0-3 puntos
- **Calidad del sueño**: Excelente, Buena, Regular, Mala, Muy mala
  - Puntuación: 0-4 puntos

**Puntuación total de sueño**: 0-14 puntos

#### Sección de Estrés (4 preguntas):
- **Sobrecarga**: Nunca, Casi nunca, A veces, Frecuentemente, Muy frecuentemente
  - Puntuación: 0-4 puntos
- **Falta de control**: Nunca, Casi nunca, A veces, Frecuentemente, Muy frecuentemente
  - Puntuación: 0-4 puntos
- **Dificultad para manejar**: Nunca, Casi nunca, A veces, Frecuentemente, Muy frecuentemente
  - Puntuación: 0-4 puntos
- **Irritabilidad**: Nunca, Casi nunca, A veces, Frecuentemente, Muy frecuentemente
  - Puntuación: 0-4 puntos

**Puntuación total de estrés**: 0-16 puntos

### 2. Cálculo de Puntuaciones

#### SleepScore (0-100)
```
SleepScore = max(0, 100 - (puntuación_cruda_sueño / 14 × 100))
```
- 0 puntos crudos → 100 SleepScore (perfecto)
- 14 puntos crudos → 0 SleepScore (muy malo)

#### StressScore (0-100)
```
StressScore = max(0, 100 - (puntuación_cruda_estrés / 16 × 100))
```
- 0 puntos crudos → 100 StressScore (sin estrés)
- 16 puntos crudos → 0 StressScore (estrés máximo)

#### Índice IR-SE (Índice de Recuperación Sueño-Estrés)
```
IR-SE = (SleepScore × 0.6) + (StressScore × 0.4)
```

**Ponderación**:
- Sueño: 60% (factor más crítico para recuperación física)
- Estrés: 40% (importante pero secundario)

### 3. Clasificación de Recuperación

| IR-SE | Nivel | Interpretación |
|-------|-------|----------------|
| 70-100 | **ALTA** | Excelente estado de recuperación, óptimo para entrenamiento |
| 50-69 | **MEDIA** | Recuperación moderada, considerar mejoras |
| 0-49 | **BAJA** | Recuperación comprometida, intervención necesaria |

### 4. Sistema de Banderas de Alerta

#### Banderas Rojas (Problemas Graves):
- **Sueño**: Puntuación cruda ≥10 puntos
  - Mensaje: "Problemas graves de sueño detectados"
  - Recomendación: Consultar especialista en medicina del sueño

- **Estrés**: Puntuación cruda ≥12 puntos
  - Mensaje: "Nivel de estrés crítico"
  - Recomendación: Buscar apoyo profesional (psicólogo/terapeuta)

#### Banderas Amarillas (Problemas Moderados):
- **Sueño subóptimo**: 7 ≤ puntuación < 10
  - Mensaje: "Calidad de sueño subóptima"
  - Recomendación: Implementar higiene del sueño

- **Estrés elevado**: 8 ≤ puntuación < 12
  - Mensaje: "Nivel de estrés elevado"
  - Recomendación: Técnicas de manejo del estrés

- **Duración insuficiente**: Menos de 6 horas de sueño
  - Mensaje: "Duración de sueño insuficiente"
  - Recomendación: Aumentar a 7-8 horas

### 5. Funcionalidad de Email

#### Destinatario
- Email: `administracion@muscleupgym.fitness`

#### Contenido del Informe
1. **Información del Cliente**
   - Nombre, email, fecha de evaluación

2. **Respuestas del Cuestionario**
   - Todas las respuestas de sueño y estrés

3. **Resultados Calculados**
   - SleepScore, StressScore, IR-SE
   - Puntuaciones crudas detalladas
   - Clasificación de recuperación

4. **Alertas y Banderas**
   - Listado de todas las banderas detectadas
   - Descripciones y recomendaciones

5. **Interpretación y Recomendaciones**
   - Explicación de los resultados
   - Fórmulas utilizadas
   - Recomendaciones generales

## Flujo de Usuario

1. Usuario completa datos personales y acepta términos
2. Aparece el cuestionario de Sueño + Estrés
3. Usuario responde las 8 preguntas (4 sueño + 4 estrés)
4. Usuario presiona "📊 Calcular Estado de Recuperación"
5. Sistema muestra:
   - Métricas: SleepScore, StressScore, IR-SE
   - Clasificación visual con código de colores
   - Banderas de alerta (si aplican)
   - Detalles técnicos (colapsable)
6. Si el cuestionario está completo, aparece botón:
   - "📧 Enviar Informe de Sueño + Estrés por Email"
7. Usuario puede enviar el informe a administración
8. Usuario continúa con el resto de la evaluación MUPAI

## Independencia del Sistema

El cuestionario de Sueño + Estrés es **completamente independiente**:
- No afecta cálculos nutricionales existentes
- No modifica el flujo de evaluación principal
- Se ejecuta en su propio espacio de session_state
- Puede omitirse sin afectar otras funcionalidades
- Tiene su propio sistema de email separado

## Testing

Se ha creado `test_suenyo_estres.py` con tests completos:

### Tests Implementados:
1. ✓ Verificación de definición de funciones
2. ✓ Verificación de integración en el flujo
3. ✓ Verificación de todas las preguntas
4. ✓ Tests de scoring logic (5 casos de prueba)
5. ✓ Tests de clasificación (ALTA/MEDIA/BAJA)
6. ✓ Tests de detección de banderas (rojas/amarillas)
7. ✓ Verificación de fórmula de ponderación

### Ejecutar Tests:
```bash
python3 test_suenyo_estres.py
```

Todos los tests pasan exitosamente ✓

## Archivos Modificados

- `streamlit_app.py`: +523 líneas
  - Funciones: `formulario_suenyo_estres()`, `enviar_email_suenyo_estres()`
  - Integración en flujo principal
  - Session state para almacenar resultados

## Archivos Nuevos

- `test_suenyo_estres.py`: Test completo del cuestionario

## Consideraciones de Desarrollo

1. **Modo Desarrollo**: Si `zoho_password == "TU_PASSWORD_AQUI"`, el email no se envía realmente (modo simulado)
2. **Session State**: Resultados se almacenan en `st.session_state.suenyo_estres_data`
3. **Flag de Completado**: `st.session_state.suenyo_estres_completado` controla visibilidad del botón de email
4. **Estilos CSS**: Usa las clases CSS existentes del sistema MUPAI para consistencia visual

## Validación Científica

### Bases del Diseño:
- **Escala de sueño**: Basada en criterios de higiene del sueño de NSF (National Sleep Foundation)
- **Escala de estrés**: Adaptada de PSS (Perceived Stress Scale)
- **Ponderación 60/40**: El sueño tiene mayor peso porque:
  - Es el factor #1 en recuperación física
  - Afecta directamente la síntesis proteica y reparación muscular
  - El estrés es modulable pero secundario al sueño para rendimiento físico

### Rangos de Clasificación:
- **ALTA (≥70)**: Estado óptimo respaldado por investigación en atletas
- **MEDIA (50-69)**: Funcional pero con margen de mejora
- **BAJA (<50)**: Requiere intervención, asociado con pobre recuperación

## Mantenimiento Futuro

### Posibles Mejoras:
1. Agregar gráficas de progreso temporal
2. Comparación con evaluaciones previas
3. Integración con datos de wearables (Fitbit, Apple Watch)
4. Análisis de tendencias (mejora/deterioro)
5. Recomendaciones personalizadas basadas en perfil

### Escalabilidad:
- Función modular permite fácil modificación
- Estructura de scoring es extensible
- Sistema de banderas es configurable
- Email template es personalizable

---

**Fecha de Implementación**: 2025-12-20
**Versión**: 1.0
**Estado**: ✅ Completo y Probado

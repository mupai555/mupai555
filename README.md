# MUPAI
DIGITAL TRAINING SCIENCE

## Actualizaciones Recientes

### Auto-Extrapolación Omron y PSMF Basado en LBM

#### Extrapolación Automática de Omron para Valores >40%

**Nueva política:** A partir de esta versión, las lecturas de Omron HBF-516 (BIA) que excedan el 40% activan **automáticamente** la extrapolación lineal para calcular el equivalente DEXA.

- **Activación automática**: Cuando una lectura Omron > 40%, el sistema extrapola automáticamente usando la pendiente de los últimos dos puntos de la tabla de calibración
- **Tope configurado**: Las extrapolaciones están limitadas a un máximo de **60%** (configurable mediante `MAX_EXTRAPOLATE`)
- **Transparencia**: La UI muestra claramente cuando se usa extrapolación, indicando que es menos fiable que la interpolación
- **Banner de alta adiposidad**: Para lecturas >= 45%, se muestra un banner destacado recomendando métodos más precisos (DEXA, InBody)

**Ejemplo:**
- Lectura Omron: 58.5% → Equivalente DEXA extrapolado: 60.0% (limitado por el tope)
- Lectura Omron: 43% → Equivalente DEXA extrapolado: 48.3%

#### PSMF Basado en LBM para Alta Adiposidad

**Nueva lógica:** Para casos de alta adiposidad, el cálculo de proteína PSMF ahora se basa en la Masa Libre de Grasa (LBM) en lugar del peso total.

**Criterios de activación:**
- **Hombres**: % grasa corporal >= 35%
- **Mujeres**: % grasa corporal >= 40%

**Factor de proteína:** 1.8 g/kg LBM (configurable mediante `PROTEIN_FACTOR_PSMF_LBM`)

**Ejemplo:**
- Hombre 140kg, 38% grasa (InBody corregido ~52.8% Omron), LBM = 86.8kg
  - Proteína PSMF: 86.8 kg × 1.8 = 156.2g/día (basado en LBM)
  - Sin LBM-switch: 140 kg × 1.6 = 224g/día (basado en peso total)

**Justificación científica:** Para personas con muy alta adiposidad, calcular la proteína sobre el peso total puede resultar en requerimientos excesivos e innecesarios. Usar LBM como base proporciona un objetivo más apropiado y sostenible mientras preserva la masa muscular.

#### Constantes Configurables

```python
MAX_EXTRAPOLATE = 60.0              # Tope máximo para extrapolación Omron
PROTEIN_FACTOR_PSMF_LBM = 1.8       # Factor g/kg LBM para PSMF en alta adiposidad
UMBRAL_ALTA_ADIPOSIDAD = 45.0       # Umbral para banner de advertencia
```

#### Tests Unitarios

Los cambios incluyen tests unitarios completos en `tests/test_conversion.py`:

**Ejecutar tests:**
```bash
python tests/test_conversion.py
```

**Tests incluidos:**
- Interpolación normal Omron (<=40%)
- Extrapolación automática Omron (>40%)
- Límite de extrapolación (tope 60%)
- PSMF normal vs LBM-based según % grasa
- Casos reales documentados

---

## ETA Block - Efecto Térmico de los Alimentos

El bloque ETA es un módulo completo que calcula el Efecto Térmico de los Alimentos basado en composición corporal y sexo.

### Características principales:

- **Cálculo científico**: Utiliza fórmulas validadas y factores diferenciados por sexo y composición corporal
- **Modular**: Completamente independiente y reutilizable
- **Visual**: Incluye componentes visuales con tarjetas informativas
- **Validación**: Sistema de validación integrado
- **Session State**: Actualiza automáticamente el estado de sesión

### Funciones principales:

- `calcular_eta_automatico()`: Función principal de cálculo del ETA
- `mostrar_bloque_eta()`: Función visual completa para el paso 5
- `validate_step_5()`: Validación del paso
- `recalcular_eta()`: Recálculo con nuevos parámetros

### Uso:

```python
from eta_block import mostrar_bloque_eta, calcular_eta_automatico

# Mostrar el bloque completo en Streamlit
is_valid = mostrar_bloque_eta()

# O calcular ETA directamente
eta = calcular_eta_automatico(tmb=1700, geaf=1.25, porcentaje_grasa=15, sexo="Hombre")
```

### Integración:

El bloque se integra perfectamente en el flujo principal de la aplicación MUPAI, reemplazando el código original del paso 5 con una implementación modular y reutilizable.

# MUPAI
DIGITAL TRAINING SCIENCE

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

---

## Auto-Extrapolación Omron y Cálculos Basados en Masa Magra (LBM)

### Política de Extrapolación Omron (>40%)

El sistema implementa un manejo automático y determinista para lecturas Omron HBF-516 fuera del rango de calibración estándar (5-40%):

#### Rangos de Manejo:

1. **≤40%**: Interpolación lineal estándar usando tabla Omron→DEXA
2. **40-45%**: Truncamiento conservador al valor de Omron=40. Se muestra aviso al usuario y opción para solicitar revisión profesional
3. **≥45%**: Extrapolación automática usando pendiente determinista (slope=1.0, equivalente a 1% DEXA por unidad Omron), con cap máximo de 60%

#### Parámetros Configurables:
- `MAX_EXTRAPOLATE = 60.0` - Cap máximo para extrapolación
- `AUTO_EXTRAPOLATE_THRESHOLD = 45.0` - Umbral de activación automática
- `SLOPE_LAST_SEGMENT = 1.0` - Pendiente de extrapolación

### PSMF Basado en Masa Magra (LBM)

Para casos de alta adiposidad, el protocolo PSMF (Protein-Sparing Modified Fast) utiliza Lean Body Mass en lugar de peso total para calcular requerimientos proteicos:

#### Umbrales de Activación:
- **Hombres**: ≥35% grasa corporal
- **Mujeres**: ≥40% grasa corporal
- **Alternativo**: IMC ≥30 (implementación futura)

#### Cálculo:
- Factor proteico: `1.8 g/kg LBM`
- Mantiene multiplicadores calóricos existentes según % grasa
- Pisos calóricos: 700 kcal (mujeres) / 800 kcal (hombres)

### Plan Tradicional en Casos Extremos

En casos de adiposidad extrema (≥45% grasa corporal o lectura Omron ≥45), el plan tradicional también utiliza LBM para mayor precisión:

#### Características:
- Factor proteico: `1.6 g/kg LBM`
- Mínimo carbohidratos: `50g/día`
- Mínimo grasas: `20g/día`
- TEI mínimo: 1400 kcal (hombres) / 1200 kcal (mujeres)
- Déficit máximo: 35% del TDEE

### Trazabilidad

El sistema registra en `session_state`:
- `grasa_extrapolada`: Indica si se aplicó extrapolación
- `grasa_extrapolada_valor`: Valor DEXA corregido usado
- `grasa_extrapolada_medido`: Lectura raw del dispositivo Omron
- `alta_adiposidad`: Flag para casos ≥45%
- `psmf_lbm_based`: Indica uso de LBM en PSMF
- `trad_protein_lbm_used`: Indica uso de LBM en plan tradicional

### Tests

Ejecutar tests de validación:
```bash
python tests/test_conversion.py
```

Los tests verifican:
- Interpolación Omron normal (≤40%)
- Truncamiento zona gris (40-45%)
- Extrapolación automática (≥45%) con cap a 60%
- PSMF basado en LBM para alta adiposidad
- Detección correcta de umbrales extremos

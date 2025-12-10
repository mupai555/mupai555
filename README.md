# MUPAI
DIGITAL TRAINING SCIENCE

## Changelog - Actualizaciones Recientes

### Auto-extrapolacion Omron (>40%) y Calculos basados en LBM

**Fecha:** Diciembre 2025

#### Nuevas Funcionalidades

1. **Auto-extrapolacion para Omron >40%**
   - Cuando las lecturas de Omron HBF-516 (BIA) superan el 40% (fuera del rango de calibracion), el sistema activa automaticamente la extrapolacion lineal
   - Limitado a un maximo de 60% por seguridad (configurable via `MAX_EXTRAPOLATE`)
   - El checkbox de extrapolacion se muestra marcado y deshabilitado cuando se activa automaticamente
   - Se establecen flags de transparencia en `session_state`: `grasa_extrapolada`, `grasa_extrapolada_valor`, `grasa_extrapolada_medido`, `alta_adiposidad`

2. **Calculos PSMF basados en LBM para alta adiposidad**
   - El protocolo PSMF ahora usa masa libre de grasa (LBM) para calcular la proteina en casos de alta adiposidad:
     - Hombres: cuando grasa_corregida >= 35% o IMC >= 30
     - Mujeres: cuando grasa_corregida >= 40% o IMC >= 30
   - Factor de proteina: 1.8 g/kg LBM (configurable via `PROTEIN_FACTOR_PSMF_LBM`)
   - Se mantienen las calorias y multiplicadores existentes
   - Flag `psmf_lbm_based` en `session_state` indica cuando se usa este calculo

3. **Plan Tradicional para casos extremos**
   - En casos de adiposidad extrema (grasa >= 45% o lectura Omron >= 45%), el plan tradicional ahora:
     - Usa proteina basada en LBM con factor 1.6 g/kg LBM (configurable via `PROTEIN_FACTOR_TRAD_LBM`)
     - Garantiza minimos de carbohidratos (50g) y grasas (20g)
     - Limita el deficit al 35% maximo
     - Aplica calorias minimas: 1200 kcal (mujeres) o 1400 kcal (hombres)
   - Flag `trad_protein_lbm_used` en `session_state` indica cuando se usa este calculo
   - Muestra mensaje informativo en UI explicando el ajuste

4. **Mejoras en UI y trazabilidad**
   - Advertencias claras cuando se usa extrapolacion
   - Alerta especial para casos de alta adiposidad
   - Indicadores en reportes cuando se usan calculos basados en LBM
   - Textos sin acentos para evitar problemas de codificacion

#### Configuracion

Nuevas constantes globales (todas configurables):
```python
MAX_EXTRAPOLATE = 60.0                    # Limite de extrapolacion (%)
PROTEIN_FACTOR_PSMF_LBM = 1.8            # Factor proteina PSMF basado en LBM
PROTEIN_FACTOR_TRAD_LBM = 1.6            # Factor proteina plan tradicional basado en LBM
EXTREME_ADIPOSITY_THRESHOLD = 45.0        # Umbral de adiposidad extrema (%)
CARB_MIN_G = 50                           # Carbohidratos minimos (g)
FAT_FLOOR_G = 20                          # Grasas minimas (g)
TEI_MIN_WOMAN = 1200                      # Calorias minimas mujeres
TEI_MIN_MAN = 1400                        # Calorias minimas hombres
MAX_DEFICIT = 0.35                        # Deficit maximo (35%)
```

#### Tests

Se incluye suite de tests completa en `tests/test_conversion.py`:
- Tests de interpolacion Omron (39%, 40%)
- Tests de extrapolacion Omron (43%, 58.5%)
- Tests de calculos PSMF con LBM
- Tests de integracion con casos reales

Para ejecutar tests:
```bash
pip install -r requirements.txt
python -m pytest tests/test_conversion.py -v
```

#### Justificacion Cientifica

- **BIA en alta adiposidad:** Los dispositivos BIA como Omron tienen limitaciones en precision para porcentajes de grasa >40%. La extrapolacion lineal es menos fiable pero proporciona una estimacion cuando no hay alternativas mejores disponibles.
- **Proteina basada en LBM:** En casos de alta adiposidad, calcular la proteina basada en masa libre de grasa (en lugar de peso total) optimiza la retencion muscular durante la perdida de peso, siguiendo protocolos establecidos para PSMF y dietas hipocaloricas.
- **Limites de seguridad:** Los pisos de calorias y macronutrientes garantizan que incluso en casos extremos, la dieta permanece dentro de rangos seguros y sostenibles.

---

## ETA Block - Efecto Termico de los Alimentos

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

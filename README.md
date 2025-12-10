# MUPAI
DIGITAL TRAINING SCIENCE

## Novedades: Auto-extrapolacion Omron y Calculos basados en LBM

### Auto-extrapolacion Omron

La aplicacion ahora maneja automaticamente lecturas Omron de alta adiposidad con un sistema de umbrales:

- **Medido ≤ 40%**: Interpolacion lineal normal (sin cambios)
- **40% < medido < 45%**: Truncamiento al valor maximo de la tabla (Omron=40) con advertencia
  - El usuario puede activar manualmente la extrapolacion mediante checkbox
- **Medido ≥ 45%**: Extrapolacion automatica determinista
  - Usa slope = 1.0 %DEXA por unidad Omron
  - Limitado por MAX_EXTRAPOLATE = 60.0%
  - Activa automaticamente allow_extrapolate=True para transparencia

### Calculos basados en LBM (Lean Body Mass)

#### PSMF (Protein Sparing Modified Fast)
Los calculos de PSMF ahora usan LBM en lugar de peso total para mejor preservacion muscular:
- **< 25% grasa**: 1.8g/kg LBM
- **≥ 25% grasa**: 1.6g/kg LBM

#### Plan Tradicional
Para casos extremos de alta adiposidad (≥35% grasa corporal), el plan tradicional usa LBM:
- **< 35% grasa**: Factores tradicionales basados en peso total
- **≥ 35% grasa**: 1.6g/kg LBM para mejor precision

### Trazabilidad
Todas las extrapolaciones y calculos especiales se registran en session_state:
- `grasa_extrapolada`: Indica si se uso extrapolacion
- `alta_adiposidad`: True para medido ≥ 45%
- `grasa_truncada`: True para medido en rango 40-45% sin extrapolacion manual

### Tests
Ejecutar tests con:
```bash
python tests/test_omron_extrapolation.py
```

---

## ETA Block - Efecto Termico de los Alimentos

El bloque ETA es un modulo completo que calcula el Efecto Termico de los Alimentos basado en composicion corporal y sexo.

### Caracteristicas principales:

- **Calculo cientifico**: Utiliza formulas validadas y factores diferenciados por sexo y composicion corporal
- **Modular**: Completamente independiente y reutilizable
- **Visual**: Incluye componentes visuales con tarjetas informativas
- **Validacion**: Sistema de validacion integrado
- **Session State**: Actualiza automaticamente el estado de sesion

### Funciones principales:

- `calcular_eta_automatico()`: Funcion principal de calculo del ETA
- `mostrar_bloque_eta()`: Funcion visual completa para el paso 5
- `validate_step_5()`: Validacion del paso
- `recalcular_eta()`: Recalculo con nuevos parametros

### Uso:

```python
from eta_block import mostrar_bloque_eta, calcular_eta_automatico

# Mostrar el bloque completo en Streamlit
is_valid = mostrar_bloque_eta()

# O calcular ETA directamente
eta = calcular_eta_automatico(tmb=1700, geaf=1.25, porcentaje_grasa=15, sexo="Hombre")
```

### Integracion:

El bloque se integra perfectamente en el flujo principal de la aplicacion MUPAI, reemplazando el codigo original del paso 5 con una implementacion modular y reutilizable.

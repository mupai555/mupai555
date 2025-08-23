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

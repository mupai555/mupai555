# Quick Reference: Omron Auto-extrapolacion y LBM

## Para desarrolladores

### Ejecutar tests
```bash
./tests/run_all_tests.sh
```

### Tests individuales
```bash
python tests/test_omron_extrapolation.py      # 11 tests de extrapolacion
python tests/test_session_state_integration.py # 4 tests de session state
python tests/test_full_workflow.py             # 4 escenarios completos
```

### Verificar sintaxis
```bash
python -m py_compile streamlit_app.py
```

## Umbrales Omron

| Rango | Comportamiento | Flags |
|-------|---------------|-------|
| ≤40% | Interpolacion normal | `grasa_extrapolada=False` |
| 40-45% | Truncar (o extrapolar si checkbox activo) | `grasa_truncada=True` |
| ≥45% | Extrapolacion automatica | `alta_adiposidad=True`, `allow_extrapolate=True` |

## Formulas de proteina

### PSMF (siempre usa LBM)
```python
if grasa_corregida < 25:
    proteina = LBM × 1.8  # g/kg LBM
else:
    proteina = LBM × 1.6  # g/kg LBM
```

### Plan tradicional
```python
if grasa_corregida >= 35:
    proteina = LBM × 1.6  # Casos extremos
else:
    # Usar peso total con factores variables
    if grasa < 10:
        proteina = peso × 2.2
    elif grasa < 15:
        proteina = peso × 2.0
    elif grasa < 25:
        proteina = peso × 1.8
    else:
        proteina = peso × 1.6
```

## Variables de session_state

### Extrapolacion Omron
- `grasa_extrapolada`: bool - True si se uso extrapolacion
- `grasa_extrapolada_valor`: float - Valor DEXA extrapolado
- `grasa_extrapolada_medido`: float - Valor Omron original
- `alta_adiposidad`: bool - True si medido ≥ 45%
- `grasa_truncada`: bool - True si truncado en zona 40-45%
- `grasa_truncada_medido`: float - Valor Omron truncado
- `allow_extrapolate`: bool - Permite extrapolacion manual

## Ejemplos rapidos

### Caso 1: Normal (25% Omron, Hombre, 80kg)
```
Grasa corregida: 27.3% DEXA (interpolado)
LBM: 58.2 kg
PSMF proteina: 93.1g (1.6g/kg LBM)
Plan tradicional: 144g (1.8g/kg peso total)
```

### Caso 2: Truncamiento (42% Omron, Hombre, 100kg, sin checkbox)
```
Grasa corregida: 45.3% DEXA (truncado a Omron=40)
LBM: 54.7 kg
PSMF proteina: 87.5g (1.6g/kg LBM)
Plan tradicional: 87.5g (1.6g/kg LBM, usa LBM por ≥35%)
```

### Caso 3: Alta adiposidad (50% Omron, Hombre, 110kg)
```
Grasa corregida: 55.3% DEXA (extrapolado auto)
LBM: 49.2 kg
PSMF proteina: 78.7g (1.6g/kg LBM)
Plan tradicional: 78.7g (1.6g/kg LBM, usa LBM por ≥35%)
```

## Archivos modificados

### Core
- `streamlit_app.py`: Logica principal actualizada

### Tests
- `tests/test_omron_extrapolation.py`: Tests de extrapolacion
- `tests/test_session_state_integration.py`: Tests de session state
- `tests/test_full_workflow.py`: Escenarios completos
- `tests/run_all_tests.sh`: Ejecutor de tests

### Documentacion
- `README.md`: Overview de features
- `CHANGELOG_OMRON_LBM.md`: Documentacion detallada
- `QUICK_REFERENCE.md`: Esta guia rapida

## Constantes importantes

```python
MAX_EXTRAPOLATE = 60.0  # Limite maximo de extrapolacion
SLOPE = 1.0             # Pendiente de extrapolacion (1.0 %DEXA / unidad Omron)
ZONA_TRANSICION = (40, 45)  # Rango de truncamiento
UMBRAL_LBM_TRADICIONAL = 35.0  # % grasa para usar LBM en plan tradicional
```

## Mensajes de UI

### Truncamiento
```
⚠️ Valor truncado: El valor medido de Omron (X%) esta en la zona de 
transicion (40-45%). Se ha truncado al valor maximo de la tabla.
```

### Extrapolacion automatica
```
ℹ️ Extrapolacion automatica aplicada: El valor medido de Omron (X%) 
esta en rango de alta adiposidad (>=45%). Valor corregido: Y% (limitado a max 60%).
```

### Plan con LBM
```
💪 Nota: Por tu % de grasa corporal (X% >= 35%), la proteina se calculo 
usando LBM (Y kg) en lugar de peso total para mejor preservacion muscular.
```

## Troubleshooting

### Test failures
1. Verificar que numpy esta instalado: `pip install numpy`
2. Verificar sintaxis: `python -m py_compile streamlit_app.py`
3. Ejecutar tests individuales para identificar fallo

### UI no muestra mensajes correctos
1. Verificar session_state variables en streamlit_app.py
2. Revisar flags en corregir_porcentaje_grasa()
3. Verificar condicionales en seccion de UI (lineas 2038-2065)

### Calculos incorrectos
1. Verificar LBM = peso × (1 - grasa_corregida/100)
2. Para PSMF: siempre usa LBM
3. Para tradicional: verifica umbral ≥35% para usar LBM

## Para mas informacion

- Ver `CHANGELOG_OMRON_LBM.md` para detalles tecnicos completos
- Ver tests para ejemplos de uso
- Ver `README.md` para overview general

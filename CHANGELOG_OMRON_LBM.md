# Changelog: Auto-extrapolacion Omron y Calculos basados en LBM

## Resumen de cambios

Este documento detalla los cambios implementados para mejorar el manejo de lecturas Omron de alta adiposidad y la precision de los calculos nutricionales mediante el uso de LBM (Lean Body Mass / Masa Libre de Grasa).

## 1. Auto-extrapolacion Omron con sistema de umbrales

### Problema original
- Las lecturas Omron >40% se truncaban al valor maximo de la tabla
- No habia diferenciacion entre casos moderados y casos de alta adiposidad
- Faltaba transparencia sobre cuando se aplicaba extrapolacion

### Solucion implementada

Se implemento un sistema de umbrales con tres zonas:

#### Zona 1: Rango normal (medido ≤ 40%)
- **Comportamiento**: Interpolacion lineal normal usando la tabla de calibracion
- **Sin cambios**: Mantiene el comportamiento original
- **Flags**: `grasa_extrapolada=False`, `alta_adiposidad=False`

#### Zona 2: Zona de transicion (40% < medido < 45%)
- **Comportamiento por defecto**: Truncamiento al valor maximo de tabla (Omron=40)
- **Comportamiento opcional**: Extrapolacion manual si usuario activa checkbox
- **Mensaje UI**: Advertencia de truncamiento con sugerencia de activar extrapolacion
- **Flags**: `grasa_truncada=True`, `grasa_truncada_medido=valor`

#### Zona 3: Alta adiposidad (medido ≥ 45%)
- **Comportamiento**: Extrapolacion automatica determinista SIEMPRE
- **Formula**: `result = base_at_40 + slope * (medido - 40)`
  - `slope = 1.0` (%DEXA por unidad Omron)
  - `base_at_40` = valor DEXA correspondiente a Omron=40
- **Limite**: Capped en `MAX_EXTRAPOLATE = 60.0%`
- **Auto-activacion**: Setea `allow_extrapolate=True` automaticamente
- **Flags**: `grasa_extrapolada=True`, `alta_adiposidad=True`, `allow_extrapolate=True`
- **Mensaje UI**: Info sobre extrapolacion automatica aplicada

### Trazabilidad en session_state

Nuevas variables para seguimiento:
```python
'grasa_extrapolada': bool        # True si se uso extrapolacion
'grasa_extrapolada_valor': float # Valor DEXA extrapolado
'grasa_extrapolada_medido': float # Valor Omron original
'alta_adiposidad': bool          # True si medido >= 45%
'grasa_truncada': bool           # True si se trunco en zona 40-45
'grasa_truncada_medido': float   # Valor Omron truncado
```

## 2. Calculos PSMF basados en LBM

### Problema original
- PSMF usaba peso total para calcular proteina
- En personas con alta adiposidad, esto resultaba en proteina excesiva
- No optimizaba la preservacion de masa muscular

### Solucion implementada

Se modifico `calculate_psmf()` para usar LBM en lugar de peso total:

#### Antes (peso total)
```python
if grasa_corregida < 25:
    proteina_g_dia = peso * 1.8  # g/kg peso total
else:
    proteina_g_dia = peso * 1.6  # g/kg peso total
```

#### Despues (LBM)
```python
if grasa_corregida < 25:
    proteina_g_dia = mlg * 1.8  # g/kg LBM
else:
    proteina_g_dia = mlg * 1.6  # g/kg LBM
```

### Ejemplo practico

**Persona con alta adiposidad:**
- Peso: 110 kg
- Grasa: 50% (Omron extrapolado a 55.3% DEXA)
- LBM: 49.2 kg

**Antes (peso total):**
- Proteina = 110 × 1.6 = 176g/dia
- Ratio por LBM = 176/49.2 = 3.58g/kg LBM (excesivo)

**Despues (LBM):**
- Proteina = 49.2 × 1.6 = 78.7g/dia
- Ratio por peso total = 78.7/110 = 0.72g/kg
- Ratio por LBM = 78.7/49.2 = 1.60g/kg LBM (optimo)

### Beneficios
1. **Precision**: Proteina ajustada a la masa que realmente la necesita
2. **Sostenibilidad**: Cantidades mas realistas y alcanzables
3. **Preservacion muscular**: Ratio optimo por kg de tejido magro
4. **Adherencia**: Protocolos menos restrictivos en calorias totales

## 3. Plan tradicional con LBM en casos extremos

### Problema original
- Plan tradicional siempre usaba peso total
- En casos de alta adiposidad (≥35%), esto resultaba en requerimientos irreales

### Solucion implementada

Se agrego logica condicional para usar LBM cuando `grasa_corregida >= 35%`:

```python
usar_lbm = grasa_corregida >= 35.0

if usar_lbm:
    # Casos extremos: usar LBM
    factor_proteina = 1.6
    proteina_g = mlg * factor_proteina
    base_proteina = "LBM"
else:
    # Casos normales: usar peso total
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    proteina_g = peso * factor_proteina
    base_proteina = "peso total"
```

### Umbrales y factores

| % Grasa | Base | Factor | Ejemplo (80kg, 20% grasa) | Ejemplo (100kg, 45% grasa) |
|---------|------|--------|---------------------------|---------------------------|
| < 10%   | Peso | 2.2    | 80 × 2.2 = 176g          | N/A                       |
| < 15%   | Peso | 2.0    | 80 × 2.0 = 160g          | N/A                       |
| < 25%   | Peso | 1.8    | 80 × 1.8 = 144g          | N/A                       |
| < 35%   | Peso | 1.6    | 80 × 1.6 = 128g          | N/A                       |
| ≥ 35%   | LBM  | 1.6    | N/A                       | 54.7 × 1.6 = 87.5g       |

### Notificacion al usuario

Cuando se usa LBM, se muestra un mensaje informativo:
```
💪 Nota: Por tu % de grasa corporal (45.3% >= 35%), 
la proteina se calculo usando LBM (54.7 kg) en lugar de peso total 
para mejor preservacion muscular: 1.6g/kg LBM = 87.5g
```

## 4. Actualizaciones de UI

### Checkbox actualizado
```
"Permitir extrapolacion Omron para valores 40-45% (opcional, menos fiable)"

Help text:
"Para valores 40-45%: permite extrapolar manualmente en lugar de truncar.
Para valores >=45%: la extrapolacion automatica siempre se aplica (alta adiposidad).
La extrapolacion es menos precisa que la interpolacion dentro del rango de la tabla."
```

### Mensajes contextuales

1. **Truncamiento (40-45%, sin extrapolacion manual)**:
   ```
   ⚠️ Valor truncado: El valor medido de Omron (42.0%) esta en la zona de 
   transicion (40-45%). Se ha truncado al valor maximo de la tabla de 
   calibracion (Omron=40, DEXA equivalente=45.3%).
   ```

2. **Extrapolacion automatica (≥45%)**:
   ```
   ℹ️ Extrapolacion automatica aplicada: El valor medido de Omron (50.0%) 
   esta en rango de alta adiposidad (>=45%). Se ha aplicado extrapolacion 
   automatica determinista con pendiente 1.0 %DEXA por unidad Omron. 
   Valor corregido: 55.3% (limitado a max 60%).
   ```

3. **PSMF con LBM**:
   ```
   ⚡ CANDIDATO PARA PROTOCOLO PSMF ACTUALIZADO (basado en LBM)
   🥩 Proteina diaria: 78.7 g/dia (1.60 g/kg LBM, 0.72 g/kg peso total)
   💪 MLG (Masa Libre de Grasa): 49.2 kg
   *Proteina calculada sobre LBM para mejor preservacion muscular*
   ```

## 5. Tests implementados

### test_omron_extrapolation.py (11 tests)
- Interpolacion en rango normal
- Truncamiento zona 40-45
- Extrapolacion manual zona 40-45
- Extrapolacion automatica ≥45
- Cap en MAX_EXTRAPOLATE
- Casos para mujeres
- PSMF con LBM (bajo y alto % grasa)
- Verificacion de otros metodos (InBody, DEXA)

### test_session_state_integration.py (4 tests)
- Session state en rango normal
- Session state con truncamiento
- Session state con extrapolacion manual
- Session state con extrapolacion automatica

### test_full_workflow.py (4 escenarios)
- Escenario normal (25% Omron)
- Escenario truncamiento (42% Omron)
- Escenario alta adiposidad (50% Omron)
- Escenario mujer alta grasa (40% Omron)

**Total: 19 tests, todos pasan ✓**

## 6. Documentacion actualizada

### README.md
- Seccion nueva sobre auto-extrapolacion Omron
- Seccion nueva sobre calculos basados en LBM
- Instrucciones para ejecutar tests

### Este documento (CHANGELOG_OMRON_LBM.md)
- Documentacion detallada de cambios
- Ejemplos practicos
- Tablas comparativas
- Beneficios y justificacion tecnica

## Beneficios generales

1. **Mayor precision cientifica**: Uso de LBM para casos donde es mas apropiado
2. **Mejor experiencia de usuario**: Mensajes claros y contextuales
3. **Transparencia**: Trazabilidad completa via session_state
4. **Sostenibilidad**: Requerimientos nutricionales mas realistas
5. **Adherencia**: Protocolos mas alcanzables para alta adiposidad
6. **Testabilidad**: Suite completa de 19 tests automatizados
7. **Mantenibilidad**: Codigo bien documentado y estructurado

## Compatibilidad

- **Sin cambios breaking**: Comportamiento original se mantiene para casos normales
- **Retrocompatible**: Variables de session_state existentes no se modifican
- **Progresivo**: Nuevas features solo se activan en casos especificos

## Notas tecnicas

### Pendiente de extrapolacion
Se eligio `slope = 1.0` basandose en los ultimos dos puntos de la tabla:
- Omron 39% → DEXA 44.3%
- Omron 40% → DEXA 45.3%
- Diferencia: (45.3 - 44.3) / (40 - 39) = 1.0

### Limite maximo
`MAX_EXTRAPOLATE = 60.0%` se establecio como:
- Limite razonable para BIA
- Proteccion contra valores irreales
- Configurable para ajustes futuros

### Factor LBM tradicional
Se usa `1.6g/kg LBM` para casos extremos (≥35%) porque:
- Es el mismo factor que PSMF para alta grasa
- Consistencia entre protocolos
- Basado en literatura cientifica para preservacion muscular

## Referencias

- Cunningham equation para TMB basado en LBM
- PSMF protocols (Lyle McDonald)
- Protein requirements for lean mass preservation
- Omron-DEXA calibration studies

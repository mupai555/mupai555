import runpy
import json

# Cargar el módulo en un namespace aislado
g = runpy.run_path('../streamlit_app.py')

# Usuario simulado
sexo = 'Hombre'
peso = 80.0
grasa_corregida = 18.0
mlg = 66.0
estatura_cm = 178

# Metabolismo / objetivos
tmb = 1800.0
tdee = 2500.0
deficit = 0.25
ingesta = round(tdee * (1 - deficit), 1)

# Nivel
nivel_entrenamiento = 'intermedio'

results = {}

# Tradicional macros
try:
    trad_macros = g['calcular_macros_tradicional'](ingesta, tmb, sexo, grasa_corregida, peso, mlg)
    results['trad_macros'] = trad_macros
except Exception as e:
    results['trad_macros_error'] = str(e)

# SPEC macros (v2)
try:
    spec_macros = g['calcular_macros_v2'](tmb, tdee, 'cut', deficit, sexo, peso, grasa_corregida, mlg, nivel_entrenamiento, selector_grasa_pct=0.30, activar_ciclaje_4_3=False)
    results['spec_macros'] = spec_macros
except Exception as e:
    results['spec_macros_error'] = str(e)

# Tradicional PSMF
try:
    psmf_trad = g['calculate_psmf'](sexo, peso, grasa_corregida, mlg, estatura_cm)
    results['psmf_trad'] = psmf_trad
except Exception as e:
    results['psmf_trad_error'] = str(e)

# SPEC PSMF v2
try:
    psmf_spec = g['calculate_psmf_v2'](sexo, peso, grasa_corregida, mlg, estatura_cm)
    results['psmf_spec'] = psmf_spec
except Exception as e:
    results['psmf_spec_error'] = str(e)

print(json.dumps(results, indent=2, ensure_ascii=False))

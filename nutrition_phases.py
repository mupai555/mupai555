#!/usr/bin/env python3
"""
Módulo de Fases Nutricionales - nutrition_phases.py

Este módulo implementa todas las reglas de fases nutricionales (Definición, Mantenimiento, 
Volumen, y PSMF) de manera modular y desacoplada de la interfaz de usuario.

El propósito es generar cálculos y estructuras detalladas para enviar reportes por correo,
sin exponer estos detalles explícitamente en la interfaz de Streamlit.

Autor: MUPAI System
Fecha: 2025
Versión: 1.0
"""


def decidir_fase_nutricional(sex, bf_percent, training_level, goal=None):
    """
    Decide la fase nutricional óptima basándose en múltiples factores.
    
    Args:
        sex (str): Sexo del usuario. Valores: 'male' o 'female' (también acepta 'Hombre' o 'Mujer')
        bf_percent (float): Porcentaje de grasa corporal
        training_level (str): Nivel de entrenamiento. Valores: 'novato', 'intermedio', 'avanzado', 'élite'
                              (también acepta 'principiante')
        goal (str, optional): Objetivo del usuario. Valores: 'fat_loss', 'muscle_gain', 'recomp', 'performance'
    
    Returns:
        dict: Diccionario con información de la fase decidida:
            - phase (str): 'cut', 'maintain', 'bulk', o 'psmf'
            - phase_name_es (str): Nombre de la fase en español
            - percentage (float): Porcentaje de déficit (-) o superávit (+)
            - reasoning (str): Explicación de por qué se eligió esta fase
            - is_psmf_candidate (bool): Si el usuario es candidato para PSMF
    
    Lógica de decisión:
        1. PSMF: Solo para personas con grasa corporal alta y objetivo de pérdida
        2. CUT (Definición): Para personas con grasa corporal alta o media-alta
        3. MAINTAIN (Mantenimiento): Para personas en rango óptimo sin objetivo específico
        4. BULK (Volumen): Para personas con grasa corporal baja
    
    Ejemplo:
        >>> result = decidir_fase_nutricional('male', 25.0, 'intermedio', 'fat_loss')
        >>> print(result['phase'])  # 'cut'
        >>> print(result['percentage'])  # -20.0
    """
    # Normalizar entradas
    sex_normalized = _normalize_sex(sex)
    bf_percent = float(bf_percent)
    training_level_normalized = _normalize_training_level(training_level)
    
    # Determinar si es candidato para PSMF
    is_psmf_candidate = _check_psmf_eligibility(sex_normalized, bf_percent, goal)
    
    # Rangos de grasa corporal por sexo
    if sex_normalized == 'male':
        very_low = 6
        low = 10
        optimal_low = 10
        optimal_high = 18
        moderate = 25
    else:  # female
        very_low = 12
        low = 16
        optimal_low = 16
        optimal_high = 23
        moderate = 30
    
    # Decisión de fase
    if is_psmf_candidate and goal == 'fat_loss':
        # PSMF: Protocolo agresivo para pérdida rápida
        phase = 'psmf'
        phase_name_es = 'PSMF (Protein Sparing Modified Fast)'
        percentage = -30.0  # Déficit agresivo
        reasoning = f"Candidato para PSMF: {bf_percent:.1f}% de grasa corporal está por encima del rango saludable. PSMF permite pérdida rápida y efectiva preservando masa muscular."
    
    elif bf_percent < very_low:
        # MUY BAJO - Superávit agresivo recomendado
        phase = 'bulk'
        phase_name_es = 'Volumen (Superávit Agresivo)'
        percentage = 12.5
        reasoning = f"Grasa corporal muy baja ({bf_percent:.1f}%). Se recomienda superávit agresivo (10-15%) para ganar masa muscular y mejorar salud hormonal."
    
    elif bf_percent < low:
        # BAJO - Superávit moderado
        phase = 'bulk'
        phase_name_es = 'Volumen (Superávit Moderado)'
        percentage = 7.5
        reasoning = f"Grasa corporal baja ({bf_percent:.1f}%). Excelente momento para ganar masa muscular con superávit moderado (5-10%)."
    
    elif optimal_low <= bf_percent <= optimal_high:
        # RANGO ÓPTIMO - Depende del objetivo
        if goal == 'fat_loss':
            phase = 'cut'
            phase_name_es = 'Definición (Déficit Moderado)'
            # Déficit basado en subrango
            if sex_normalized == 'male':
                if bf_percent <= 15:
                    percentage = -10.0
                else:
                    percentage = -15.0
            else:  # female
                if bf_percent <= 20:
                    percentage = -10.0
                else:
                    percentage = -15.0
            reasoning = f"En rango óptimo ({bf_percent:.1f}%) con objetivo de pérdida de grasa. Déficit moderado para minimizar pérdida muscular."
        
        elif goal == 'muscle_gain':
            phase = 'bulk'
            phase_name_es = 'Volumen (Superávit Ligero)'
            # Superávit basado en subrango
            if sex_normalized == 'male':
                if bf_percent <= 15:
                    percentage = 7.5
                else:
                    percentage = 5.0
            else:  # female
                if bf_percent <= 20:
                    percentage = 7.5
                else:
                    percentage = 5.0
            reasoning = f"En rango óptimo ({bf_percent:.1f}%) con objetivo de ganancia muscular. Superávit controlado para maximizar músculo y minimizar grasa."
        
        else:  # 'recomp', 'performance', o None
            phase = 'maintain'
            phase_name_es = 'Mantenimiento (Recomposición)'
            # Ligero superávit para recomposición
            if sex_normalized == 'male':
                if bf_percent <= 15:
                    percentage = 2.5
                else:
                    percentage = 0.0
            else:  # female
                if bf_percent <= 20:
                    percentage = 2.5
                else:
                    percentage = 0.0
            reasoning = f"En rango óptimo ({bf_percent:.1f}%). Mantenimiento o ligero superávit para recomposición corporal."
    
    elif bf_percent > optimal_high:
        # SOBREPESO - Déficit
        phase = 'cut'
        phase_name_es = 'Definición (Déficit)'
        
        # Calcular déficit basado en % de grasa
        if sex_normalized == 'male':
            if bf_percent <= 22:
                percentage = -15.0
            elif bf_percent <= 25:
                percentage = -20.0
            elif bf_percent <= 30:
                percentage = -25.0
            else:
                percentage = -30.0
        else:  # female
            if bf_percent <= 27:
                percentage = -15.0
            elif bf_percent <= 30:
                percentage = -20.0
            elif bf_percent <= 35:
                percentage = -25.0
            else:
                percentage = -30.0
        
        reasoning = f"Grasa corporal elevada ({bf_percent:.1f}%). Déficit calórico para reducir grasa y mejorar salud metabólica."
    
    else:
        # Fallback - Mantenimiento
        phase = 'maintain'
        phase_name_es = 'Mantenimiento'
        percentage = 0.0
        reasoning = f"Fase de mantenimiento por defecto para {bf_percent:.1f}% de grasa corporal."
    
    return {
        'phase': phase,
        'phase_name_es': phase_name_es,
        'percentage': percentage,
        'reasoning': reasoning,
        'is_psmf_candidate': is_psmf_candidate,
        'bf_percent': bf_percent,
        'sex': sex_normalized,
        'training_level': training_level_normalized,
        'goal': goal
    }


def calcular_calorias_objetivo(maintenance_calories, phase_info):
    """
    Calcula las calorías objetivo basadas en el mantenimiento y la fase nutricional.
    
    Args:
        maintenance_calories (float): Calorías de mantenimiento (TMB × GEAF × ETA + GEE)
        phase_info (dict): Información de la fase (del resultado de decidir_fase_nutricional)
    
    Returns:
        dict: Diccionario con:
            - target_calories (float): Calorías objetivo
            - deficit_percentage (float): Porcentaje de déficit (solo si phase='cut' o 'psmf')
            - surplus_percentage (float): Porcentaje de superávit (solo si phase='bulk')
            - maintenance_calories (float): Calorías de mantenimiento originales
    
    Fórmulas:
        - Definición: kcal = mantenimiento × (1 + deficit_percentage/100)
        - Mantenimiento: kcal = mantenimiento × (1 + percentage/100)
        - Volumen: kcal = mantenimiento × (1 + surplus_percentage/100)
    
    Ejemplo:
        >>> phase = decidir_fase_nutricional('male', 25.0, 'intermedio', 'fat_loss')
        >>> calorias = calcular_calorias_objetivo(2500, phase)
        >>> print(calorias['target_calories'])  # 2000.0
    """
    maintenance_calories = float(maintenance_calories)
    percentage = phase_info['percentage']
    phase = phase_info['phase']
    
    # Calcular calorías objetivo
    target_calories = maintenance_calories * (1 + percentage / 100)
    
    result = {
        'target_calories': int(round(target_calories)),
        'maintenance_calories': int(round(maintenance_calories)),
        'percentage': percentage,
        'phase': phase
    }
    
    # Agregar información específica según fase
    if phase in ['cut', 'psmf']:
        result['deficit_percentage'] = abs(percentage)
        result['deficit_kcal'] = int(round(maintenance_calories - target_calories))
    elif phase == 'bulk':
        result['surplus_percentage'] = percentage
        result['surplus_kcal'] = int(round(target_calories - maintenance_calories))
    
    return result


def generar_proyecciones(phase_info, current_weight, weeks=4):
    """
    Genera proyecciones de peso para 4-5 semanas con diferentes tasas de cambio.
    
    Args:
        phase_info (dict): Información de la fase (del resultado de decidir_fase_nutricional)
        current_weight (float): Peso actual en kg
        weeks (int): Número de semanas para proyectar (por defecto 4)
    
    Returns:
        dict: Diccionario con proyecciones:
            - weekly_rate_low (float): Tasa semanal baja (% del peso corporal)
            - weekly_rate_mid (float): Tasa semanal media (% del peso corporal)
            - weekly_rate_high (float): Tasa semanal alta (% del peso corporal)
            - weekly_kg_low (float): Cambio semanal bajo en kg
            - weekly_kg_mid (float): Cambio semanal medio en kg
            - weekly_kg_high (float): Cambio semanal alto en kg
            - weights_low (list): Pesos proyectados con tasa baja por semana
            - weights_mid (list): Pesos proyectados con tasa media por semana
            - weights_high (list): Pesos proyectados con tasa alta por semana
            - explanation (str): Explicación de las proyecciones
    
    Lógica de proyección:
        - En Definición: Tasas basadas en % de grasa (0.5%, 0.7%, 1.0%, 1.5% según grasa)
        - En Volumen: Tasas basadas en nivel de entrenamiento (novatos ganan más rápido)
        - En Mantenimiento: Fluctuaciones mínimas (±0.1%)
        - Casos avanzados: Se mantienen cualitativos sin proyecciones numéricas agresivas
    
    Ejemplo:
        >>> phase = decidir_fase_nutricional('male', 25.0, 'intermedio', 'fat_loss')
        >>> proyecciones = generar_proyecciones(phase, 80.0, weeks=4)
        >>> print(proyecciones['weekly_rate_mid'])  # -0.7
    """
    current_weight = float(current_weight)
    phase = phase_info['phase']
    sex = phase_info['sex']
    bf_percent = phase_info['bf_percent']
    training_level = phase_info['training_level']
    
    if phase in ['cut', 'psmf']:
        # DEFINICIÓN: Pérdidas semanales basadas en % de grasa corporal
        if sex == 'male':
            if bf_percent < 12:
                # Muy bajo - pérdida muy conservadora
                rates = [-0.3, -0.5, -0.7]
                explanation = "Grasa corporal baja. Pérdida muy conservadora para preservar masa muscular y salud hormonal."
            elif bf_percent < 18:
                # Rango óptimo - pérdida conservadora
                rates = [-0.5, -0.7, -1.0]
                explanation = "En rango óptimo. Pérdida conservadora y sostenible."
            elif bf_percent < 25:
                # Elevado - pérdida moderada
                rates = [-0.7, -1.0, -1.5]
                explanation = "Grasa elevada. Pérdida moderada es segura y efectiva."
            else:
                # Muy elevado - pérdida más agresiva
                rates = [-1.0, -1.5, -2.0]
                explanation = "Grasa muy elevada. Pérdida más agresiva es segura inicialmente."
        else:  # female
            if bf_percent < 18:
                # Muy bajo - pérdida muy conservadora
                rates = [-0.3, -0.5, -0.7]
                explanation = "Grasa corporal baja. Pérdida muy conservadora para salud hormonal."
            elif bf_percent < 23:
                # Rango óptimo - pérdida conservadora
                rates = [-0.5, -0.7, -1.0]
                explanation = "En rango óptimo. Pérdida conservadora y sostenible."
            elif bf_percent < 30:
                # Elevado - pérdida moderada
                rates = [-0.7, -1.0, -1.5]
                explanation = "Grasa elevada. Pérdida moderada es segura y efectiva."
            else:
                # Muy elevado - pérdida más agresiva
                rates = [-1.0, -1.5, -2.0]
                explanation = "Grasa muy elevada. Pérdida más agresiva es segura inicialmente."
    
    elif phase == 'bulk':
        # VOLUMEN: Ganancia basada en nivel de entrenamiento
        if training_level in ['novato', 'principiante']:
            rates = [0.2, 0.35, 0.5]
            explanation = "Nivel principiante. Mayor potencial de ganancia muscular rápida."
        elif training_level == 'intermedio':
            rates = [0.15, 0.25, 0.4]
            explanation = "Nivel intermedio. Ganancia muscular moderada y sostenible."
        else:  # avanzado, élite
            rates = [0.1, 0.15, 0.25]
            explanation = "Nivel avanzado. Ganancia muscular más lenta y selectiva (enfoque cualitativo)."
    
    else:  # maintain
        # MANTENIMIENTO: Fluctuaciones mínimas
        rates = [-0.1, 0.0, 0.1]
        explanation = "Mantenimiento. Fluctuaciones normales por hidratación y contenido intestinal."
    
    # Calcular kg por semana
    weekly_kg_low = current_weight * (rates[0] / 100)
    weekly_kg_mid = current_weight * (rates[1] / 100)
    weekly_kg_high = current_weight * (rates[2] / 100)
    
    # Generar pesos proyectados por semana
    weights_low = [current_weight]
    weights_mid = [current_weight]
    weights_high = [current_weight]
    
    for week in range(1, weeks + 1):
        weights_low.append(round(weights_low[-1] + weekly_kg_low, 1))
        weights_mid.append(round(weights_mid[-1] + weekly_kg_mid, 1))
        weights_high.append(round(weights_high[-1] + weekly_kg_high, 1))
    
    return {
        'weekly_rate_low': rates[0],
        'weekly_rate_mid': rates[1],
        'weekly_rate_high': rates[2],
        'weekly_kg_low': round(weekly_kg_low, 2),
        'weekly_kg_mid': round(weekly_kg_mid, 2),
        'weekly_kg_high': round(weekly_kg_high, 2),
        'weights_low': weights_low,
        'weights_mid': weights_mid,
        'weights_high': weights_high,
        'total_change_low': round(weights_low[-1] - current_weight, 1),
        'total_change_mid': round(weights_mid[-1] - current_weight, 1),
        'total_change_high': round(weights_high[-1] - current_weight, 1),
        'explanation': explanation,
        'weeks': weeks
    }


def generar_analisis_completo(sex, bf_percent, training_level, goal, maintenance_calories, current_weight, weeks=4):
    """
    Función principal que genera el análisis completo de fases nutricionales.
    
    Esta es la función de más alto nivel que orquesta todo el análisis.
    
    Args:
        sex (str): Sexo del usuario ('male'/'female' o 'Hombre'/'Mujer')
        bf_percent (float): Porcentaje de grasa corporal
        training_level (str): Nivel de entrenamiento
        goal (str): Objetivo del usuario
        maintenance_calories (float): Calorías de mantenimiento
        current_weight (float): Peso actual en kg
        weeks (int): Número de semanas para proyectar (por defecto 4)
    
    Returns:
        dict: Diccionario completo con toda la información:
            - phase_decision: Información de la fase decidida
            - calories: Información de calorías objetivo
            - projections: Proyecciones de peso
            - summary: Resumen ejecutivo
    
    Ejemplo de uso:
        >>> analisis = generar_analisis_completo(
        ...     sex='male',
        ...     bf_percent=20.0,
        ...     training_level='intermedio',
        ...     goal='fat_loss',
        ...     maintenance_calories=2500,
        ...     current_weight=80.0,
        ...     weeks=4
        ... )
        >>> print(analisis['phase_decision']['phase'])  # 'cut'
        >>> print(analisis['calories']['target_calories'])  # 2125.0
    """
    # Paso 1: Decidir fase nutricional
    phase_decision = decidir_fase_nutricional(sex, bf_percent, training_level, goal)
    
    # Paso 2: Calcular calorías objetivo
    calories = calcular_calorias_objetivo(maintenance_calories, phase_decision)
    
    # Paso 3: Generar proyecciones
    projections = generar_proyecciones(phase_decision, current_weight, weeks)
    
    # Paso 4: Crear resumen ejecutivo
    summary = _crear_resumen_ejecutivo(phase_decision, calories, projections, current_weight)
    
    return {
        'phase_decision': phase_decision,
        'calories': calories,
        'projections': projections,
        'summary': summary,
        'metadata': {
            'version': '1.0',
            'module': 'nutrition_phases',
            'generated_for': {
                'sex': sex,
                'bf_percent': bf_percent,
                'training_level': training_level,
                'goal': goal,
                'current_weight': current_weight
            }
        }
    }


# ==================== FUNCIONES AUXILIARES PRIVADAS ====================

def _normalize_sex(sex):
    """Normaliza el valor de sexo a 'male' o 'female'."""
    if sex.lower() in ['male', 'hombre', 'm', 'masculino']:
        return 'male'
    elif sex.lower() in ['female', 'mujer', 'f', 'femenino']:
        return 'female'
    else:
        raise ValueError(f"Valor de sexo no válido: {sex}. Use 'male'/'female' o 'Hombre'/'Mujer'")


def _normalize_training_level(training_level):
    """Normaliza el nivel de entrenamiento."""
    training_level = training_level.lower()
    if training_level in ['novato', 'principiante', 'beginner']:
        return 'novato'
    elif training_level in ['intermedio', 'intermediate']:
        return 'intermedio'
    elif training_level in ['avanzado', 'advanced']:
        return 'avanzado'
    elif training_level in ['élite', 'elite']:
        return 'élite'
    else:
        # Por defecto, intermedio
        return 'intermedio'


def _check_psmf_eligibility(sex, bf_percent, goal):
    """
    Verifica si el usuario es candidato para PSMF.
    
    Criterios PSMF:
        - Hombres: >18% grasa corporal
        - Mujeres: >23% grasa corporal
        - Objetivo: pérdida de grasa
    """
    if goal != 'fat_loss':
        return False
    
    if sex == 'male':
        return bf_percent > 18
    else:  # female
        return bf_percent > 23


def _crear_resumen_ejecutivo(phase_decision, calories, projections, current_weight):
    """Crea un resumen ejecutivo del análisis."""
    phase = phase_decision['phase']
    phase_name = phase_decision['phase_name_es']
    
    summary = f"""
RESUMEN EJECUTIVO - ANÁLISIS DE FASE NUTRICIONAL
================================================

FASE RECOMENDADA: {phase_name}
Tipo: {phase.upper()}

JUSTIFICACIÓN:
{phase_decision['reasoning']}

CALORÍAS:
- Mantenimiento: {calories['maintenance_calories']:.0f} kcal/día
- Objetivo: {calories['target_calories']:.0f} kcal/día
- Diferencia: {calories['target_calories'] - calories['maintenance_calories']:+.0f} kcal/día ({phase_decision['percentage']:+.1f}%)

PROYECCIÓN DE PESO ({projections['weeks']} SEMANAS):
- Peso actual: {current_weight:.1f} kg
- Escenario conservador: {projections['weights_low'][-1]:.1f} kg ({projections['total_change_low']:+.1f} kg)
- Escenario medio: {projections['weights_mid'][-1]:.1f} kg ({projections['total_change_mid']:+.1f} kg)
- Escenario agresivo: {projections['weights_high'][-1]:.1f} kg ({projections['total_change_high']:+.1f} kg)

TASAS SEMANALES:
- Conservadora: {projections['weekly_rate_low']:+.1f}% ({projections['weekly_kg_low']:+.2f} kg/semana)
- Media: {projections['weekly_rate_mid']:+.1f}% ({projections['weekly_kg_mid']:+.2f} kg/semana)
- Agresiva: {projections['weekly_rate_high']:+.1f}% ({projections['weekly_kg_high']:+.2f} kg/semana)

EXPLICACIÓN:
{projections['explanation']}
"""
    
    return summary.strip()


def formatear_para_email(analisis_completo):
    """
    Formatea el análisis completo para incluir en el cuerpo del email.
    
    Args:
        analisis_completo (dict): Resultado de generar_analisis_completo()
    
    Returns:
        str: Texto formateado para el email
    
    Ejemplo:
        >>> analisis = generar_analisis_completo(...)
        >>> texto_email = formatear_para_email(analisis)
        >>> # Incluir texto_email en el cuerpo del correo
    """
    phase = analisis_completo['phase_decision']
    calories = analisis_completo['calories']
    proj = analisis_completo['projections']
    
    texto = f"""
=====================================
ANÁLISIS DE FASE NUTRICIONAL
=====================================
Módulo: Nutrition Phases v1.0
Generado por: MUPAI System

📊 FASE NUTRICIONAL ASIGNADA:
-------------------------------------
Fase: {phase['phase_name_es']}
Tipo técnico: {phase['phase'].upper()}
Porcentaje: {phase['percentage']:+.1f}%

📝 JUSTIFICACIÓN:
{phase['reasoning']}

🔥 CALORÍAS OBJETIVO:
-------------------------------------
- Mantenimiento (TMB × GEAF × ETA + GEE): {calories['maintenance_calories']:.0f} kcal/día
- Objetivo nutricional: {calories['target_calories']:.0f} kcal/día
- Diferencia: {calories['target_calories'] - calories['maintenance_calories']:+.0f} kcal/día
"""
    
    if 'deficit_percentage' in calories:
        texto += f"- Déficit aplicado: {calories['deficit_percentage']:.1f}% ({calories['deficit_kcal']:.0f} kcal)\n"
    elif 'surplus_percentage' in calories:
        texto += f"- Superávit aplicado: {calories['surplus_percentage']:.1f}% ({calories['surplus_kcal']:.0f} kcal)\n"
    
    texto += f"""
📈 PROYECCIONES DE PESO ({proj['weeks']} SEMANAS):
-------------------------------------
Peso inicial: {analisis_completo['metadata']['generated_for']['current_weight']:.1f} kg

ESCENARIO CONSERVADOR:
  • Tasa semanal: {proj['weekly_rate_low']:+.1f}% ({proj['weekly_kg_low']:+.2f} kg/semana)
  • Peso final: {proj['weights_low'][-1]:.1f} kg
  • Cambio total: {proj['total_change_low']:+.1f} kg

ESCENARIO MEDIO (RECOMENDADO):
  • Tasa semanal: {proj['weekly_rate_mid']:+.1f}% ({proj['weekly_kg_mid']:+.2f} kg/semana)
  • Peso final: {proj['weights_mid'][-1]:.1f} kg
  • Cambio total: {proj['total_change_mid']:+.1f} kg

ESCENARIO AGRESIVO:
  • Tasa semanal: {proj['weekly_rate_high']:+.1f}% ({proj['weekly_kg_high']:+.2f} kg/semana)
  • Peso final: {proj['weights_high'][-1]:.1f} kg
  • Cambio total: {proj['total_change_high']:+.1f} kg

📊 PROGRESIÓN SEMANAL (ESCENARIO MEDIO):
"""
    
    for i, weight in enumerate(proj['weights_mid']):
        if i == 0:
            texto += f"  Semana 0 (inicial): {weight:.1f} kg\n"
        else:
            change = weight - proj['weights_mid'][i-1]
            texto += f"  Semana {i}: {weight:.1f} kg ({change:+.1f} kg)\n"
    
    texto += f"""
💡 INTERPRETACIÓN:
-------------------------------------
{proj['explanation']}

⚠️ NOTAS IMPORTANTES:
-------------------------------------
• Las proyecciones son estimaciones basadas en datos científicos y pueden variar según adherencia al plan.
• Se recomienda seguimiento cada 1-2 semanas para ajustar según progreso real.
• Mantener ingesta de proteína alta para preservar masa muscular durante déficit.
• Hidratación adecuada (35-40 ml/kg/día) es crucial para resultados óptimos.
"""
    
    if phase['is_psmf_candidate']:
        texto += """
🔥 CANDIDATO PARA PSMF:
-------------------------------------
• El usuario cumple los criterios para Protein Sparing Modified Fast
• PSMF permite pérdida más rápida preservando masa muscular
• Requiere alta adherencia y supervisión profesional
• Considerar PSMF solo si el usuario está comprometido con el protocolo
"""
    
    texto += """
=====================================
© 2025 MUPAI - Nutrition Phases Module
=====================================
"""
    
    return texto


# ==================== EJEMPLO DE USO ====================

if __name__ == "__main__":
    # Ejemplo de uso del módulo
    print("=" * 60)
    print("EJEMPLO DE USO - Módulo de Fases Nutricionales")
    print("=" * 60)
    print()
    
    # Caso de ejemplo: Hombre, 20% grasa, intermedio, objetivo pérdida
    print("CASO 1: Hombre con 20% grasa, nivel intermedio, objetivo pérdida de grasa")
    print("-" * 60)
    
    analisis1 = generar_analisis_completo(
        sex='male',
        bf_percent=20.0,
        training_level='intermedio',
        goal='fat_loss',
        maintenance_calories=2500,
        current_weight=80.0,
        weeks=4
    )
    
    print(analisis1['summary'])
    print()
    
    # Caso 2: Mujer, 18% grasa, avanzado, objetivo ganancia muscular
    print("=" * 60)
    print("CASO 2: Mujer con 18% grasa, nivel avanzado, objetivo ganancia muscular")
    print("-" * 60)
    
    analisis2 = generar_analisis_completo(
        sex='female',
        bf_percent=18.0,
        training_level='avanzado',
        goal='muscle_gain',
        maintenance_calories=2000,
        current_weight=60.0,
        weeks=5
    )
    
    print(analisis2['summary'])
    print()
    
    # Mostrar formato de email para el primer caso
    print("=" * 60)
    print("FORMATO PARA EMAIL (Caso 1)")
    print("=" * 60)
    print(formatear_para_email(analisis1))

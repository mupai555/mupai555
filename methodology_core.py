"""
MUPAI Methodology Core Module
==============================

⚠️ CONFIDENTIAL - INTELLECTUAL PROPERTY PROTECTION ⚠️

This module contains proprietary calculation logic and methodology that constitutes
the intellectual property of MUPAI/Muscle Up GYM. The specific algorithms, formulas,
thresholds, and classification systems implemented here are protected and should not
be disclosed, copied, or used outside of authorized MUPAI applications.

PROTECTED ELEMENTS:
- Body composition correction algorithms
- FFMI interpretation modes and thresholds
- PSMF tier system and calculations
- Protein, fat, and carbohydrate allocation logic
- Training level classification system
- Metabolic age calculations
- All specific numerical thresholds and factors

This module provides an abstraction layer that hides implementation details while
maintaining full functionality. External code should only call the public interface
functions provided here.

© 2025 MUPAI - All Rights Reserved
"""

# ==================== INTERNAL CONSTANTS (PROTECTED) ====================
# These constants are part of the proprietary methodology

# Omron conversion table (Siedler & Tinsley 2022)
_OMRON_CONVERSION_TABLE = {
    4: 4.6, 5: 5.4, 6: 6.3, 7: 7.1, 8: 7.9, 9: 8.8, 10: 9.6, 11: 10.4,
    12: 11.3, 13: 12.1, 14: 13.0, 15: 13.8, 16: 14.6, 17: 15.5, 18: 16.3,
    19: 17.2, 20: 18.0, 21: 18.8, 22: 19.7, 23: 20.5, 24: 21.3, 25: 22.2,
    26: 23.0, 27: 23.9, 28: 24.7, 29: 25.5, 30: 26.4, 31: 27.2, 32: 28.1,
    33: 28.9, 34: 29.7, 35: 30.6, 36: 31.4, 37: 32.2, 38: 33.1, 39: 33.9,
    40: 34.8, 41: 35.6, 42: 36.4, 43: 37.3, 44: 38.1, 45: 38.9, 46: 39.8,
    47: 40.6, 48: 41.5, 49: 42.3, 50: 43.1, 51: 44.0, 52: 44.8, 53: 45.7,
    54: 46.5, 55: 47.3, 56: 48.2, 57: 49.0, 58: 49.8, 59: 50.7, 60: 51.5,
}

# ==================== PUBLIC INTERFACE FUNCTIONS ====================

def calculate_basal_metabolic_rate(lean_mass_kg):
    """
    Calculate basal metabolic rate using proprietary formula.
    
    Args:
        lean_mass_kg: Lean body mass in kilograms
        
    Returns:
        float: Basal metabolic rate in kcal/day
    """
    try:
        lean_mass = float(lean_mass_kg)
    except (TypeError, ValueError):
        lean_mass = 0.0
    return 370 + (21.6 * lean_mass)


def calculate_lean_mass(weight_kg, body_fat_percent):
    """
    Calculate lean body mass (fat-free mass).
    
    Args:
        weight_kg: Total body weight in kilograms
        body_fat_percent: Body fat percentage
        
    Returns:
        float: Lean body mass in kilograms
    """
    try:
        weight = float(weight_kg)
        bf_pct = float(body_fat_percent)
    except (TypeError, ValueError):
        weight = 0.0
        bf_pct = 0.0
    return weight * (1 - bf_pct / 100)


def correct_body_fat_measurement(measured_value, method, sex):
    """
    Correct body fat percentage based on measurement method.
    Uses proprietary correction factors for different measurement devices.
    
    Args:
        measured_value: Raw measured body fat percentage
        method: Measurement method used
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        float: Corrected body fat percentage (DEXA-equivalent)
    """
    try:
        measured = float(measured_value)
    except (TypeError, ValueError):
        measured = 0.0

    # Apply proprietary correction based on method
    if method == "Omron HBF-516 (BIA)":
        rounded = int(round(measured))
        if rounded < 4 or rounded > 60:
            return measured
        return _OMRON_CONVERSION_TABLE.get(rounded, measured)
    elif method == "InBody 270 (BIA profesional)":
        return measured * 1.02
    elif method == "Bod Pod (Pletismografía)":
        factor = 1.0 if sex == "Mujer" else 1.03
        return measured * factor
    else:  # DEXA or others
        return measured


def calculate_ffmi_normalized(lean_mass_kg, height_cm):
    """
    Calculate Fat-Free Mass Index normalized to 1.80m height.
    Uses proprietary normalization algorithm.
    
    Args:
        lean_mass_kg: Lean body mass in kilograms
        height_cm: Height in centimeters
        
    Returns:
        float: Normalized FFMI value
    """
    try:
        lm = float(lean_mass_kg)
        height_m = float(height_cm) / 100
    except (TypeError, ValueError):
        lm = 0.0
        height_m = 1.80
    
    if height_m <= 0:
        height_m = 1.80
    
    # Proprietary FFMI calculation with normalization
    ffmi_base = lm / (height_m ** 2)
    ffmi_normalized = ffmi_base + 6.3 * (1.8 - height_m)
    
    return ffmi_normalized


def classify_ffmi_level(ffmi_value, sex):
    """
    Classify FFMI level using proprietary classification system.
    
    Args:
        ffmi_value: Calculated FFMI value
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        str: Classification category
    """
    try:
        ffmi = float(ffmi_value)
    except (TypeError, ValueError):
        ffmi = 0.0
    
    # Proprietary classification thresholds
    if sex == "Hombre":
        thresholds = [(18, "Bajo"), (20, "Promedio"), (22, "Bueno"), (25, "Avanzado"), (100, "Élite")]
    else:
        thresholds = [(15, "Bajo"), (17, "Promedio"), (19, "Bueno"), (21, "Avanzado"), (100, "Élite")]
    
    for threshold, classification in thresholds:
        if ffmi < threshold:
            return classification
    
    return "Élite"


def calculate_fat_mass_index(weight_kg, body_fat_corrected, height_cm):
    """
    Calculate Fat Mass Index using proprietary algorithm.
    
    Args:
        weight_kg: Total body weight in kilograms
        body_fat_corrected: Corrected body fat percentage
        height_cm: Height in centimeters
        
    Returns:
        float: Fat Mass Index value
    """
    try:
        weight = float(weight_kg)
        bf_pct = float(body_fat_corrected)
        height_m = float(height_cm) / 100
    except (TypeError, ValueError):
        return 0.0
    
    if height_m <= 0:
        return 0.0
    
    fat_mass = weight * (bf_pct / 100)
    fmi = fat_mass / (height_m ** 2)
    
    return fmi


def determine_ffmi_interpretation_mode(body_fat_corrected, sex):
    """
    Determine FFMI interpretation mode using proprietary system.
    
    Args:
        body_fat_corrected: Corrected body fat percentage
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        str: Interpretation mode ("GREEN", "AMBER", or "RED")
    """
    try:
        bf = float(body_fat_corrected)
    except (TypeError, ValueError):
        return "GREEN"
    
    # Proprietary mode determination logic
    if sex == "Hombre":
        if 11.9 <= bf <= 22.7:
            return "GREEN"
        elif 22.7 < bf <= 26.5:
            return "AMBER"
        else:
            return "RED"
    else:  # Mujer
        if 20.8 <= bf <= 31.0:
            return "GREEN"
        elif 31.0 < bf <= 38.2:
            return "AMBER"
        else:
            return "RED"


def calculate_psmf_protocol(sex, weight_kg, body_fat_corrected, lean_mass_kg, height_cm=None):
    """
    Calculate PSMF protocol parameters using proprietary tier system.
    
    Args:
        sex: Biological sex ("Hombre" or "Mujer")
        weight_kg: Total body weight
        body_fat_corrected: Corrected body fat percentage
        lean_mass_kg: Lean body mass
        height_cm: Height in centimeters (optional)
        
    Returns:
        dict: PSMF parameters or {"psmf_aplicable": False}
    """
    try:
        weight = float(weight_kg)
        bf_pct = float(body_fat_corrected)
        lm = float(lean_mass_kg)
    except (TypeError, ValueError):
        weight = 70.0
        bf_pct = 20.0
        lm = 60.0
    
    # Proprietary eligibility criteria
    if sex == "Hombre" and bf_pct > 18:
        eligible = True
        calorie_floor = 800
    elif sex == "Mujer" and bf_pct > 23:
        eligible = True
        calorie_floor = 700
    else:
        return {"psmf_aplicable": False}
    
    if not eligible:
        return {"psmf_aplicable": False}
    
    # Calculate BMI and ideal weight if height provided
    if height_cm is not None:
        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)
        ideal_weight = 25 * (height_m ** 2)
    else:
        bmi = None
        ideal_weight = None
    
    # Proprietary tier determination
    if (bmi is not None and bmi >= 40) or \
       (sex == "Hombre" and bf_pct >= 35) or \
       (sex == "Mujer" and bf_pct >= 45):
        tier = 3
    elif (sex == "Hombre" and 25 <= bf_pct < 35) or \
         (sex == "Mujer" and 35 <= bf_pct < 45):
        tier = 2
    else:
        tier = 1
    
    # Proprietary base selection
    if tier == 1:
        protein_base = weight
        base_name = "Peso total"
    elif tier == 2:
        protein_base = lm
        base_name = "MLG"
    elif tier == 3:
        protein_base = ideal_weight if ideal_weight is not None else lm
        base_name = "Peso ideal (IMC 25)"
    else:
        protein_base = weight
        base_name = "Peso total"
    
    # Proprietary protein and fat factors
    if bf_pct < 25:
        protein_factor = 1.8
        fat_grams = 30.0
    else:
        protein_factor = 1.6
        fat_grams = 50.0
    
    protein_grams = round(protein_base * protein_factor, 1)
    
    # Proprietary calorie multiplier
    if bf_pct > 35:
        multiplier = 8.3
        profile = "alto % grasa (PSMF tradicional)"
    elif bf_pct >= 25 and sex == "Hombre":
        multiplier = 9.0
        profile = "% grasa moderado"
    elif bf_pct >= 30 and sex == "Mujer":
        multiplier = 9.0
        profile = "% grasa moderado"
    else:
        multiplier = 9.6
        profile = "más magro (abdominales visibles)"
    
    target_calories = round(protein_grams * multiplier, 0)
    
    # Proprietary carb cap by tier
    carb_caps = {1: 50, 2: 40, 3: 30}
    carb_cap = carb_caps.get(tier, 50)
    
    # Calculate carbs with cap
    protein_kcal = 4 * protein_grams
    fat_kcal = 9 * fat_grams
    carbs_calculated = max((target_calories - (protein_kcal + fat_kcal)) / 4, 0)
    
    carbs_final = min(carbs_calculated, carb_cap)
    cap_applied = carbs_calculated > carb_cap
    
    final_calories = protein_kcal + fat_kcal + (4 * carbs_final)
    
    if final_calories < calorie_floor:
        final_calories = calorie_floor
    
    # Proprietary weight loss projections
    if sex == "Hombre":
        loss_min, loss_max = 0.8, 1.2
    else:
        loss_min, loss_max = 0.6, 1.0
    
    return {
        "psmf_aplicable": True,
        "proteina_g_dia": protein_grams,
        "grasa_g_dia": fat_grams,
        "carbs_g_dia": round(carbs_final, 1),
        "calorias_dia": final_calories,
        "calorias_piso_dia": calorie_floor,
        "multiplicador": multiplier,
        "perfil_grasa": profile,
        "perdida_semanal_kg": (loss_min, loss_max),
        "criterio": f"Protocolo con tiers: {profile}",
        "tier_psmf": tier,
        "base_proteina_usada": base_name,
        "base_proteina_kg": round(protein_base, 2),
        "carb_cap_aplicado_g": carb_cap,
        "carb_cap_fue_aplicado": cap_applied,
        "factor_proteina_psmf": protein_factor
    }


def suggest_caloric_deficit(body_fat_percent, sex):
    """
    Suggest caloric deficit using proprietary algorithm.
    
    Args:
        body_fat_percent: Body fat percentage
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        int: Recommended deficit percentage
    """
    try:
        bf_pct = float(body_fat_percent)
    except (TypeError, ValueError):
        bf_pct = 0.0
    
    # Proprietary deficit ranges
    ranges_men = [
        (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
        (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 40, 35), (40.1, 45, 40),
        (45.1, 100, 50)
    ]
    ranges_women = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 40, 30), (40.1, 45, 35), (45.1, 50, 40),
        (50.1, 100, 50)
    ]
    
    table = ranges_men if sex == "Hombre" else ranges_women
    cap = 30
    extra_limit = 30 if sex == "Hombre" else 35
    
    for min_bf, max_bf, deficit in table:
        if min_bf <= bf_pct <= max_bf:
            return min(deficit, cap) if bf_pct <= extra_limit else deficit
    
    return 20  # Default


def determine_nutritional_phase(body_fat_corrected, sex):
    """
    Determine nutritional phase using proprietary logic.
    
    Args:
        body_fat_corrected: Corrected body fat percentage
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        tuple: (phase_description, percentage)
    """
    try:
        bf = float(body_fat_corrected)
    except (TypeError, ValueError):
        bf = 0.0
    
    # Proprietary phase determination
    if sex == "Hombre":
        if bf < 6:
            return "Superávit recomendado: 10-15%", 12.5
        elif bf <= 10:
            return "Superávit recomendado: 5-10%", 7.5
        elif bf <= 15:
            return "Mantenimiento o ligero superávit: 0-5%", 2.5
        elif bf <= 18:
            return "Mantenimiento", 0
        else:
            deficit = suggest_caloric_deficit(bf, sex)
            return f"Déficit recomendado: {deficit}%", -deficit
    else:  # Mujer
        if bf < 12:
            return "Superávit recomendado: 10-15%", 12.5
        elif bf <= 16:
            return "Superávit recomendado: 5-10%", 7.5
        elif bf <= 20:
            return "Mantenimiento o ligero superávit: 0-5%", 2.5
        elif bf <= 23:
            return "Mantenimiento", 0
        else:
            deficit = suggest_caloric_deficit(bf, sex)
            return f"Déficit recomendado: {deficit}%", -deficit


def calculate_metabolic_age(chronological_age, body_fat_percent, sex):
    """
    Calculate metabolic age using proprietary algorithm.
    
    Args:
        chronological_age: Actual age in years
        body_fat_percent: Body fat percentage
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        int: Estimated metabolic age
    """
    try:
        age = float(chronological_age)
        bf_pct = float(body_fat_percent)
    except (TypeError, ValueError):
        age = 18
        bf_pct = 0.0
    
    # Proprietary metabolic age calculation
    ideal_bf = 15 if sex == "Hombre" else 22
    bf_difference = bf_pct - ideal_bf
    age_adjustment = bf_difference * 0.3
    metabolic_age = age + age_adjustment
    
    return max(18, min(80, round(metabolic_age)))


def get_activity_factor(level):
    """
    Get activity factor using proprietary values.
    
    Args:
        level: Activity level
        
    Returns:
        float: Activity factor multiplier
    """
    factors = {
        "Sedentario": 1.00,
        "Moderadamente-activo": 1.11,
        "Activo": 1.25,
        "Muy-activo": 1.45
    }
    return factors.get(level, 1.00)


def is_in_healthy_range(body_fat_percent, sex):
    """
    Determine if body fat is in healthy range using proprietary criteria.
    
    Args:
        body_fat_percent: Body fat percentage
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        bool: True if in healthy range
    """
    try:
        bf = float(body_fat_percent)
    except (TypeError, ValueError):
        return True
    
    if sex == "Hombre":
        return bf <= 25.0
    else:
        return bf <= 32.0


def get_traditional_protein_factor(body_fat_corrected):
    """
    Get protein factor for traditional plan using proprietary logic.
    
    Args:
        body_fat_corrected: Corrected body fat percentage
        
    Returns:
        float: Protein factor in g/kg
    """
    try:
        bf = float(body_fat_corrected)
    except (TypeError, ValueError):
        bf = 20.0
    
    # Proprietary protein factor determination
    if bf < 10:
        return 2.2
    elif bf < 15:
        return 2.0
    elif bf < 25:
        return 1.8
    else:
        return 1.6


def should_use_lean_mass_for_protein(sex, body_fat_corrected):
    """
    Determine if lean mass should be used for protein calculation.
    
    Args:
        sex: Biological sex ("Hombre" or "Mujer")
        body_fat_corrected: Corrected body fat percentage
        
    Returns:
        bool: True if should use lean mass
    """
    try:
        bf = float(body_fat_corrected)
    except (TypeError, ValueError):
        return False
    
    # Proprietary 30/42 rule
    if sex == "Hombre" and bf >= 30:
        return True
    elif sex == "Mujer" and bf >= 42:
        return True
    else:
        return False


def get_traditional_fat_percentage(body_fat_corrected, sex):
    """
    Get fat percentage of BMR for traditional plan.
    
    Args:
        body_fat_corrected: Corrected body fat percentage (unused)
        sex: Biological sex (unused)
        
    Returns:
        float: Fat percentage of BMR (0.40 = 40%)
    """
    # Proprietary logic: always 40% BMR for traditional plan
    return 0.40


def calculate_scientific_projection(sex, body_fat_corrected, training_level, current_weight, deficit_surplus_percent):
    """
    Calculate scientific weight change projection using proprietary algorithm.
    
    Args:
        sex: Biological sex ("Hombre" or "Mujer")
        body_fat_corrected: Corrected body fat percentage
        training_level: Training level ("principiante", "intermedio", "avanzado", "élite")
        current_weight: Current weight in kg
        deficit_surplus_percent: Deficit (-) or surplus (+) percentage
        
    Returns:
        dict: Projection data with ranges and explanations
    """
    try:
        weight = float(current_weight)
        bf = float(body_fat_corrected)
        pct = float(deficit_surplus_percent)
    except (ValueError, TypeError):
        weight = 70.0
        bf = 20.0
        pct = 0.0
    
    # Proprietary projection logic
    if pct < 0:  # Deficit
        if sex == "Hombre":
            if training_level in ["principiante", "intermedio"]:
                range_min, range_max = -1.0, -0.5
            else:
                range_min, range_max = -0.7, -0.3
        else:  # Mujer
            if training_level in ["principiante", "intermedio"]:
                range_min, range_max = -0.8, -0.3
            else:
                range_min, range_max = -0.6, -0.2
        
        kg_min = weight * (range_min / 100)
        kg_max = weight * (range_max / 100)
        explanation = "Pérdida de peso proyectada"
    elif pct > 0:  # Surplus
        if sex == "Hombre":
            if training_level in ["principiante", "intermedio"]:
                range_min, range_max = 0.3, 0.7
            else:
                range_min, range_max = 0.2, 0.5
        else:  # Mujer
            if training_level in ["principiante", "intermedio"]:
                range_min, range_max = 0.2, 0.5
            else:
                range_min, range_max = 0.1, 0.3
        
        kg_min = weight * (range_min / 100)
        kg_max = weight * (range_max / 100)
        explanation = "Ganancia de peso proyectada"
    else:  # Maintenance
        range_min, range_max = 0.0, 0.0
        kg_min, kg_max = 0.0, 0.0
        explanation = "Mantenimiento"
    
    return {
        "rango_semanal_pct": (range_min, range_max),
        "rango_semanal_kg": (kg_min, kg_max),
        "rango_total_6sem_kg": (kg_min * 6, kg_max * 6),
        "explicacion_textual": explanation
    }


def classify_visceral_fat(level):
    """
    Classify visceral fat level using proprietary criteria.
    
    Args:
        level: Visceral fat level (1-59)
        
    Returns:
        str: Classification
    """
    try:
        lvl = int(level)
    except (TypeError, ValueError):
        return "No medido"
    
    # Proprietary classification
    if lvl < 1:
        return "No medido"
    elif 1 <= lvl <= 12:
        return "Saludable"
    elif 13 <= lvl <= 15:
        return "Elevado"
    else:  # >= 16
        return "Alto riesgo"


def classify_muscle_mass(percent, age, sex):
    """
    Classify muscle mass percentage using proprietary criteria.
    
    Args:
        percent: Muscle mass percentage
        age: Age in years
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        str: Classification
    """
    try:
        pct = float(percent)
        age_val = int(age)
    except (TypeError, ValueError):
        return "No medido"
    
    # Proprietary classification logic
    if pct <= 0:
        return "No medido"
    
    # Simplified classification (actual logic is proprietary)
    if sex == "Hombre":
        if pct < 35:
            return "Bajo"
        elif pct < 40:
            return "Normal"
        elif pct < 45:
            return "Bueno"
        else:
            return "Excelente"
    else:  # Mujer
        if pct < 28:
            return "Bajo"
        elif pct < 33:
            return "Normal"
        elif pct < 38:
            return "Bueno"
        else:
            return "Excelente"


def classify_fmi(fmi_value, sex):
    """
    Classify FMI using proprietary ranges.
    
    Args:
        fmi_value: Fat Mass Index value
        sex: Biological sex ("Hombre" or "Mujer")
        
    Returns:
        str: Classification
    """
    try:
        fmi = float(fmi_value)
    except (TypeError, ValueError):
        return "No calculado"
    
    # Proprietary FMI classification
    if sex == "Hombre":
        if fmi < 3:
            return "Bajo"
        elif fmi < 6:
            return "Normal"
        elif fmi < 9:
            return "Elevado"
        else:
            return "Muy elevado"
    else:  # Mujer
        if fmi < 5:
            return "Bajo"
        elif fmi < 9:
            return "Normal"
        elif fmi < 13:
            return "Elevado"
        else:
            return "Muy elevado"

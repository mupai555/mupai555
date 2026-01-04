"""
Nueva Lógica de Cálculo de Macros y Calorías
============================================

Sistema completo de cálculo con:
- BF operacional (sin visual, solo numérico)
- Clasificación por BF (5 categorías)
- Déficit por interpolación lineal (knots)
- Guardrails IR-SE/sueño
- PBM (Protein Base Mass)
- Orden estricto P→F→C
- Ciclaje 4-3 días
- PSMF con factor k dinámico
"""

import math
from typing import Dict, List, Tuple, Optional


# ============================================================================
# 1. BF OPERACIONAL (sin visual)
# ============================================================================

def calcular_bf_operacional(
    bf_corr_pct: Optional[float] = None,
    bf_measured_pct: Optional[float] = None
) -> Tuple[float, str]:
    """
    Calcula el BF operacional para todos los cálculos posteriores.
    
    Args:
        bf_corr_pct: BF corregido (ej: ajustado a DEXA)
        bf_measured_pct: BF medido directo
        
    Returns:
        (bf_operational, confiabilidad)
        confiabilidad: "alta" o "media"
    """
    if bf_corr_pct is not None:
        return float(bf_corr_pct), "alta"
    elif bf_measured_pct is not None:
        return float(bf_measured_pct), "media"
    else:
        raise ValueError("Se requiere al menos un valor de BF (corregido o medido)")


# ============================================================================
# 2. CLASIFICACIÓN POR BF
# ============================================================================

def clasificar_bf(bf_operational: float, sexo: str) -> str:
    """
    Clasifica el BF en una de 5 categorías según sexo.
    
    Hombres:
        Preparación: ≤8%
        Zona triple: 8-15%
        Promedio: 15-21%
        Sobrepeso: 21-26%
        Obesidad: ≥26%
    
    Mujeres:
        Preparación: ≤14%
        Zona triple: 14-24%
        Promedio: 24-33%
        Sobrepeso: 33-39%
        Obesidad: ≥39%
    
    Returns:
        Una de: "preparacion", "zona_triple", "promedio", "sobrepeso", "obesidad"
    """
    if sexo.lower() in ["hombre", "masculino", "male", "m"]:
        if bf_operational <= 8:
            return "preparacion"
        elif bf_operational <= 15:
            return "zona_triple"
        elif bf_operational <= 21:
            return "promedio"
        elif bf_operational < 26:
            return "sobrepeso"
        else:
            return "obesidad"
    else:  # Mujer
        if bf_operational <= 14:
            return "preparacion"
        elif bf_operational <= 24:
            return "zona_triple"
        elif bf_operational <= 33:
            return "promedio"
        elif bf_operational < 39:
            return "sobrepeso"
        else:
            return "obesidad"


def obtener_fases_disponibles(categoria_bf: str) -> List[str]:
    """
    Determina qué fases nutricionales se deben presentar según categoría BF.
    
    Returns:
        Lista de fases: ["cut", "maintenance", "bulk", "psmf"]
    """
    if categoria_bf == "zona_triple":
        return ["cut", "maintenance", "bulk"]
    elif categoria_bf == "promedio":
        return ["cut", "maintenance"]  # bulk solo con excepción
    elif categoria_bf == "sobrepeso":
        return ["cut", "maintenance"]  # maintenance como diet break
    elif categoria_bf == "obesidad":
        return ["cut", "psmf", "maintenance"]  # maintenance como diet break
    elif categoria_bf == "preparacion":
        return ["maintenance", "bulk"]  # típicamente no cut
    else:
        return ["cut", "maintenance"]


# ============================================================================
# 3. DÉFICIT POR INTERPOLACIÓN LINEAL
# ============================================================================

def interpolar_deficit(bf_operational: float, sexo: str) -> float:
    """
    Calcula el % de déficit mediante interpolación lineal entre knots.
    
    Hombres knots: (4,2.5), (8,7.5), (15,25), (21,40), (26,50)
    Mujeres knots: (8,2.5), (14,7.5), (24,25), (33,40), (39,50)
    
    Returns:
        déficit en % (ej: 25.0 para 25%)
    """
    if sexo.lower() in ["hombre", "masculino", "male", "m"]:
        knots = [(4, 2.5), (8, 7.5), (15, 25), (21, 40), (26, 50)]
    else:
        knots = [(8, 2.5), (14, 7.5), (24, 25), (33, 40), (39, 50)]
    
    # Caso extremo inferior
    if bf_operational <= knots[0][0]:
        return knots[0][1]
    
    # Caso extremo superior
    if bf_operational >= knots[-1][0]:
        return 50.0
    
    # Validar bf_operational es número válido (CRÍTICO para evitar NaN)
    if not isinstance(bf_operational, (int, float)):
        raise ValueError(f"bf_operational debe ser número, recibido: {type(bf_operational).__name__}")
    if bf_operational < 0 or bf_operational > 100:
        raise ValueError(f"bf_operational debe estar 0-100%, recibido: {bf_operational}%")
    
    # Interpolación lineal entre knots
    for i in range(len(knots) - 1):
        bf1, def1 = knots[i]
        bf2, def2 = knots[i + 1]
        
        if bf1 <= bf_operational <= bf2:
            # Interpolación lineal: y = y1 + (y2-y1)/(x2-x1) * (x-x1)
            deficit = def1 + (def2 - def1) / (bf2 - bf1) * (bf_operational - bf1)
            return round(deficit, 1)
    
    return 25.0  # Fallback


def aplicar_guardrails_deficit(
    deficit_pct: float,
    ir_se_score: Optional[float] = None,
    sleep_hours: Optional[float] = None
) -> Tuple[float, str]:
    """
    Aplica caps al déficit según recuperación y sueño.
    
    IR-SE ≥ 70: estándar
    IR-SE 50-69: cap 30%
    IR-SE < 50: cap 25%
    sleep_hours < 6: cap 30%
    
    Returns:
        (deficit_ajustado, warning)
    """
    warning = ""
    cap = 100.0  # Sin cap inicialmente
    warnings_list = []
    
    # Check sueño
    if sleep_hours is not None and sleep_hours < 6:
        cap = min(cap, 30.0)
        warnings_list.append("sueño < 6h")
    
    # Check IR-SE
    if ir_se_score is not None:
        if ir_se_score >= 70:
            pass  # Sin cap
        elif ir_se_score >= 50:
            cap = min(cap, 30.0)
            warnings_list.append("IR-SE 50-69")
        else:  # < 50
            cap = min(cap, 25.0)
            warnings_list.append("IR-SE < 50")
    
    deficit_ajustado = min(deficit_pct, cap)
    
    if deficit_ajustado < deficit_pct and warnings_list:
        warning = f"Déficit limitado a {cap}% por: {', '.join(warnings_list)}"
    
    return deficit_ajustado, warning


# ============================================================================
# 4. KCAL OBJETIVO POR FASE
# ============================================================================

def calcular_kcal_cut(
    maintenance_kcal: float,
    bf_operational: float,
    sexo: str,
    ir_se_score: Optional[float] = None,
    sleep_hours: Optional[float] = None
) -> Tuple[int, float, str]:
    """
    Calcula kcal para fase CUT con déficit interpolado y guardrails.
    
    Returns:
        (kcal_avg_cut, deficit_pct_aplicado, warning)
    """
    deficit_pct = interpolar_deficit(bf_operational, sexo)
    deficit_ajustado, warning = aplicar_guardrails_deficit(deficit_pct, ir_se_score, sleep_hours)
    
    kcal_avg_cut = round(maintenance_kcal * (1 - deficit_ajustado / 100))
    
    return kcal_avg_cut, deficit_ajustado, warning


def calcular_kcal_maintenance(maintenance_kcal: float) -> int:
    """
    Calcula kcal para MAINTENANCE (trivial pero por completitud).
    """
    return round(maintenance_kcal)


def calcular_kcal_bulk(
    maintenance_kcal: float,
    training_level: str,
    bf_operational: float,
    sexo: str,
    categoria_bf: str
) -> Tuple[int, float]:
    """
    Calcula kcal para BULK con superávit según nivel de entrenamiento.
    
    NOTA: Valida maintenance_kcal > 0 para evitar cálculos inválidos (CRÍTICO).
    
    Rangos base:
        novato: 5-15%
        intermedio: 2-7%
        avanzado: 1-3%
        elite: 1-3%
    
    Selección determinística:
        En zona triple: BF bajo → parte alta, BF alto → parte baja
        Fuera: mínimo del rango
    
    Returns:
        (kcal_avg_bulk, surplus_pct)
    """
    # Validar maintenance_kcal (CRÍTICO: nunca debe ser 0 o negativo)
    if not isinstance(maintenance_kcal, (int, float)):
        raise ValueError(f"maintenance_kcal debe ser número, recibido: {type(maintenance_kcal).__name__}")
    if maintenance_kcal <= 0:
        raise ValueError(f"maintenance_kcal debe ser > 0, recibido: {maintenance_kcal}")
    
    # Rangos por nivel
    rangos = {
        "novato": (5, 15),
        "principiante": (5, 15),
        "intermedio": (2, 7),
        "avanzado": (1, 3),
        "elite": (1, 3)
    }
    
    nivel = training_level.lower()
    if nivel not in rangos:
        nivel = "intermedio"  # default
    
    min_surplus, max_surplus = rangos[nivel]
    
    # Selección determinística
    if categoria_bf == "zona_triple":
        # Determinar si BF es "bajo" o "alto" dentro de zona triple
        if sexo.lower() in ["hombre", "masculino", "male", "m"]:
            # Zona triple: 8-15%
            bf_medio = 11.5
        else:
            # Zona triple: 14-24%
            bf_medio = 19.0
        
        if bf_operational <= bf_medio:
            # BF bajo → parte alta del rango
            surplus_pct = max_surplus
        else:
            # BF alto → parte baja del rango
            surplus_pct = min_surplus
    else:
        # Fuera de zona triple: usar mínimo
        surplus_pct = min_surplus
    
    kcal_avg_bulk = round(maintenance_kcal * (1 + surplus_pct / 100))
    
    return kcal_avg_bulk, surplus_pct


# ============================================================================
# 5. PBM (PROTEIN BASE MASS)
# ============================================================================

def calcular_pbm(weight_kg: float, bf_operational: float, sexo: str) -> Tuple[float, str]:
    """
    Calcula Protein Base Mass para no sobre-penalizar BF alto.
    
    Umbral overweight:
        Hombre: 20%
        Mujer: 30%
    
    Si BF ≤ umbral: PBM = peso total
    Si BF > umbral: PBM = FFM / (1 - umbral)
    
    NOTA: Valida weight_kg > 0 para evitar FFM inválido (CRÍTICO).
    
    Returns:
        (pbm_kg, base_usada)
    """
    # Validar weight_kg (CRÍTICO: nunca debe ser ≤ 0)
    if not isinstance(weight_kg, (int, float)):
        raise ValueError(f"weight_kg debe ser número, recibido: {type(weight_kg).__name__}")
    if weight_kg <= 0:
        raise ValueError(f"weight_kg debe ser > 0, recibido: {weight_kg}")
    
    bf_decimal = bf_operational / 100
    ffm = weight_kg * (1 - bf_decimal)
    
    if sexo.lower() in ["hombre", "masculino", "male", "m"]:
        umbral = 0.20
    else:
        umbral = 0.30
    
    if bf_decimal <= umbral:
        return weight_kg, "peso_total"
    else:
        # PBM = peso que tendría si tuviera el umbral de BF manteniendo FFM
        pbm = ffm / (1 - umbral)
        return round(pbm, 1), "pbm_ajustado"


# ============================================================================
# 6. MACROS - PROTEÍNA
# ============================================================================

def calcular_proteina(
    weight_kg: float,
    bf_operational: float,
    sexo: str,
    fase: str,
    deficit_pct: float = 0,
    categoria_bf: str = "promedio",
    robustez_explicita: bool = False
) -> Tuple[float, float, str]:
    """
    Calcula proteína según PBM y multiplicadores por fase.
    
    Multiplicadores:
        Maintenance: 1.6 g/kg PBM
        Bulk: 1.6 (o 1.8 si robustez_explicita)
        Cut base: 1.8
        Cut con déficit ≥ 30%: 2.0
        Cut en Preparación: 2.0
    
    Returns:
        (protein_g, multiplicador, base_usada)
    """
    pbm, base_usada = calcular_pbm(weight_kg, bf_operational, sexo)
    
    # Determinar multiplicador
    if fase == "maintenance":
        multiplicador = 1.6
    elif fase == "bulk":
        multiplicador = 1.8 if robustez_explicita else 1.6
    elif fase == "cut":
        if categoria_bf == "preparacion":
            multiplicador = 2.0
        elif deficit_pct >= 30:
            multiplicador = 2.0
        else:
            multiplicador = 1.8
    else:
        multiplicador = 1.8  # default
    
    protein_g = round(pbm * multiplicador, 1)
    
    return protein_g, multiplicador, base_usada


def calcular_proteina_psmf(
    weight_kg: float,
    bf_operational: float,
    sexo: str,
    maxima_retencion: bool = False
) -> Tuple[float, str]:
    """
    Calcula proteína para PSMF.
    
    Si overweight (>20% H, >30% M): 2.3 × FFM
    Si no overweight: 1.8 × peso (o 2.0 si máxima retención)
    
    Returns:
        (protein_g, metodo)
    """
    bf_decimal = bf_operational / 100
    ffm = weight_kg * (1 - bf_decimal)
    
    if sexo.lower() in ["hombre", "masculino", "male", "m"]:
        umbral = 0.20
    else:
        umbral = 0.30
    
    if bf_decimal > umbral:
        # Overweight
        protein_g = round(2.3 * ffm, 1)
        metodo = "2.3_ffm"
    else:
        # No overweight
        multiplicador = 2.0 if maxima_retencion else 1.8
        protein_g = round(multiplicador * weight_kg, 1)
        metodo = f"{multiplicador}_peso"
    
    return protein_g, metodo


# ============================================================================
# 7. MACROS - GRASA
# ============================================================================

def calcular_grasa(
    target_kcal: float,
    fat_pct: float = 0.30,
    prioridad_rendimiento: bool = False,
    preferencia_low_carb: bool = False
) -> Tuple[float, float]:
    """
    Calcula grasa como % de kcal objetivo.
    
    fat_pct solo puede ser: 0.20, 0.30, 0.40
    
    Default: 0.30
    0.20 si prioridad_rendimiento (alta demanda glucógeno)
    0.40 si preferencia_low_carb
    
    Returns:
        (fat_g, fat_pct_usado)
    """
    # Determinar fat_pct
    if preferencia_low_carb:
        fat_pct_final = 0.40
    elif prioridad_rendimiento:
        fat_pct_final = 0.20
    else:
        fat_pct_final = 0.30
    
    # Validar que sea uno de los 3 valores permitidos
    if fat_pct_final not in [0.20, 0.30, 0.40]:
        fat_pct_final = 0.30
    
    fat_g = round((target_kcal * fat_pct_final) / 9, 1)
    
    return fat_g, fat_pct_final


# ============================================================================
# 8. MACROS - CARBOHIDRATOS (RESIDUAL)
# ============================================================================

def calcular_carbohidratos_residual(
    target_kcal: float,
    protein_g: float,
    fat_g: float
) -> Tuple[float, bool]:
    """
    Calcula carbohidratos residuales.
    
    carb_g = (target_kcal - 4*protein - 9*fat) / 4
    
    Returns:
        (carb_g, necesita_ajuste)
        necesita_ajuste=True si carb_g < 0
    """
    kcal_usadas = (4 * protein_g) + (9 * fat_g)
    kcal_restantes = target_kcal - kcal_usadas
    
    carb_g = round(kcal_restantes / 4, 1)
    necesita_ajuste = carb_g < 0
    
    return carb_g, necesita_ajuste


def ajustar_macros_si_carbos_negativos(
    target_kcal: float,
    protein_g: float,
    fat_pct_actual: float
) -> Dict[str, float]:
    """
    Si carbos quedan negativos, baja fat_pct un nivel y recalcula.
    Orden: 0.40 → 0.30 → 0.20
    NUNCA baja proteína.
    
    Returns:
        dict con: protein_g, fat_g, fat_pct, carb_g
    """
    fat_pct_opciones = [0.40, 0.30, 0.20]
    
    # Encontrar índice actual
    try:
        idx_actual = fat_pct_opciones.index(fat_pct_actual)
    except ValueError:
        idx_actual = 1  # Default 0.30
    
    # Intentar niveles más bajos
    for idx in range(idx_actual + 1, len(fat_pct_opciones)):
        fat_pct_nuevo = fat_pct_opciones[idx]
        fat_g = round((target_kcal * fat_pct_nuevo) / 9, 1)
        carb_g, necesita_ajuste = calcular_carbohidratos_residual(target_kcal, protein_g, fat_g)
        
        if not necesita_ajuste:
            return {
                'protein_g': protein_g,
                'fat_g': fat_g,
                'fat_pct': fat_pct_nuevo,
                'carb_g': carb_g
            }
    
    # Si llegamos aquí, usar mínimo posible
    fat_pct_minimo = 0.20
    fat_g = round((target_kcal * fat_pct_minimo) / 9, 1)
    carb_g = max(0, round((target_kcal - 4*protein_g - 9*fat_g) / 4, 1))
    
    return {
        'protein_g': protein_g,
        'fat_g': fat_g,
        'fat_pct': fat_pct_minimo,
        'carb_g': carb_g
    }


# ============================================================================
# 9. PSMF CON FACTOR K
# ============================================================================

def calcular_macros_psmf(
    protein_g: float,
    categoria_bf: str
) -> Dict[str, float]:
    """
    Calcula macros PSMF con factor k dinámico.
    
    Factores k:
        Preparación: 9.7
        Zona triple: 9.0
        Promedio: 8.6
        Sobrepeso/Obesidad: 8.3
    
    Lógica:
        1. kcal_psmf = protein_g * k
        2. kcal_rest = kcal_psmf - 4*protein_g
        3. fat_g = (kcal_rest * 0.70) / 9, clamp 20-60g
        4. carb_g residual
        5. Si carb_g < 0: subir k
        6. Si carb_g > 60: subir fat_share a 0.80, si persiste subir k
    
    Returns:
        dict con: kcal_psmf, protein_g, fat_g, carb_g, k_usado
    """
    # Determinar k inicial
    k_map = {
        "preparacion": 9.7,
        "zona_triple": 9.0,
        "promedio": 8.6,
        "sobrepeso": 8.3,
        "obesidad": 8.3
    }
    
    k_inicial = k_map.get(categoria_bf, 8.6)
    k_opciones = [8.3, 8.6, 9.0, 9.7]  # Orden ascendente
    
    # Encontrar índice de k inicial
    try:
        idx_k = k_opciones.index(k_inicial)
    except ValueError:
        idx_k = 1
    
    fat_share_rest = 0.70
    
    # Intentar con k inicial
    for i in range(idx_k, len(k_opciones)):
        k = k_opciones[i]
        kcal_psmf = round(protein_g * k)
        kcal_rest = kcal_psmf - 4 * protein_g
        
        # Probar con fat_share 0.70
        fat_g_calc = (kcal_rest * 0.70) / 9
        fat_g = max(20, min(60, round(fat_g_calc, 1)))
        
        carb_kcal = kcal_psmf - 4*protein_g - 9*fat_g
        carb_g = round(max(0, carb_kcal / 4), 1)
        
        # Check 1: carbos no negativos
        if carb_g >= 0:
            # Check 2: si carbos > 60, intentar con fat_share 0.80
            if carb_g > 60:
                fat_g_calc2 = (kcal_rest * 0.80) / 9
                fat_g2 = max(20, min(60, round(fat_g_calc2, 1)))
                carb_kcal2 = kcal_psmf - 4*protein_g - 9*fat_g2
                carb_g2 = round(max(0, carb_kcal2 / 4), 1)
                
                if carb_g2 <= 60:
                    # Usar versión con fat_share 0.80
                    return {
                        'kcal_psmf': kcal_psmf,
                        'protein_g': protein_g,
                        'fat_g': fat_g2,
                        'carb_g': carb_g2,
                        'k_usado': k,
                        'fat_share': 0.80
                    }
                # Si persiste > 60, continuar a siguiente k
            else:
                # Todo bien, retornar
                return {
                    'kcal_psmf': kcal_psmf,
                    'protein_g': protein_g,
                    'fat_g': fat_g,
                    'carb_g': carb_g,
                    'k_usado': k,
                    'fat_share': 0.70
                }
    
    # Fallback con k máximo
    k = 9.7
    kcal_psmf = round(protein_g * k)
    kcal_rest = kcal_psmf - 4 * protein_g
    fat_g_calc = (kcal_rest * 0.70) / 9
    fat_g = max(20, min(60, round(fat_g_calc, 1)))
    carb_kcal = kcal_psmf - 4*protein_g - 9*fat_g
    carb_g = max(0, round(carb_kcal / 4, 1))
    
    return {
        'kcal_psmf': kcal_psmf,
        'protein_g': protein_g,
        'fat_g': fat_g,
        'carb_g': carb_g,
        'k_usado': k,
        'fat_share': 0.70
    }


# ============================================================================
# 10. CICLAJE 4-3 DÍAS
# ============================================================================

def calcular_ciclaje_4_3(
    kcal_avg_fase: float,
    maintenance_kcal: float,
    fase: str,
    protein_g: float,
    fat_pct: float = 0.30,
    prioridad_rendimiento: bool = False,
    preferencia_low_carb: bool = False
) -> Dict[str, Dict]:
    """
    Calcula macros para ciclaje semanal 4-3.
    
    LOW: Lun-Jue (4 días)
    HIGH: Vie-Dom (3 días)
    
    Factores LOW:
        cut: 0.8
        maintenance: 0.9
        bulk: 0.95
    
    Caps HIGH:
        cut: ≤ 1.05 * maintenance_kcal
        maintenance: ≤ 1.10 * maintenance_kcal
        bulk: ≤ 1.20 * maintenance_kcal
    
    Proteína constante. Grasa/carbo ajustados por P→F→C.
    
    Returns:
        dict con 'low_days' y 'high_days', cada uno con protein/fat/carb/kcal
    """
    # Factores LOW y caps HIGH por fase
    factores = {
        "cut": (0.8, 1.05),
        "maintenance": (0.9, 1.10),
        "bulk": (0.95, 1.20)
    }
    
    low_factor, high_cap_factor = factores.get(fase, (0.9, 1.10))
    
    budget_week = 7 * kcal_avg_fase
    kcal_low = round(kcal_avg_fase * low_factor)
    kcal_high_calc = round((budget_week - 4 * kcal_low) / 3)
    
    # Aplicar cap
    cap_high = maintenance_kcal * high_cap_factor
    
    if kcal_high_calc > cap_high:
        # Subir kcal_low en pasos de 10 hasta cumplir cap
        while kcal_high_calc > cap_high and kcal_low < kcal_avg_fase:
            kcal_low += 10
            kcal_high_calc = round((budget_week - 4 * kcal_low) / 3)
    
    kcal_high = round(kcal_high_calc)
    
    # Calcular macros para LOW days
    fat_g_low, fat_pct_usado = calcular_grasa(
        kcal_low, fat_pct, prioridad_rendimiento, preferencia_low_carb
    )
    carb_g_low, necesita_ajuste_low = calcular_carbohidratos_residual(
        kcal_low, protein_g, fat_g_low
    )
    
    if necesita_ajuste_low:
        macros_low = ajustar_macros_si_carbos_negativos(kcal_low, protein_g, fat_pct_usado)
    else:
        macros_low = {
            'protein_g': protein_g,
            'fat_g': fat_g_low,
            'fat_pct': fat_pct_usado,
            'carb_g': carb_g_low
        }
    
    # Calcular macros para HIGH days
    fat_g_high, fat_pct_usado_high = calcular_grasa(
        kcal_high, fat_pct, prioridad_rendimiento, preferencia_low_carb
    )
    carb_g_high, necesita_ajuste_high = calcular_carbohidratos_residual(
        kcal_high, protein_g, fat_g_high
    )
    
    if necesita_ajuste_high:
        macros_high = ajustar_macros_si_carbos_negativos(kcal_high, protein_g, fat_pct_usado_high)
    else:
        macros_high = {
            'protein_g': protein_g,
            'fat_g': fat_g_high,
            'fat_pct': fat_pct_usado_high,
            'carb_g': carb_g_high
        }
    
    return {
        'low_days': {
            'kcal': kcal_low,
            'protein_g': macros_low['protein_g'],
            'fat_g': macros_low['fat_g'],
            'carb_g': macros_low['carb_g'],
            'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves']
        },
        'high_days': {
            'kcal': kcal_high,
            'protein_g': macros_high['protein_g'],
            'fat_g': macros_high['fat_g'],
            'carb_g': macros_high['carb_g'],
            'dias': ['Viernes', 'Sábado', 'Domingo']
        }
    }


# ============================================================================
# 11. FUNCIÓN PRINCIPAL - CALCULAR TODO
# ============================================================================

def calcular_plan_nutricional_completo(
    # Datos antropométricos
    weight_kg: float,
    bf_corr_pct: Optional[float] = None,
    bf_measured_pct: Optional[float] = None,
    sexo: str = "Hombre",
    
    # Energético
    maintenance_kcal: float = 2500,
    
    # Training
    training_level: str = "intermedio",
    
    # Recuperación
    ir_se_score: Optional[float] = None,
    sleep_hours: Optional[float] = None,
    
    # Preferencias
    fase_deseada: Optional[str] = None,
    prioridad_rendimiento: bool = False,
    preferencia_low_carb: bool = False,
    robustez_explicita: bool = False,
    maxima_retencion_psmf: bool = False,
    
    # Ciclaje
    activar_ciclaje_4_3: bool = False,
    
    # Fat %
    fat_pct: float = 0.30
) -> Dict:
    """
    Función principal que calcula todo el plan nutricional.
    
    Proceso:
        1. BF operacional
        2. Clasificación BF
        3. Fases disponibles
        4. Calcular kcal para cada fase
        5. Calcular macros P→F→C
        6. Opcional: Ciclaje 4-3
        7. Checks de consistencia
    
    Returns:
        dict completo con todos los resultados
    """
    # 1. BF Operacional
    bf_operational, confiabilidad_bf = calcular_bf_operacional(bf_corr_pct, bf_measured_pct)
    
    # 2. Clasificación
    categoria_bf = clasificar_bf(bf_operational, sexo)
    
    # 3. Fases disponibles
    fases_disponibles = obtener_fases_disponibles(categoria_bf)
    
    # 4 & 5. Calcular cada fase disponible
    resultados = {
        'bf_operational': bf_operational,
        'confiabilidad_bf': confiabilidad_bf,
        'categoria_bf': categoria_bf,
        'fases_disponibles': fases_disponibles,
        'fases': {}
    }
    
    # CUT
    if "cut" in fases_disponibles:
        kcal_cut, deficit_pct, warning_cut = calcular_kcal_cut(
            maintenance_kcal, bf_operational, sexo, ir_se_score, sleep_hours
        )
        
        protein_g_cut, mult_cut, base_cut = calcular_proteina(
            weight_kg, bf_operational, sexo, "cut", deficit_pct, categoria_bf
        )
        
        fat_g_cut, fat_pct_cut = calcular_grasa(
            kcal_cut, fat_pct, prioridad_rendimiento, preferencia_low_carb
        )
        
        carb_g_cut, necesita_ajuste_cut = calcular_carbohidratos_residual(
            kcal_cut, protein_g_cut, fat_g_cut
        )
        
        if necesita_ajuste_cut:
            macros_cut = ajustar_macros_si_carbos_negativos(kcal_cut, protein_g_cut, fat_pct_cut)
        else:
            macros_cut = {
                'protein_g': protein_g_cut,
                'fat_g': fat_g_cut,
                'fat_pct': fat_pct_cut,
                'carb_g': carb_g_cut
            }
        
        resultados['fases']['cut'] = {
            'kcal': kcal_cut,
            'deficit_pct': deficit_pct,
            'warning': warning_cut,
            'macros': macros_cut,
            'multiplicador_proteina': mult_cut,
            'base_proteina': base_cut
        }
        
        # Ciclaje 4-3 para cut
        if activar_ciclaje_4_3:
            ciclaje_cut = calcular_ciclaje_4_3(
                kcal_cut, maintenance_kcal, "cut", protein_g_cut,
                fat_pct, prioridad_rendimiento, preferencia_low_carb
            )
            resultados['fases']['cut']['ciclaje_4_3'] = ciclaje_cut
    
    # MAINTENANCE
    if "maintenance" in fases_disponibles:
        kcal_maint = calcular_kcal_maintenance(maintenance_kcal)
        
        protein_g_maint, mult_maint, base_maint = calcular_proteina(
            weight_kg, bf_operational, sexo, "maintenance", 0, categoria_bf
        )
        
        fat_g_maint, fat_pct_maint = calcular_grasa(
            kcal_maint, fat_pct, prioridad_rendimiento, preferencia_low_carb
        )
        
        carb_g_maint, necesita_ajuste_maint = calcular_carbohidratos_residual(
            kcal_maint, protein_g_maint, fat_g_maint
        )
        
        if necesita_ajuste_maint:
            macros_maint = ajustar_macros_si_carbos_negativos(kcal_maint, protein_g_maint, fat_pct_maint)
        else:
            macros_maint = {
                'protein_g': protein_g_maint,
                'fat_g': fat_g_maint,
                'fat_pct': fat_pct_maint,
                'carb_g': carb_g_maint
            }
        
        resultados['fases']['maintenance'] = {
            'kcal': kcal_maint,
            'macros': macros_maint,
            'multiplicador_proteina': mult_maint,
            'base_proteina': base_maint
        }
        
        if activar_ciclaje_4_3:
            ciclaje_maint = calcular_ciclaje_4_3(
                kcal_maint, maintenance_kcal, "maintenance", protein_g_maint,
                fat_pct, prioridad_rendimiento, preferencia_low_carb
            )
            resultados['fases']['maintenance']['ciclaje_4_3'] = ciclaje_maint
    
    # BULK
    if "bulk" in fases_disponibles:
        kcal_bulk, surplus_pct = calcular_kcal_bulk(
            maintenance_kcal, training_level, bf_operational, sexo, categoria_bf
        )
        
        protein_g_bulk, mult_bulk, base_bulk = calcular_proteina(
            weight_kg, bf_operational, sexo, "bulk", 0, categoria_bf, robustez_explicita
        )
        
        fat_g_bulk, fat_pct_bulk = calcular_grasa(
            kcal_bulk, fat_pct, prioridad_rendimiento, preferencia_low_carb
        )
        
        carb_g_bulk, necesita_ajuste_bulk = calcular_carbohidratos_residual(
            kcal_bulk, protein_g_bulk, fat_g_bulk
        )
        
        if necesita_ajuste_bulk:
            macros_bulk = ajustar_macros_si_carbos_negativos(kcal_bulk, protein_g_bulk, fat_pct_bulk)
        else:
            macros_bulk = {
                'protein_g': protein_g_bulk,
                'fat_g': fat_g_bulk,
                'fat_pct': fat_pct_bulk,
                'carb_g': carb_g_bulk
            }
        
        resultados['fases']['bulk'] = {
            'kcal': kcal_bulk,
            'surplus_pct': surplus_pct,
            'macros': macros_bulk,
            'multiplicador_proteina': mult_bulk,
            'base_proteina': base_bulk
        }
        
        if activar_ciclaje_4_3:
            ciclaje_bulk = calcular_ciclaje_4_3(
                kcal_bulk, maintenance_kcal, "bulk", protein_g_bulk,
                fat_pct, prioridad_rendimiento, preferencia_low_carb
            )
            resultados['fases']['bulk']['ciclaje_4_3'] = ciclaje_bulk
    
    # PSMF
    if "psmf" in fases_disponibles:
        protein_g_psmf, metodo_psmf = calcular_proteina_psmf(
            weight_kg, bf_operational, sexo, maxima_retencion_psmf
        )
        
        macros_psmf = calcular_macros_psmf(protein_g_psmf, categoria_bf)
        
        # Check de guardrails para PSMF
        warning_psmf = ""
        if ir_se_score is not None:
            if ir_se_score < 50:
                warning_psmf = "⚠️ PSMF NO RECOMENDADO: IR-SE < 50 (recuperación muy baja)"
            elif 50 <= ir_se_score < 70:
                warning_psmf = "⚠️ PSMF solo como opción: IR-SE 50-69 (recuperación moderada)"
        
        resultados['fases']['psmf'] = {
            'kcal': macros_psmf['kcal_psmf'],
            'macros': {
                'protein_g': macros_psmf['protein_g'],
                'fat_g': macros_psmf['fat_g'],
                'carb_g': macros_psmf['carb_g'],
                'fat_pct': None  # No aplica en PSMF
            },
            'k_usado': macros_psmf['k_usado'],
            'fat_share': macros_psmf['fat_share'],
            'metodo_proteina': metodo_psmf,
            'warning': warning_psmf
        }
    
    # 7. Checks de consistencia
    resultados['checks'] = verificar_consistencia(resultados)
    
    return resultados


# ============================================================================
# 12. CHECKS DE CONSISTENCIA
# ============================================================================

def verificar_consistencia(resultados: Dict) -> Dict[str, bool]:
    """
    Verifica la consistencia de todos los cálculos.
    
    Checks:
        - Cierre calórico (4P + 9F + 4C ≈ target_kcal)
        - Carbos no negativos
        - High-day caps en ciclaje
    
    Returns:
        dict con resultados de checks
    """
    checks = {
        'cierre_calorico_ok': True,
        'carbos_no_negativos_ok': True,
        'high_day_caps_ok': True,
        'detalles': []
    }
    
    for fase, datos in resultados.get('fases', {}).items():
        if fase == 'psmf':
            continue  # PSMF tiene lógica especial
        
        macros = datos.get('macros', {})
        kcal_target = datos.get('kcal', 0)
        
        # Check cierre calórico
        p = macros.get('protein_g', 0)
        f = macros.get('fat_g', 0)
        c = macros.get('carb_g', 0)
        
        kcal_calculadas = 4*p + 9*f + 4*c
        diferencia = abs(kcal_calculadas - kcal_target)
        
        if diferencia > 10:  # Tolerancia 10 kcal
            checks['cierre_calorico_ok'] = False
            checks['detalles'].append(
                f"{fase}: Diferencia calórica {diferencia:.0f} kcal "
                f"(calculado {kcal_calculadas:.0f} vs target {kcal_target})"
            )
        
        # Check carbos no negativos
        if c < 0:
            checks['carbos_no_negativos_ok'] = False
            checks['detalles'].append(f"{fase}: Carbohidratos negativos ({c}g)")
        
        # Check ciclaje
        if 'ciclaje_4_3' in datos:
            ciclaje = datos['ciclaje_4_3']
            kcal_high = ciclaje['high_days']['kcal']
            maintenance_kcal = resultados.get('maintenance_kcal', 0)
            
            caps = {
                'cut': 1.05,
                'maintenance': 1.10,
                'bulk': 1.20
            }
            
            cap_factor = caps.get(fase, 1.10)
            if kcal_high > maintenance_kcal * cap_factor:
                checks['high_day_caps_ok'] = False
                checks['detalles'].append(
                    f"{fase}: High-day excede cap "
                    f"({kcal_high} > {maintenance_kcal * cap_factor:.0f})"
                )
    
    return checks


# ============================================================================
# 13. MAPEO CATEGORÍAS: INTERNO → CLIENTE
# ============================================================================

def obtener_nombre_cliente(categoria_interna: str, sexo: str = "Hombre") -> Dict[str, str]:
    """
    Convierte categoría interna a nombres amigables para cliente.
    
    Args:
        categoria_interna: "preparacion", "zona_triple", "promedio", "sobrepeso", "obesidad"
        sexo: Para mensajes específicos por género
    
    Returns:
        dict con: nombre_corto, nombre_completo, icono, descripcion
    """
    nombres = {
        "preparacion": {
            "nombre_corto": "Muy Definido",
            "nombre_completo": "Muy Definido / Nivel de Fisicoculturismo",
            "icono": "🏆",
            "descripcion_h": "Estás en nivel de competencia o fisicoculturismo. Tu definición muscular es excepcional.",
            "descripcion_m": "Estás en nivel de competencia. Tu definición muscular es excepcional."
        },
        "zona_triple": {
            "nombre_corto": "Atlético",
            "nombre_completo": "Atlético",
            "icono": "🎯",
            "descripcion_h": "Tu composición corporal es atlética y óptima para rendimiento. Tienes flexibilidad para elegir tu objetivo.",
            "descripcion_m": "Tu composición corporal es atlética y óptima para rendimiento. Tienes flexibilidad para elegir tu objetivo."
        },
        "promedio": {
            "nombre_corto": "Saludable",
            "nombre_completo": "Saludable",
            "icono": "💪",
            "descripcion_h": "Estás en un rango saludable con oportunidad de mejorar tu definición muscular.",
            "descripcion_m": "Estás en un rango saludable con oportunidad de mejorar tu composición corporal."
        },
        "sobrepeso": {
            "nombre_corto": "Sobrepeso",
            "nombre_completo": "Sobrepeso",
            "icono": "⚠️",
            "descripcion_h": "Reducir grasa corporal mejorará significativamente tu salud y rendimiento físico.",
            "descripcion_m": "Reducir grasa corporal mejorará significativamente tu salud y bienestar general."
        },
        "obesidad": {
            "nombre_corto": "Obesidad",
            "nombre_completo": "Obesidad",
            "icono": "🚨",
            "descripcion_h": "Tu salud se beneficiará enormemente de una reducción de grasa corporal supervisada profesionalmente.",
            "descripcion_m": "Tu salud se beneficiará enormemente de una reducción de grasa corporal supervisada profesionalmente."
        }
    }
    
    info = nombres.get(categoria_interna, nombres["promedio"])
    sexo_key = "descripcion_h" if sexo.lower() in ["hombre", "masculino", "male", "m"] else "descripcion_m"
    
    return {
        "nombre_corto": info["nombre_corto"],
        "nombre_completo": info["nombre_completo"],
        "icono": info["icono"],
        "descripcion": info[sexo_key]
    }


def obtener_rangos_bf_categoria(categoria_interna: str, sexo: str = "Hombre") -> str:
    """
    Retorna el rango de BF% para una categoría.
    
    Returns:
        string con el rango (ej: "8-15%")
    """
    if sexo.lower() in ["hombre", "masculino", "male", "m"]:
        rangos = {
            "preparacion": "≤8%",
            "zona_triple": "8-15%",
            "promedio": "15-21%",
            "sobrepeso": "21-26%",
            "obesidad": "≥26%"
        }
    else:
        rangos = {
            "preparacion": "≤14%",
            "zona_triple": "14-24%",
            "promedio": "24-33%",
            "sobrepeso": "33-39%",
            "obesidad": "≥39%"
        }
    
    return rangos.get(categoria_interna, "N/A")


# ============================================================================
# 14. HELPERS PARA VISUALIZACIÓN
# ============================================================================

def formatear_resultado_fase(fase_datos: Dict) -> str:
    """
    Formatea los resultados de una fase para visualización.
    """
    macros = fase_datos.get('macros', {})
    kcal = fase_datos.get('kcal', 0)
    
    output = f"📊 Calorías: {kcal} kcal\n"
    output += f"🥩 Proteína: {macros.get('protein_g', 0)}g ({macros.get('protein_g', 0)*4} kcal)\n"
    output += f"🥑 Grasa: {macros.get('fat_g', 0)}g ({macros.get('fat_g', 0)*9:.0f} kcal)\n"
    output += f"🍞 Carbohidratos: {macros.get('carb_g', 0)}g ({macros.get('carb_g', 0)*4:.0f} kcal)\n"
    
    if 'deficit_pct' in fase_datos:
        output += f"\n📉 Déficit: {fase_datos['deficit_pct']}%\n"
    
    if 'surplus_pct' in fase_datos:
        output += f"\n📈 Superávit: {fase_datos['surplus_pct']}%\n"
    
    if 'warning' in fase_datos and fase_datos['warning']:
        output += f"\n⚠️ {fase_datos['warning']}\n"
    
    if 'ciclaje_4_3' in fase_datos:
        ciclaje = fase_datos['ciclaje_4_3']
        output += f"\n🔄 CICLAJE 4-3 ACTIVADO:\n"
        output += f"  LOW (Lun-Jue): {ciclaje['low_days']['kcal']} kcal\n"
        output += f"    P:{ciclaje['low_days']['protein_g']}g F:{ciclaje['low_days']['fat_g']}g C:{ciclaje['low_days']['carb_g']}g\n"
        output += f"  HIGH (Vie-Dom): {ciclaje['high_days']['kcal']} kcal\n"
        output += f"    P:{ciclaje['high_days']['protein_g']}g F:{ciclaje['high_days']['fat_g']}g C:{ciclaje['high_days']['carb_g']}g\n"
    
    return output


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 70)
    print("EJEMPLO DE USO - Nueva Lógica de Macros")
    print("=" * 70)
    
    resultado = calcular_plan_nutricional_completo(
        weight_kg=80,
        bf_corr_pct=18.0,
        sexo="Hombre",
        maintenance_kcal=2500,
        training_level="intermedio",
        ir_se_score=75,
        sleep_hours=7.5,
        prioridad_rendimiento=False,
        preferencia_low_carb=False,
        activar_ciclaje_4_3=True
    )
    
    print(f"\n🎯 BF Operacional: {resultado['bf_operational']}%")
    print(f"📁 Categoría: {resultado['categoria_bf']}")
    print(f"✅ Fases disponibles: {', '.join(resultado['fases_disponibles'])}")
    
    for fase, datos in resultado['fases'].items():
        print(f"\n{'='*70}")
        print(f"FASE: {fase.upper()}")
        print('='*70)
        print(formatear_resultado_fase(datos))
    
    print("\n" + "="*70)
    print("CHECKS DE CONSISTENCIA")
    print("="*70)
    checks = resultado['checks']
    print(f"✅ Cierre calórico: {checks['cierre_calorico_ok']}")
    print(f"✅ Carbos no negativos: {checks['carbos_no_negativos_ok']}")
    print(f"✅ High-day caps: {checks['high_day_caps_ok']}")
    
    if checks['detalles']:
        print("\n⚠️ Detalles:")
        for detalle in checks['detalles']:
            print(f"  - {detalle}")

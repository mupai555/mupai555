"""
Integración de Nueva Lógica de Macros con Sistema Existente
===========================================================

Este módulo conecta la nueva lógica de macros con los cálculos
energéticos actuales (TMB, GEAF, ETA, GEE).
"""

from typing import Dict, Optional
from nueva_logica_macros import (
    calcular_plan_nutricional_completo,
    calcular_bf_operacional,
    clasificar_bf,
    formatear_resultado_fase
)


# ============================================================================
# FUNCIONES DE INTEGRACIÓN CON SISTEMA ACTUAL
# ============================================================================

def calcular_ge_total(
    tmb: float,
    geaf: float,
    eta: float,
    gee_promedio_dia: float
) -> float:
    """
    Calcula Gasto Energético Total usando la fórmula actual del sistema.
    
    GE = TMB × GEAF × ETA + GEE
    
    Args:
        tmb: Tasa Metabólica Basal (Cunningham)
        geaf: Gasto Energético por Actividad Física (factor)
        eta: Efecto Térmico de Alimentos (factor)
        gee_promedio_dia: Gasto Energético por Ejercicio (kcal/día promedio)
    
    Returns:
        GE total en kcal/día
    """
    ge_total = (tmb * geaf * eta) + gee_promedio_dia
    return ge_total


def preparar_datos_desde_sistema_actual(
    # Datos antropométricos (ya calculados en sistema actual)
    peso_kg: float,
    grasa_corregida: float,  # Ya ajustado a DEXA
    sexo: str,
    mlg: float,
    
    # Datos energéticos (ya calculados)
    tmb: float,
    geaf: float,
    eta: float,
    gee_promedio_dia: float,
    
    # Training (ya recogido)
    nivel_entrenamiento: str,
    dias_fuerza: int,
    
    # Recuperación (ya recogido)
    calidad_suenyo: Optional[float] = None,  # Horas promedio
    nivel_estres: Optional[str] = None,  # "bajo", "moderado", "alto"
    
    # Opcional: IR-SE si lo tienes calculado
    ir_se_score: Optional[float] = None
) -> Dict:
    """
    Prepara todos los datos desde el sistema actual para la nueva lógica.
    
    Esta función actúa como puente entre ambos sistemas.
    
    Returns:
        dict con todos los parámetros listos para calcular_plan_nutricional_completo()
    """
    # 1. Calcular GE (maintenance_kcal)
    maintenance_kcal = calcular_ge_total(tmb, geaf, eta, gee_promedio_dia)
    
    # 2. Estimar IR-SE si no lo tienes (CRÍTICO: garantizar que nunca sea None)
    if ir_se_score is None:
        if calidad_suenyo is not None and nivel_estres is not None:
            ir_se_score = estimar_ir_se_basico(calidad_suenyo, nivel_estres)
        else:
            ir_se_score = 60.0  # Default: recuperación moderada si falta info de sueño/estrés
    
    # 3. Normalizar nivel entrenamiento
    nivel_map = {
        "principiante": "novato",
        "intermedio": "intermedio",
        "avanzado": "avanzado",
        "élite": "elite",
        "elite": "elite"
    }
    training_level = nivel_map.get(nivel_entrenamiento.lower(), "intermedio")
    
    return {
        'weight_kg': peso_kg,
        'bf_corr_pct': grasa_corregida,
        'bf_measured_pct': None,  # Ya tenemos corregido
        'sexo': sexo,
        'maintenance_kcal': maintenance_kcal,
        'training_level': training_level,
        'ir_se_score': ir_se_score,
        'sleep_hours': calidad_suenyo,
        
        # Metadata para tracking
        '_metadata': {
            'tmb': tmb,
            'geaf': geaf,
            'eta': eta,
            'gee_promedio_dia': gee_promedio_dia,
            'mlg': mlg,
            'dias_fuerza': dias_fuerza
        }
    }


def estimar_ir_se_basico(calidad_suenyo: float, nivel_estres: str) -> float:
    """
    Estimación básica de IR-SE (Índice de Recuperación - Sueño y Estrés).
    
    Escala 0-100:
        ≥70: Excelente recuperación
        50-69: Recuperación moderada
        <50: Recuperación baja
    
    Args:
        calidad_suenyo: Horas de sueño promedio (debe ser numérico)
        nivel_estres: "bajo", "moderado", "alto"
    
    Returns:
        IR-SE score (0-100)
    """
    # Validar y convertir calidad_suenyo a float (CRÍTICO: debe ser numérico antes de comparación)
    if calidad_suenyo is None:
        calidad_suenyo = 7.0
    else:
        try:
            calidad_suenyo = float(calidad_suenyo)
        except (TypeError, ValueError):
            calidad_suenyo = 7.0
    
    # Validar nivel_estres como string (CRÍTICO: debe ser string antes de comparación)
    if not nivel_estres or not isinstance(nivel_estres, str):
        nivel_estres = "moderado"
    
    # Base por sueño (0-60 puntos)
    if calidad_suenyo >= 8:
        puntos_suenyo = 60
    elif calidad_suenyo >= 7:
        puntos_suenyo = 50
    elif calidad_suenyo >= 6:
        puntos_suenyo = 35
    else:
        puntos_suenyo = 20
    
    # Ajuste por estrés (0-40 puntos)
    estres_map = {
        "bajo": 40,
        "moderado": 25,
        "alto": 10
    }
    puntos_estres = estres_map.get(nivel_estres.lower(), 25)
    
    ir_se = puntos_suenyo + puntos_estres
    return min(100, max(0, ir_se))


# ============================================================================
# FUNCIÓN PRINCIPAL DE INTEGRACIÓN
# ============================================================================

def calcular_plan_con_sistema_actual(
    # Datos del sistema actual
    peso: float,
    grasa_corregida: float,
    sexo: str,
    mlg: float,
    tmb: float,
    geaf: float,
    eta: float,
    gee_promedio_dia: float,
    nivel_entrenamiento: str,
    dias_fuerza: int,
    
    # Datos de recuperación
    calidad_suenyo: Optional[float] = None,
    nivel_estres: Optional[str] = None,
    ir_se_score: Optional[float] = None,
    
    # Preferencias
    prioridad_rendimiento: bool = False,
    preferencia_low_carb: bool = False,
    robustez_explicita: bool = False,
    activar_ciclaje_4_3: bool = False,
    fat_pct: float = 0.30
) -> Dict:
    """
    Función principal que integra ambos sistemas.
    
    ENTRADA: Todos los datos que ya calculas en streamlit_app.py
    SALIDA: Plan nutricional completo con nueva lógica
    
    Ejemplo de uso en streamlit_app.py:
    ```python
    from integracion_nueva_logica import calcular_plan_con_sistema_actual
    
    # Después de calcular TMB, GEAF, ETA, GEE...
    plan = calcular_plan_con_sistema_actual(
        peso=peso,
        grasa_corregida=grasa_corregida,
        sexo=sexo,
        mlg=mlg,
        tmb=tmb,
        geaf=geaf,
        eta=eta,
        gee_promedio_dia=gee_prom_dia,
        nivel_entrenamiento=nivel_entrenamiento,
        dias_fuerza=dias_fuerza,
        calidad_suenyo=promedio_horas_suenyo,
        nivel_estres=nivel_estres_actual,
        activar_ciclaje_4_3=True
    )
    
    # Acceder a resultados
    if 'cut' in plan['fases']:
        kcal_cut = plan['fases']['cut']['kcal']
        macros_cut = plan['fases']['cut']['macros']
        print(f"CUT: {kcal_cut} kcal")
        print(f"P: {macros_cut['protein_g']}g")
        print(f"F: {macros_cut['fat_g']}g")
        print(f"C: {macros_cut['carb_g']}g")
    ```
    
    Returns:
        dict con plan completo (igual a calcular_plan_nutricional_completo)
    """
    # 1. Preparar datos
    datos = preparar_datos_desde_sistema_actual(
        peso_kg=peso,
        grasa_corregida=grasa_corregida,
        sexo=sexo,
        mlg=mlg,
        tmb=tmb,
        geaf=geaf,
        eta=eta,
        gee_promedio_dia=gee_promedio_dia,
        nivel_entrenamiento=nivel_entrenamiento,
        dias_fuerza=dias_fuerza,
        calidad_suenyo=calidad_suenyo,
        nivel_estres=nivel_estres,
        ir_se_score=ir_se_score
    )
    
    # 2. Calcular plan con nueva lógica
    plan = calcular_plan_nutricional_completo(
        weight_kg=datos['weight_kg'],
        bf_corr_pct=datos['bf_corr_pct'],
        bf_measured_pct=datos['bf_measured_pct'],
        sexo=datos['sexo'],
        maintenance_kcal=datos['maintenance_kcal'],
        training_level=datos['training_level'],
        ir_se_score=datos['ir_se_score'],
        sleep_hours=datos['sleep_hours'],
        prioridad_rendimiento=prioridad_rendimiento,
        preferencia_low_carb=preferencia_low_carb,
        robustez_explicita=robustez_explicita,
        activar_ciclaje_4_3=activar_ciclaje_4_3,
        fat_pct=fat_pct
    )
    
    # 3. Agregar metadata del sistema actual
    plan['metadata_sistema_actual'] = datos['_metadata']
    
    return plan


# ============================================================================
# FUNCIÓN DE COMPATIBILIDAD CON FORMATO ANTIGUO
# ============================================================================

def convertir_a_formato_tradicional(plan_nuevo: Dict, fase: str = "cut") -> Dict:
    """
    Convierte el resultado de la nueva lógica al formato del calcular_macros_tradicional.
    
    Útil para mantener compatibilidad con código existente.
    
    Args:
        plan_nuevo: Output de calcular_plan_nutricional_completo()
        fase: Qué fase extraer ("cut", "maintenance", "bulk", "psmf")
    
    Returns:
        dict en formato antiguo:
        {
            'proteina_g': float,
            'proteina_kcal': float,
            'grasa_g': float,
            'grasa_kcal': float,
            'carbo_g': float,
            'carbo_kcal': float,
            'base_proteina': str,
            'factor_proteina': float
        }
    """
    if fase not in plan_nuevo.get('fases', {}):
        raise ValueError(f"Fase '{fase}' no disponible en el plan calculado")
    
    fase_data = plan_nuevo['fases'][fase]
    macros = fase_data['macros']
    
    return {
        'proteina_g': macros['protein_g'],
        'proteina_kcal': macros['protein_g'] * 4,
        'grasa_g': macros['fat_g'],
        'grasa_kcal': macros['fat_g'] * 9,
        'carbo_g': macros['carb_g'],
        'carbo_kcal': macros['carb_g'] * 4,
        'base_proteina': fase_data.get('base_proteina', 'pbm'),
        'factor_proteina': fase_data.get('multiplicador_proteina', 1.8)
    }


# ============================================================================
# HELPERS PARA UI
# ============================================================================

def obtener_recomendacion_fase(plan: Dict) -> str:
    """
    Determina qué fase recomendar según categoría BF.
    
    Returns:
        "cut", "maintenance", "bulk", o "psmf"
    """
    categoria = plan['categoria_bf']
    
    if categoria == "obesidad":
        return "cut"  # O "psmf" si condiciones son óptimas
    elif categoria == "sobrepeso":
        return "cut"
    elif categoria == "promedio":
        return "cut"  # O "maintenance" si prefiere recomp
    elif categoria == "zona_triple":
        return "cut"  # Usuario elige entre cut/maint/bulk
    elif categoria == "preparacion":
        return "maintenance"  # O "bulk" para ganar
    
    return "cut"


def generar_texto_explicativo_categoria(categoria: str, sexo: str, para_cliente: bool = True) -> str:
    """
    Genera texto explicativo para la categoría BF del usuario.
    
    Args:
        categoria: Categoría interna
        sexo: Sexo del usuario
        para_cliente: Si True usa nombres cliente, si False usa técnicos
    """
    from nueva_logica_macros import obtener_nombre_cliente, obtener_rangos_bf_categoria
    
    if para_cliente:
        # Nombres amigables para cliente
        info = obtener_nombre_cliente(categoria, sexo)
        rango = obtener_rangos_bf_categoria(categoria, sexo)
        
        return f"{info['icono']} **{info['nombre_completo']}** ({rango})\n{info['descripcion']}"
    else:
        # Nombres técnicos para interno
        if sexo.lower() in ["hombre", "masculino", "male", "m"]:
            textos = {
                "preparacion": "🏆 Preparación (≤8% BF): Nivel competitivo. Foco en mantenimiento o ganancia controlada.",
                "zona_triple": "🎯 Zona Triple (8-15% BF): Rango óptimo. Opciones: cut/maintenance/bulk.",
                "promedio": "💪 Promedio (15-21% BF): Enfoque en definición o recomposición.",
                "sobrepeso": "⚠️ Sobrepeso (21-26% BF): Priorizar pérdida de grasa.",
                "obesidad": "🚨 Obesidad (≥26% BF): Pérdida de grasa con supervisión. PSMF disponible."
            }
        else:
            textos = {
                "preparacion": "🏆 Preparación (≤14% BF): Nivel competitivo. Foco en mantenimiento o ganancia controlada.",
                "zona_triple": "🎯 Zona Triple (14-24% BF): Rango óptimo. Opciones: cut/maintenance/bulk.",
                "promedio": "💪 Promedio (24-33% BF): Enfoque en definición o recomposición.",
                "sobrepeso": "⚠️ Sobrepeso (33-39% BF): Priorizar pérdida de grasa.",
                "obesidad": "🚨 Obesidad (≥39% BF): Pérdida de grasa con supervisión. PSMF disponible."
            }
        
        return textos.get(categoria, "Categoría no reconocida")


def formatear_plan_para_ui(plan: Dict, sexo: str = "Hombre", para_cliente: bool = True) -> str:
    """
    Formatea el plan completo para mostrar en la UI de Streamlit.
    
    Args:
        plan: Plan calculado
        sexo: Sexo del usuario
        para_cliente: Si True usa nombres amigables, si False usa técnicos
    """
    output = []
    
    # Header
    output.append("=" * 70)
    output.append("📊 PLAN NUTRICIONAL PERSONALIZADO")
    output.append("=" * 70)
    output.append("")
    
    # Info general
    output.append(f"🎯 BF Operacional: {plan['bf_operational']}% ({plan['confiabilidad_bf']} confiabilidad)")
    
    if para_cliente:
        from nueva_logica_macros import obtener_nombre_cliente
        info_categoria = obtener_nombre_cliente(plan['categoria_bf'], sexo)
        output.append(f"{info_categoria['icono']} Categoría: {info_categoria['nombre_completo']}")
    else:
        output.append(f"📁 Categoría: {plan['categoria_bf'].replace('_', ' ').title()}")
    
    output.append("")
    output.append(generar_texto_explicativo_categoria(plan['categoria_bf'], sexo, para_cliente))
    output.append("")
    output.append(f"✅ Fases disponibles: {', '.join([f.upper() for f in plan['fases_disponibles']])}")
    output.append("")
    
    # Cada fase
    for fase, datos in plan['fases'].items():
        output.append("=" * 70)
        output.append(f"FASE: {fase.upper()}")
        output.append("=" * 70)
        output.append(formatear_resultado_fase(datos))
        output.append("")
    
    # Checks
    if 'checks' in plan:
        output.append("=" * 70)
        output.append("✅ VERIFICACIÓN DE CONSISTENCIA")
        output.append("=" * 70)
        checks = plan['checks']
        output.append(f"{'✅' if checks['cierre_calorico_ok'] else '❌'} Cierre calórico")
        output.append(f"{'✅' if checks['carbos_no_negativos_ok'] else '❌'} Carbos no negativos")
        output.append(f"{'✅' if checks['high_day_caps_ok'] else '❌'} High-day caps")
        
        if checks['detalles']:
            output.append("\n⚠️ Detalles:")
            for detalle in checks['detalles']:
                output.append(f"  - {detalle}")
    
    return "\n".join(output)


# ============================================================================
# EJEMPLO DE USO COMPLETO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("EJEMPLO: INTEGRACIÓN CON SISTEMA ACTUAL")
    print("=" * 70)
    
    # Simular datos que ya tienes calculados en streamlit_app.py
    ejemplo_datos = {
        'peso': 80.0,
        'grasa_corregida': 18.0,
        'sexo': 'Hombre',
        'mlg': 65.6,
        'tmb': 1823,
        'geaf': 1.55,
        'eta': 1.10,
        'gee_promedio_dia': 285,
        'nivel_entrenamiento': 'intermedio',
        'dias_fuerza': 4,
        'calidad_suenyo': 7.5,
        'nivel_estres': 'bajo',
        'activar_ciclaje_4_3': True
    }
    
    # Calcular plan con nueva lógica
    plan = calcular_plan_con_sistema_actual(**ejemplo_datos)
    
    # Mostrar resultado formateado PARA CLIENTE
    print("\n" + "=" * 70)
    print("VERSIÓN PARA CLIENTE")
    print("=" * 70)
    print(formatear_plan_para_ui(plan, sexo='Hombre', para_cliente=True))
    
    # Mostrar resultado formateado TÉCNICO (para ti)
    print("\n" + "=" * 70)
    print("VERSIÓN TÉCNICA (INTERNA)")
    print("=" * 70)
    print(formatear_plan_para_ui(plan, sexo='Hombre', para_cliente=False))
    
    # Ejemplo: Convertir a formato antiguo (compatibilidad)
    print("\n" + "=" * 70)
    print("CONVERSIÓN A FORMATO TRADICIONAL (CUT)")
    print("=" * 70)
    formato_antiguo = convertir_a_formato_tradicional(plan, fase="cut")
    print(f"Proteína: {formato_antiguo['proteina_g']}g ({formato_antiguo['proteina_kcal']} kcal)")
    print(f"Grasa: {formato_antiguo['grasa_g']}g ({formato_antiguo['grasa_kcal']} kcal)")
    print(f"Carbos: {formato_antiguo['carbo_g']}g ({formato_antiguo['carbo_kcal']} kcal)")
    print(f"Base: {formato_antiguo['base_proteina']}")
    print(f"Factor: {formato_antiguo['factor_proteina']} g/kg")


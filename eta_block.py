"""
ETA Block - Efecto Térmico de los Alimentos (Thermal Effect of Food)

Este módulo contiene toda la funcionalidad relacionada con el cálculo del Efecto Térmico 
de los Alimentos (ETA), incluyendo funciones de cálculo, validación y componentes visuales.

Características principales:
- Cálculo científico del ETA basado en composición corporal y sexo
- Validación de datos de entrada
- Interfaz visual con tarjetas informativas
- Actualización del estado de sesión
- Integración lista para el flujo principal de la aplicación
"""

import streamlit as st


def calcular_tmb_cunningham(mlg):
    """
    Calcula el TMB (Tasa Metabólica Basal) usando la fórmula de Cunningham.
    
    Args:
        mlg: Masa Libre de Grasa en kg
        
    Returns:
        float: TMB en kcal/día
    """
    try:
        mlg = float(mlg)
    except (TypeError, ValueError):
        mlg = 0.0
    return 370 + (21.6 * mlg)


def calcular_mlg(peso, porcentaje_grasa):
    """
    Calcula la Masa Libre de Grasa.
    
    Args:
        peso: Peso corporal en kg
        porcentaje_grasa: Porcentaje de grasa corporal
        
    Returns:
        float: Masa Libre de Grasa en kg
    """
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        peso = 0.0
        porcentaje_grasa = 0.0
    return peso * (1 - porcentaje_grasa / 100)


def corregir_porcentaje_grasa(medido, metodo, sexo):
    """
    Corrige el porcentaje de grasa según el método de medición.
    Si el método es Omron, ajusta con tablas especializadas por sexo.
    Si InBody, aplica factor.
    Si BodPod, aplica factor por sexo.
    Si DEXA, devuelve el valor medido.
    
    Args:
        medido: Porcentaje de grasa medido
        metodo: Método de medición utilizado
        sexo: "Hombre" o "Mujer"
        
    Returns:
        float: Porcentaje de grasa corregido
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 20.0
    
    if metodo == "Omron HBF-516 (BIA)":
        # Tabla de conversión para hombres
        if sexo == "Hombre":
            tabla = {
                5: 4.2, 6: 5.2, 7: 6.2, 8: 7.2, 9: 8.2,
                10: 9.7, 11: 10.7, 12: 11.7, 13: 12.7, 14: 13.7,
                15: 15.2, 16: 16.2, 17: 17.2, 18: 18.2, 19: 19.2,
                20: 20.7, 21: 21.7, 22: 22.7, 23: 23.7, 24: 24.7,
                25: 26.2, 26: 27.2, 27: 28.2, 28: 29.2, 29: 30.2,
                30: 31.7, 31: 32.7, 32: 33.7, 33: 34.7, 34: 35.7,
                35: 37.2, 36: 38.2, 37: 39.2, 38: 40.2, 39: 41.2,
                40: 42.2
            }
        else:  # Mujer
            tabla = {
                5: 5.7, 6: 6.7, 7: 7.7, 8: 8.7, 9: 9.7,
                10: 10.2, 11: 11.2, 12: 12.2, 13: 13.2, 14: 14.2,
                15: 15.7, 16: 16.7, 17: 17.7, 18: 18.7, 19: 19.7,
                20: 20.2, 21: 21.2, 22: 22.2, 23: 23.2, 24: 24.2,
                25: 26.7, 26: 27.7, 27: 28.7, 28: 29.7, 29: 30.7,
                30: 33.2, 31: 34.2, 32: 35.2, 33: 36.2, 34: 37.2,
                35: 39.7, 36: 40.7, 37: 41.7, 38: 42.7, 39: 43.7,
                40: 44.7
            }
        
        grasa_redondeada = int(round(medido))
        grasa_redondeada = min(max(grasa_redondeada, 5), 40)
        return tabla.get(grasa_redondeada, medido)
    elif metodo == "InBody 270 (BIA profesional)":
        return medido * 1.02
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return medido * factor
    else:  # DEXA (Gold Standard) u otros
        return medido


def obtener_geaf(nivel):
    """
    Devuelve el factor de actividad física (GEAF) según el nivel.
    
    Args:
        nivel: Nivel de actividad física
        
    Returns:
        float: Factor GEAF
    """
    valores = {
        "Sedentario": 1.00,
        "Moderadamente-activo": 1.11,
        "Activo": 1.25,
        "Muy-activo": 1.45
    }
    return valores.get(nivel, 1.00)


def calcular_eta_automatico(tmb, geaf, porcentaje_grasa, sexo):
    """
    Calcula el Efecto Térmico de los Alimentos (ETA) automáticamente.
    Fórmula científica basada en composición corporal y gasto energético.
    
    Args:
        tmb: Tasa Metabólica Basal (kcal)
        geaf: Factor de Actividad Física
        porcentaje_grasa: Porcentaje de grasa corporal
        sexo: "Hombre" o "Mujer"
    
    Returns:
        float: ETA en kcal/día
    """
    try:
        tmb = float(tmb)
        geaf = float(geaf)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        return 0.0
    
    # Gasto energético base (TMB * GEAF)
    gasto_base = tmb * geaf
    
    # Factor ETA basado en composición corporal y sexo
    # Personas más magras tienen mayor ETA debido a mayor masa muscular
    if sexo == "Hombre":
        if porcentaje_grasa <= 10:
            factor_eta = 0.12  # 12% para hombres muy magros
        elif porcentaje_grasa <= 15:
            factor_eta = 0.11  # 11% para hombres magros
        elif porcentaje_grasa <= 20:
            factor_eta = 0.10  # 10% para hombres normales
        else:
            factor_eta = 0.09  # 9% para hombres con más grasa
    else:  # Mujer
        if porcentaje_grasa <= 16:
            factor_eta = 0.11  # 11% para mujeres muy magras
        elif porcentaje_grasa <= 21:
            factor_eta = 0.10  # 10% para mujeres magras
        elif porcentaje_grasa <= 26:
            factor_eta = 0.09  # 9% para mujeres normales
        else:
            factor_eta = 0.08  # 8% para mujeres con más grasa
    
    # ETA = Factor * Gasto energético base
    eta = gasto_base * factor_eta
    
    return round(eta, 1)


def validate_step_5():
    """
    Valida que el paso 5 (efecto térmico) esté completo.
    
    Returns:
        bool: True si el paso está válido, False en caso contrario
    """
    # ETA se calcula automáticamente, solo necesitamos los datos previos
    peso = st.session_state.get("peso", 0)
    porcentaje_grasa = st.session_state.get("grasa_corporal", 0)
    actividad = st.session_state.get("actividad_diaria", "")
    return peso > 0 and porcentaje_grasa > 0 and len(actividad) > 0


def crear_tarjeta_eta(titulo, contenido, tipo="info"):
    """
    Crea una tarjeta visual para mostrar información del ETA.
    
    Args:
        titulo: Título de la tarjeta
        contenido: Contenido de la tarjeta
        tipo: Tipo de tarjeta (info, success, warning, error)
    """
    color_map = {
        "info": "#17a2b8",
        "success": "#28a745", 
        "warning": "#ffc107",
        "error": "#dc3545"
    }
    color = color_map.get(tipo, "#17a2b8")
    
    st.markdown(f"""
    <div style="
        border-left: 4px solid {color};
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    ">
        <h4 style="color: {color}; margin: 0 0 0.5rem 0;">{titulo}</h4>
        <p style="color: #cccccc; margin: 0;">{contenido}</p>
    </div>
    """, unsafe_allow_html=True)


def mostrar_bloque_eta():
    """
    Función principal que muestra el bloque completo del ETA (Paso 5).
    Incluye toda la lógica visual y de cálculo para el Efecto Térmico de los Alimentos.
    
    Returns:
        bool: True si el paso está válido y completo
    """
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">🍽️ Paso 5: Efecto Térmico de los Alimentos</h1>
        <p class="step-subtitle">Cálculo automático del gasto energético adicional por digestión</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # Obtener datos previos para calcular ETA automáticamente
    peso = st.session_state.get("peso", 0)
    grasa_corporal = st.session_state.get("grasa_corporal", 0)
    metodo_grasa = st.session_state.get("metodo_grasa", "DEXA (Gold Standard)")
    actividad_diaria = st.session_state.get("actividad_diaria", "")
    sexo = st.session_state.get("sexo", "Hombre")
    
    if peso > 0 and grasa_corporal > 0 and actividad_diaria:
        # Calcular valores necesarios
        grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
        mlg = calcular_mlg(peso, grasa_corregida)
        tmb = calcular_tmb_cunningham(mlg)
        geaf = obtener_geaf(actividad_diaria)
        eta_calculado = calcular_eta_automatico(tmb, geaf, grasa_corregida, sexo)
        
        # Mostrar información científica
        st.markdown("### 🧬 Cálculo Científico del ETA")
        st.info("""
        **💡 ¿Qué es el Efecto Térmico de los Alimentos (ETA)?**
        
        Es el aumento temporal del gasto energético después de comer, debido al proceso de digestión, absorción, transporte y metabolismo de los nutrientes. Representa típicamente 8-15% del gasto energético total diario.
        """)
        
        # Mostrar resultados automáticos en tarjetas visuales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🔥 TMB (Cunningham)", 
                f"{tmb:.0f} kcal/día",
                help="Tasa Metabólica Basal calculada con fórmula de Cunningham"
            )
        with col2:
            st.metric(
                "🚶 Factor GEAF", 
                f"{geaf:.2f}",
                help=f"Factor de actividad física: {actividad_diaria}"
            )
        with col3:
            st.metric(
                "🍽️ ETA Calculado", 
                f"{eta_calculado:.0f} kcal/día",
                help="Efecto Térmico de los Alimentos calculado automáticamente"
            )
        
        # Guardar el ETA calculado en session_state
        st.session_state.eta_calculado = eta_calculado
        
        # Explicación del cálculo
        factor_eta = eta_calculado / (tmb * geaf) * 100 if (tmb * geaf) > 0 else 0
        st.markdown(f"""
        **📊 Detalles del cálculo:**
        - **Gasto energético base:** {tmb:.0f} × {geaf:.2f} = {(tmb * geaf):.0f} kcal/día
        - **Factor ETA aplicado:** {factor_eta:.1f}% (basado en composición corporal)
        - **ETA resultante:** {eta_calculado:.0f} kcal/día
        """)
        
        st.success("✅ **ETA calculado automáticamente con base científica**")
        
        # Mostrar tarjetas informativas adicionales
        crear_tarjeta_eta(
            "🔬 Base Científica",
            "El cálculo se basa en la composición corporal específica del usuario. Las personas con mayor masa muscular (menor % grasa) tienen un ETA más alto debido al mayor costo energético del tejido muscular.",
            "info"
        )
        
        crear_tarjeta_eta(
            "⚖️ Factores Considerados",
            f"Sexo: {sexo} | Grasa corporal: {grasa_corregida:.1f}% | Actividad: {actividad_diaria} | Factor aplicado: {factor_eta:.1f}%",
            "success"
        )
        
    else:
        st.warning("⚠️ Completa los pasos anteriores para calcular el ETA automáticamente")
        
        # Mostrar información educativa mientras no hay datos
        crear_tarjeta_eta(
            "📚 ¿Por qué es importante el ETA?",
            "El Efecto Térmico de los Alimentos es un componente clave del gasto energético total diario. Su cálculo preciso permite una estimación más exacta de las necesidades calóricas.",
            "info"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Validar si el paso está completo
    is_step_5_valid = validate_step_5()
    if is_step_5_valid:
        st.markdown('<div class="step-motivation">⚡ ¡Perfecto! Un paso más y terminamos.</div>', unsafe_allow_html=True)
    
    return is_step_5_valid


# Función de conveniencia para obtener el ETA calculado
def obtener_eta_calculado():
    """
    Obtiene el ETA calculado del estado de sesión.
    
    Returns:
        float: ETA calculado en kcal/día, o 0 si no está disponible
    """
    return st.session_state.get("eta_calculado", 0.0)


# Función para recalcular ETA con nuevos parámetros
def recalcular_eta(peso, grasa_corporal, metodo_grasa, actividad_diaria, sexo):
    """
    Recalcula el ETA con nuevos parámetros y actualiza el estado de sesión.
    
    Args:
        peso: Peso corporal en kg
        grasa_corporal: Porcentaje de grasa corporal
        metodo_grasa: Método de medición de grasa
        actividad_diaria: Nivel de actividad diaria
        sexo: "Hombre" o "Mujer"
        
    Returns:
        float: ETA recalculado en kcal/día
    """
    if peso > 0 and grasa_corporal > 0 and actividad_diaria:
        grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
        mlg = calcular_mlg(peso, grasa_corregida)
        tmb = calcular_tmb_cunningham(mlg)
        geaf = obtener_geaf(actividad_diaria)
        eta_calculado = calcular_eta_automatico(tmb, geaf, grasa_corregida, sexo)
        
        # Actualizar el estado de sesión
        st.session_state.eta_calculado = eta_calculado
        
        return eta_calculado
    
    return 0.0
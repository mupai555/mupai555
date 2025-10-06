"""
MUPAI - Wizard de Composición Corporal (Paso 4)
===============================================

Este archivo contiene una implementación completa y funcional del paso 4 del wizard
de evaluación MUPAI, enfocado en la composición corporal y antropometría.

Características principales:
- Formulario visual con todos los campos requeridos
- Validaciones estrictas en tiempo real
- Cálculos automáticos de métricas clave (IMC, FFMI, MLG, % Grasa corregida)
- Visualización clara y entendible de resultados
- Navegación simple del paso
- Comentarios explicativos detallados

Autor: MUPAI System
Fecha: 2024
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import re

# ==================== CONFIGURACIÓN DE PÁGINA ====================
st.set_page_config(
    page_title="MUPAI - Composición Corporal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
:root {
    --mupai-yellow: #F4C430;
    --mupai-dark-yellow: #DAA520;
    --mupai-black: #181A1B;
    --mupai-gray: #232425;
    --mupai-light-gray: #EDEDED;
    --mupai-white: #FFFFFF;
    --mupai-success: #27AE60;
    --mupai-warning: #F39C12;
    --mupai-danger: #E74C3C;
    --mupai-info: #3498DB;
}

/* Contenedor principal con fondo */
.main-container {
    background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    border: 2px solid var(--mupai-yellow);
}

/* Tarjetas informativas */
.content-card {
    background: linear-gradient(135deg, #2C2C2C 0%, #3A3A3A 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid var(--mupai-yellow);
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}

.content-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.content-card h3 {
    color: var(--mupai-yellow);
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.content-card div {
    color: #F5F5F5;
    line-height: 1.5;
}

/* Métricas destacadas */
.metric-card {
    background: linear-gradient(135deg, #2C2C2C 0%, #3A3A3A 100%);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    border: 2px solid var(--mupai-success);
    margin: 0.5rem 0;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--mupai-yellow);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 1rem;
    color: #F5F5F5;
    margin-bottom: 0.25rem;
}

.metric-help {
    font-size: 0.8rem;
    color: #B0B0B0;
    font-style: italic;
}

/* Indicadores de validación */
.validation-success {
    color: var(--mupai-success);
    font-weight: bold;
}

.validation-error {
    color: var(--mupai-danger);
    font-weight: bold;
}

.validation-warning {
    color: var(--mupai-warning);
    font-weight: bold;
}

/* Botones de navegación */
.nav-button {
    padding: 0.75rem 2rem;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-button-primary {
    background: var(--mupai-yellow);
    color: var(--mupai-black);
}

.nav-button-secondary {
    background: var(--mupai-gray);
    color: var(--mupai-white);
}

/* Progreso del paso */
.step-progress {
    background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    border: 2px solid var(--mupai-info);
}

.step-title {
    color: var(--mupai-yellow);
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.step-description {
    color: #F5F5F5;
    line-height: 1.5;
}

/* Alertas personalizadas */
.alert-success {
    background: rgba(39, 174, 96, 0.1);
    border: 1px solid var(--mupai-success);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.alert-warning {
    background: rgba(243, 156, 18, 0.1);
    border: 1px solid var(--mupai-warning);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.alert-error {
    background: rgba(231, 76, 60, 0.1);
    border: 1px solid var(--mupai-danger);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES AUXILIARES ====================

def safe_float(value, default=0.0):
    """
    Convierte un valor a float de forma segura.
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si la conversión falla
        
    Returns:
        float: Valor convertido o valor por defecto
    """
    try:
        if value == '' or value is None:
            return float(default)
        return float(value)
    except (ValueError, TypeError):
        return float(default)

def safe_int(value, default=0):
    """
    Convierte un valor a int de forma segura.
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si la conversión falla
        
    Returns:
        int: Valor convertido o valor por defecto
    """
    try:
        if value == '' or value is None:
            return int(default)
        return int(value)
    except (ValueError, TypeError):
        return int(default)

def crear_tarjeta(titulo, contenido, tipo="info"):
    """
    Crea una tarjeta visual informativa.
    
    Args:
        titulo: Título de la tarjeta
        contenido: Contenido descriptivo
        tipo: Tipo de tarjeta (info, success, warning, danger)
        
    Returns:
        str: HTML de la tarjeta
    """
    colores = {
        "info": "var(--mupai-info)",
        "success": "var(--mupai-success)",
        "warning": "var(--mupai-warning)",
        "danger": "var(--mupai-danger)"
    }
    color = colores.get(tipo, "var(--mupai-info)")
    return f"""
    <div class="content-card" style="border-left-color: {color};">
        <h3>{titulo}</h3>
        <div>{contenido}</div>
    </div>
    """

def calcular_imc(peso, estatura_cm):
    """
    Calcula el Índice de Masa Corporal (IMC).
    
    Args:
        peso: Peso en kg
        estatura_cm: Estatura en centímetros
        
    Returns:
        float: IMC calculado
    """
    try:
        peso = float(peso)
        estatura_m = float(estatura_cm) / 100
        if estatura_m <= 0:
            return 0.0
        return peso / (estatura_m ** 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0

def calcular_mlg(peso, porcentaje_grasa):
    """
    Calcula la Masa Libre de Grasa (MLG).
    
    Args:
        peso: Peso corporal en kg
        porcentaje_grasa: Porcentaje de grasa corporal
        
    Returns:
        float: Masa Libre de Grasa en kg
    """
    try:
        peso = float(peso)
        porcentaje_grasa = float(porcentaje_grasa)
        return peso * (1 - porcentaje_grasa / 100)
    except (TypeError, ValueError):
        return 0.0

def calcular_ffmi(mlg, estatura_cm):
    """
    Calcula el FFMI (Fat Free Mass Index) y lo normaliza a 1.80m.
    
    Args:
        mlg: Masa Libre de Grasa en kg
        estatura_cm: Estatura en centímetros
        
    Returns:
        float: FFMI normalizado
    """
    try:
        mlg = float(mlg)
        estatura_m = float(estatura_cm) / 100
        if estatura_m <= 0:
            estatura_m = 1.80
        ffmi = mlg / (estatura_m ** 2)
        # Normalización a 1.80m de estatura
        ffmi_normalizado = ffmi + 6.3 * (1.8 - estatura_m)
        return ffmi_normalizado
    except (TypeError, ValueError):
        return 0.0

def corregir_grasa_corporal(medido, metodo, sexo):
    """
    Corrige el porcentaje de grasa según el método de medición para equivalencia DEXA.
    
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
    
    # Factores de corrección basados en estudios científicos
    if "Omron" in metodo:
        # BIA básica tiende a subestimar
        factor = 1.5 if sexo == "Hombre" else 2.0
        return medido + factor
    elif "InBody" in metodo:
        # BIA profesional más precisa
        factor = 1.0 if sexo == "Hombre" else 1.2
        return medido + factor
    elif "Bod Pod" in metodo:
        # Pletismografía tiende a sobreestimar ligeramente
        factor = -0.5 if sexo == "Hombre" else -0.3
        return medido + factor
    else:  # DEXA (Gold Standard)
        return medido

def clasificar_imc(imc):
    """
    Clasifica el IMC según estándares médicos.
    
    Args:
        imc: Índice de Masa Corporal
        
    Returns:
        tuple: (clasificación, color_css)
    """
    if imc < 18.5:
        return "Bajo peso", "var(--mupai-info)"
    elif imc < 25:
        return "Normal", "var(--mupai-success)"
    elif imc < 30:
        return "Sobrepeso", "var(--mupai-warning)"
    else:
        return "Obesidad", "var(--mupai-danger)"

def clasificar_ffmi(ffmi, sexo):
    """
    Clasifica el FFMI según sexo y estándares deportivos.
    
    Args:
        ffmi: Fat Free Mass Index
        sexo: "Hombre" o "Mujer"
        
    Returns:
        tuple: (clasificación, color_css)
    """
    if sexo == "Hombre":
        if ffmi < 18:
            return "Bajo", "var(--mupai-danger)"
        elif ffmi < 20:
            return "Promedio", "var(--mupai-warning)"
        elif ffmi < 22:
            return "Bueno", "var(--mupai-info)"
        elif ffmi < 25:
            return "Avanzado", "var(--mupai-success)"
        else:
            return "Élite", "var(--mupai-yellow)"
    else:  # Mujer
        if ffmi < 15:
            return "Bajo", "var(--mupai-danger)"
        elif ffmi < 17:
            return "Promedio", "var(--mupai-warning)"
        elif ffmi < 19:
            return "Bueno", "var(--mupai-info)"
        elif ffmi < 21:
            return "Avanzado", "var(--mupai-success)"
        else:
            return "Élite", "var(--mupai-yellow)"

def validar_peso(peso):
    """
    Valida el campo de peso corporal.
    
    Args:
        peso: Peso a validar
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    try:
        peso_float = float(peso)
        if peso_float <= 0:
            return False, "El peso debe ser mayor a 0 kg"
        if peso_float < 30:
            return False, "El peso debe ser mayor a 30 kg"
        if peso_float > 200:
            return False, "El peso debe ser menor a 200 kg"
        return True, ""
    except (TypeError, ValueError):
        return False, "El peso debe ser un número válido"

def validar_estatura(estatura):
    """
    Valida el campo de estatura.
    
    Args:
        estatura: Estatura a validar
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    try:
        estatura_int = int(estatura)
        if estatura_int <= 0:
            return False, "La estatura debe ser mayor a 0 cm"
        if estatura_int < 120:
            return False, "La estatura debe ser mayor a 120 cm"
        if estatura_int > 220:
            return False, "La estatura debe ser menor a 220 cm"
        return True, ""
    except (TypeError, ValueError):
        return False, "La estatura debe ser un número entero válido"

def validar_grasa_corporal(grasa):
    """
    Valida el campo de porcentaje de grasa corporal.
    
    Args:
        grasa: Porcentaje de grasa a validar
        
    Returns:
        tuple: (es_válido, mensaje_error)
    """
    try:
        grasa_float = float(grasa)
        if grasa_float <= 0:
            return False, "El porcentaje de grasa debe ser mayor a 0%"
        if grasa_float < 3:
            return False, "El porcentaje de grasa debe ser mayor a 3%"
        if grasa_float > 60:
            return False, "El porcentaje de grasa debe ser menor a 60%"
        return True, ""
    except (TypeError, ValueError):
        return False, "El porcentaje de grasa debe ser un número válido"

# ==================== INICIALIZACIÓN DE ESTADO ====================

# Inicializar variables de sesión si no existen
if 'paso_completado' not in st.session_state:
    st.session_state.paso_completado = False

if 'datos_guardados' not in st.session_state:
    st.session_state.datos_guardados = False

if 'sexo' not in st.session_state:
    st.session_state.sexo = "Hombre"

# ==================== INTERFAZ PRINCIPAL ====================

def main():
    """
    Función principal que renderiza la interfaz del wizard de composición corporal.
    """
    
    # Título principal
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="color: var(--mupai-yellow); text-align: center;">🧙‍♂️ MUPAI - Wizard de Evaluación</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Progreso del paso
    st.markdown("""
    <div class="step-progress">
        <div class="step-title">📊 Paso 4 de 7: Composición Corporal y Antropometría</div>
        <div class="step-description">
            Medición precisa de tu composición corporal para cálculos metabólicos exactos.
            Todos los campos son obligatorios para continuar.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tarjetas informativas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(crear_tarjeta(
            "📊 Composición Corporal",
            "Medición precisa de tu masa magra, grasa corporal y distribución de tejidos para cálculos metabólicos exactos.",
            "info"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(crear_tarjeta(
            "🔬 Métodos Científicos",
            "Utilizamos correcciones validadas según el método de medición para obtener valores equivalentes al estándar DEXA.",
            "success"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(crear_tarjeta(
            "⚡ Precisión TMB",
            "Los datos antropométricos permiten calcular tu tasa metabólica basal con la fórmula de Cunningham (más precisa).",
            "warning"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulario principal
    st.markdown("### 📋 Datos Antropométricos")
    st.markdown("**Importante:** Completa todos los campos para habilitar los cálculos automáticos.")
    
    # Campo de sexo biológico (necesario para cálculos)
    sexo = st.selectbox(
        "🚻 Sexo biológico",
        ["Hombre", "Mujer"],
        index=0 if st.session_state.sexo == "Hombre" else 1,
        help="Necesario para aplicar correcciones específicas por sexo en los cálculos"
    )
    st.session_state.sexo = sexo
    
    # Campos principales en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Campo Peso
        peso_default = 70.0
        peso = st.number_input(
            "⚖️ Peso corporal (kg)",
            min_value=30.0,
            max_value=200.0,
            value=peso_default,
            step=0.1,
            help="Peso en ayunas, sin ropa, por la mañana"
        )
        
        # Validación en tiempo real del peso
        peso_valido, peso_error = validar_peso(peso)
        if not peso_valido:
            st.markdown(f'<div class="validation-error">⚠️ {peso_error}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="validation-success">✅ Peso válido</div>', unsafe_allow_html=True)
    
    with col2:
        # Campo Estatura
        estatura_default = 170
        estatura = st.number_input(
            "📏 Estatura (cm)",
            min_value=120,
            max_value=220,
            value=estatura_default,
            step=1,
            help="Medida sin zapatos, en posición erguida"
        )
        
        # Validación en tiempo real de la estatura
        estatura_valida, estatura_error = validar_estatura(estatura)
        if not estatura_valida:
            st.markdown(f'<div class="validation-error">⚠️ {estatura_error}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="validation-success">✅ Estatura válida</div>', unsafe_allow_html=True)
    
    with col3:
        # Campo Método de medición
        metodo_grasa = st.selectbox(
            "📊 Método de medición de grasa",
            [
                "Omron HBF-516 (BIA básica)",
                "InBody 270 (BIA profesional)",
                "Bod Pod (Pletismografía)",
                "DEXA (Gold Standard)"
            ],
            help="Selecciona el método que utilizaste para medir tu porcentaje de grasa corporal"
        )
        
        st.markdown(f'<div class="validation-success">✅ Método seleccionado</div>', unsafe_allow_html=True)
    
    # Campo Porcentaje de grasa corporal (ancho completo)
    st.markdown("#### 💪 Porcentaje de grasa corporal")
    
    col_grasa1, col_grasa2 = st.columns([2, 1])
    
    with col_grasa1:
        grasa_default = 20.0 if sexo == "Hombre" else 25.0
        grasa_corporal = st.number_input(
            f"% de grasa corporal medido con {metodo_grasa.split('(')[0].strip()}",
            min_value=3.0,
            max_value=60.0,
            value=grasa_default,
            step=0.1,
            help=f"Valor obtenido con {metodo_grasa}"
        )
        
        # Validación en tiempo real de la grasa corporal
        grasa_valida, grasa_error = validar_grasa_corporal(grasa_corporal)
        if not grasa_valida:
            st.markdown(f'<div class="validation-error">⚠️ {grasa_error}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="validation-success">✅ Porcentaje válido</div>', unsafe_allow_html=True)
    
    with col_grasa2:
        # Información sobre rangos normales
        if sexo == "Hombre":
            rango_info = """
            **Rangos Hombre:**
            - Atlético: 6-13%
            - Fitness: 14-17%
            - Aceptable: 18-24%
            - Alto: >25%
            """
        else:
            rango_info = """
            **Rangos Mujer:**
            - Atlético: 16-20%
            - Fitness: 21-24%
            - Aceptable: 25-31%
            - Alto: >32%
            """
        st.markdown(rango_info)
    
    st.markdown("---")
    
    # ==================== CÁLCULOS Y MÉTRICAS ====================
    
    # Verificar si todos los datos son válidos
    todos_datos_validos = peso_valido and estatura_valida and grasa_valida
    
    if todos_datos_validos:
        st.markdown("### 📈 Métricas Calculadas")
        
        # Realizar todos los cálculos
        imc = calcular_imc(peso, estatura)
        mlg = calcular_mlg(peso, grasa_corporal)
        ffmi = calcular_ffmi(mlg, estatura)
        grasa_corregida = corregir_grasa_corporal(grasa_corporal, metodo_grasa, sexo)
        masa_grasa = peso - mlg
        
        # Clasificaciones
        clasificacion_imc, color_imc = clasificar_imc(imc)
        clasificacion_ffmi, color_ffmi = clasificar_ffmi(ffmi, sexo)
        
        # Mostrar métricas en tarjetas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">IMC</div>
                <div class="metric-value">{imc:.1f}</div>
                <div class="metric-help">{clasificacion_imc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">FFMI</div>
                <div class="metric-value">{ffmi:.1f}</div>
                <div class="metric-help">{clasificacion_ffmi}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Grasa Corregida</div>
                <div class="metric-value">{grasa_corregida:.1f}%</div>
                <div class="metric-help">Equivalente DEXA</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Masa Libre Grasa</div>
                <div class="metric-value">{mlg:.1f} kg</div>
                <div class="metric-help">Peso sin grasa</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Información detallada
        st.markdown("#### 📊 Información Detallada")
        
        col_det1, col_det2 = st.columns(2)
        
        with col_det1:
            st.markdown(f"""
            **Composición Corporal:**
            - Peso total: {peso:.1f} kg
            - Masa libre de grasa: {mlg:.1f} kg ({(mlg/peso*100):.1f}%)
            - Masa grasa: {masa_grasa:.1f} kg ({grasa_corregida:.1f}%)
            """)
            
            st.markdown(f"""
            **Índices:**
            - IMC: {imc:.1f} kg/m² ({clasificacion_imc})
            - FFMI: {ffmi:.1f} ({clasificacion_ffmi})
            """)
        
        with col_det2:
            st.markdown(f"""
            **Corrección por Método:**
            - Método utilizado: {metodo_grasa}
            - Grasa medida: {grasa_corporal:.1f}%
            - Grasa corregida (DEXA): {grasa_corregida:.1f}%
            - Diferencia: {abs(grasa_corregida - grasa_corporal):.1f}% puntos
            """)
            
            # Recomendaciones basadas en FFMI
            if sexo == "Hombre":
                if ffmi < 18:
                    recomendacion = "Considera aumentar masa muscular"
                elif ffmi > 25:
                    recomendacion = "Excelente desarrollo muscular"
                else:
                    recomendacion = "Desarrollo muscular normal"
            else:
                if ffmi < 15:
                    recomendacion = "Considera aumentar masa muscular"
                elif ffmi > 21:
                    recomendacion = "Excelente desarrollo muscular"
                else:
                    recomendacion = "Desarrollo muscular normal"
            
            st.markdown(f"**Evaluación:** {recomendacion}")
        
        # Marcar paso como completado
        st.session_state.paso_completado = True
        
        # Mensaje de éxito
        st.markdown("""
        <div class="alert-success">
            <strong>✅ ¡Datos completados correctamente!</strong><br>
            Todas las métricas han sido calculadas y están listas para continuar.
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Mostrar errores si faltan datos
        errores = []
        if not peso_valido:
            errores.append(peso_error)
        if not estatura_valida:
            errores.append(estatura_error)
        if not grasa_valida:
            errores.append(grasa_error)
        
        st.markdown(f"""
        <div class="alert-error">
            <strong>⚠️ Completa todos los campos correctamente:</strong><br>
            {'<br>'.join(f'• {error}' for error in errores)}
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.paso_completado = False
    
    st.markdown("---")
    
    # ==================== NAVEGACIÓN ====================
    
    st.markdown("### 🔄 Navegación")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Paso Anterior", help="Volver al paso anterior del wizard"):
            st.info("🔄 En una implementación completa, aquí se navegaría al Paso 3: Datos Personales")
    
    with col3:
        paso_valido = st.session_state.paso_completado
        boton_texto = "Siguiente Paso ➡️" if paso_valido else "Complete todos los campos"
        
        if st.button(boton_texto, disabled=not paso_valido, help="Continuar al siguiente paso"):
            if paso_valido:
                st.success("🎉 ¡Paso completado! En una implementación completa, avanzarías al Paso 5: Evaluación Funcional")
                st.balloons()
            else:
                st.error("❌ Completa todos los campos antes de continuar")
    
    # ==================== INFORMACIÓN ADICIONAL ====================
    
    with st.expander("📚 Información Científica", expanded=False):
        st.markdown("""
        ### Bases Científicas de los Cálculos
        
        **IMC (Índice de Masa Corporal):**
        - Fórmula: Peso (kg) / Estatura² (m)
        - Estándar internacional para evaluación básica
        - Limitación: No distingue entre masa muscular y grasa
        
        **FFMI (Fat Free Mass Index):**
        - Fórmula: MLG (kg) / Estatura² (m), normalizado a 1.80m
        - Mejor indicador de desarrollo muscular que el IMC
        - Útil para evaluar potencial genético y progreso
        
        **Corrección por Método de Medición:**
        - **BIA básica (Omron):** Tiende a subestimar grasa corporal
        - **BIA profesional (InBody):** Más precisa, corrección menor
        - **Pletismografía (Bod Pod):** Puede sobreestimar ligeramente
        - **DEXA:** Considerado el estándar de oro
        
        **Masa Libre de Grasa (MLG):**
        - Incluye músculo, huesos, órganos y agua
        - Base para cálculo del TMB con fórmula de Cunningham
        - Indicador clave para programación nutricional
        """)
    
    with st.expander("🎯 Objetivos y Uso de Datos", expanded=False):
        st.markdown("""
        ### ¿Para qué se usan estos datos?
        
        **Cálculo del TMB (Tasa Metabólica Basal):**
        - Fórmula de Cunningham: TMB = 370 + (21.6 × MLG)
        - Más precisa que fórmulas basadas solo en peso
        
        **Programación Nutricional:**
        - Determinación de calorías objetivo
        - Cálculo de macronutrientes específicos
        - Estrategias de déficit/superávit personalizadas
        
        **Monitoreo de Progreso:**
        - Cambios en composición corporal
        - Evolución del FFMI
        - Ajustes en el plan según resultados
        
        **Evaluación Funcional:**
        - Correlación entre composición y rendimiento
        - Identificación de fortalezas y debilidades
        - Recomendaciones de entrenamiento específicas
        """)

# ==================== EJECUTAR APLICACIÓN ====================

if __name__ == "__main__":
    main()
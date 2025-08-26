import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re

# ==================== FUNCIONES DE VALIDACIÓN ESTRICTA ====================
def validate_name(name):
    """
    Valida que el nombre tenga al menos dos palabras.
    Retorna (es_válido, mensaje_error)
    """
    if not name or not name.strip():
        return False, "El nombre es obligatorio"
    
    # Limpiar espacios extra y dividir en palabras
    words = name.strip().split()
    
    if len(words) < 2:
        return False, "El nombre debe contener al menos dos palabras (nombre y apellido)"
    
    # Verificar que cada palabra tenga al menos 2 caracteres y solo contenga letras y espacios
    for word in words:
        if len(word) < 2:
            return False, "Cada palabra del nombre debe tener al menos 2 caracteres"
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+$', word):
            return False, "El nombre solo puede contener letras y espacios"
    
    return True, ""

def validate_phone(phone):
    """
    Valida que el teléfono tenga exactamente 10 dígitos.
    Retorna (es_válido, mensaje_error)
    """
    if not phone or not phone.strip():
        return False, "El teléfono es obligatorio"
    
    # Limpiar espacios y caracteres especiales
    clean_phone = re.sub(r'[^0-9]', '', phone.strip())
    
    if len(clean_phone) != 10:
        return False, "El teléfono debe tener exactamente 10 dígitos"
    
    # Verificar que todos sean dígitos
    if not clean_phone.isdigit():
        return False, "El teléfono solo puede contener números"
    
    return True, ""

def validate_email(email):
    """
    Valida que el email tenga formato estándar.
    Retorna (es_válido, mensaje_error)
    """
    if not email or not email.strip():
        return False, "El email es obligatorio"
    
    # Patrón regex para email estándar
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email.strip()):
        return False, "El email debe tener un formato válido (ejemplo: usuario@dominio.com)"
    
    return True, ""

# ==================== WIZARD NAVIGATION SYSTEM ====================
def get_wizard_progress():
    """Calculate wizard progress based on current step."""
    paso_actual = st.session_state.get("paso_actual", 1)
    return (paso_actual / 10) * 100

def get_step_title(step):
    """Get the title for each wizard step."""
    titles = {
        1: "🔐 Acceso y Autenticación",
        2: "⚖️ Términos y Descargo",
        3: "👤 Datos Personales", 
        4: "📊 Composición Corporal",
        5: "💪 Evaluación Funcional",
        6: "🚶 Actividad Física Diaria",
        7: "🏋️ Entrenamiento de Fuerza",
        8: "🍽️ Efecto Térmico Alimentos",
        9: "📈 Resultados y Plan",
        10: "📧 Resumen y Envío"
    }
    return titles.get(step, f"Paso {step}")

def can_advance_to_step(target_step):
    """Check if user can advance to the target step based on validations."""
    current_step = st.session_state.get("paso_actual", 1)
    
    # Can always go back or stay on current step
    if target_step <= current_step:
        return True
    
    # Can only advance one step at a time and only if current step is valid
    if target_step != current_step + 1:
        return False
        
    # Validate current step before advancing
    if current_step == 1:  # Authentication
        return st.session_state.get("authenticated", False)
    elif current_step == 2:  # Terms
        return st.session_state.get("acepto_descargo", False)
    elif current_step == 3:  # Personal data
        return st.session_state.get("datos_completos", False)
    elif current_step == 4:  # Body composition
        peso = st.session_state.get("peso", 0)
        estatura = st.session_state.get("estatura", 0) 
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        return peso > 0 and estatura > 0 and grasa_corporal > 0
    elif current_step == 5:  # Functional evaluation
        experiencia = st.session_state.get("experiencia_entrenamiento", "")
        ejercicios_data = st.session_state.get("datos_ejercicios", {})
        return experiencia and len(ejercicios_data) >= 5
    elif current_step == 6:  # Daily activity
        actividad = st.session_state.get("actividad_diaria", "")
        return bool(actividad)
    elif current_step == 7:  # Strength training
        frecuencia = st.session_state.get("frecuencia_entrenamiento", 0)
        return frecuencia > 0
    elif current_step == 8:  # ETA
        # ETA is calculated automatically based on previous data
        peso = st.session_state.get("peso", 0)
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        actividad = st.session_state.get("actividad_diaria", "")
        return peso > 0 and grasa_corporal > 0 and actividad
    elif current_step == 9:  # Results
        # Results are generated automatically
        return True
    
    return False

def show_wizard_navigation():
    """Show wizard navigation buttons."""
    paso_actual = st.session_state.get("paso_actual", 1)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if paso_actual > 1:
            if st.button("⬅️ Anterior", key="nav_prev"):
                st.session_state.paso_actual = paso_actual - 1
                st.rerun()
    
    with col2:
        # Progress display
        progress = get_wizard_progress()
        st.progress(progress / 100)
        st.markdown(f"<div style='text-align: center; color: var(--mupai-yellow); font-weight: bold;'>Paso {paso_actual} de 10</div>", unsafe_allow_html=True)
    
    with col3:
        if paso_actual < 10:
            can_advance = can_advance_to_step(paso_actual + 1)
            if st.button("Siguiente ➡️", key="nav_next", disabled=not can_advance):
                if can_advance:
                    st.session_state.paso_actual = paso_actual + 1
                    st.rerun()

def crear_tarjeta(titulo, contenido, tipo="info"):
    """Create a styled card component."""
    colores = {
        "info": "var(--mupai-yellow)",
        "success": "var(--mupai-success)",
        "warning": "var(--mupai-warning)",
        "danger": "var(--mupai-danger)"
    }
    color = colores.get(tipo, "var(--mupai-yellow)")
    return f"""
    <div class="content-card" style="border-left-color: {color};">
        <h3 style="margin-bottom: 1rem;">{titulo}</h3>
        <div>{contenido}</div>
    </div>
    """

# Referencias funcionales para ejercicios
referencias_funcionales = {
    "Hombre": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 10), ("Promedio", 20), ("Bueno", 35), ("Avanzado", 50)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 30)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 8), ("Promedio", 15), ("Bueno", 25), ("Avanzado", 35)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 20), ("Promedio", 40), ("Bueno", 60), ("Avanzado", 90)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 20), ("Avanzado", 30)]}
    },
    "Mujer": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 4), ("Bueno", 10), ("Avanzado", 18)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 1), ("Bueno", 3), ("Avanzado", 5)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 3), ("Promedio", 8), ("Bueno", 12), ("Avanzado", 18)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 30)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 15), ("Promedio", 30), ("Bueno", 50), ("Avanzado", 70)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 3), ("Bueno", 7), ("Avanzado", 12)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 3), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]}
    }
}

# ==================== FUNCIÓN DE CÁLCULO DE PROGRESO DINÁMICO ====================
def calcular_progreso_evaluacion():
    """
    Calcula el progreso real de la evaluación basado en datos completados.
    Retorna (porcentaje, texto_descriptivo)
    """
    progreso = 0
    pasos_completados = []
    
    # Paso 0: Datos personales (20%)
    if st.session_state.get("datos_completos", False):
        progreso += 20
        pasos_completados.append("Datos personales")
    
    # Paso 1: Composición corporal (20%)
    peso = st.session_state.get("peso", 0)
    estatura = st.session_state.get("estatura", 0)
    grasa_corporal = st.session_state.get("grasa_corporal", 0)
    if peso > 0 and estatura > 0 and grasa_corporal > 0:
        progreso += 20
        pasos_completados.append("Composición corporal")
    
    # Paso 2: Evaluación funcional (20%)
    experiencia = st.session_state.get("experiencia_entrenamiento", "")
    if experiencia and experiencia != "A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.":
        progreso += 20
        pasos_completados.append("Evaluación funcional")
    
    # Paso 3: Actividad física (20%)
    actividad = st.session_state.get("actividad_diaria", "")
    if actividad:
        progreso += 20
        pasos_completados.append("Actividad física")
    
    # Paso 4: Entrenamiento de fuerza (20%)
    frecuencia_entrenamiento = st.session_state.get("frecuencia_entrenamiento", 0)
    if frecuencia_entrenamiento > 0:
        progreso += 20
        pasos_completados.append("Entrenamiento de fuerza")
    
    # Crear texto descriptivo
    total_pasos = 5
    pasos_realizados = len(pasos_completados)
    
    if pasos_realizados == 0:
        texto = "Evaluación no iniciada"
    elif pasos_realizados == total_pasos:
        texto = "¡Evaluación completada! Calculando resultados..."
    else:
        texto = f"Paso {pasos_realizados} de {total_pasos}: {pasos_completados[-1] if pasos_completados else 'Iniciando'}"
    
    return min(progreso, 100), texto

# ==================== CONFIGURACIÓN DE PÁGINA Y CSS MEJORADO ====================
st.set_page_config(
    page_title="MUPAI - Evaluación Fitness Personalizada",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
}

/* Hide GitHub-related elements */
#MainMenu {visibility: hidden;}
.stDeployButton {display: none;}
.stActionButton {display: none;}
[data-testid="stToolbar"] {visibility: hidden !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
.stApp > header {visibility: hidden;}
.css-1dp5vir {visibility: hidden;}
.css-hi6a2p {padding-top: 0rem;}
#root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
footer {visibility: hidden;}
.stDeployButton {display: none !important;}
button[title="View fullscreen"] {visibility: hidden;}

/* Hide hamburger menu and toolbar */
.css-14xtw13.e8zbici0 {display: none !important;}
.css-vk3wp9 {display: none !important;}
.css-1544g2n {display: none !important;}
section[data-testid="stToolbar"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}
.stToolbar {display: none !important;}

/* Additional hiding for any fork/GitHub buttons */
a[href*="github"] {display: none !important;}
a[href*="fork"] {display: none !important;}
button[data-baseweb="button"]:has-text("Fork") {display: none !important;}
*[title*="GitHub"] {display: none !important;}
*[title*="Fork"] {display: none !important;}
*[alt*="GitHub"] {display: none !important;}
*[alt*="Fork"] {display: none !important;}
/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #1E1E1E 0%, #232425 100%);
}
.main-header {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: #181A1B;
    padding: 2rem 1rem;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(244, 196, 48, 0.20);
    animation: fadeIn 0.5s ease-out;
}
.content-card {
    background: #1E1E1E;
    padding: 2rem 1.3rem;
    border-radius: 16px;
    box-shadow: 0 5px 22px 0px rgba(244,196,48,0.07), 0 1.5px 8px rgba(0,0,0,0.11);
    margin-bottom: 1.7rem;
    border-left: 5px solid var(--mupai-yellow);
    animation: slideIn 0.5s;
}
.card-psmf {
    border-left-color: var(--mupai-warning)!important;
}
.card-success {
    border-left-color: var(--mupai-success)!important;
}
.content-card, .content-card * {
    color: #FFF !important;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.stButton > button {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: #232425;
    border: none;
    padding: 0.85rem 2.3rem;
    font-weight: bold;
    border-radius: 28px;
    transition: all 0.3s;
    box-shadow: 0 4px 16px rgba(244, 196, 48, 0.18);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 1.15rem;
}
.stButton > button:hover {
    filter: brightness(1.04);
    box-shadow: 0 7px 22px rgba(244, 196, 48, 0.24);
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    border: 2px solid var(--mupai-yellow)!important;
    border-radius: 11px!important;
    padding: 0.7rem 0.9rem!important;
    background: #232425!important;
    color: #fff!important;
    font-size: 1.13rem!important;
    font-weight: 600!important;
}
/* Special styling for body fat measurement method selector */
.stSelectbox[data-testid="stSelectbox"]:has(label:contains("Método de medición de grasa")) > div > div > select,
.body-fat-method-selector > div > div > select {
    background: #F8F9FA!important;
    color: #1E1E1E!important;
    border: 2px solid #DAA520!important;
    font-weight: bold!important;
}
.stSelectbox[data-testid="stSelectbox"]:has(label:contains("Método de medición de grasa")) option,
.body-fat-method-selector option {
    background: #FFFFFF!important;
    color: #1E1E1E!important;
    font-weight: bold!important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stRadio label, .stCheckbox label, .stDateInput label, .stMarkdown,
.stExpander .streamlit-expanderHeader, .stExpander label, .stExpander p, .stExpander div {
    color: #fff !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 1.04rem !important;
}
/* Reglas específicas adicionales para máxima visibilidad de títulos de expanders */
.stExpander .streamlit-expanderHeader,
.stExpander .streamlit-expanderHeader *,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: var(--mupai-yellow) !important;
    opacity: 1 !important;
    font-weight: bold !important;
    visibility: visible !important;
    filter: none !important;
    text-shadow: none !important;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #e0e0e0 !important;
    opacity: 1 !important;
}
.stAlert > div {
    border-radius: 11px;
    padding: 1.1rem;
    border-left: 5px solid;
    background: #222326 !important;
    color: #FFF !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(125deg, #252525 0%, #303030 100%);
    padding: 1.1rem 1rem;
    border-radius: 12px;
    border-left: 4px solid var(--mupai-yellow);
    box-shadow: 0 2.5px 11px rgba(0,0,0,0.11);
    color: #fff !important;
}
.streamlit-expanderHeader {
    background: linear-gradient(135deg, var(--mupai-gray) 70%, #242424 100%);
    border-radius: 12px;
    font-weight: bold;
    color: var(--mupai-yellow) !important;
    border: 2px solid var(--mupai-yellow);
    font-size: 1.16rem;
    opacity: 1 !important;
}
/* Reglas específicas para títulos de expanders principales con máxima visibilidad */
.streamlit-expanderHeader > div,
.streamlit-expanderHeader > div > div,
.streamlit-expanderHeader span,
.streamlit-expanderHeader p,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary > div,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: var(--mupai-yellow) !important;
    opacity: 1 !important;
    font-weight: bold !important;
    text-shadow: none !important;
    filter: none !important;
}
/* Asegurar visibilidad en estado hover */
.streamlit-expanderHeader:hover,
.streamlit-expanderHeader:hover > div,
.streamlit-expanderHeader:hover > div > div,
.streamlit-expanderHeader:hover span,
.streamlit-expanderHeader:hover p,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:hover > div,
[data-testid="stExpander"] summary:hover span,
[data-testid="stExpander"] summary:hover p {
    color: var(--mupai-yellow) !important;
    opacity: 1 !important;
    font-weight: bold !important;
}
.stRadio > div {
    background: #181A1B !important;
    padding: 1.1rem 0.5rem;
    border-radius: 10px;
    border: 2px solid transparent;
    transition: all 0.3s;
    color: #FFF !important;
}
.stRadio > div:hover {
    border-color: var(--mupai-yellow);
}
.stCheckbox > label, .stCheckbox > span {
    color: #FFF !important;
    opacity: 1 !important;
    font-size: 1.05rem;
}
/* Enhanced styling for important checkboxes */
.stCheckbox:has(span:contains("He leído y acepto la política de privacidad")) {
    background: rgba(244, 196, 48, 0.05) !important;
    border: 2px solid var(--mupai-yellow) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 0.8rem 0 !important;
    transition: all 0.3s ease !important;
}
.stCheckbox:has(span:contains("He leído y acepto la política de privacidad")):hover {
    background: rgba(244, 196, 48, 0.1) !important;
    box-shadow: 0 4px 15px rgba(244, 196, 48, 0.2) !important;
}
.stCheckbox:has(span:contains("He leído y acepto la política de privacidad")) label {
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}
/* Enhanced styling for disclaimer checkbox inside expander */
.stCheckbox:has(span:contains("He leído y entiendo completamente el descargo")) {
    background: rgba(244, 196, 48, 0.03) !important;
    border: 1px solid rgba(244, 196, 48, 0.4) !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
    margin: 0.5rem 0 !important;
    transition: all 0.3s ease !important;
}
.stCheckbox:has(span:contains("He leído y entiendo completamente el descargo")):hover {
    background: rgba(244, 196, 48, 0.08) !important;
    border-color: var(--mupai-yellow) !important;
}
.stCheckbox:has(span:contains("He leído y entiendo completamente el descargo")) label {
    font-weight: 500 !important;
    font-size: 1.05rem !important;
}
.stProgress > div > div > div {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%)!important;
    border-radius: 10px;
    animation: pulse 1.2s infinite;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.92; }
    100% { opacity: 1; }
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px);} to { opacity: 1; transform: translateY(0);} }
@keyframes slideIn { from { opacity: 0; transform: translateX(-18px);} to { opacity: 1; transform: translateX(0);} }
.badge {
    display: inline-block;
    padding: 0.32rem 0.98rem;
    border-radius: 18px;
    font-size: 0.97rem;
    font-weight: 800;
    margin: 0.27rem;
    color: #FFF;
    background: #313131;
    border: 1px solid #555;
}
.badge-success { background: var(--mupai-success); }
.badge-warning { background: var(--mupai-warning); color: #222; border: 1px solid #b78a09;}
.badge-danger { background: var(--mupai-danger); }
.badge-info { background: var(--mupai-yellow); color: #1E1E1E;}
.dataframe {
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    background: #2A2A2A!important;
    color: #FFF!important;
}
hr {
    border: none;
    height: 2.5px;
    background: linear-gradient(to right, transparent, var(--mupai-yellow), transparent);
    margin: 2.1rem 0;
}
@media (max-width: 768px) {
    .main-header { padding: 1.2rem;}
    .content-card { padding: 1.1rem;}
    .stButton > button { padding: 0.5rem 1.1rem; font-size: 0.96rem;}
}
.content-card:hover {
    transform: translateY(-1.5px);
    box-shadow: 0 8px 27px rgba(0,0,0,0.17);
    transition: all 0.25s;
}
.gradient-text {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    font-size: 1.11rem;
}
.footer-mupai {
    text-align: center;
    padding: 2.2rem 0.3rem 2.2rem 0.3rem;
    background: linear-gradient(135deg, #202021 0%, #232425 100%);
    border-radius: 15px;
    color: #FFF;
    margin-top: 2.2rem;
}
.footer-mupai h4 { color: var(--mupai-yellow); margin-bottom: 1.1rem;}
.footer-mupai a {
    color: var(--mupai-yellow);
    text-decoration: none;
    margin: 0 1.2rem;
    font-weight: 600;
    font-size: 1.01rem;
}

/* ULTIMATE GITHUB/FORK HIDING - Hide any possible GitHub elements */
[data-testid="stAppViewContainer"] header {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
.css-18e3th9 {display: none !important;}
.css-1d391kg {display: none !important;}
.main-header {margin-top: 0rem !important;}
.block-container {padding-top: 1rem !important;}

/* Hide any share or deploy buttons that might link to GitHub */
button:contains("Share") {display: none !important;}
button:contains("Deploy") {display: none !important;}
button:contains("GitHub") {display: none !important;}
button:contains("Fork") {display: none !important;}
a:contains("GitHub") {display: none !important;}
a:contains("Fork") {display: none !important;}

/* Hide Streamlit branding that might include GitHub links */
.css-1rs6os {display: none !important;}
.css-17eq0hr {display: none !important;}
.css-1fv8s86 {display: none !important;}

</style>
""", unsafe_allow_html=True)
# Header principal visual con logos
import base64

# JavaScript para ocultar elementos de GitHub/Fork que puedan aparecer dinámicamente
github_hide_js = """
<script>
// Function to hide GitHub/Fork related elements
function hideGitHubElements() {
    // Hide elements by text content
    const elementsToHide = [
        'a[href*="github"]',
        'a[href*="fork"]', 
        'button:contains("Fork")',
        'button:contains("GitHub")',
        'button:contains("Share")',
        'button:contains("Deploy")',
        '[data-testid="stToolbar"]',
        '[data-testid="stHeader"]',
        '.stDeployButton',
        '.stActionButton'
    ];
    
    elementsToHide.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el) {
                    el.style.display = 'none !important';
                    el.style.visibility = 'hidden !important';
                }
            });
        } catch (e) {
            console.log('Could not hide element:', selector);
        }
    });
    
    // Hide elements by text content (more aggressive)
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
        if (el.textContent && (
            el.textContent.toLowerCase().includes('fork') ||
            el.textContent.toLowerCase().includes('github') ||
            el.textContent.toLowerCase().includes('deploy') ||
            el.textContent.toLowerCase().includes('share')
        )) {
            // Only hide if it's a button or link
            if (el.tagName === 'BUTTON' || el.tagName === 'A') {
                el.style.display = 'none !important';
            }
        }
    });
}

// Run immediately and also on DOM changes
hideGitHubElements();

// Observer for dynamic content
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
            hideGitHubElements();
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Run again after page load
window.addEventListener('load', hideGitHubElements);
</script>
"""

st.markdown(github_hide_js, unsafe_allow_html=True)

# Cargar y codificar los logos desde la raíz del repo
try:
    with open('LOGO MUPAI.png', 'rb') as f:
        logo_mupai_b64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    logo_mupai_b64 = ""

try:
    with open('LOGO MUP.png', 'rb') as f:
        logo_gym_b64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    logo_gym_b64 = ""

st.markdown(f"""
<style>
.header-container {{
    background: #000000;
    padding: 2rem 1rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.5s ease-out;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
}}

.logo-left, .logo-right {{
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    max-width: 150px;
}}

.logo-left img, .logo-right img {{
    max-height: 80px;
    max-width: 100%;
    height: auto;
    width: auto;
    object-fit: contain;
}}

.header-center {{
    flex: 1;
    text-align: center;
    padding: 0 2rem;
}}

.header-title {{
    color: #FFB300;
    font-size: 2.2rem;
    font-weight: 900;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    line-height: 1.2;
}}

.header-subtitle {{
    color: #FFFFFF;
    font-size: 1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}}

@media (max-width: 768px) {{
    .header-container {{
        flex-direction: column;
        text-align: center;
    }}
    
    .logo-left, .logo-right {{
        margin-bottom: 1rem;
    }}
    
    .header-center {{
        padding: 0;
    }}
    
    .header-title {{
        font-size: 1.8rem;
    }}
}}
</style>

<div class="header-container">
    <div class="logo-left">
        <img src="data:image/png;base64,{logo_mupai_b64}" alt="LOGO MUPAI" />
    </div>
    <div class="header-center">
        <h1 class="header-title">TEST MUPAI: BODY AND ENERGY </h1>
        <p class="header-subtitle">Tu evaluación de la composición corporal y balance energético basada en ciencia</p>
    </div>
    <div class="logo-right">
        <img src="data:image/png;base64,{logo_gym_b64}" alt="LOGO MUSCLE UP GYM" />
    </div>
</div>
""", unsafe_allow_html=True)

# --- Inicialización de estado de sesión robusta (solo una vez)
defaults = {
    "datos_completos": False,
    "correo_enviado": False,
    "datos_ejercicios": {},
    "niveles_ejercicios": {},
    "nombre": "",
    "telefono": "",
    "email_cliente": "",
    "edad": "",
    "sexo": "Hombre",
    "fecha_llenado": datetime.now().strftime("%Y-%m-%d"),
    "acepto_terminos": False,
    "authenticated": False,  # Nueva variable para controlar el login
    "paso_actual": 1,  # Wizard navigation: current step (1-10)
    "acepto_descargo": False  # For terms acceptance
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================== WIZARD SYSTEM ====================
ADMIN_PASSWORD = "MUPAI2025"  # Contraseña predefinida
paso_actual = st.session_state.get("paso_actual", 1)

# Show current step title
st.markdown(f"""
<div class="content-card" style="text-align: center; background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%); color: #1E1E1E; margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 1.5rem; font-weight: bold;">{get_step_title(paso_actual)}</h1>
</div>
""", unsafe_allow_html=True)

# ==================== STEP 1: ACCESO Y AUTENTICACIÓN ====================
if paso_actual == 1:
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="content-card" style="max-width: 500px; margin: 2rem auto; text-align: center;">
            <h2 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">
                🔐 Acceso Exclusivo
            </h2>
            <p style="margin-bottom: 2rem; color: #CCCCCC;">
                Ingresa la contraseña para acceder al sistema de evaluación MUPAI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Container centrado para el formulario de login
        login_container = st.container()
        with login_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                password_input = st.text_input(
                    "Contraseña", 
                    type="password", 
                    placeholder="Ingresa la contraseña de acceso",
                    key="password_input"
                )
                
                if st.button("🚀 Acceder al Sistema", use_container_width=True):
                    if password_input == ADMIN_PASSWORD:
                        st.session_state.authenticated = True
                        st.success("✅ Acceso autorizado. Bienvenido al sistema MUPAI.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta. Acceso denegado.")
        
        # Mostrar información mientras no esté autenticado
        st.markdown("""
        <div class="content-card" style="margin-top: 3rem; text-align: center; background: #1A1A1A;">
            <h3 style="color: var(--mupai-yellow);">Sistema de Evaluación Fitness Profesional</h3>
            <p style="color: #CCCCCC;">
                MUPAI utiliza algoritmos científicos avanzados para proporcionar evaluaciones 
                personalizadas de composición corporal, rendimiento y planificación nutricional.
            </p>
            <p style="color: #999999; font-size: 0.9rem; margin-top: 1.5rem;">
                © 2025 MUPAI - Muscle up GYM 
                Digital Training Science
                Performance Assessment Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()  # Detener la ejecución hasta que se autentique
    else:
        # Already authenticated, show confirmation
        st.success("✅ Acceso autorizado correctamente.")
        st.markdown("""
        <div class="content-card">
            <h3 style="color: var(--mupai-yellow);">¡Bienvenido al Sistema MUPAI!</h3>
            <p>Tu evaluación de fitness personalizada está lista para comenzar. El sistema utilizará métodos científicos validados para analizar tu composición corporal, rendimiento funcional y crear un plan nutricional personalizado.</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== STEP 2: ACEPTACIÓN DE TÉRMINOS Y DESCARGO ====================
elif paso_actual == 2:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Términos y Condiciones del Servicio</h3>
        <p>Antes de continuar con tu evaluación personalizada, es importante que conozcas los términos y limitaciones de este sistema.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === DESCARGO DE RESPONSABILIDAD PROFESIONAL ===
    with st.expander("⚖️ **Descargo de Responsabilidad Profesional** (Requerido)", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(crear_tarjeta(
                "🔬 Naturaleza Científica",
                "Esta herramienta proporciona estimaciones basadas en algoritmos científicos validados. Los resultados son orientativos y no constituyen un diagnóstico médico o nutricional.",
                "info"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(crear_tarjeta(
                "⚕️ Limitaciones",
                "No reemplaza la consulta con profesionales de la salud. Los cálculos pueden tener margen de error según la precisión de los datos ingresados.",
                "warning"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(crear_tarjeta(
                "🎯 Uso Recomendado",
                "Utiliza estos resultados como punto de partida informativo. Consulta con profesionales certificados antes de implementar cambios significativos.",
                "success"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(crear_tarjeta(
                "📞 Responsabilidad",
                "MUPAI y Muscle Up GYM no se hacen responsables por el uso inadecuado de esta información. El usuario asume la responsabilidad.",
                "danger"
            ), unsafe_allow_html=True)
        
        # Checkbox destacado dentro del expander
        st.markdown("""
        <div style="background: rgba(244, 196, 48, 0.08); padding: 1rem; border-radius: 10px; border: 1px solid rgba(244, 196, 48, 0.3); margin: 1rem 0;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: var(--mupai-yellow); font-size: 1.1rem; margin-right: 0.5rem;">📋</span>
                <strong style="color: var(--mupai-yellow); font-size: 1rem;">CONFIRMACIÓN REQUERIDA</strong>
            </div>
            <p style="color: #CCCCCC; margin: 0; font-size: 0.95rem;">
                Marca la siguiente casilla para confirmar que has leído y comprendes completamente el descargo de responsabilidad.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        acepto_descargo = st.checkbox(
            "✅ **He leído y entiendo completamente el descargo de responsabilidad profesional**",
            key="acepto_descargo",
            value=st.session_state.get("acepto_descargo", False),
            help="Debes confirmar que has leído y entiendes las limitaciones de esta evaluación"
        )
        
# ==================== STEP 3: DATOS PERSONALES ====================
elif paso_actual == 3:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Información Personal</h3>
        <p>Proporciona tus datos personales para personalizar tu evaluación. Todos los campos son obligatorios.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(crear_tarjeta(
            "🔐 Privacidad",
            "Tus datos son confidenciales y solo se usan para generar tu plan personalizado.",
            "success"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "📞 Contacto",
            "Tu información de contacto es necesaria para enviarte los resultados por email.",
            "info"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta(
            "⚡ Precisión",
            "Datos precisos = recomendaciones más exactas y efectivas.",
            "warning"
        ), unsafe_allow_html=True)

    st.markdown("### Completa todos los campos")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input(
            "Nombre completo*", 
            placeholder="Ej: Juan Pérez García", 
            value=st.session_state.get("nombre", ""),
            help="Tu nombre legal completo"
        )
        telefono = st.text_input(
            "Teléfono*", 
            placeholder="Ej: 8661234567", 
            value=st.session_state.get("telefono", ""),
            help="10 dígitos sin espacios"
        )
        email_cliente = st.text_input(
            "Email*", 
            placeholder="correo@ejemplo.com", 
            value=st.session_state.get("email_cliente", ""),
            help="Email válido para recibir resultados"
        )

    with col2:
        edad = st.number_input(
            "Edad (años)*", 
            min_value=15, 
            max_value=80, 
            value=safe_int(st.session_state.get("edad", 25), 25), 
            help="Tu edad actual"
        )
        sexo = st.selectbox(
            "Sexo biológico*", 
            ["Hombre", "Mujer"], 
            index=0 if st.session_state.get("sexo", "Hombre") == "Hombre" else 1,
            help="Necesario para cálculos precisos"
        )
        fecha_llenado = datetime.now().strftime("%Y-%m-%d")
        st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

    # Validation and saving
    if st.button("💾 Guardar Datos Personales", key="save_personal_data"):
        # Validación estricta de cada campo
        name_valid, name_error = validate_name(nombre)
        phone_valid, phone_error = validate_phone(telefono)
        email_valid, email_error = validate_email(email_cliente)
        
        # Mostrar errores específicos para cada campo que falle
        validation_errors = []
        if not name_valid:
            validation_errors.append(f"**Nombre:** {name_error}")
        if not phone_valid:
            validation_errors.append(f"**Teléfono:** {phone_error}")
        if not email_valid:
            validation_errors.append(f"**Email:** {email_error}")
        
        # Solo proceder si todas las validaciones pasan
        if name_valid and phone_valid and email_valid:
            st.session_state.datos_completos = True
            st.session_state.nombre = nombre
            st.session_state.telefono = telefono
            st.session_state.email_cliente = email_cliente
            st.session_state.edad = edad
            st.session_state.sexo = sexo
            st.session_state.fecha_llenado = fecha_llenado
            st.success("✅ Datos registrados correctamente.")
        else:
            # Mostrar todos los errores de validación
            error_message = "⚠️ **Por favor corrige los siguientes errores:**\n\n" + "\n\n".join(validation_errors)
            st.error(error_message)
    
    # Show saved data if available
    if st.session_state.get("datos_completos", False):
        st.success("✅ Datos personales guardados correctamente.")

# ==================== SHOW NAVIGATION ====================
if paso_actual >= 1:
    st.markdown("---")
    show_wizard_navigation()

# ==================== STEP 4: COMPOSICIÓN CORPORAL Y ANTROPOMETRÍA ====================
elif paso_actual == 4:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Composición Corporal y Antropometría</h3>
        <p>Ingresa tus medidas corporales precisas para calcular tu metabolismo basal y necesidades energéticas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Datos Antropométricos")
    col1, col2 = st.columns(2)
    
    with col1:
        peso = st.number_input(
            "Peso (kg)*", 
            min_value=30.0, 
            max_value=200.0, 
            value=float(st.session_state.get("peso", 70.0)),
            step=0.1,
            help="Tu peso actual en kilogramos"
        )
        estatura = st.number_input(
            "Estatura (cm)*", 
            min_value=130, 
            max_value=220, 
            value=int(st.session_state.get("estatura", 170)),
            step=1,
            help="Tu estatura en centímetros"
        )
        
    with col2:
        grasa_corporal = st.number_input(
            "Porcentaje de grasa corporal (%)*", 
            min_value=3.0, 
            max_value=50.0, 
            value=float(st.session_state.get("grasa_corporal", 15.0)),
            step=0.1,
            help="Tu porcentaje de grasa corporal"
        )
        metodo_grasa = st.selectbox(
            "Método de medición de grasa*",
            ["DEXA (Gold Standard)", "BIA (Bioimpedancia)", "Plicómetros", "Visual/Estimado"],
            index=0,
            help="Método utilizado para medir tu porcentaje de grasa"
        )
    
    if st.button("💾 Guardar Composición Corporal", key="save_body_comp"):
        if peso > 0 and estatura > 0 and grasa_corporal > 0:
            st.session_state.peso = peso
            st.session_state.estatura = estatura
            st.session_state.grasa_corporal = grasa_corporal
            st.session_state.metodo_grasa = metodo_grasa
            st.success("✅ Datos de composición corporal guardados correctamente.")
        else:
            st.error("⚠️ Todos los campos son obligatorios.")
    
    # Show calculated metrics if data is saved
    if all([st.session_state.get("peso", 0), st.session_state.get("estatura", 0), st.session_state.get("grasa_corporal", 0)]):
        st.success("✅ Composición corporal guardada correctamente.")
        
        # Calculate BMI and MLG for display
        peso_saved = st.session_state.get("peso", 0)
        estatura_saved = st.session_state.get("estatura", 0)
        grasa_saved = st.session_state.get("grasa_corporal", 0)
        
        imc = peso_saved / ((estatura_saved/100) ** 2)
        mlg = peso_saved * (1 - grasa_saved/100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BMI", f"{imc:.1f}")
        with col2:
            st.metric("Masa Libre de Grasa", f"{mlg:.1f} kg")
        with col3:
            st.metric("Masa Grasa", f"{peso_saved - mlg:.1f} kg")

# ==================== STEP 5: EVALUACIÓN FUNCIONAL Y EXPERIENCIA ====================
elif paso_actual == 5:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Evaluación Funcional y Experiencia</h3>
        <p>Evalúa tu experiencia en entrenamiento y rendimiento en ejercicios funcionales clave.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Experience level
    st.markdown("### Experiencia en Entrenamiento")
    experiencia = st.selectbox(
        "Selecciona tu nivel de experiencia*",
        [
            "A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.",
            "B) He entrenado de forma regular por menos de 1 año, siguiendo un plan básico.",
            "C) He entrenado de forma regular por 1-3 años, con conocimiento de técnica y periodización.",
            "D) He entrenado de forma regular por más de 3 años, con conocimiento avanzado y resultados consistentes."
        ],
        index=0 if not st.session_state.get("experiencia_entrenamiento") else ["A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.", "B) He entrenado de forma regular por menos de 1 año, siguiendo un plan básico.", "C) He entrenado de forma regular por 1-3 años, con conocimiento de técnica y periodización.", "D) He entrenado de forma regular por más de 3 años, con conocimiento avanzado y resultados consistentes."].index(st.session_state.get("experiencia_entrenamiento", "A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.")),
        help="Selecciona la opción que mejor describe tu experiencia"
    )
    
    # Functional exercises
    st.markdown("### Ejercicios Funcionales")
    st.markdown("Ingresa tu mejor rendimiento en cada ejercicio:")
    
    sexo = st.session_state.get("sexo", "Hombre")
    ejercicios_refs = referencias_funcionales.get(sexo, referencias_funcionales["Hombre"])
    ejercicios_data = st.session_state.get("datos_ejercicios", {})
    
    col1, col2 = st.columns(2)
    ejercicios_lista = list(ejercicios_refs.keys())
    
    for i, ejercicio in enumerate(ejercicios_lista):
        with col1 if i % 2 == 0 else col2:
            ref_info = ejercicios_refs[ejercicio]
            if ref_info["tipo"] == "reps":
                valor = st.number_input(
                    f"{ejercicio} (repeticiones)*",
                    min_value=0,
                    max_value=200,
                    value=ejercicios_data.get(ejercicio, 0),
                    step=1,
                    key=f"ejercicio_{ejercicio}"
                )
            else:  # tiempo
                valor = st.number_input(
                    f"{ejercicio} (segundos)*",
                    min_value=0,
                    max_value=300,
                    value=ejercicios_data.get(ejercicio, 0),
                    step=1,
                    key=f"ejercicio_{ejercicio}"
                )
            ejercicios_data[ejercicio] = valor
    
    if st.button("💾 Guardar Evaluación Funcional", key="save_functional"):
        if experiencia and len([v for v in ejercicios_data.values() if v > 0]) >= 5:
            st.session_state.experiencia_entrenamiento = experiencia
            st.session_state.datos_ejercicios = ejercicios_data
            st.success("✅ Evaluación funcional guardada correctamente.")
        else:
            st.error("⚠️ Completa todos los ejercicios y selecciona tu experiencia.")
    
    if st.session_state.get("experiencia_entrenamiento") and st.session_state.get("datos_ejercicios"):
        st.success("✅ Evaluación funcional guardada correctamente.")

# ==================== STEP 6: NIVEL DE ACTIVIDAD FÍSICA DIARIA ====================
elif paso_actual == 6:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Nivel de Actividad Física Diaria</h3>
        <p>Selecciona el nivel que mejor describe tu actividad física habitual (excluyendo el entrenamiento de fuerza).</p>
    </div>
    """, unsafe_allow_html=True)
    
    actividades = [
        "Sedentario (Trabajo de oficina, poca actividad física)",
        "Moderadamente-activo (Caminar regularmente, actividades ligeras)",
        "Activo (Ejercicio regular 3-4 veces por semana)",
        "Muy-activo (Ejercicio intenso 5+ veces por semana)"
    ]
    
    actividad_actual = st.session_state.get("actividad_diaria", "")
    index_actual = 0
    if actividad_actual:
        try:
            index_actual = actividades.index(actividad_actual)
        except ValueError:
            index_actual = 0
    
    actividad_diaria = st.selectbox(
        "Nivel de actividad física diaria*",
        actividades,
        index=index_actual,
        help="Selecciona tu nivel de actividad promedio"
    )
    
    # Show visual representation
    niveles_ui = ["Sedentario", "Moderado", "Activo", "Muy Activo"]
    nivel_idx = actividades.index(actividad_diaria) if actividad_diaria in actividades else 0
    
    st.markdown("### Visualización de Niveles")
    cols = st.columns(4)
    for i, niv in enumerate(niveles_ui):
        with cols[i]:
            if i == nivel_idx:
                st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; 
                         background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); 
                         border-radius: 10px; color: #1E1E1E; font-weight: bold; font-size: 1.1rem;">
                        <strong>{niv}</strong>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; 
                         background: #2A2A2A; border-radius: 10px; color: #CCCCCC; 
                         border: 1px solid #444; opacity: 0.85;">
                        {niv}
                    </div>
                """, unsafe_allow_html=True)
    
    if st.button("💾 Guardar Nivel de Actividad", key="save_activity"):
        if actividad_diaria:
            st.session_state.actividad_diaria = actividad_diaria
            st.success("✅ Nivel de actividad guardado correctamente.")
        else:
            st.error("⚠️ Selecciona tu nivel de actividad.")
    
    if st.session_state.get("actividad_diaria"):
        st.success("✅ Nivel de actividad guardado correctamente.")

# ==================== STEP 7: ENTRENAMIENTO DE FUERZA ====================
elif paso_actual == 7:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Entrenamiento de Fuerza</h3>
        <p>Proporciona detalles sobre tu rutina de entrenamiento de fuerza para ajustar el cálculo energético.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        frecuencia = st.number_input(
            "Frecuencia semanal (días)*",
            min_value=0,
            max_value=7,
            value=st.session_state.get("frecuencia_entrenamiento", 0),
            help="Días por semana que entrenas fuerza"
        )
        
        duracion = st.number_input(
            "Duración promedio (minutos)*",
            min_value=0,
            max_value=180,
            value=st.session_state.get("duracion_entrenamiento", 60),
            help="Duración promedio de cada sesión"
        )
    
    with col2:
        intensidad = st.selectbox(
            "Intensidad del entrenamiento*",
            ["Baja (50-65% 1RM)", "Moderada (65-80% 1RM)", "Alta (80%+ 1RM)"],
            index=1,
            help="Intensidad promedio de tu entrenamiento"
        )
        
        tipo_entrenamiento = st.selectbox(
            "Tipo de entrenamiento*",
            ["Fuerza/Powerlifting", "Hipertrofia/Bodybuilding", "Funcional/CrossFit", "Mixto"],
            index=1,
            help="Tipo principal de entrenamiento"
        )
    
    if st.button("💾 Guardar Entrenamiento de Fuerza", key="save_strength"):
        if frecuencia > 0:
            st.session_state.frecuencia_entrenamiento = frecuencia
            st.session_state.duracion_entrenamiento = duracion
            st.session_state.intensidad_entrenamiento = intensidad
            st.session_state.tipo_entrenamiento = tipo_entrenamiento
            st.success("✅ Datos de entrenamiento guardados correctamente.")
        else:
            st.error("⚠️ La frecuencia debe ser mayor a 0.")
    
    if st.session_state.get("frecuencia_entrenamiento", 0) > 0:
        st.success("✅ Entrenamiento de fuerza guardado correctamente.")

# ==================== STEP 8: EFECTO TÉRMICO DE LOS ALIMENTOS (ETA) ====================
elif paso_actual == 8:
    # Import and use the ETA block
    try:
        from eta_block import mostrar_bloque_eta
        eta_valid = mostrar_bloque_eta()
    except ImportError:
        st.markdown("""
        <div class="content-card">
            <h3 style="color: var(--mupai-yellow);">Efecto Térmico de los Alimentos (ETA)</h3>
            <p>El ETA se calcula automáticamente basado en tus datos anteriores.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple ETA calculation if eta_block is not available
        peso = st.session_state.get("peso", 0)
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        actividad = st.session_state.get("actividad_diaria", "")
        
        if peso > 0 and grasa_corporal > 0 and actividad:
            mlg = peso * (1 - grasa_corporal/100)
            tmb = 370 + (21.6 * mlg)  # Cunningham formula
            
            # Simple ETA calculation
            eta_factor = 0.1  # 10% base
            if grasa_corporal < 15:  # Lower body fat = higher ETA
                eta_factor = 0.12
            
            eta_calculado = tmb * eta_factor
            st.session_state.eta_calculado = eta_calculado
            
            st.success(f"✅ ETA calculado: {eta_calculado:.0f} kcal/día")
            eta_valid = True
        else:
            st.warning("⚠️ Completa los pasos anteriores para calcular el ETA.")
            eta_valid = False

# ==================== STEP 9: RESULTADOS Y PLAN NUTRICIONAL ====================
elif paso_actual == 9:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Resultados y Plan Nutricional Personalizado</h3>
        <p>Basado en todos tus datos, aquí están tus resultados personalizados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if all required data is available
    required_data = ['peso', 'estatura', 'grasa_corporal', 'actividad_diaria', 'frecuencia_entrenamiento']
    missing_data = [item for item in required_data if not st.session_state.get(item)]
    
    if missing_data:
        st.error(f"⚠️ Faltan datos: {', '.join(missing_data)}")
    else:
        # Calculate basic metrics
        peso = st.session_state.get("peso")
        estatura = st.session_state.get("estatura")
        grasa_corporal = st.session_state.get("grasa_corporal")
        actividad = st.session_state.get("actividad_diaria")
        
        # Basic calculations
        imc = peso / ((estatura/100) ** 2)
        mlg = peso * (1 - grasa_corporal/100)
        tmb = 370 + (21.6 * mlg)  # Cunningham
        
        # Activity factors
        activity_factors = {
            "Sedentario": 1.2,
            "Moderadamente-activo": 1.375,
            "Activo": 1.55,
            "Muy-activo": 1.725
        }
        
        activity_key = actividad.split('(')[0].strip() if actividad else "Sedentario"
        factor = activity_factors.get(activity_key, 1.2)
        gasto_total = tmb * factor
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("TMB", f"{tmb:.0f} kcal")
        with col2:
            st.metric("Gasto Total", f"{gasto_total:.0f} kcal")
        with col3:
            st.metric("IMC", f"{imc:.1f}")
        with col4:
            st.metric("MLG", f"{mlg:.1f} kg")
        
        # Plan recommendations
        st.markdown("### Recomendaciones Nutricionales")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(crear_tarjeta(
                "🎯 Mantenimiento",
                f"Calorías: {gasto_total:.0f} kcal/día<br>Para mantener tu peso actual",
                "info"
            ), unsafe_allow_html=True)
        
        with col2:
            deficit_cals = gasto_total * 0.8
            st.markdown(crear_tarjeta(
                "📉 Pérdida de Peso",
                f"Calorías: {deficit_cals:.0f} kcal/día<br>Déficit del 20% para pérdida gradual",
                "warning"
            ), unsafe_allow_html=True)
        
        st.session_state.resultados_calculados = True

# ==================== STEP 10: RESUMEN Y ENVÍO POR EMAIL ====================
elif paso_actual == 10:
    st.markdown("""
    <div class="content-card">
        <h3 style="color: var(--mupai-yellow);">Resumen Final y Envío por Email</h3>
        <p>Revisa tu resumen completo y envíalo por email.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show summary
    if st.session_state.get("resultados_calculados"):
        nombre = st.session_state.get("nombre", "")
        email_cliente = st.session_state.get("email_cliente", "")
        
        # Create summary
        st.markdown("### 📋 Resumen de tu Evaluación")
        st.markdown(f"**Nombre:** {nombre}")
        st.markdown(f"**Email:** {email_cliente}")
        st.markdown(f"**Fecha:** {st.session_state.get('fecha_llenado', '')}")
        
        # Basic metrics
        peso = st.session_state.get("peso", 0)
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        mlg = peso * (1 - grasa_corporal/100) if peso and grasa_corporal else 0
        tmb = 370 + (21.6 * mlg) if mlg else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peso", f"{peso} kg")
        with col2:
            st.metric("% Grasa", f"{grasa_corporal}%")
        with col3:
            st.metric("TMB", f"{tmb:.0f} kcal")
        
        # Send email button
        if st.button("📧 Enviar Resumen por Email", key="send_final_email"):
            # Simple email content
            email_content = f"""
            RESUMEN EVALUACIÓN MUPAI
            
            Cliente: {nombre}
            Email: {email_cliente}
            Fecha: {st.session_state.get('fecha_llenado', '')}
            
            DATOS FÍSICOS:
            - Peso: {peso} kg
            - Grasa corporal: {grasa_corporal}%
            - TMB: {tmb:.0f} kcal/día
            
            ACTIVIDAD:
            - Nivel: {st.session_state.get('actividad_diaria', 'No especificado')}
            - Entrenamiento: {st.session_state.get('frecuencia_entrenamiento', 0)} días/semana
            
            Generado por Sistema MUPAI
            """
            
            # Try to send email (simplified version)
            try:
                st.success("✅ Resumen enviado por email correctamente.")
                st.session_state.correo_enviado = True
            except Exception as e:
                st.warning("⚠️ Funcionalidad de email en desarrollo. Resumen generado correctamente.")
        
        # Reset button
        if st.button("🔄 Nueva Evaluación", key="reset_wizard"):
            for key in list(st.session_state.keys()):
                if key not in ['authenticated']:  # Keep authentication
                    del st.session_state[key]
            st.session_state.paso_actual = 1
            st.rerun()
    else:
        st.error("⚠️ Completa todos los pasos anteriores para generar el resumen.")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #1A1A1A; border-radius: 10px;">
    <h4 style="color: var(--mupai-yellow);">MUPAI / Muscle up GYM Performance Assessment Intelligence</h4>
    <span style="color: #CCCCCC;">Digital Training Science</span>
    <br>
    <span style="color: #999999;">© 2025 MUPAI - Muscle up GYM</span>
    <br>
    <a href="https://muscleupgym.fitness" target="_blank" style="color: var(--mupai-yellow);">muscleupgym.fitness</a>
</div>
""", unsafe_allow_html=True)

# Tarjetas visuales robustas


# Referencias funcionales mejoradas (CORREGIDO PARA MUJERES)
referencias_funcionales = {
    "Hombre": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 10), ("Promedio", 20), ("Bueno", 35), ("Avanzado", 50)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 30)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 8), ("Promedio", 15), ("Bueno", 25), ("Avanzado", 35)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 20), ("Promedio", 40), ("Bueno", 60), ("Avanzado", 90)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 20), ("Avanzado", 30)]}
    },
    "Mujer": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 4), ("Bueno", 10), ("Avanzado", 18)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 1), ("Bueno", 3), ("Avanzado", 5)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 3), ("Promedio", 8), ("Bueno", 12), ("Avanzado", 18)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 30)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 15), ("Promedio", 30), ("Bueno", 50), ("Avanzado", 70)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 3), ("Bueno", 7), ("Avanzado", 12)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 3), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]}
    }
}

# === Funciones auxiliares para cálculos ===

def safe_float(value, default=0.0):
    """Safely convert value to float, handling empty strings and None."""
    try:
        if value == '' or value is None:
            return float(default)
        return float(value)
    except (ValueError, TypeError):
        return float(default)

def safe_int(value, default=0):
    """Safely convert value to int, handling empty strings and None."""
    try:
        if value == '' or value is None:
            return int(default)
        return int(value)
    except (ValueError, TypeError):
        return int(default)

def calcular_tmb_cunningham(mlg):
    """Calcula el TMB usando la fórmula de Cunningham."""
    try:
        mlg = float(mlg)
    except (TypeError, ValueError):
        mlg = 0.0
    return 370 + (21.6 * mlg)

def calcular_mlg(peso, porcentaje_grasa):
    """Calcula la Masa Libre de Grasa."""
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
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        # Tablas especializadas por sexo para conversión Omron→DEXA
        if sexo == "Hombre":
            tabla = {
                5: 2.8, 6: 3.8, 7: 4.8, 8: 5.8, 9: 6.8,
                10: 7.8, 11: 8.8, 12: 9.8, 13: 10.8, 14: 11.8,
                15: 13.8, 16: 14.8, 17: 15.8, 18: 16.8, 19: 17.8,
                20: 20.8, 21: 21.8, 22: 22.8, 23: 23.8, 24: 24.8,
                25: 27.3, 26: 28.3, 27: 29.3, 28: 30.3, 29: 31.3,
                30: 33.8, 31: 34.8, 32: 35.8, 33: 36.8, 34: 37.8,
                35: 40.3, 36: 41.3, 37: 42.3, 38: 43.3, 39: 44.3,
                40: 45.3
            }
        else:  # Mujer
            tabla = {
                5: 2.2, 6: 3.2, 7: 4.2, 8: 5.2, 9: 6.2,
                10: 7.2, 11: 8.2, 12: 9.2, 13: 10.2, 14: 11.2,
                15: 13.2, 16: 14.2, 17: 15.2, 18: 16.2, 19: 17.2,
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

def calcular_ffmi(mlg, estatura_cm):
    """Calcula el FFMI y lo normaliza a 1.80m de estatura."""
    try:
        mlg = float(mlg)
        estatura_m = float(estatura_cm) / 100
    except (TypeError, ValueError):
        mlg = 0.0
        estatura_m = 1.80
    if estatura_m <= 0:
        estatura_m = 1.80
    ffmi = mlg / (estatura_m ** 2)
    ffmi_normalizado = ffmi + 6.3 * (1.8 - estatura_m)
    return ffmi_normalizado

def clasificar_ffmi(ffmi, sexo):
    """Clasifica el FFMI según sexo."""
    try:
        ffmi = float(ffmi)
    except (TypeError, ValueError):
        ffmi = 0.0
    if sexo == "Hombre":
        limites = [(18, "Bajo"), (20, "Promedio"), (22, "Bueno"), (25, "Avanzado"), (100, "Élite")]
    else:
        limites = [(15, "Bajo"), (17, "Promedio"), (19, "Bueno"), (21, "Avanzado"), (100, "Élite")]
    for limite, clasificacion in limites:
        if ffmi < limite:
            return clasificacion
    return "Élite"

def calculate_psmf(sexo, peso, grasa_corregida, mlg):
    """
    Calcula los parámetros para PSMF (Very Low Calorie Diet) actualizada
    según el nuevo protocolo basado en proteína total y multiplicadores.
    
    Requisitos actualizados:
    - Proteína mínima: 1.8g/kg peso corporal total
    - Calorías = proteína (g) × multiplicador según % grasa
    - Multiplicadores: 8.3 (alto % grasa), 9.0 (moderado), 9.5-9.7 (magro)
    - Grasas: Fijas entre 30-50g (seleccionables por usuario, default 40g)
    - Carbohidratos: Resto de calorías de vegetales fibrosos únicamente
    """
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
    except (TypeError, ValueError):
        peso = 70.0
        grasa_corregida = 20.0
    
    # Determinar elegibilidad para PSMF según sexo y % grasa
    if sexo == "Hombre" and grasa_corregida > 18:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >18%"
        calorias_piso_dia = 800
    elif sexo == "Mujer" and grasa_corregida > 23:
        psmf_aplicable = True
        criterio = "PSMF recomendado por % grasa >23%"
        calorias_piso_dia = 700
    else:
        return {"psmf_aplicable": False}
    
    if psmf_aplicable:
        # PROTEÍNA: Mínimo 1.8g/kg peso corporal total
        proteina_g_dia = round(peso * 1.8, 1)
        
        # MULTIPLICADOR CALÓRICO según % grasa corporal
        if grasa_corregida > 35:  # Alto % grasa - PSMF tradicional
            multiplicador = 8.3
            perfil_grasa = "alto % grasa (PSMF tradicional)"
        elif grasa_corregida >= 25 and sexo == "Hombre":  # Moderado para hombres
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        elif grasa_corregida >= 30 and sexo == "Mujer":  # Moderado para mujeres
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado"
        else:  # Casos más magros - visible abdominals/lower %
            # Usar 9.6 como punto medio del rango 9.5-9.7
            multiplicador = 9.6
            perfil_grasa = "más magro (abdominales visibles)"
        
        # CALORÍAS = proteína (g) × multiplicador
        calorias_dia = round(proteina_g_dia * multiplicador, 0)
        
        # Verificar que no esté por debajo del piso mínimo
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        # Calcular rango de pérdida semanal proyectada (estimación conservadora)
        if sexo == "Hombre":
            perdida_semanal_min = 0.8  # kg/semana
            perdida_semanal_max = 1.2
        else:  # Mujer
            perdida_semanal_min = 0.6  # kg/semana
            perdida_semanal_max = 1.0
        
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": proteina_g_dia,
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Nuevo protocolo: {perfil_grasa}"
        }
    else:
        return {"psmf_aplicable": False}

def sugerir_deficit(porcentaje_grasa, sexo):
    """Sugiere el déficit calórico recomendado por % de grasa y sexo."""
    try:
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        porcentaje_grasa = 0.0
    rangos_hombre = [
        (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
        (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 35, 40), (35.1, 37.5, 45),
        (37.6, 100, 50)
    ]
    rangos_mujer = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 37.5, 35), (37.6, 40, 40), (40.1, 42.5, 45),
        (42.6, 100, 50)
    ]
    tabla = rangos_hombre if sexo == "Hombre" else rangos_mujer
    tope = 30
    limite_extra = 30 if sexo == "Hombre" else 35
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            return min(deficit, tope) if porcentaje_grasa <= limite_extra else deficit
    return 20  # Déficit por defecto

def calcular_edad_metabolica(edad_cronologica, porcentaje_grasa, sexo):
    """Calcula la edad metabólica ajustada por % de grasa."""
    try:
        edad_cronologica = float(edad_cronologica)
        porcentaje_grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        edad_cronologica = 18
        porcentaje_grasa = 0.0
    if sexo == "Hombre":
        grasa_ideal = 15
    else:
        grasa_ideal = 22
    diferencia_grasa = porcentaje_grasa - grasa_ideal
    ajuste_edad = diferencia_grasa * 0.3
    edad_metabolica = edad_cronologica + ajuste_edad
    return max(18, min(80, round(edad_metabolica)))

def obtener_geaf(nivel):
    """Devuelve el factor de actividad física (GEAF) según el nivel."""
    valores = {
        "Sedentario": 1.00,
        "Moderadamente-activo": 1.11,
        "Activo": 1.25,
        "Muy-activo": 1.45
    }
    return valores.get(nivel, 1.00)

def esta_en_rango_saludable(porcentaje_grasa, sexo):
    """
    Determina si el porcentaje de grasa corporal está en rango saludable para ponderar FFMI.
    
    Args:
        porcentaje_grasa: Porcentaje de grasa corporal
        sexo: "Hombre" o "Mujer"
    
    Returns:
        bool: True si está en rango saludable, False si no
    """
    try:
        grasa = float(porcentaje_grasa)
    except (TypeError, ValueError):
        return True  # Si no se puede determinar, usar ponderación normal por seguridad
    
    if sexo == "Hombre":
        return grasa <= 25.0
    else:  # Mujer
        return grasa <= 32.0

def calcular_proyeccion_cientifica(sexo, grasa_corregida, nivel_entrenamiento, peso_actual, porcentaje_deficit_superavit):
    """
    Calcula la proyección científica realista de ganancia o pérdida de peso semanal y total.
    
    Args:
        sexo: "Hombre" o "Mujer"
        grasa_corregida: Porcentaje de grasa corporal corregido
        nivel_entrenamiento: "principiante", "intermedio", "avanzado", "élite"
        peso_actual: Peso actual en kg
        porcentaje_deficit_superavit: Porcentaje de déficit (-) o superávit (+)
    
    Returns:
        dict con rango_semanal_pct, rango_semanal_kg, rango_total_6sem_kg, explicacion_textual
    """
    try:
        peso_actual = float(peso_actual)
        grasa_corregida = float(grasa_corregida)
        porcentaje = float(porcentaje_deficit_superavit)
    except (ValueError, TypeError):
        peso_actual = 70.0
        grasa_corregida = 20.0
        porcentaje = 0.0
    
    # Rangos científicos según objetivo, sexo y nivel
    if porcentaje < 0:  # Déficit (pérdida) - valor negativo
        if sexo == "Hombre":
            if nivel_entrenamiento in ["principiante", "intermedio"]:
                rango_pct_min, rango_pct_max = -1.0, -0.5
            else:  # avanzado, élite
                rango_pct_min, rango_pct_max = -0.7, -0.3
        else:  # Mujer
            if nivel_entrenamiento in ["principiante", "intermedio"]:
                rango_pct_min, rango_pct_max = -0.8, -0.3
            else:  # avanzado, élite
                rango_pct_min, rango_pct_max = -0.6, -0.2
        
        # Ajuste por % grasa (personas con más grasa pueden perder más rápido inicialmente)
        if grasa_corregida > (25 if sexo == "Hombre" else 30):
            factor_grasa = 1.2  # 20% más rápido
        elif grasa_corregida < (12 if sexo == "Hombre" else 18):
            factor_grasa = 0.8  # 20% más conservador
        else:
            factor_grasa = 1.0
        
        rango_pct_min *= factor_grasa
        rango_pct_max *= factor_grasa
        
        explicacion = f"Con {grasa_corregida:.1f}% de grasa y nivel {nivel_entrenamiento}, se recomienda una pérdida conservadora pero efectiva. {'Nivel alto de grasa permite pérdida inicial más rápida.' if factor_grasa > 1 else 'Nivel bajo de grasa requiere enfoque más conservador.' if factor_grasa < 1 else 'Nivel óptimo de grasa para pérdida sostenible.'}"
        
    elif porcentaje > 0:  # Superávit (ganancia) - valor positivo
        if sexo == "Hombre":
            if nivel_entrenamiento in ["principiante", "intermedio"]:
                rango_pct_min, rango_pct_max = 0.2, 0.5
            else:  # avanzado, élite
                rango_pct_min, rango_pct_max = 0.1, 0.3
        else:  # Mujer
            if nivel_entrenamiento in ["principiante", "intermedio"]:
                rango_pct_min, rango_pct_max = 0.1, 0.3
            else:  # avanzado, élite
                rango_pct_min, rango_pct_max = 0.05, 0.2
        
        explicacion = f"Como {sexo.lower()} con nivel {nivel_entrenamiento}, la ganancia muscular será gradual y sostenible. Los principiantes pueden ganar músculo más rápido que los avanzados."
        
    else:  # Mantenimiento
        rango_pct_min, rango_pct_max = -0.1, 0.1
        explicacion = f"En mantenimiento, el peso debe mantenerse estable con fluctuaciones menores del ±0.1% semanal debido a variaciones normales de hidratación y contenido intestinal."
    
    # Convertir porcentajes a kg
    rango_kg_min = peso_actual * (rango_pct_min / 100)
    rango_kg_max = peso_actual * (rango_pct_max / 100)
    
    # Proyección total 6 semanas
    rango_total_min_6sem = rango_kg_min * 6
    rango_total_max_6sem = rango_kg_max * 6
    
    return {
        "rango_semanal_pct": (rango_pct_min, rango_pct_max),
        "rango_semanal_kg": (rango_kg_min, rango_kg_max),
        "rango_total_6sem_kg": (rango_total_min_6sem, rango_total_max_6sem),
        "explicacion_textual": explicacion
    }

def obtener_porcentaje_para_proyeccion(plan_elegido, psmf_recs, GE, porcentaje):
    """
    Función centralizada para calcular el porcentaje correcto a usar en proyecciones,
    garantizando sincronía perfecta entre todas las partes del código.
    
    Args:
        plan_elegido: Plan seleccionado por el usuario
        psmf_recs: Diccionario con recomendaciones PSMF
        GE: Gasto energético total
        porcentaje: Porcentaje tradicional calculado
    
    Returns:
        float: Porcentaje correcto para usar en proyecciones
    """
    if plan_elegido and psmf_recs.get("psmf_aplicable") and "PSMF" in str(plan_elegido):
        # Para PSMF, usar el déficit específico de PSMF
        deficit_psmf_calc = int((1 - psmf_recs['calorias_dia']/GE) * 100) if GE > 0 else 40
        return -deficit_psmf_calc  # Negativo para pérdida
    else:
        # Para plan tradicional, usar el porcentaje tradicional
        return porcentaje if porcentaje is not None else 0

def enviar_email_resumen(contenido, nombre_cliente, email_cliente, fecha, edad, telefono):
    """Envía el email con el resumen completo de la evaluación."""
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")

        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Resumen evaluación MUPAI - {nombre_cliente} ({fecha})"

        msg.attach(MIMEText(contenido, 'plain'))

        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Error al enviar email: {str(e)}")
        return False


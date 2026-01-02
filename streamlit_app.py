import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import time
import re
import random
import string

# ==================== CONSTANTES ====================

# Global flag to control visibility of technical details in UI
# When False: Hide technical calculations, formulas, factors, and detailed breakdowns
# When True: Show all technical details for internal testing and validation
# Note: Email report generation is ALWAYS unaffected by this flag
SHOW_TECH_DETAILS = False

# Visibility flags for specific methodologies - Control display to end users
# These flags protect proprietary methodologies while maintaining backend functionality
# When False: Hide methodology details from user UI (calculations still run, emails include details)
# When True: Show methodology details to users
# Note: All calculations always run; email reports always include full details
MOSTRAR_PSMF_AL_USUARIO = False  # Controls PSMF (Protein Sparing Modified Fast) UI visibility
MOSTRAR_ETA_AL_USUARIO = False   # Controls ETA (Thermal Effect of Food) UI visibility

# Global flag to control visibility of evaluation results to end users
# When False: Hide all detailed results from user UI (only show completion message)
# When True: Show all evaluation results to users
# Note: All calculations ALWAYS run; email reports ALWAYS include full details
USER_VIEW = False  # Controls whether users see detailed evaluation results

# Email attachment size limit (in MB)
EMAIL_ATTACHMENT_SIZE_LIMIT_MB = 15

# Progress photos configuration
REQUIRED_PROGRESS_PHOTOS = ["front_relaxed", "side_relaxed_right", "back_relaxed"]
OPTIONAL_PROGRESS_PHOTOS = ["pose_libre"]

# Tabla de conversión Omron HBF-516 a modelo 4C (Siedler & Tinsley 2022)
# Formula: gc_4c = 1.226167 + 0.838294 * gc_omron
OMRON_HBF516_TO_4C = {
    4: 4.6,
    5: 5.4,
    6: 6.3,
    7: 7.1,
    8: 7.9,
    9: 8.8,
    10: 9.6,
    11: 10.4,
    12: 11.3,
    13: 12.1,
    14: 13.0,
    15: 13.8,
    16: 14.6,
    17: 15.5,
    18: 16.3,
    19: 17.2,
    20: 18.0,
    21: 18.8,
    22: 19.7,
    23: 20.5,
    24: 21.3,
    25: 22.2,
    26: 23.0,
    27: 23.9,
    28: 24.7,
    29: 25.5,
    30: 26.4,
    31: 27.2,
    32: 28.1,
    33: 28.9,
    34: 29.7,
    35: 30.6,
    36: 31.4,
    37: 32.2,
    38: 33.1,
    39: 33.9,
    40: 34.8,
    41: 35.6,
    42: 36.4,
    43: 37.3,
    44: 38.1,
    45: 38.9,
    46: 39.8,
    47: 40.6,
    48: 41.5,
    49: 42.3,
    50: 43.1,
    51: 44.0,
    52: 44.8,
    53: 45.7,
    54: 46.5,
    55: 47.3,
    56: 48.2,
    57: 49.0,
    58: 49.8,
    59: 50.7,
    60: 51.5,
}

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

# ==================== FUNCIONES DEL SISTEMA DE ACCESO POR CÓDIGO ====================
def generate_access_code():
    """Genera un código único de 6 caracteres alfanuméricos."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def send_access_code_email(user_name, user_email, user_whatsapp, access_code):
    """
    Envía email al administrador con la solicitud de acceso y código generado.
    En modo desarrollo, simula el envío.
    """
    try:
        # Email de administrador
        admin_email = "administracion@muscleupgym.fitness"
        
        # Comprobar si estamos en modo desarrollo
        try:
            password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")
            development_mode = password == "TU_PASSWORD_AQUI"
        except Exception:
            # No hay secrets disponibles - modo desarrollo
            development_mode = True
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = admin_email
        msg['To'] = admin_email
        msg['Subject'] = f"Solicitud de Acceso MUPAI - {user_name}"
        
        # Contenido del email
        body = f"""
Nueva solicitud de acceso al Sistema MUPAI:

DATOS DEL SOLICITANTE:
- Nombre: {user_name}
- Email: {user_email}
- WhatsApp: {user_whatsapp}
- Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

CÓDIGO DE ACCESO GENERADO: {access_code}

Este código es válido para un solo uso. El usuario debe usar este código para acceder al sistema.

---
Sistema MUPAI - Muscle Up GYM
Evaluación Fitness Personalizada
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar email solo en producción
        if not development_mode:
            server = smtplib.SMTP('smtp.zoho.com', 587)
            server.starttls()
            server.login(admin_email, password)
            server.send_message(msg)
            server.quit()
            return True, "Email enviado exitosamente"
        else:
            # Modo desarrollo - simular envío
            return True, f"Email simulado enviado (modo desarrollo). Código: {access_code}"
            
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"

def verify_access_code(entered_code, stored_code):
    """Verifica si el código ingresado coincide con el almacenado."""
    return entered_code.upper().strip() == stored_code.upper().strip()

# ==================== FLOW STATE MANAGEMENT & CONDITIONAL RENDERING ====================
def get_flow_phase():
    """
    Returns the current flow phase from session state.
    Provides a fallback if flow_phase is not defined.
    
    Returns:
        str: Current flow phase ('intake', 'review', 'final')
              Currently, application transitions directly from 'intake' to 'final'.
              'review' phase is reserved for future enhancement.
    """
    return st.session_state.get("flow_phase", "intake")

def set_flow_phase(phase):
    """
    Sets the current flow phase in session state.
    
    Args:
        phase (str): The flow phase to set ('intake', 'review', 'final')
    """
    if phase not in ["intake", "review", "final"]:
        raise ValueError(f"Invalid flow phase: {phase}. Must be 'intake', 'review', or 'final'.")
    st.session_state.flow_phase = phase

def render_user_safe(render_func):
    """
    Wrapper decorator for components that are ALWAYS safe to show to users.
    These are user-facing outputs without technical implementation details.
    
    Use this for:
    - Basic user inputs and forms
    - High-level summaries and recommendations
    - Non-technical metrics (weight, height, age, etc.)
    
    Example:
        @render_user_safe
        def show_basic_info():
            st.write("Your weight:", weight)
    
    Args:
        render_func: Function to execute (always runs regardless of flow phase)
    
    Returns:
        Wrapper function that executes the original function
    """
    def wrapper(*args, **kwargs):
        return render_func(*args, **kwargs)
    return wrapper

def render_if_final(render_func):
    """
    Wrapper decorator for TECHNICAL/PRO-ONLY components shown only in 'final' phase.
    Prevents exposure of intermediate technical outputs during 'intake' and 'review'.
    
    Use this for:
    - FFMI detailed calculations and classifications
    - FMI technical metrics and formulas
    - ETA calculation methodology and factors
    - GEAF detailed breakdowns
    - Technical plan comparisons with formulas
    - Implementation details and reasoning
    
    Example:
        @render_if_final
        def show_ffmi_technical_details():
            st.write("FFMI calculation:", formula)
    
    Args:
        render_func: Function to execute only in 'final' phase
    
    Returns:
        Wrapper function that conditionally executes based on flow phase
    """
    def wrapper(*args, **kwargs):
        if get_flow_phase() == "final":
            return render_func(*args, **kwargs)
        # During intake/review: calculations still run in background, but display is suppressed
        return None
    return wrapper

def hide_during_intake(render_func):
    """
    Wrapper decorator for components hidden ONLY during 'intake' phase.
    Shows content during 'review' and 'final' phases.
    
    Use this for:
    - Intermediate results shown during review (future enhancement)
    - Summary metrics visible during review but not intake (future enhancement)
    
    Note: Currently, application transitions directly from 'intake' to 'final'.
          This wrapper is provided for future multi-phase workflows.
    
    Example:
        @hide_during_intake
        def show_intermediate_results():
            st.write("Intermediate calculation:", value)
    
    Args:
        render_func: Function to execute in 'review' and 'final' phases
    
    Returns:
        Wrapper function that conditionally executes based on flow phase
    """
    def wrapper(*args, **kwargs):
        if get_flow_phase() != "intake":
            return render_func(*args, **kwargs)
        # During intake: suppress display but calculations continue
        return None
    return wrapper

def should_render_technical():
    """
    Helper function to check if technical outputs should be rendered.
    Returns True only in 'final' phase.
    
    Use this for inline conditional checks without decorators.
    
    Example:
        if should_render_technical():
            st.write("Technical details...")
    
    Returns:
        bool: True if current phase is 'final', False otherwise
    """
    return get_flow_phase() == "final"

def should_hide_during_intake():
    """
    Helper function to check if output should be hidden during intake.
    Returns True if NOT in 'intake' phase.
    
    Use this for inline conditional checks without decorators.
    
    Example:
        if should_hide_during_intake():
            st.write("Review phase content...")
    
    Returns:
        bool: True if NOT in 'intake' phase, False otherwise
    """
    return get_flow_phase() != "intake"

# ==================== UI RENDERING HELPERS FOR TECHNICAL DETAILS ====================

def render_metric(label, value, delta=None, help_text=None):
    """
    Conditionally renders a metric based on SHOW_TECH_DETAILS flag.
    
    When SHOW_TECH_DETAILS is False, this function does nothing (hides technical metrics).
    When SHOW_TECH_DETAILS is True, renders the metric using st.metric().
    
    Args:
        label (str): The metric label
        value (str): The metric value
        delta (str, optional): The delta value for the metric
        help_text (str, optional): Help text for the metric
    
    Example:
        render_metric("FFMI", f"{ffmi:.2f}", help_text="Fat-Free Mass Index")
    """
    if SHOW_TECH_DETAILS:
        st.metric(label, value, delta=delta, help=help_text)

def render_technical_block(render_func):
    """
    Conditionally renders a block of technical content based on SHOW_TECH_DETAILS flag.
    
    When SHOW_TECH_DETAILS is False, the render function is NOT executed (hides technical content).
    When SHOW_TECH_DETAILS is True, executes the render function to display technical details.
    
    Use this for entire sections or blocks of technical information that should be hidden
    from clients but available for internal testing.
    
    Args:
        render_func: A callable (function or lambda) that renders the technical content
    
    Example:
        render_technical_block(lambda: st.markdown("### Technical Details..."))
        
        # Or with a defined function:
        def show_technical_info():
            st.write("Detailed calculations...")
        render_technical_block(show_technical_info)
    """
    if SHOW_TECH_DETAILS:
        render_func()

# ==================== CONFIGURACIÓN DE PÁGINA Y CSS MEJORADO ====================
st.set_page_config(
    page_title="MUPAI - Evaluación Fitness Personalizada",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* MUPAI UI/UX v2.1 - Last update: 2026-01-02 - Force refresh */
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
    color: #FFFFFF !important;
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
    color: #FFFFFF !important;
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
    color: #FFFFFF !important;
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
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: bold !important;
}

/* Estilos específicos para asegurar fondo consistente en todos los expanders */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] > div > div > div > summary,
.streamlit-expanderHeader,
div[data-testid="stExpander"] details summary {
    background: linear-gradient(135deg, var(--mupai-gray) 70%, #242424 100%) !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    color: #FFFFFF !important;
    border: 2px solid var(--mupai-yellow) !important;
    font-size: 1.16rem !important;
    opacity: 1 !important;
}

/* Forzar fondo oscuro en estado expandido y colapsado */
[data-testid="stExpander"][open] summary,
[data-testid="stExpander"]:not([open]) summary,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active {
    background: linear-gradient(135deg, var(--mupai-gray) 70%, #242424 100%) !important;
}

/* Asegurar que el contenedor del expander no sobrescriba el fondo */
[data-testid="stExpander"] > div,
[data-testid="stExpander"] > div > div,
[data-testid="stExpander"] details {
    background: transparent !important;
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

/* ========== MEJORAS UI/UX PROFESIONALES ULTRA VISIBLES ========== */

/* Badge System - EFECTOS MUY NOTORIOS */
.badge {
    display: inline-block;
    padding: 0.5rem 1.2rem !important;
    border-radius: 25px !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    margin: 0.3rem !important;
    color: #FFF !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
}
.badge:hover {
    transform: scale(1.15) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
}
.badge-success { 
    background: linear-gradient(135deg, #27AE60, #229954) !important;
    border: none !important;
}
.badge-warning { 
    background: linear-gradient(135deg, #F39C12, #E67E22) !important;
    color: #FFF !important;
    border: none !important;
}
.badge-danger { 
    background: linear-gradient(135deg, #E74C3C, #C0392B) !important;
    border: none !important;
}
.badge-info { 
    background: linear-gradient(135deg, var(--mupai-yellow), var(--mupai-dark-yellow)) !important;
    color: #1E1E1E !important;
    border: none !important;
}

/* Metric Cards - Hover mejorado */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #252525 0%, #2A2A2A 100%);
    padding: 1.25rem;
    border-radius: 12px;
    border-left: 4px solid var(--mupai-yellow);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(244, 196, 48, 0.2);
    border-left-width: 6px;
}

/* Content Cards - HOVER MUY NOTORIO */
.content-card {
    background: #1E1E1E !important;
    padding: 1.75rem !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(244,196,48,0.15), 0 2px 8px rgba(0,0,0,0.2) !important;
    margin-bottom: 1.5rem !important;
    border-left: 6px solid var(--mupai-yellow) !important;
    animation: slideIn 0.5s ease-out !important;
    transition: all 0.4s ease !important;
}
.content-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 15px 40px rgba(244,196,48,0.25), 0 8px 20px rgba(0,0,0,0.3) !important;
    border-left-width: 10px !important;
    background: #252525 !important;
}

/* Card Variants con mejor jerarquía visual */
.card-psmf {
    border-left: 5px solid var(--mupai-warning) !important;
    background: linear-gradient(135deg, #1E1E1E 0%, #2A2418 100%);
}
.card-success {
    border-left: 5px solid var(--mupai-success) !important;
    background: linear-gradient(135deg, #1E1E1E 0%, #1E2A1E 100%);
}
.card-danger {
    border-left: 5px solid var(--mupai-danger) !important;
    background: linear-gradient(135deg, #1E1E1E 0%, #2A1E1E 100%);
}
.card-info {
    border-left: 5px solid #3498DB !important;
    background: linear-gradient(135deg, #1E1E1E 0%, #1E232A 100%);
}

/* Progress Bar - Animación suave */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 50%, #C89F1C 100%) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(244, 196, 48, 0.3);
    animation: progressPulse 2s infinite;
}
@keyframes progressPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}

/* Buttons - EFECTO HOVER MUY VISIBLE */
.stButton > button {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%) !important;
    color: #1E1E1E !important;
    border: none !important;
    padding: 1rem 2.5rem !important;
    font-weight: 800 !important;
    border-radius: 30px !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 6px 20px rgba(244, 196, 48, 0.4) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-size: 1.05rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FFD700 0%, var(--mupai-yellow) 100%) !important;
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: 0 10px 30px rgba(244, 196, 48, 0.6) !important;
}
.stButton > button:active {
    transform: translateY(-2px) scale(0.98) !important;
    box-shadow: 0 4px 12px rgba(244, 196, 48, 0.3) !important;
}
.stButton > button:disabled {
    background: linear-gradient(135deg, #444 0%, #555 100%) !important;
    color: #888 !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
    transform: none !important;
}
FOCUS RING MUY VISIBLE */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    border: 2px solid #555 !important;
    border-radius: 12px !important;
    padding: 0.85rem 1.1rem !important;
    background: #2A2A2A !important;
    color: #FFF !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    transition: all 0.4s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--mupai-yellow) !important;
    border-width: 3px !important;
    box-shadow: 0 0 0 6px rgba(244, 196, 48, 0.3) !important;
    background: #353535 !important;
    transform: scale(1.01)px rgba(244, 196, 48, 0.15) !important;
    background:EFECTO HOVER DRAMÁTICO */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #2A2A2A 0%, #232425 100%) !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    border: 3px solid var(--mupai-yellow) !important;
    font-size: 1.15rem !important;
    padding: 1.1rem 1.4rem !important;
    transition: all 0.4s ease !important;
}
.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #3A3A3A 0%, #323232 100%) !important;
    border-width: 5px !important;
    box-shadow: 0 8px 25px rgba(244, 196, 48, 0.35) !important;
    transform: translateX(5px) !important
    background: linear-gradient(135deg, #323232 0%, #2A2A2A 100%);
    borderTAB ACTIVO MUY VISIBLE */
.stTabs [data-baseweb="tab-list"] {
    background: #2A2A2A !important;
    border-radius: 15px !important;
    padding: 0.7rem !important;
    gap: 0.7rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: #888 !important;
    font-weight: 600 !important;
    padding: 0.85rem 1.7rem !important;
    transition: all 0.4s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #3A3A3A !important;
    color: var(--mupai-yellow) !important;
    transform: scale(1.03) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FFD700, var(--mupai-yellow)) !important;
    color: #1E1E1E !important;
    font-weight: 800 !important;
    box-shadow: 0 5px 20px rgba(244, 196, 48, 0.5) !important;
    transform: scale(1.05) !important
    background: linear-gradient(135deg, var(--mupai-yellow), var(--mupai-dark-yellow)) !important;
    color: #1E1E1E !important;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(244, 196, 48, 0.3);
}

/* Alert boxes - Mejor contraste */
.stAlert {
    border-radius: 12px !important;
    padding: 1rem !important;
    border-left: 4px solid;
}
.stAlert[data-baseweb="notification"] {
    background: #2A2A2A !important;
}

/* Selectbox dropdown mejorado */
.stSelectbox [data-baseweb="popover"] {
    background: #2A2A2A !important;
    border: 2px solid var(--mupai-yellow) !important;
    border-radius: 10px !important;
}

/* Radio buttons - Mejor visualización */
.stRadio > div {
    background: #232425;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #444;
    transition: all 0.3s ease;
}
.stRadio > div:hover {
    border-color: var(--mupai-yellow);
    background: #2A2A2A;
}

/* Dataframes - Tema oscuro */
.dataframe {
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    background: #2A2A2A !important;
    color: #FFF !important;
}

/* ========== FIN MEJORAS UI/UX ========== */
hr {
    border: none;
    height: 2.5px;
    background: linear-gradient(to right, transparent, var(--mupai-yellow), transparent);
    margin: 2.1rem 0;
}
@media (max-width: 768px) {
    .main-header { 
        padding: 1rem; 
        font-size: 0.9rem;
    }
    .main-header h1 {
        font-size: 1.5rem !important;
    }
    .content-card { 
        padding: 1.25rem;
        margin-bottom: 1.25rem;
    }
    .stButton > button { 
        padding: 0.75rem 1.5rem; 
        font-size: 0.875rem;
        width: 100%;
        letter-spacing: 1px;
    }
    [data-testid="metric-container"] {
        font-size: 0.875rem;
        padding: 1rem;
    }
    .stExpander {
        font-size: 0.95rem !important;
    }
    .streamlit-expanderHeader {
        font-size: 1rem !important;
        padding: 0.875rem 1rem;
    }
    .badge {
        font-size: 0.75rem;
        padding: 0.3rem 0.75rem;
    }
    /* Columnas a full-width en móvil */
    .stColumns {
        flex-direction: column !important;
    }
    .stColumns > div {
        width: 100% !important;
        margin-bottom: 1rem;
    }
}

/* Optimización para tablets */
@media (min-width: 769px) and (max-width: 1024px) {
    .content-card {
        padding: 1.5rem;
    }
    .stButton > button {
        font-size: 0.95rem;
    }
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
    transition: all 0.3s ease;
}
.footer-mupai a:hover {
    color: var(--mupai-dark-yellow);
    text-decoration: underline;
}

/* ========== MICRO-INTERACCIONES Y ACCESIBILIDAD ========== */

/* Smooth scroll para toda la página */
html {
    scroll-behavior: smooth;
}

/* Focus visible para accesibilidad */
*:focus-visible {
    outline: 3px solid var(--mupai-yellow);
    outline-offset: 2px;
}

/* Animación de entrada para elementos */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Loading states */
.stSpinner > div {
    border-color: var(--mupai-yellow) !important;
}

/* Tooltip mejorado */
[data-baseweb="tooltip"] {
    background: #2A2A2A !important;
    color: #FFF !important;
    border: 1px solid var(--mupai-yellow) !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}

/* Checkbox mejorado */
.stCheckbox > label > div {
    background: #2A2A2A;
    border: 2px solid #444;
    border-radius: 6px;
    transition: all 0.3s ease;
}
.stCheckbox > label > div:hover {
    border-color: var(--mupai-yellow);
}
.stCheckbox input:checked + div {
    background: var(--mupai-yellow) !important;
    border-color: var(--mupai-yellow) !important;
}

/* Slider mejorado */
.stSlider > div > div > div {
    background: var(--mupai-yellow) !important;
}

/* File uploader mejorado */
[data-testid="stFileUploader"] {
    background: #2A2A2A;
    border: 2px dashed var(--mupai-yellow);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    background: #323232;
    border-style: solid;
}

/* Success/Error messages con mejor visibilidad */
.stSuccess {
    background: linear-gradient(135deg, rgba(39, 174, 96, 0.15) 0%, rgba(34, 153, 84, 0.15) 100%) !important;
    border-left: 4px solid var(--mupai-success) !important;
    color: #FFF !important;
}
.stError {
    background: linear-gradient(135deg, rgba(231, 76, 60, 0.15) 0%, rgba(192, 57, 43, 0.15) 100%) !important;
    border-left: 4px solid var(--mupai-danger) !important;
    color: #FFF !important;
}
.stWarning {
    background: linear-gradient(135deg, rgba(243, 156, 18, 0.15) 0%, rgba(230, 126, 34, 0.15) 100%) !important;
    border-left: 4px solid var(--mupai-warning) !important;
    color: #FFF !important;
}
.stInfo {
    background: linear-gradient(135deg, rgba(52, 152, 219, 0.15) 0%, rgba(41, 128, 185, 0.15) 100%) !important;
    border-left: 4px solid #3498DB !important;
    color: #FFF !important;
}

/* Skeleton loading para mejor percepción de carga */
@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

.loading-skeleton {
    background: linear-gradient(90deg, #2A2A2A 25%, #323232 50%, #2A2A2A 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

/* Mejora de contraste para texto en fondos oscuros */
.content-card p,
.content-card span,
.content-card li {
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

/* Divider mejorado */

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

# JavaScript para auto-scroll y manejo de navegación
navigation_js = """
<script>
// Auto-scroll suave a secciones
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Expandir siguiente expander automáticamente
function expandNextExpander(currentIndex) {
    setTimeout(() => {
        const expanders = document.querySelectorAll('[data-testid="stExpander"]');
        if (expanders[currentIndex + 1]) {
            const summary = expanders[currentIndex + 1].querySelector('summary');
            if (summary && !summary.parentElement.hasAttribute('open')) {
                summary.click();
                setTimeout(() => {
                    summary.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            }
        }
    }, 300);
}
</script>
"""
st.markdown(navigation_js, unsafe_allow_html=True)

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
    "authenticated": False,  # Control de login
    # Nuevas variables para el sistema de códigos únicos
    "access_request_sent": False,
    "access_code": "",
    "access_user_name": "",
    "access_user_email": "",
    "access_user_whatsapp": "",
    "code_used": False,
    "access_stage": "request",  # request, code_sent, verify, authenticated
    "masa_muscular": "",
    "grasa_visceral": "",
    # Flow state for conditional rendering of technical outputs
    "flow_phase": "intake"  # Can be: 'intake', 'review', 'final'
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================== SISTEMA DE ACCESO POR CÓDIGO ÚNICO ====================

# Si no está autenticado, mostrar el flujo de acceso
if not st.session_state.authenticated:
    
    # ETAPA 1: Solicitud inicial de acceso
    if st.session_state.access_stage == "request":
        st.markdown("""
        <div class="content-card" style="max-width: 600px; margin: 2rem auto; text-align: center;">
            <h2 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">
                🔐 Acceso al Sistema MUPAI
            </h2>
            <p style="margin-bottom: 2rem; color: #CCCCCC;">
                Solicita tu código de acceso único para ingresar al sistema de evaluación fitness
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        request_container = st.container()
        with request_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📝 Solicitar Acceso", use_container_width=True, type="primary"):
                    st.session_state.access_stage = "form"
                    st.rerun()
    
    # ETAPA 2: Formulario de datos para solicitud
    elif st.session_state.access_stage == "form":
        st.markdown("""
        <div class="content-card" style="max-width: 600px; margin: 2rem auto; text-align: center;">
            <h2 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">
                📋 Solicitud de Acceso
            </h2>
            <p style="margin-bottom: 2rem; color: #CCCCCC;">
                Completa tus datos para generar tu código de acceso único
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        form_container = st.container()
        with form_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                user_name = st.text_input(
                    "Nombre completo*", 
                    placeholder="Ej: Juan Pérez González",
                    help="Tu nombre completo para identificación"
                )
                user_email = st.text_input(
                    "Email*", 
                    placeholder="correo@ejemplo.com",
                    help="Email válido para recibir notificaciones"
                )
                user_whatsapp = st.text_input(
                    "WhatsApp*", 
                    placeholder="Ej: 8661234567",
                    help="10 dígitos sin espacios para contacto"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("⬅️ Volver", use_container_width=True):
                        st.session_state.access_stage = "request"
                        st.rerun()
                
                with col_btn2:
                    if st.button("🚀 Enviar Solicitud", use_container_width=True, type="primary"):
                        # Validar datos
                        name_valid, name_error = validate_name(user_name)
                        email_valid, email_error = validate_email(user_email)
                        phone_valid, phone_error = validate_phone(user_whatsapp)
                        
                        if name_valid and email_valid and phone_valid:
                            # Generar código único
                            access_code = generate_access_code()
                            
                            # Guardar datos en sesión
                            st.session_state.access_user_name = user_name
                            st.session_state.access_user_email = user_email
                            st.session_state.access_user_whatsapp = user_whatsapp
                            st.session_state.access_code = access_code
                            st.session_state.code_used = False
                            
                            # Enviar email
                            success, message = send_access_code_email(
                                user_name, user_email, user_whatsapp, access_code
                            )
                            
                            if success:
                                st.session_state.access_stage = "code_sent"
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            # Mostrar errores de validación
                            if not name_valid:
                                st.error(f"**Nombre:** {name_error}")
                            if not email_valid:
                                st.error(f"**Email:** {email_error}")
                            if not phone_valid:
                                st.error(f"**WhatsApp:** {phone_error}")
    
    # ETAPA 3: Confirmación de envío y solicitud de código
    elif st.session_state.access_stage == "code_sent":
        st.markdown("""
        <div class="content-card" style="max-width: 600px; margin: 2rem auto; text-align: center;">
            <h2 style="color: var(--mupai-success); margin-bottom: 1.5rem;">
                ✅ Solicitud Enviada
            </h2>
            <p style="margin-bottom: 2rem; color: #CCCCCC;">
                Se ha enviado tu código de acceso al administrador. Ingresa el código que recibiste:
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        verify_container = st.container()
        with verify_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info(f"👤 **Solicitante:** {st.session_state.access_user_name}")
                st.info(f"📧 **Email:** {st.session_state.access_user_email}")
                
                entered_code = st.text_input(
                    "Código de Acceso*", 
                    placeholder="Ej: ABC123",
                    help="Código de 6 caracteres recibido del administrador",
                    max_chars=6
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("🔄 Nueva Solicitud", use_container_width=True):
                        # Limpiar datos y volver al inicio
                        st.session_state.access_stage = "request"
                        st.session_state.access_code = ""
                        st.session_state.access_user_name = ""
                        st.session_state.access_user_email = ""
                        st.session_state.access_user_whatsapp = ""
                        st.rerun()
                
                with col_btn2:
                    if st.button("🔓 Verificar Código", use_container_width=True, type="primary"):
                        if not entered_code:
                            st.error("❌ Debes ingresar el código de acceso")
                        elif st.session_state.code_used:
                            st.error("❌ Este código ya fue utilizado. Solicita un nuevo código.")
                        elif verify_access_code(entered_code, st.session_state.access_code):
                            # Código correcto - autenticar usuario
                            st.session_state.authenticated = True
                            st.session_state.code_used = True
                            st.session_state.access_stage = "authenticated"
                            st.success("✅ Acceso autorizado. Bienvenido al sistema MUPAI.")
                            st.rerun()
                        else:
                            st.error("❌ Código incorrecto. Verifica e intenta nuevamente.")
    
    # Mostrar información del sistema mientras no esté autenticado
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

# Tarjetas visuales robustas
def crear_tarjeta(titulo, contenido, tipo="info"):
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

# Referencias funcionales mejoradas (CORREGIDO PARA MUJERES)
# Fondos (Hombres) - Referencias basadas en evidencia científica y consenso:
# ACSM, NSCA, McGill, Army PT Test, FMS, Journal of Strength & Conditioning Research, 2019
# Rangos por nivel: Bajo (3-6), Promedio (7-10), Bueno (11-14), Avanzado (15+)
# Referencias científicas actualizadas basadas en:
# - Cooper Institute (2016): Percentiles poblacionales
# - NSCA Performance Standards (2018)
# - US Army Physical Fitness Test (2020)
# - Boyle & McGill (2014): Bodyweight benchmarks
# - Contreras (2014): Hip thrust standards
# - McGill (2010): Core endurance tests
referencias_funcionales = {
    "Hombre": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 15), ("Promedio", 25), ("Bueno", 35), ("Avanzado", 45)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 3), ("Promedio", 6), ("Bueno", 12), ("Avanzado", 18)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 8), ("Promedio", 14), ("Bueno", 20), ("Avanzado", 28)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 6), ("Promedio", 12), ("Bueno", 18), ("Avanzado", 25)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 10), ("Promedio", 18), ("Bueno", 28), ("Avanzado", 40)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 30), ("Promedio", 60), ("Bueno", 90), ("Avanzado", 120)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 20), ("Avanzado", 30)]}
    },
    "Mujer": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 28)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 6), ("Bueno", 12), ("Avanzado", 18)]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 1), ("Bueno", 3), ("Avanzado", 6)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 22)]},
        "Sentadilla búlgara unilateral": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 22)]},
        "Puente de glúteo unilateral": {"tipo": "reps", "niveles": [("Bajo", 8), ("Promedio", 15), ("Bueno", 25), ("Avanzado", 35)]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 25), ("Promedio", 45), ("Bueno", 70), ("Avanzado", 100)]},
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
    Si el método es Omron HBF-516, convierte a modelo 4C (4-compartment body composition) 
    usando la fórmula de Siedler & Tinsley (2022): gc_4c = 1.226167 + 0.838294 * gc_omron.
    Validación de rango 4%-60%.
    Si InBody, aplica factor.
    Si BodPod, aplica factor por sexo.
    Si DEXA, devuelve el valor medido.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        # Conversión unificada Omron→4C (sin dependencia de género)
        # Validar rango: solo convertir si está entre 4% y 60%
        grasa_redondeada = int(round(medido))
        
        # Si está fuera del rango 4%-60%, devolver el valor original
        if grasa_redondeada < 4 or grasa_redondeada > 60:
            return medido
        
        # Usar tabla de conversión OMRON_HBF516_TO_4C
        return OMRON_HBF516_TO_4C.get(grasa_redondeada, medido)
    elif metodo == "InBody 270 (BIA profesional)":
        return medido * 1.02
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
        return medido * factor
    else:  # DEXA (Gold Standard) u otros
        return medido

def calcular_ffmi(mlg, estatura_cm):
    """
    Calcula el Fat-Free Mass Index (FFMI) - Índice de Masa Libre de Grasa.
    
    FFMI = MLG / estatura^2
    
    Parámetros:
        mlg: Masa Libre de Grasa en kg
        estatura_cm: Estatura en centímetros
    
    Retorna:
        float: FFMI calculado
    """
    if not mlg or not estatura_cm or mlg <= 0 or estatura_cm <= 0:
        return 0.0
    
    try:
        estatura_m = estatura_cm / 100
        mlg = float(mlg)
    except:
        return 0.0
    
    # Fórmula: FFMI = MLG (kg) / Estatura (m)^2
    # Rango normal hombres: 18-22
    # Rango normal mujeres: 15-18
    # Límite natural superior: ~25-26 (hombres), ~20-21 (mujeres)
    
    # Masa Libre de Grasa en kg
    # Se calcula como: MLG = Peso Total * (1 - Porcentaje_Grasa/100)
    # O directamente si la báscula lo reporta
    
    # Validación: MLG no puede ser 0 o negativa
    if mlg <= 0:
        return 0.0
    
    # FFMI = MLG / (Estatura en metros)^2
    # Similar al IMC pero usando MLG en vez de peso total
    
    # Normalizar por estatura
    estatura_m = estatura_cm / 100.0
    
    if estatura_m <= 0:
        return 0.0
    
    try:
        mlg = float(mlg)
    except:
        mlg = 0.0
    
    ffmi = mlg / (estatura_m ** 2)
    
    return ffmi

def estimar_masa_muscular_desde_mlg(mlg, sexo, nivel_entrenamiento='intermedio'):
    """
    Estima masa muscular esquelética desde MLG usando factores científicos.
    
    MLG incluye: músculo + huesos (~15%) + órganos (~10-15%) + agua (~30%)
    Músculo esquelético ≈ 35-45% de MLG según nivel de entrenamiento
    
    Factores basados en literatura científica:
    - Wang et al. (2000): distribución de tejidos en MLG
    - Kim et al. (2002): masa muscular apendicular
    - Janssen et al. (2000): ecuaciones de predicción
    
    Parámetros:
        mlg: Masa Libre de Grasa en kg
        sexo: 'Hombre' o 'Mujer'
        nivel_entrenamiento: 'principiante', 'intermedio' o 'avanzado'
    
    Retorna:
        float: Masa muscular estimada en kg
    """
    if not mlg or mlg <= 0:
        return 0.0
    
    # Factores conservadores por nivel y sexo
    factores = {
        'Hombre': {
            'principiante': 0.37,  # 37% de MLG es músculo
            'intermedio': 0.40,    # 40% de MLG es músculo
            'avanzado': 0.43       # 43% de MLG es músculo
        },
        'Mujer': {
            'principiante': 0.33,  # 33% de MLG es músculo
            'intermedio': 0.36,    # 36% de MLG es músculo  
            'avanzado': 0.40       # 40% de MLG es músculo
        }
    }
    
    nivel = nivel_entrenamiento.lower() if nivel_entrenamiento else 'intermedio'
    factor = factores.get(sexo, factores['Hombre']).get(nivel, 0.38)
    
    masa_muscular_estimada = mlg * factor
    
    return masa_muscular_estimada

def calcular_ffmi(mlg, estatura_cm):
    """
    Calcula el FFMI (Fat-Free Mass Index) y lo normaliza a 1.80m de estatura.
    
    El FFMI es un indicador de la masa muscular ajustado por altura que permite
    comparar el desarrollo muscular entre individuos de diferentes estaturas.
    
    PARAMETROS:
    -----------
    mlg : float
        Masa Libre de Grasa (MLG) en kilogramos.
        Se calcula como: MLG = Peso Total * (1 - Porcentaje_Grasa/100)
        Representa todo el tejido corporal excepto la grasa (musculos, huesos, organos, agua).
    
    estatura_cm : float
        Estatura del individuo en centimetros.
    
    CALCULO:
    --------
    1. FFMI Base = MLG / (Estatura_en_metros^2)
       - Similar al IMC pero usando masa libre de grasa en lugar de peso total
       - Refleja cuanta masa muscular tiene la persona por unidad de altura al cuadrado
    
    2. FFMI Normalizado = FFMI_Base + 6.3 * (1.8 - Estatura_en_metros)
       - Formula de Kouri et al. (1995) para normalizar a 1.80m de referencia
       - El factor 6.3 compensa las diferencias naturales de proporcion corporal
       - Personas mas altas tienden a tener FFMI base mas bajo sin tener menos musculo
       - La normalizacion permite comparaciones justas entre diferentes estaturas
    
    RETORNA:
    --------
    float
        FFMI normalizado a 1.80m de estatura.
        Valores tipicos:
        - Hombres: 18-25 (natural), >25 (potencialmente no natural)
        - Mujeres: 15-21 (natural), >21 (potencialmente no natural)
    
    REFERENCIAS:
    -----------
    - Kouri EM, et al. (1995). "Fat-free mass index in users and nonusers of 
      anabolic-androgenic steroids." Clinical Journal of Sport Medicine.
    """
    # Validacion y conversion de parametros a valores numericos
    try:
        mlg = float(mlg)
        estatura_m = float(estatura_cm) / 100
    except (TypeError, ValueError):
        # Si hay error en la conversion, usar valores por defecto seguros
        mlg = 0.0
        estatura_m = 1.80
    
    # Validar que la estatura sea positiva, usar 1.80m como fallback
    if estatura_m <= 0:
        estatura_m = 1.80
    
    # Paso 1: Calcular FFMI base (masa libre de grasa dividida por altura al cuadrado)
    ffmi = mlg / (estatura_m ** 2)
    
    # Paso 2: Normalizar a 1.80m usando la formula de Kouri
    # Esta normalizacion permite comparar el FFMI entre personas de diferentes alturas
    ffmi_normalizado = ffmi + 6.3 * (1.8 - estatura_m)
    
    return ffmi_normalizado

def clasificar_ffmi(ffmi, sexo):
    """
    Clasifica el FFMI (Fat-Free Mass Index) en categorias segun el sexo del usuario.
    
    El FFMI refleja el desarrollo muscular y varia significativamente entre hombres
    y mujeres debido a diferencias biologicas en composicion hormonal, cantidad de
    testosterona, y distribucion natural de masa muscular.
    
    PARAMETROS:
    -----------
    ffmi : float
        Valor de FFMI normalizado calculado previamente.
    
    sexo : str
        "Hombre" o "Mujer" - determina que escala de clasificacion usar.
    
    CLASIFICACION PARA HOMBRES:
    ---------------------------
    - Bajo (<18):      Desarrollo muscular insuficiente. Tipico en sedentarios o con
                       nutricion inadecuada. Indica necesidad de entrenamiento de fuerza
                       y optimizacion nutricional.
    
    - Promedio (18-20): Desarrollo muscular normal en poblacion general. Presente en
                        personas con actividad fisica moderada o principiantes en
                        entrenamiento de fuerza (0-2 anos de experiencia).
    
    - Bueno (20-22):   Buen desarrollo muscular. Alcanzable naturalmente con
                       entrenamiento de fuerza consistente (2-4 anos) y nutricion
                       adecuada. Representa un fisico atletico.
    
    - Avanzado (22-25): Desarrollo muscular muy avanzado. Requiere anos de entrenamiento
                        disciplinado (4-8+ anos) y optimizacion de todos los factores
                        (entrenamiento, nutricion, descanso, genetica favorable).
                        Limite superior del potencial natural para mayoria.
    
    - Elite (>25):     Desarrollo muscular excepcional. Dificil de alcanzar naturalmente.
                       Puede indicar genetica excepcional o uso de farmacologia.
                       Valores >26-27 son casi imposibles sin ayuda ergogenica.
    
    CLASIFICACION PARA MUJERES:
    ---------------------------
    - Bajo (<15):      Desarrollo muscular insuficiente. Requiere entrenamiento de
                       fuerza y nutricion adecuada para salud y funcionalidad.
    
    - Promedio (15-17): Desarrollo muscular normal. Tipico en poblacion femenina
                        general activa o con entrenamiento basico (0-2 anos).
    
    - Bueno (17-19):   Buen desarrollo muscular. Alcanzable con entrenamiento
                       consistente (2-4 anos) y nutricion optimizada. Fisico atletico.
    
    - Avanzado (19-21): Desarrollo muy avanzado. Requiere anos de dedicacion (4-8+ anos).
                        Limite superior del potencial natural para mayoria de mujeres.
    
    - Elite (>21):     Desarrollo excepcional. Raro naturalmente. Puede indicar genetica
                       superior o uso de farmacologia. Valores >22-23 son altamente
                       improbables sin ayuda ergogenica.
    
    RAZON DE DIFERENCIAS POR SEXO:
    ------------------------------
    Los umbrales son aproximadamente 3 puntos mas bajos para mujeres debido a:
    
    1. HORMONAS: Las mujeres tienen ~10-20% de la testosterona de los hombres, limitando
       la capacidad de sintesis proteica y ganancia muscular.
    
    2. COMPOSICION: Las mujeres tienen naturalmente 6-11% mas grasa corporal esencial
       (necesaria para funciones reproductivas), reduciendo el porcentaje de masa magra.
    
    3. DISTRIBUCION: Los hombres tienen mayor masa muscular en torso y brazos, mientras
       que las mujeres tienen distribucion mas uniforme o concentrada en piernas.
    
    4. GENETICA: Diferencias en expresion genica relacionada con miogenesis (formacion
       de tejido muscular) favorecen mayor desarrollo en hombres.
    
    RETORNA:
    --------
    str
        Categoria de clasificacion: "Bajo", "Promedio", "Bueno", "Avanzado" o "Elite"
    
    REFERENCIAS:
    -----------
    - Kouri EM, et al. (1995). Clinical Journal of Sport Medicine.
    - Schoenfeld BJ, et al. (2020). Sports Medicine - sex differences in training.
    """
    # Validar y convertir FFMI a valor numerico
    try:
        ffmi = float(ffmi)
    except (TypeError, ValueError):
        ffmi = 0.0
    
    # Definir umbrales de clasificacion especificos por sexo
    if sexo == "Hombre":
        # Umbrales masculinos: reflejan mayor potencial de masa muscular
        limites = [(18, "Bajo"), (20, "Promedio"), (22, "Bueno"), (25, "Avanzado"), (100, "Élite")]
    else:
        # Umbrales femeninos: ajustados ~3 puntos mas bajos por diferencias biologicas
        limites = [(15, "Bajo"), (17, "Promedio"), (19, "Bueno"), (21, "Avanzado"), (100, "Élite")]
    
    # Iterar sobre los limites y retornar la primera clasificacion que aplique
    for limite, clasificacion in limites:
        if ffmi < limite:
            return clasificacion
    
    # Si el FFMI supera todos los limites, clasificar como Elite
    return "Élite"

def calcular_fmi(peso, grasa_corregida, estatura_cm):
    """
    Calcula el FMI/BFMI (Fat Mass Index / Body Fat Mass Index).
    
    El FMI es un indicador de adiposidad ajustado por altura que complementa
    al FFMI. Permite evaluar la cantidad de grasa corporal de forma normalizada
    por la estatura del individuo.
    
    PARAMETROS:
    -----------
    peso : float
        Peso total del individuo en kilogramos.
    
    grasa_corregida : float
        Porcentaje de grasa corporal corregido (equivalente DEXA).
    
    estatura_cm : float
        Estatura del individuo en centímetros.
    
    CALCULO:
    --------
    1. Masa Grasa (kg) = Peso Total * (Porcentaje_Grasa / 100)
    2. FMI = Masa Grasa / (Estatura_en_metros^2)
    
    RETORNA:
    --------
    float
        FMI (índice de masa grasa por altura al cuadrado).
        Valores de referencia:
        - Hombres: <3 (bajo), 3-6 (normal), 6-9 (elevado), >9 (muy elevado)
        - Mujeres: <5 (bajo), 5-9 (normal), 9-13 (elevado), >13 (muy elevado)
    
    REFERENCIAS:
    -----------
    - Kelly TL, et al. (2009). "Dual energy X-Ray absorptiometry body composition
      reference values from NHANES." PLoS ONE.
    """
    try:
        peso = float(peso)
        grasa_corregida = float(grasa_corregida)
        estatura_m = float(estatura_cm) / 100
    except (TypeError, ValueError):
        return 0.0
    
    # Validar que la estatura sea positiva
    if estatura_m <= 0:
        return 0.0
    
    # Calcular masa grasa
    masa_grasa = peso * (grasa_corregida / 100)
    
    # Calcular FMI
    fmi = masa_grasa / (estatura_m ** 2)
    
    return fmi

def obtener_modo_interpretacion_ffmi(grasa_corregida, sexo):
    """
    Determina el modo de interpretación del FFMI basado en el porcentaje de grasa
    corporal corregido y el sexo del usuario.
    
    Este sistema controla cómo se interpreta y reporta el FFMI, reconociendo que
    en casos de adiposidad elevada, la masa libre de grasa puede estar inflada por
    componentes no musculares (agua corporal, órganos, masa estructural), haciendo
    que el FFMI pierda validez como proxy de muscularidad atlética.
    
    PARAMETROS:
    -----------
    grasa_corregida : float
        Porcentaje de grasa corporal corregido (equivalente DEXA).
    
    sexo : str
        "Hombre" o "Mujer" - determina qué umbrales aplicar.
    
    MODOS DE INTERPRETACIÓN:
    ------------------------
    GREEN (Verde) - Interpretación válida como muscularidad:
        - Hombres: 11.9% - 22.7% grasa corporal
        - Mujeres: 20.8% - 31.0% grasa corporal
        - El FFMI es un buen indicador de desarrollo muscular
        - Se muestran clasificaciones atléticas (Bajo-Élite)
        - Se incluyen módulos de potencial genético
    
    AMBER (Ámbar) - Interpretación limitada:
        - Hombres: >22.7% - 26.5% grasa corporal
        - Mujeres: >31.0% - 38.2% grasa corporal
        - El FFMI comienza a ser menos confiable
        - Se reporta valor numérico con advertencia
        - Se ocultan o degradan clasificaciones atléticas
        - Se reducen/ocultan módulos de potencial
    
    RED (Rojo) - No aplica clasificación atlética:
        - Hombres: >26.5% grasa corporal
        - Mujeres: >38.2% grasa corporal
        - El FFMI pierde validez como indicador de muscularidad
        - Se reporta valor pero con explicación clara
        - No se muestran clasificaciones atléticas
        - No se muestran módulos de potencial
    
    FUNDAMENTO CIENTÍFICO:
    ---------------------
    Con adiposidad elevada, la masa libre de grasa (MLG) incluye proporcionalmente
    más agua corporal, masa de órganos y tejido estructural, no solo músculo. Esto
    hace que el FFMI se eleve artificialmente y no refleje el desarrollo muscular
    real. Los umbrales están diseñados para:
    
    - GREEN: Rango donde la MLG es principalmente músculo esquelético
    - AMBER: Zona de transición donde comienza la inflación
    - RED: Rango donde la inflación es significativa y el FFMI no es interpretable
    
    RETORNA:
    --------
    str
        Modo de interpretación: "GREEN", "AMBER" o "RED"
    
    REFERENCIAS:
    -----------
    - Kouri EM, et al. (1995). Clinical Journal of Sport Medicine.
    - VanItallie TB, et al. (1990). "Height-normalized indices of body's fat-free
      mass and fat mass: potentially useful indicators of nutritional status."
    - Kyle UG, et al. (2004). "Fat-free and fat mass percentiles in 5225 healthy
      subjects aged 15 to 98 years." Nutrition.
    """
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        # Si no se puede determinar, usar GREEN por defecto (conservador)
        return "GREEN"
    
    if sexo == "Hombre":
        # Umbrales para hombres
        if 11.9 <= grasa <= 22.7:
            return "GREEN"
        elif 22.7 < grasa <= 26.5:
            return "AMBER"
        else:  # grasa > 26.5 o grasa < 11.9
            return "RED"
    else:  # Mujer
        # Umbrales para mujeres
        if 20.8 <= grasa <= 31.0:
            return "GREEN"
        elif 31.0 < grasa <= 38.2:
            return "AMBER"
        else:  # grasa > 38.2 o grasa < 20.8
            return "RED"

def calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura_cm=None):
    """
    Calcula los parámetros para PSMF (Very Low Calorie Diet) actualizada
    según el nuevo protocolo basado en tiers de adiposidad.
    
    Requisitos actualizados con sistema de tiers:
    - Tier 1 (baja adiposidad): Base = peso total
    - Tier 2 (adiposidad moderada): Base = MLG
    - Tier 3 (alta adiposidad): Base = peso ideal (IMC 25)
    - Proteína según % grasa: 1.8g/kg (<25% grasa) o 1.6g/kg (≥25% grasa)
    - Grasas según % grasa: 30g/día (<25% grasa) o 50g/día (≥25% grasa)
    - Calorías objetivo = proteína (g) × multiplicador según % grasa
    - Multiplicadores: 8.3 (alto % grasa), 9.0 (moderado), 9.5-9.7 (magro)
    - Carb cap por tier: Tier 1=50g, Tier 2=40g, Tier 3=30g
    - Carbohidratos: Calculados desde calorías restantes, limitados por carb cap
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
        # Calcular variables necesarias
        if estatura_cm is not None:
            estatura_m = estatura_cm / 100
            imc = peso / (estatura_m ** 2)
            peso_ideal_ref_kg = 25 * (estatura_m ** 2)
        else:
            estatura_m = None
            imc = None
            peso_ideal_ref_kg = None
        
        # DETERMINACIÓN DE TIER basado en adiposidad
        # Tier 3 predomina - verificar primero
        if (imc is not None and imc >= 40) or \
           (sexo == "Hombre" and grasa_corregida >= 35) or \
           (sexo == "Mujer" and grasa_corregida >= 45):
            tier = 3
        # Tier 2
        elif (sexo == "Hombre" and 25 <= grasa_corregida < 35) or \
             (sexo == "Mujer" and 35 <= grasa_corregida < 45):
            tier = 2
        # Tier 1
        elif (sexo == "Hombre" and grasa_corregida < 25) or \
             (sexo == "Mujer" and grasa_corregida < 35):
            tier = 1
        else:
            tier = 1  # Default fallback
        
        # ELECCIÓN DE BASE DE PROTEÍNA según tier
        if tier == 1:
            base_proteina_kg = peso
            base_proteina_nombre = "Peso total"
        elif tier == 2:
            base_proteina_kg = mlg
            base_proteina_nombre = "MLG"
        elif tier == 3:
            base_proteina_kg = peso_ideal_ref_kg if peso_ideal_ref_kg is not None else mlg
            base_proteina_nombre = "Peso ideal (IMC 25)"
        else:
            base_proteina_kg = peso
            base_proteina_nombre = "Peso total"
        
        # FACTORES DE PROTEÍNA Y GRASAS según % grasa corporal corregida
        if grasa_corregida < 25:
            # < 25% grasa: 1.8g/kg proteína + 30g grasas
            factor_proteina_psmf = 1.8
            grasa_g_dia = 30.0
        else:
            # ≥ 25% grasa: 1.6g/kg proteína + 50g grasas
            factor_proteina_psmf = 1.6
            grasa_g_dia = 50.0
        
        proteina_g_dia = round(base_proteina_kg * factor_proteina_psmf, 1)
        
        # MULTIPLICADOR CALÓRICO según % grasa corporal (para calorías objetivo)
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
        
        # CALORÍAS OBJETIVO = proteína (g) × multiplicador
        kcal_psmf_obj = round(proteina_g_dia * multiplicador, 0)
        
        # CARB CAP por tier
        if tier == 1:
            carb_cap_g = 50
        elif tier == 2:
            carb_cap_g = 40
        elif tier == 3:
            carb_cap_g = 30
        else:
            carb_cap_g = 50  # Default
        
        # CÁLCULO DE CARBOHIDRATOS con cap
        kcal_prot = 4 * proteina_g_dia
        kcal_grasa = 9 * grasa_g_dia
        carbs_g_calculado = max((kcal_psmf_obj - (kcal_prot + kcal_grasa)) / 4, 0)
        
        carbs_g = min(carbs_g_calculado, carb_cap_g)
        carb_cap_aplicado = carbs_g_calculado > carb_cap_g
        
        # CALORÍAS FINALES recalculadas por macros
        calorias_dia = kcal_prot + kcal_grasa + (4 * carbs_g)
        
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
            "grasa_g_dia": grasa_g_dia,
            "carbs_g_dia": round(carbs_g, 1),
            "calorias_dia": calorias_dia,
            "calorias_piso_dia": calorias_piso_dia,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Protocolo con tiers: {perfil_grasa}",
            # Nuevos campos de explainabilidad
            "tier_psmf": tier,
            "base_proteina_usada": base_proteina_nombre,
            "base_proteina_kg": round(base_proteina_kg, 2),
            "carb_cap_aplicado_g": carb_cap_g,
            "carb_cap_fue_aplicado": carb_cap_aplicado,
            "factor_proteina_psmf": factor_proteina_psmf
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
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 40, 35), (40.1, 45, 40),
        (45.1, 100, 50)
    ]
    rangos_mujer = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 40, 30), (40.1, 45, 35), (45.1, 50, 40),
        (50.1, 100, 50)
    ]
    tabla = rangos_hombre if sexo == "Hombre" else rangos_mujer
    tope = 30
    limite_extra = 30 if sexo == "Hombre" else 35
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            return min(deficit, tope) if porcentaje_grasa <= limite_extra else deficit
    return 20  # Déficit por defecto

def determinar_fase_nutricional_refinada(grasa_corregida, sexo):
    """
    Determina la fase nutricional refinada basada en % de grasa corporal y sexo.
    Usa la tabla completa de rangos para decisiones más precisas.
    """
    try:
        grasa_corregida = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa_corregida = 0.0
    
    if sexo == "Hombre":
        # Rangos refinados para hombres
        if grasa_corregida < 6:
            # Muy bajo - competición
            fase = "Superávit recomendado: 10-15%"
            porcentaje = 12.5
        elif grasa_corregida <= 10:
            # Bajo - atlético
            fase = "Superávit recomendado: 5-10%"
            porcentaje = 7.5
        elif grasa_corregida <= 15:
            # Fitness/atlético - puede mantener o ligero superávit
            fase = "Mantenimiento o ligero superávit: 0-5%"
            porcentaje = 2.5
        elif grasa_corregida <= 18:
            # Buena condición - mantenimiento
            fase = "Mantenimiento"
            porcentaje = 0
        else:
            # Sobrepeso - déficit según tabla
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje = -deficit_valor
            fase = f"Déficit recomendado: {deficit_valor}%"
    else:  # Mujer
        # Rangos refinados para mujeres
        if grasa_corregida < 12:
            # Muy bajo - competición
            fase = "Superávit recomendado: 10-15%"
            porcentaje = 12.5
        elif grasa_corregida <= 16:
            # Bajo - atlético
            fase = "Superávit recomendado: 5-10%"
            porcentaje = 7.5
        elif grasa_corregida <= 20:
            # Fitness/atlético - puede mantener o ligero superávit
            fase = "Mantenimiento o ligero superávit: 0-5%"
            porcentaje = 2.5
        elif grasa_corregida <= 23:
            # Buena condición - mantenimiento
            fase = "Mantenimiento"
            porcentaje = 0
        else:
            # Sobrepeso - déficit según tabla
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje = -deficit_valor
            fase = f"Déficit recomendado: {deficit_valor}%"
    
    return fase, porcentaje

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

def obtener_factor_proteina_tradicional(grasa_corregida):
    """
    Determina el factor de proteína en g/kg según el porcentaje de grasa corporal corregido
    para el plan tradicional.
    
    Escala de distribución:
    - Si grasa_corregida >= 35%: 1.6g/kg proteína
    - Si grasa_corregida entre 25% y 34.9%: 1.8g/kg proteína
    - Si grasa_corregida entre 15% y 24.9%: 2.0g/kg proteína
    - Si grasa_corregida entre 4% y 14.9%: 2.2g/kg proteína
    
    GRASA: Ahora SIEMPRE 40% TMB (independiente del % grasa corporal)
    
    Args:
        grasa_corregida: Porcentaje de grasa corporal corregido
    
    Returns:
        float: Factor de proteína en g/kg peso corporal
    """
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        grasa = 20.0  # Valor por defecto
    
    if grasa >= 35:
        return 1.6
    elif grasa >= 25:
        return 1.8
    elif grasa >= 15:
        return 2.0
    else:  # grasa < 15 (includes 4-14.9%)
        return 2.2

def debe_usar_mlg_para_proteina(sexo, grasa_corregida):
    """
    Determina si se debe usar MLG como base para el cálculo de proteína
    según las reglas 35/42 para alta adiposidad.
    
    Reglas:
    - Hombres: usar MLG si grasa_corregida >= 35%
    - Mujeres: usar MLG si grasa_corregida >= 42%
    - De lo contrario: usar peso total
    
    Razón: En obesidad alta, usar peso total infla inapropiadamente la proteína.
    
    Args:
        sexo: "Hombre" o "Mujer"
        grasa_corregida: Porcentaje de grasa corporal corregido
    
    Returns:
        bool: True si se debe usar MLG, False si se debe usar peso total
    """
    try:
        grasa = float(grasa_corregida)
    except (TypeError, ValueError):
        return False
    
    if sexo == "Hombre" and grasa >= 35:
        return True
    elif sexo == "Mujer" and grasa >= 42:
        return True
    else:
        return False

def obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo):
    """
    Determina el porcentaje del TMB/BMR que debe destinarse a grasas para el plan tradicional.
    
    NUEVA LÓGICA CIENTÍFICA (implementada según requerimientos):
    - Fat intake se establece SIEMPRE en 40% del TMB/BMR para CUALQUIER % de grasa corporal
    - Esto se basa en evidencia científica que demuestra beneficios metabólicos óptimos
    - La ingesta mínima se garantiza mediante restricción del 20% del TEI (aplicada posteriormente)
    
    Referencias científicas:
    - Hämäläinen et al., 1984: Efectos metabólicos de diferentes ratios de grasas
    - Volek et al., 1997: Adaptaciones metabólicas al entrenamiento de resistencia
    - Smith et al., 2011: Optimización de macronutrientes para composición corporal
    - Riechman et al., 2007: Síntesis proteica y balance energético
    - Burke et al., 2011: Estrategias nutricionales para deportistas
    
    Args:
        grasa_corregida: Porcentaje de grasa corporal corregido (no utilizado en nueva lógica)
        sexo: "Hombre" o "Mujer" (no utilizado en nueva lógica)
    
    Returns:
        float: Porcentaje del TMB destinado a grasas (0.40 = 40%)
    """
    # Nueva lógica científica: SIEMPRE 40% del TMB/BMR para grasas
    # independientemente del % de grasa corporal o sexo
    return 0.40  # 40% TMB (aplicable a todos los usuarios del plan TRADICIONAL)

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

def calcular_macros_tradicional(ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg):
    """
    Función centralizada para calcular macronutrientes del plan tradicional.
    Garantiza consistencia en todos los cálculos (UI, email, reportes).
    
    Lógica de cálculo:
    1. PROTEÍNA: Usar MLG si aplica regla 35/42, sino usar peso total
       - Factor varía según % grasa: 1.6-2.2 g/kg
    2. GRASA: SIEMPRE 40% del TMB (con restricciones 20-40% TEI)
    3. CARBOHIDRATOS: Calorías restantes
    
    Args:
        ingesta_calorica_tradicional: Calorías totales del plan tradicional
        tmb: Tasa metabólica basal
        sexo: "Hombre" o "Mujer"
        grasa_corregida: % grasa corporal corregido
        peso: Peso corporal en kg
        mlg: Masa libre de grasa en kg
    
    Returns:
        dict: {
            'proteina_g': gramos de proteína,
            'proteina_kcal': calorías de proteína,
            'grasa_g': gramos de grasa,
            'grasa_kcal': calorías de grasa,
            'carbo_g': gramos de carbohidratos,
            'carbo_kcal': calorías de carbohidratos,
            'base_proteina': 'MLG' o 'Peso total',
            'factor_proteina': factor usado para proteína
        }
    """
    # 1. PROTEÍNA: Determinar base y calcular
    usar_mlg = debe_usar_mlg_para_proteina(sexo, grasa_corregida)
    base_proteina_kg = mlg if usar_mlg else peso
    base_proteina_nombre = "MLG" if usar_mlg else "Peso total"
    factor_proteina = obtener_factor_proteina_tradicional(grasa_corregida)
    
    proteina_g = round(base_proteina_kg * factor_proteina, 1)
    proteina_kcal = proteina_g * 4
    
    # 2. GRASA: SIEMPRE 40% TMB con restricciones 20-40% TEI
    grasa_min_kcal = ingesta_calorica_tradicional * 0.20  # Mínimo 20% TEI
    grasa_max_kcal = ingesta_calorica_tradicional * 0.40  # Máximo 40% TEI
    porcentaje_grasa_tmb = obtener_porcentaje_grasa_tmb_tradicional(grasa_corregida, sexo)
    grasa_ideal_kcal = tmb * porcentaje_grasa_tmb  # 40% TMB
    
    # Aplicar restricciones
    grasa_kcal = max(grasa_min_kcal, min(grasa_ideal_kcal, grasa_max_kcal))
    grasa_g = round(grasa_kcal / 9, 1)
    
    # 3. CARBOHIDRATOS: Calorías restantes
    carbo_kcal = ingesta_calorica_tradicional - proteina_kcal - grasa_kcal
    carbo_g = round(max(0, carbo_kcal / 4), 1)
    
    return {
        'proteina_g': proteina_g,
        'proteina_kcal': proteina_kcal,
        'grasa_g': grasa_g,
        'grasa_kcal': grasa_kcal,
        'carbo_g': carbo_g,
        'carbo_kcal': carbo_kcal,
        'base_proteina': base_proteina_nombre,
        'base_proteina_kg': base_proteina_kg,
        'factor_proteina': factor_proteina,
        'usar_mlg': usar_mlg
    }

def calcular_macros_psmf(psmf_recs):
    """
    Función centralizada para calcular macronutrientes del plan PSMF.
    Garantiza consistencia en todos los cálculos (UI, email, reportes).
    
    Los cálculos PSMF ya están centralizados en calculate_psmf(),
    esta función simplemente extrae y formatea los resultados de forma consistente.
    
    Args:
        psmf_recs: Diccionario retornado por calculate_psmf()
    
    Returns:
        dict: {
            'proteina_g': gramos de proteína,
            'proteina_kcal': calorías de proteína,
            'grasa_g': gramos de grasa,
            'grasa_kcal': calorías de grasa,
            'carbo_g': gramos de carbohidratos,
            'carbo_kcal': calorías de carbohidratos,
            'calorias_dia': calorías totales,
            'aplicable': bool indicando si PSMF es aplicable
        }
    """
    if not psmf_recs.get('psmf_aplicable', False):
        return {
            'proteina_g': 0,
            'proteina_kcal': 0,
            'grasa_g': 0,
            'grasa_kcal': 0,
            'carbo_g': 0,
            'carbo_kcal': 0,
            'calorias_dia': 0,
            'aplicable': False
        }
    
    proteina_g = psmf_recs.get('proteina_g_dia', 0)
    grasa_g = psmf_recs.get('grasa_g_dia', 0)
    carbo_g = psmf_recs.get('carbs_g_dia', 0)
    
    # Calcular calorías de cada macro
    proteina_kcal = proteina_g * 4
    grasa_kcal = grasa_g * 9
    carbo_kcal = carbo_g * 4
    
    return {
        'proteina_g': proteina_g,
        'proteina_kcal': proteina_kcal,
        'grasa_g': grasa_g,
        'grasa_kcal': grasa_kcal,
        'carbo_g': carbo_g,
        'carbo_kcal': carbo_kcal,
        'calorias_dia': psmf_recs.get('calorias_dia', 0),
        'aplicable': True
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

def enviar_email_cliente(nombre_cliente, email_cliente, fecha, edad, sexo, peso, estatura, imc,
                         grasa_corregida, mlg, ffmi=None, nivel_entrenamiento=None, 
                         circunferencia_cintura=None, grasa_visceral=None, edad_metabolica=None,
                         wthr=None, masa_grasa=None, progress_photos=None, masa_muscular_aparato=0, masa_muscular_estimada=0):
    """
    Envía email al cliente con resultados completos de evaluación corporal.
    
    Incluye:
    - Datos personales básicos (incluye ciclo menstrual si aplica)
    - Composición corporal completa
    - Índices corporales (FFMI, WtHR, grasa visceral)
    - Edad metabólica
    - Nivel de entrenamiento
    - Nivel de recuperación (sueño/estrés si disponible)
    - Fotos de progreso
    
    NO incluye:
    - Plan nutricional (macros/calorías) - cliente debe consultarte
    - Proyección de progreso - cliente debe consultarte
    - Ecuaciones científicas (TMB, cálculos GEAF, ETA, etc.)
    - Metodología de cálculo
    - Factores multiplicadores
    """
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = email_cliente
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")
        
        # Cargar logos para emails
        import base64
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

        # Calcular valores derivados
        masa_grasa_calc = peso - mlg if masa_grasa is None else masa_grasa
        pct_mlg = (mlg / peso * 100) if peso > 0 else 0
        
        # Calcular modo de interpretación FFMI
        modo_ffmi_email = obtener_modo_interpretacion_ffmi(grasa_corregida, sexo)
        
        # Masa muscular: aparato viene como %, estimada como kg
        # Convertir aparato de % a kg, y calcular % de estimada
        masa_muscular_aparato_kg = (peso * masa_muscular_aparato / 100) if peso > 0 and masa_muscular_aparato > 0 else 0
        pct_masa_muscular_aparato = masa_muscular_aparato  # Ya es porcentaje desde Omron
        pct_masa_muscular_estimada = (masa_muscular_estimada / peso * 100) if peso > 0 and masa_muscular_estimada > 0 else 0
        
        # Clasificar WtHR si está disponible
        wthr_clasificacion = ""
        if wthr is not None:
            if wthr < 0.40:
                wthr_clasificacion = " - 🟢 Extremadamente delgado"
            elif wthr < 0.50:
                wthr_clasificacion = " - 🟢 Saludable"
            elif wthr < 0.60:
                wthr_clasificacion = " - 🟡 Sobrepeso"
            else:
                wthr_clasificacion = " - 🔴 Obesidad"
        
        # Clasificar grasa visceral si está disponible
        grasa_visceral_clasificacion = ""
        if grasa_visceral is not None:
            if grasa_visceral < 10:
                grasa_visceral_clasificacion = " - 🟢 Nivel saludable"
            elif grasa_visceral < 15:
                grasa_visceral_clasificacion = " - 🟡 Nivel elevado"
            else:
                grasa_visceral_clasificacion = " - 🔴 Nivel alto (riesgo)"
        
        # Categorizar grasa corporal con feedback detallado
        if sexo == "Hombre":
            if grasa_corregida < 6:
                categoria_grasa = "Muy bajo (Competición)"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel de competición. Difícil de mantener a largo plazo. Puede afectar hormonas y rendimiento."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 12:
                categoria_grasa = "Atlético"
                emoji_grasa = "💪"
                feedback_grasa = "Excelente nivel. Buena definición muscular visible. Rendimiento deportivo óptimo."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • <strong>6-12%: Atlético/Competición (muy definido) ← Tú estás aquí</strong><br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 18:
                categoria_grasa = "Fitness"
                emoji_grasa = "🏃"
                feedback_grasa = "Nivel fitness saludable. Buena relación salud-estética. Sostenible a largo plazo."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • <strong>12-18%: Fitness (saludable, estético) ← Tú estás aquí</strong><br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 25:
                categoria_grasa = "Promedio"
                emoji_grasa = "📊"
                feedback_grasa = "Nivel promedio. Espacio para mejorar composición corporal con entrenamiento y nutrición."
                rango_saludable = "Rango fitness: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • <strong>18-25%: Promedio aceptable ← Tú estás aquí</strong><br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            else:
                categoria_grasa = "Alto"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel elevado. Recomendable reducir para mejorar salud metabólica y reducir riesgos."
                rango_saludable = "Rango fitness: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • <strong>25-30%: Sobrepeso (considerar reducir) ← Tú estás aquí</strong><br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
        else:  # Mujer
            if grasa_corregida < 12:
                categoria_grasa = "Muy bajo (Competición)"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel de competición. Muy difícil de mantener. Puede afectar ciclo menstrual y hormonas."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 17:
                categoria_grasa = "Atlético"
                emoji_grasa = "💪"
                feedback_grasa = "Excelente nivel atlético. Muy buena definición muscular. Rendimiento deportivo óptimo."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • <strong>12-17%: Atlético/Competición (muy definido) ← Tú estás aquí</strong><br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 23:
                categoria_grasa = "Fitness"
                emoji_grasa = "🏃"
                feedback_grasa = "Nivel fitness saludable. Buena relación salud-estética. Sostenible a largo plazo."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • <strong>17-23%: Fitness (saludable, estético) ← Tú estás aquí</strong><br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 30:
                categoria_grasa = "Promedio"
                emoji_grasa = "📊"
                feedback_grasa = "Nivel promedio. Espacio para mejorar composición corporal con entrenamiento y nutrición."
                rango_saludable = "Rango fitness: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • <strong>23-30%: Promedio aceptable ← Tú estás aquí</strong><br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            else:
                categoria_grasa = "Alto"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel elevado. Recomendable reducir para mejorar salud metabólica y reducir riesgos."
                rango_saludable = "Rango fitness: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • <strong>30-35%: Sobrepeso (considerar reducir) ← Tú estás aquí</strong><br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
        
        # Feedback para FFMI si está disponible
        feedback_ffmi = ""
        rangos_ffmi = ""
        if ffmi is not None:
            if sexo == "Hombre":
                if ffmi < 18:
                    feedback_ffmi = "Por debajo del promedio. Potencial de ganancia muscular significativo con entrenamiento."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • <strong>&lt;18: Por debajo del promedio ← Tú estás aquí</strong><br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 20:
                    feedback_ffmi = "Nivel promedio. Desarrollo muscular natural normal. Buen punto de partida."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • <strong>18-20: Promedio (desarrollo natural normal) ← Tú estás aquí</strong><br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 22:
                    feedback_ffmi = "Por encima del promedio. Buen desarrollo muscular. Nivel de entrenamiento intermedio-avanzado."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • <strong>20-22: Por encima del promedio (buen entrenamiento) ← Tú estás aquí</strong><br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 25:
                    feedback_ffmi = "Excelente desarrollo. Nivel avanzado. Años de entrenamiento consistente."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • <strong>22-25: Excelente (años de entrenamiento) ← Tú estás aquí</strong><br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                else:
                    feedback_ffmi = "Elite/excepcional. Desarrollo muscular muy avanzado. Genética favorable o entrenamiento de años."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • <strong>25+: Elite/excepcional (límite natural ~25-26) ← Tú estás aquí</strong>
                    """
            else:  # Mujer
                if ffmi < 15:
                    feedback_ffmi = "Por debajo del promedio. Potencial de ganancia muscular significativo con entrenamiento."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • <strong>&lt;15: Por debajo del promedio ← Tú estás aquí</strong><br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 17:
                    feedback_ffmi = "Nivel promedio. Desarrollo muscular natural normal. Buen punto de partida."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • <strong>15-17: Promedio (desarrollo natural normal) ← Tú estás aquí</strong><br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 18:
                    feedback_ffmi = "Por encima del promedio. Buen desarrollo muscular. Nivel intermedio-avanzado."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • <strong>17-18: Por encima del promedio (buen entrenamiento) ← Tú estás aquí</strong><br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 20:
                    feedback_ffmi = "Excelente desarrollo. Nivel avanzado. Años de entrenamiento consistente."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • <strong>18-20: Excelente (años de entrenamiento) ← Tú estás aquí</strong><br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                else:
                    feedback_ffmi = "Elite/excepcional. Desarrollo muscular muy avanzado. Genética favorable o entrenamiento de años."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • <strong>20+: Elite/excepcional (límite natural ~20-21) ← Tú estás aquí</strong>
                    """
        
        # Feedback para IMC (Índice de Masa Corporal)
        feedback_imc = ""
        rangos_imc = ""
        if imc < 16:
            feedback_imc = "Delgadez severa. Por debajo del peso saludable. Considera consulta nutricional."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • <strong>&lt;16: Delgadez severa ← Tú estás aquí</strong><br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 17:
            feedback_imc = "Delgadez moderada. Por debajo del peso recomendado. Evalúa aumentar masa muscular."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • <strong>16-17: Delgadez moderada ← Tú estás aquí</strong><br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 18.5:
            feedback_imc = "Delgadez leve. Cerca del rango saludable. Considera ganar masa muscular."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • <strong>17-18.5: Delgadez leve ← Tú estás aquí</strong><br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 25:
            feedback_imc = "¡Excelente! Normopeso. Rango saludable según OMS. Mantén buenos hábitos."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • <strong>18.5-25: Normopeso (saludable) ← Tú estás aquí</strong><br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 30:
            feedback_imc = "Sobrepeso. Riesgo moderado de complicaciones metabólicas. Beneficio de reducir grasa."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • <strong>25-30: Sobrepeso ← Tú estás aquí</strong><br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 35:
            feedback_imc = "Obesidad grado I. Riesgo incrementado. Importante reducir grasa corporal para salud."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • <strong>30-35: Obesidad grado I ← Tú estás aquí</strong><br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 40:
            feedback_imc = "Obesidad grado II (severa). Alto riesgo. Prioritario trabajar en reducción de peso."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • <strong>35-40: Obesidad grado II ← Tú estás aquí</strong><br>
            • 40+: Obesidad grado III (mórbida)
            """
        else:
            feedback_imc = "Obesidad grado III (mórbida). Riesgo muy alto. Urgente intervención médica y nutricional."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • <strong>40+: Obesidad grado III (mórbida) ← Tú estás aquí</strong>
            """
        
        # Feedback para edad metabólica
        feedback_edad_metabolica = ""
        rangos_edad_metabolica = ""
        if edad_metabolica is not None:
            diff_edad = edad - edad_metabolica
            if diff_edad > 5:
                feedback_edad_metabolica = "¡Excelente! Tu metabolismo está significativamente más joven. Refleja buenos hábitos y composición corporal saludable."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • <strong>Tu edad real - metabólica = {diff:.0f} años (Excelente) ← Tú estás aquí</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=diff_edad)
            elif diff_edad > 0:
                feedback_edad_metabolica = "Bien. Tu metabolismo es ligeramente más joven. Continúa con buenos hábitos de entrenamiento y nutrición."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • <strong>1-5 años menor: Buen estado, por encima del promedio ← Tú estás aquí ({diff:.0f} años)</strong><br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=diff_edad)
            elif diff_edad == 0:
                feedback_edad_metabolica = "Tu edad metabólica coincide con tu edad cronológica. Hay espacio para mejorar con ejercicio y nutrición."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • <strong>Igual: Normal, hay espacio para mejorar ← Tú estás aquí</strong><br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """
            elif diff_edad > -5:
                feedback_edad_metabolica = "Tu metabolismo está ligeramente envejecido. Mejorar composición corporal ayudará a revertir esto."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • <strong>1-5 años mayor: Atención, prioriza mejorar composición ← Tú estás aquí ({diff:.0f} años)</strong><br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=abs(diff_edad))
            else:
                feedback_edad_metabolica = "Atención: metabolismo envejecido. Prioriza mejorar composición corporal, ejercicio y hábitos de sueño."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • <strong>Más de 5 años mayor: Urgente optimizar estilo de vida ← Tú estás aquí ({diff:.0f} años)</strong>
                """.format(diff=abs(diff_edad))
        
        # Feedback para WtHR
        feedback_wthr = ""
        rangos_wthr = ""
        if wthr is not None:
            if wthr < 0.40:
                feedback_wthr = "Extremadamente delgado. Considera si es saludable para ti."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • <strong>&lt;0.40: Muy delgado/Atlético ← Tú estás aquí</strong><br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            elif wthr < 0.50:
                feedback_wthr = "¡Excelente! Rango saludable. Bajo riesgo cardiovascular y metabólico."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • <strong>0.40-0.50: Saludable (riesgo CVD bajo) ← Tú estás aquí</strong><br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            elif wthr < 0.60:
                feedback_wthr = "Atención: sobrepeso. Riesgo moderado. Reducir cintura mejorará salud metabólica."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • <strong>0.50-0.60: Sobrepeso (riesgo CVD incrementado) ← Tú estás aquí</strong><br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            else:
                feedback_wthr = "Alerta: obesidad central. Alto riesgo cardiovascular. Prioriza reducir grasa abdominal."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • <strong>0.60+: Obesidad central (riesgo CVD alto) ← Tú estás aquí</strong><br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
        
        # Feedback para grasa visceral
        feedback_visceral = ""
        if grasa_visceral is not None:
            if grasa_visceral < 10:
                feedback_visceral = "¡Perfecto! Nivel saludable. La grasa visceral es la más peligrosa y la tuya está bien controlada."
                info_visceral = "Nivel 1-9 = Saludable. Bajo riesgo de diabetes tipo 2, enfermedades cardíacas y síndrome metabólico."
            elif grasa_visceral < 15:
                feedback_visceral = "Atención: nivel elevado. Considera reducirlo con ejercicio cardiovascular y dieta antiinflamatoria."
                info_visceral = "Nivel 10-14 = Elevado. Riesgo moderado. Prioriza ejercicio aeróbico y reducir calorías."
            else:
                feedback_visceral = "Alerta: nivel alto. Aumenta riesgo de diabetes, enfermedades cardíacas. Prioriza reducirlo urgentemente."
                info_visceral = "Nivel 15+ = Alto riesgo. Requiere atención inmediata. La grasa visceral rodea órganos internos."
        
        # Feedback para masa muscular (priorizar aparato, fallback a estimada)
        masa_muscular_para_feedback = masa_muscular_aparato if masa_muscular_aparato > 0 else masa_muscular_estimada
        pct_masa_muscular_para_feedback = pct_masa_muscular_aparato if pct_masa_muscular_aparato > 0 else pct_masa_muscular_estimada
        
        feedback_masa_muscular = ""
        if masa_muscular_para_feedback > 0 and pct_masa_muscular_para_feedback > 0:
            if sexo == "Hombre":
                if pct_masa_muscular_para_feedback < 33:
                    feedback_masa_muscular = "Bajo. Potencial significativo de ganancia muscular con entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 38:
                    feedback_masa_muscular = "Por debajo del promedio. Responderás bien al entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 44:
                    feedback_masa_muscular = "Promedio saludable. Buen punto de partida para desarrollo muscular."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 50:
                    feedback_masa_muscular = "Por encima del promedio. Buen desarrollo muscular. Sigue con entrenamiento consistente."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                else:
                    feedback_masa_muscular = "Excelente. Desarrollo muscular avanzado. Mantén con entrenamiento y nutrición óptimos."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
            else:  # Mujer
                if pct_masa_muscular_para_feedback < 28:
                    feedback_masa_muscular = "Bajo. Gran potencial de ganancia muscular con entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 31:
                    feedback_masa_muscular = "Por debajo del promedio. Responderás bien al entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 35:
                    feedback_masa_muscular = "Promedio saludable. Buen punto de partida para desarrollo muscular."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 40:
                    feedback_masa_muscular = "Por encima del promedio. Buen desarrollo muscular. Sigue así."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                else:
                    feedback_masa_muscular = "Excelente. Desarrollo muscular avanzado. Mantén con entrenamiento y nutrición óptimos."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
        else:
            feedback_masa_muscular = "No hay suficientes datos para evaluar masa muscular."
            rango_masa_muscular = ""
        
        # Feedback para nivel de entrenamiento
        feedback_nivel = ""
        if nivel_entrenamiento:
            if nivel_entrenamiento.lower() == 'principiante':
                feedback_nivel = "Inicio del viaje. Gran potencial de mejora. Enfócate en aprender técnica y crear hábitos consistentes."
            elif nivel_entrenamiento.lower() == 'intermedio':
                feedback_nivel = "Nivel sólido. Ya tienes base. Enfócate en periodización, progresión e intensidad para seguir avanzando."
            elif nivel_entrenamiento.lower() == 'avanzado':
                feedback_nivel = "Nivel avanzado. Años de entrenamiento. Necesitas programación muy específica y recuperación óptima."
            else:
                feedback_nivel = "Tu nivel refleja tu experiencia, desarrollo muscular y capacidad funcional actual."
        
        # Obtener datos de ciclo menstrual si aplica
        ciclo_menstrual_info = ""
        if sexo == "Mujer":
            ciclo = st.session_state.get('ciclo_menstrual', None)
            if ciclo:
                ciclo_menstrual_info = f"\n   • Fase del ciclo menstrual: {ciclo}"
        
        # Obtener datos de sueño y estrés si están disponibles
        seccion_recuperacion = ""
        if st.session_state.get('suenyo_estres_completado', False):
            data_se = st.session_state.get('suenyo_estres_data', {})
            if data_se and 'ir_se' in data_se:
                ir_se = data_se.get('ir_se', 0)
                nivel_recup = data_se.get('nivel_recuperacion', 'No determinado')
                emoji_recup = data_se.get('emoji_nivel', '')
                
                seccion_recuperacion = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😴 ESTADO DE RECUPERACIÓN (SUEÑO + ESTRÉS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ╔════════════════════════════════════════════════════════════════╗
   ║  ÍNDICE DE RECUPERACIÓN (IR-SE): {ir_se:.1f}/100                   ║
   ║  NIVEL: {nivel_recup} {emoji_recup}                                      ║
   ╚════════════════════════════════════════════════════════════════╝

   • Calidad de sueño: {data_se.get('sleep_score', 0):.1f}/100
   • Nivel de estrés: {data_se.get('stress_score', 0):.1f}/100
   
   💡 Este índice refleja tu capacidad de recuperación y adaptación al
      entrenamiento. Valores bajos pueden limitar tu progreso.
"""

        contenido = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   REPORTE DE EVALUACIÓN CORPORAL                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Muscle Up Performance Assessment Intelligence                               ║
║  {datetime.now().strftime("%Y-%m-%d")}                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Hola {nombre_cliente},

¡Gracias por confiar en nosotros para tu evaluación! Aquí están los resultados
completos de tu análisis de composición corporal y rendimiento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DATOS DE EVALUACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 IDENTIFICACIÓN:
   • Nombre: {nombre_cliente}
   • Edad: {edad} años
   • Sexo: {sexo}
   • Fecha de evaluación: {fecha}{ciclo_menstrual_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 COMPOSICIÓN CORPORAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📏 MEDIDAS BÁSICAS:
   
   ╔════════════════════════════════════════════════════════════════╗
   ║  Peso corporal:         {peso:.1f} kg                              ║
   ║  Estatura:              {estatura:.1f} cm                           ║
   ║  IMC:                   {imc:.1f} kg/m²                         ║
   ╚════════════════════════════════════════════════════════════════╝

📊 ANÁLISIS DE TEJIDOS:

   ╔════════════════════════════════════════════════════════════════╗
   ║  % Grasa corporal:      {grasa_corregida:.1f}% {emoji_grasa}                        ║
   ║  Categoría:             {categoria_grasa}                  ║
   ║                                                                ║
   ║  Masa Grasa:            {masa_grasa_calc:.1f} kg                            ║
   ║  Masa Libre de Grasa (MLG): {mlg:.1f} kg ({pct_mlg:.1f}%)              ║
   ╚════════════════════════════════════════════════════════════════╝
   
   💪 MASA MUSCULAR ESQUELÉTICA:
   {f'   🔵 Omron (medido):      {masa_muscular_aparato_kg:.1f} kg ({pct_masa_muscular_aparato:.1f}%)' if masa_muscular_aparato > 0 else ''}
   🟣 Estimado científico: {masa_muscular_estimada:.1f} kg ({pct_masa_muscular_estimada:.1f}%)
   
   📝 Nota: Omron mide directamente; estimado se calcula desde MLG.
      Si difieren >15%, puede ser por hidratación o método.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ÍNDICES CORPORALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💪 FFMI (Índice de Masa Libre de Grasa):
   • Valor: {ffmi:.1f} {'(dato no disponible)' if ffmi is None else ''}
   • Indicador: Desarrollo muscular ajustado por altura
   
⚕️ ÍNDICES DE SALUD:"""

        # Agregar circunferencia de cintura y WtHR si están disponibles
        if circunferencia_cintura is not None:
            contenido += f"""
   • Circunferencia de cintura: {circunferencia_cintura} cm"""
        
        if wthr is not None:
            contenido += f"""
   • Ratio Cintura-Altura (WtHR): {wthr:.3f}{wthr_clasificacion}"""
        
        if grasa_visceral is not None:
            contenido += f"""
   • Grasa visceral: Nivel {grasa_visceral}{grasa_visceral_clasificacion}"""
        
        if edad_metabolica is not None:
            contenido += f"""

🧬 EDAD METABÓLICA:
   • Edad cronológica: {edad} años
   • Edad metabólica: {edad_metabolica} años
   • {'✅ Tu metabolismo es ' + str(edad - edad_metabolica) + ' años más joven' if edad_metabolica < edad else '⚠️ Tu metabolismo está ' + str(edad_metabolica - edad) + ' años por encima' if edad_metabolica > edad else '📊 Tu edad metabólica coincide con tu edad'}"""

        # Agregar nivel de entrenamiento si está disponible
        if nivel_entrenamiento:
            contenido += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 NIVEL DE ENTRENAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ╔════════════════════════════════════════════════════════════════╗
   ║  NIVEL: {nivel_entrenamiento.upper()}                                       ║
   ╚════════════════════════════════════════════════════════════════╝
   
   Este nivel se calcula evaluando tu desarrollo muscular, rendimiento
   funcional y experiencia de entrenamiento."""

        # Agregar sección de recuperación si está disponible
        contenido += seccion_recuperacion

        contenido += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 FOTOGRAFÍAS DE PROGRESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Las fotografías de tu evaluación están adjuntas a este correo para tu registro.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 PRÓXIMOS PASOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu coach se pondrá en contacto contigo para:

   ✅ Revisar en detalle tus resultados
   ✅ Diseñar tu plan nutricional personalizado
   ✅ Establecer objetivos específicos y proyecciones
   ✅ Programar tu seguimiento y ajustes

Si tienes alguna pregunta o inquietud, no dudes en contactarnos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Muscle Up GYM
Digital Training Science
muscleupgym.fitness
administracion@muscleupgym.fitness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        msg = MIMEMultipart('alternative')
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Resultados de tu Evaluación Corporal - {nombre_cliente}"

        # Convertir contenido a HTML profesional
        contenido_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #FFD700;
            padding: 30px 20px;
            text-align: center;
            position: relative;
        }}
        .header-logos {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 0 20px;
        }}
        .header-logo {{
            max-height: 60px;
            max-width: 150px;
            object-fit: contain;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            color: #cccccc;
            font-size: 14px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            color: #1a1a1a;
            padding: 12px 15px;
            margin: 0 -20px 20px -20px;
            font-size: 18px;
            font-weight: 600;
            border-left: 5px solid #FF8C00;
        }}
        .info-row {{
            display: table;
            width: 100%;
            margin-bottom: 10px;
        }}
        .info-label {{
            font-weight: 600;
            color: #555555;
            margin-right: 10px;
        }}
        .info-value {{
            color: #1a1a1a;
        }}
        .card {{
            background-color: #f9f9f9;
            border-left: 4px solid #FFD700;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        .card-highlight {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #1a1a1a;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 600;
            font-size: 18px;
        }}
        .metric-grid {{
            display: table;
            width: 100%;
            border-collapse: collapse;
        }}
        .metric-row {{
            display: table-row;
        }}
        .metric-cell {{
            display: table-cell;
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            vertical-align: middle;
        }}
        .metric-label {{
            font-weight: 600;
            color: #555555;
            width: 50%;
        }}
        .metric-value {{
            color: #1a1a1a;
            font-size: 16px;
            text-align: right;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-green {{
            background-color: #27AE60;
            color: white;
        }}
        .badge-yellow {{
            background-color: #F39C12;
            color: white;
        }}
        .badge-red {{
            background-color: #E74C3C;
            color: white;
        }}
        .badge-blue {{
            background-color: #3498DB;
            color: white;
        }}
        .index-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #FFD700;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            text-align: center;
        }}
        .index-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 10px 0;
        }}
        .index-label {{
            font-size: 14px;
            color: #555555;
            margin-bottom: 5px;
        }}
        .cta-box {{
            background-color: #f0f8ff;
            border: 2px solid #3498DB;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .cta-title {{
            color: #3498DB;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        .cta-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .cta-list li {{
            padding: 8px 0 8px 30px;
            position: relative;
        }}
        .cta-list li:before {{
            content: "✅";
            position: absolute;
            left: 0;
        }}
        .footer {{
            background-color: #1a1a1a;
            color: #cccccc;
            padding: 30px 20px;
            text-align: center;
            font-size: 14px;
        }}
        .footer-logos {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-bottom: 20px;
        }}
        .footer-logo {{
            max-height: 50px;
            max-width: 120px;
            object-fit: contain;
            opacity: 0.9;
        }}
        .footer a {{
            color: #FFD700;
            text-decoration: none;
        }}
        @media only screen and (max-width: 600px) {{
            .container {{
                margin: 0;
                border-radius: 0;
            }}
            .content {{
                padding: 20px 15px;
            }}
            .section-title {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-logos">
                <img src="data:image/png;base64,{logo_mupai_b64}" alt="MUPAI Logo" class="header-logo" />
                <img src="data:image/png;base64,{logo_gym_b64}" alt="Muscle Up GYM Logo" class="header-logo" />
            </div>
            <h1>REPORTE DE EVALUACIÓN CORPORAL</h1>
            <p>Muscle Up Performance Assessment Intelligence</p>
            <p>{datetime.now().strftime("%d de %B, %Y")}</p>
        </div>
        
        <div class="content">
            <p style="font-size: 16px; color: #555;">Hola <strong>{nombre_cliente}</strong>,</p>
            <p style="font-size: 14px; color: #666; margin-bottom: 30px;">
                ¡Gracias por confiar en nosotros para tu evaluación! Aquí están los resultados 
                completos de tu análisis de composición corporal y rendimiento.
            </p>
            
            <!-- DATOS DE EVALUACIÓN -->
            <div class="section">
                <div class="section-title">📊 Datos de Evaluación</div>
                <div class="card">
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Nombre</div>
                            <div class="metric-cell metric-value">{nombre_cliente}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad</div>
                            <div class="metric-cell metric-value">{edad} años</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Sexo</div>
                            <div class="metric-cell metric-value">{sexo}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Fecha de evaluación</div>
                            <div class="metric-cell metric-value">{fecha}</div>
                        </div>
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Fase del ciclo</div>
                            <div class="metric-cell metric-value">{st.session_state.get('ciclo_menstrual', '')}</div>
                        </div>''' if sexo == "Mujer" and st.session_state.get('ciclo_menstrual') else ''}
                    </div>
                </div>
            </div>
            
            <!-- COMPOSICIÓN CORPORAL -->
            <div class="section">
                <div class="section-title">📐 Composición Corporal</div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Medidas Básicas</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Peso corporal</div>
                            <div class="metric-cell metric-value"><strong>{peso:.1f} kg</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Estatura</div>
                            <div class="metric-cell metric-value"><strong>{estatura:.1f} cm</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">IMC</div>
                            <div class="metric-cell metric-value"><strong>{imc:.1f} kg/m²</strong></div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #e3f2fd; border-radius: 5px; border-left: 4px solid #3498DB;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">📊 Sobre tu IMC:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_imc}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_imc}</p>
                    </div>
                </div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Análisis de Tejidos</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">% Grasa corporal</div>
                            <div class="metric-cell metric-value">
                                <strong>{grasa_corregida:.1f}%</strong>
                                <span class="badge badge-{('green' if emoji_grasa == '💪' else 'yellow' if emoji_grasa == '🏃' else 'blue' if emoji_grasa == '📊' else 'red')}">{categoria_grasa}</span>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #FFD700;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💡 Interpretación:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_grasa}</p>
                        <p style="margin: 0 0 8px 0; font-size: 12px; color: #888;">{rango_saludable}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_detallados}</p>
                    </div>
                    <div class="metric-grid" style="margin-top: 15px;">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Masa Grasa</div>
                            <div class="metric-cell metric-value"><strong>{masa_grasa_calc:.1f} kg</strong></div>
                        </div>
                        <div class="metric-row" style="background-color: #fff9e6;">
                            <div class="metric-cell metric-label">Masa Libre de Grasa (MLG)</div>
                            <div class="metric-cell metric-value"><strong>{mlg:.1f} kg ({pct_mlg:.1f}%)</strong></div>
                        </div>
                    </div>
                    
                    <!-- Sección de Masa Muscular -->
                    <div style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 8px; border-left: 4px solid #27AE60;">
                        <h4 style="margin: 0 0 12px 0; color: #27AE60; font-size: 16px;">💪 Masa Muscular Esquelética</h4>
                        
                        {f'''<div style="background-color: rgba(255,255,255,0.9); padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #2196F3;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <span style="font-weight: 600; color: #555;">🔵 Omron (bioimpedancia):</span>
                                <span style="font-size: 18px; font-weight: 700; color: #2196F3;">{masa_muscular_aparato_kg:.1f} kg ({pct_masa_muscular_aparato:.1f}%)</span>
                            </div>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; font-style: italic;">Valor medido directamente por tu báscula de bioimpedancia</p>
                        </div>''' if masa_muscular_aparato > 0 else ''}
                        
                        <div style="background-color: rgba(255,255,255,0.9); padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #9C27B0;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <span style="font-weight: 600; color: #555;">🟣 Estimado científico:</span>
                                <span style="font-size: 18px; font-weight: 700; color: #9C27B0;">{masa_muscular_estimada:.1f} kg ({pct_masa_muscular_estimada:.1f}%)</span>
                            </div>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; font-style: italic;">Calculado desde MLG usando factores por nivel de entrenamiento</p>
                        </div>
                        
                        <div style="background-color: rgba(255,193,7,0.15); padding: 10px; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                            <p style="margin: 0 0 5px 0; font-weight: 600;">📊 ¿Por qué dos valores?</p>
                            <p style="margin: 0 0 5px 0;">• <strong>Omron</strong>: Medición directa por corriente eléctrica (±3-5% error)</p>
                            <p style="margin: 0 0 5px 0;">• <strong>Estimado</strong>: Cálculo desde MLG × factor ({('0.37-0.43' if sexo == 'Hombre' else '0.33-0.40')} según nivel)</p>
                            <p style="margin: 0; font-style: italic; color: #777;">Ambos métodos son válidos. Si difieren mucho (>15%), puede indicar variación en hidratación o método de medición.</p>
                        </div>
                    </div>
                    
                    {f'''<div style="margin-top: 15px; padding: 12px; background-color: #e3f2fd; border-radius: 5px; border-left: 4px solid #3498DB;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💡 Interpretación (usando {('Omron' if masa_muscular_aparato > 0 else 'valor estimado')}):</p>
                        <p style="margin: 0 0 5px 0; font-size: 13px; color: #444;">{feedback_masa_muscular}</p>
                        <p style="margin: 0; font-size: 12px; color: #888;">{rango_masa_muscular}</p>
                    </div>''' if feedback_masa_muscular else ''}
                    
                    <div style="margin-top: 10px; padding: 10px; background-color: #fff3e0; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                        <p style="margin: 0 0 5px 0; font-weight: 600;">🔬 Nota científica:</p>
                        <p style="margin: 0;">La <strong>MLG incluye</strong>: músculo + huesos (~15%) + órganos (~12%) + agua (~30-35%). La masa muscular es solo el componente esquelético contráctil.</p>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #e8f5e9; border-radius: 5px; border-left: 4px solid #27AE60;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💪 Sobre tu masa muscular:</p>
                        <p style="margin: 0 0 5px 0; font-size: 13px; color: #444;">{feedback_masa_muscular}</p>
                        <p style="margin: 0; font-size: 12px; color: #888;">{rango_masa_muscular}</p>
                    </div>
                </div>
            </div>
            
            <!-- ÍNDICES CORPORALES -->
            <div class="section">
                <div class="section-title">📈 Índices Corporales</div>
                
                <div class="index-card">
                    <div class="index-label">💪 FFMI (Índice de Masa Libre de Grasa)</div>
                    <div class="index-value">{ffmi:.1f}</div>
                    <p style="margin: 5px 0 0 0; font-size: 13px; color: #666;">Desarrollo muscular ajustado por altura</p>
                    <div style="margin-top: 10px; padding: 10px; background-color: #fff9e6; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                        <p style="margin: 0 0 5px 0; font-weight: 600;">📊 ¿Qué es el FFMI?</p>
                        <p style="margin: 0;">El FFMI normaliza tu masa muscular según tu altura, permitiendo comparaciones justas entre personas de diferentes estaturas. Es el "IMC del músculo".</p>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: rgba(255,215,0,0.1); border-radius: 5px;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444; font-weight: 600;">💡 Tu nivel:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_ffmi}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_ffmi}</p>
                    </div>
                    <div style="margin-top: 12px; padding: 12px; background-color: {('#d4edda' if modo_ffmi_email == 'GREEN' else '#fff3cd' if modo_ffmi_email == 'AMBER' else '#f8d7da')}; border-radius: 5px; border-left: 4px solid {('#28a745' if modo_ffmi_email == 'GREEN' else '#ffc107' if modo_ffmi_email == 'AMBER' else '#dc3545')};">
                        <p style="margin: 0 0 8px 0; font-size: 13px; font-weight: 600; color: #333;">⚠️ Validez de interpretación:</p>
                        <p style="margin: 0 0 8px 0; font-size: 12px; color: #555; line-height: 1.5;">
                            <strong>{('🟢 ALTA' if modo_ffmi_email == 'GREEN' else '🟡 MODERADA' if modo_ffmi_email == 'AMBER' else '🔴 LIMITADA')}</strong> - 
                            {('Tu % de grasa está en rango saludable. El FFMI refleja fielmente tu desarrollo muscular.' if modo_ffmi_email == 'GREEN' else 'Tu % de grasa está elevado. El FFMI puede estar ligeramente inflado por retención de agua/inflamación.' if modo_ffmi_email == 'AMBER' else 'Tu % de grasa está muy alto o muy bajo. El FFMI no es confiable en este rango debido a alteraciones en la composición de MLG.')}
                        </p>
                        <p style="margin: 0; font-size: 11px; color: #666; font-style: italic;">
                            Rangos válidos: Hombres 12-23%, Mujeres 21-31%. Fuera de estos rangos, la MLG incluye más agua/inflamación que músculo real.
                        </p>
                    </div>
                </div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Índices de Salud</h4>
                    <div class="metric-grid">
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Circunferencia cintura</div>
                            <div class="metric-cell metric-value"><strong>{circunferencia_cintura} cm</strong></div>
                        </div>''' if circunferencia_cintura is not None else ''}
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Ratio Cintura-Altura</div>
                            <div class="metric-cell metric-value">
                                <strong>{wthr:.3f}</strong>
                                <span class="badge badge-{('green' if '🟢' in wthr_clasificacion else 'yellow' if '🟡' in wthr_clasificacion else 'red')}">{wthr_clasificacion.replace(' - 🟢', '').replace(' - 🟡', '').replace(' - 🔴', '')}</span>
                            </div>
                        </div>''' if wthr is not None else ''}
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Grasa visceral</div>
                            <div class="metric-cell metric-value">
                                <strong>Nivel {grasa_visceral}</strong>
                                <span class="badge badge-{('green' if '🟢' in grasa_visceral_clasificacion else 'yellow' if '🟡' in grasa_visceral_clasificacion else 'red')}">{grasa_visceral_clasificacion.replace(' - 🟢', '').replace(' - 🟡', '').replace(' - 🔴', '')}</span>
                            </div>
                        </div>''' if grasa_visceral is not None else ''}
                    </div>
                </div>
                
                {f'''<div style="margin-top: 10px; padding: 12px; background-color: #f0f8ff; border-radius: 5px; border-left: 3px solid #3498DB; font-size: 13px; color: #555;">
                    <p style="margin: 0 0 8px 0; font-weight: 600;">💡 Sobre estos índices:</p>
                    {('<p style="margin: 0 0 5px 0;"><strong>WtHR:</strong> ' + feedback_wthr + '</p><p style="margin: 8px 0 0 0; font-size: 12px; color: #777; line-height: 1.6;">' + rangos_wthr + '</p>') if wthr is not None else ''}
                    {('<p style="margin: 0 0 5px 0;"><strong>Grasa visceral:</strong> ' + feedback_visceral + '</p>') if grasa_visceral is not None else ''}
                    {('<p style="margin: 8px 0 0 0; font-size: 12px; color: #777;"><em>' + info_visceral + '</em></p>') if grasa_visceral is not None else ''}
                </div>''' if wthr is not None or grasa_visceral is not None else ''}
                
                {f'''<div class="card" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-left-color: #3498DB;">
                    <h4 style="margin-top: 0; color: #3498DB;">🧬 Edad Metabólica</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad cronológica</div>
                            <div class="metric-cell metric-value"><strong>{edad} años</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad metabólica</div>
                            <div class="metric-cell metric-value"><strong>{edad_metabolica} años</strong></div>
                        </div>
                    </div>
                    <p style="margin: 15px 0 0 0; padding: 10px; background-color: {'#d4edda' if edad_metabolica < edad else '#fff3cd' if edad_metabolica == edad else '#f8d7da'}; border-radius: 5px; font-size: 14px; text-align: center;">
                        {'✅ Tu metabolismo es ' + str(edad - edad_metabolica) + ' años más joven' if edad_metabolica < edad else '⚠️ Tu metabolismo está ' + str(edad_metabolica - edad) + ' años por encima' if edad_metabolica > edad else '📊 Tu edad metabólica coincide con tu edad'}
                    </p>
                    <div style="margin-top: 12px; padding: 10px; background-color: rgba(255,255,255,0.7); border-radius: 5px; font-size: 12px; color: #555;">
                        <p style="margin: 0 0 8px 0;"><strong>💡 Qué significa:</strong> {feedback_edad_metabolica}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_edad_metabolica}</p>
                    </div>
                </div>''' if edad_metabolica is not None else ''}
            </div>
            
            <!-- NIVEL DE ENTRENAMIENTO -->
            {f'''<div class="section">
                <div class="section-title">💪 Nivel de Entrenamiento</div>
                <div class="card-highlight">
                    NIVEL: {nivel_entrenamiento.upper()}
                </div>
                <p style="font-size: 14px; color: #666; text-align: center;">
                    Este nivel se calcula evaluando tu desarrollo muscular, rendimiento funcional y experiencia de entrenamiento.
                </p>
                <div style="margin-top: 15px; padding: 12px; background-color: #fff9e6; border-radius: 5px; border-left: 3px solid #FFD700; font-size: 13px; color: #555;">
                    <p style="margin: 0; font-weight: 600;">💡 Interpretación de tu nivel:</p>
                    <p style="margin: 8px 0 0 0;">{feedback_nivel}</p>
                </div>
            </div>''' if nivel_entrenamiento else ''}
            
            <!-- ESTADO DE RECUPERACIÓN -->
            {(lambda s: s.replace('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '<div class="section">').replace('😴 ESTADO DE RECUPERACIÓN (SUEÑO + ESTRÉS)', '<div class="section-title">😴 Estado de Recuperación</div>').replace('   ╔════════════════════════════════════════════════════════════════╗' + chr(10) + '   ║  ÍNDICE DE RECUPERACIÓN (IR-SE):', '<div class="index-card"><div class="index-label">Índice de Recuperación (IR-SE)</div><div class="index-value">').replace('/100                   ║' + chr(10) + '   ║  NIVEL:', '/100</div><div style="font-size: 18px; font-weight: 600; margin-top: 10px;">NIVEL:').replace(' ║' + chr(10) + '   ╚════════════════════════════════════════════════════════════════╝' + chr(10) + chr(10) + '   • Calidad de sueño:', '</div></div><div class="card"><div class="metric-grid"><div class="metric-row"><div class="metric-cell metric-label">Calidad de sueño</div><div class="metric-cell metric-value"><strong>').replace('/100' + chr(10) + '   • Nivel de estrés:', '/100</strong></div></div><div class="metric-row"><div class="metric-cell metric-label">Nivel de estrés</div><div class="metric-cell metric-value"><strong>').replace('/100' + chr(10) + '   ' + chr(10) + '   💡 Este índice refleja tu capacidad de recuperación y adaptación al' + chr(10) + '      entrenamiento. Valores bajos pueden limitar tu progreso.', '/100</strong></div></div></div></div><p style="font-size: 14px; color: #666; padding: 15px; background-color: #f0f8ff; border-radius: 5px;">💡 Este índice refleja tu capacidad de recuperación y adaptación al entrenamiento. Valores bajos pueden limitar tu progreso.</p></div>'))(seccion_recuperacion) if seccion_recuperacion else ''}
            
            <!-- FOTOGRAFÍAS -->
            <div class="section">
                <div class="section-title">📸 Fotografías de Progreso</div>
                <div class="card">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        Las fotografías de tu evaluación están adjuntas a este correo para tu registro personal.
                    </p>
                </div>
            </div>
            
            <!-- PRÓXIMOS PASOS -->
            <div class="section">
                <div class="section-title">📱 Próximos Pasos</div>
                <div class="cta-box">
                    <div class="cta-title">Tu coach se pondrá en contacto contigo para:</div>
                    <ul class="cta-list">
                        <li>Revisar en detalle tus resultados</li>
                        <li>Diseñar tu plan nutricional personalizado</li>
                        <li>Establecer objetivos específicos y proyecciones</li>
                        <li>Programar tu seguimiento y ajustes</li>
                    </ul>
                </div>
                <p style="font-size: 14px; color: #666; text-align: center; margin-top: 20px;">
                    Si tienes alguna pregunta o inquietud, no dudes en contactarnos.
                </p>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-logos">
                <img src="data:image/png;base64,{logo_mupai_b64}" alt="MUPAI" class="footer-logo" />
                <img src="data:image/png;base64,{logo_gym_b64}" alt="Muscle Up GYM" class="footer-logo" />
            </div>
            <p style="margin: 0 0 10px 0; font-weight: 600; color: #FFD700;">Muscle Up GYM</p>
            <p style="margin: 0 0 10px 0;">Digital Training Science</p>
            <p style="margin: 0;"><a href="https://muscleupgym.fitness">muscleupgym.fitness</a></p>
            <p style="margin: 5px 0 0 0;"><a href="mailto:administracion@muscleupgym.fitness">administracion@muscleupgym.fitness</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        # Adjuntar versión HTML (preferida)
        msg.attach(MIMEText(contenido_html, 'html', 'utf-8'))
        # Adjuntar versión texto plano como fallback
        msg.attach(MIMEText(contenido, 'plain', 'utf-8'))
        
        # Adjuntar fotos de progreso si están disponibles
        if progress_photos:
            success, total_size_mb, error_msg = attach_progress_photos_to_email(msg, progress_photos)
            if not success:
                st.warning(f"⚠️ No se pudieron adjuntar fotos al email del cliente: {error_msg}")

        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Error al enviar email al cliente: {str(e)}")
        return False

def enviar_email_resumen(contenido, nombre_cliente, email_cliente, fecha, edad, telefono, progress_photos=None):
    """Envía el email COMPLETO CIENTÍFICO a administración."""
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")

        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Resumen evaluación MUPAI - {nombre_cliente} ({fecha})"

        msg.attach(MIMEText(contenido, 'plain'))
        
        # Attach progress photos if provided
        if progress_photos:
            success, total_size_mb, error_msg = attach_progress_photos_to_email(msg, progress_photos)
            if not success:
                st.error(f"Error al adjuntar fotos: {error_msg}")
                return False
            
            # Check if total email size exceeds limit
            if total_size_mb > EMAIL_ATTACHMENT_SIZE_LIMIT_MB:
                st.warning(f"⚠️ El tamaño total de las fotos ({total_size_mb:.2f} MB) excede el límite de email ({EMAIL_ATTACHMENT_SIZE_LIMIT_MB} MB). Se recomienda implementar almacenamiento externo.")
                # For now, we'll still try to send but log the warning

        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Error al enviar email: {str(e)}")
        return False

def clasificar_grasa_visceral(nivel):
    """
    Clasifica el nivel de grasa visceral según rangos saludables.
    
    Args:
        nivel: Nivel de grasa visceral (1-59)
        
    Returns:
        str: Clasificación (Saludable, Elevado, Alto riesgo, o N/D)
    """
    if nivel < 1:
        return "N/D"
    elif nivel <= 12:
        return "Saludable"
    elif nivel <= 15:
        return "Elevado"
    else:
        return "Alto riesgo"

def clasificar_wthr(wthr):
    """
    Clasifica el Waist-to-Height Ratio (Ratio cintura-altura) según rangos saludables.
    
    Args:
        wthr: Waist-to-Height Ratio (circunferencia_cintura / estatura)
        
    Returns:
        str: Clasificación (Saludable, Riesgo aumentado, Alto riesgo, o N/D)
    """
    if wthr <= 0:
        return "N/D"
    elif wthr < 0.5:
        return "Saludable (<0.5)"
    elif wthr < 0.6:
        return "Riesgo aumentado (0.5-0.6)"
    else:
        return "Alto riesgo (≥0.6)"

def clasificar_masa_muscular(porcentaje, edad, sexo):
    """
    Clasifica el porcentaje de masa muscular según edad y sexo.
    Solo aplica cuando el campo está vacío o es N/D.
    
    Args:
        porcentaje: Porcentaje de masa muscular (0-100)
        edad: Edad del cliente
        sexo: "Hombre" o "Mujer"
        
    Returns:
        str: Clasificación (Bajo, Normal, Alto, o N/D)
    """
    # Values <= 0 indicate unmeasured/unavailable data
    # (session state default "" converts to 0.0 via safe_float)
    if porcentaje <= 0:
        return "N/D"
    
    # Rangos aproximados basados en edad y sexo
    if sexo == "Hombre":
        if edad < 40:
            if porcentaje < 33:
                return "Bajo"
            elif porcentaje < 40:
                return "Normal"
            else:
                return "Alto"
        elif edad < 60:
            if porcentaje < 30:
                return "Bajo"
            elif porcentaje < 37:
                return "Normal"
            else:
                return "Alto"
        else:
            if porcentaje < 27:
                return "Bajo"
            elif porcentaje < 34:
                return "Normal"
            else:
                return "Alto"
    else:  # Mujer
        if edad < 40:
            if porcentaje < 24:
                return "Bajo"
            elif porcentaje < 31:
                return "Normal"
            else:
                return "Alto"
        elif edad < 60:
            if porcentaje < 22:
                return "Bajo"
            elif porcentaje < 28:
                return "Normal"
            else:
                return "Alto"
        else:
            if porcentaje < 20:
                return "Bajo"
            elif porcentaje < 26:
                return "Normal"
            else:
                return "Alto"

def format_photo_status(progress_photos):
    """
    Format the photo status message for email body.
    
    Args:
        progress_photos: Dictionary with photo files or None
    
    Returns:
        str: Formatted status message
    """
    if not progress_photos:
        return "✗ Sin fotografías adjuntas"
    
    # Check if optional photo is present
    has_optional = progress_photos.get("pose_libre") is not None
    
    if has_optional:
        return "✓ 4 fotografías adjuntas (frontal, lateral, posterior, pose libre)"
    else:
        return "✓ 3 fotografías adjuntas (frontal, lateral, posterior)"

def enviar_email_parte2(nombre_cliente, fecha, edad, sexo, peso, estatura, imc, grasa_corregida, 
                        mlg, ffmi=None, nivel_entrenamiento=None, circunferencia_cintura=None, grasa_visceral=None, 
                        edad_metabolica=None, wthr=None, masa_grasa=None, progress_photos=None, 
                        masa_muscular_aparato=0, masa_muscular_estimada=0, masa_muscular=None, tmb=None, ciclo_menstrual=None):
    """
    Envía el email interno (Parte 2) con TODO EL CONTENIDO IDÉNTICO del email cliente.
    Destinatario exclusivo: administracion@muscleupgym.fitness (sin CC/BCC)
    
    IMPORTANTE: Este email contiene EXACTAMENTE el mismo contenido HTML que recibe el cliente,
    para que el administrador pueda ver qué información se envió al usuario.
    La única diferencia es el asunto del email que indica que es copia interna.
    
    Args:
        Los mismos parámetros que enviar_email_cliente() para mantener sincronía total.
    """
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")
        
        # Cargar logos para emails (igual que en enviar_email_cliente)
        import base64
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

        # === USAR TODO EL CÓDIGO DEL EMAIL CLIENTE (contenido idéntico) ===
        # Este email contiene EXACTAMENTE el mismo HTML que el cliente recibe
        
        # Calcular valores derivados
        masa_grasa_calc = peso - mlg if masa_grasa is None else masa_grasa
        pct_mlg = (mlg / peso * 100) if peso > 0 else 0
        
        # Calcular modo de interpretación FFMI
        modo_ffmi_email = obtener_modo_interpretacion_ffmi(grasa_corregida, sexo)
        
        # Masa muscular: aparato viene como %, estimada como kg
        # Convertir aparato de % a kg, y calcular % de estimada
        masa_muscular_aparato_kg = (peso * masa_muscular_aparato / 100) if peso > 0 and masa_muscular_aparato > 0 else 0
        pct_masa_muscular_aparato = masa_muscular_aparato  # Ya es porcentaje desde Omron
        pct_masa_muscular_estimada = (masa_muscular_estimada / peso * 100) if peso > 0 and masa_muscular_estimada > 0 else 0
        
        # Clasificar WtHR si está disponible
        wthr_clasificacion = ""
        if wthr is not None:
            if wthr < 0.40:
                wthr_clasificacion = " - 🟢 Extremadamente delgado"
            elif wthr < 0.50:
                wthr_clasificacion = " - 🟢 Saludable"
            elif wthr < 0.60:
                wthr_clasificacion = " - 🟡 Sobrepeso"
            else:
                wthr_clasificacion = " - 🔴 Obesidad"
        
        # Clasificar grasa visceral si está disponible
        grasa_visceral_clasificacion = ""
        if grasa_visceral is not None:
            if grasa_visceral < 10:
                grasa_visceral_clasificacion = " - 🟢 Nivel saludable"
            elif grasa_visceral < 15:
                grasa_visceral_clasificacion = " - 🟡 Nivel elevado"
            else:
                grasa_visceral_clasificacion = " - 🔴 Nivel alto (riesgo)"
        
        # Variables para compatibilidad con contenido texto plano (legacy)
        circunferencia_cintura_val = circunferencia_cintura if circunferencia_cintura is not None else 0
        masa_muscular_val = masa_muscular if masa_muscular is not None else 0
        grasa_visceral_val = grasa_visceral if grasa_visceral is not None else 0
        clasificacion_wthr = wthr_clasificacion.replace(' - ', '').replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')
        clasificacion_grasa_visceral = grasa_visceral_clasificacion.replace(' - ', '').replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')
        clasificacion_masa_muscular = "Normal"  # Placeholder para el texto plano

        # Categorizar grasa corporal con feedback detallado
        if sexo == "Hombre":
            if grasa_corregida < 6:
                categoria_grasa = "Muy bajo (Competición)"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel de competición. Difícil de mantener a largo plazo. Puede afectar hormonas y rendimiento."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 12:
                categoria_grasa = "Atlético"
                emoji_grasa = "💪"
                feedback_grasa = "Excelente nivel. Buena definición muscular visible. Rendimiento deportivo óptimo."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • <strong>6-12%: Atlético/Competición (muy definido) ← Tú estás aquí</strong><br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 18:
                categoria_grasa = "Fitness"
                emoji_grasa = "🏃"
                feedback_grasa = "Nivel fitness saludable. Buena relación salud-estética. Sostenible a largo plazo."
                rango_saludable = "Rango saludable: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • <strong>12-18%: Fitness (saludable, estético) ← Tú estás aquí</strong><br>
                • 18-25%: Promedio aceptable<br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 25:
                categoria_grasa = "Promedio"
                emoji_grasa = "📊"
                feedback_grasa = "Nivel promedio. Espacio para mejorar composición corporal con entrenamiento y nutrición."
                rango_saludable = "Rango fitness: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • <strong>18-25%: Promedio aceptable ← Tú estás aquí</strong><br>
                • 25-30%: Sobrepeso (considerar reducir)<br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
            else:
                categoria_grasa = "Alto"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel elevado. Recomendable reducir para mejorar salud metabólica y reducir riesgos."
                rango_saludable = "Rango fitness: 12-18%"
                rangos_detallados = """
                <strong>Rangos de referencia (Hombres):</strong><br>
                • 3-6%: Esencial (mínimo para sobrevivir)<br>
                • 6-12%: Atlético/Competición (muy definido)<br>
                • 12-18%: Fitness (saludable, estético)<br>
                • 18-25%: Promedio aceptable<br>
                • <strong>25-30%: Sobrepeso (considerar reducir) ← Tú estás aquí</strong><br>
                • 30%+: Obesidad (riesgo metabólico alto)
                """
        else:  # Mujer
            if grasa_corregida < 12:
                categoria_grasa = "Muy bajo (Competición)"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel de competición. Muy difícil de mantener. Puede afectar ciclo menstrual y hormonas."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 17:
                categoria_grasa = "Atlético"
                emoji_grasa = "💪"
                feedback_grasa = "Excelente nivel atlético. Muy buena definición muscular. Rendimiento deportivo óptimo."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • <strong>12-17%: Atlético/Competición (muy definido) ← Tú estás aquí</strong><br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 23:
                categoria_grasa = "Fitness"
                emoji_grasa = "🏃"
                feedback_grasa = "Nivel fitness saludable. Buena relación salud-estética. Sostenible a largo plazo."
                rango_saludable = "Rango saludable: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • <strong>17-23%: Fitness (saludable, estético) ← Tú estás aquí</strong><br>
                • 23-30%: Promedio aceptable<br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            elif grasa_corregida < 30:
                categoria_grasa = "Promedio"
                emoji_grasa = "📊"
                feedback_grasa = "Nivel promedio. Espacio para mejorar composición corporal con entrenamiento y nutrición."
                rango_saludable = "Rango fitness: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • <strong>23-30%: Promedio aceptable ← Tú estás aquí</strong><br>
                • 30-35%: Sobrepeso (considerar reducir)<br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
            else:
                categoria_grasa = "Alto"
                emoji_grasa = "⚠️"
                feedback_grasa = "Nivel elevado. Recomendable reducir para mejorar salud metabólica y reducir riesgos."
                rango_saludable = "Rango fitness: 17-23%"
                rangos_detallados = """
                <strong>Rangos de referencia (Mujeres):</strong><br>
                • 10-12%: Esencial (mínimo, puede afectar fertilidad)<br>
                • 12-17%: Atlético/Competición (muy definido)<br>
                • 17-23%: Fitness (saludable, estético)<br>
                • 23-30%: Promedio aceptable<br>
                • <strong>30-35%: Sobrepeso (considerar reducir) ← Tú estás aquí</strong><br>
                • 35%+: Obesidad (riesgo metabólico alto)
                """
        
        # Feedback para FFMI si está disponible
        feedback_ffmi = ""
        rangos_ffmi = ""
        if ffmi is not None:
            if sexo == "Hombre":
                if ffmi < 18:
                    feedback_ffmi = "Por debajo del promedio. Potencial de ganancia muscular significativo con entrenamiento."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • <strong>&lt;18: Por debajo del promedio ← Tú estás aquí</strong><br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 20:
                    feedback_ffmi = "Nivel promedio. Desarrollo muscular natural normal. Buen punto de partida."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • <strong>18-20: Promedio (desarrollo natural normal) ← Tú estás aquí</strong><br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 22:
                    feedback_ffmi = "Por encima del promedio. Buen desarrollo muscular. Nivel de entrenamiento intermedio-avanzado."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • <strong>20-22: Por encima del promedio (buen entrenamiento) ← Tú estás aquí</strong><br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                elif ffmi < 25:
                    feedback_ffmi = "Excelente desarrollo. Nivel avanzado. Años de entrenamiento consistente."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • <strong>22-25: Excelente (años de entrenamiento) ← Tú estás aquí</strong><br>
                    • 25+: Elite/excepcional (límite natural ~25-26)
                    """
                else:
                    feedback_ffmi = "Elite/excepcional. Desarrollo muscular muy avanzado. Genética favorable o entrenamiento de años."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Hombres):</strong><br>
                    • &lt;18: Por debajo del promedio<br>
                    • 18-20: Promedio (desarrollo natural normal)<br>
                    • 20-22: Por encima del promedio (buen entrenamiento)<br>
                    • 22-25: Excelente (años de entrenamiento)<br>
                    • <strong>25+: Elite/excepcional (límite natural ~25-26) ← Tú estás aquí</strong>
                    """
            else:  # Mujer
                if ffmi < 15:
                    feedback_ffmi = "Por debajo del promedio. Potencial de ganancia muscular significativo con entrenamiento."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • <strong>&lt;15: Por debajo del promedio ← Tú estás aquí</strong><br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 17:
                    feedback_ffmi = "Nivel promedio. Desarrollo muscular natural normal. Buen punto de partida."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • <strong>15-17: Promedio (desarrollo natural normal) ← Tú estás aquí</strong><br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 18:
                    feedback_ffmi = "Por encima del promedio. Buen desarrollo muscular. Nivel intermedio-avanzado."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • <strong>17-18: Por encima del promedio (buen entrenamiento) ← Tú estás aquí</strong><br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                elif ffmi < 20:
                    feedback_ffmi = "Excelente desarrollo. Nivel avanzado. Años de entrenamiento consistente."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • <strong>18-20: Excelente (años de entrenamiento) ← Tú estás aquí</strong><br>
                    • 20+: Elite/excepcional (límite natural ~20-21)
                    """
                else:
                    feedback_ffmi = "Elite/excepcional. Desarrollo muscular muy avanzado. Genética favorable o entrenamiento de años."
                    rangos_ffmi = """
                    <strong>Rangos FFMI (Mujeres):</strong><br>
                    • &lt;15: Por debajo del promedio<br>
                    • 15-17: Promedio (desarrollo natural normal)<br>
                    • 17-18: Por encima del promedio (buen entrenamiento)<br>
                    • 18-20: Excelente (años de entrenamiento)<br>
                    • <strong>20+: Elite/excepcional (límite natural ~20-21) ← Tú estás aquí</strong>
                    """
        
        # Feedback para IMC (Índice de Masa Corporal)
        feedback_imc = ""
        rangos_imc = ""
        if imc < 16:
            feedback_imc = "Delgadez severa. Por debajo del peso saludable. Considera consulta nutricional."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • <strong>&lt;16: Delgadez severa ← Tú estás aquí</strong><br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 17:
            feedback_imc = "Delgadez moderada. Por debajo del peso recomendado. Evalúa aumentar masa muscular."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • <strong>16-17: Delgadez moderada ← Tú estás aquí</strong><br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 18.5:
            feedback_imc = "Delgadez leve. Cerca del rango saludable. Considera ganar masa muscular."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • <strong>17-18.5: Delgadez leve ← Tú estás aquí</strong><br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 25:
            feedback_imc = "¡Excelente! Normopeso. Rango saludable según OMS. Mantén buenos hábitos."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • <strong>18.5-25: Normopeso (saludable) ← Tú estás aquí</strong><br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 30:
            feedback_imc = "Sobrepeso. Riesgo moderado de complicaciones metabólicas. Beneficio de reducir grasa."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • <strong>25-30: Sobrepeso ← Tú estás aquí</strong><br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 35:
            feedback_imc = "Obesidad grado I. Riesgo incrementado. Importante reducir grasa corporal para salud."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • <strong>30-35: Obesidad grado I ← Tú estás aquí</strong><br>
            • 35-40: Obesidad grado II<br>
            • 40+: Obesidad grado III (mórbida)
            """
        elif imc < 40:
            feedback_imc = "Obesidad grado II (severa). Alto riesgo. Prioritario trabajar en reducción de peso."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • <strong>35-40: Obesidad grado II ← Tú estás aquí</strong><br>
            • 40+: Obesidad grado III (mórbida)
            """
        else:
            feedback_imc = "Obesidad grado III (mórbida). Riesgo muy alto. Urgente intervención médica y nutricional."
            rangos_imc = """
            <strong>Clasificación IMC (OMS):</strong><br>
            • &lt;16: Delgadez severa<br>
            • 16-17: Delgadez moderada<br>
            • 17-18.5: Delgadez leve<br>
            • 18.5-25: Normopeso (saludable)<br>
            • 25-30: Sobrepeso<br>
            • 30-35: Obesidad grado I<br>
            • 35-40: Obesidad grado II<br>
            • <strong>40+: Obesidad grado III (mórbida) ← Tú estás aquí</strong>
            """
        
        # Feedback para edad metabólica
        feedback_edad_metabolica = ""
        rangos_edad_metabolica = ""
        if edad_metabolica is not None:
            diff_edad = edad - edad_metabolica
            if diff_edad > 5:
                feedback_edad_metabolica = "¡Excelente! Tu metabolismo está significativamente más joven. Refleja buenos hábitos y composición corporal saludable."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • <strong>Tu edad real - metabólica = {diff:.0f} años (Excelente) ← Tú estás aquí</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=diff_edad)
            elif diff_edad > 0:
                feedback_edad_metabolica = "Bien. Tu metabolismo es ligeramente más joven. Continúa con buenos hábitos de entrenamiento y nutrición."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • <strong>1-5 años menor: Buen estado, por encima del promedio ← Tú estás aquí ({diff:.0f} años)</strong><br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=diff_edad)
            elif diff_edad == 0:
                feedback_edad_metabolica = "Tu edad metabólica coincide con tu edad cronológica. Hay espacio para mejorar con ejercicio y nutrición."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • <strong>Igual: Normal, hay espacio para mejorar ← Tú estás aquí</strong><br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """
            elif diff_edad > -5:
                feedback_edad_metabolica = "Tu metabolismo está ligeramente envejecido. Mejorar composición corporal ayudará a revertir esto."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • <strong>1-5 años mayor: Atención, prioriza mejorar composición ← Tú estás aquí ({diff:.0f} años)</strong><br>
                • Más de 5 años mayor: Urgente optimizar estilo de vida
                """.format(diff=abs(diff_edad))
            else:
                feedback_edad_metabolica = "Atención: metabolismo envejecido. Prioriza mejorar composición corporal, ejercicio y hábitos de sueño."
                rangos_edad_metabolica = """
                <strong>Interpretación Edad Metabólica:</strong><br>
                • Más de 5 años menor: Metabolismo juvenil, salud óptima<br>
                • 1-5 años menor: Buen estado, por encima del promedio<br>
                • Igual: Normal, hay espacio para mejorar<br>
                • 1-5 años mayor: Atención, prioriza mejorar composición<br>
                • <strong>Más de 5 años mayor: Urgente optimizar estilo de vida ← Tú estás aquí ({diff:.0f} años)</strong>
                """.format(diff=abs(diff_edad))
        
        # Feedback para WtHR
        feedback_wthr = ""
        rangos_wthr = ""
        if wthr is not None:
            if wthr < 0.40:
                feedback_wthr = "Extremadamente delgado. Considera si es saludable para ti."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • <strong>&lt;0.40: Muy delgado/Atlético ← Tú estás aquí</strong><br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            elif wthr < 0.50:
                feedback_wthr = "¡Excelente! Rango saludable. Bajo riesgo cardiovascular y metabólico."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • <strong>0.40-0.50: Saludable (riesgo CVD bajo) ← Tú estás aquí</strong><br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            elif wthr < 0.60:
                feedback_wthr = "Atención: sobrepeso. Riesgo moderado. Reducir cintura mejorará salud metabólica."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • <strong>0.50-0.60: Sobrepeso (riesgo CVD incrementado) ← Tú estás aquí</strong><br>
                • 0.60+: Obesidad central (riesgo CVD alto)<br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
            else:
                feedback_wthr = "Alerta: obesidad central. Alto riesgo cardiovascular. Prioriza reducir grasa abdominal."
                rangos_wthr = """
                <strong>Rangos WtHR (Waist-to-Height Ratio):</strong><br>
                • &lt;0.40: Muy delgado/Atlético<br>
                • 0.40-0.50: Saludable (riesgo CVD bajo)<br>
                • 0.50-0.60: Sobrepeso (riesgo CVD incrementado)<br>
                • <strong>0.60+: Obesidad central (riesgo CVD alto) ← Tú estás aquí</strong><br><br>
                <em>CVD = Enfermedad cardiovascular. Recomendación general: mantener WtHR &lt;0.50</em>
                """
        
        # Feedback para grasa visceral
        feedback_visceral = ""
        if grasa_visceral is not None:
            if grasa_visceral < 10:
                feedback_visceral = "¡Perfecto! Nivel saludable. La grasa visceral es la más peligrosa y la tuya está bien controlada."
                info_visceral = "Nivel 1-9 = Saludable. Bajo riesgo de diabetes tipo 2, enfermedades cardíacas y síndrome metabólico."
            elif grasa_visceral < 15:
                feedback_visceral = "Atención: nivel elevado. Considera reducirlo con ejercicio cardiovascular y dieta antiinflamatoria."
                info_visceral = "Nivel 10-14 = Elevado. Riesgo moderado. Prioriza ejercicio aeróbico y reducir calorías."
            else:
                feedback_visceral = "Alerta: nivel alto. Aumenta riesgo de diabetes, enfermedades cardíacas. Prioriza reducirlo urgentemente."
                info_visceral = "Nivel 15+ = Alto riesgo. Requiere atención inmediata. La grasa visceral rodea órganos internos."
        
        # Feedback para masa muscular (priorizar aparato, fallback a estimada)
        masa_muscular_para_feedback = masa_muscular_aparato if masa_muscular_aparato > 0 else masa_muscular_estimada
        pct_masa_muscular_para_feedback = pct_masa_muscular_aparato if pct_masa_muscular_aparato > 0 else pct_masa_muscular_estimada
        
        feedback_masa_muscular = ""
        if masa_muscular_para_feedback > 0 and pct_masa_muscular_para_feedback > 0:
            if sexo == "Hombre":
                if pct_masa_muscular_para_feedback < 33:
                    feedback_masa_muscular = "Bajo. Potencial significativo de ganancia muscular con entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 38:
                    feedback_masa_muscular = "Por debajo del promedio. Responderás bien al entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 44:
                    feedback_masa_muscular = "Promedio saludable. Buen punto de partida para desarrollo muscular."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                elif pct_masa_muscular_para_feedback < 50:
                    feedback_masa_muscular = "Por encima del promedio. Buen desarrollo muscular. Sigue con entrenamiento consistente."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
                else:
                    feedback_masa_muscular = "Excelente. Desarrollo muscular avanzado. Mantén con entrenamiento y nutrición óptimos."
                    rango_masa_muscular = "Rango objetivo: 38-44%"
            else:  # Mujer
                if pct_masa_muscular_para_feedback < 28:
                    feedback_masa_muscular = "Bajo. Gran potencial de ganancia muscular con entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 31:
                    feedback_masa_muscular = "Por debajo del promedio. Responderás bien al entrenamiento de fuerza."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 35:
                    feedback_masa_muscular = "Promedio saludable. Buen punto de partida para desarrollo muscular."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                elif pct_masa_muscular_para_feedback < 40:
                    feedback_masa_muscular = "Por encima del promedio. Buen desarrollo muscular. Sigue así."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
                else:
                    feedback_masa_muscular = "Excelente. Desarrollo muscular avanzado. Mantén con entrenamiento y nutrición óptimos."
                    rango_masa_muscular = "Rango objetivo: 31-37%"
        else:
            feedback_masa_muscular = "No hay suficientes datos para evaluar masa muscular."
            rango_masa_muscular = ""
        
        # Feedback para nivel de entrenamiento
        feedback_nivel = ""
        if nivel_entrenamiento:
            if nivel_entrenamiento.lower() == 'principiante':
                feedback_nivel = "Inicio del viaje. Gran potencial de mejora. Enfócate en aprender técnica y crear hábitos consistentes."
            elif nivel_entrenamiento.lower() == 'intermedio':
                feedback_nivel = "Nivel sólido. Ya tienes base. Enfócate en periodización, progresión e intensidad para seguir avanzando."
            elif nivel_entrenamiento.lower() == 'avanzado':
                feedback_nivel = "Nivel avanzado. Años de entrenamiento. Necesitas programación muy específica y recuperación óptima."
            else:
                feedback_nivel = "Tu nivel refleja tu experiencia, desarrollo muscular y capacidad funcional actual."
        
        # Obtener datos de ciclo menstrual si aplica
        ciclo_menstrual_info = ""
        if sexo == "Mujer":
            ciclo = st.session_state.get('ciclo_menstrual', None)
            if ciclo:
                ciclo_menstrual_info = f"\n   • Fase del ciclo menstrual: {ciclo}"
        
        # Obtener datos de sueño y estrés si están disponibles
        seccion_recuperacion = ""
        if st.session_state.get('suenyo_estres_completado', False):
            data_se = st.session_state.get('suenyo_estres_data', {})
            if data_se and 'ir_se' in data_se:
                ir_se = data_se.get('ir_se', 0)
                nivel_recup = data_se.get('nivel_recuperacion', 'No determinado')
                emoji_recup = data_se.get('emoji_nivel', '')
                
                seccion_recuperacion = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😴 ESTADO DE RECUPERACIÓN (SUEÑO + ESTRÉS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ╔════════════════════════════════════════════════════════════════╗
   ║  ÍNDICE DE RECUPERACIÓN (IR-SE): {ir_se:.1f}/100                   ║
   ║  NIVEL: {nivel_recup} {emoji_recup}                                      ║
   ╚════════════════════════════════════════════════════════════════╝

   • Calidad de sueño: {data_se.get('sleep_score', 0):.1f}/100
   • Nivel de estrés: {data_se.get('stress_score', 0):.1f}/100
   
   💡 Este índice refleja tu capacidad de recuperación y adaptación al
      entrenamiento. Valores bajos pueden limitar tu progreso.
"""

        contenido = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   REPORTE DE EVALUACIÓN CORPORAL                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Muscle Up Performance Assessment Intelligence                               ║
║  {datetime.now().strftime("%Y-%m-%d")}                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Hola {nombre_cliente},

¡Gracias por confiar en nosotros para tu evaluación! Aquí están los resultados
completos de tu análisis de composición corporal y rendimiento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DATOS DE EVALUACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 IDENTIFICACIÓN:
   • Nombre: {nombre_cliente}
   • Edad: {edad} años
   • Sexo: {sexo}
   • Fecha de evaluación: {fecha}{ciclo_menstrual_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 COMPOSICIÓN CORPORAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📏 MEDIDAS BÁSICAS:
   
   ╔════════════════════════════════════════════════════════════════╗
   ║  Peso corporal:         {peso:.1f} kg                              ║
   ║  Estatura:              {estatura:.1f} cm                           ║
   ║  IMC:                   {imc:.1f} kg/m²                         ║
   ╚════════════════════════════════════════════════════════════════╝

📊 ANÁLISIS DE TEJIDOS:

   ╔════════════════════════════════════════════════════════════════╗
   ║  % Grasa corporal:      {grasa_corregida:.1f}% {emoji_grasa}                        ║
   ║  Categoría:             {categoria_grasa}                  ║
   ║                                                                ║
   ║  Masa Grasa:            {masa_grasa_calc:.1f} kg                            ║
   ║  Masa Libre de Grasa (MLG): {mlg:.1f} kg ({pct_mlg:.1f}%)              ║
   ╚════════════════════════════════════════════════════════════════╝
   
   💪 MASA MUSCULAR ESQUELÉTICA:
   {f'   🔵 Omron (medido):      {masa_muscular_aparato_kg:.1f} kg ({pct_masa_muscular_aparato:.1f}%)' if masa_muscular_aparato > 0 else ''}
   🟣 Estimado científico: {masa_muscular_estimada:.1f} kg ({pct_masa_muscular_estimada:.1f}%)
   
   📝 Nota: Omron mide directamente; estimado se calcula desde MLG.
      Si difieren >15%, puede ser por hidratación o método.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ÍNDICES CORPORALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💪 FFMI (Índice de Masa Libre de Grasa):
   • Valor: {ffmi:.1f} {'(dato no disponible)' if ffmi is None else ''}
   • Indicador: Desarrollo muscular ajustado por altura
   
⚕️ ÍNDICES DE SALUD:"""

        # Agregar circunferencia de cintura y WtHR si están disponibles
        if circunferencia_cintura is not None:
            contenido += f"""
   • Circunferencia de cintura: {circunferencia_cintura} cm"""
        
        if wthr is not None:
            contenido += f"""
   • Ratio Cintura-Altura (WtHR): {wthr:.3f}{wthr_clasificacion}"""
        
        if grasa_visceral is not None:
            contenido += f"""
   • Grasa visceral: Nivel {grasa_visceral}{grasa_visceral_clasificacion}"""
        
        if edad_metabolica is not None:
            contenido += f"""

🧬 EDAD METABÓLICA:
   • Edad cronológica: {edad} años
   • Edad metabólica: {edad_metabolica} años
   • {'✅ Tu metabolismo es ' + str(edad - edad_metabolica) + ' años más joven' if edad_metabolica < edad else '⚠️ Tu metabolismo está ' + str(edad_metabolica - edad) + ' años por encima' if edad_metabolica > edad else '📊 Tu edad metabólica coincide con tu edad'}"""

        # Agregar nivel de entrenamiento si está disponible
        if nivel_entrenamiento:
            contenido += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 NIVEL DE ENTRENAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ╔════════════════════════════════════════════════════════════════╗
   ║  NIVEL: {nivel_entrenamiento.upper()}                                       ║
   ╚════════════════════════════════════════════════════════════════╝
   
   Este nivel se calcula evaluando tu desarrollo muscular, rendimiento
   funcional y experiencia de entrenamiento."""

        # Agregar sección de recuperación si está disponible
        contenido += seccion_recuperacion

        contenido += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 FOTOGRAFÍAS DE PROGRESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Las fotografías de tu evaluación están adjuntas a este correo para tu registro.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 PRÓXIMOS PASOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu coach se pondrá en contacto contigo para:

   ✅ Revisar en detalle tus resultados
   ✅ Diseñar tu plan nutricional personalizado
   ✅ Establecer objetivos específicos y proyecciones
   ✅ Programar tu seguimiento y ajustes

Si tienes alguna pregunta o inquietud, no dudes en contactarnos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Muscle Up GYM
Digital Training Science
muscleupgym.fitness
administracion@muscleupgym.fitness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        msg = MIMEMultipart('alternative')
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Resultados de tu Evaluación Corporal - {nombre_cliente}"

        
        # Construir el cuerpo del email profesional (texto plano como fallback)
        contenido = f"""
=====================================
REPORTE DE EVALUACIÓN — PARTE 2
(Lectura Visual, Línea Base)
=====================================
Sistema: MUPAI v2.0 - Muscle Up Performance Assessment Intelligence
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=====================================
INFORMACIÓN DEL CLIENTE
=====================================
Nombre completo: {nombre_cliente}
Fecha de evaluación: {fecha}
Edad: {edad} años
Sexo: {sexo}
{f"Fase del ciclo menstrual: {ciclo_menstrual}" if ciclo_menstrual else ""}

=====================================
COMPOSICIÓN CORPORAL — LÍNEA BASE
=====================================

📊 ANTROPOMETRÍA BÁSICA:
   • Peso corporal: {peso:.1f} kg
   • Estatura: {estatura:.1f} cm ({estatura/100:.2f} m)
   • IMC: {imc:.1f} kg/m²
   • Circunferencia de cintura: {f"{circunferencia_cintura_val:.1f} cm" if circunferencia_cintura_val > 0 else "[____]"}
   • Ratio Cintura-Altura (WtHR): {f"{wthr:.3f}" if wthr > 0 else "[____]"}
     {f"→ Clasificación: {clasificacion_wthr}" if wthr > 0 else ""}

📊 COMPOSICIÓN CORPORAL (MÉTODO DEXA-EQUIVALENTE):
   • % Grasa corporal (corregido DEXA): {grasa_corregida:.1f}%
   • Masa Libre de Grasa (MLG): {mlg:.1f} kg
   • Masa Grasa: {peso - mlg:.1f} kg

📊 INDICADORES OPCIONALES MEDIDOS:
   • % Masa muscular: {f"{masa_muscular_val:.1f}%" if masa_muscular_val > 0 else "[____]"}
     {f"→ Clasificación: {clasificacion_masa_muscular}" if masa_muscular_val > 0 else ""}
     
   • Grasa visceral (nivel): {grasa_visceral_val if grasa_visceral_val >= 1 else "[____]"}
     {f"→ Clasificación: {clasificacion_grasa_visceral}" if grasa_visceral_val >= 1 else ""}

📊 METABOLISMO BASAL:
   • TMB (Cunningham): {tmb:.0f} kcal/día

📷 FOTOGRAFÍAS DE PROGRESO:
   {format_photo_status(progress_photos)}

=====================================
NOTAS IMPORTANTES
=====================================
✓ Este es un reporte de LÍNEA BASE (baseline evaluation)
✓ No incluye comparaciones con sesiones previas
✓ Las clasificaciones automáticas se aplican SOLO cuando los campos están vacíos o marcados como N/D
✓ Los datos existentes y sus clasificaciones originales se respetan sin sustitución

=====================================
RECORDATORIO PROFESIONAL
=====================================
• Este reporte es exclusivamente para uso interno administrativo
• Basado en evaluación científica con corrección DEXA
• Requiere interpretación por profesional calificado
• Los valores [____] indican datos no medidos o no disponibles

=====================================
© 2025 MUPAI - Muscle Up GYM
Digital Training Science
muscleupgym.fitness
=====================================
"""

        contenido_html = f"""

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #FFD700;
            padding: 30px 20px;
            text-align: center;
            position: relative;
        }}
        .header-logos {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 0 20px;
        }}
        .header-logo {{
            max-height: 60px;
            max-width: 150px;
            object-fit: contain;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            color: #cccccc;
            font-size: 14px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            color: #1a1a1a;
            padding: 12px 15px;
            margin: 0 -20px 20px -20px;
            font-size: 18px;
            font-weight: 600;
            border-left: 5px solid #FF8C00;
        }}
        .info-row {{
            display: table;
            width: 100%;
            margin-bottom: 10px;
        }}
        .info-label {{
            font-weight: 600;
            color: #555555;
            margin-right: 10px;
        }}
        .info-value {{
            color: #1a1a1a;
        }}
        .card {{
            background-color: #f9f9f9;
            border-left: 4px solid #FFD700;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        .card-highlight {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #1a1a1a;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 600;
            font-size: 18px;
        }}
        .metric-grid {{
            display: table;
            width: 100%;
            border-collapse: collapse;
        }}
        .metric-row {{
            display: table-row;
        }}
        .metric-cell {{
            display: table-cell;
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            vertical-align: middle;
        }}
        .metric-label {{
            font-weight: 600;
            color: #555555;
            width: 50%;
        }}
        .metric-value {{
            color: #1a1a1a;
            font-size: 16px;
            text-align: right;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-green {{
            background-color: #27AE60;
            color: white;
        }}
        .badge-yellow {{
            background-color: #F39C12;
            color: white;
        }}
        .badge-red {{
            background-color: #E74C3C;
            color: white;
        }}
        .badge-blue {{
            background-color: #3498DB;
            color: white;
        }}
        .index-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #FFD700;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            text-align: center;
        }}
        .index-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 10px 0;
        }}
        .index-label {{
            font-size: 14px;
            color: #555555;
            margin-bottom: 5px;
        }}
        .cta-box {{
            background-color: #f0f8ff;
            border: 2px solid #3498DB;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .cta-title {{
            color: #3498DB;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        .cta-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .cta-list li {{
            padding: 8px 0 8px 30px;
            position: relative;
        }}
        .cta-list li:before {{
            content: "✅";
            position: absolute;
            left: 0;
        }}
        .footer {{
            background-color: #1a1a1a;
            color: #cccccc;
            padding: 30px 20px;
            text-align: center;
            font-size: 14px;
        }}
        .footer-logos {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-bottom: 20px;
        }}
        .footer-logo {{
            max-height: 50px;
            max-width: 120px;
            object-fit: contain;
            opacity: 0.9;
        }}
        .footer a {{
            color: #FFD700;
            text-decoration: none;
        }}
        @media only screen and (max-width: 600px) {{
            .container {{
                margin: 0;
                border-radius: 0;
            }}
            .content {{
                padding: 20px 15px;
            }}
            .section-title {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-logos">
                <img src="data:image/png;base64,{logo_mupai_b64}" alt="MUPAI Logo" class="header-logo" />
                <img src="data:image/png;base64,{logo_gym_b64}" alt="Muscle Up GYM Logo" class="header-logo" />
            </div>
            <h1>REPORTE INTERNO — PARTE 2</h1>
            <p>Muscle Up Performance Assessment Intelligence</p>
            <p>{datetime.now().strftime("%d de %B, %Y")}</p>
            <span class="badge-internal">🔒 CONFIDENCIAL - USO INTERNO</span>
        </div>
        
        <div class="content">
            <p style="font-size: 16px; color: #555;">Hola <strong>{nombre_cliente}</strong>,</p>
            <p style="font-size: 14px; color: #666; margin-bottom: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px;">
                <strong>⚠️ Nota administrativa:</strong> Este reporte contiene TODA la información enviada al cliente para referencia interna.
            </p>
            <p style="font-size: 14px; color: #666; margin-bottom: 30px;">
                ¡Gracias por confiar en nosotros para tu evaluación! Aquí están los resultados 
                completos de tu análisis de composición corporal y rendimiento.
            </p>
            
            <!-- DATOS DE EVALUACIÓN -->
            <div class="section">
                <div class="section-title">📊 Datos de Evaluación</div>
                <div class="card">
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Nombre</div>
                            <div class="metric-cell metric-value">{nombre_cliente}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad</div>
                            <div class="metric-cell metric-value">{edad} años</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Sexo</div>
                            <div class="metric-cell metric-value">{sexo}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Fecha de evaluación</div>
                            <div class="metric-cell metric-value">{fecha}</div>
                        </div>
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Fase del ciclo</div>
                            <div class="metric-cell metric-value">{st.session_state.get('ciclo_menstrual', '')}</div>
                        </div>''' if sexo == "Mujer" and st.session_state.get('ciclo_menstrual') else ''}
                    </div>
                </div>
            </div>
            
            <!-- COMPOSICIÓN CORPORAL -->
            <div class="section">
                <div class="section-title">📐 Composición Corporal</div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Medidas Básicas</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Peso corporal</div>
                            <div class="metric-cell metric-value"><strong>{peso:.1f} kg</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Estatura</div>
                            <div class="metric-cell metric-value"><strong>{estatura:.1f} cm</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">IMC</div>
                            <div class="metric-cell metric-value"><strong>{imc:.1f} kg/m²</strong></div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #e3f2fd; border-radius: 5px; border-left: 4px solid #3498DB;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">📊 Sobre tu IMC:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_imc}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_imc}</p>
                    </div>
                </div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Análisis de Tejidos</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">% Grasa corporal</div>
                            <div class="metric-cell metric-value">
                                <strong>{grasa_corregida:.1f}%</strong>
                                <span class="badge badge-{('green' if emoji_grasa == '💪' else 'yellow' if emoji_grasa == '🏃' else 'blue' if emoji_grasa == '📊' else 'red')}">{categoria_grasa}</span>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #FFD700;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💡 Interpretación:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_grasa}</p>
                        <p style="margin: 0 0 8px 0; font-size: 12px; color: #888;">{rango_saludable}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_detallados}</p>
                    </div>
                    <div class="metric-grid" style="margin-top: 15px;">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Masa Grasa</div>
                            <div class="metric-cell metric-value"><strong>{masa_grasa_calc:.1f} kg</strong></div>
                        </div>
                        <div class="metric-row" style="background-color: #fff9e6;">
                            <div class="metric-cell metric-label">Masa Libre de Grasa (MLG)</div>
                            <div class="metric-cell metric-value"><strong>{mlg:.1f} kg ({pct_mlg:.1f}%)</strong></div>
                        </div>
                    </div>
                    
                    <!-- Sección de Masa Muscular -->
                    <div style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 8px; border-left: 4px solid #27AE60;">
                        <h4 style="margin: 0 0 12px 0; color: #27AE60; font-size: 16px;">💪 Masa Muscular Esquelética</h4>
                        
                        {f'''<div style="background-color: rgba(255,255,255,0.9); padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #2196F3;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <span style="font-weight: 600; color: #555;">🔵 Omron (bioimpedancia):</span>
                                <span style="font-size: 18px; font-weight: 700; color: #2196F3;">{masa_muscular_aparato_kg:.1f} kg ({pct_masa_muscular_aparato:.1f}%)</span>
                            </div>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; font-style: italic;">Valor medido directamente por tu báscula de bioimpedancia</p>
                        </div>''' if masa_muscular_aparato > 0 else ''}
                        
                        <div style="background-color: rgba(255,255,255,0.9); padding: 12px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #9C27B0;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <span style="font-weight: 600; color: #555;">🟣 Estimado científico:</span>
                                <span style="font-size: 18px; font-weight: 700; color: #9C27B0;">{masa_muscular_estimada:.1f} kg ({pct_masa_muscular_estimada:.1f}%)</span>
                            </div>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; font-style: italic;">Calculado desde MLG usando factores por nivel de entrenamiento</p>
                        </div>
                        
                        <div style="background-color: rgba(255,193,7,0.15); padding: 10px; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                            <p style="margin: 0 0 5px 0; font-weight: 600;">📊 ¿Por qué dos valores?</p>
                            <p style="margin: 0 0 5px 0;">• <strong>Omron</strong>: Medición directa por corriente eléctrica (±3-5% error)</p>
                            <p style="margin: 0 0 5px 0;">• <strong>Estimado</strong>: Cálculo desde MLG × factor ({('0.37-0.43' if sexo == 'Hombre' else '0.33-0.40')} según nivel)</p>
                            <p style="margin: 0; font-style: italic; color: #777;">Ambos métodos son válidos. Si difieren mucho (>15%), puede indicar variación en hidratación o método de medición.</p>
                        </div>
                    </div>
                    
                    {f'''<div style="margin-top: 15px; padding: 12px; background-color: #e3f2fd; border-radius: 5px; border-left: 4px solid #3498DB;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💡 Interpretación (usando {('Omron' if masa_muscular_aparato > 0 else 'valor estimado')}):</p>
                        <p style="margin: 0 0 5px 0; font-size: 13px; color: #444;">{feedback_masa_muscular}</p>
                        <p style="margin: 0; font-size: 12px; color: #888;">{rango_masa_muscular}</p>
                    </div>''' if feedback_masa_muscular else ''}
                    
                    <div style="margin-top: 10px; padding: 10px; background-color: #fff3e0; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                        <p style="margin: 0 0 5px 0; font-weight: 600;">🔬 Nota científica:</p>
                        <p style="margin: 0;">La <strong>MLG incluye</strong>: músculo + huesos (~15%) + órganos (~12%) + agua (~30-35%). La masa muscular es solo el componente esquelético contráctil.</p>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: #e8f5e9; border-radius: 5px; border-left: 4px solid #27AE60;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-weight: 600;">💪 Sobre tu masa muscular:</p>
                        <p style="margin: 0 0 5px 0; font-size: 13px; color: #444;">{feedback_masa_muscular}</p>
                        <p style="margin: 0; font-size: 12px; color: #888;">{rango_masa_muscular}</p>
                    </div>
                </div>
            </div>
            
            <!-- ÍNDICES CORPORALES -->
            <div class="section">
                <div class="section-title">📈 Índices Corporales</div>
                
                <div class="index-card">
                    <div class="index-label">💪 FFMI (Índice de Masa Libre de Grasa)</div>
                    <div class="index-value">{ffmi:.1f}</div>
                    <p style="margin: 5px 0 0 0; font-size: 13px; color: #666;">Desarrollo muscular ajustado por altura</p>
                    <div style="margin-top: 10px; padding: 10px; background-color: #fff9e6; border-radius: 5px; font-size: 12px; color: #555; line-height: 1.5;">
                        <p style="margin: 0 0 5px 0; font-weight: 600;">📊 ¿Qué es el FFMI?</p>
                        <p style="margin: 0;">El FFMI normaliza tu masa muscular según tu altura, permitiendo comparaciones justas entre personas de diferentes estaturas. Es el "IMC del músculo".</p>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background-color: rgba(255,215,0,0.1); border-radius: 5px;">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444; font-weight: 600;">💡 Tu nivel:</p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #444;">{feedback_ffmi}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_ffmi}</p>
                    </div>
                    <div style="margin-top: 12px; padding: 12px; background-color: {('#d4edda' if modo_ffmi_email == 'GREEN' else '#fff3cd' if modo_ffmi_email == 'AMBER' else '#f8d7da')}; border-radius: 5px; border-left: 4px solid {('#28a745' if modo_ffmi_email == 'GREEN' else '#ffc107' if modo_ffmi_email == 'AMBER' else '#dc3545')};">
                        <p style="margin: 0 0 8px 0; font-size: 13px; font-weight: 600; color: #333;">⚠️ Validez de interpretación:</p>
                        <p style="margin: 0 0 8px 0; font-size: 12px; color: #555; line-height: 1.5;">
                            <strong>{('🟢 ALTA' if modo_ffmi_email == 'GREEN' else '🟡 MODERADA' if modo_ffmi_email == 'AMBER' else '🔴 LIMITADA')}</strong> - 
                            {('Tu % de grasa está en rango saludable. El FFMI refleja fielmente tu desarrollo muscular.' if modo_ffmi_email == 'GREEN' else 'Tu % de grasa está elevado. El FFMI puede estar ligeramente inflado por retención de agua/inflamación.' if modo_ffmi_email == 'AMBER' else 'Tu % de grasa está muy alto o muy bajo. El FFMI no es confiable en este rango debido a alteraciones en la composición de MLG.')}
                        </p>
                        <p style="margin: 0; font-size: 11px; color: #666; font-style: italic;">
                            Rangos válidos: Hombres 12-23%, Mujeres 21-31%. Fuera de estos rangos, la MLG incluye más agua/inflamación que músculo real.
                        </p>
                    </div>
                </div>
                
                <div class="card">
                    <h4 style="margin-top: 0; color: #555;">Índices de Salud</h4>
                    <div class="metric-grid">
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Circunferencia cintura</div>
                            <div class="metric-cell metric-value"><strong>{circunferencia_cintura} cm</strong></div>
                        </div>''' if circunferencia_cintura is not None else ''}
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Ratio Cintura-Altura</div>
                            <div class="metric-cell metric-value">
                                <strong>{wthr:.3f}</strong>
                                <span class="badge badge-{('green' if '🟢' in wthr_clasificacion else 'yellow' if '🟡' in wthr_clasificacion else 'red')}">{wthr_clasificacion.replace(' - 🟢', '').replace(' - 🟡', '').replace(' - 🔴', '')}</span>
                            </div>
                        </div>''' if wthr is not None else ''}
                        {f'''<div class="metric-row">
                            <div class="metric-cell metric-label">Grasa visceral</div>
                            <div class="metric-cell metric-value">
                                <strong>Nivel {grasa_visceral}</strong>
                                <span class="badge badge-{('green' if '🟢' in grasa_visceral_clasificacion else 'yellow' if '🟡' in grasa_visceral_clasificacion else 'red')}">{grasa_visceral_clasificacion.replace(' - 🟢', '').replace(' - 🟡', '').replace(' - 🔴', '')}</span>
                            </div>
                        </div>''' if grasa_visceral is not None else ''}
                    </div>
                </div>
                
                {f'''<div style="margin-top: 10px; padding: 12px; background-color: #f0f8ff; border-radius: 5px; border-left: 3px solid #3498DB; font-size: 13px; color: #555;">
                    <p style="margin: 0 0 8px 0; font-weight: 600;">💡 Sobre estos índices:</p>
                    {('<p style="margin: 0 0 5px 0;"><strong>WtHR:</strong> ' + feedback_wthr + '</p><p style="margin: 8px 0 0 0; font-size: 12px; color: #777; line-height: 1.6;">' + rangos_wthr + '</p>') if wthr is not None else ''}
                    {('<p style="margin: 0 0 5px 0;"><strong>Grasa visceral:</strong> ' + feedback_visceral + '</p>') if grasa_visceral is not None else ''}
                    {('<p style="margin: 8px 0 0 0; font-size: 12px; color: #777;"><em>' + info_visceral + '</em></p>') if grasa_visceral is not None else ''}
                </div>''' if wthr is not None or grasa_visceral is not None else ''}
                
                {f'''<div class="card" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-left-color: #3498DB;">
                    <h4 style="margin-top: 0; color: #3498DB;">🧬 Edad Metabólica</h4>
                    <div class="metric-grid">
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad cronológica</div>
                            <div class="metric-cell metric-value"><strong>{edad} años</strong></div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-cell metric-label">Edad metabólica</div>
                            <div class="metric-cell metric-value"><strong>{edad_metabolica} años</strong></div>
                        </div>
                    </div>
                    <p style="margin: 15px 0 0 0; padding: 10px; background-color: {'#d4edda' if edad_metabolica < edad else '#fff3cd' if edad_metabolica == edad else '#f8d7da'}; border-radius: 5px; font-size: 14px; text-align: center;">
                        {'✅ Tu metabolismo es ' + str(edad - edad_metabolica) + ' años más joven' if edad_metabolica < edad else '⚠️ Tu metabolismo está ' + str(edad_metabolica - edad) + ' años por encima' if edad_metabolica > edad else '📊 Tu edad metabólica coincide con tu edad'}
                    </p>
                    <div style="margin-top: 12px; padding: 10px; background-color: rgba(255,255,255,0.7); border-radius: 5px; font-size: 12px; color: #555;">
                        <p style="margin: 0 0 8px 0;"><strong>💡 Qué significa:</strong> {feedback_edad_metabolica}</p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.6;">{rangos_edad_metabolica}</p>
                    </div>
                </div>''' if edad_metabolica is not None else ''}
            </div>
            
            <!-- NIVEL DE ENTRENAMIENTO -->
            {f'''<div class="section">
                <div class="section-title">💪 Nivel de Entrenamiento</div>
                <div class="card-highlight">
                    NIVEL: {nivel_entrenamiento.upper()}
                </div>
                <p style="font-size: 14px; color: #666; text-align: center;">
                    Este nivel se calcula evaluando tu desarrollo muscular, rendimiento funcional y experiencia de entrenamiento.
                </p>
                <div style="margin-top: 15px; padding: 12px; background-color: #fff9e6; border-radius: 5px; border-left: 3px solid #FFD700; font-size: 13px; color: #555;">
                    <p style="margin: 0; font-weight: 600;">💡 Interpretación de tu nivel:</p>
                    <p style="margin: 8px 0 0 0;">{feedback_nivel}</p>
                </div>
            </div>''' if nivel_entrenamiento else ''}
            
            <!-- ESTADO DE RECUPERACIÓN -->
            {(lambda s: s.replace('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '<div class="section">').replace('😴 ESTADO DE RECUPERACIÓN (SUEÑO + ESTRÉS)', '<div class="section-title">😴 Estado de Recuperación</div>').replace('   ╔════════════════════════════════════════════════════════════════╗' + chr(10) + '   ║  ÍNDICE DE RECUPERACIÓN (IR-SE):', '<div class="index-card"><div class="index-label">Índice de Recuperación (IR-SE)</div><div class="index-value">').replace('/100                   ║' + chr(10) + '   ║  NIVEL:', '/100</div><div style="font-size: 18px; font-weight: 600; margin-top: 10px;">NIVEL:').replace(' ║' + chr(10) + '   ╚════════════════════════════════════════════════════════════════╝' + chr(10) + chr(10) + '   • Calidad de sueño:', '</div></div><div class="card"><div class="metric-grid"><div class="metric-row"><div class="metric-cell metric-label">Calidad de sueño</div><div class="metric-cell metric-value"><strong>').replace('/100' + chr(10) + '   • Nivel de estrés:', '/100</strong></div></div><div class="metric-row"><div class="metric-cell metric-label">Nivel de estrés</div><div class="metric-cell metric-value"><strong>').replace('/100' + chr(10) + '   ' + chr(10) + '   💡 Este índice refleja tu capacidad de recuperación y adaptación al' + chr(10) + '      entrenamiento. Valores bajos pueden limitar tu progreso.', '/100</strong></div></div></div></div><p style="font-size: 14px; color: #666; padding: 15px; background-color: #f0f8ff; border-radius: 5px;">💡 Este índice refleja tu capacidad de recuperación y adaptación al entrenamiento. Valores bajos pueden limitar tu progreso.</p></div>'))(seccion_recuperacion) if seccion_recuperacion else ''}
            
            <!-- FOTOGRAFÍAS -->
            <div class="section">
                <div class="section-title">📸 Fotografías de Progreso</div>
                <div class="card">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        Las fotografías de tu evaluación están adjuntas a este correo para tu registro personal.
                    </p>
                </div>
            </div>
            
            <!-- PRÓXIMOS PASOS -->
            <div class="section">
                <div class="section-title">📱 Próximos Pasos</div>
                <div class="cta-box">
                    <div class="cta-title">Tu coach se pondrá en contacto contigo para:</div>
                    <ul class="cta-list">
                        <li>Revisar en detalle tus resultados</li>
                        <li>Diseñar tu plan nutricional personalizado</li>
                        <li>Establecer objetivos específicos y proyecciones</li>
                        <li>Programar tu seguimiento y ajustes</li>
                    </ul>
                </div>
                <p style="font-size: 14px; color: #666; text-align: center; margin-top: 20px;">
                    Si tienes alguna pregunta o inquietud, no dudes en contactarnos.
                </p>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-logos">
                <img src="data:image/png;base64,{logo_mupai_b64}" alt="MUPAI" class="footer-logo" />
                <img src="data:image/png;base64,{logo_gym_b64}" alt="Muscle Up GYM" class="footer-logo" />
            </div>
            <p style="margin: 0 0 10px 0; font-weight: 600; color: #FFD700;">Muscle Up GYM</p>
            <p style="margin: 0 0 10px 0;">Digital Training Science</p>
            <p style="margin: 0;"><a href="https://muscleupgym.fitness">muscleupgym.fitness</a></p>
            <p style="margin: 5px 0 0 0;"><a href="mailto:administracion@muscleupgym.fitness">administracion@muscleupgym.fitness</a></p>
        </div>
    </div>
</body>
</html>"""

        msg = MIMEMultipart('alternative')
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"[COPIA INTERNA] Reporte de Evaluación Corporal — {nombre_cliente} — {fecha}"

        # Adjuntar versión texto plano como fallback
        msg.attach(MIMEText(contenido, 'plain', 'utf-8'))
        # Adjuntar versión HTML (preferida)
        msg.attach(MIMEText(contenido_html, 'html', 'utf-8'))
        
        # Attach progress photos if provided
        if progress_photos:
            success, total_size_mb, error_msg = attach_progress_photos_to_email(msg, progress_photos)
            if not success:
                st.error(f"Error al adjuntar fotos en Parte 2: {error_msg}")
                return False

        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Error al enviar email Parte 2: {str(e)}")
        return False

def enviar_email_yaml(datos_completos):
    """
    Envía email a administración con TODO el contenido del reporte completo en formato YAML.
    
    Propósito: Facilitar el procesamiento de datos por ChatGPT u otros LLMs.
    El formato YAML es más fácil de parsear que HTML para análisis automatizado.
    
    Args:
        datos_completos: Diccionario con TODOS los datos del Email 1 (reporte completo)
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    try:
        import yaml
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")
        
        # Extraer nombre y fecha del diccionario anidado
        nombre_cliente = datos_completos.get('datos_personales', {}).get('nombre_cliente', 'N/A')
        fecha = datos_completos.get('metadata', {}).get('fecha_evaluacion', datetime.now().strftime("%Y-%m-%d"))
        
        # Generar contenido YAML estructurado
        yaml_content = yaml.dump(datos_completos, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"📊 YAML Data Export — {nombre_cliente} — {fecha}"
        
        # Cuerpo del email explicativo
        body = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    REPORTE COMPLETO EN FORMATO YAML                         ║
║                  Para procesamiento por ChatGPT/LLMs                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Cliente: {nombre_cliente}
Fecha: {fecha}
Sistema: MUPAI v2.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PROPÓSITO:
   Este archivo contiene TODOS los datos del reporte completo en formato YAML
   para facilitar su procesamiento por ChatGPT u otros sistemas de IA.

📊 CONTENIDO INCLUIDO:
   ✅ Datos personales (nombre, edad, sexo, contacto)
   ✅ Composición corporal completa (peso, estatura, IMC, grasa, MLG)
   ✅ Índices corporales (FFMI, WtHR, grasa visceral, edad metabólica)
   ✅ Macronutrientes tradicionales (proteína, grasa, carbohidratos)
   ✅ Plan PSMF (si aplica)
   ✅ Proyecciones de progreso (1, 2, 3 meses)
   ✅ Metabolismo (TMB, GE, GEAF)
   ✅ Nivel de entrenamiento
   ✅ Sueño y estrés (si disponible)
   ✅ Clasificaciones y feedbacks

💡 USO SUGERIDO:
   - Copiar el contenido YAML en ChatGPT para análisis
   - Usar en proyectos de automatización
   - Crear dashboards personalizados
   - Comparar evolución entre evaluaciones

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTENIDO YAML:

{yaml_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

© 2025 MUPAI - Muscle Up GYM
Digital Training Science
muscleupgym.fitness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Enviar
        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error al enviar email YAML: {str(e)}")
        return False

# ==================== CUESTIONARIO SUEÑO + ESTRÉS ====================

def formulario_suenyo_estres():
    """
    Cuestionario modular para evaluar el Estado de Recuperación (Sueño + Estrés).
    
    Captura datos sin mostrar puntuaciones al usuario. Los cálculos se realizan
    silenciosamente en segundo plano y se incluyen en el reporte final enviado
    a administración.
    
    Calcula (silenciosamente):
    - SleepScore: Puntuación de calidad del sueño (0-100)
    - StressScore: Puntuación de nivel de estrés (0-100)
    - IR-SE: Índice de Recuperación Sueño-Estrés
    - Clasificación: ALTA, MEDIA, BAJA recuperación
    - Banderas de alerta: Detección de problemas graves
    
    Returns:
        dict: Diccionario con resultados calculados para incluir en email
    """
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 😴 Estado de Recuperación (Sueño + Estrés)")
    st.markdown("""
    Por favor responde las siguientes preguntas sobre tu calidad de sueño y nivel de estrés. 
    Esta información será incluida en tu reporte de evaluación para un análisis integral.
    """)
    
    # Initialize session state for sleep/stress data
    if 'suenyo_estres_completado' not in st.session_state:
        st.session_state.suenyo_estres_completado = False
    if 'suenyo_estres_data' not in st.session_state:
        st.session_state.suenyo_estres_data = {}
    
    # ========== PREGUNTAS DE SUEÑO ==========
    st.markdown("#### 🌙 Sección 1: Calidad del Sueño")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pregunta 1: Horas de sueño
        horas_sueno = st.selectbox(
            "¿Cuántas horas duermes en promedio por noche?",
            options=[
                "≥8 horas",
                "7-7.9 horas",
                "6-6.9 horas",
                "5-5.9 horas",
                "<5 horas"
            ],
            help="Selecciona el rango que mejor describe tu promedio de sueño"
        )
        
        # Pregunta 2: Tiempo para conciliar el sueño
        tiempo_conciliar = st.selectbox(
            "¿Cuánto tiempo tardas en quedarte dormido?",
            options=[
                "Menos de 15 minutos",
                "15-30 minutos",
                "30-60 minutos",
                "Más de 60 minutos"
            ],
            help="Tiempo promedio desde que te acuestas hasta que te duermes"
        )
    
    with col2:
        # Pregunta 3: Despertares nocturnos
        veces_despierta = st.selectbox(
            "¿Cuántas veces te despiertas durante la noche?",
            options=[
                "Ninguna",
                "1 vez",
                "2 veces",
                "3 o más veces"
            ],
            help="Número promedio de despertares por noche"
        )
        
        # Pregunta 4: Calidad del sueño
        calidad_sueno = st.selectbox(
            "¿Cómo calificarías la calidad general de tu sueño?",
            options=[
                "Excelente",
                "Buena",
                "Regular",
                "Mala",
                "Muy mala"
            ],
            help="Calificación subjetiva de qué tan reparador es tu sueño"
        )
    
    # ========== PREGUNTAS DE ESTRÉS ==========
    st.markdown("#### 🧠 Sección 2: Nivel de Estrés")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Pregunta 5: Sensación de sobrecarga
        sobrecarga = st.selectbox(
            "¿Con qué frecuencia te sientes sobrecargado o abrumado?",
            options=[
                "Nunca",
                "Casi nunca",
                "A veces",
                "Frecuentemente",
                "Muy frecuentemente"
            ],
            help="Evalúa tu sensación de estar desbordado por responsabilidades"
        )
        
        # Pregunta 6: Falta de control
        falta_control = st.selectbox(
            "¿Con qué frecuencia sientes que no puedes controlar las cosas importantes de tu vida?",
            options=[
                "Nunca",
                "Casi nunca",
                "A veces",
                "Frecuentemente",
                "Muy frecuentemente"
            ],
            help="Sensación de control sobre tu vida y circunstancias"
        )
    
    with col4:
        # Pregunta 7: Dificultad para manejar
        dificultad_manejar = st.selectbox(
            "¿Con qué frecuencia sientes que las dificultades se acumulan tanto que no puedes manejarlas?",
            options=[
                "Nunca",
                "Casi nunca",
                "A veces",
                "Frecuentemente",
                "Muy frecuentemente"
            ],
            help="Capacidad para enfrentar problemas y desafíos"
        )
        
        # Pregunta 8: Irritabilidad
        irritabilidad = st.selectbox(
            "¿Con qué frecuencia te sientes irritable o molesto sin razón aparente?",
            options=[
                "Nunca",
                "Casi nunca",
                "A veces",
                "Frecuentemente",
                "Muy frecuentemente"
            ],
            help="Nivel de irritabilidad en tu día a día"
        )
    
    # ========== CÁLCULO SILENCIOSO DE PUNTUACIONES ==========
    # Los cálculos se realizan cada vez que se ejecuta el formulario
    # No se muestran resultados al usuario, solo se capturan para el reporte
    
    # Puntuaciones de sueño
    puntos_horas = {
        "≥8 horas": 0,
        "7-7.9 horas": 1,
        "6-6.9 horas": 2,
        "5-5.9 horas": 3,
        "<5 horas": 4
    }
    
    puntos_conciliar = {
        "Menos de 15 minutos": 0,
        "15-30 minutos": 1,
        "30-60 minutos": 2,
        "Más de 60 minutos": 3
    }
    
    puntos_despertares = {
        "Ninguna": 0,
        "1 vez": 1,
        "2 veces": 2,
        "3 o más veces": 3
    }
    
    puntos_calidad = {
        "Excelente": 0,
        "Buena": 1,
        "Regular": 2,
        "Mala": 3,
        "Muy mala": 4
    }
    
    # Puntuaciones de estrés
    puntos_estres = {
        "Nunca": 0,
        "Casi nunca": 1,
        "A veces": 2,
        "Frecuentemente": 3,
        "Muy frecuentemente": 4
    }
    
    # Calcular puntuación total de sueño (0-14 puntos)
    sleep_raw = (
        puntos_horas[horas_sueno] +
        puntos_conciliar[tiempo_conciliar] +
        puntos_despertares[veces_despierta] +
        puntos_calidad[calidad_sueno]
    )
    
    # Calcular puntuación total de estrés (0-16 puntos)
    stress_raw = (
        puntos_estres[sobrecarga] +
        puntos_estres[falta_control] +
        puntos_estres[dificultad_manejar] +
        puntos_estres[irritabilidad]
    )
    
    # Normalizar a 0-100 (invertido: menor puntuación = mejor)
    # Para sueño: 0 puntos = 100 score, 14 puntos = 0 score
    sleep_score = max(0, 100 - (sleep_raw / 14 * 100))
    
    # Para estrés: 0 puntos = 100 score, 16 puntos = 0 score
    stress_score = max(0, 100 - (stress_raw / 16 * 100))
    
    # Calcular IR-SE (Índice de Recuperación Sueño-Estrés)
    # Ponderación: 60% sueño, 40% estrés (el sueño es más crítico para recuperación)
    ir_se = (sleep_score * 0.6) + (stress_score * 0.4)
    
    # Clasificar recuperación
    if ir_se >= 70:
        nivel_recuperacion = "ALTA"
        color_nivel = "#27AE60"
        emoji_nivel = "✅"
        mensaje_nivel = "Excelente estado de recuperación. Tu cuerpo está bien preparado para el entrenamiento."
    elif ir_se >= 50:
        nivel_recuperacion = "MEDIA"
        color_nivel = "#F39C12"
        emoji_nivel = "⚠️"
        mensaje_nivel = "Estado de recuperación moderado. Considera mejorar la calidad del sueño o reducir el estrés."
    else:
        nivel_recuperacion = "BAJA"
        color_nivel = "#E74C3C"
        emoji_nivel = "🚨"
        mensaje_nivel = "Estado de recuperación comprometido. Es importante abordar problemas de sueño y/o estrés."
    
    # Detectar banderas rojas y amarillas
    banderas = []
    
    # Banderas rojas (problemas graves)
    if sleep_raw >= 10:  # Sueño muy problemático
        banderas.append(("🔴 BANDERA ROJA", "Problemas graves de sueño detectados", 
                       "Tu calidad y cantidad de sueño están significativamente comprometidas. "
                       "Considera consultar con un especialista en medicina del sueño."))
    
    if stress_raw >= 12:  # Estrés muy alto
        banderas.append(("🔴 BANDERA ROJA", "Nivel de estrés crítico", 
                       "Tu nivel de estrés está en rango muy alto. "
                       "Se recomienda buscar apoyo profesional (psicólogo o terapeuta)."))
    
    # Banderas amarillas (problemas moderados)
    if 7 <= sleep_raw < 10:
        banderas.append(("🟡 BANDERA AMARILLA", "Calidad de sueño subóptima", 
                       "Tu sueño necesita atención. Implementa higiene del sueño: "
                       "horarios regulares, ambiente oscuro, evitar pantallas antes de dormir."))
    
    if 8 <= stress_raw < 12:
        banderas.append(("🟡 BANDERA AMARILLA", "Nivel de estrés elevado", 
                       "Tu nivel de estrés está por encima del ideal. "
                       "Considera técnicas de manejo: meditación, ejercicio, tiempo libre."))
    
    if puntos_horas[horas_sueno] >= 3:  # Menos de 6 horas
        banderas.append(("🟡 BANDERA AMARILLA", "Duración de sueño insuficiente", 
                       f"Duermes {horas_sueno}. Se recomiendan al menos 7-8 horas para recuperación óptima."))
    
    # Guardar en session state (silenciosamente - no mostrar al usuario)
    st.session_state.suenyo_estres_data = {
        'horas_sueno': horas_sueno,
        'tiempo_conciliar': tiempo_conciliar,
        'veces_despierta': veces_despierta,
        'calidad_sueno': calidad_sueno,
        'sobrecarga': sobrecarga,
        'falta_control': falta_control,
        'dificultad_manejar': dificultad_manejar,
        'irritabilidad': irritabilidad,
        'sleep_raw': sleep_raw,
        'stress_raw': stress_raw,
        'sleep_score': sleep_score,
        'stress_score': stress_score,
        'ir_se': ir_se,
        'nivel_recuperacion': nivel_recuperacion,
        'color_nivel': color_nivel,
        'emoji_nivel': emoji_nivel,
        'mensaje_nivel': mensaje_nivel,
        'banderas': banderas
    }
    st.session_state.suenyo_estres_completado = True
    
    # Mensaje de confirmación (sin mostrar puntuaciones)
    st.success("✅ Respuestas guardadas. Estos datos serán incluidos en tu reporte de evaluación.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Return data for integration into main email
    return st.session_state.suenyo_estres_data if st.session_state.suenyo_estres_completado else None

def formulario_metas_personales():
    """
    Cuestionario modular para capturar objetivos personales a mediano y largo plazo.
    
    Permite al usuario detallar sus metas relacionadas con composición corporal,
    rendimiento físico, y otros objetivos personales para 6-12 meses y más de 12 meses.
    
    Este campo es obligatorio y debe estar completo antes de poder enviar el cuestionario.
    
    Returns:
        dict: Diccionario con la información de metas personales para incluir en email
    """
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Metas Personales — Objetivos a Mediano y Largo Plazo")
    st.markdown("""
    **Este apartado es obligatorio.** Describe tus objetivos personales relacionados con la composición corporal 
    y rendimiento físico. Esta información nos ayudará a personalizar mejor tu plan de entrenamiento y nutrición.
    """)
    
    # Initialize session state for personal goals
    if 'metas_personales_completado' not in st.session_state:
        st.session_state.metas_personales_completado = False
    if 'metas_personales' not in st.session_state:
        st.session_state.metas_personales = ""
    
    # Instructions and examples
    st.markdown("""
    <div style="background: #252525; padding: 1rem; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 1rem;">
        <h4 style="color: #FFD700; margin-top: 0;">💡 Instrucciones y Ejemplos</h4>
        <p style="color: #CCCCCC; margin-bottom: 0.5rem;">
            Por favor describe tus objetivos específicos considerando los siguientes aspectos:
        </p>
        <ul style="color: #CCCCCC; line-height: 1.8;">
            <li><strong>Composición corporal:</strong> Reducir grasa corporal del X% al Y%, aumentar masa muscular en Z kg</li>
            <li><strong>Rendimiento físico:</strong> Mejorar fuerza en ejercicios específicos, aumentar resistencia cardiovascular</li>
            <li><strong>Objetivos estéticos:</strong> Definición muscular, mejora de zonas específicas del cuerpo</li>
            <li><strong>Salud y bienestar:</strong> Reducir factores de riesgo metabólico, mejorar calidad de sueño, reducir estrés</li>
            <li><strong>Plazos:</strong> Distingue entre metas a mediano plazo (6-12 meses) y largo plazo (más de 12 meses)</li>
        </ul>
        <p style="color: #CCCCCC; margin-bottom: 0; font-style: italic;">
            <strong>Ejemplo:</strong> "A mediano plazo (6-12 meses): Reducir grasa corporal del 25% al 18%, aumentar 
            masa muscular en 3-4 kg, mejorar mi rendimiento en press de banca de 60kg a 80kg. A largo plazo (más de 12 meses): 
            Mantener un porcentaje de grasa corporal entre 12-15%, competir en mi primera carrera de medio maratón, 
            desarrollar un físico atlético y funcional para deportes recreativos."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Text area for personal goals with initial value from session state
    metas_texto = st.text_area(
        "✍️ Describe tus metas personales (mínimo 50 caracteres)*",
        value=st.session_state.metas_personales,
        height=250,
        placeholder="Escribe aquí tus objetivos a mediano plazo (6-12 meses) y largo plazo (más de 12 meses)...",
        help="Campo obligatorio. Describe tus metas específicas de composición corporal, rendimiento físico y bienestar general.",
        key="metas_personales_input"
    )
    
    # Real-time validation and feedback
    metas_texto_clean = metas_texto.strip() if metas_texto else ""
    char_count = len(metas_texto_clean)
    
    # Character counter with color coding
    if char_count == 0:
        st.markdown(f"""
        <div style="color: #E74C3C; font-weight: bold; margin-top: -10px;">
            ⚠️ Campo vacío. Por favor describe tus metas personales (mínimo 50 caracteres).
        </div>
        """, unsafe_allow_html=True)
    elif char_count < 50:
        st.markdown(f"""
        <div style="color: #F39C12; font-weight: bold; margin-top: -10px;">
            ⚠️ Caracteres: {char_count}/50 (mínimo). Por favor proporciona más detalles sobre tus objetivos.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="color: #27AE60; font-weight: bold; margin-top: -10px;">
            ✅ Caracteres: {char_count} - ¡Perfecto! Tus metas han sido capturadas correctamente.
        </div>
        """, unsafe_allow_html=True)
    
    # Update session state
    st.session_state.metas_personales = metas_texto_clean
    st.session_state.metas_personales_completado = char_count >= 50
    
    # Show confirmation message if complete
    if st.session_state.metas_personales_completado:
        st.success("✅ Metas personales completadas. Esta información será incluida en tu reporte de evaluación.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Return data for integration into main email
    return st.session_state.metas_personales if st.session_state.metas_personales_completado else None

# ==================== CUESTIONARIO CICLO MENSTRUAL ====================

def formulario_ciclo_menstrual(sexo):
    """
    Cuestionario para recoger información sobre la fase del ciclo menstrual.
    Solo se muestra cuando sexo == "Mujer".
    
    La información es obligatoria y se incluye en el reporte sin afectar cálculos.
    
    Args:
        sexo: Sexo biológico del usuario ("Hombre" o "Mujer")
    
    Returns:
        str: Fase del ciclo menstrual seleccionada (None si no aplica)
    """
    # Solo mostrar si es mujer
    if sexo != "Mujer":
        return None
    
    # Initialize session state for menstrual cycle data
    if 'ciclo_menstrual' not in st.session_state:
        st.session_state.ciclo_menstrual = None
    if 'ciclo_menstrual_completado' not in st.session_state:
        st.session_state.ciclo_menstrual_completado = False
    
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🌸 Información del Ciclo Menstrual")
    st.markdown("""
    Esta información es importante para interpretar correctamente los resultados de tu evaluación 
    de bioimpedancia y composición corporal. Por favor responde estas preguntas simples:
    """)
    
    # Opciones del ciclo menstrual con lenguaje más simple y cotidiano
    opciones_ciclo = [
        "Selecciona una opción...",
        "Estoy en mi periodo (menstruando actualmente)",
        "Terminé mi periodo hace 1-7 días (semana después del periodo)",
        "Estoy a mitad de ciclo - días 12-16 (semana en medio del ciclo)",
        "Estoy en la segunda mitad del ciclo - días 17-28 (1-2 semanas antes del siguiente periodo)",
        "No tengo ciclo menstrual (menopausia, embarazo, condición médica, o anticonceptivos sin regla)"
    ]
    
    # Calculate index for selectbox (restore previous selection if exists)
    default_index = 0
    if st.session_state.ciclo_menstrual and st.session_state.ciclo_menstrual in opciones_ciclo:
        default_index = opciones_ciclo.index(st.session_state.ciclo_menstrual)
    
    # Select box para la fase del ciclo
    ciclo_seleccionado = st.selectbox(
        "🌸 ¿En qué momento de tu ciclo menstrual estás?*",
        options=opciones_ciclo,
        index=default_index,
        help="Selecciona la opción que mejor describe tu situación actual. Si no estás segura del día exacto, elige la opción que más se acerque."
    )
    
    # Validación: no se permite continuar sin seleccionar una opción válida
    if ciclo_seleccionado == "Selecciona una opción...":
        st.warning("⚠️ **Campo obligatorio:** Por favor selecciona en qué momento de tu ciclo menstrual estás para continuar.")
        st.session_state.ciclo_menstrual_completado = False
        
        # Agregar ayuda adicional
        with st.expander("❓ ¿Necesitas ayuda para responder?"):
            st.markdown("""
            **Guía rápida:**
            
            - **Estoy en mi periodo:** Si estás menstruando actualmente (días 1-5 aprox.)
            
            - **Terminé mi periodo hace 1-7 días:** Si tu periodo terminó hace poco (días 6-12 aprox.)
            
            - **Estoy a mitad de ciclo:** Si estás aproximadamente a la mitad entre un periodo y otro (días 13-16 aprox.)
            
            - **Segunda mitad del ciclo:** Si estás entre la mitad del ciclo y tu próximo periodo (días 17-28 aprox.)
            
            - **No tengo ciclo menstrual:** Si estás en menopausia, embarazada, usas anticonceptivos que eliminan tu periodo, o tienes alguna condición médica que detiene tu ciclo
            
            💡 **Tip:** Si no estás segura del día exacto, no te preocupes. Elige la opción que más se acerque a tu situación actual.
            """)
    else:
        # Guardar en session state
        st.session_state.ciclo_menstrual = ciclo_seleccionado
        st.session_state.ciclo_menstrual_completado = True
        # Extract short name safely (handle cases without parentheses)
        short_name = ciclo_seleccionado.split('(')[0].strip() if '(' in ciclo_seleccionado else ciclo_seleccionado
        st.success(f"✅ Fase registrada: {short_name}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Return data for integration into report
    return st.session_state.ciclo_menstrual if st.session_state.ciclo_menstrual_completado else None

def enviar_email_suenyo_estres(nombre_cliente, email_cliente, fecha, data_suenyo_estres):
    """
    Envía por correo el informe del cuestionario de Sueño + Estrés.
    
    Args:
        nombre_cliente: Nombre del cliente
        email_cliente: Email del cliente
        fecha: Fecha de evaluación
        data_suenyo_estres: Diccionario con los resultados del cuestionario
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")
        
        # Construir el contenido del email
        contenido = f"""
=====================================
EVALUACIÓN SUEÑO + ESTRÉS - MUPAI
=====================================
Sistema: MUPAI v2.0 - Muscle Up Performance Assessment Intelligence
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=====================================
INFORMACIÓN DEL CLIENTE
=====================================
Nombre: {nombre_cliente}
Email: {email_cliente}
Fecha de evaluación: {fecha}

=====================================
RESPUESTAS DEL CUESTIONARIO
=====================================

🌙 SECCIÓN SUEÑO:
   • Horas de sueño: {data_suenyo_estres['horas_sueno']}
   • Tiempo para conciliar: {data_suenyo_estres['tiempo_conciliar']}
   • Despertares nocturnos: {data_suenyo_estres['veces_despierta']}
   • Calidad del sueño: {data_suenyo_estres['calidad_sueno']}

🧠 SECCIÓN ESTRÉS:
   • Sensación de sobrecarga: {data_suenyo_estres['sobrecarga']}
   • Falta de control: {data_suenyo_estres['falta_control']}
   • Dificultad para manejar: {data_suenyo_estres['dificultad_manejar']}
   • Irritabilidad: {data_suenyo_estres['irritabilidad']}

=====================================
RESULTADOS CALCULADOS
=====================================

📊 PUNTUACIONES:
   • Sleep Score: {data_suenyo_estres['sleep_score']:.1f}/100
   • Stress Score: {data_suenyo_estres['stress_score']:.1f}/100
   • Índice IR-SE: {data_suenyo_estres['ir_se']:.1f}/100

📊 PUNTUACIONES DETALLADAS:
   • Puntuación cruda sueño: {data_suenyo_estres['sleep_raw']}/14 puntos
   • Puntuación cruda estrés: {data_suenyo_estres['stress_raw']}/16 puntos

🎯 CLASIFICACIÓN:
   • Nivel de recuperación: {data_suenyo_estres['nivel_recuperacion']}
   • Mensaje: {data_suenyo_estres['mensaje_nivel']}

=====================================
ALERTAS Y BANDERAS
=====================================
"""
        
        if data_suenyo_estres['banderas']:
            for tipo, titulo, descripcion in data_suenyo_estres['banderas']:
                contenido += f"""
{tipo}: {titulo}
{descripcion}

"""
        else:
            contenido += "\n✅ No se detectaron banderas de alerta.\n"
        
        contenido += f"""
=====================================
INTERPRETACIÓN Y RECOMENDACIONES
=====================================

INTERPRETACIÓN GENERAL:
El Índice de Recuperación Sueño-Estrés (IR-SE) de {data_suenyo_estres['ir_se']:.1f} indica
un estado de recuperación {data_suenyo_estres['nivel_recuperacion'].lower()}.

RANGOS DE CLASIFICACIÓN:
• ALTA (70-100): Excelente recuperación, óptimo para entrenamiento
• MEDIA (50-69): Recuperación moderada, atención a mejoras
• BAJA (0-49): Recuperación comprometida, intervención necesaria

FÓRMULA IR-SE:
IR-SE = (Sleep Score × 0.6) + (Stress Score × 0.4)

El sueño tiene mayor peso (60%) porque es el factor más crítico
para la recuperación física y mental.

RECOMENDACIONES GENERALES:
• Mantener horarios regulares de sueño (7-9 horas)
• Crear un ambiente óptimo: oscuro, fresco, silencioso
• Evitar pantallas 1-2 horas antes de dormir
• Practicar técnicas de manejo del estrés: meditación, ejercicio, hobbies
• Considerar ayuda profesional si las puntuaciones son muy bajas

=====================================
© 2025 MUPAI - Muscle Up GYM
Digital Training Science
muscleupgym.fitness
=====================================
"""
        
        # Crear y enviar mensaje
        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Evaluación Sueño + Estrés - {nombre_cliente} - {fecha}"
        
        msg.attach(MIMEText(contenido, 'plain'))
        
        # Comprobar si estamos en modo desarrollo
        development_mode = password == "TU_PASSWORD_AQUI"
        
        if not development_mode:
            server = smtplib.SMTP('smtp.zoho.com', 587)
            server.starttls()
            server.login(email_origen, password)
            server.send_message(msg)
            server.quit()
        
        return True
        
    except Exception as e:
        st.error(f"Error al enviar email de Sueño + Estrés: {str(e)}")
        return False

def attach_progress_photos_to_email(msg, progress_photos):
    """
    Attaches progress photos to an email message.
    
    Args:
        msg: MIMEMultipart email message object
        progress_photos: Dictionary with photo files {key: UploadedFile}
    
    Returns:
        tuple: (success, total_size_mb, error_message)
    """
    try:
        total_size = 0
        photo_mapping = {
            "front_relaxed": "PHOTO1_front_relaxed",
            "side_relaxed_right": "PHOTO2_side_relaxed_right",
            "back_relaxed": "PHOTO3_back_relaxed",
            "pose_libre": "PHOTO4_pose_libre"
        }
        
        # Check required photos
        for key in REQUIRED_PROGRESS_PHOTOS:
            photo = progress_photos.get(key)
            if photo is None:
                return False, 0, f"Falta foto requerida: {key}"
        
        # Attach all available photos (required + optional)
        for key, filename_prefix in photo_mapping.items():
            photo = progress_photos.get(key)
            if photo is None:
                # Skip optional photos if not provided
                if key in OPTIONAL_PROGRESS_PHOTOS:
                    continue
                # Should not reach here for required photos due to check above
                return False, 0, f"Falta foto: {key}"
            
            # Get file extension
            file_extension = photo.name.lower().split('.')[-1]
            filename = f"{filename_prefix}.{file_extension}"
            
            # Read photo data and reset file pointer
            photo.seek(0)  # Reset file pointer to beginning
            photo_data = photo.read()
            photo.seek(0)  # Reset again after reading for future access
            total_size += len(photo_data)
            
            # Create attachment
            if file_extension in ['jpg', 'jpeg']:
                attachment = MIMEImage(photo_data, _subtype='jpeg')
            elif file_extension == 'png':
                attachment = MIMEImage(photo_data, _subtype='png')
            else:
                # Fallback to base attachment
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(photo_data)
                encoders.encode_base64(attachment)
            
            attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(attachment)
        
        total_size_mb = total_size / (1024 * 1024)
        return True, total_size_mb, ""
    
    except Exception as e:
        return False, 0, f"Error al adjuntar fotos: {str(e)}"

# ==================== PROGRESS PHOTOS SECTION ====================

def validate_progress_photo(uploaded_file):
    """
    Validates a progress photo for format and size.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "Se requiere una foto"
    
    # Check file extension
    file_extension = uploaded_file.name.lower().split('.')[-1]
    if file_extension not in ['jpg', 'jpeg', 'png']:
        return False, f"Formato no válido. Solo se permiten JPG, JPEG o PNG (recibido: {file_extension})"
    
    # Check file size (100 MB = 100 * 1024 * 1024 bytes)
    # Increased to accommodate high-resolution photos from modern smartphones
    max_size = 100 * 1024 * 1024
    if uploaded_file.size > max_size:
        size_mb = uploaded_file.size / (1024 * 1024)
        return False, f"Archivo muy grande ({size_mb:.1f} MB). Máximo permitido: 100 MB"
    
    return True, ""

def render_progress_photos_section():
    """
    Renders the progress photos upload section with validation.
    This section is isolated and doesn't affect existing logic.
    """
    st.markdown("---")
    st.markdown('<div class="content-card" style="background: #1A1A1A; border-left: 4px solid var(--mupai-yellow);">', unsafe_allow_html=True)
    st.markdown("### 📸 Fotografías de Progreso (PNG o JPG)")
    
    st.markdown("""
    <p style="color: #CCCCCC; line-height: 1.6; margin-bottom: 1.5rem;">
    Sube tus fotos de progreso siguiendo el protocolo (misma luz, misma distancia, cámara a altura del ombligo). 
    <strong style="color: var(--mupai-yellow);">Estas fotos son obligatorias</strong> para evaluar tu composición corporal.
    </p>
    """, unsafe_allow_html=True)
    
    # Initialize session state for photos if not exists
    if "progress_photos" not in st.session_state:
        st.session_state.progress_photos = {
            "front_relaxed": None,
            "side_relaxed_right": None,
            "back_relaxed": None,
            "pose_libre": None
        }
    
    # Create three columns for the first row of photo uploads
    col1, col2, col3 = st.columns(3)
    
    validation_errors = []
    
    with col1:
        st.markdown("#### 📷 Foto 1 – Frontal relajado")
        front_photo = st.file_uploader(
            "Foto frontal",
            type=["jpg", "jpeg", "png"],
            key="front_relaxed_uploader",
            help="Foto de frente, brazos a los lados, postura natural",
            label_visibility="collapsed"
        )
        
        if front_photo:
            is_valid, error_msg = validate_progress_photo(front_photo)
            if is_valid:
                st.session_state.progress_photos["front_relaxed"] = front_photo
                st.image(front_photo, caption="✅ Foto frontal cargada", use_container_width=True)
                st.success(f"✓ {front_photo.size / (1024*1024):.2f} MB")
            else:
                st.session_state.progress_photos["front_relaxed"] = None
                st.error(f"❌ {error_msg}")
                validation_errors.append(f"Foto 1 (Frontal): {error_msg}")
        else:
            st.session_state.progress_photos["front_relaxed"] = None
            st.warning("⚠️ Foto frontal requerida")
    
    with col2:
        st.markdown("#### 📷 Foto 2 – Perfil lateral relajado")
        side_photo = st.file_uploader(
            "Foto lateral",
            type=["jpg", "jpeg", "png"],
            key="side_relaxed_right_uploader",
            help="Foto de perfil derecho, brazos a los lados, postura natural",
            label_visibility="collapsed"
        )
        
        if side_photo:
            is_valid, error_msg = validate_progress_photo(side_photo)
            if is_valid:
                st.session_state.progress_photos["side_relaxed_right"] = side_photo
                st.image(side_photo, caption="✅ Foto lateral cargada", use_container_width=True)
                st.success(f"✓ {side_photo.size / (1024*1024):.2f} MB")
            else:
                st.session_state.progress_photos["side_relaxed_right"] = None
                st.error(f"❌ {error_msg}")
                validation_errors.append(f"Foto 2 (Lateral): {error_msg}")
        else:
            st.session_state.progress_photos["side_relaxed_right"] = None
            st.warning("⚠️ Foto lateral requerida")
    
    with col3:
        st.markdown("#### 📷 Foto 3 – Posterior relajado")
        back_photo = st.file_uploader(
            "Foto posterior",
            type=["jpg", "jpeg", "png"],
            key="back_relaxed_uploader",
            help="Foto de espalda, brazos a los lados, postura natural",
            label_visibility="collapsed"
        )
        
        if back_photo:
            is_valid, error_msg = validate_progress_photo(back_photo)
            if is_valid:
                st.session_state.progress_photos["back_relaxed"] = back_photo
                st.image(back_photo, caption="✅ Foto posterior cargada", use_container_width=True)
                st.success(f"✓ {back_photo.size / (1024*1024):.2f} MB")
            else:
                st.session_state.progress_photos["back_relaxed"] = None
                st.error(f"❌ {error_msg}")
                validation_errors.append(f"Foto 3 (Posterior): {error_msg}")
        else:
            st.session_state.progress_photos["back_relaxed"] = None
            st.warning("⚠️ Foto posterior requerida")
    
    # Add spacing between rows
    st.markdown("<br>", unsafe_allow_html=True)
    
    # New section for the free pose photo
    st.markdown("""
    <div style="margin-top: 1.5rem; padding: 1rem; background: #252525; border-radius: 10px; border-left: 3px solid #F39C12;">
        <h4 style="color: #F39C12; margin-bottom: 0.5rem;">📸 Foto Adicional - Pose Libre</h4>
        <p style="color: #CCCCCC; font-size: 0.95rem; margin-bottom: 0;">
            Opcional: Carga una fotografía adicional en la pose que prefieras para complementar tu evaluación.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered column for the free pose photo
    col_spacer1, col_libre, col_spacer2 = st.columns([1, 2, 1])
    
    with col_libre:
        st.markdown("#### 📷 Foto 4 – Pose Libre")
        libre_photo = st.file_uploader(
            "Foto pose libre",
            type=["jpg", "jpeg", "png"],
            key="pose_libre_uploader",
            help="Foto en la pose que prefieras - Opcional",
            label_visibility="collapsed"
        )
        
        if libre_photo:
            is_valid, error_msg = validate_progress_photo(libre_photo)
            if is_valid:
                st.session_state.progress_photos["pose_libre"] = libre_photo
                st.image(libre_photo, caption="✅ Foto pose libre cargada", use_container_width=True)
                st.success(f"✓ {libre_photo.size / (1024*1024):.2f} MB")
            else:
                st.session_state.progress_photos["pose_libre"] = None
                st.error(f"❌ {error_msg}")
                validation_errors.append(f"Foto 4 (Pose Libre): {error_msg}")
        else:
            st.session_state.progress_photos["pose_libre"] = None
            st.info("💡 Foto opcional - No requerida")
    
    # Show validation summary
    if validation_errors:
        st.error("**Errores de validación:**")
        for error in validation_errors:
            st.markdown(f"- {error}")
    
    # Calculate total size of all photos
    total_size = 0
    photos_uploaded = 0
    for key, photo in st.session_state.progress_photos.items():
        if photo is not None:
            total_size += photo.size
            photos_uploaded += 1
    
    # Display upload status
    st.markdown("---")
    
    # Count required photos and optional photo
    required_photos_uploaded = sum(1 for key in REQUIRED_PROGRESS_PHOTOS 
                                   if st.session_state.progress_photos.get(key) is not None)
    optional_photo_uploaded = st.session_state.progress_photos.get("pose_libre") is not None
    
    if required_photos_uploaded == 3:
        total_size_mb = total_size / (1024 * 1024)
        if total_size_mb > EMAIL_ATTACHMENT_SIZE_LIMIT_MB:
            st.warning(f"⚠️ **Advertencia:** El tamaño total de las fotos ({total_size_mb:.2f} MB) excede el límite de email ({EMAIL_ATTACHMENT_SIZE_LIMIT_MB} MB). Las fotos se subirán a almacenamiento externo y se incluirán enlaces en el email.")
        else:
            status_msg = f"✅ Las 3 fotos requeridas están cargadas correctamente"
            if optional_photo_uploaded:
                status_msg += " + 1 foto opcional"
            status_msg += f". Tamaño total: {total_size_mb:.2f} MB"
            st.success(status_msg)
    else:
        status_msg = f"📊 **Estado:** {required_photos_uploaded} de 3 fotos requeridas cargadas"
        if optional_photo_uploaded:
            status_msg += " (+ 1 foto opcional cargada)"
        st.info(status_msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return validation_errors

        # ==================== FUNCIONES DE PROGRESO ====================

def check_step_completion(step_number):
    """Verificar si un paso específico está completo"""
    if step_number == 1:  # Datos personales
        required = ['nombre', 'telefono', 'email_cliente', 'edad', 'sexo', 'acepto_descargo']
        return all(st.session_state.get(field) for field in required)
    elif step_number == 2:  # Composición corporal
        required = ['peso', 'estatura', 'grasa_corporal', 'masa_muscular']
        return all(st.session_state.get(field, 0) > 0 for field in required)
    elif step_number == 3:  # Evaluación funcional
        return (st.session_state.get('experiencia_completa', False) and 
                len(st.session_state.get('datos_ejercicios', {})) >= 5)
    elif step_number == 4:  # Actividad física
        return bool(st.session_state.get('actividad_diaria'))
    elif step_number == 5:  # Entrenamiento
        return (st.session_state.get('frecuencia_entrenamiento', 0) > 0 and
                st.session_state.get('minutos_por_sesion', 0) > 0)
    return False

def get_step_status_indicator(step_number):
    """Obtener indicador visual del estado del paso"""
    if check_step_completion(step_number):
        return '✅', '#27AE60', 'Completado'
    else:
        return '⏳', '#F4C430', 'Pendiente'

def calculate_dynamic_progress():
    """Calcular progreso dinámico basado en campos completados"""
    total_required = 0
    completed = 0
    
    # Datos personales básicos (6 campos)
    personal_fields = {'nombre': st.session_state.get('nombre', ''),
                      'telefono': st.session_state.get('telefono', ''),
                      'email_cliente': st.session_state.get('email_cliente', ''),
                      'edad': st.session_state.get('edad', 0),
                      'sexo': st.session_state.get('sexo', ''),
                      'acepto_descargo': st.session_state.get('acepto_descargo', False)}
    
    for key, val in personal_fields.items():
        total_required += 1
        if val and str(val).strip():
            completed += 1
    
    # Composición corporal (5 campos principales)
    body_fields = {'peso': st.session_state.get('peso', 0),
                   'estatura': st.session_state.get('estatura', 0),
                   'grasa_corporal': st.session_state.get('grasa_corporal', 0),
                   'masa_muscular': st.session_state.get('masa_muscular', 0)}
    
    for key, val in body_fields.items():
        total_required += 1
        if val and val > 0:
            completed += 1
    
    # Experiencia de entrenamiento
    total_required += 1
    if st.session_state.get('experiencia_completa', False):
        completed += 1
    
    # Ejercicios funcionales (5 ejercicios)
    total_required += 5
    ejercicios = st.session_state.get('datos_ejercicios', {})
    completed += min(len(ejercicios), 5)
    
    # Actividad diaria
    total_required += 1
    if st.session_state.get('actividad_diaria'):
        completed += 1
    
    # Frecuencia de entrenamiento (checkear strings, no números)
    total_required += 1
    if st.session_state.get('frecuencia_entrenamiento'):
        completed += 1
    
    # Fotos de progreso (3 requeridas)
    total_required += 3
    photos = st.session_state.get('progress_photos', {})
    for key in REQUIRED_PROGRESS_PHOTOS:
        if photos.get(key):
            completed += 1
    
    percentage = int((completed / total_required) * 100) if total_required > 0 else 0
    return percentage, completed, total_required

# ==================== VISUALES INICIALES ====================

# Progreso dinámico en tiempo real
progress_pct, fields_done, fields_total = calculate_dynamic_progress()
st.markdown(f'''
<div style="background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #F4C430;">
    <h3 style="color: #F4C430; margin: 0 0 1rem 0;">📊 Progreso de Evaluación</h3>
    <div style="background: #0A0A0A; border-radius: 10px; height: 30px; overflow: hidden; margin-bottom: 0.5rem;">
        <div style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); height: 100%; width: {progress_pct}%; transition: width 0.3s ease; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #1E1E1E;">
            {progress_pct}%
        </div>
    </div>
    <p style="color: #AAA; margin: 0; font-size: 0.9rem; text-align: right;">{fields_done} de {fields_total} campos completados</p>
</div>
''', unsafe_allow_html=True)

# Misión, Visión y Compromiso con diseño mejorado
with st.expander("🎯 **Misión, Visión y Compromiso MUPAI**", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(crear_tarjeta(
            "🎯 Misión",
            "Hacer accesible el entrenamiento basado en ciencia, ofreciendo planes personalizados que se adaptan a todos los niveles de condición física.",
            "info"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "👁️ Visión",
            "Ser el referente global en evaluación y entrenamiento digital personalizado, uniendo investigación científica con experiencia práctica.",
            "success"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta(
            "🤝 Compromiso",
            "Nos guiamos por la ética, transparencia y precisión científica para ofrecer resultados reales, medibles y sostenibles.",
            "warning"
        ), unsafe_allow_html=True)

# BLOQUE 0: Datos personales con diseño mejorado
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("### 👤 Información Personal")
st.markdown("Por favor, completa todos los campos para comenzar tu evaluación personalizada.")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre completo*", placeholder="Ej: Juan Pérez García", help="Tu nombre legal completo")
    telefono = st.text_input("Teléfono*", placeholder="Ej: 8661234567", help="10 dígitos sin espacios")
    email_cliente = st.text_input("Email*", placeholder="correo@ejemplo.com", help="Email válido para recibir resultados")

with col2:
    edad = st.number_input("Edad (años)*", min_value=15, max_value=80, value=safe_int(st.session_state.get("edad", 25), 25), help="Tu edad actual")
    sexo = st.selectbox("Sexo biológico*", ["Hombre", "Mujer"], help="Necesario para cálculos precisos")
    fecha_llenado = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

# === DESCARGO DE RESPONSABILIDAD PROFESIONAL ===
with st.expander("⚖️ **Descargo de Responsabilidad Profesional** (Requerido)", expanded=False):
    # Función para crear tarjetas visuales
    def crear_tarjeta(titulo, contenido, tipo="info"):
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
        help="Debes confirmar que has leído y entiendes las limitaciones de esta evaluación"
    )

# Checkbox principal con diseño destacado (solo se habilita si se acepta el descargo)
st.markdown(f"""
<div class="content-card" style="border-left-color: var(--mupai-warning); margin: 1.5rem 0; background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%); border: 2px solid var(--mupai-yellow); box-shadow: 0 8px 25px rgba(244, 196, 48, 0.15);">
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span class="badge badge-warning" style="margin-right: 0.8rem; font-size: 0.9rem;">✅ ACEPTACIÓN REQUERIDA</span>
        <h4 style="margin: 0; color: #FFF; font-size: 1.1rem;">Confirmación Final de Términos</h4>
    </div>
    <div style="background: rgba(244, 196, 48, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid var(--mupai-yellow); margin-bottom: 1rem;">
        <p style="color: #FFF; margin: 0; font-weight: 500; font-size: 1.05rem;">
            <strong style="color: var(--mupai-yellow);">⚠️ IMPORTANTE:</strong> 
            Para continuar con tu evaluación personalizada, debes confirmar que has leído y aceptas completamente nuestros términos y el descargo de responsabilidad profesional.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

acepto_terminos = st.checkbox(
    "✅ **He leído y acepto la política de privacidad y el descargo de responsabilidad**",
    disabled=not st.session_state.get("acepto_descargo", False),
    help="Primero debes leer y aceptar el descargo de responsabilidad profesional arriba" if not st.session_state.get("acepto_descargo", False) else "Acepto los términos para continuar con la evaluación"
)

if st.button("🚀 COMENZAR EVALUACIÓN", disabled=not (acepto_terminos and st.session_state.get("acepto_descargo", False))):
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
        st.session_state.acepto_terminos = acepto_terminos
        # Transition to 'final' phase to show technical outputs
        set_flow_phase("final")
        st.success("✅ Datos registrados correctamente. ¡Continuemos con tu evaluación!")
    else:
        # Mostrar todos los errores de validación
        error_message = "⚠️ **Por favor corrige los siguientes errores:**\n\n" + "\n\n".join(validation_errors)
        st.error(error_message)

st.markdown('</div>', unsafe_allow_html=True)

# Botón de navegación inteligente
if st.session_state.datos_completos:
    status_icon, status_color, status_text = get_step_status_indicator(1)
    st.markdown(f'''
    <div style="text-align: right; margin: 1.5rem 0;">
        <span style="background: {status_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold; margin-right: 1rem;">
            {status_icon} Paso 1 {status_text}
        </span>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("➡️ Continuar al Paso 2", key="nav_to_step2", use_container_width=True):
            st.markdown('<script>expandNextExpander(0);</script>', unsafe_allow_html=True)
            st.rerun()

if not st.session_state.datos_completos:
    st.markdown("""
    <div class="content-card" style="margin-top:2rem; padding:3rem; background: #181A1B; color: #F5F5F5; border-left: 5px solid #F4C430;">
        <div style="text-align:center;">
            <h2 style="color: #F5C430; font-weight:900; margin:0;">
                🏋️ Bienvenido a MUPAI
            </h2>
            <p style="color: #F5F5F5;font-size:1.1rem;font-weight:600;margin-top:1.5rem;">
                <span style="font-size:1.15rem; font-weight:700;">¿Cómo funciona el cuestionario?</span>
            </p>
            <div style="text-align:left;display:inline-block;max-width:650px;">
                <ul style="list-style:none;padding:0;">
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">📝</span> <b>Paso 1:</b> Datos personales<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recopilamos tu nombre, edad, sexo y contacto para personalizar el análisis.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">⚖️</span> <b>Paso 2:</b> Composición corporal<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Medidas científicas de peso, estatura y % de grasa corporal usando métodos validados (DEXA, BIA).
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">💪</span> <b>Paso 3:</b> Experiencia y rendimiento funcional<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Indicas tu experiencia y tus mejores resultados en ejercicios clave.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🚶</span> <b>Paso 4:</b> Actividad física diaria<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Clasificamos tu nivel de actividad habitual para ajustar el cálculo energético.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🍽️</span> <b>Paso 5:</b> Efecto térmico de los alimentos (ETA)<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Calculamos el gasto energético extra por digestión, según tu composición corporal y evidencia científica.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🏋️</span> <b>Paso 6:</b> Entrenamiento de fuerza<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Ajustamos tu gasto según frecuencia y nivel de entrenamiento de resistencia.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">📈</span> <b>Resultado final:</b> Plan nutricional personalizado<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recibes tus métricas clave, diagnóstico y recomendaciones basadas en ciencia.
                        </span>
                    </li>
                </ul>
                <div style="margin-top:1.2em; font-size:1rem; color:#F4C430;">
                    <b>Finalidad:</b> Este cuestionario integra principios científicos y experiencia práctica para ofrecerte un diagnóstico preciso y recomendaciones útiles. <br>
                    <b>Tiempo estimado:</b> Menos de 5 minutos.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# VALIDACIÓN DATOS PERSONALES PARA CONTINUAR
datos_personales_completos = all([nombre, telefono, email_cliente]) and acepto_terminos and st.session_state.get("acepto_descargo", False)

if datos_personales_completos and st.session_state.datos_completos:
    # ========== CUESTIONARIO SUEÑO + ESTRÉS (INTEGRADO) ==========
    # Llamar al formulario de sueño y estrés ANTES de cualquier cálculo complejo
    # Los datos se capturan y se incluirán automáticamente en el email final
    resultado_suenyo_estres = formulario_suenyo_estres()
    
    # ========== CUESTIONARIO CICLO MENSTRUAL (SOLO PARA MUJERES) ==========
    # Llamar al formulario del ciclo menstrual después de datos personales
    # y antes de la composición corporal. Solo se muestra si sexo == "Mujer"
    # La información se captura y se incluirá en el reporte sin afectar cálculos
    ciclo_menstrual = formulario_ciclo_menstrual(sexo)
    
    # Progress bar general
    progress = st.progress(0)
    progress_text = st.empty()

    # BLOQUE 1: Datos antropométricos con diseño mejorado
    with st.expander("📊 **Paso 1: Composición Corporal y Antropometría**", expanded=True):
        st.markdown('<p style="color: #F4C430; font-size: 0.9rem; margin-bottom: 1rem;">✓ Completa estos datos para obtener tu análisis de composición corporal</p>', unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            # Ensure peso has a valid default
            peso_default = 70.0
            peso_value = st.session_state.get("peso", peso_default)
            if peso_value == '' or peso_value is None or peso_value == 0:
                peso_value = peso_default
            peso = st.number_input(
                "⚖️ Peso corporal (kg)",
                min_value=30.0,
                max_value=200.0,
                value=safe_float(peso_value, peso_default),
                step=0.1,
                key="peso",
                help="Peso en ayunas, sin ropa"
            )
        with col2:
            # Ensure estatura has a valid default
            estatura_default = 170.0
            estatura_value = st.session_state.get("estatura", estatura_default)
            if estatura_value == '' or estatura_value is None or estatura_value == 0:
                estatura_value = estatura_default
            estatura = st.number_input(
                "📏 Estatura (cm)",
                min_value=120.0,
                max_value=220.0,
                value=safe_float(estatura_value, estatura_default),
                step=0.1,
                key="estatura",
                help="Medida sin zapatos (puede incluir decimales, ej: 165.5)"
            )
        with col3:
            st.markdown('<div class="body-fat-method-selector">', unsafe_allow_html=True)
            metodo_grasa = st.selectbox(
                "📊 Método de medición de grasa",
                ["Omron HBF-516 (BIA)", "InBody 270 (BIA profesional)", "Bod Pod (Pletismografía)", "DEXA (Gold Standard)"],
                key="metodo_grasa",
                help="Selecciona el método utilizado"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Ensure grasa_corporal has a valid default
        grasa_default = 20.0
        grasa_value = st.session_state.get("grasa_corporal", grasa_default)
        if grasa_value == '' or grasa_value is None or grasa_value == 0:
            grasa_value = grasa_default
        grasa_corporal = st.number_input(
            f"💪 % de grasa corporal ({metodo_grasa.split('(')[0].strip()})",
            min_value=3.0,
            max_value=60.0,
            value=safe_float(grasa_value, grasa_default),
            step=0.1,
            key="grasa_corporal",
            help="Valor medido con el método seleccionado"
        )

        # Campo opcional - % Masa muscular (no afecta cálculos)
        masa_muscular_default = st.session_state.get("masa_muscular", 0.0)
        masa_muscular = st.number_input(
            "💪 % Masa muscular (medición Omron, opcional)",
            min_value=0.0,
            max_value=100.0,
            value=safe_float(masa_muscular_default, 0.0),
            step=0.1,
            key="masa_muscular",
            help="Introduce el % de masa muscular según tu báscula Omron. Se comparará con el valor estimado científico en el reporte. Si no lo conoces, déjalo en 0."
        )

        # Campo opcional - Grasa visceral (no afecta cálculos)
        grasa_visceral_default = st.session_state.get("grasa_visceral", 0)
        grasa_visceral_safe = safe_int(grasa_visceral_default, 0)
        grasa_visceral = st.number_input(
            "🫀 Grasa visceral (nivel, opcional)",
            min_value=1,
            max_value=59,
            value=grasa_visceral_safe if grasa_visceral_safe >= 1 else 1,
            step=1,
            key="grasa_visceral",
            help="La grasa visceral es la grasa que rodea los órganos internos. Valores saludables: 1-12. Valores altos (≥13) indican mayor riesgo de enfermedades metabólicas. Este dato se guarda y se incluye en el reporte, pero no afecta los cálculos."
        )

        # Campo opcional - Circunferencia de cintura (no afecta cálculos)
        circunferencia_cintura_default = st.session_state.get("circunferencia_cintura", 0.0)
        circunferencia_cintura_safe = safe_float(circunferencia_cintura_default, 0.0)
        circunferencia_cintura = st.number_input(
            "📏 Circunferencia de cintura (cm, opcional)",
            min_value=0.0,
            max_value=200.0,
            value=circunferencia_cintura_safe if circunferencia_cintura_safe > 0 else 0.0,
            step=0.1,
            key="circunferencia_cintura",
            help="Medida de la circunferencia de la cintura a la altura del ombligo. Este dato se incluye en el reporte junto con el ratio cintura-altura (WtHR). Valores saludables WtHR: <0.5 (hombres y mujeres)."
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # Note: session_state is automatically managed by widget keys, so no explicit assignments needed

    # Cálculos antropométricos
    sexo = st.session_state.sexo
    edad = st.session_state.edad
    metodo_grasa = st.session_state.metodo_grasa
    peso = st.session_state.peso
    estatura = st.session_state.estatura
    grasa_corporal = st.session_state.grasa_corporal
    masa_muscular = st.session_state.get("masa_muscular", 0.0)
    grasa_visceral = st.session_state.get("grasa_visceral", 0)

    grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
    mlg = calcular_mlg(peso, grasa_corregida)
    tmb = calcular_tmb_cunningham(mlg)

    # Validar estatura > 0
    if estatura <= 0:
        st.error("Error: La estatura debe ser mayor que cero para calcular FFMI.")
        ffmi = 0
    else:
        ffmi = calcular_ffmi(mlg, estatura)

    nivel_ffmi = clasificar_ffmi(ffmi, sexo)
    edad_metabolica = calcular_edad_metabolica(edad, grasa_corregida, sexo)

    # Display results to user (controlled by USER_VIEW flag)
    if USER_VIEW:
        # Mostrar corrección si aplica
        if metodo_grasa != "DEXA (Gold Standard)" and abs(grasa_corregida - grasa_corporal) > 0.1:
            st.info(
                f"📊 Valor corregido a equivalente DEXA: {grasa_corregida:.1f}% "
                f"(ajuste de {grasa_corregida - grasa_corporal:+.1f}%)"
            )

        # Resultados principales visuales
        st.markdown("### 📈 Resultados de tu composición corporal")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("% Grasa (DEXA)", f"{grasa_corregida:.1f}%", "Normal" if 10 <= grasa_corregida <= 25 else "Revisar")
        with col2:
            st.metric("MLG", f"{mlg:.1f} kg", "Masa Libre de Grasa")
        with col3:
            st.metric("TMB", f"{tmb:.0f} kcal", "Metabolismo Basal")
        with col4:
            try:
                edad_num = int(edad)
                diferencia_edad = edad_metabolica - edad_num
            except (ValueError, TypeError):
                edad_num = 25
                diferencia_edad = 0
            st.metric("Edad Metabólica", f"{edad_metabolica} años", f"{'+' if diferencia_edad > 0 else ''}{diferencia_edad} años")
        
        # Mostrar masa muscular y grasa visceral si están disponibles
        try:
            masa_muscular_val = safe_float(masa_muscular, 0.0)
            grasa_visceral_val = safe_int(grasa_visceral, 0)
            
            # Mostrar solo si hay al menos uno con valor
            if masa_muscular_val > 0 or grasa_visceral_val >= 1:
                col1, col2, col3, col4 = st.columns(4)
                if masa_muscular_val > 0:
                    with col1:
                        st.metric("Masa muscular (%)", f"{masa_muscular_val:.1f}%")
                if grasa_visceral_val >= 1:
                    with col2:
                        # Determinar estado basado en rangos saludables
                        if grasa_visceral_val <= 12:
                            estado = "Saludable"
                        elif grasa_visceral_val <= 15:
                            estado = "Elevado"
                        else:
                            estado = "Alto riesgo"
                        st.metric("Grasa visceral (nivel)", f"{grasa_visceral_val}", estado)
        except (ValueError, TypeError):
            pass  # No se muestra si hay error en el valor

    # Calcular FMI/BFMI (siempre - calculations run regardless of USER_VIEW)
    fmi = calcular_fmi(peso, grasa_corregida, estatura)
    
    # Determinar modo de interpretación FFMI (siempre - calculations run regardless of USER_VIEW)
    modo_ffmi = obtener_modo_interpretacion_ffmi(grasa_corregida, sexo)
    
    if USER_VIEW:
        # FFMI con visualización mejorada y explicación detallada
        st.markdown("### 💪 Índice de Masa Libre de Grasa (FFMI) y Adiposidad (FMI)")
        
        # Technical details: FFMI mode interpretation (controlled by SHOW_TECH_DETAILS flag)
        if SHOW_TECH_DETAILS:
            # Mostrar modo de interpretación con badge
            modo_colors = {
                "GREEN": ("success", "🟢", "Interpretación válida como muscularidad"),
                "AMBER": ("warning", "🟡", "Interpretación limitada por adiposidad"),
                "RED": ("danger", "🔴", "No aplicable clasificación atlética")
            }
            modo_color, modo_emoji, modo_desc = modo_colors.get(modo_ffmi, ("info", "⚪", ""))
        
            # Border colors for mode badges
            border_colors = {
                "GREEN": "#4CAF50",
                "AMBER": "#FF9800",
                "RED": "#F44336"
            }
            border_color = border_colors.get(modo_ffmi, "#4CAF50")
        
            st.markdown(f"""
            <div style="background-color: #f0f8ff; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {border_color};">
            <p style="margin: 0; font-size: 13px; color: #333;">
            <b>Modo de interpretación FFMI:</b> {modo_emoji} <span class="badge badge-{modo_color}">{modo_ffmi}</span> - {modo_desc}
            </p>
            </div>
            """, unsafe_allow_html=True)
        
            # Explicación del FFMI antes de mostrar el valor
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
            <p style="margin: 0; font-size: 14px; color: #333;">
            <b>¿Qué es el FFMI?</b><br>
            El Fat-Free Mass Index (FFMI) es un indicador científico que mide tu masa muscular 
            ajustada por altura. Similar al IMC, pero usando solo masa libre de grasa (músculos, 
            huesos, órganos) sin contar la grasa corporal. Este índice permite comparar el 
            desarrollo muscular entre personas de diferentes estaturas de forma justa.
            </p>
            <p style="margin: 10px 0 0 0; font-size: 13px; color: #555;">
            <b>Cálculo:</b> FFMI = (Masa Libre de Grasa / Altura²) + normalización a 1.80m<br>
            <b>Tu MLG:</b> {mlg:.1f} kg | <b>Tu Altura:</b> {estatura} cm → <b>Tu FFMI:</b> {ffmi:.2f}
            </p>
            </div>
            """.format(mlg=mlg, estatura=estatura, ffmi=ffmi), unsafe_allow_html=True)
    
        # Mostrar FFMI y FMI en columnas
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown("#### FFMI (Masa Libre de Grasa / Altura²)")
        
            # Always show basic classification, hide technical details
            if not SHOW_TECH_DETAILS:
                # Client-facing: Show only high-level classification
                st.markdown(f"""
                <h2 style="margin: 0;">Nivel: {nivel_ffmi}</h2>
                """, unsafe_allow_html=True)
            elif SHOW_TECH_DETAILS and modo_ffmi == "GREEN":
                # MODO GREEN: Mostrar clasificación completa
                color_nivel = {
                    "Bajo": "danger",
                    "Promedio": "warning",
                    "Bueno": "success",
                    "Avanzado": "info",
                    "Élite": "success"
                }.get(nivel_ffmi, "info")
                st.markdown(f"""
                <h2 style="margin: 0;">FFMI: {ffmi:.2f} 
                <span class="badge badge-{color_nivel}">{nivel_ffmi}</span></h2>
                """, unsafe_allow_html=True)
            
                if sexo == "Hombre":
                    ffmi_max = 25
                    rangos_ffmi = {"Bajo": 18, "Promedio": 20, "Bueno": 22, "Avanzado": 25}
                else:
                    ffmi_max = 21
                    rangos_ffmi = {"Bajo": 15, "Promedio": 17, "Bueno": 19, "Avanzado": 21}
            
                progreso_ffmi = min(ffmi / ffmi_max, 1.0)
                st.progress(progreso_ffmi)
                st.caption(f"Desarrollo muscular: {progreso_ffmi*100:.0f}% del potencial natural máximo")
            
                # Interpretación específica del nivel actual
                interpretaciones = {
                    "Hombre": {
                        "Bajo": "Indica desarrollo muscular insuficiente. Prioriza entrenamiento de fuerza y nutrición adecuada.",
                        "Promedio": "Desarrollo normal en población general. Con entrenamiento consistente puedes mejorar significativamente.",
                        "Bueno": "Buen desarrollo muscular alcanzable con 2-4 años de entrenamiento disciplinado. ¡Sigue así!",
                        "Avanzado": "Desarrollo muy avanzado. Estás cerca del límite natural. Optimiza detalles para máximo progreso.",
                        "Élite": "Desarrollo excepcional. Has alcanzado un nivel muy difícil de lograr naturalmente. ¡Excelente trabajo!"
                    },
                    "Mujer": {
                        "Bajo": "Indica desarrollo muscular insuficiente. El entrenamiento de fuerza te ayudará significativamente.",
                        "Promedio": "Desarrollo normal en población femenina. Hay mucho margen para mejorar con entrenamiento.",
                        "Bueno": "Buen desarrollo muscular. Refleja dedicación al entrenamiento de fuerza. ¡Continúa!",
                        "Avanzado": "Desarrollo muy avanzado para mujeres. Cercano al límite natural. Excelente dedicación.",
                        "Élite": "Desarrollo excepcional. Nivel muy difícil de alcanzar naturalmente. ¡Impresionante logro!"
                    }
                }
                st.info(f"📋 **Interpretación:** {interpretaciones[sexo][nivel_ffmi]}")
            
                # Mostrar rangos de referencia
                st.info(f"""
                **Referencia FFMI ({sexo}):**
                - Bajo: <{rangos_ffmi['Bajo']}
                - Promedio: {rangos_ffmi['Bajo']}-{rangos_ffmi['Promedio']}
                - Bueno: {rangos_ffmi['Promedio']}-{rangos_ffmi['Bueno']}
                - Avanzado: {rangos_ffmi['Bueno']}-{rangos_ffmi['Avanzado']}
                - Élite: >{rangos_ffmi['Avanzado']}
                """)
            
            elif SHOW_TECH_DETAILS and modo_ffmi == "AMBER":
                # MODO AMBER: Mostrar valor pero con interpretación limitada
                st.markdown(f"""
                <h2 style="margin: 0;">FFMI: {ffmi:.2f}</h2>
                <p style="color: #FF9800; font-weight: bold;">Interpretación limitada por adiposidad</p>
                """, unsafe_allow_html=True)
            
                st.warning("""
                ⚠️ **FFMI calculado; interpretación limitada**
            
                Tu porcentaje de grasa corporal está en una zona donde el FFMI comienza a 
                inflarse por componentes no musculares de la masa libre de grasa (agua corporal 
                adicional, masa estructural). Se reporta el valor numérico pero la clasificación 
                atlética puede no reflejar tu desarrollo muscular real.
            
                **Recomendación:** Enfócate en reducir grasa corporal para que el FFMI sea 
                un indicador más preciso de tu muscularidad.
                """)
            
            elif SHOW_TECH_DETAILS:  # RED mode
                # MODO RED: Mostrar valor con explicación clara de no aplicabilidad
                st.markdown(f"""
                <h2 style="margin: 0;">FFMI: {ffmi:.2f}</h2>
                <p style="color: #F44336; font-weight: bold;">Clasificación FFMI: No aplica</p>
                """, unsafe_allow_html=True)
            
                st.error("""
                🔴 **Clasificación atlética no aplicable**
            
                Con adiposidad muy alta, el FFMI puede elevarse significativamente por masa 
                libre de grasa no muscular (incluyendo agua corporal expandida, órganos y 
                tejido estructural) y deja de ser un proxy válido de muscularidad atlética.
            
                **Se reporta el valor numérico pero no se clasifica como indicador de desarrollo muscular.**
            
                Una vez que reduzcas tu porcentaje de grasa a niveles más saludables, el FFMI 
                será interpretable y útil para evaluar tu progreso muscular.
                """)
    
        with col2:
            st.markdown("#### FMI/BFMI (Masa Grasa / Altura²)")
        
            # Technical details: FMI classification (controlled by SHOW_TECH_DETAILS flag)
            if not SHOW_TECH_DETAILS:
                # Client-facing: Hide FMI technical details entirely
                pass
            elif SHOW_TECH_DETAILS:
                st.markdown(f"""
                <h2 style="margin: 0;">FMI: {fmi:.2f}</h2>
                """, unsafe_allow_html=True)
                # Clasificar FMI según sexo
                if sexo == "Hombre":
                    if fmi < 3:
                        fmi_cat = "Bajo"
                        fmi_color = "info"
                    elif fmi < 6:
                        fmi_cat = "Normal"
                        fmi_color = "success"
                    elif fmi < 9:
                        fmi_cat = "Elevado"
                        fmi_color = "warning"
                    else:
                        fmi_cat = "Muy elevado"
                        fmi_color = "danger"
                else:  # Mujer
                    if fmi < 5:
                        fmi_cat = "Bajo"
                        fmi_color = "info"
                    elif fmi < 9:
                        fmi_cat = "Normal"
                        fmi_color = "success"
                    elif fmi < 13:
                        fmi_cat = "Elevado"
                        fmi_color = "warning"
                    else:
                        fmi_cat = "Muy elevado"
                        fmi_color = "danger"
            
                st.markdown(f"""
                <span class="badge badge-{fmi_color}">{fmi_cat}</span>
                """, unsafe_allow_html=True)
            
                st.info(f"""
                **Referencia FMI ({sexo}):**
                {"- Bajo: <3" if sexo == "Hombre" else "- Bajo: <5"}
                {"- Normal: 3-6" if sexo == "Hombre" else "- Normal: 5-9"}
                {"- Elevado: 6-9" if sexo == "Hombre" else "- Elevado: 9-13"}
                {"- Muy elevado: >9" if sexo == "Hombre" else "- Muy elevado: >13"}
                """)
            
                st.info("""
                **¿Qué es el FMI?**
            
                El FMI (Fat Mass Index) complementa al FFMI al medir la adiposidad 
                ajustada por altura. Siempre se reporta para contextualizar la 
                composición corporal completa.
                """)
    
            # Technical details: Additional FFMI mode explanation (controlled by SHOW_TECH_DETAILS flag)
            if SHOW_TECH_DETAILS and modo_ffmi != "GREEN":
                st.info(f"""
                💡 **Nota sobre interpretación FFMI:**
            
                Los umbrales para mujeres son ~3 puntos más bajos que para hombres debido a diferencias biológicas:
                - Menos testosterona natural
                - Mayor % grasa esencial (necesaria para funciones reproductivas)
                - Diferente distribución muscular natural
            
                Tu clasificación está en modo **{modo_ffmi}** basado en tu porcentaje de grasa corporal actual ({grasa_corregida:.1f}%).
                """)

else:
    st.info("Por favor completa los datos personales para comenzar la evaluación.")
    # === INICIALIZACIÓN DE VARIABLES CRÍTICAS ===
# Inicializar variables críticas con valores por defecto seguros
if 'peso' not in locals():
    peso = 70.0
if 'estatura' not in locals():
    estatura = 170
if 'grasa_corporal' not in locals():
    grasa_corporal = 20.0
if 'sexo' not in locals():
    sexo = "Hombre"
if 'edad' not in locals():
    edad = 25
if 'metodo_grasa' not in locals():
    metodo_grasa = "Omron HBF-516 (BIA)"
if 'masa_muscular' not in locals():
    masa_muscular = st.session_state.get("masa_muscular", 0.0)
if 'grasa_visceral' not in locals():
    grasa_visceral = st.session_state.get("grasa_visceral", 0)
if 'grasa_corregida' not in locals():
    grasa_corregida = 20.0
if 'mlg' not in locals():
    mlg = 50.0
if 'tmb' not in locals():
    tmb = 1800.0
if 'ffmi' not in locals():
    ffmi = 18.0
if 'nivel_ffmi' not in locals():
    nivel_ffmi = "Bajo"
if 'edad_metabolica' not in locals():
    edad_metabolica = 25
if 'ingesta_calorica' not in locals():
    ingesta_calorica = 2000.0
if 'proteina_g' not in locals():
    proteina_g = 100.0
if 'grasa_g' not in locals():
    grasa_g = 60.0
if 'carbo_g' not in locals():
    carbo_g = 200.0
if 'grasa_kcal' not in locals():
    grasa_kcal = 540.0
if 'carbo_kcal' not in locals():
    carbo_kcal = 800.0
if 'fase' not in locals():
    fase = "Mantenimiento"
if 'plan_elegido' not in locals():
    plan_elegido = "Plan Tradicional"

# === ACTUALIZA VARIABLES CLAVE DESDE session_state ANTES DE CUALQUIER CÁLCULO CRÍTICO ===
# Esto fuerza que SIEMPRE se use el último dato capturado por el usuario

peso = st.session_state.get("peso", 0)
estatura = st.session_state.get("estatura", 0)
grasa_corporal = st.session_state.get("grasa_corporal", 0)
sexo = st.session_state.get("sexo", "Hombre")
edad = st.session_state.get("edad", 0)
metodo_grasa = st.session_state.get("metodo_grasa", "Omron HBF-516 (BIA)")

# Note: Session state is automatically managed by widget keys

# --- Recalcula variables críticas para PSMF ---
grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
mlg = calcular_mlg(peso, grasa_corregida)

# --- Cálculo PSMF ---
# PSMF calculations ALWAYS run to ensure backend processing and reporting
# UI display is controlled by MOSTRAR_PSMF_AL_USUARIO flag
psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg, estatura)

# Store PSMF results in session_state for downstream use (calculations, reporting, emails)
st.session_state.psmf_recs = psmf_recs
st.session_state.psmf_aplicable = psmf_recs.get("psmf_aplicable", False)

# UI Display: Only show if MOSTRAR_PSMF_AL_USUARIO is True
if psmf_recs.get("psmf_aplicable") and MOSTRAR_PSMF_AL_USUARIO:
    st.markdown('<div class="content-card card-psmf">', unsafe_allow_html=True)
    
    # High-level message for clients (always shown)
    if not SHOW_TECH_DETAILS:
        st.warning(f"""
        ⚡ **CANDIDATO PARA PROTOCOLO PSMF**
        Por tu composición corporal, podrías beneficiarte de una fase de pérdida rápida.
        
        ⚠️ **ADVERTENCIAS DE SEGURIDAD:**
        • Duración máxima: 6-8 semanas
        • Requiere supervisión médica/nutricional
        • Suplementación obligatoria: multivitamínico, omega-3, electrolitos
        
        *PSMF = Protein Sparing Modified Fast (ayuno modificado ahorrador de proteína)*
        """)
    else:
        # Technical details (only shown when SHOW_TECH_DETAILS = True)
        perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
        tier_psmf = psmf_recs.get('tier_psmf', 1)
        base_proteina_usada = psmf_recs.get('base_proteina_usada', 'Peso total')
        carb_cap = psmf_recs.get('carb_cap_aplicado_g', 50)
        st.warning(f"""
        ⚡ **CANDIDATO PARA PROTOCOLO PSMF ACTUALIZADO**
        Por tu % de grasa corporal ({grasa_corregida:.1f}%), podrías beneficiarte de una fase de pérdida rápida:
        
        🏷️ **Tier de adiposidad:** Tier {tier_psmf}
        🥩 **Proteína diaria:** {psmf_recs['proteina_g_dia']} g/día ({psmf_recs.get('factor_proteina_psmf', 1.6)}g/kg × {psmf_recs.get('base_proteina_kg', peso):.1f}kg {base_proteina_usada})
        🥑 **Grasas diarias:** {psmf_recs['grasa_g_dia']} g/día
        🌾 **Carbohidratos diarios:** {psmf_recs.get('carbs_g_dia', 0)} g/día (tope: {carb_cap}g)
        🔥 **Calorías diarias:** {psmf_recs['calorias_dia']:.0f} kcal/día
        📊 **Multiplicador:** {psmf_recs.get('multiplicador', 8.3)} (perfil: {psmf_recs.get('perfil_grasa', 'alto % grasa')})
        📈 **Pérdida semanal proyectada:** {perdida_min}-{perdida_max} kg/semana
        ⚠️ **Mínimo absoluto:** {psmf_recs['calorias_piso_dia']} kcal/día
        📋 **Criterio:** {psmf_recs['criterio']}
        
        ⚠️ **ADVERTENCIAS DE SEGURIDAD:**
        • Duración máxima: 6-8 semanas
        • Requiere supervisión médica/nutricional
        • Carbohidratos limitados según tier (solo de vegetales fibrosos)
        • Suplementación obligatoria: multivitamínico, omega-3, electrolitos
        
        *PSMF = Protein Sparing Modified Fast (ayuno modificado ahorrador de proteína)*
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
rango_grasa_ok = (4, 12) if sexo == "Hombre" else (10, 18)
fuera_rango = grasa_corregida < rango_grasa_ok[0] or grasa_corregida > rango_grasa_ok[1]
if fuera_rango:
    st.info(f"""
    ℹ️ **Nota sobre precisión**: Para máxima precisión en la estimación del FFMI, 
    el % de grasa ideal está entre {rango_grasa_ok[0]}-{rango_grasa_ok[1]}%. 
    Tu valor actual ({grasa_corregida:.1f}%) puede 
    {'subestimar' if grasa_corregida < rango_grasa_ok[0] else 'sobrestimar'} 
    ligeramente tu potencial muscular.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

progress = st.progress(0)
progress_text = st.empty()

# BLOQUE 2: Evaluación funcional mejorada (versión científica y capciosa)
step2_icon, step2_color, step2_status = get_step_status_indicator(2)
step2_title = f"💪 **Paso 2: Evaluación Funcional y Nivel de Entrenamiento** {step2_icon}"
with st.expander(step2_title, expanded=False):
    st.markdown(f'<p style="color: {step2_color}; font-size: 0.9rem; margin-bottom: 1rem; font-weight: bold;">Estado: {step2_status}</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #F4C430; font-size: 0.9rem; margin-bottom: 1rem;">✓ Evalúa tu capacidad funcional y experiencia de entrenamiento</p>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.markdown("### 📋 Experiencia en entrenamiento **(Requerido)**")
    st.markdown("*Este campo es obligatorio para continuar con la evaluación*")
    
    st.markdown("""
    **Responde las siguientes preguntas sobre tu historial de entrenamiento:**
    """)
    
    # Pregunta 1: Frecuencia real de entrenamiento
    st.markdown("#### 1️⃣ Frecuencia de entrenamiento")
    frecuencia = st.radio(
        "En los **últimos 6 meses**, ¿con qué frecuencia has entrenado de manera consistente?",
        [
            "Menos de 1 vez por semana o con pausas largas (más de 2 semanas sin entrenar)",
            "1-2 veces por semana de forma irregular",
            "2-3 veces por semana de forma consistente",
            "4 o más veces por semana de forma consistente"
        ],
        help="Sé honesto. La consistencia real es más importante que la intención.",
        key="frecuencia_entrenamiento"
    )
    
    # Pregunta 2: Tiempo total de experiencia
    st.markdown("#### 2️⃣ Tiempo de experiencia acumulada")
    tiempo_experiencia = st.radio(
        "¿Cuánto tiempo **acumulado** llevas entrenando de forma consistente en tu vida? (suma todos los períodos en los que entrenaste regularmente)",
        [
            "Menos de 6 meses",
            "6 meses a 1 año",
            "1 a 2 años",
            "Más de 2 años"
        ],
        help="Cuenta solo los períodos donde entrenaste al menos 2 veces por semana de forma regular.",
        key="tiempo_experiencia"
    )
    
    # Pregunta 3: Tipo de entrenamiento
    st.markdown("#### 3️⃣ Tipo de entrenamiento y progresión")
    tipo_entrenamiento = st.radio(
        "¿Qué describe mejor tu forma de entrenar actualmente?",
        [
            "Hago ejercicios variados sin llevar registro ni plan específico",
            "Sigo rutinas de internet o apps pero no registro mis cargas ni progresión",
            "Sigo un programa con progresión de cargas y llevo registro de mis entrenamientos",
            "Planeo mi entrenamiento considerando periodización, volumen, intensidad y ajusto según mi progreso"
        ],
        help="Selecciona la opción que refleje tu realidad actual, no tus aspiraciones.",
        key="tipo_entrenamiento"
    )
    
    # Guardar respuestas en session state
    if frecuencia and tiempo_experiencia and tipo_entrenamiento:
        st.session_state.experiencia_completa = True
        st.session_state.experiencia_respuestas = {
            'frecuencia': frecuencia,
            'tiempo': tiempo_experiencia,
            'tipo': tipo_entrenamiento
        }
        
        # Mostrar confirmación
        st.success("✅ Cuestionario de experiencia completado")
        experiencia = True  # Para mantener compatibilidad con el resto del código
    else:
        st.session_state.experiencia_completa = False
        experiencia = False

    # Allow all users to access functional exercises regardless of experience level
    if experiencia:
        st.markdown("### 🏆 Evaluación de rendimiento por categoría")
        st.info("💡 **Importante:** Debes completar las 5 categorías de ejercicios para poder enviar el cuestionario. Para cada categoría, selecciona el ejercicio donde hayas alcanzado tu mejor rendimiento y proporciona el máximo que hayas logrado manteniendo una técnica adecuada.")
        
        # Show progress of completed exercises
        ejercicios_previos = st.session_state.get("datos_ejercicios", {})
        if ejercicios_previos and len(ejercicios_previos) > 0:
            st.success(f"✅ Has completado {len(ejercicios_previos)} de 5 categorías de ejercicios")

        ejercicios_data = {}
        niveles_ejercicios = {}

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💪 Empuje", "🏋️ Tracción", "🦵 Pierna Empuje", "🦵 Pierna Tracción", "🧘 Core"])
    else:
        st.warning("⚠️ **Primero debes seleccionar tu nivel de experiencia en entrenamiento para acceder a la evaluación de ejercicios funcionales.**")
        ejercicios_data = {}
        niveles_ejercicios = {}

    if experiencia:
        with tab1:
            st.markdown("#### Empuje superior")
            col1, col2 = st.columns(2)
            with col1:
                empuje = st.selectbox(
                    "Elige tu mejor ejercicio de empuje:",
                    ["Flexiones", "Fondos"],
                    help="Selecciona el ejercicio donde tengas mejor rendimiento y técnica."
                )
            with col2:
                empuje_reps = st.number_input(
                    f"¿Cuántas repeticiones continuas realizas con buena forma en {empuje}?",
                    min_value=0, max_value=100, value=safe_int(st.session_state.get(f"{empuje}_reps", 10), 10),
                    help="Sin pausas, sin perder rango completo de movimiento."
                )
                ejercicios_data[empuje] = empuje_reps

        with tab2:
            st.markdown("#### Tracción superior")
            col1, col2 = st.columns(2)
            with col1:
                traccion = st.selectbox(
                    "Elige tu mejor ejercicio de tracción:",
                    ["Dominadas", "Remo invertido"],
                    help="Selecciona el ejercicio donde tengas mejor rendimiento y técnica."
                )
            with col2:
                traccion_reps = st.number_input(
                    f"¿Cuántas repeticiones continuas realizas con buena forma en {traccion}?",
                    min_value=0, max_value=50, value=safe_int(st.session_state.get(f"{traccion}_reps", 5), 5),
                    help="Sin balanceo ni uso de impulso; técnica estricta."
                )
                ejercicios_data[traccion] = traccion_reps

        with tab3:
            st.markdown("#### Tren inferior empuje")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Ejercicio:**")
                st.info("Sentadilla búlgara unilateral")
            with col2:
                pierna_empuje_reps = st.number_input(
                    "¿Cuántas repeticiones continuas realizas con buena forma en Sentadilla búlgara unilateral?",
                    min_value=0, max_value=50, value=safe_int(st.session_state.get("Sentadilla búlgara unilateral_reps", 10), 10),
                    help="Repeticiones con técnica controlada por cada pierna.",
                    key="sentadilla_bulgara_reps"
                )
                ejercicios_data["Sentadilla búlgara unilateral"] = pierna_empuje_reps

        with tab4:
            st.markdown("#### Tren inferior tracción")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Ejercicio:**")
                st.info("Puente de glúteo unilateral")
            with col2:
                pierna_traccion_reps = st.number_input(
                    "¿Cuántas repeticiones continuas realizas con buena forma en Puente de glúteo unilateral?",
                    min_value=0, max_value=50, value=safe_int(st.session_state.get("Puente de glúteo unilateral_reps", 15), 15),
                    help="Repeticiones con técnica controlada por cada pierna.",
                    key="puente_gluteo_reps"
                )
                ejercicios_data["Puente de glúteo unilateral"] = pierna_traccion_reps

        with tab5:
            st.markdown("#### Core y estabilidad")
            st.markdown("**Ejercicio:**")
            st.info("Plancha frontal")
            
            core_tiempo = st.number_input(
                "¿Cuál es el máximo tiempo (segundos) que mantienes la posición de plancha con técnica correcta?",
                min_value=0, max_value=600, value=safe_int(st.session_state.get("plancha_tiempo", 60), 60),
                help="Mantén la posición sin perder alineación corporal: cuerpo recto desde cabeza hasta talones, sin elevar cadera ni dejarla caer."
            )
            ejercicios_data["Plancha"] = core_tiempo

        # Evaluar niveles según referencias (always run calculations)
        if USER_VIEW:
            st.markdown("### 📊 Tu nivel en cada ejercicio")
            cols = st.columns(5)  # Changed from 4 to 5 to accommodate 5 exercises
        else:
            cols = None
        
        for idx, (ejercicio, valor) in enumerate(ejercicios_data.items()):
            if ejercicio in referencias_funcionales[sexo]:
                ref = referencias_funcionales[sexo][ejercicio]
                nivel_ej = "Bajo"  # Por defecto

                if ref["tipo"] == "reps":
                    for nombre_nivel, umbral in ref["niveles"]:
                        if valor >= umbral:
                            nivel_ej = nombre_nivel
                        else:
                            break
                elif ref["tipo"] == "tiempo":
                    for nombre_nivel, umbral in ref["niveles"]:
                        if valor >= umbral:
                            nivel_ej = nombre_nivel
                        else:
                            break
                elif ref["tipo"] == "reps_peso" and isinstance(valor, tuple):
                    reps, peso = valor
                    # Recorrer niveles de mayor a menor para asignar el nivel más alto posible
                    for nombre_nivel, (umbral_reps, umbral_peso) in reversed(ref["niveles"]):
                        if reps >= umbral_reps and peso >= umbral_peso:
                            nivel_ej = nombre_nivel
                            break

                niveles_ejercicios[ejercicio] = nivel_ej
                st.session_state.niveles_ejercicios[ejercicio] = nivel_ej

                # Display results to user (controlled by USER_VIEW flag)
                if USER_VIEW:
                    with cols[idx % 5]:  # Changed from 4 to 5
                        # Mostrar con badge de color
                        color_badge = {
                            "Bajo": "danger",
                            "Promedio": "warning",
                            "Bueno": "success",
                            "Avanzado": "info"
                        }.get(nivel_ej, "info")

                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #F4C430; border-radius: 10px; border: 2px solid #DAA520;">
                            <strong style="color: #1E1E1E; font-weight: bold; font-size: 1.1rem;">{ejercicio}</strong><br>
                            <span class="badge badge-{color_badge}" style="font-size: 1rem; background: #1E1E1E; color: #F4C430; font-weight: bold; margin: 0.5rem 0;">{nivel_ej}</span><br>
                            <small style="color: #1E1E1E; font-weight: bold;">{valor if not isinstance(valor, tuple) else f'{valor[0]}x{valor[1]}kg'}</small>
                        </div>
                        """, unsafe_allow_html=True)

# Guardar datos
st.session_state.datos_ejercicios = ejercicios_data

# Initialize variables with safe defaults
if 'nivel_ffmi' not in locals() or nivel_ffmi is None:
    nivel_ffmi = "Bajo"  # Valor por defecto válido

if 'experiencia' not in locals() or experiencia is None:
    experiencia = "A) He entrenado de forma irregular"  # Valor por defecto

if 'niveles_ejercicios' not in locals() or niveles_ejercicios is None:
    niveles_ejercicios = {}  # Diccionario vacío por defecto

# ==================== CÁLCULO DEL NIVEL GLOBAL DE ENTRENAMIENTO ====================
# Calcular puntuaciones individuales de cada componente

# 1. FFMI (Desarrollo Muscular): 1-5 puntos basado en masa muscular ajustada
puntos_ffmi = {"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4, "Élite": 5}.get(nivel_ffmi, 1)

# 2. Experiencia: 1-4 puntos basado en historial de entrenamiento
# Calcular puntos de experiencia basados en las nuevas preguntas específicas
if st.session_state.get('experiencia_completa', False):
    respuestas = st.session_state.get('experiencia_respuestas', {})
    
    # Frecuencia (0-1.5 puntos)
    frecuencia_puntos = {
        "Menos de 1 vez por semana o con pausas largas (más de 2 semanas sin entrenar)": 0.25,
        "1-2 veces por semana de forma irregular": 0.5,
        "2-3 veces por semana de forma consistente": 1.0,
        "4 o más veces por semana de forma consistente": 1.5
    }.get(respuestas.get('frecuencia', ''), 0.25)
    
    # Tiempo de experiencia (0-1.5 puntos)
    tiempo_puntos = {
        "Menos de 6 meses": 0.25,
        "6 meses a 1 año": 0.5,
        "1 a 2 años": 1.0,
        "Más de 2 años": 1.5
    }.get(respuestas.get('tiempo', ''), 0.25)
    
    # Tipo de entrenamiento (0-1 punto)
    tipo_puntos = {
        "Hago ejercicios variados sin llevar registro ni plan específico": 0.25,
        "Sigo rutinas de internet o apps pero no registro mis cargas ni progresión": 0.5,
        "Sigo un programa con progresión de cargas y llevo registro de mis entrenamientos": 0.75,
        "Planeo mi entrenamiento considerando periodización, volumen, intensidad y ajusto según mi progreso": 1.0
    }.get(respuestas.get('tipo', ''), 0.25)
    
    # Total: 1-4 puntos (similar al sistema anterior)
    puntos_exp = frecuencia_puntos + tiempo_puntos + tipo_puntos
    
    # Guardar para compatibilidad con validación
    st.session_state.experiencia_seleccion = f"Nuevo sistema: {puntos_exp:.2f} puntos"
else:
    # Sistema antiguo para compatibilidad (deprecated)
    experiencia_valor = st.session_state.get("experiencia_seleccion", "") or experiencia
    puntos_exp = {"A)": 1, "B)": 2, "C)": 3, "D)": 4}.get(experiencia_valor[:2] if experiencia_valor and len(experiencia_valor) >= 2 else "", 1)

# 3. Rendimiento Funcional: 1-4 puntos promedio de los 5 ejercicios funcionales
puntos_por_nivel = {"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4}
puntos_funcional = sum([puntos_por_nivel.get(n, 1) for n in niveles_ejercicios.values()]) / len(niveles_ejercicios) if niveles_ejercicios else 1

# Determinar el modo de interpretación FFMI para ajustar ponderación
modo_ffmi = obtener_modo_interpretacion_ffmi(grasa_corregida, sexo)

# Mantener compatibilidad con lógica existente
en_rango_saludable = esta_en_rango_saludable(grasa_corregida, sexo)

# ==================== PONDERACIÓN ADAPTATIVA MEJORADA ====================
# La ponderación se ajusta según el modo de interpretación FFMI (GREEN/AMBER/RED)
# que refleja la confiabilidad del FFMI como indicador de muscularidad.
#
# FUNDAMENTO CIENTÍFICO:
# - GREEN: El FFMI es confiable, la MLG es principalmente músculo esquelético
# - AMBER: El FFMI comienza a inflarse por componentes no musculares
# - RED: El FFMI pierde validez, la MLG incluye mucha agua/órganos/estructura
# - La capacidad funcional es siempre un indicador objetivo del nivel de entrenamiento
# - La experiencia proporciona contexto sobre la madurez del entrenamiento

if modo_ffmi == "GREEN":
    # MODO GREEN: Ponderación científica optimizada
    # - FFMI: 30% - Reducido para minimizar ventaja genética (Kouri et al. 1995)
    # - Funcional: 55% - Maximizado como indicador más objetivo (Helms 2014: correlación 0.85 con training age)
    # - Experiencia: 15% - Reducido por sesgo de autoreporte (Peterson et al. 2011)
    peso_ffmi = 0.30
    peso_funcional = 0.55
    peso_experiencia = 0.15
    criterio_ponderacion = "Modo GREEN - Ponderación científica optimizada"
elif modo_ffmi == "AMBER":
    # MODO AMBER: FFMI con validez reducida
    # - FFMI: 10% - Señal mínima de masa muscular vs sedentario, pero inflado por MLG no muscular
    # - Funcional: 65% - Alto como indicador objetivo (Schoenfeld 2010)
    # - Experiencia: 25% - Compensación moderada por FFMI poco confiable
    peso_ffmi = 0.10
    peso_funcional = 0.65
    peso_experiencia = 0.25
    criterio_ponderacion = "Modo AMBER - FFMI validez reducida por adiposidad moderada"
else:  # RED
    # MODO RED: FFMI excluido completamente
    # - FFMI: 0% - Inválido como indicador de muscularidad con adiposidad muy alta
    # - Funcional: 50% - Reducido porque exceso de peso afecta ejercicios de peso corporal
    # - Experiencia: 50% - Maximizado como único indicador restante confiable (Rønnestad 2007)
    peso_ffmi = 0.0
    peso_funcional = 0.50
    peso_experiencia = 0.50
    criterio_ponderacion = "Modo RED - FFMI excluido, ponderación experiencia-funcional equilibrada"

# Calcular puntaje total normalizado (0.0 a 1.0)
puntaje_total = (puntos_ffmi / 5 * peso_ffmi) + (puntos_funcional / 4 * peso_funcional) + (puntos_exp / 4 * peso_experiencia)

# Almacenar en session_state para uso posterior
st.session_state.puntos_ffmi = puntos_ffmi
st.session_state.puntos_funcional = puntos_funcional
st.session_state.puntos_exp = puntos_exp
st.session_state.puntaje_total = puntaje_total
st.session_state.en_rango_saludable = en_rango_saludable
st.session_state.criterio_ponderacion = criterio_ponderacion

if puntaje_total < 0.40:
    nivel_entrenamiento = "principiante"
elif puntaje_total < 0.60:
    nivel_entrenamiento = "intermedio"
elif puntaje_total < 0.78:
    nivel_entrenamiento = "avanzado"
else:
    nivel_entrenamiento = "élite"

# Store in session_state for consistent access
st.session_state.nivel_entrenamiento = nivel_entrenamiento

# Validar si todos los ejercicios funcionales y experiencia están completos
ejercicios_funcionales_completos = len(ejercicios_data) >= 5  # Debe tener los 5 ejercicios
experiencia_completa = experiencia  # Allow all experience levels

# === MOSTRAR RESUMEN GLOBAL TEMPRANO (ADICIONAL) ===
# Mostrar resumen global después de los badges de ejercicios si hay datos suficientes
if ejercicios_funcionales_completos and experiencia_completa and USER_VIEW:
    st.markdown("### 🎯 Tu Nivel Global de Entrenamiento")
    st.markdown("*Análisis integral basado en desarrollo muscular, rendimiento funcional y experiencia*")
    
    col1_global, col2_global, col3_global, col4_global = st.columns(4)
    
    with col1_global:
        st.metric("Desarrollo Muscular", f"{puntos_ffmi}/5", f"FFMI: {nivel_ffmi}")

    with col2_global:
        st.metric("Rendimiento", f"{puntos_funcional:.1f}/4", "Capacidad funcional")

    with col3_global:
        st.metric("Experiencia", f"{puntos_exp}/4", experiencia[3:20] + "...")

    with col4_global:
        color_nivel_entrenamiento = {
            "principiante": "warning",
            "intermedio": "info",
            "avanzado": "success",
            "élite": "success"
        }.get(nivel_entrenamiento, "info")

        st.markdown(f"""
        <div style="text-align: center;">
            <h3 style="margin: 0;">Nivel Global</h3>
            <span class="badge badge-{color_nivel_entrenamiento}" style="font-size: 1.2rem;">
                {nivel_entrenamiento.upper()}
            </span><br>
            <small>Score: {puntaje_total:.2f}/1.0</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.success(f"""
    ✅ **Análisis completado:** Tu nivel global de entrenamiento es **{nivel_entrenamiento.upper()}**
    
    Este nivel se usará para personalizar todos los cálculos energéticos y nutricionales posteriores.
    """)
    
    # Mostrar información sobre la ponderación aplicada según modo FFMI
    if modo_ffmi == "GREEN":
        st.info(f"""
        ✅ **PONDERACIÓN CIENTÍFICA OPTIMIZADA (Modo GREEN)**
        
        Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) permite una interpretación válida del FFMI como muscularidad.
        
        **Ponderación aplicada (basada en evidencia científica):**
        - 🏋️ FFMI (desarrollo muscular): **{peso_ffmi*100:.0f}%** (reducido para minimizar ventaja genética)
        - 💪 Rendimiento funcional: **{peso_funcional*100:.0f}%** (maximizado como indicador más objetivo)
        - 📚 Experiencia: **{peso_experiencia*100:.0f}%** (ajustado por posible sesgo de autoreporte)
        
        📚 **Base científica:** Helms et al. (2014) demostró que el rendimiento funcional correlaciona 0.85 
        con training age real, mientras que el FFMI tiene componente genético significativo (Kouri 1995).
        """)
    elif modo_ffmi == "AMBER":
        st.warning(f"""
        ⚠️ **PONDERACIÓN AJUSTADA (Modo AMBER)**
        
        Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) está en zona donde el FFMI tiene 
        validez reducida como indicador de muscularidad (incluye agua, órganos, estructura).
        
        **Ponderación aplicada (ajustada científicamente):**
        - 🏋️ FFMI (desarrollo muscular): **{peso_ffmi*100:.0f}%** (señal mínima, validez reducida)
        - 💪 Rendimiento funcional: **{peso_funcional*100:.0f}%** (maximizado como indicador objetivo)
        - 📚 Experiencia: **{peso_experiencia*100:.0f}%** (aumentado para compensar)
        
        **Razón científica:** En esta zona de adiposidad, la MLG (masa libre de grasa) incluye proporcionalmente 
        más agua corporal y menos músculo esquelético. El rendimiento funcional es indicador más objetivo (Schoenfeld 2010).
        """)
    else:  # RED
        st.error(f"""
        🔴 **PONDERACIÓN AJUSTADA (Modo RED)**
        
        Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) está en rango donde el FFMI no es 
        válido como indicador de muscularidad atlética.
        
        **Ponderación aplicada (optimizada para alta adiposidad):**
        - 🏋️ FFMI (desarrollo muscular): **{peso_ffmi*100:.0f}%** (excluido por falta de validez)
        - 💪 Rendimiento funcional: **{peso_funcional*100:.0f}%** (ajustado porque el peso afecta ejercicios)
        - 📚 Experiencia: **{peso_experiencia*100:.0f}%** (maximizado como indicador principal)
        
        **Razón científica:** Con adiposidad muy alta, el FFMI pierde validez porque la MLG incluye 
        proporcionalmente mucha agua, órganos y estructura, no músculo. El nivel se evalúa equilibrando 
        experiencia (training age) y rendimiento funcional ajustado por peso corporal (Rønnestad 2007).
        """)

if ejercicios_funcionales_completos and experiencia_completa:
    # Mostrar el bloque visual del nivel global solo si todo está completo
    pass  # El bloque ya se mostró arriba
else:
    # Mostrar mensaje informativo si faltan datos
    faltantes = []
    if not ejercicios_funcionales_completos:
        faltantes.append("ejercicios funcionales")
    if not experiencia_completa:
        faltantes.append("pregunta de experiencia")
    
    st.info(f"""
    ℹ️ **Para ver tu análisis integral de nivel, completa:**
    
    {'• Los ' + faltantes[0] if len(faltantes) > 0 else ''}
    {'• La ' + faltantes[1] if len(faltantes) > 1 else ''}
    
    Una vez completados todos los datos, se mostrará tu ponderación de FFMI, rendimiento funcional y experiencia.
    """)
    # === Potencial genético ===
# Initialize variables with safe defaults
if 'ffmi' not in locals():
    ffmi = 0
if 'ffmi_genetico_max' not in locals():
    ffmi_genetico_max = 22 if sexo == "Hombre" else 19
if 'porc_potencial' not in locals():
    porc_potencial = 0

# Mostrar potencial genético solo en modo GREEN
# En modo AMBER se degrada, en modo RED se oculta completamente
if 'ffmi' in locals() and 'nivel_entrenamiento' in locals() and ffmi > 0 and 'modo_ffmi' in locals():
    if sexo == "Hombre":
        ffmi_genetico_max = {
            "principiante": 22, "intermedio": 23.5,
            "avanzado": 24.5, "élite": 25
        }.get(nivel_entrenamiento, 22)
    else:
        ffmi_genetico_max = {
            "principiante": 19, "intermedio": 20,
            "avanzado": 20.5, "élite": 21
        }.get(nivel_entrenamiento, 19)

    porc_potencial = min((ffmi / ffmi_genetico_max) * 100, 100) if ffmi_genetico_max > 0 else 0

    if modo_ffmi == "GREEN":
        # MODO GREEN: Mostrar análisis completo de potencial
        st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
        st.success(f"""
        📈 **Análisis de tu potencial muscular**

        Has desarrollado aproximadamente el **{porc_potencial:.0f}%** de tu potencial muscular natural.

        - FFMI actual: {ffmi:.2f}
        - FFMI máximo estimado: {ffmi_genetico_max:.1f}
        - Margen de crecimiento: {max(0, ffmi_genetico_max - ffmi):.1f} puntos
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    elif modo_ffmi == "AMBER":
        # MODO AMBER: Mostrar con advertencia orientativa
        st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
        st.info(f"""
        📈 **Análisis de tu potencial muscular (orientativo)**

        ⚠️ Nota: Debido a tu nivel de adiposidad actual, estos valores son orientativos.

        - FFMI actual: {ffmi:.2f}
        - FFMI máximo estimado: {ffmi_genetico_max:.1f} (orientativo)
        - Potencial estimado: {porc_potencial:.0f}% (orientativo)
        
        Reduce tu % de grasa corporal para obtener una estimación más precisa de tu potencial muscular.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    else:  # RED
        # MODO RED: No mostrar potencial genético, ya que FFMI no es válido
        st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
        st.info("""
        📈 **Análisis de potencial muscular**

        ℹ️ El análisis de potencial muscular basado en FFMI no está disponible debido a que tu nivel 
        de adiposidad actual hace que el FFMI no sea un indicador válido de muscularidad.

        **Recomendación:** Enfócate primero en reducir tu porcentaje de grasa corporal a niveles 
        más saludables. Una vez logrado esto, podrás acceder a un análisis preciso de tu potencial 
        muscular y margen de crecimiento.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Completa primero todos los datos anteriores para ver tu potencial genético.")

# BLOQUE 3: Actividad física diaria
step3_icon, step3_color, step3_status = get_step_status_indicator(3)
step3_title = f"🚶 **Paso 3: Nivel de Actividad Física Diaria** {step3_icon}"
with st.expander(step3_title, expanded=False):
    st.markdown(f'<p style="color: {step3_color}; font-size: 0.9rem; margin-bottom: 1rem; font-weight: bold;">Estado: {step3_status}</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #F4C430; font-size: 0.9rem; margin-bottom: 1rem;">✓ Indica tu nivel de actividad física en el día a día</p>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Evalúa tu actividad física fuera del ejercicio planificado")

    # Opciones para el usuario (debe coincidir el orden con 'niveles')
    opciones_radio = [
        "Sedentario (trabajo de oficina, <5,000 pasos/día)",
        "Moderadamente-activo (trabajo mixto, 5,000-10,000 pasos/día)",
        "Activo (trabajo físico, 10,000-12,500 pasos/día)",
        "Muy-activo (trabajo muy físico, >12,500 pasos/día)"
    ]
    niveles = ["Sedentario", "Moderadamente-activo", "Activo", "Muy-activo"]
    niveles_ui = ["🪑 Sedentario", "🚶 Moderadamente-activo", "🏃 Activo", "💪 Muy-activo"]

    nivel_actividad = st.radio(
        "Selecciona el nivel que mejor te describe:",
        opciones_radio,
        help="No incluyas el ejercicio planificado, solo tu actividad diaria habitual"
    )

    # Extraer el texto base del nivel seleccionado (antes del paréntesis)
    nivel_actividad_text = nivel_actividad.split('(')[0].strip()

    # Garantiza coincidencia usando el índice (más robusto si cambias el orden)
    try:
        nivel_idx = niveles.index(nivel_actividad_text)
    except ValueError:
        nivel_idx = 0  # Default: Sedentario

    # Visualización gráfica del nivel seleccionado
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
                         background: #f8f9fa; border-radius: 10px; opacity: 0.5; color: #222;">
                        {niv}
                    </div>
                """, unsafe_allow_html=True)

    # Factores de actividad según nivel seleccionado
    geaf = obtener_geaf(nivel_actividad_text)
    st.session_state.nivel_actividad = nivel_actividad_text
    st.session_state.geaf = geaf

    # Technical details: Display GEAF factor details (controlled by SHOW_TECH_DETAILS flag)
    if SHOW_TECH_DETAILS:
        # Mensaje resumen
        st.success(
            f"✅ **Tu nivel de actividad física diaria: {nivel_actividad_text}**\n\n"
            f"- Factor GEAF: **{geaf}**\n"
            f"- Esto multiplicará tu gasto energético basal en un {(geaf-1)*100:.0f}%"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ===== ETA CALCULATION (ALWAYS RUNS) =====
# ETA calculations ALWAYS run regardless of UI visibility flag
# This ensures values are available for downstream calorie calculations, backend processing, and reporting
# UI display is controlled by MOSTRAR_ETA_AL_USUARIO flag
#
# ETA (Thermal Effect of Food) Logic:
# - Leaner individuals have higher ETA due to more metabolically active muscle tissue
# - Higher ETA means more calories burned through food digestion and processing
# 
# ETA Ranges:
# Men:   ≤10% BF → 1.15 (High),  11-20% BF → 1.12 (Medium),  >20% BF → 1.10 (Standard)
# Women: ≤20% BF → 1.15 (High),  21-30% BF → 1.12 (Medium),  >30% BF → 1.10 (Standard)
#
# These factors multiply TMB × GEAF to get total daily energy expenditure (TDEE)
if grasa_corregida <= 10 and sexo == "Hombre":
    eta = 1.15
    eta_desc = "ETA alto (muy magro, ≤10% grasa)"
    eta_color = "success"
elif grasa_corregida <= 20 and sexo == "Mujer":
    eta = 1.15
    eta_desc = "ETA alto (muy magra, ≤20% grasa)"
    eta_color = "success"
elif grasa_corregida <= 20 and sexo == "Hombre":
    eta = 1.12
    eta_desc = "ETA medio (magro, 11-20% grasa)"
    eta_color = "info"
elif grasa_corregida <= 30 and sexo == "Mujer":
    eta = 1.12
    eta_desc = "ETA medio (normal, 21-30% grasa)"
    eta_color = "info"
else:
    eta = 1.10
    eta_desc = f"ETA estándar (>{20 if sexo == 'Hombre' else 30}% grasa)"
    eta_color = "warning"

# Store ETA results in session_state for downstream use (calculations, reporting, emails)
st.session_state.eta = eta
st.session_state.eta_desc = eta_desc
st.session_state.eta_color = eta_color

# UI Display: Only show ETA expander if MOSTRAR_ETA_AL_USUARIO is True
if MOSTRAR_ETA_AL_USUARIO:
    # BLOQUE 4: ETA (Efecto Térmico de los Alimentos)
    with st.expander("🍽️ **Paso 4: Efecto Térmico de los Alimentos (ETA)**", expanded=True):
        progress.progress(70)
        progress_text.text("Paso 4 de 5: Cálculo del efecto térmico")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        # Technical details: Display ETA calculation details (controlled by SHOW_TECH_DETAILS flag)
        if SHOW_TECH_DETAILS:
            st.markdown("### 🔥 Determinación automática del ETA")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                <div class="content-card" style="text-align: center;">
                    <h2 style="margin: 0;">ETA: {eta}</h2>
                    <span class="badge badge-{eta_color}">{eta_desc}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.info(f"""
                **¿Qué es el ETA?**

                Es la energía que tu cuerpo gasta digiriendo y procesando alimentos.

                Aumenta tu gasto total en un {(eta-1)*100:.0f}%
                """)

        st.markdown('</div>', unsafe_allow_html=True)
else:
    # BLOQUE 4: Placeholder when ETA details are hidden from users
    with st.expander("📊 **Paso 4: Cálculo Automático de Factores Metabólicos**", expanded=False):
        progress.progress(70)
        progress_text.text("Paso 4 de 5: Procesamiento automático")
        
        st.info("""
        ℹ️ **Este paso se calcula automáticamente en función de los datos que has proporcionado.**
        
        Nuestro sistema procesa tu información de composición corporal y nivel de actividad para 
        ajustar de manera precisa tus requerimientos energéticos totales.
        """)

# BLOQUE 5: Entrenamiento de fuerza
step5_icon, step5_color, step5_status = get_step_status_indicator(5)
step5_title = f"🏋️ **Paso 5: Gasto Energético del Ejercicio (GEE)** {step5_icon}"
with st.expander(step5_title, expanded=False):
    st.markdown(f'<p style="color: {step5_color}; font-size: 0.9rem; margin-bottom: 1rem; font-weight: bold;">Estado: {step5_status}</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #F4C430; font-size: 0.9rem; margin-bottom: 1rem;">✓ Proporciona información sobre tu rutina de entrenamiento</p>', unsafe_allow_html=True)
    progress.progress(80)
    progress_text.text("Paso 5 de 5: Cálculo del gasto por ejercicio")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 💪 Frecuencia de entrenamiento de fuerza")

    dias_fuerza = st.slider(
        "¿Cuántos días por semana entrenas con pesas/resistencia?",
        min_value=0, max_value=7, value=3,
        help="Solo cuenta entrenamientos de fuerza, no cardio"
    )
    st.session_state.dias_fuerza = dias_fuerza

    # Cálculo del GEE según nivel global de entrenamiento
    if 'nivel_entrenamiento' in locals() and nivel_entrenamiento:
        if nivel_entrenamiento == "principiante":
            kcal_sesion = 300
            nivel_gee = "300 kcal/sesión"
            gee_color = "warning"
        elif nivel_entrenamiento == "intermedio":
            kcal_sesion = 350
            nivel_gee = "350 kcal/sesión"
            gee_color = "info"
        elif nivel_entrenamiento == "avanzado":
            kcal_sesion = 400
            nivel_gee = "400 kcal/sesión"
            gee_color = "info"
        else:  # élite
            kcal_sesion = 500
            nivel_gee = "500 kcal/sesión"
            gee_color = "success"
    else:
        # Fallback si no hay nivel_entrenamiento calculado
        kcal_sesion = 300
        nivel_gee = "300 kcal/sesión"
        gee_color = "warning"

    gee_semanal = dias_fuerza * kcal_sesion
    gee_prom_dia = gee_semanal / 7

    st.session_state.kcal_sesion = kcal_sesion
    st.session_state.gee_semanal = gee_semanal
    st.session_state.gee_prom_dia = gee_prom_dia

    # Display metrics conditionally based on SHOW_TECH_DETAILS flag
    if SHOW_TECH_DETAILS:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Días/semana", f"{dias_fuerza} días", "Sin entrenar" if dias_fuerza == 0 else "Activo")
        with col2:
            current_level = nivel_entrenamiento.capitalize() if 'nivel_entrenamiento' in locals() and nivel_entrenamiento else "Sin calcular"
            st.metric("Gasto/sesión", f"{kcal_sesion} kcal", f"Nivel {current_level}")
        with col3:
            st.metric("Promedio diario", f"{gee_prom_dia:.0f} kcal/día", f"Total: {gee_semanal} kcal/sem")

        st.markdown(f"""
        <div class="content-card" style="background: #D6EAF8; color: #1E1E1E; border: 2px solid #3498DB; padding: 1.5rem;">
            💡 <strong style="color: #1E1E1E; font-weight: bold;">Cálculo personalizado:</strong> Tu gasto por sesión ({nivel_gee}) 
            se basa en tu <strong>nivel global de entrenamiento</strong> ({current_level}), que combina desarrollo muscular, 
            rendimiento funcional y experiencia. Esto proporciona una estimación más precisa de tu gasto energético real.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Client-friendly message without technical details
        st.markdown("""
        <div class="content-card" style="background: #D6EAF8; color: #1E1E1E; border: 2px solid #3498DB; padding: 1.5rem;">
            💡 <strong style="color: #1E1E1E; font-weight: bold;">Cálculo personalizado:</strong> En base a tu nivel global de entrenamiento – que combina desarrollo muscular, rendimiento funcional y experiencia – se han realizado los cálculos personalizados.
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # BLOQUE 6: Cálculo final con comparativa PSMF
# Display final nutritional plan to user (controlled by USER_VIEW flag)
# Note: All calculations always run; only display is conditional
if USER_VIEW:
    with st.expander("📈 **RESULTADO FINAL: Tu Plan Nutricional Personalizado**", expanded=True):
        progress.progress(100)
        progress_text.text("Paso final: Calculando tu plan nutricional personalizado")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        # Determinar si el usuario está en el rango óptimo para selección interactiva
        en_rango_optimo = False
        if sexo == "Hombre" and 10 <= grasa_corregida <= 18:
            en_rango_optimo = True
        elif sexo == "Mujer" and 16 <= grasa_corregida <= 23:
            en_rango_optimo = True
        
        # Lógica interactiva para usuarios en rango óptimo
        if en_rango_optimo:
            st.markdown("### 🎯 Selección de objetivo nutricional")
            st.info(f"""
            🎉 **¡Excelente!** Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) está en el rango óptimo 
            para {'hombres (10-18%)' if sexo == 'Hombre' else 'mujeres (16-23%)'}. 
            Puedes elegir tu objetivo nutricional según tus metas personales.
            """)
        
            objetivo_seleccionado = st.selectbox(
                "**Elige tu objetivo nutricional:**",
                ["Déficit (Pérdida de grasa)", "Mantenimiento (Recomposición)", "Superávit (Ganancia muscular)"],
                key="objetivo_nutricional",
                help="Selecciona el objetivo que mejor se alinee con tus metas actuales"
            )
        
            # Determinar porcentaje y explicación según subrango y objetivo
            if sexo == "Hombre":
                if 10 <= grasa_corregida <= 15:
                    # Subrango 10-15% hombres
                    if "Déficit" in objetivo_seleccionado:
                        porcentaje = -10
                        fase = "Déficit moderado: 10%"
                    elif "Mantenimiento" in objetivo_seleccionado:
                        porcentaje = 2.5
                        fase = "Mantenimiento con ligero superávit: 2.5%"
                    else:  # Superávit
                        porcentaje = 7.5
                        fase = "Superávit moderado: 7.5%"
                else:  # 15-18% hombres
                    if "Déficit" in objetivo_seleccionado:
                        porcentaje = -15
                        fase = "Déficit moderado: 15%"
                    elif "Mantenimiento" in objetivo_seleccionado:
                        porcentaje = 0
                        fase = "Mantenimiento"
                    else:  # Superávit
                        porcentaje = 5
                        fase = "Superávit ligero: 5%"
            else:  # Mujer
                if 16 <= grasa_corregida <= 20:
                    # Subrango 16-20% mujeres
                    if "Déficit" in objetivo_seleccionado:
                        porcentaje = -10
                        fase = "Déficit moderado: 10%"
                    elif "Mantenimiento" in objetivo_seleccionado:
                        porcentaje = 2.5
                        fase = "Mantenimiento con ligero superávit: 2.5%"
                    else:  # Superávit
                        porcentaje = 7.5
                        fase = "Superávit moderado: 7.5%"
                else:  # 20-23% mujeres
                    if "Déficit" in objetivo_seleccionado:
                        porcentaje = -15
                        fase = "Déficit moderado: 15%"
                    elif "Mantenimiento" in objetivo_seleccionado:
                        porcentaje = 0
                        fase = "Mantenimiento"
                    else:  # Superávit
                        porcentaje = 5
                        fase = "Superávit ligero: 5%"
        
            # Mostrar explicación del objetivo seleccionado
            st.success(f"**Objetivo seleccionado:** {fase}")
        
        else:
            # Usar lógica automática para usuarios fuera del rango óptimo
            fase, porcentaje = determinar_fase_nutricional_refinada(grasa_corregida, sexo)

        fbeo = 1 + porcentaje / 100  # Cambio de signo para reflejar nueva convención

        # Perfil del usuario
        st.markdown("### 📋 Tu perfil nutricional")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"• **Sexo:** {sexo}")
            st.write(f"• **% Grasa corporal:** {grasa_corregida:.1f}%")
            try:
                st.write(f"• **FFMI:** {ffmi:.2f} ({nivel_ffmi})")
            except Exception:
                st.write("• **FFMI:** – (completa todos los datos para calcular)")
        with col2:
            try:
                st.write(f"• **Nivel:** {nivel_entrenamiento.capitalize()}")
            except Exception:
                st.write("• **Nivel:** –")
            try:
                st.write(f"• **Edad metabólica:** {edad_metabolica} años")
            except Exception:
                st.write("• **Edad metabólica:** –")
            try:
                st.write(f"• **Objetivo:** {fase}")
            except Exception:
                st.write("• **Objetivo:** –")

        # Cálculo del gasto energético
        GE = tmb * geaf * eta + gee_prom_dia
        ingesta_calorica_tradicional = GE * fbeo

        # COMPARATIVA PSMF si aplica
        # UI Display: Only show plan selection if MOSTRAR_PSMF_AL_USUARIO is True
        plan_elegido = "Tradicional"
        if psmf_recs.get("psmf_aplicable") and MOSTRAR_PSMF_AL_USUARIO:
            st.markdown("### ⚡ Opciones de plan nutricional")
            st.warning("Eres candidato para el protocolo PSMF. Puedes elegir entre dos estrategias:")

            plan_elegido = st.radio(
                "Selecciona tu estrategia preferida:",
                ["Plan Tradicional (déficit moderado, más sostenible)",
                 "Protocolo PSMF (pérdida rápida, más restrictivo)"],
                index=0,
                help="PSMF es muy efectivo pero requiere mucha disciplina"
            )
        
            # Grasas automáticas según % grasa corporal (sin selección manual)
            if "PSMF" in plan_elegido:
                st.markdown("#### 🥑 Grasas asignadas automáticamente para PSMF")
                if grasa_corregida < 25:
                    grasa_psmf_seleccionada = 30.0
                    st.info(f"**Grasas asignadas:** {grasa_psmf_seleccionada}g/día (automático para {grasa_corregida:.1f}% grasa corporal < 25%)")
                else:
                    grasa_psmf_seleccionada = 50.0
                    st.info(f"**Grasas asignadas:** {grasa_psmf_seleccionada}g/día (automático para {grasa_corregida:.1f}% grasa corporal ≥ 25%)")
                st.caption("💡 Las grasas se asignan automáticamente según tu porcentaje de grasa corporal corregida para optimizar la adherencia y efectividad del protocolo.")
            else:
                grasa_psmf_seleccionada = 40.0  # Valor por defecto para plan tradicional

            # Technical details: Detailed plan comparison (controlled by SHOW_TECH_DETAILS flag)
            if SHOW_TECH_DETAILS:
                st.markdown("### 📊 Comparativa de planes")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
                    st.markdown("#### ✅ Plan Tradicional")
                    st.metric("Déficit", f"{porcentaje}%", "Moderado")
                    st.metric("Calorías", f"{ingesta_calorica_tradicional:.0f} kcal/día")
                    st.metric("Pérdida esperada", "0.5-0.7 kg/semana")
                    st.markdown("""
                    **Ventajas:**
                    - ✅ Mayor adherencia
                    - ✅ Más energía para entrenar  
                    - ✅ Sostenible largo plazo
                    - ✅ Menor pérdida muscular
                    - ✅ Vida social normal
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    deficit_psmf = int((1 - psmf_recs['calorias_dia']/GE) * 100)
                    perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
                    multiplicador = psmf_recs.get('multiplicador', 8.3)
                    perfil_grasa = psmf_recs.get('perfil_grasa', 'alto % grasa')
                
                    st.markdown('<div class="content-card card-psmf">', unsafe_allow_html=True)
                    st.markdown("#### ⚡ Protocolo PSMF Actualizado")
                    st.metric("Déficit", f"~{deficit_psmf}%", "Agresivo")
                    st.metric("Calorías", f"{psmf_recs['calorias_dia']:.0f} kcal/día")
                    st.metric("Multiplicador", f"{multiplicador}", f"Perfil: {perfil_grasa}")
                    st.metric("Pérdida esperada", f"{perdida_min}-{perdida_max} kg/semana")
                    tier_psmf = psmf_recs.get('tier_psmf', 1)
                    base_prot_usada = psmf_recs.get('base_proteina_usada', 'Peso total')
                    carb_cap = psmf_recs.get('carb_cap_aplicado_g', 50)
                    st.markdown(f"""
                    **Consideraciones:**
                    - ⚠️ Muy restrictivo
                    - ⚠️ Máximo 6-8 semanas
                    - ⚠️ Requiere supervisión médica
                    - 🏷️ Tier {tier_psmf} (base: {base_prot_usada})
                    - ⚠️ Proteína: {psmf_recs['proteina_g_dia']}g/día ({'1.8g/kg' if grasa_corregida < 25 else '1.6g/kg'} automático)
                    - ⚠️ Grasas: {psmf_recs.get('grasa_g_dia', 40)}g/día (automático según % grasa)
                    - ⚠️ Carbos: {psmf_recs.get('carbs_g_dia', 0)}g/día (tope: {carb_cap}g)
                    - ⚠️ Suplementación necesaria
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

        # FORZAR actualización de variables clave desde session_state
        peso = st.session_state.get("peso", 0)
        estatura = st.session_state.get("estatura", 0)
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        sexo = st.session_state.get("sexo", "Hombre")
        edad = st.session_state.get("edad", 0)

        # --- Cálculo de macros para plan elegido ---
        if psmf_recs.get("psmf_aplicable") and "PSMF" in plan_elegido:
            # ----------- PSMF ACTUALIZADO -----------
            ingesta_calorica = psmf_recs['calorias_dia']
            proteina_g = psmf_recs['proteina_g_dia']
            proteina_kcal = proteina_g * 4
        
            # GRASAS: Usar el valor automático calculado por la función PSMF
            grasa_g = psmf_recs.get('grasa_g_dia', 40.0)
            grasa_kcal = grasa_g * 9
        
            # CARBOHIDRATOS: Usar el valor calculado con carb cap aplicado
            carbo_g = psmf_recs.get('carbs_g_dia', 0)
            carbo_kcal = carbo_g * 4
        
            multiplicador = psmf_recs.get('multiplicador', 8.3)
            perfil_grasa = psmf_recs.get('perfil_grasa', 'alto % grasa')
            perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
            tier_psmf = psmf_recs.get('tier_psmf', 1)
            base_proteina_usada = psmf_recs.get('base_proteina_usada', 'Peso total')
            carb_cap = psmf_recs.get('carb_cap_aplicado_g', 50)
            carb_cap_fue_aplicado = psmf_recs.get('carb_cap_fue_aplicado', False)
        
            fase = f"PSMF Actualizado - Pérdida rápida (déficit ~{deficit_psmf}%, multiplicador {multiplicador}, Tier {tier_psmf})"

            # UI Display: Only show warnings if MOSTRAR_PSMF_AL_USUARIO is True
            if MOSTRAR_PSMF_AL_USUARIO:
                # Client-facing vs technical warnings
                if not SHOW_TECH_DETAILS:
                    st.error(f"""
                    ⚠️ **ADVERTENCIA IMPORTANTE SOBRE PSMF:**
                    - Es un protocolo **MUY RESTRICTIVO**
                    - **Duración máxima:** 6-8 semanas
                    - **Requiere:** Supervisión médica y análisis de sangre regulares
                    - **Suplementación obligatoria:** Multivitamínico, omega-3, electrolitos, magnesio
                    - **No apto para:** Personas con historial de TCA, problemas médicos o embarazo
                    """)
                else:
                    st.error(f"""
                    ⚠️ **ADVERTENCIA IMPORTANTE SOBRE PSMF ACTUALIZADO:**
                    - Es un protocolo **MUY RESTRICTIVO** con cálculo basado en tiers de adiposidad
                    - **Duración máxima:** 6-8 semanas
                    - **Tier de adiposidad:** Tier {tier_psmf} (base proteína: {base_proteina_usada})
                    - **Proteína:** {proteina_g}g/día ({psmf_recs.get('factor_proteina_psmf', 1.6)}g/kg × {psmf_recs.get('base_proteina_kg', peso):.1f}kg según {grasa_corregida:.1f}% grasa corporal)
                    - **Grasas:** {grasa_g}g/día (asignación automática según {grasa_corregida:.1f}% grasa corporal)
                    - **Carbohidratos:** {carbo_g}g/día (tope Tier {tier_psmf}: {carb_cap}g) - Solo de vegetales fibrosos
                    - **Multiplicador calórico:** {multiplicador} (perfil: {perfil_grasa})
                    - **Pérdida proyectada:** {perdida_min}-{perdida_max} kg/semana
                    - **Requiere:** Supervisión médica y análisis de sangre regulares
                    - **Suplementación obligatoria:** Multivitamínico, omega-3, electrolitos, magnesio
                    - **No apto para:** Personas con historial de TCA, problemas médicos o embarazo
                    """)
        
            if SHOW_TECH_DETAILS and MOSTRAR_PSMF_AL_USUARIO and carb_cap_fue_aplicado:
                st.info("💡 Se aplicó tope de carbohidratos para mantener PSMF consistente; kcal finales recalculadas por macros.")
        else:
            # ----------- TRADICIONAL -----------
            ingesta_calorica = ingesta_calorica_tradicional

            # Usar función centralizada para calcular macros tradicionales
            macros_tradicional = calcular_macros_tradicional(
                ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg
            )
            
            # Extraer valores calculados
            proteina_g = macros_tradicional['proteina_g']
            proteina_kcal = macros_tradicional['proteina_kcal']
            grasa_g = macros_tradicional['grasa_g']
            grasa_kcal = macros_tradicional['grasa_kcal']
            carbo_g = macros_tradicional['carbo_g']
            carbo_kcal = macros_tradicional['carbo_kcal']
            base_proteina_nombre = macros_tradicional['base_proteina']
            base_proteina_kg = macros_tradicional['base_proteina_kg']
            factor_proteina = macros_tradicional['factor_proteina']
            usar_mlg_para_proteina = macros_tradicional['usar_mlg']
            if carbo_g < 50:
                st.warning(f"⚠️ Tus carbohidratos han quedado muy bajos ({carbo_g}g). Considera aumentar calorías o reducir grasa para una dieta más sostenible.")

            # --- DESGLOSE FINAL VISUAL ---
            # Technical details: Hide detailed breakdown formulas
            if SHOW_TECH_DETAILS:
                st.markdown("### 🍽️ Distribución de macronutrientes")
                st.write(f"- **Proteína:** {proteina_g}g ({proteina_kcal:.0f} kcal, {proteina_kcal/ingesta_calorica*100:.1f}%) - Base: {base_proteina_nombre} ({base_proteina_kg:.1f} kg × {factor_proteina} g/kg)")
                if usar_mlg_para_proteina:
                    st.info("ℹ️ En alta adiposidad, usar peso total infla la proteína de forma inapropiada; por eso se usa MLG como base.")
                st.write(f"- **Grasas:** {grasa_g}g ({grasa_kcal:.0f} kcal, {grasa_kcal/ingesta_calorica*100:.1f}%)")
                st.write(f"- **Carbohidratos:** {carbo_g}g ({carbo_kcal:.0f} kcal, {carbo_kcal/ingesta_calorica*100:.1f}%)")



            # Resultado final con diseño premium
            st.markdown("### 🎯 Tu plan nutricional personalizado")

            # Client-facing: Always show high-level results
            st.markdown(f"""
            **Calorías objetivo:** {ingesta_calorica:.0f} kcal/día
        
            **Macros finales (P/F/C):** {proteina_g}g / {grasa_g}g / {carbo_g}g
            """)
        
            # Technical details: Show detailed metrics and breakdowns
            if SHOW_TECH_DETAILS:
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔥 Calorías", f"{ingesta_calorica:.0f} kcal/día", 
                             f"{ingesta_calorica/peso:.1f} kcal/kg" if peso > 0 else "– kcal/kg")
                with col2:
                    st.metric("🥩 Proteína", f"{proteina_g} g", 
                             f"{proteina_g/peso:.2f} g/kg" if peso > 0 else "– g/kg")
                with col3:
                    st.metric("🥑 Grasas", f"{grasa_g} g", 
                             f"{round(grasa_kcal/ingesta_calorica*100)}%" if ingesta_calorica > 0 else "–%")
                with col4:
                    st.metric("🍞 Carbohidratos", f"{carbo_g} g", 
                             f"{round(carbo_kcal/ingesta_calorica*100)}%")

                # Visualización de distribución de macros
                st.markdown("### 📊 Distribución de macronutrientes")
                import pandas as pd
                macro_data = {
                    "Macronutriente": ["Proteína", "Grasas", "Carbohidratos"],
                    "Gramos": [proteina_g, grasa_g, carbo_g],
                    "Calorías": [f"{proteina_kcal:.0f}", f"{grasa_kcal:.0f}", f"{carbo_kcal:.0f}"],
                    "% del total": [
                        f"{round(proteina_kcal/ingesta_calorica*100, 1)}%",
                        f"{round(grasa_kcal/ingesta_calorica*100, 1)}%",
                        f"{round(carbo_kcal/ingesta_calorica*100, 1)}%"
                    ]
                }
                df_macros = pd.DataFrame(macro_data)
                st.dataframe(
                    df_macros,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Macronutriente": st.column_config.TextColumn("Macronutriente", width="medium"),
                        "Gramos": st.column_config.TextColumn("Gramos/día", width="small"),
                        "Calorías": st.column_config.TextColumn("Calorías", width="small"),
                        "% del total": st.column_config.TextColumn("% Total", width="small"),
                    }
                )

            # Recomendaciones adicionales
            st.markdown("### 💡 Recomendaciones para optimizar resultados")
            col1, col2 = st.columns(2)
            with col1:
                st.info("""
                **📅 Timing de comidas:**
                - 3-4 comidas al día
                - Proteína en cada comida
                - Pre/post entreno con carbos
                - Última comida 2-3h antes de dormir
                """)
            with col2:
                st.info("""
                **💧 Hidratación y suplementos:**
                - Agua: 35-40ml/kg peso
                - Creatina: 5g/día
                - Vitamina D: 2000-4000 UI
                - Omega-3: 2-3g EPA+DHA
                """)

        st.markdown('</div>', unsafe_allow_html=True)
else:
    # When USER_VIEW=False: Run essential calculations without UI display
    # This ensures email generation has all required variables
    progress.progress(100)
    progress_text.text("Procesando datos...")
    
    # Determinar si el usuario está en el rango óptimo
    en_rango_optimo = False
    if sexo == "Hombre" and 10 <= grasa_corregida <= 18:
        en_rango_optimo = True
    elif sexo == "Mujer" and 16 <= grasa_corregida <= 23:
        en_rango_optimo = True
    
    # Use automatic phase determination (no user selection when USER_VIEW=False)
    fase, porcentaje = determinar_fase_nutricional_refinada(grasa_corregida, sexo)
    fbeo = 1 + porcentaje / 100
    
    # Calculate energy expenditure
    GE = tmb * geaf * eta + gee_prom_dia
    ingesta_calorica_tradicional = GE * fbeo
    
    # Default plan selection
    plan_elegido = "Tradicional"
    grasa_psmf_seleccionada = 40.0
    
    # Calculate macros for traditional plan using centralized function
    ingesta_calorica = ingesta_calorica_tradicional
    macros_tradicional = calcular_macros_tradicional(
        ingesta_calorica_tradicional, tmb, sexo, grasa_corregida, peso, mlg
    )
    
    # Extract calculated values
    proteina_g = macros_tradicional['proteina_g']
    proteina_kcal = macros_tradicional['proteina_kcal']
    grasa_g = macros_tradicional['grasa_g']
    grasa_kcal = macros_tradicional['grasa_kcal']
    carbo_g = macros_tradicional['carbo_g']
    carbo_kcal = macros_tradicional['carbo_kcal']

# --- FORZAR actualización de variables clave desde session_state ---
peso = st.session_state.get("peso", 0)
estatura = st.session_state.get("estatura", 0)
grasa_corporal = st.session_state.get("grasa_corporal", 0)

# RESUMEN FINAL MEJORADO (display controlled by USER_VIEW flag)
if USER_VIEW:
    st.markdown("---")
    st.markdown('<div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E;">', unsafe_allow_html=True)
    st.markdown("## 🎯 **Resumen Final de tu Evaluación MUPAI**")
    st.markdown(f"*Fecha: {fecha_llenado} | Cliente: {nombre}*")

    # Crear resumen visual con métricas clave
    col1, col2, col3 = st.columns(3)
    with col1:
        # Ensure edad is numeric for calculations
        try:
            edad_num = int(edad)
            diferencia_edad = edad_metabolica - edad_num
            evaluacion = '⚠️ Mejorar' if edad_metabolica > edad_num + 2 else '✅ Excelente' if edad_metabolica < edad_num - 2 else '👍 Normal'
        except (ValueError, TypeError):
            edad_num = 25  # Default fallback
            diferencia_edad = 0
            evaluacion = '👍 Normal'
    
        st.markdown(f"""
        ### 👤 Perfil Personal
        - **Edad cronológica:** {edad} años
        - **Edad metabólica:** {edad_metabolica} años
        - **Diferencia:** {diferencia_edad:+d} años
        - **Evaluación:** {evaluacion}
        """)
    with col2:
        # Determinar interpretación del FFMI para el resumen según modo
        if modo_ffmi == "GREEN":
            if nivel_ffmi in ["Bajo", "Promedio"]:
                ffmi_interpretacion = "Margen significativo de mejora"
            elif nivel_ffmi == "Bueno":
                ffmi_interpretacion = "Buen desarrollo, continúa mejorando"
            elif nivel_ffmi == "Avanzado":
                ffmi_interpretacion = "Desarrollo avanzado, cerca del límite natural"
            else:  # Élite
                ffmi_interpretacion = "Desarrollo excepcional alcanzado"
            ffmi_texto_potencial = f"- *{porc_potencial:.0f}% del potencial máximo ({ffmi_genetico_max:.1f} FFMI)*"
        elif modo_ffmi == "AMBER":
            ffmi_interpretacion = "Interpretación limitada por adiposidad"
            ffmi_texto_potencial = "- *Valores orientativos (reduce grasa para mayor precisión)*"
        else:  # RED
            ffmi_interpretacion = "No aplica clasificación atlética"
            ffmi_texto_potencial = "- *Reducir grasa para interpretación válida*"
    
        st.markdown(f"""
        ### 💪 Composición Corporal
        - **Peso:** {peso} kg | **Altura:** {estatura:.1f} cm
        - **% Grasa:** {grasa_corregida:.1f}% | **MLG:** {mlg:.1f} kg
        - **Cintura:** {f"{circunferencia_cintura:.1f} cm" if circunferencia_cintura > 0 else "No medido"} | **WtHR:** {f"{circunferencia_cintura/estatura:.3f}" if circunferencia_cintura > 0 and estatura > 0 else "N/D"}
        - **FFMI:** {ffmi:.2f} {"(" + nivel_ffmi + ")" if modo_ffmi == "GREEN" else "(Modo " + modo_ffmi + ")"}
          - *{ffmi_interpretacion}*
          {ffmi_texto_potencial if modo_ffmi != "RED" else ""}
        - **FMI:** {fmi:.2f} (Índice de masa grasa)
        """)
    with col3:
        # Safe calculations for display
        proteina_ratio = f"({proteina_g/peso:.2f}g/kg)" if peso > 0 else "(–g/kg)"
        grasa_percent = f"({round(grasa_kcal/ingesta_calorica*100)}%)" if ingesta_calorica > 0 else "(–%)"
        carbo_percent = f"({round(carbo_kcal/ingesta_calorica*100)}%)" if ingesta_calorica > 0 else "(–%)"
        estrategia = plan_elegido.split('(')[0].strip() if 'plan_elegido' in locals() and plan_elegido else "Plan tradicional"
    
        st.markdown(f"""
        ### 🍽️ Plan Nutricional
        - **Objetivo:** {fase}
        - **Calorías:** {ingesta_calorica:.0f} kcal/día
        - **Proteína:** {proteina_g}g {proteina_ratio}
        - **Grasas:** {grasa_g}g {grasa_percent}
        - **Carbohidratos:** {carbo_g}g {carbo_percent}
        - **Estrategia:** {estrategia}
        """)

    # Mensaje motivacional personalizado
    mensaje_motivacional = ""
    try:
        edad_num = int(edad)
        if edad_metabolica > edad_num + 2:
            mensaje_motivacional = "Tu edad metabólica indica que hay margen significativo de mejora. ¡Este plan te ayudará a rejuvenecer metabólicamente!"
        elif edad_metabolica < edad_num - 2:
            mensaje_motivacional = "¡Excelente! Tu edad metabólica es menor que tu edad real. Mantén este gran trabajo."
        else:
            mensaje_motivacional = "Tu edad metabólica está bien alineada con tu edad cronológica. Sigamos optimizando tu composición corporal."
    except (ValueError, TypeError):
        mensaje_motivacional = "Tu edad metabólica está bien alineada con tu edad cronológica. Sigamos optimizando tu composición corporal."

    st.success(f"""
    ### ✅ Evaluación completada exitosamente

    {mensaje_motivacional}

    **Tu plan personalizado** considera todos los factores evaluados: composición corporal, 
    nivel de entrenamiento, actividad diaria y objetivos. La fase recomendada es **{fase}** 
    con una ingesta de **{ingesta_calorica:.0f} kcal/día**.

    {'⚠️ **Nota:** Elegiste el protocolo PSMF. Recuerda que es temporal (6-8 semanas máximo) y requiere supervisión.' if 'PSMF' in plan_elegido and MOSTRAR_PSMF_AL_USUARIO else ''}
    """)
    # Advertencias finales si aplican
    if fuera_rango:
        st.warning(f"""
        ⚠️ **Consideración sobre el FFMI:** Tu % de grasa ({grasa_corregida:.1f}%) está fuera del 
        rango ideal para máxima precisión ({rango_grasa_ok[0]}-{rango_grasa_ok[1]}%). 
        Los valores de FFMI y potencial muscular son estimaciones que mejorarán su precisión 
        cuando alcances el rango óptimo.
        """)

    st.markdown('</div>', unsafe_allow_html=True)
else:
    # When USER_VIEW=False: Show simple completion message instead of detailed results
    st.markdown("---")
    st.markdown('<div class="content-card" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white;">', unsafe_allow_html=True)
    st.markdown("## ✅ Evaluación completada exitosamente")
    st.markdown("""
    Tus respuestas han sido recolectadas, validadas y procesadas correctamente.

    La información que proporcionaste será utilizada por Muscle Up GYM y el sistema MUPAI 
    para el análisis integral de tu perfil corporal, energético y metabólico, 
    así como para la generación de tu plan nutricional personalizado, proyecciones y recomendaciones.

    Con fines de seguimiento, control de calidad y optimización continua del servicio, 
    estos datos quedan registrados de forma segura en los sistemas internos de Muscle Up GYM.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ====== BOTONES Y ENVÍO FINAL (SOLO POR BOTÓN, NUNCA AUTOMÁTICO) ======

def datos_completos_para_email():
    """
    Valida que todos los campos obligatorios del cuestionario estén completos.
    
    Returns:
        list: Lista de nombres de campos faltantes. Lista vacía si todo está completo.
    """
    faltantes = []
    
    # Validar datos personales básicos
    if not nombre or not nombre.strip():
        faltantes.append("Nombre completo")
    if not telefono or not telefono.strip():
        faltantes.append("Teléfono")
    if not email_cliente or not email_cliente.strip():
        faltantes.append("Email")
    if not edad or edad <= 0:
        faltantes.append("Edad")
    
    # Validar ciclo menstrual (obligatorio solo para mujeres)
    if sexo == "Mujer":
        ciclo_menstrual = st.session_state.get('ciclo_menstrual')
        if not ciclo_menstrual or ciclo_menstrual == "Selecciona una opción...":
            faltantes.append("Fase del ciclo menstrual")
    
    # Validar datos antropométricos
    if not peso or peso <= 0:
        faltantes.append("Peso corporal")
    if not estatura or estatura <= 0:
        faltantes.append("Estatura")
    if not grasa_corporal or grasa_corporal <= 0:
        faltantes.append("Porcentaje de grasa corporal")
    
    # Validar experiencia de entrenamiento
    # Check both the new system and old system for backward compatibility
    if st.session_state.get('experiencia_completa', False):
        # Nuevo sistema - validar que esté completo
        pass  # Ya está validado
    else:
        # Sistema antiguo
        experiencia_valor = st.session_state.get("experiencia_seleccion", "") or st.session_state.get("experiencia", "")
        if not experiencia_valor or not isinstance(experiencia_valor, str) or len(experiencia_valor) < 3:
            faltantes.append("Nivel de experiencia en entrenamiento")
    
    # Validar ejercicios funcionales (deben ser 5)
    ejercicios_data = st.session_state.get("datos_ejercicios", {})
    if not ejercicios_data or len(ejercicios_data) < 5:
        faltantes.append(f"Ejercicios funcionales completos (tienes {len(ejercicios_data) if ejercicios_data else 0} de 5 requeridos)")
    
    # Validar fotografías de progreso (obligatorias)
    progress_photos = st.session_state.get("progress_photos", {})
    photo_labels = {
        "front_relaxed": "Foto 1 - Frontal relajado",
        "side_relaxed_right": "Foto 2 - Perfil lateral relajado (derecho)",
        "back_relaxed": "Foto 3 - Posterior relajado"
    }
    for key in REQUIRED_PROGRESS_PHOTOS:
        if not progress_photos.get(key):
            faltantes.append(photo_labels.get(key, f"Foto requerida: {key}"))
    
    # Validar metas personales (obligatorio)
    metas_personales = st.session_state.get("metas_personales", "")
    if not metas_personales or len(metas_personales.strip()) < 50:
        faltantes.append("Metas Personales - Objetivos a mediano y largo plazo (mínimo 50 caracteres)")
    
    return faltantes

# Construir tabla_resumen robusta para el email (idéntica a tu estructura, NO resumida)
# Calculate safe values
try:
    imc = peso/(estatura/100)**2 if estatura > 0 else 0
    ratio_kcal_kg = ingesta_calorica/peso if peso > 0 else 0
    proteina_percent = round(proteina_kcal/ingesta_calorica*100, 1) if ingesta_calorica > 0 else 0
    grasa_percent = round(grasa_kcal/ingesta_calorica*100, 1) if ingesta_calorica > 0 else 0
    carbo_percent = round(carbo_kcal/ingesta_calorica*100, 1) if ingesta_calorica > 0 else 0
    proteina_kcal_safe = proteina_g * 4 if 'proteina_g' in locals() else 0
    grasa_kcal_safe = grasa_g * 9 if 'grasa_g' in locals() else 0
    carbo_kcal_safe = carbo_g * 4 if 'carbo_g' in locals() else 0
except:
    imc = 0
    ratio_kcal_kg = 0
    proteina_percent = 0
    grasa_percent = 0
    carbo_percent = 0
    proteina_kcal_safe = 0
    grasa_kcal_safe = 0
    carbo_kcal_safe = 0

# Initialize missing variables
if 'fbeo' not in locals():
    fbeo = 1.0

# Ensure critical variables exist for email generation
if 'fmi' not in locals():
    fmi = calcular_fmi(peso if 'peso' in locals() else 70, 
                       grasa_corregida if 'grasa_corregida' in locals() else 20, 
                       estatura if 'estatura' in locals() else 170) if 'peso' in locals() and 'grasa_corregida' in locals() and 'estatura' in locals() else 0

if 'modo_ffmi' not in locals():
    modo_ffmi = obtener_modo_interpretacion_ffmi(
        grasa_corregida if 'grasa_corregida' in locals() else 20,
        sexo if 'sexo' in locals() else "Hombre"
    ) if 'grasa_corregida' in locals() and 'sexo' in locals() else "GREEN"

if 'nivel_ffmi' not in locals():
    nivel_ffmi = "Promedio"

if 'ffmi_genetico_max' not in locals():
    ffmi_genetico_max = 22 if sexo == "Hombre" else 19

if 'porc_potencial' not in locals():
    porc_potencial = 0

if 'ffmi' not in locals():
    ffmi = 0

# Helper function to generate FFMI classification text for email
def generar_texto_clasificacion_ffmi(modo_ffmi, sexo, nivel_ffmi, ffmi_genetico_max, porc_potencial, ffmi):
    """
    Genera el texto de clasificación FFMI para el email según el modo.
    """
    if modo_ffmi == "GREEN":
        # GREEN mode: Full classification with potential
        if sexo == "Hombre":
            interpretacion = """- Bajo (<18): Desarrollo insuficiente, priorizar fuerza y nutrición
- Promedio (18-20): Normal en población general, gran margen de mejora
- Bueno (20-22): Buen desarrollo, requiere 2-4 años de entrenamiento
- Avanzado (22-25): Muy avanzado, cerca del límite natural
- Élite (>25): Excepcional, difícil de alcanzar naturalmente"""
        else:  # Mujer
            interpretacion = """- Bajo (<15): Desarrollo insuficiente, priorizar fuerza y nutrición
- Promedio (15-17): Normal en población general, gran margen de mejora
- Bueno (17-19): Buen desarrollo, requiere 2-4 años de entrenamiento
- Avanzado (19-21): Muy avanzado, cerca del límite natural
- Élite (>21): Excepcional, difícil de alcanzar naturalmente"""
        
        return f"""- Clasificación: {nivel_ffmi}
- FFMI máximo estimado (genético): {ffmi_genetico_max:.1f}
- Potencial alcanzado: {porc_potencial:.0f}%
- Margen de crecimiento: {max(0, ffmi_genetico_max - ffmi):.1f} puntos FFMI

INTERPRETACIÓN PARA {sexo.upper()}:
{interpretacion}"""
    
    elif modo_ffmi == "AMBER":
        # AMBER mode: Limited interpretation
        return """- Clasificación: FFMI calculado; interpretación limitada por adiposidad
- Valores de potencial: orientativos (reduce grasa para mayor precisión)"""
    
    else:  # RED
        # RED mode: Not applicable
        return """- Clasificación FFMI: No aplica

EXPLICACIÓN:
Con adiposidad muy alta, el FFMI puede elevarse por masa libre de grasa no muscular
(incluyendo agua corporal expandida, órganos, masa estructural) y deja de ser un proxy
válido de muscularidad atlética. Se reporta el valor pero no se clasifica.

RECOMENDACIÓN:
Enfócate en reducir tu porcentaje de grasa corporal a niveles más saludables.
Una vez logrado, el FFMI será interpretable y útil para evaluar progreso muscular."""

# Helper function to classify FMI for email
def clasificar_fmi_email(fmi, sexo):
    """
    Clasifica el FMI para el email según sexo.
    """
    if sexo == "Hombre":
        if fmi < 3:
            return "Bajo (<3)"
        elif fmi < 6:
            return "Normal (3-6)"
        elif fmi < 9:
            return "Elevado (6-9)"
        else:
            return "Muy elevado (>9)"
    else:  # Mujer
        if fmi < 5:
            return "Bajo (<5)"
        elif fmi < 9:
            return "Normal (5-9)"
        elif fmi < 13:
            return "Elevado (9-13)"
        else:
            return "Muy elevado (>13)"

# Generate classification texts
texto_clasificacion_ffmi = generar_texto_clasificacion_ffmi(
    modo_ffmi, sexo, nivel_ffmi, ffmi_genetico_max, porc_potencial, ffmi
)
categoria_fmi = clasificar_fmi_email(fmi, sexo)

# Format grasa_visceral for report
grasa_visceral_report = safe_int(grasa_visceral, 0)
grasa_visceral_str = str(grasa_visceral_report) if grasa_visceral_report >= 1 else 'No medido'

# Format circunferencia_cintura and calculate WtHR for report
circunferencia_cintura_report = safe_float(circunferencia_cintura, 0.0)
circunferencia_cintura_str = f"{circunferencia_cintura_report:.1f} cm" if circunferencia_cintura_report > 0 else 'No medido'

# Calculate WtHR (Waist-to-Height Ratio)
wthr_report = 0.0
wthr_str = 'No medido'
wthr_clasificacion_str = ''
if circunferencia_cintura_report > 0 and estatura > 0:
    wthr_report = circunferencia_cintura_report / estatura
    wthr_str = f"{wthr_report:.3f}"
    wthr_clasificacion_str = f" → {clasificar_wthr(wthr_report)}"

# Agregar secciones adicionales del cuestionario - mover antes de tabla_resumen
experiencia_text = experiencia if 'experiencia' in locals() and experiencia else "No especificado"
nivel_actividad_text = nivel_actividad.split('(')[0].strip() if 'nivel_actividad' in locals() and nivel_actividad else "No especificado"

# Generar detalle de ejercicios funcionales
ejercicios_detalle = ""
if 'ejercicios_data' in locals() and ejercicios_data:
    for ejercicio, valor in ejercicios_data.items():
        nivel_ej = st.session_state.niveles_ejercicios.get(ejercicio, "No evaluado")
        if ejercicio in ["Plancha", "L-sit"]:
            ejercicios_detalle += f"   • {ejercicio}: {valor} segundos → Nivel: {nivel_ej}\n"
        else:
            ejercicios_detalle += f"   • {ejercicio}: {valor} repeticiones → Nivel: {nivel_ej}\n"
else:
    ejercicios_detalle = "   • No se completaron las evaluaciones funcionales\n"

# Calcular ambos planes nutricionales para comparación
plan_tradicional_calorias = ingesta_calorica_tradicional if 'ingesta_calorica_tradicional' in locals() else 0
plan_psmf_disponible = psmf_recs.get("psmf_aplicable", False) if 'psmf_recs' in locals() else False

# Información de entrenamiento de fuerza
dias_fuerza_text = dias_fuerza if 'dias_fuerza' in locals() else 0
kcal_sesion_text = kcal_sesion if 'kcal_sesion' in locals() else 0

# Calcular categoría de grasa corporal (una sola vez)
categoria_grasa_corporal = (
    "Muy bajo (Competición)" if (sexo == "Hombre" and grasa_corregida < 6) or (sexo == "Mujer" and grasa_corregida < 12)
    else "Atlético" if (sexo == "Hombre" and grasa_corregida < 12) or (sexo == "Mujer" and grasa_corregida < 17)
    else "Fitness" if (sexo == "Hombre" and grasa_corregida < 18) or (sexo == "Mujer" and grasa_corregida < 23)
    else "Promedio" if (sexo == "Hombre" and grasa_corregida < 25) or (sexo == "Mujer" and grasa_corregida < 30)
    else "Alto"
)

tabla_resumen = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              EVALUACIÓN MUPAI - INFORME CIENTÍFICO COMPLETO                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Sistema: MUPAI v2.0 - Muscle Up Performance Assessment Intelligence          ║
║  Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 1: IDENTIFICACIÓN DEL CLIENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 DATOS PERSONALES:
   • Nombre completo: {nombre}
   • Edad: {edad} años
   • Sexo biológico: {sexo}
{f"   • Fase del ciclo menstrual: {st.session_state.get('ciclo_menstrual', 'No especificado')}" if sexo == "Mujer" and st.session_state.get('ciclo_menstrual') else ""}
   • Teléfono: {telefono}
   • Email: {email_cliente}
   • Fecha de evaluación: {fecha_llenado}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 2: COMPOSICIÓN CORPORAL COMPLETA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 2.1 ANTROPOMETRÍA BÁSICA:
   • Peso corporal: {peso} kg
   • Estatura: {estatura:.1f} cm ({estatura/100:.2f} m)
   • IMC: {imc:.1f} kg/m²
   • Circunferencia de cintura: {circunferencia_cintura_str}
   • Ratio Cintura-Altura (WtHR): {wthr_str}{wthr_clasificacion_str}

📊 2.2 ANÁLISIS DE TEJIDOS:
   • Método de medición: {metodo_grasa}
   • % Grasa corporal medido: {grasa_corporal}%
   • % Grasa corregido (equivalente DEXA): {grasa_corregida:.1f}%
   • Ajuste aplicado: {grasa_corregida - grasa_corporal:+.1f}%
   • Categoría de adiposidad: {categoria_grasa_corporal}
   
   • Masa Libre de Grasa (MLG): {mlg:.1f} kg
   • Masa Grasa: {peso - mlg:.1f} kg
   • % Masa muscular: {safe_float(masa_muscular, 0.0):.1f}%
   • Grasa visceral (nivel 1-59): {grasa_visceral_str}

📈 2.3 ÍNDICES DE COMPOSICIÓN CORPORAL:

   ┌─ FFMI (Fat-Free Mass Index) ─────────────────────────────────────┐
   │ Indicador científico del desarrollo muscular ajustado por altura │
   └──────────────────────────────────────────────────────────────────┘
   
   MODO DE INTERPRETACIÓN: {modo_ffmi}
   {f"🟢 GREEN - Interpretación válida como muscularidad" if modo_ffmi == "GREEN" else "🟡 AMBER - Interpretación limitada por adiposidad" if modo_ffmi == "AMBER" else "🔴 RED - No aplicable clasificación atlética"}
   
   CÁLCULO:
   • MLG: {mlg:.1f} kg
   • FFMI Base = MLG / Altura²: {mlg / ((estatura/100)**2):.2f}
   • FFMI Normalizado (a 1.80m): {ffmi:.2f}
     Fórmula: FFMI_base + 6.3 × (1.8 - altura_m)
   
   CLASIFICACIÓN:
{texto_clasificacion_ffmi}

   ┌─ FMI (Fat Mass Index) ───────────────────────────────────────────┐
   │ Indicador de adiposidad ajustado por altura                      │
   └──────────────────────────────────────────────────────────────────┘
   
   • Masa Grasa: {peso - mlg:.1f} kg
   • FMI = Masa Grasa / Altura²: {fmi:.2f}
   • Categoría: {categoria_fmi}

   NOTA: Los umbrales femeninos difieren de masculinos debido a diferencias
   hormonales (menos testosterona), mayor % grasa esencial, y diferente
   distribución de masa muscular.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 3: EVALUACIÓN FUNCIONAL Y NIVEL DE ENTRENAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 3.1 EXPERIENCIA AUTODECLARADA:
{experiencia_text}

💪 3.2 PRUEBAS FUNCIONALES:
{ejercicios_detalle}

🎯 3.3 NIVEL GLOBAL DE ENTRENAMIENTO:

   El nivel se calcula mediante puntuación ponderada de tres componentes:

   ┌──────────────────────────────────────────────────────────────────┐
   │ COMPONENTE 1: DESARROLLO MUSCULAR (FFMI)                        │
   │ • Puntuación: {puntos_ffmi if 'puntos_ffmi' in locals() else 0}/5 puntos                                        │
   │ • Clasificación: {nivel_ffmi}                                           │
   │ • Interpretación: Masa muscular ajustada por altura             │
   ├──────────────────────────────────────────────────────────────────┤
   │ COMPONENTE 2: RENDIMIENTO FUNCIONAL                             │
   │ • Puntuación: {puntos_funcional if 'puntos_funcional' in locals() else 0:.1f}/4 puntos                                       │
   │ • Base: Promedio de ejercicios evaluados                        │
   │ • Interpretación: Capacidad física en movimientos fundamentales │
   ├──────────────────────────────────────────────────────────────────┤
   │ COMPONENTE 3: EXPERIENCIA DECLARADA                             │
   │ • Puntuación: {puntos_exp if 'puntos_exp' in locals() else 0}/4 puntos                                         │
   │ • Interpretación: Años de entrenamiento y conocimiento          │
   └──────────────────────────────────────────────────────────────────┘

   SISTEMA DE PONDERACIÓN:
{'   ESTÁNDAR (grasa en rango saludable):' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else '   AJUSTADA (grasa fuera de rango saludable):'}
{'   • FFMI: 40% | Funcional: 40% | Experiencia: 20%' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else '   • FFMI: 0% (excluido) | Funcional: 80% | Experiencia: 20%'}

{'   NOTA: Con % grasa saludable, el FFMI es indicador confiable.' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else f'   NOTA: Con % grasa fuera de rango (>{25 if sexo == "Hombre" else 32}%), el FFMI no se pondera.'}

   ╔════════════════════════════════════════════════════════════════╗
   ║  RESULTADO FINAL                                               ║
   ║  • Nivel: {nivel_entrenamiento.upper() if 'nivel_entrenamiento' in locals() else 'INTERMEDIO'}                                            ║
   ║  • Puntuación: {puntaje_total if 'puntaje_total' in locals() else 0:.2f}/1.0                                          ║
   ║  • Estado grasa: {'En rango saludable' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else 'Fuera de rango saludable'}                               ║
   ╚════════════════════════════════════════════════════════════════╝"""

# ==================== SECCIÓN 4: SUEÑO + ESTRÉS (si disponible) ====================
# Se integra ANTES del gasto energético porque afecta la recuperación
if st.session_state.get('suenyo_estres_completado', False) and st.session_state.get('suenyo_estres_data'):
    data_se = st.session_state.suenyo_estres_data
    
    if all(key in data_se for key in ['sleep_score', 'stress_score', 'ir_se', 'nivel_recuperacion']):
        # Generar banderas de alerta
        banderas_texto = ""
        if data_se.get('banderas'):
            for tipo, titulo, descripcion in data_se['banderas']:
                banderas_texto += f"   {tipo}: {titulo}\n   {descripcion}\n\n"
        else:
            banderas_texto = "   ✅ No se detectaron banderas de alerta.\n"
        
        tabla_resumen += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 4: ESTADO DE RECUPERACIÓN (SUEÑO + ESTRÉS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Factores críticos que impactan la recuperación, síntesis proteica y
   adaptación al entrenamiento.

🌙 4.1 CALIDAD DEL SUEÑO:
   • Horas por noche: {data_se.get('horas_sueno', 'No reportado')}
   • Tiempo para conciliar: {data_se.get('tiempo_conciliar', 'No reportado')}
   • Despertares nocturnos: {data_se.get('veces_despierta', 'No reportado')}
   • Calidad percibida: {data_se.get('calidad_sueno', 'No reportado')}

🧠 4.2 NIVEL DE ESTRÉS:
   • Sensación de sobrecarga: {data_se.get('sobrecarga', 'No reportado')}
   • Falta de control: {data_se.get('falta_control', 'No reportado')}
   • Dificultad para manejar: {data_se.get('dificultad_manejar', 'No reportado')}
   • Irritabilidad: {data_se.get('irritabilidad', 'No reportado')}

📊 4.3 PUNTUACIONES CALCULADAS:

   ┌─────────────────────────────────────────────────────────────────┐
   │ Sleep Score:  {data_se.get('sleep_score', 0):.1f}/100  │  Stress Score:  {data_se.get('stress_score', 0):.1f}/100 │
   ├─────────────────────────────────────────────────────────────────┤
   │ Índice IR-SE (Recuperación): {data_se.get('ir_se', 0):.1f}/100                       │
   │ Fórmula: (Sleep × 60%) + (Stress × 40%)                        │
   ├─────────────────────────────────────────────────────────────────┤
   │ CLASIFICACIÓN: {data_se.get('nivel_recuperacion', 'No determinado')} {data_se.get('emoji_nivel', '')}                                     │
   │ {data_se.get('mensaje_nivel', '')}                             │
   └─────────────────────────────────────────────────────────────────┘

   RANGOS: ALTA (70-100) | MEDIA (50-69) | BAJA (<50)

⚠️ BANDERAS DE ALERTA:
{banderas_texto}
💡 IMPACTO EN ENTRENAMIENTO:
   • Sueño <7h reduce síntesis proteica hasta 18%
   • Estrés crónico eleva cortisol (catabolismo muscular)
   • Si IR-SE < 50, considerar reducir volumen/intensidad"""

# Calcular proyección científica para el email
try:
    porcentaje_email = obtener_porcentaje_para_proyeccion(
        plan_elegido if 'plan_elegido' in locals() else "",
        psmf_recs if 'psmf_recs' in locals() else {},
        GE if 'GE' in locals() else 0,
        porcentaje if 'porcentaje' in locals() else 0
    )
        
    proyeccion_email = calcular_proyeccion_cientifica(
        sexo, 
        grasa_corregida, 
        nivel_entrenamiento if 'nivel_entrenamiento' in locals() else 'intermedio',
        peso, 
        porcentaje_email
    )
    objetivo_texto = "(déficit)" if porcentaje_email < 0 else "(superávit)" if porcentaje_email > 0 else "(mantenimiento)"
    porcentaje_valor = porcentaje_email
except:
    porcentaje_email = 0
    objetivo_texto = "(mantenimiento)"
    porcentaje_valor = 0
    proyeccion_email = {
        'rango_semanal_pct': (0, 0),
        'rango_semanal_kg': (0, 0),
        'rango_total_6sem_kg': (0, 0),
        'explicacion_textual': 'Error en cálculo'
    }

tabla_resumen += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 5: GASTO ENERGÉTICO (MOTOR METABÓLICO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Cálculo del gasto energético total mediante componentes aditivos.

🔥 5.1 TASA METABÓLICA BASAL (TMB):
   • Ecuación: Cunningham (basada en MLG)
   • TMB = 500 + (22 × MLG)
   • Resultado: {tmb:.0f} kcal/día
   • Edad metabólica estimada: {edad_metabolica} años (vs cronológica: {edad} años)

🚶 5.2 GASTO POR ACTIVIDAD DIARIA (GEAF):
   • Nivel: {nivel_actividad_text}
   • Factor multiplicador: {geaf if 'geaf' in locals() else 1.0}
   • Descripción: {nivel_actividad if 'nivel_actividad' in locals() and nivel_actividad else 'No especificado'}
   • Impacto: +{(geaf-1)*100 if 'geaf' in locals() else 0:.0f}% sobre TMB

🏋️ 5.3 GASTO POR ENTRENAMIENTO (GEE):
   • Días/semana: {dias_fuerza_text}
   • Gasto por sesión: {kcal_sesion_text} kcal
   • Criterio: Basado en nivel ({nivel_entrenamiento.capitalize() if 'nivel_entrenamiento' in locals() else 'Intermedio'})
   • Gasto semanal: {gee_semanal if 'gee_semanal' in locals() else 0:.0f} kcal
   • Promedio diario: {gee_prom_dia if 'gee_prom_dia' in locals() else 0:.0f} kcal/día

🔥 5.4 EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):
   • Factor: {eta if 'eta' in locals() else 1.1}
   • Criterio: {eta_desc if 'eta_desc' in locals() else 'ETA estándar'}
   • Justificación: % grasa ({grasa_corregida:.1f}%) y sexo ({sexo})

   ╔════════════════════════════════════════════════════════════════╗
   ║  GASTO ENERGÉTICO TOTAL (GE)                                   ║
   ║  GE = (TMB × GEAF) + GEE × ETA                                 ║
   ║                                                                ║
   ║  GE = ({tmb:.0f} × {geaf if 'geaf' in locals() else 1.0}) + {gee_prom_dia if 'gee_prom_dia' in locals() else 0:.0f} × {eta if 'eta' in locals() else 1.1}                             ║
   ║                                                                ║
   ║  ══► GE TOTAL: {GE:.0f} kcal/día                               ║
   ╚════════════════════════════════════════════════════════════════╝"""

# Calcular macros del plan tradicional para el resumen del email usando función centralizada
macros_tradicional_email = calcular_macros_tradicional(
    plan_tradicional_calorias, tmb, sexo, grasa_corregida, peso, mlg
)

# Extraer valores
proteina_g_tradicional = macros_tradicional_email['proteina_g']
proteina_kcal_tradicional = macros_tradicional_email['proteina_kcal']
grasa_g_tradicional = macros_tradicional_email['grasa_g']
grasa_kcal_tradicional = macros_tradicional_email['grasa_kcal']
carbo_g_tradicional = macros_tradicional_email['carbo_g']
carbo_kcal_tradicional = macros_tradicional_email['carbo_kcal']
base_proteina_nombre_email = macros_tradicional_email['base_proteina']
factor_proteina_tradicional_email = macros_tradicional_email['factor_proteina']

# Calcular base proteína kg para la nota
usar_mlg_para_proteina_email = (base_proteina_nombre_email == "MLG")
base_proteina_kg_email = mlg if usar_mlg_para_proteina_email else peso

nota_mlg_email = f"\n     (Base: {base_proteina_nombre_email} = {base_proteina_kg_email:.1f} kg × {factor_proteina_tradicional_email:.1f} g/kg)" if usar_mlg_para_proteina_email else ""
if usar_mlg_para_proteina_email:
    nota_mlg_email += "\n     ℹ️ En alta adiposidad, usar peso total infla proteína; por eso se usa MLG"

# ==================== EMAIL: COMPARATIVA DE PLANES ====================
tabla_resumen += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 6: PLAN NUTRICIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Prescripción nutricional basada en gasto energético y objetivos.

🎯 6.1 DIAGNÓSTICO Y FASE:
   • Fase recomendada: {fase}
   • Factor FBEO: {fbeo:.2f}
   • Ingesta calórica objetivo: {ingesta_calorica:.0f} kcal/día
   • Ratio kcal/kg: {ratio_kcal_kg:.1f}

📊 6.2 PLAN TRADICIONAL (Déficit/Superávit Moderado):

   ┌─────────────────────────────────────────────────────────────────┐
   │ CALORÍAS: {plan_tradicional_calorias:.0f} kcal/día                                   │
   │ ESTRATEGIA: {fase}                                      │
   ├─────────────────────────────────────────────────────────────────┤
   │ MACRONUTRIENTES:                                               │
   │ • Proteína: {proteina_g_tradicional:.1f}g ({proteina_kcal_tradicional:.0f} kcal) = {proteina_kcal_tradicional/plan_tradicional_calorias*100 if plan_tradicional_calorias > 0 else 0:.1f}%{nota_mlg_email}                │
   │ • Grasas: {grasa_g_tradicional:.1f}g ({grasa_kcal_tradicional:.0f} kcal) = {grasa_kcal_tradicional/plan_tradicional_calorias*100 if plan_tradicional_calorias > 0 else 0:.1f}%                        │
   │ • Carbohidratos: {carbo_g_tradicional:.1f}g ({carbo_kcal_tradicional:.0f} kcal) = {carbo_kcal_tradicional/plan_tradicional_calorias*100 if plan_tradicional_calorias > 0 else 0:.1f}%                 │
   ├─────────────────────────────────────────────────────────────────┤
   │ • Sostenibilidad: ALTA                                         │
   │ • Cambio esperado: 0.3-0.7% peso corporal/semana               │
   │ • Duración: Indefinida con ajustes periódicos                  │
   └─────────────────────────────────────────────────────────────────┘"""

if plan_psmf_disponible:
    macros_psmf_email = calcular_macros_psmf(psmf_recs)
    proteina_g_psmf = macros_psmf_email['proteina_g']
    proteina_kcal_psmf = macros_psmf_email['proteina_kcal']
    grasa_g_psmf = macros_psmf_email['grasa_g']
    grasa_kcal_psmf = macros_psmf_email['grasa_kcal']
    carbo_g_psmf = macros_psmf_email['carbo_g']
    carbo_kcal_psmf = macros_psmf_email['carbo_kcal']
    calorias_dia_psmf = macros_psmf_email['calorias_dia']
    
    tabla_resumen += f"""

⚡ 6.3 PROTOCOLO PSMF (APLICABLE):

   ┌─────────────────────────────────────────────────────────────────┐
   │ CALORÍAS: {calorias_dia_psmf:.0f} kcal/día                                     │
   │ CRITERIO: {psmf_recs.get('criterio', 'No especificado')}                               │
   ├─────────────────────────────────────────────────────────────────┤
   │ MACRONUTRIENTES:                                               │
   │ • Proteína: {proteina_g_psmf:.1f}g ({proteina_kcal_psmf:.0f} kcal) = {proteina_kcal_psmf/calorias_dia_psmf*100 if calorias_dia_psmf > 0 else 0:.1f}%                       │
   │ • Grasas: {grasa_g_psmf:.1f}g ({grasa_kcal_psmf:.0f} kcal) = {grasa_kcal_psmf/calorias_dia_psmf*100 if calorias_dia_psmf > 0 else 0:.1f}%                          │
   │ • Carbohidratos: {carbo_g_psmf:.1f}g ({carbo_kcal_psmf:.0f} kcal) = {carbo_kcal_psmf/calorias_dia_psmf*100 if calorias_dia_psmf > 0 else 0:.1f}% (vegetales fibrosos)  │
   ├─────────────────────────────────────────────────────────────────┤
   │ • Multiplicador: {psmf_recs.get('multiplicador', 8.3)} (perfil: {psmf_recs.get('perfil_grasa', 'alto % grasa')})               │
   │ • Déficit: ~{int((1 - calorias_dia_psmf/(GE if 'GE' in locals() else 2000)) * 100) if calorias_dia_psmf > 0 else 0}%                                                │
   │ • Pérdida esperada: {psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[0]}-{psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[1]} kg/semana                        │
   │ • Sostenibilidad: BAJA (máx 6-8 semanas)                       │
   │ • Suplementación: Multivitamínico, omega-3, electrolitos, Mg   │
   │ • ⚠️ Requiere supervisión médica y análisis de sangre         │
   └─────────────────────────────────────────────────────────────────┘"""
else:
    tabla_resumen += f"""

⚡ 6.3 PROTOCOLO PSMF (NO APLICABLE):
   • Razón: % grasa no cumple criterios mínimos
   • Criterio H: >18% | M: >23% (actual: {grasa_corregida:.1f}%)
   • Recomendación: Usar plan tradicional"""

tabla_resumen += f"""

📋 6.4 COMPARATIVA DE ESTRATEGIAS:
   • Disponibilidad: {'Ambos aplicables' if plan_psmf_disponible else 'Solo tradicional'}
   • Velocidad: {'PSMF 2-3x más rápido' if plan_psmf_disponible else 'Tradicional = moderada'}
   • Riesgo muscular: {'PSMF = mayor' if plan_psmf_disponible else 'Tradicional = mínimo'}
   • Adherencia: {'Tradicional >> PSMF' if plan_psmf_disponible else 'Tradicional = alta'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 7: PROYECCIÓN A 6 SEMANAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PROYECCIÓN CIENTÍFICA:

   • Objetivo: {porcentaje_valor:+.0f}% {objetivo_texto}
   • Rango semanal: {proyeccion_email['rango_semanal_pct'][0]:.1f}% a {proyeccion_email['rango_semanal_pct'][1]:.1f}% del peso corporal
   • Cambio semanal: {proyeccion_email['rango_semanal_kg'][0]:+.2f} a {proyeccion_email['rango_semanal_kg'][1]:+.2f} kg/semana
   • Cambio total (6 sem): {proyeccion_email['rango_total_6sem_kg'][0]:+.2f} a {proyeccion_email['rango_total_6sem_kg'][1]:+.2f} kg

   ╔════════════════════════════════════════════════════════════════╗
   ║  PESO ACTUAL: {peso:.1f} kg                                       ║
   ║  PESO PROYECTADO: {peso + proyeccion_email['rango_total_6sem_kg'][0]:.1f} a {peso + proyeccion_email['rango_total_6sem_kg'][1]:.1f} kg                         ║
   ╚════════════════════════════════════════════════════════════════╝

   📝 Explicación: {proyeccion_email['explicacion_textual']}"""

# ==================== METAS PERSONALES (si disponible) ====================
if st.session_state.get('metas_personales_completado', False):
    metas_texto = st.session_state.metas_personales
    
    tabla_resumen += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 8: METAS PERSONALES DEL CLIENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OBJETIVOS AUTODECLARADOS:
{metas_texto}

📋 CONSIDERACIONES:
   • Establecer hitos intermedios medibles
   • Ajustar plazos según respuesta individual
   • Adherencia y consistencia son clave"""

tabla_resumen += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECCIÓN 9: RECOMENDACIONES Y ADVERTENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 9.1 SUPLEMENTACIÓN RECOMENDADA:
   • Creatina monohidrato: 5g/día
   • Vitamina D3: 2000-4000 UI/día
   • Omega-3 (EPA+DHA): 2-3g/día
   • Multivitamínico: 1/día
{'   • ADICIONAL PSMF: Electrolitos, magnesio, complejo B' if plan_psmf_disponible else ''}

💧 9.2 HIDRATACIÓN:
   • Mínimo recomendado: {peso * 35 if 'peso' in locals() and peso > 0 else 2450:.0f} ml/día (35ml/kg)

📈 9.3 MÉTRICAS DE SEGUIMIENTO:
   • Peso: Diario (misma hora y condiciones)
   • Medidas: Semanal (cintura, cadera, brazos)
   • Fotos: Bisemanal (misma iluminación/pose)
   • Rendimiento: Cada sesión (cargas/repeticiones)
   • Energía: Diario (escala 1-10)

🎯 9.4 RECOMENDACIONES ESPECÍFICAS:
   • Reevaluación: Cada 2-3 semanas
   • Enfoque: {'Pérdida de grasa manteniendo músculo' if porcentaje_email < 0 else 'Ganancia muscular controlada' if porcentaje_email > 0 else 'Recomposición corporal'}
   • Timing: Proteína en cada comida, carbos pre/post entreno
   • Descanso: 7-9 horas/noche

⚠️ 9.5 ADVERTENCIAS IMPORTANTES:

   ┌─────────────────────────────────────────────────────────────────┐
   │ • Este análisis es herramienta de apoyo, NO sustituye          │
   │   supervisión profesional                                      │
   │ • Cálculos basados en ecuaciones validadas, pero la            │
   │   respuesta individual varía                                   │
   │ • Se recomienda evaluación médica antes de planes restrictivos │
{'   │ • PSMF: Supervisión médica OBLIGATORIA                         │' if plan_psmf_disponible else ''}
   └─────────────────────────────────────────────────────────────────┘

   NATURALEZA DE LAS ESTIMACIONES:
   El cuerpo humano es un sistema complejo, no lineal y dinámico.
   Los resultados dependen de: adherencia, sueño, estrés, respuesta
   individual, factores hormonales/genéticos, actividad no planificada.

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    © 2025 MUPAI - Muscle Up GYM                               ║
║                       Digital Training Science                                ║
║                        muscleupgym.fitness                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# ==================== RESUMEN PERSONALIZADO ====================
# Solo mostrar si los datos están completos para la evaluación
if st.session_state.datos_completos and 'peso' in locals() and peso > 0:
    st.markdown("---")
    st.markdown("""
    <div class="content-card" style="background: linear-gradient(135deg, #1E1E1E 0%, #232425 100%); border-left: 4px solid var(--mupai-yellow);">
        <h2 style="color: var(--mupai-yellow); text-align: center; margin-bottom: 2rem;">
            🎯 Resumen Personalizado y Proyección
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Categorizar grasa corporal
    if sexo == "Hombre":
        if grasa_corregida < 6:
            categoria_grasa = "Muy bajo (Competición)"
            color_categoria = "#E74C3C"
        elif grasa_corregida < 12:
            categoria_grasa = "Atlético"
            color_categoria = "#27AE60"
        elif grasa_corregida < 18:
            categoria_grasa = "Fitness"
            color_categoria = "#F39C12"
        elif grasa_corregida < 25:
            categoria_grasa = "Promedio"
            color_categoria = "#3498DB"
        else:
            categoria_grasa = "Alto"
            color_categoria = "#E74C3C"
    else:  # Mujer
        if grasa_corregida < 12:
            categoria_grasa = "Muy bajo (Competición)"
            color_categoria = "#E74C3C"
        elif grasa_corregida < 17:
            categoria_grasa = "Atlético"
            color_categoria = "#27AE60"
        elif grasa_corregida < 23:
            categoria_grasa = "Fitness"
            color_categoria = "#F39C12"
        elif grasa_corregida < 30:
            categoria_grasa = "Promedio"
            color_categoria = "#3498DB"
        else:
            categoria_grasa = "Alto"
            color_categoria = "#E74C3C"
    
    # Usar proyección científica realista
    peso_actual = peso if peso > 0 else 70  # Fallback si no hay peso
    
    # Determinar el porcentaje correcto según el plan elegido usando función centralizada
    porcentaje_for_projection = obtener_porcentaje_para_proyeccion(
        plan_elegido if 'plan_elegido' in locals() else "",
        psmf_recs if 'psmf_recs' in locals() else {},
        GE if 'GE' in locals() else 0,
        porcentaje if 'porcentaje' in locals() else 0
    )
    
    # Calcular proyección científica
    proyeccion = calcular_proyeccion_cientifica(
        sexo, 
        grasa_corregida, 
        nivel_entrenamiento if 'nivel_entrenamiento' in locals() else 'intermedio',
        peso_actual, 
        porcentaje_for_projection
    )
    
    # Determinar tipo de cambio y dirección
    if porcentaje_for_projection < 0:  # Déficit (pérdida) - valor negativo
        tipo_cambio = "pérdida"
        direccion = "-"
    elif porcentaje_for_projection > 0:  # Superávit (ganancia) - valor positivo
        tipo_cambio = "ganancia"
        direccion = "+"
    else:  # Mantenimiento
        tipo_cambio = "mantenimiento"
        direccion = ""
    
    # Usar el rango medio para la proyección visual
    cambio_semanal_medio = (proyeccion['rango_semanal_kg'][0] + proyeccion['rango_semanal_kg'][1]) / 2
    cambio_6_semanas_medio = (proyeccion['rango_total_6sem_kg'][0] + proyeccion['rango_total_6sem_kg'][1]) / 2
    peso_proyectado = peso_actual + cambio_6_semanas_medio
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="content-card" style="background: #1A1A1A;">
            <h3 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">📊 Diagnóstico Personalizado</h3>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Categoría de Grasa Corporal:</strong><br>
                <span style="color: {color_categoria}; font-weight: bold; font-size: 1.1rem;">{categoria_grasa}</span>
                <span style="color: #999999;"> ({grasa_corregida:.1f}%)</span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Nivel de Entrenamiento:</strong><br>
                <span style="color: var(--mupai-yellow); font-weight: bold;">{nivel_entrenamiento.capitalize() if 'nivel_entrenamiento' in locals() else 'Intermedio'}</span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Objetivo Recomendado:</strong><br>
                <span style="color: #27AE60; font-weight: bold;">{fase}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="content-card" style="background: #1A1A1A;">
            <h3 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">📈 Proyección Científica 6 Semanas</h3>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Rango Semanal Científico:</strong><br>
                <span style="color: {'#27AE60' if direccion == '+' else '#E74C3C' if direccion == '-' else '#3498DB'}; font-weight: bold; font-size: 1.1rem;">
                    {proyeccion['rango_semanal_pct'][0]:.1f}% a {proyeccion['rango_semanal_pct'][1]:.1f}% del peso corporal
                </span><br>
                <span style="color: #999999; font-size: 0.9rem;">
                    ({proyeccion['rango_semanal_kg'][0]:+.2f} a {proyeccion['rango_semanal_kg'][1]:+.2f} kg/semana)
                </span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Peso Actual → Rango Proyectado:</strong><br>
                <span style="color: #CCCCCC; font-size: 1.1rem;">{peso_actual:.1f} kg → </span>
                <span style="color: var(--mupai-yellow); font-weight: bold; font-size: 1.1rem;">
                    {peso_actual + proyeccion['rango_total_6sem_kg'][0]:.1f} a {peso_actual + proyeccion['rango_total_6sem_kg'][1]:.1f} kg
                </span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #CCCCCC;">Cambio Total Estimado:</strong><br>
                <span style="color: {'#27AE60' if direccion == '+' else '#E74C3C' if direccion == '-' else '#3498DB'}; font-weight: bold; font-size: 1.1rem;">
                    {proyeccion['rango_total_6sem_kg'][0]:+.2f} a {proyeccion['rango_total_6sem_kg'][1]:+.2f} kg en 6 semanas
                </span>
            </div>
            <div style="margin-bottom: 0;">
                <strong style="color: #CCCCCC;">Explicación Científica:</strong><br>
                <span style="color: #CCCCCC; font-size: 0.9rem; line-height: 1.4;">
                    {proyeccion['explicacion_textual']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Nota aclaratoria
    st.markdown("""
    <div class="content-card" style="background: #252525; border-left: 4px solid #F39C12;">
        <h4 style="color: #F39C12; margin-bottom: 1rem;">⚠️ Importante: Naturaleza de las Estimaciones</h4>
        <p style="color: #CCCCCC; line-height: 1.6; margin-bottom: 0;">
            <strong>Estas son estimaciones basadas en modelos científicos.</strong> El cuerpo humano es un sistema complejo, 
            no lineal y dinámico. Los resultados reales dependerán de múltiples factores como:
        </p>
        <ul style="color: #CCCCCC; margin: 1rem 0; line-height: 1.6;">
            <li>Adherencia estricta al plan nutricional y de entrenamiento</li>
            <li>Calidad del sueño y gestión del estrés</li>
            <li>Respuesta individual y adaptaciones metabólicas</li>
            <li>Factores hormonales y genéticos</li>
            <li>Variaciones en la actividad diaria no planificada</li>
        </ul>
        <p style="color: #CCCCCC; line-height: 1.6; margin-bottom: 0;">
            <strong>Recomendación:</strong> Utiliza estas proyecciones como guía inicial y ajusta según tu progreso real. 
            Se recomienda evaluación periódica cada 2-3 semanas para optimizar resultados.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- Personal Goals Section (placed before progress photos) ---
resultado_metas_personales = formulario_metas_personales()

# --- Progress Photos Section (placed before final submission) ---
render_progress_photos_section()

# --- Botón para enviar email (solo si no se ha enviado y todo completo) ---
if not st.session_state.get("correo_enviado", False):
    # Check if all required fields are complete before showing the button
    faltantes = datos_completos_para_email()
    
    # Show button but disable if fields are missing
    button_disabled = len(faltantes) > 0
    
    if st.button("📧 Enviar Resumen por Email", key="enviar_email", disabled=button_disabled, 
                 help="Completa todos los campos requeridos para habilitar el envío" if button_disabled else "Enviar resumen por email"):
        # Double-check validation before sending
        faltantes = datos_completos_para_email()
        if faltantes:
            # Show detailed error message with all missing fields
            st.error("❌ **No se puede enviar el resumen. Por favor completa los siguientes campos obligatorios:**")
            for campo_faltante in faltantes:
                st.markdown(f"- ❌ **{campo_faltante}**")
            st.warning("⚠️ Revisa el formulario arriba y completa todos los campos requeridos, luego intenta enviar nuevamente.")
        else:
            with st.spinner("📧 Enviando resumen por email..."):
                # Get progress photos from session state
                progress_photos = st.session_state.get("progress_photos", {})
                
                # Definir variables opcionales para evitar errores de Pylance
                wthr = None
                GEAF = None
                proyecciones = None
                
                # Calcular wthr si tenemos circunferencia_cintura
                if 'circunferencia_cintura' in locals() and circunferencia_cintura and circunferencia_cintura > 0 and estatura > 0:
                    wthr = circunferencia_cintura / estatura
                
                # Enviar email completo a administración
                ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono, progress_photos)
                
                # Calcular FFMI antes de enviar (asegurar que siempre existe)
                ffmi_para_email = calcular_ffmi(mlg, estatura) if 'ffmi' not in locals() or ffmi is None else ffmi
                
                # Recuperar masa muscular original del aparato (dato ingresado por usuario)
                masa_muscular_aparato = st.session_state.get('masa_muscular', 0)
                
                # Calcular masa muscular estimada científicamente
                masa_muscular_estimada_email = estimar_masa_muscular_desde_mlg(
                    mlg, 
                    sexo, 
                    nivel_entrenamiento if 'nivel_entrenamiento' in locals() else 'intermedio'
                )
                
                # Enviar reporte de evaluación corporal completo al cliente
                ok_cliente = enviar_email_cliente(
                    nombre, email_cliente, fecha_llenado, edad, sexo, peso, estatura, imc,
                    grasa_corregida, mlg, 
                    ffmi_para_email,  # Siempre enviamos FFMI calculado
                    nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None,
                    circunferencia_cintura if 'circunferencia_cintura' in locals() else None,
                    grasa_visceral if 'grasa_visceral' in locals() else None,
                    edad_metabolica if 'edad_metabolica' in locals() else None,
                    wthr if 'wthr' in locals() else None,
                    peso - mlg,  # masa_grasa
                    progress_photos,
                    masa_muscular_aparato,  # Masa muscular del Omron
                    masa_muscular_estimada_email  # Masa muscular estimada
                )
                
                if ok:
                    st.session_state["correo_enviado"] = True
                    st.success("✅ Email completo enviado exitosamente a administración")
                    
                    if ok_cliente:
                        st.success(f"✅ Reporte de evaluación enviado exitosamente a {email_cliente}")
                    else:
                        st.warning(f"⚠️ Email a administración enviado, pero hubo un error al enviar el reporte al cliente ({email_cliente})")
                    
                    # Enviar email Parte 2 (interno) con TODO EL CONTENIDO del email cliente
                    ok_parte2 = enviar_email_parte2(
                        nombre, fecha_llenado, edad, sexo, peso, estatura, imc,
                        grasa_corregida, mlg,
                        ffmi_para_email,  # FFMI completo
                        nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None,
                        circunferencia_cintura if 'circunferencia_cintura' in locals() else None,
                        grasa_visceral if 'grasa_visceral' in locals() else None,
                        edad_metabolica if 'edad_metabolica' in locals() else None,
                        wthr if 'wthr' in locals() else None,
                        peso - mlg,  # masa_grasa
                        progress_photos,
                        masa_muscular_aparato,  # Masa muscular del Omron
                        masa_muscular_estimada_email,  # Masa muscular estimada
                        masa_muscular if 'masa_muscular' in locals() else None,  # Fallback legacy
                        tmb if 'tmb' in locals() else None,  # TMB
                        st.session_state.get('ciclo_menstrual')
                    )
                    if ok_parte2:
                        st.success("✅ Reporte interno (Parte 2) enviado exitosamente")
                    else:
                        st.warning("⚠️ Emails enviados, pero hubo un error con el reporte interno")
                    
                    # Construir diccionario completo para email YAML
                    datos_completos_yaml = {
                        'nombre_cliente': nombre,  # Para compatibilidad
                        'fecha': fecha_llenado,  # Para compatibilidad
                        'metadata': {
                            'fecha_evaluacion': fecha_llenado,
                            'sistema': 'MUPAI v2.0',
                            'version': '2.0.0',
                            'tipo_reporte': 'Evaluacion_Completa'
                        },
                        'datos_personales': {
                            'nombre_cliente': nombre,
                            'email': email_cliente,
                            'telefono': telefono if 'telefono' in locals() else None,
                            'edad': edad,
                            'sexo': sexo,
                            'ciclo_menstrual': st.session_state.get('ciclo_menstrual')
                        },
                        'composicion_corporal': {
                            'peso_kg': float(peso),
                            'estatura_cm': float(estatura),
                            'imc': float(imc),
                            'grasa_corporal_pct': float(grasa_corregida),
                            'mlg_kg': float(mlg),
                            'masa_grasa_kg': float(peso - mlg),
                            'circunferencia_cintura_cm': float(circunferencia_cintura) if 'circunferencia_cintura' in locals() and circunferencia_cintura else None,
                            'masa_muscular_omron_kg': float(masa_muscular_aparato) if masa_muscular_aparato > 0 else None,
                            'masa_muscular_estimada_kg': float(masa_muscular_estimada_email),
                        },
                        'indices_corporales': {
                            'ffmi': float(ffmi_para_email) if ffmi_para_email else None,
                            'wthr': float(wthr) if 'wthr' in locals() and wthr else None,
                            'grasa_visceral_nivel': int(grasa_visceral) if 'grasa_visceral' in locals() and grasa_visceral else None,
                            'edad_metabolica': int(edad_metabolica) if 'edad_metabolica' in locals() and edad_metabolica else None,
                            'nivel_entrenamiento': nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None
                        },
                        'metabolismo': {
                            'tmb_kcal': float(tmb) if 'tmb' in locals() else None,
                            'ge_kcal': float(GE) if 'GE' in locals() else None,
                            'geaf': float(GEAF) if 'GEAF' in locals() else None
                        },
                        'macronutrientes_tradicionales': {
                            'proteina_g': float(proteina_g) if 'proteina_g' in locals() else None,
                            'proteina_kcal': float(proteina_kcal) if 'proteina_kcal' in locals() else None,
                            'grasa_g': float(grasa_g) if 'grasa_g' in locals() else None,
                            'grasa_kcal': float(grasa_kcal) if 'grasa_kcal' in locals() else None,
                            'carbohidratos_g': float(carbo_g) if 'carbo_g' in locals() else None,
                            'carbohidratos_kcal': float(carbo_kcal) if 'carbo_kcal' in locals() else None,
                            'calorias_totales': float(ingesta_calorica) if 'ingesta_calorica' in locals() else None,
                            'base_proteina': base_proteina_nombre if 'base_proteina_nombre' in locals() else None,
                            'factor_proteina': float(factor_proteina) if 'factor_proteina' in locals() else None
                        },
                        'plan_psmf': {
                            'aplicable': psmf_recs.get('psmf_aplicable', False) if 'psmf_recs' in locals() else False,
                            'proteina_g': float(psmf_recs.get('proteina_g_dia', 0)) if 'psmf_recs' in locals() else None,
                            'grasa_g': float(psmf_recs.get('grasa_g_dia', 0)) if 'psmf_recs' in locals() else None,
                            'carbohidratos_g': float(psmf_recs.get('carbs_g_dia', 0)) if 'psmf_recs' in locals() else None,
                            'calorias_dia': float(psmf_recs.get('calorias_dia', 0)) if 'psmf_recs' in locals() else None,
                            'tier': psmf_recs.get('tier', None) if 'psmf_recs' in locals() else None
                        },
                        'proyecciones': {
                            '1_mes': proyecciones[0] if 'proyecciones' in locals() and len(proyecciones) > 0 else None,
                            '2_meses': proyecciones[1] if 'proyecciones' in locals() and len(proyecciones) > 1 else None,
                            '3_meses': proyecciones[2] if 'proyecciones' in locals() and len(proyecciones) > 2 else None
                        },
                        'recuperacion': {
                            'suenyo_estres_completado': st.session_state.get('suenyo_estres_completado', False),
                            'ir_se': st.session_state.get('suenyo_estres_data', {}).get('ir_se', None),
                            'nivel_recuperacion': st.session_state.get('suenyo_estres_data', {}).get('nivel_recuperacion', None),
                            'sleep_score': st.session_state.get('suenyo_estres_data', {}).get('sleep_score', None),
                            'stress_score': st.session_state.get('suenyo_estres_data', {}).get('stress_score', None)
                        }
                    }
                    
                    # Enviar email con datos en formato YAML
                    ok_yaml = enviar_email_yaml(datos_completos_yaml)
                    if ok_yaml:
                        st.success("✅ Reporte YAML enviado exitosamente (para ChatGPT/análisis)")
                    else:
                        st.warning("⚠️ Emails principales enviados, pero hubo un error con el reporte YAML")
                else:
                    st.error("❌ Error al enviar email. Contacta a soporte técnico.")
    
    # Show validation status above the button
    if faltantes:
        st.warning(f"⚠️ **Faltan {len(faltantes)} campo(s) obligatorio(s) por completar:**")
        for campo_faltante in faltantes:
            st.markdown(f"- 📝 **{campo_faltante}**")
        st.info("💡 **Tip:** Completa todos los campos del cuestionario para poder enviar el resumen.")
else:
    st.info("✅ El resumen ya fue enviado por email. Si requieres reenviarlo, refresca la página o usa el botón de 'Reenviar Email'.")

# --- Opción para reenviar manualmente (opcional) ---
faltantes_reenvio = datos_completos_para_email()
button_reenvio_disabled = len(faltantes_reenvio) > 0

if st.button("📧 Reenviar Email", key="reenviar_email", disabled=button_reenvio_disabled,
             help="Completa todos los campos requeridos para habilitar el reenvío" if button_reenvio_disabled else "Reenviar resumen por email"):
    faltantes = datos_completos_para_email()
    if faltantes:
        # Show detailed error message with all missing fields
        st.error("❌ **No se puede reenviar el resumen. Por favor completa los siguientes campos obligatorios:**")
        for campo_faltante in faltantes:
            st.markdown(f"- ❌ **{campo_faltante}**")
        st.warning("⚠️ Revisa el formulario arriba y completa todos los campos requeridos, luego intenta enviar nuevamente.")
    else:
        with st.spinner("📧 Reenviando resumen por email..."):
            # Get progress photos from session state
            progress_photos = st.session_state.get("progress_photos", {})
            
            # Reenviar email completo a administración
            ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono, progress_photos)
            
            # Reenviar reporte de evaluación corporal completo al cliente
            ok_cliente = enviar_email_cliente(
                nombre, email_cliente, fecha_llenado, edad, sexo, peso, estatura, imc,
                grasa_corregida, mlg,
                ffmi if 'ffmi' in locals() else None,
                nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None,
                circunferencia_cintura if 'circunferencia_cintura' in locals() else None,
                grasa_visceral if 'grasa_visceral' in locals() else None,
                edad_metabolica if 'edad_metabolica' in locals() else None,
                wthr if 'wthr' in locals() else None,
                peso - mlg,  # masa_grasa
                progress_photos
            )
            
            if ok:
                st.session_state["correo_enviado"] = True
                st.success("✅ Email completo reenviado exitosamente a administración")
                
                if ok_cliente:
                    st.success(f"✅ Reporte de evaluación reenviado exitosamente a {email_cliente}")
                else:
                    st.warning(f"⚠️ Email a administración reenviado, pero hubo un error al reenviar el reporte al cliente ({email_cliente})")
                
                # Reenviar email Parte 2 (interno)
                ok_parte2 = enviar_email_parte2(
                    nombre, fecha_llenado, edad, sexo, peso, estatura, imc,
                    grasa_corregida, mlg,
                    ffmi_para_email,  # FFMI completo
                    nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None,
                    circunferencia_cintura if 'circunferencia_cintura' in locals() else None,
                    grasa_visceral if 'grasa_visceral' in locals() else None,
                    edad_metabolica if 'edad_metabolica' in locals() else None,
                    wthr if 'wthr' in locals() else None,
                    peso - mlg,  # masa_grasa
                    progress_photos,
                    masa_muscular_aparato,  # Masa muscular del Omron
                    masa_muscular_estimada_email,  # Masa muscular estimada
                    masa_muscular if 'masa_muscular' in locals() else None,  # Fallback legacy
                    tmb if 'tmb' in locals() else None,  # TMB
                    st.session_state.get('ciclo_menstrual')
                )
                if ok_parte2:
                    st.success("✅ Reporte interno (Parte 2) reenviado exitosamente")
                else:
                    st.warning("⚠️ Emails reenviados, pero hubo un error con el reporte interno")
                
                # Construir y reenviar email YAML
                datos_completos_yaml_reenvio = {
                    'metadata': {
                        'fecha_evaluacion': fecha_llenado,
                        'sistema': 'MUPAI v2.0',
                        'version': '2.0.0',
                        'tipo_reporte': 'Evaluacion_Completa_Reenvio'
                    },
                    'datos_personales': {
                        'nombre_cliente': nombre,
                        'email': email_cliente,
                        'telefono': telefono if 'telefono' in locals() else None,
                        'edad': edad,
                        'sexo': sexo,
                        'ciclo_menstrual': st.session_state.get('ciclo_menstrual')
                    },
                    'composicion_corporal': {
                        'peso_kg': float(peso),
                        'estatura_cm': float(estatura),
                        'imc': float(imc),
                        'grasa_corporal_pct': float(grasa_corregida),
                        'mlg_kg': float(mlg),
                        'masa_grasa_kg': float(peso - mlg),
                        'circunferencia_cintura_cm': float(circunferencia_cintura) if 'circunferencia_cintura' in locals() and circunferencia_cintura else None,
                        'masa_muscular_omron_kg': float(masa_muscular_aparato) if masa_muscular_aparato > 0 else None,
                        'masa_muscular_estimada_kg': float(masa_muscular_estimada_email),
                    },
                    'indices_corporales': {
                        'ffmi': float(ffmi_para_email) if ffmi_para_email else None,
                        'wthr': float(wthr) if 'wthr' in locals() and wthr else None,
                        'grasa_visceral_nivel': int(grasa_visceral) if 'grasa_visceral' in locals() and grasa_visceral else None,
                        'edad_metabolica': int(edad_metabolica) if 'edad_metabolica' in locals() and edad_metabolica else None,
                        'nivel_entrenamiento': nivel_entrenamiento if 'nivel_entrenamiento' in locals() else None
                    },
                    'metabolismo': {
                        'tmb_kcal': float(tmb) if 'tmb' in locals() else None,
                        'ge_kcal': float(GE) if 'GE' in locals() else None,
                        'geaf': float(GEAF) if 'GEAF' in locals() else None
                    },
                    'macronutrientes_tradicionales': {
                        'proteina_g': float(proteina_g) if 'proteina_g' in locals() else None,
                        'proteina_kcal': float(proteina_kcal) if 'proteina_kcal' in locals() else None,
                        'grasa_g': float(grasa_g) if 'grasa_g' in locals() else None,
                        'grasa_kcal': float(grasa_kcal) if 'grasa_kcal' in locals() else None,
                        'carbohidratos_g': float(carbo_g) if 'carbo_g' in locals() else None,
                        'carbohidratos_kcal': float(carbo_kcal) if 'carbo_kcal' in locals() else None,
                        'calorias_totales': float(ingesta_calorica) if 'ingesta_calorica' in locals() else None,
                        'base_proteina': base_proteina_nombre if 'base_proteina_nombre' in locals() else None,
                        'factor_proteina': float(factor_proteina) if 'factor_proteina' in locals() else None
                    },
                    'plan_psmf': {
                        'aplicable': psmf_recs.get('psmf_aplicable', False) if 'psmf_recs' in locals() else False,
                        'proteina_g': float(psmf_recs.get('proteina_g_dia', 0)) if 'psmf_recs' in locals() else None,
                        'grasa_g': float(psmf_recs.get('grasa_g_dia', 0)) if 'psmf_recs' in locals() else None,
                        'carbohidratos_g': float(psmf_recs.get('carbs_g_dia', 0)) if 'psmf_recs' in locals() else None,
                        'calorias_dia': float(psmf_recs.get('calorias_dia', 0)) if 'psmf_recs' in locals() else None,
                        'tier': psmf_recs.get('tier', None) if 'psmf_recs' in locals() else None
                    },
                    'proyecciones': {
                        '1_mes': proyecciones[0] if 'proyecciones' in locals() and len(proyecciones) > 0 else None,
                        '2_meses': proyecciones[1] if 'proyecciones' in locals() and len(proyecciones) > 1 else None,
                        '3_meses': proyecciones[2] if 'proyecciones' in locals() and len(proyecciones) > 2 else None
                    },
                    'recuperacion': {
                        'suenyo_estres_completado': st.session_state.get('suenyo_estres_completado', False),
                        'ir_se': st.session_state.get('suenyo_estres_data', {}).get('ir_se', None),
                        'nivel_recuperacion': st.session_state.get('suenyo_estres_data', {}).get('nivel_recuperacion', None),
                        'sleep_score': st.session_state.get('suenyo_estres_data', {}).get('sleep_score', None),
                        'stress_score': st.session_state.get('suenyo_estres_data', {}).get('stress_score', None)
                    }
                }
                
                ok_yaml_reenvio = enviar_email_yaml(datos_completos_yaml_reenvio)
                if ok_yaml_reenvio:
                    st.success("✅ Reporte YAML reenviado exitosamente")
                else:
                    st.warning("⚠️ Emails principales reenviados, pero hubo un error con el reporte YAML")
            else:
                st.error("❌ Error al reenviar email. Contacta a soporte técnico.")

# --- Limpieza de sesión y botón de nueva evaluación ---
if st.button("🔄 Nueva Evaluación", key="nueva"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Footer moderno
st.markdown("""
<div class="footer-mupai">
    <h4>MUPAI / Muscle up GYM Performance Assessment Intelligence</h4>
    <span>Digital Training Science</span>
    <br>
    <span>© 2025 MUPAI - Muscle up GYM / MUPAI</span>
    <br>
    <a href="https://muscleupgym.fitness" target="_blank">muscleupgym.fitness</a>
</div>
""", unsafe_allow_html=True)

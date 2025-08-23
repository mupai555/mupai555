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

# ==================== FUNCIONES DE VALIDACIÓN POR PASOS ====================

def validate_step_1():
    """Valida que todos los campos del paso 1 (datos personales) estén completos."""
    nombre = st.session_state.get("nombre", "")
    telefono = st.session_state.get("telefono", "")
    email = st.session_state.get("email_cliente", "")
    acepto_terminos = st.session_state.get("acepto_terminos", False)
    
    # Realizar validaciones individuales
    name_valid, _ = validate_name(nombre)
    phone_valid, _ = validate_phone(telefono)
    email_valid, _ = validate_email(email)
    
    return name_valid and phone_valid and email_valid and acepto_terminos

def validate_step_2():
    """Valida que todos los campos del paso 2 (composición corporal) estén completos."""
    peso = st.session_state.get("peso", 0)
    estatura = st.session_state.get("estatura", 0)
    grasa_corporal = st.session_state.get("grasa_corporal", 0)
    
    return peso > 30 and estatura > 120 and grasa_corporal > 0

def validate_step_3():
    """Valida que el paso 3 (evaluación funcional) esté completo."""
    experiencia = st.session_state.get("experiencia_entrenamiento", "")
    if not experiencia or experiencia.startswith("A) He entrenado de forma irregular"):
        return False
    
    # Verificar que haya al menos un dato de ejercicio si la experiencia está completa
    has_exercise_data = False
    for key in st.session_state:
        if "reps" in key or "peso" in key:
            has_exercise_data = True
            break
    
    return True  # Para simplificar, solo validamos la experiencia

def validate_step_4():
    """Valida que el paso 4 (actividad física) esté completo."""
    actividad = st.session_state.get("actividad_diaria", "")
    return len(actividad) > 0

def validate_step_5():
    """Valida que el paso 5 (efecto térmico) esté completo."""
    eta_factor = st.session_state.get("eta_factor", 0)
    return eta_factor > 0

def validate_step_6():
    """Valida que el paso 6 (gasto energético) esté completo."""
    entrenamiento_fuerza = st.session_state.get("entrenamiento_fuerza", "")
    return len(entrenamiento_fuerza) > 0

def get_step_progress():
    """Calcula el progreso actual basado en los pasos completados."""
    current_step = st.session_state.get("current_step", 1)
    total_steps = 6
    return min((current_step - 1) * 100 / total_steps, 100)

def advance_step():
    """Avanza al siguiente paso si la validación es exitosa."""
    current_step = st.session_state.get("current_step", 1)
    
    # Validar el paso actual antes de avanzar
    if current_step == 1 and validate_step_1():
        st.session_state.step_1_complete = True
        st.session_state.current_step = 2
    elif current_step == 2 and validate_step_2():
        st.session_state.step_2_complete = True
        st.session_state.current_step = 3
    elif current_step == 3 and validate_step_3():
        st.session_state.step_3_complete = True
        st.session_state.current_step = 4
    elif current_step == 4 and validate_step_4():
        st.session_state.step_4_complete = True
        st.session_state.current_step = 5
    elif current_step == 5 and validate_step_5():
        st.session_state.step_5_complete = True
        st.session_state.current_step = 6
    elif current_step == 6 and validate_step_6():
        st.session_state.step_6_complete = True
        st.session_state.questionnaire_complete = True
        st.session_state.current_step = 7
    
    return st.session_state.current_step

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
    color: #FFF !important;
    border: 2px solid var(--mupai-yellow);
    font-size: 1.16rem;
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
/* ==================== ESTILOS PARA NAVEGACIÓN POR PASOS ==================== */
.step-header {
    background: linear-gradient(135deg, var(--mupai-black) 0%, #2A2A2A 100%);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    border: 2px solid var(--mupai-yellow);
    text-align: center;
    animation: fadeIn 0.6s ease-out;
}
.step-title {
    color: var(--mupai-yellow);
    font-size: 1.8rem;
    font-weight: 900;
    margin: 0 0 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
.step-subtitle {
    color: #F5F5F5;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
}
.next-button {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: var(--mupai-black);
    border: none;
    padding: 1rem 3rem;
    font-weight: 900;
    border-radius: 50px;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(244, 196, 48, 0.25);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 1.2rem;
    margin: 2rem 0 1rem 0;
    cursor: pointer;
}
.next-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(244, 196, 48, 0.35);
    filter: brightness(1.05);
}
.next-button:disabled {
    background: #555555;
    color: #888888;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
}
.step-motivation {
    background: linear-gradient(135deg, var(--mupai-success) 0%, #27AE60 100%);
    color: white;
    padding: 1.2rem 2rem;
    border-radius: 12px;
    text-align: center;
    margin: 1.5rem 0;
    font-weight: 700;
    font-size: 1.1rem;
    animation: slideIn 0.5s ease-out;
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.2);
}
.step-validation-error {
    background: linear-gradient(135deg, var(--mupai-danger) 0%, #C0392B 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    font-weight: 600;
    animation: slideIn 0.4s ease-out;
}
.progress-container {
    background: #1E1E1E;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    border: 1px solid #333;
    position: sticky;
    top: 10px;
    z-index: 100;
}
.progress-text {
    color: var(--mupai-yellow);
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.completion-card {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: var(--mupai-black);
    padding: 3rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(244, 196, 48, 0.3);
    animation: fadeIn 0.8s ease-out;
}
.completion-card h1 {
    color: var(--mupai-black);
    font-size: 2.5rem;
    font-weight: 900;
    margin: 0 0 1rem 0;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.completion-card p {
    color: var(--mupai-black);
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)
# Header principal visual con logos
import base64

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
    "current_step": 1,  # Control de pasos del cuestionario
    "step_1_complete": False,  # Datos personales
    "step_2_complete": False,  # Composición corporal
    "step_3_complete": False,  # Evaluación funcional
    "step_4_complete": False,  # Actividad física
    "step_5_complete": False,  # Efecto térmico
    "step_6_complete": False,  # Gasto energético ejercicio
    "questionnaire_complete": False  # Cuestionario completado
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================== SISTEMA DE AUTENTICACIÓN ====================
ADMIN_PASSWORD = "MUPAI2025"  # Contraseña predefinida

# Si no está autenticado, mostrar login
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
        # ==================== VISUALES INICIALES ====================

# ==================== SISTEMA DE NAVEGACIÓN POR PASOS ====================

# Progreso general y navegación
current_step = st.session_state.get("current_step", 1)
total_steps = 6

# Contenedor de progreso fijo
st.markdown("""
<div class="progress-container">
    <div class="progress-text">
        📊 Progreso del Cuestionario MUPAI
    </div>
</div>
""", unsafe_allow_html=True)

# Barra de progreso
progress_value = get_step_progress()
progress_bar = st.progress(progress_value / 100)
progress_text = st.empty()

# Actualizar texto de progreso
step_names = {
    1: "Datos Personales",
    2: "Composición Corporal", 
    3: "Evaluación Funcional",
    4: "Actividad Física",
    5: "Efecto Térmico",
    6: "Gasto Energético",
    7: "Resultados Finales"
}

if current_step <= 6:
    progress_text.markdown(f"""
    <div style="text-align: center; color: var(--mupai-yellow); font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem;">
        🚀 Paso {current_step} de {total_steps}: {step_names[current_step]}
    </div>
    """, unsafe_allow_html=True)
else:
    progress_text.markdown(f"""
    <div style="text-align: center; color: var(--mupai-success); font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem;">
        🎉 ¡Cuestionario Completado! - {step_names[7]}
    </div>
    """, unsafe_allow_html=True)

# ==================== PASO 1: DATOS PERSONALES ====================
if current_step == 1:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">👤 Paso 1: Información Personal</h1>
        <p class="step-subtitle">Comparte tus datos básicos para personalizar tu evaluación</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input(
            "Nombre completo*", 
            value=st.session_state.get("nombre", ""),
            placeholder="Ej: Juan Pérez García", 
            help="Tu nombre legal completo",
            key="nombre"
        )
        telefono = st.text_input(
            "Teléfono*", 
            value=st.session_state.get("telefono", ""),
            placeholder="Ej: 8661234567", 
            help="10 dígitos sin espacios",
            key="telefono"
        )
        email_cliente = st.text_input(
            "Email*", 
            value=st.session_state.get("email_cliente", ""),
            placeholder="correo@ejemplo.com", 
            help="Email válido para recibir resultados",
            key="email_cliente"
        )

    with col2:
        edad = st.number_input(
            "Edad (años)*", 
            min_value=15, 
            max_value=80, 
            value=safe_int(st.session_state.get("edad", 25), 25), 
            help="Tu edad actual",
            key="edad"
        )
        sexo = st.selectbox(
            "Sexo biológico*", 
            ["Hombre", "Mujer"], 
            index=0 if st.session_state.get("sexo", "Hombre") == "Hombre" else 1,
            help="Necesario para cálculos precisos",
            key="sexo"
        )
        fecha_llenado = datetime.now().strftime("%Y-%m-%d")
        st.session_state.fecha_llenado = fecha_llenado
        st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

    acepto_terminos = st.checkbox(
        "He leído y acepto la política de privacidad y el descargo de responsabilidad",
        value=st.session_state.get("acepto_terminos", False),
        key="acepto_terminos"
    )

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Validación y botón Siguiente
    is_step_1_valid = validate_step_1()
    
    if is_step_1_valid:
        st.markdown("""
        <div class="step-motivation">
            ✅ ¡Perfecto! Todos los datos están completos. ¡Listo para continuar!
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚀 SIGUIENTE: COMPOSICIÓN CORPORAL",
            disabled=not is_step_1_valid,
            key="next_step_1",
            help="Continúa al siguiente paso" if is_step_1_valid else "Completa todos los campos para continuar"
        ):
            if is_step_1_valid:
                advance_step()
                st.rerun()
    
    if not is_step_1_valid:
        st.markdown("""
        <div class="step-validation-error">
            ⚠️ Por favor completa todos los campos requeridos y acepta los términos para continuar
        </div>
        """, unsafe_allow_html=True)

# ==================== BIENVENIDA INFORMATIVA ====================
if current_step == 1 and not st.session_state.get("datos_completos", False):
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

# ==================== PASO 2: COMPOSICIÓN CORPORAL ====================
elif current_step == 2:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">📊 Paso 2: Composición Corporal</h1>
        <p class="step-subtitle">Ingresa tus medidas antropométricas para cálculos precisos</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        estatura_default = 170
        estatura_value = st.session_state.get("estatura", estatura_default)
        if estatura_value == '' or estatura_value is None or estatura_value == 0:
            estatura_value = estatura_default
        estatura = st.number_input(
            "📏 Estatura (cm)",
            min_value=120,
            max_value=220,
            value=safe_int(estatura_value, estatura_default),
            key="estatura",
            help="Medida sin zapatos"
        )
    with col3:
        st.markdown('<div class="body-fat-method-selector">', unsafe_allow_html=True)
        metodo_grasa = st.selectbox(
            "📊 Método de medición de grasa",
            ["Omron HBF-516 (BIA)", "InBody 270 (BIA profesional)", "Bod Pod (Pletismografía)", "DEXA (Gold Standard)"],
            index=0 if st.session_state.get("metodo_grasa", "Omron HBF-516 (BIA)").startswith("Omron") else 
                  1 if st.session_state.get("metodo_grasa", "").startswith("InBody") else
                  2 if st.session_state.get("metodo_grasa", "").startswith("Bod Pod") else 3,
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

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Realizar cálculos si hay datos válidos
    if peso > 30 and estatura > 120 and grasa_corporal > 0:
        grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, st.session_state.get("sexo", "Hombre"))
        mlg = calcular_mlg(peso, grasa_corregida)
        tmb = calcular_tmb_cunningham(mlg)
        ffmi = calcular_ffmi(mlg, estatura) if estatura > 0 else 0
        nivel_ffmi = clasificar_ffmi(ffmi, st.session_state.get("sexo", "Hombre"))
        edad_metabolica = calcular_edad_metabolica(st.session_state.get("edad", 25), grasa_corregida, st.session_state.get("sexo", "Hombre"))
        
        # Mostrar corrección si aplica
        if metodo_grasa != "DEXA (Gold Standard)" and abs(grasa_corregida - grasa_corporal) > 0.1:
            st.info(
                f"📊 Valor corregido a equivalente DEXA: {grasa_corregida:.1f}% "
                f"(ajuste de {grasa_corregida - grasa_corporal:+.1f}%)"
            )
    
    # Validación y botón Siguiente
    is_step_2_valid = validate_step_2()
    
    if is_step_2_valid:
        st.markdown("""
        <div class="step-motivation">
            💪 ¡Excelente! Tus datos antropométricos están completos. ¡Sigamos evaluando tu nivel!
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "💪 SIGUIENTE: EVALUACIÓN FUNCIONAL",
            disabled=not is_step_2_valid,
            key="next_step_2",
            help="Continúa al siguiente paso" if is_step_2_valid else "Completa todos los campos para continuar"
        ):
            if is_step_2_valid:
                advance_step()
                st.rerun()
    
    if not is_step_2_valid:
        st.markdown("""
        <div class="step-validation-error">
            ⚠️ Por favor completa todos los campos: peso, estatura y % de grasa corporal
        </div>
        """, unsafe_allow_html=True)
# ==================== PASO 3: EVALUACIÓN FUNCIONAL ====================
elif current_step == 3:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">💪 Paso 3: Evaluación Funcional</h1>
        <p class="step-subtitle">Evalúa tu experiencia y nivel de entrenamiento</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.markdown("### 📋 Experiencia en entrenamiento")
    experiencia = st.radio(
        "¿Cuál de las siguientes afirmaciones describe con mayor precisión tu hábito de entrenamiento en los últimos dos años?",
        [
            "A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.",
            "B) He entrenado al menos 2 veces por semana siguiendo rutinas generales sin mucha progresión planificada.",
            "C) He seguido un programa de entrenamiento estructurado con objetivos claros y progresión semanal.",
            "D) He diseñado o ajustado personalmente mis planes de entrenamiento, monitoreando variables como volumen, intensidad y recuperación."
        ],
        index=0 if st.session_state.get("experiencia_entrenamiento", "").startswith("A)") else
              1 if st.session_state.get("experiencia_entrenamiento", "").startswith("B)") else  
              2 if st.session_state.get("experiencia_entrenamiento", "").startswith("C)") else
              3 if st.session_state.get("experiencia_entrenamiento", "").startswith("D)") else 0,
        help="Tu respuesta debe reflejar tu consistencia y planificación real.",
        key="experiencia_entrenamiento"
    )

    # Solo mostrar ejercicios funcionales si la experiencia ha sido contestada apropiadamente
    if experiencia and not experiencia.startswith("A) He entrenado de forma irregular"):
        st.markdown("### 🏆 Evaluación de rendimiento básica")
        st.info("💡 Proporciona tus mejores resultados en ejercicios básicos manteniendo una técnica adecuada.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💪 Empuje superior")
            empuje = st.selectbox(
                "Elige tu mejor ejercicio de empuje:",
                ["Flexiones", "Fondos"],
                index=0 if st.session_state.get("empuje_ejercicio", "Flexiones") == "Flexiones" else 1,
                help="Selecciona el ejercicio donde tengas mejor rendimiento.",
                key="empuje_ejercicio"
            )
            empuje_reps = st.number_input(
                f"Repeticiones continuas en {empuje}:",
                min_value=0, 
                max_value=100, 
                value=st.session_state.get("empuje_reps", 10),
                help="Sin pausas, con buena forma.",
                key="empuje_reps"
            )
            
        with col2:
            st.markdown("#### 🏋️ Tracción superior")
            traccion = st.selectbox(
                "Elige tu mejor ejercicio de tracción:",
                ["Dominadas", "Remo"],
                index=0 if st.session_state.get("traccion_ejercicio", "Dominadas") == "Dominadas" else 1,
                help="Selecciona el ejercicio donde tengas mejor rendimiento.",
                key="traccion_ejercicio"
            )
            traccion_reps = st.number_input(
                f"Repeticiones continuas en {traccion}:",
                min_value=0, 
                max_value=50, 
                value=st.session_state.get("traccion_reps", 5),
                help="Sin pausas, con buena forma.",
                key="traccion_reps"
            )

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### 🦵 Tren inferior")
            piernas = st.selectbox(
                "Elige tu mejor ejercicio de piernas:",
                ["Sentadillas", "Peso muerto"],
                index=0 if st.session_state.get("piernas_ejercicio", "Sentadillas") == "Sentadillas" else 1,
                help="Selecciona el ejercicio donde tengas mejor rendimiento.",
                key="piernas_ejercicio"
            )
            piernas_peso = st.number_input(
                f"Peso máximo en {piernas} (kg):",
                min_value=0.0, 
                max_value=300.0, 
                value=st.session_state.get("piernas_peso", 50.0),
                step=2.5,
                help="1RM o peso con buena técnica.",
                key="piernas_peso"
            )
            
        with col4:
            st.markdown("#### 🧘 Core")
            core_tiempo = st.number_input(
                "Tiempo máximo en plancha (segundos):",
                min_value=0, 
                max_value=600, 
                value=st.session_state.get("core_tiempo", 60),
                help="Tiempo máximo manteniendo plancha correcta.",
                key="core_tiempo"
            )

    else:
        if experiencia.startswith("A) He entrenado de forma irregular"):
            st.warning("⚠️ **Has seleccionado 'entrenamiento irregular'. Esto limitará las recomendaciones avanzadas.**")
            st.info("💡 Considera elegir una opción que refleje mejor tu experiencia para obtener recomendaciones más precisas.")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Validación y botón Siguiente
    is_step_3_valid = validate_step_3()
    
    if is_step_3_valid:
        st.markdown("""
        <div class="step-motivation">
            🏆 ¡Perfecto! Tu evaluación funcional está completa. ¡Analicemos tu actividad diaria!
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚶 SIGUIENTE: ACTIVIDAD FÍSICA DIARIA",
            disabled=not is_step_3_valid,
            key="next_step_3",
            help="Continúa al siguiente paso" if is_step_3_valid else "Selecciona una experiencia válida para continuar"
        ):
            if is_step_3_valid:
                advance_step()
                st.rerun()
    
    if not is_step_3_valid:
        st.markdown("""
        <div class="step-validation-error">
            ⚠️ Por favor selecciona una opción de experiencia diferente a "entrenamiento irregular"
        </div>
        """, unsafe_allow_html=True)

# ==================== PASO 4-6 Y RESULTADO FINAL ====================
# ==================== PASO 4-6 Y RESULTADO FINAL ====================
elif current_step == 4:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">🚶 Paso 4: Actividad Física Diaria</h1>
        <p class="step-subtitle">Evalúa tu nivel de actividad habitual fuera del ejercicio</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    opciones_actividad = [
        "Sedentario (trabajo de oficina, <5,000 pasos/día)",
        "Moderadamente-activo (trabajo mixto, 5,000-10,000 pasos/día)",
        "Activo (trabajo físico, 10,000-12,500 pasos/día)",
        "Muy-activo (trabajo muy físico, >12,500 pasos/día)"
    ]

    actividad_diaria = st.radio(
        "Selecciona tu nivel de actividad diaria:",
        opciones_actividad,
        index=0,
        help="Considera tu trabajo, transporte y actividades domésticas",
        key="actividad_diaria"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    is_step_4_valid = validate_step_4()
    if is_step_4_valid:
        st.markdown('<div class="step-motivation">🔥 ¡Excelente! Continuemos con el siguiente paso.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🍽️ SIGUIENTE: EFECTO TÉRMICO", disabled=not is_step_4_valid, key="next_step_4"):
            advance_step()
            st.rerun()

elif current_step == 5:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">🍽️ Paso 5: Efecto Térmico de los Alimentos</h1>
        <p class="step-subtitle">Calcula el gasto energético adicional por digestión</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    eta_factor = st.slider(
        "Factor ETA (%)",
        min_value=8.0,
        max_value=15.0,
        value=10.0,
        step=0.5,
        help="Típicamente entre 8-15% del gasto energético total",
        key="eta_factor"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    is_step_5_valid = validate_step_5()
    if is_step_5_valid:
        st.markdown('<div class="step-motivation">⚡ ¡Perfecto! Un paso más y terminamos.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏋️ SIGUIENTE: GASTO ENERGÉTICO", disabled=not is_step_5_valid, key="next_step_5"):
            advance_step()
            st.rerun()

elif current_step == 6:
    st.markdown("""
    <div class="step-header">
        <h1 class="step-title">🏋️ Paso 6: Gasto Energético del Ejercicio</h1>
        <p class="step-subtitle">Define tu rutina de entrenamiento de fuerza</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    frecuencia_opciones = [
        "0-1 días por semana (principiante)",
        "2 días por semana (intermedio)",
        "3 días por semana (regular)",
        "4-5 días por semana (avanzado)",
        "6+ días por semana (élite/competitivo)"
    ]
    
    entrenamiento_fuerza = st.radio(
        "¿Con qué frecuencia entrenas fuerza/resistencia?",
        frecuencia_opciones,
        index=0,
        help="Incluye pesas, calistenia, entrenamiento funcional",
        key="entrenamiento_fuerza"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    is_step_6_valid = validate_step_6()
    if is_step_6_valid:
        st.markdown('<div class="step-motivation">🎯 ¡Increíble! Tu evaluación está completa.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📈 VER RESULTADOS FINALES", disabled=not is_step_6_valid, key="next_step_6"):
            advance_step()
            st.rerun()

# ==================== PASO 7: RESULTADOS FINALES ====================
elif current_step == 7:
    st.markdown("""
    <div class="completion-card">
        <h1>🎉 ¡EVALUACIÓN COMPLETADA!</h1>
        <p>Tu cuestionario MUPAI ha sido procesado exitosamente</p>
        <p>🏆 Todos los pasos han sido completados con excelencia</p>
        <p>📊 Tus datos están siendo analizados para crear tu plan personalizado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Realizar cálculos finales con los datos disponibles
    peso = st.session_state.get("peso", 70.0)
    estatura = st.session_state.get("estatura", 170)
    grasa_corporal = st.session_state.get("grasa_corporal", 20.0)
    sexo = st.session_state.get("sexo", "Hombre")
    edad = st.session_state.get("edad", 25)
    metodo_grasa = st.session_state.get("metodo_grasa", "Omron HBF-516 (BIA)")
    
    if peso > 0 and estatura > 0 and grasa_corporal > 0:
        grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
        mlg = calcular_mlg(peso, grasa_corregida)
        tmb = calcular_tmb_cunningham(mlg)
        ffmi = calcular_ffmi(mlg, estatura) if estatura > 0 else 0
        
        st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
        st.markdown("### 📊 Resumen de tu Evaluación")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💪 Masa Libre de Grasa", f"{mlg:.1f} kg")
            st.metric("🔥 TMB Cunningham", f"{tmb:.0f} kcal")
        with col2:
            st.metric("📏 FFMI", f"{ffmi:.1f}")
            st.metric("⚖️ Grasa Corregida", f"{grasa_corregida:.1f}%")
        with col3:
            experiencia = st.session_state.get("experiencia_entrenamiento", "No especificado")[:20] + "..."
            st.metric("💪 Experiencia", experiencia)
            actividad = st.session_state.get("actividad_diaria", "No especificado")[:15] + "..."
            st.metric("🚶 Actividad", actividad)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botón para nueva evaluación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 NUEVA EVALUACIÓN", key="nueva_evaluacion_final"):
            for key in list(st.session_state.keys()):
                if key not in ["authenticated"]:  # Mantener autenticación
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

# Mensaje para pasos no válidos
else:
    st.error("❌ Error en la navegación. Reiniciando...")
    st.session_state.current_step = 1
    st.rerun()

# ==================== MENSAJE FINAL SIMPLIFICADO ====================
# Solo mostrar si los datos están completos para la evaluación
if st.session_state.datos_completos and 'peso' in locals() and peso > 0:
    st.markdown("---")
    # Just show a simple congratulatory message instead of technical details
    pass  # The earlier completion message handles this

# --- Botón para enviar al coach (usuario solo ve confirmación) ---
if not st.session_state.get("correo_enviado", False):
    if st.button("🚀 Enviar Mi Evaluación al Coach", key="enviar_email"):
        faltantes = datos_completos_para_email()
        if faltantes:
            st.error(f"❌ Por favor completa los siguientes datos: {', '.join(faltantes)}")
        else:
            with st.spinner("🚀 Enviando tu evaluación al coach..."):
                ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono)
                if ok:
                    st.session_state["correo_enviado"] = True
                    st.success("✅ ¡Perfecto! Tu evaluación ha sido enviada exitosamente a tu coach")
                else:
                    st.error("❌ Hubo un problema técnico. Por favor intenta de nuevo o contacta a soporte.")
else:
    st.success("✅ Tu evaluación ya fue enviada exitosamente. Tu coach se pondrá en contacto contigo pronto.")

# --- Opción para reenviar (simplificada) ---
if st.button("📧 Reenviar Evaluación", key="reenviar_email"):
    faltantes = datos_completos_para_email()
    if faltantes:
        st.error(f"❌ Por favor completa los siguientes datos: {', '.join(faltantes)}")
    else:
        with st.spinner("📧 Reenviando tu evaluación..."):
            ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono)
            if ok:
                st.session_state["correo_enviado"] = True
                st.success("✅ ¡Listo! Tu evaluación ha sido reenviada a tu coach")
            else:
                st.error("❌ Hubo un problema técnico. Por favor intenta de nuevo o contacta a soporte.")

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

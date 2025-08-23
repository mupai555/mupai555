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
    "authenticated": False  # Nueva variable para controlar el login
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

acepto_terminos = st.checkbox("He leído y acepto la política de privacidad y el descargo de responsabilidad")

if st.button("🚀 COMENZAR EVALUACIÓN", disabled=not acepto_terminos):
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
        st.success("✅ Datos registrados correctamente. ¡Continuemos con tu evaluación!")
    else:
        # Mostrar todos los errores de validación
        error_message = "⚠️ **Por favor corrige los siguientes errores:**\n\n" + "\n\n".join(validation_errors)
        st.error(error_message)

st.markdown('</div>', unsafe_allow_html=True)

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
datos_personales_completos = all([nombre, telefono, email_cliente]) and acepto_terminos

if datos_personales_completos and st.session_state.datos_completos:
    # Progress bar general
    progress = st.progress(0)
    progress_text = st.empty()

    # BLOQUE 1: Datos antropométricos con diseño mejorado
    with st.expander("📊 **Paso 1: Composición Corporal y Antropometría**", expanded=True):
        progress.progress(20)
        progress_text.text("Paso 1 de 5: Evaluación de composición corporal")

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

    # Note: session_state is automatically managed by widget keys, so no explicit assignments needed

    # Cálculos antropométricos
    sexo = st.session_state.sexo
    edad = st.session_state.edad
    metodo_grasa = st.session_state.metodo_grasa
    peso = st.session_state.peso
    estatura = st.session_state.estatura
    grasa_corporal = st.session_state.grasa_corporal

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

    # FFMI con visualización mejorada
    st.markdown("### 💪 Índice de Masa Libre de Grasa (FFMI)")
    col1, col2 = st.columns([2, 1])
    with col1:
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
    with col2:
        st.info(f"""
        **Referencia FFMI ({sexo}):**
        - Bajo: <{rangos_ffmi['Bajo']}
        - Promedio: {rangos_ffmi['Bajo']}-{rangos_ffmi['Promedio']}
        - Bueno: {rangos_ffmi['Promedio']}-{rangos_ffmi['Bueno']}
        - Avanzado: {rangos_ffmi['Bueno']}-{rangos_ffmi['Avanzado']}
        - Élite: >{rangos_ffmi['Avanzado']}
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
psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
if psmf_recs.get("psmf_aplicable"):
    st.markdown('<div class="content-card card-psmf">', unsafe_allow_html=True)
    perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
    st.warning(f"""
    ⚡ **CANDIDATO PARA PROTOCOLO PSMF ACTUALIZADO**
    Por tu % de grasa corporal ({grasa_corregida:.1f}%), podrías beneficiarte de una fase de pérdida rápida:
    
    🥩 **Proteína diaria:** {psmf_recs['proteina_g_dia']} g/día ({psmf_recs['proteina_g_dia']/peso:.2f} g/kg peso total)
    🔥 **Calorías diarias:** {psmf_recs['calorias_dia']:.0f} kcal/día
    📊 **Multiplicador:** {psmf_recs.get('multiplicador', 8.3)} (perfil: {psmf_recs.get('perfil_grasa', 'alto % grasa')})
    📈 **Pérdida semanal proyectada:** {perdida_min}-{perdida_max} kg/semana
    ⚠️ **Mínimo absoluto:** {psmf_recs['calorias_piso_dia']} kcal/día
    📋 **Criterio:** {psmf_recs['criterio']}
    
    ⚠️ **ADVERTENCIAS DE SEGURIDAD:**
    • Duración máxima: 6-8 semanas
    • Requiere supervisión médica/nutricional
    • Carbohidratos y grasas al mínimo (solo de fuentes magras y vegetales)
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
with st.expander("💪 **Paso 2: Evaluación Funcional y Nivel de Entrenamiento**", expanded=True):
    progress.progress(40)
    progress_text.text("Paso 2 de 5: Evaluación de capacidades funcionales")

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
        help="Tu respuesta debe reflejar tu consistencia y planificación real."
    )

    # Solo mostrar ejercicios funcionales si la experiencia ha sido contestada apropiadamente
    if experiencia and not experiencia.startswith("A) He entrenado de forma irregular"):
        st.markdown("### 🏆 Evaluación de rendimiento por categoría")
        st.info("💡 Para cada categoría, selecciona el ejercicio donde hayas alcanzado tu mejor rendimiento y proporciona el máximo que hayas logrado manteniendo una técnica adecuada.")

        ejercicios_data = {}
        niveles_ejercicios = {}

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💪 Empuje", "🏋️ Tracción", "🦵 Pierna Empuje", "🦵 Pierna Tracción", "🧘 Core"])
    else:
        st.warning("⚠️ **Primero debes seleccionar tu nivel de experiencia en entrenamiento para acceder a la evaluación de ejercicios funcionales.**")
        st.info("Por favor, selecciona una opción diferente a 'A) He entrenado de forma irregular' para continuar con la evaluación funcional.")
        ejercicios_data = {}
        niveles_ejercicios = {}

    if experiencia and not experiencia.startswith("A) He entrenado de forma irregular"):
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
            col1, col2 = st.columns(2)
            with col1:
                core = st.selectbox(
                    "Elige tu mejor ejercicio de core:",
                    ["Plancha", "Ab wheel", "L-sit"],
                    help="Selecciona el ejercicio donde tengas mejor rendimiento y técnica."
                )
            with col2:
                if core == "Plancha":
                    core_tiempo = st.number_input(
                        "¿Cuál es el máximo tiempo (segundos) que mantienes la posición de plancha con técnica correcta?",
                        min_value=0, max_value=600, value=safe_int(st.session_state.get("plancha_tiempo", 60), 60),
                        help="Mantén la posición sin perder alineación corporal."
                    )
                    ejercicios_data[core] = core_tiempo
                else:
                    core_reps = st.number_input(
                        f"¿Cuántas repeticiones completas realizas en {core} con buena forma?",
                        min_value=0, max_value=100, value=safe_int(st.session_state.get(f"{core}_reps", 10), 10),
                        help="Repeticiones con control y sin compensaciones."
                    )
                    ejercicios_data[core] = core_reps

        # Evaluar niveles según referencias
        st.markdown("### 📊 Tu nivel en cada ejercicio")

        cols = st.columns(5)  # Changed from 4 to 5 to accommodate 5 exercises
        for idx, (ejercicio, valor) in enumerate(ejercicios_data.items()):
            with cols[idx % 5]:  # Changed from 4 to 5
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

# Calcular nivel global con ponderación
puntos_ffmi = {"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4, "Élite": 5}.get(nivel_ffmi, 1)
puntos_exp = {"A)": 1, "B)": 2, "C)": 3, "D)": 4}.get(experiencia[:2] if experiencia and len(experiencia) >= 2 else "", 1)
puntos_por_nivel = {"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4}
puntos_funcional = sum([puntos_por_nivel.get(n, 1) for n in niveles_ejercicios.values()]) / len(niveles_ejercicios) if niveles_ejercicios else 1

# Determinar si el porcentaje de grasa está en rango saludable para ponderar FFMI
en_rango_saludable = esta_en_rango_saludable(grasa_corregida, sexo)

# Ponderación adaptativa según el porcentaje de grasa corporal
if en_rango_saludable:
    # Rango saludable: FFMI 40%, funcionalidad 40%, experiencia 20%
    puntaje_total = (puntos_ffmi / 5 * 0.4) + (puntos_funcional / 4 * 0.4) + (puntos_exp / 4 * 0.2)
else:
    # Fuera de rango saludable (obesidad): FFMI 0%, funcionalidad 80%, experiencia 20%
    puntaje_total = (puntos_ffmi / 5 * 0.0) + (puntos_funcional / 4 * 0.8) + (puntos_exp / 4 * 0.2)

if puntaje_total < 0.3:
    nivel_entrenamiento = "principiante"
elif puntaje_total < 0.5:
    nivel_entrenamiento = "intermedio"
elif puntaje_total < 0.7:
    nivel_entrenamiento = "avanzado"
else:
    nivel_entrenamiento = "élite"

# Validar si todos los ejercicios funcionales y experiencia están completos
ejercicios_funcionales_completos = len(ejercicios_data) >= 5  # Debe tener los 5 ejercicios
experiencia_completa = experiencia and not experiencia.startswith("A) He entrenado de forma irregular")

# === MOSTRAR RESUMEN GLOBAL TEMPRANO (ADICIONAL) ===
# Mostrar resumen global después de los badges de ejercicios si hay datos suficientes
if ejercicios_funcionales_completos and experiencia_completa:
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
    
    # Mostrar advertencia si FFMI no se pondera por exceso de grasa
    if not en_rango_saludable:
        rango_texto = "≤25%" if sexo == "Hombre" else "≤32%"
        st.warning(f"""
        ⚠️ **ADVERTENCIA: FFMI no ponderado por exceso de grasa corporal**
        
        Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) está fuera del rango saludable para {sexo.lower()}s ({rango_texto}).
        
        **Ponderación aplicada:**
        - 🏋️ FFMI (desarrollo muscular): **0%** (no ponderado)
        - 💪 Funcionalidad: **80%** 
        - 📚 Experiencia: **20%**
        
        Una vez que alcances el rango saludable de grasa corporal, se aplicará la ponderación estándar (40% FFMI, 40% funcionalidad, 20% experiencia).
        """)
    else:
        st.info(f"""
        ✅ **Ponderación completa aplicada**
        
        Tu porcentaje de grasa corporal ({grasa_corregida:.1f}%) está en rango saludable. Se aplica la ponderación estándar:
        
        - 🏋️ FFMI (desarrollo muscular): **40%**
        - 💪 Funcionalidad: **40%** 
        - 📚 Experiencia: **20%**
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

if 'ffmi' in locals() and 'nivel_entrenamiento' in locals() and ffmi > 0:
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

    st.markdown('<div class="content-card card-success">', unsafe_allow_html=True)
    st.success(f"""
    📈 **Análisis de tu potencial muscular**

    Has desarrollado aproximadamente el **{porc_potencial:.0f}%** de tu potencial muscular natural.

    - FFMI actual: {ffmi:.2f}
    - FFMI máximo estimado: {ffmi_genetico_max:.1f}
    - Margen de crecimiento: {max(0, ffmi_genetico_max - ffmi):.1f} puntos
    """)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Completa primero todos los datos anteriores para ver tu potencial genético.")

# BLOQUE 3: Actividad física diaria
with st.expander("🚶 **Paso 3: Nivel de Actividad Física Diaria**", expanded=True):
    progress.progress(60)
    progress_text.text("Paso 3 de 5: Evaluación de actividad diaria")

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

    # Mensaje resumen
    st.success(
        f"✅ **Tu nivel de actividad física diaria: {nivel_actividad_text}**\n\n"
        f"- Factor GEAF: **{geaf}**\n"
        f"- Esto multiplicará tu gasto energético basal en un {(geaf-1)*100:.0f}%"
    )

    st.markdown('</div>', unsafe_allow_html=True)
    # BLOQUE 4: ETA (Efecto Térmico de los Alimentos)
with st.expander("🍽️ **Paso 4: Efecto Térmico de los Alimentos (ETA)**", expanded=True):
    progress.progress(70)
    progress_text.text("Paso 4 de 5: Cálculo del efecto térmico")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.markdown("### 🔥 Determinación automática del ETA")
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

    # Guarda ETA en session_state para usarlo en los cálculos finales
    st.session_state.eta = eta
    st.session_state.eta_desc = eta_desc
    st.session_state.eta_color = eta_color

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
    # BLOQUE 5: Entrenamiento de fuerza
with st.expander("🏋️ **Paso 5: Gasto Energético del Ejercicio (GEE)**", expanded=True):
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
    st.markdown('</div>', unsafe_allow_html=True)
    # BLOQUE 6: Cálculo final con comparativa PSMF
with st.expander("📈 **RESULTADO FINAL: Tu Plan Nutricional Personalizado**", expanded=True):
    progress.progress(100)
    progress_text.text("Paso final: Calculando tu plan nutricional personalizado")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    # Determinar fase nutricional
    if sexo == "Hombre":
        if grasa_corregida < 10:
            fase = "Superávit recomendado: 10-15%"
            porcentaje = 12.5  # Positivo para superávit (ganancia)
        elif grasa_corregida <= 18:
            fase = "Mantenimiento o minivolumen"
            porcentaje = 0
        else:
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje = -deficit_valor  # Negativo para déficit (pérdida)
            fase = f"Déficit recomendado: {deficit_valor}%"
    else:  # Mujer
        if grasa_corregida < 16:
            fase = "Superávit recomendado: 10%"
            porcentaje = 10  # Positivo para superávit (ganancia)
        elif grasa_corregida <= 23:
            fase = "Mantenimiento"
            porcentaje = 0
        else:
            deficit_valor = sugerir_deficit(grasa_corregida, sexo)
            porcentaje = -deficit_valor  # Negativo para déficit (pérdida)
            fase = f"Déficit recomendado: {deficit_valor}%"

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
    plan_elegido = "Tradicional"
    if psmf_recs.get("psmf_aplicable"):
        st.markdown("### ⚡ Opciones de plan nutricional")
        st.warning("Eres candidato para el protocolo PSMF. Puedes elegir entre dos estrategias:")

        plan_elegido = st.radio(
            "Selecciona tu estrategia preferida:",
            ["Plan Tradicional (déficit moderado, más sostenible)",
             "Protocolo PSMF (pérdida rápida, más restrictivo)"],
            index=0,
            help="PSMF es muy efectivo pero requiere mucha disciplina"
        )
        
        # Opción para seleccionar grasa en PSMF (30-50g)
        grasa_psmf_seleccionada = 40.0  # Valor por defecto
        if "PSMF" in plan_elegido:
            st.markdown("#### 🥑 Configuración de grasas para PSMF")
            grasa_psmf_seleccionada = st.slider(
                "Selecciona la cantidad de grasa diaria (en gramos):",
                min_value=30.0,
                max_value=50.0,
                value=40.0,
                step=1.0,
                help="Rango permitido para PSMF: 30-50g de grasas de fuentes magras (pescado, aceite de oliva mínimo)"
            )

        # Mostrar comparativa visual
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
            st.markdown(f"""
            **Consideraciones:**
            - ⚠️ Muy restrictivo
            - ⚠️ Máximo 6-8 semanas
            - ⚠️ Requiere supervisión médica
            - ⚠️ Proteína: {psmf_recs['proteina_g_dia']}g/día (1.8g/kg mínimo)
            - ⚠️ Grasas: 30-50g (seleccionable, fuentes magras)
            - ⚠️ Carbos: resto de calorías (solo vegetales fibrosos)
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
        
        # GRASAS: Usar el valor seleccionado por el usuario (30-50g)
        grasa_g = grasa_psmf_seleccionada if 'grasa_psmf_seleccionada' in locals() else 40.0
        grasa_kcal = grasa_g * 9
        
        # CARBOHIDRATOS: El resto de calorías de vegetales fibrosos únicamente
        carbo_kcal = max(ingesta_calorica - proteina_kcal - grasa_kcal, 0)
        carbo_g = round(carbo_kcal / 4, 1)
        
        multiplicador = psmf_recs.get('multiplicador', 8.3)
        perfil_grasa = psmf_recs.get('perfil_grasa', 'alto % grasa')
        perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
        
        fase = f"PSMF Actualizado - Pérdida rápida (déficit ~{deficit_psmf}%, multiplicador {multiplicador})"

        st.error(f"""
        ⚠️ **ADVERTENCIA IMPORTANTE SOBRE PSMF ACTUALIZADO:**
        - Es un protocolo **MUY RESTRICTIVO** con nuevo cálculo basado en proteína total
        - **Duración máxima:** 6-8 semanas
        - **Proteína:** {proteina_g}g/día (1.8g/kg peso total mínimo)
        - **Multiplicador calórico:** {multiplicador} (perfil: {perfil_grasa})
        - **Pérdida proyectada:** {perdida_min}-{perdida_max} kg/semana
        - **Requiere:** Supervisión médica y análisis de sangre regulares
        - **Carbohidratos:** Solo de vegetales fibrosos ({carbo_g}g calculados según calorías restantes)
        - **Grasas:** {grasa_g}g (rango 30-50g, fuentes magras como pescado, aceite de oliva mínimo)
        - **Suplementación obligatoria:** Multivitamínico, omega-3, electrolitos, magnesio
        - **No apto para:** Personas con historial de TCA, problemas médicos o embarazo
        """)
    else:
        # ----------- TRADICIONAL -----------
        ingesta_calorica = ingesta_calorica_tradicional

        # PROTEÍNA: 1.8g/kg peso corporal total
        proteina_g = round(peso * 1.8, 1)
        proteina_kcal = proteina_g * 4

        # GRASA: 40% TMB/REE, nunca menos del 20% ni más del 40% de calorías totales
        grasa_min_kcal = ingesta_calorica * 0.20
        grasa_ideal_kcal = tmb * 0.40
        grasa_ideal_g = round(grasa_ideal_kcal / 9, 1)
        grasa_min_g = round(grasa_min_kcal / 9, 1)
        grasa_max_kcal = ingesta_calorica * 0.40
        grasa_g = max(grasa_min_g, grasa_ideal_g)
        if grasa_g * 9 > grasa_max_kcal:
            grasa_g = round(grasa_max_kcal / 9, 1)
        grasa_kcal = grasa_g * 9

        # CARBOHIDRATOS: el resto de las calorías
        carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
        carbo_g = round(carbo_kcal / 4, 1)
        if carbo_g < 50:
            st.warning(f"⚠️ Tus carbohidratos han quedado muy bajos ({carbo_g}g). Considera aumentar calorías o reducir grasa para una dieta más sostenible.")

        # --- DESGLOSE FINAL VISUAL ---
        st.markdown("### 🍽️ Distribución de macronutrientes")
        st.write(f"- **Proteína:** {proteina_g}g ({proteina_kcal:.0f} kcal, {proteina_kcal/ingesta_calorica*100:.1f}%)")
        st.write(f"- **Grasas:** {grasa_g}g ({grasa_kcal:.0f} kcal, {grasa_kcal/ingesta_calorica*100:.1f}%)")
        st.write(f"- **Carbohidratos:** {carbo_g}g ({carbo_kcal:.0f} kcal, {carbo_kcal/ingesta_calorica*100:.1f}%)")

        # Mostrar cálculo detallado con diseño mejorado
        st.markdown("### 🧮 Desglose del cálculo")
        with st.expander("Ver cálculo detallado", expanded=False):
            st.code(f"""
Gasto Energético Total (GE) = TMB × GEAF × ETA + GEE
GE = {tmb:.0f} × {geaf} × {eta} + {gee_prom_dia:.0f} = {GE:.0f} kcal

Factor de Balance Energético (FBEO) = 1 - (déficit/100)
FBEO = 1 - ({porcentaje}/100) = {fbeo:.2f}

Ingesta Calórica = GE × FBEO
Ingesta = {GE:.0f} × {fbeo:.2f} = {ingesta_calorica:.0f} kcal/día
""")

        # Resultado final con diseño premium
        st.markdown("### 🎯 Tu plan nutricional personalizado")

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

# --- FORZAR actualización de variables clave desde session_state ---
peso = st.session_state.get("peso", 0)
estatura = st.session_state.get("estatura", 0)
grasa_corporal = st.session_state.get("grasa_corporal", 0)

# RESUMEN FINAL MEJORADO
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
    st.markdown(f"""
    ### 💪 Composición Corporal
    - **Peso:** {peso} kg | **Altura:** {estatura} cm
    - **% Grasa:** {grasa_corregida:.1f}% | **MLG:** {mlg:.1f} kg
    - **FFMI:** {ffmi:.2f} ({nivel_ffmi})
    - **Potencial:** {porc_potencial:.0f}% alcanzado
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

{'⚠️ **Nota:** Elegiste el protocolo PSMF. Recuerda que es temporal (6-8 semanas máximo) y requiere supervisión.' if 'PSMF' in plan_elegido else ''}
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

# ====== BOTONES Y ENVÍO FINAL (SOLO POR BOTÓN, NUNCA AUTOMÁTICO) ======

def datos_completos_para_email():
    obligatorios = {
        "Nombre": nombre,
        "Peso": peso,
        "Estatura": estatura,
        "Edad": edad,
        "Email": email_cliente,
        "Teléfono": telefono
    }
    faltantes = [campo for campo, valor in obligatorios.items() if not valor]
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

tabla_resumen = f"""
=====================================
EVALUACIÓN MUPAI - INFORME COMPLETO
=====================================
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sistema: MUPAI v2.0 - Muscle Up Performance Assessment Intelligence

=====================================
DATOS DEL CLIENTE:
=====================================
- Nombre completo: {nombre}
- Edad: {edad} años
- Sexo: {sexo}
- Teléfono: {telefono}
- Email: {email_cliente}
- Fecha evaluación: {fecha_llenado}

=====================================
ANTROPOMETRÍA Y COMPOSICIÓN:
=====================================
- Peso: {peso} kg
- Estatura: {estatura} cm
- IMC: {imc:.1f} kg/m²
- Método medición grasa: {metodo_grasa}
- % Grasa medido: {grasa_corporal}%
- % Grasa corregido (DEXA): {grasa_corregida:.1f}%
- Masa Libre de Grasa: {mlg:.1f} kg
- Masa Grasa: {peso - mlg:.1f} kg

=====================================
ÍNDICES METABÓLICOS:
=====================================
- TMB (Cunningham): {tmb:.0f} kcal
- FFMI actual: {ffmi:.2f}
- Clasificación FFMI: {nivel_ffmi}
- FFMI máximo estimado: {ffmi_genetico_max:.1f}
- Potencial alcanzado: {porc_potencial:.0f}%
- Margen de crecimiento: {max(0, ffmi_genetico_max - ffmi):.1f} puntos FFMI

=====================================
FACTORES DE ACTIVIDAD:
=====================================
- Nivel actividad diaria: {nivel_actividad.split('(')[0].strip()}
- Factor GEAF: {geaf}
- Factor ETA: {eta}
- Días entreno/semana: {dias_fuerza}
- Gasto por sesión: {kcal_sesion} kcal
- GEE promedio diario: {gee_prom_dia:.0f} kcal
- Gasto Energético Total: {GE:.0f} kcal

=====================================
PLAN NUTRICIONAL CALCULADO:
=====================================
- Fase: {fase}
- Factor FBEO: {fbeo:.2f}
- Ingesta calórica: {ingesta_calorica:.0f} kcal/día
- Ratio kcal/kg: {ratio_kcal_kg:.1f}

DISTRIBUCIÓN DE MACRONUTRIENTES:
- Proteína: {proteina_g}g ({proteina_kcal_safe:.0f} kcal) = {proteina_percent}%
- Grasas: {grasa_g}g ({grasa_kcal_safe:.0f} kcal) = {grasa_percent}%
- Carbohidratos: {carbo_g}g ({carbo_kcal_safe:.0f} kcal) = {carbo_percent}%

=====================================
RESUMEN PERSONALIZADO Y PROYECCIÓN
=====================================
📊 DIAGNÓSTICO PERSONALIZADO:
- Categoría grasa corporal: {
    "Muy bajo (Competición)" if (sexo == "Hombre" and grasa_corregida < 6) or (sexo == "Mujer" and grasa_corregida < 12)
    else "Atlético" if (sexo == "Hombre" and grasa_corregida < 12) or (sexo == "Mujer" and grasa_corregida < 17)
    else "Fitness" if (sexo == "Hombre" and grasa_corregida < 18) or (sexo == "Mujer" and grasa_corregida < 23)
    else "Promedio" if (sexo == "Hombre" and grasa_corregida < 25) or (sexo == "Mujer" and grasa_corregida < 30)
    else "Alto"
} ({grasa_corregida:.1f}%)
- Nivel de entrenamiento: {nivel_entrenamiento.capitalize() if 'nivel_entrenamiento' in locals() else 'Intermedio'}
- Objetivo recomendado: {fase}

📈 PROYECCIÓN CIENTÍFICA 6 SEMANAS:"""

# Calcular proyección científica para el email
try:
    # Determinar el porcentaje correcto según el plan elegido usando función centralizada
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
    
    tabla_resumen += f"""
- Objetivo recomendado: {porcentaje_valor:+.0f}% {objetivo_texto}
- Rango semanal científico: {proyeccion_email['rango_semanal_pct'][0]:.1f}% a {proyeccion_email['rango_semanal_pct'][1]:.1f}% del peso corporal
- Cambio semanal estimado: {proyeccion_email['rango_semanal_kg'][0]:+.2f} a {proyeccion_email['rango_semanal_kg'][1]:+.2f} kg/semana
- Rango total 6 semanas: {proyeccion_email['rango_total_6sem_kg'][0]:+.2f} a {proyeccion_email['rango_total_6sem_kg'][1]:+.2f} kg
- Peso actual → rango proyectado: {peso:.1f} kg → {peso + proyeccion_email['rango_total_6sem_kg'][0]:.1f} a {peso + proyeccion_email['rango_total_6sem_kg'][1]:.1f} kg
- Explicación científica: {proyeccion_email['explicacion_textual']}
"""
except:
    tabla_resumen += "\n- Error en cálculo de proyección. Usar valores por defecto.\n"

# Agregar secciones adicionales del cuestionario
experiencia_text = experiencia if 'experiencia' in locals() and experiencia else "No especificado"
nivel_actividad_text = nivel_actividad.split('(')[0].strip() if 'nivel_actividad' in locals() and nivel_actividad else "No especificado"

# Generar detalle de ejercicios funcionales
ejercicios_detalle = ""
if 'ejercicios_data' in locals() and ejercicios_data:
    for ejercicio, valor in ejercicios_data.items():
        nivel_ej = st.session_state.niveles_ejercicios.get(ejercicio, "No evaluado")
        if ejercicio in ["Plancha", "L-sit"]:
            ejercicios_detalle += f"- {ejercicio}: {valor} segundos → Nivel: {nivel_ej}\n"
        else:
            ejercicios_detalle += f"- {ejercicio}: {valor} repeticiones → Nivel: {nivel_ej}\n"
else:
    ejercicios_detalle = "- No se completaron las evaluaciones funcionales\n"

# Calcular ambos planes nutricionales para comparación
plan_tradicional_calorias = ingesta_calorica_tradicional if 'ingesta_calorica_tradicional' in locals() else 0
plan_psmf_disponible = psmf_recs.get("psmf_aplicable", False) if 'psmf_recs' in locals() else False

# Información de entrenamiento de fuerza
dias_fuerza_text = dias_fuerza if 'dias_fuerza' in locals() else 0
kcal_sesion_text = kcal_sesion if 'kcal_sesion' in locals() else 0

tabla_resumen += f"""

=====================================
EXPERIENCIA Y RESPUESTAS FUNCIONALES
=====================================
📋 EXPERIENCIA DE ENTRENAMIENTO:
{experiencia_text}

💪 EVALUACIÓN FUNCIONAL DETALLADA:
{ejercicios_detalle}

=====================================
NIVEL GLOBAL DE ENTRENAMIENTO
=====================================
🎯 DESGLOSE DEL NIVEL GLOBAL:
- Desarrollo muscular (FFMI): {puntos_ffmi if 'puntos_ffmi' in locals() else 0}/5 puntos → {nivel_ffmi}
- Rendimiento funcional: {puntos_funcional if 'puntos_funcional' in locals() else 0:.1f}/4 puntos → Promedio de ejercicios
- Experiencia declarada: {puntos_exp if 'puntos_exp' in locals() else 0}/4 puntos → {experiencia_text[:50]}...
- PONDERACIÓN APLICADA: {'40% FFMI + 40% Funcional + 20% Experiencia (rango saludable)' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else '0% FFMI + 80% Funcional + 20% Experiencia (fuera de rango saludable)'}
- GRASA CORPORAL: {grasa_corregida:.1f}% ({'En rango saludable' if (en_rango_saludable if 'en_rango_saludable' in locals() else True) else f'Fuera de rango saludable (>{25 if sexo == "Hombre" else 32}%)'})
- RESULTADO FINAL: {nivel_entrenamiento.upper() if 'nivel_entrenamiento' in locals() else 'INTERMEDIO'} (Score: {puntaje_total if 'puntaje_total' in locals() else 0:.2f}/1.0)

=====================================
ACTIVIDAD FÍSICA DIARIA Y FACTORES
=====================================
🚶 NIVEL DE ACTIVIDAD DIARIA:
- Clasificación: {nivel_actividad_text}
- Factor GEAF aplicado: {geaf if 'geaf' in locals() else 1.0}
- Descripción: {nivel_actividad if 'nivel_actividad' in locals() and nivel_actividad else 'No especificado'}
- Impacto metabólico: Multiplica el TMB en {(geaf-1)*100 if 'geaf' in locals() else 0:.0f}%

🔥 EFECTO TÉRMICO DE LOS ALIMENTOS (ETA):
- Factor ETA: {eta if 'eta' in locals() else 1.1}
- Criterio aplicado: {eta_desc if 'eta_desc' in locals() else 'ETA estándar'}
- Justificación: Basado en % grasa corporal ({grasa_corregida:.1f}%) y sexo ({sexo})

=====================================
ENTRENAMIENTO DE FUERZA - DETALLE
=====================================
🏋️ FRECUENCIA Y GASTO ENERGÉTICO:
- Días de entrenamiento/semana: {dias_fuerza_text} días
- Gasto por sesión: {kcal_sesion_text} kcal
- Criterio del gasto: Basado en nivel global ({nivel_entrenamiento.capitalize() if 'nivel_entrenamiento' in locals() else 'Intermedio'})
- Gasto semanal total: {gee_semanal if 'gee_semanal' in locals() else 0:.0f} kcal
- Promedio diario (GEE): {gee_prom_dia if 'gee_prom_dia' in locals() else 0:.0f} kcal/día

=====================================
COMPARATIVA COMPLETA DE PLANES NUTRICIONALES
=====================================
📊 PLAN TRADICIONAL (DÉFICIT/SUPERÁVIT MODERADO):
- Calorías: {plan_tradicional_calorias:.0f} kcal/día
- Estrategia: {fase}
- Proteína: {peso * 1.8 if 'peso' in locals() and peso > 0 else 0:.1f}g/día (1.8g/kg peso)
- Grasas: ~40% del TMB = {tmb * 0.40 / 9 if 'tmb' in locals() else 0:.1f}g/día (ajustado por límites 20-40% calorías)
- Carbohidratos: Resto de calorías disponibles
- Sostenibilidad: ALTA - Recomendado para adherencia a largo plazo
- Pérdida/ganancia esperada: 0.3-0.7% peso corporal/semana
- Duración recomendada: Indefinida con ajustes periódicos

⚡ PROTOCOLO PSMF ACTUALIZADO {'(APLICABLE)' if plan_psmf_disponible else '(NO APLICABLE)'}:"""

if plan_psmf_disponible:
    tabla_resumen += f"""
- Calorías: {psmf_recs['calorias_dia']:.0f} kcal/día
- Criterio de aplicabilidad: {psmf_recs.get('criterio', 'No especificado')}
- Proteína: {psmf_recs['proteina_g_dia']:.1f}g/día (1.8g/kg peso mínimo)
- Multiplicador calórico: {psmf_recs.get('multiplicador', 8.3)} (perfil: {psmf_recs.get('perfil_grasa', 'alto % grasa')})
- Grasas: 30-50g/día (fuentes magras: pescado, aceite oliva mínimo)
- Carbohidratos: Solo de vegetales fibrosos ({(psmf_recs['calorias_dia'] - psmf_recs['proteina_g_dia']*4 - 40*9)/4 if psmf_recs.get('calorias_dia', 0) > 0 else 0:.1f}g estimados)
- Déficit estimado: ~{int((1 - psmf_recs['calorias_dia']/(GE if 'GE' in locals() else 2000)) * 100) if psmf_recs.get('calorias_dia', 0) > 0 else 0}%
- Pérdida esperada: {psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[0]}-{psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[1]} kg/semana
- Sostenibilidad: BAJA - Máximo 6-8 semanas
- Duración recomendada: 6-8 semanas con supervisión médica obligatoria
- Suplementación necesaria: Multivitamínico, omega-3, electrolitos, magnesio
- Monitoreo requerido: Análisis de sangre regulares"""
else:
    tabla_resumen += f"""
- RAZÓN DE NO APLICABILIDAD: % grasa no cumple criterios mínimos
- Criterio hombres: >18% grasa corporal (actual: {grasa_corregida:.1f}%)
- Criterio mujeres: >23% grasa corporal (actual: {grasa_corregida:.1f}%)
- RECOMENDACIÓN: Usar plan tradicional hasta alcanzar % grasa objetivo"""

tabla_resumen += f"""

📋 ANÁLISIS COMPARATIVO DE ESTRATEGIAS:
- TRADICIONAL vs PSMF: {'Ambos aplicables - Usuario puede elegir' if plan_psmf_disponible else 'Solo tradicional aplicable'}
- Velocidad de resultados: {'PSMF 2-3x más rápido' if plan_psmf_disponible else 'Tradicional = velocidad moderada sostenible'}
- Riesgo de pérdida muscular: {'PSMF = mayor riesgo' if plan_psmf_disponible else 'Tradicional = riesgo mínimo'}
- Facilidad de adherencia: {'Tradicional >> PSMF' if plan_psmf_disponible else 'Tradicional = alta adherencia'}
- Impacto en rendimiento: {'PSMF = reducción significativa' if plan_psmf_disponible else 'Tradicional = impacto mínimo'}

=====================================
PREFERENCIAS Y HÁBITOS ADICIONALES
=====================================
🍽️ INFORMACIÓN NUTRICIONAL ADICIONAL:
- Método medición grasa: {metodo_grasa} → Ajuste DEXA: {grasa_corregida - grasa_corporal:+.1f}%
- Edad metabólica calculada: {edad_metabolica} años (vs cronológica: {edad} años)
- Categoría de grasa corporal: {
    "Muy bajo (Competición)" if (sexo == "Hombre" and grasa_corregida < 6) or (sexo == "Mujer" and grasa_corregida < 12)
    else "Atlético" if (sexo == "Hombre" and grasa_corregida < 12) or (sexo == "Mujer" and grasa_corregida < 17)
    else "Fitness" if (sexo == "Hombre" and grasa_corregida < 18) or (sexo == "Mujer" and grasa_corregida < 23)
    else "Promedio" if (sexo == "Hombre" and grasa_corregida < 25) or (sexo == "Mujer" and grasa_corregida < 30)
    else "Alto"
}

💊 SUPLEMENTACIÓN RECOMENDADA:
- Creatina monohidrato: 5g/día (mejora rendimiento y recuperación)
- Vitamina D3: 2000-4000 UI/día (optimización hormonal)
- Omega-3 (EPA+DHA): 2-3g/día (antiinflamatorio y salud cardiovascular)
- Multivitamínico: 1/día (seguro nutricional)
{'- ADICIONAL PARA PSMF: Electrolitos, magnesio, complejo B' if plan_psmf_disponible else ''}

=====================================
NOTAS, ADVERTENCIAS Y RECOMENDACIONES
=====================================
⚠️ ADVERTENCIAS IMPORTANTES:
- Este análisis es una herramienta de apoyo, NO sustituye supervisión profesional
- Los cálculos están basados en ecuaciones científicas validadas pero la respuesta individual varía
- Se recomienda evaluación médica antes de iniciar cualquier plan nutricional restrictivo
{'- CRÍTICO PARA PSMF: Supervisión médica OBLIGATORIA con análisis de sangre regulares' if plan_psmf_disponible else ''}
- Hidratación mínima: {peso * 35 if 'peso' in locals() and peso > 0 else 2450:.0f}ml/día (35ml/kg peso)

🎯 RECOMENDACIONES ESPECÍFICAS:
- Reevaluación recomendada: Cada 2-3 semanas para ajustes
- Enfoque principal: {'Pérdida de grasa manteniendo músculo' if porcentaje < 0 else 'Ganancia muscular controlada' if porcentaje > 0 else 'Recomposición corporal'}
- Timing de nutrientes: Proteína en cada comida, carbohidratos pre/post entreno
- Descanso óptimo: 7-9 horas/noche para maximizar resultados
- Gestión del estrés: Técnicas de relajación y mindfulness recomendadas

📈 MÉTRICAS DE SEGUIMIENTO SUGERIDAS:
- Peso corporal: Diario (misma hora, condiciones)
- Medidas corporales: Semanal (cintura, cadera, brazos)
- Fotos progreso: Bisemanal (misma iluminación y pose)
- Rendimiento en ejercicios: Cada sesión (seguimiento de cargas/repeticiones)
- Energía y bienestar: Diario (escala 1-10)

⚠️ IMPORTANTE - NATURALEZA DE LAS ESTIMACIONES:
Estas son estimaciones basadas en modelos científicos. El cuerpo humano 
es un sistema complejo, no lineal y dinámico. Los resultados reales 
dependerán de múltiples factores como:

- Adherencia estricta al plan nutricional y de entrenamiento
- Calidad del sueño y gestión del estrés  
- Respuesta individual y adaptaciones metabólicas
- Factores hormonales y genéticos
- Variaciones en la actividad diaria no planificada

RECOMENDACIÓN: Utiliza estas proyecciones como guía inicial y ajusta 
según tu progreso real. Se recomienda evaluación periódica cada 2-3 
semanas para optimizar resultados.

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

# --- Botón para enviar email (solo si no se ha enviado y todo completo) ---
if not st.session_state.get("correo_enviado", False):
    if st.button("📧 Enviar Resumen por Email", key="enviar_email"):
        faltantes = datos_completos_para_email()
        if faltantes:
            st.error(f"❌ No se puede enviar el email. Faltan: {', '.join(faltantes)}")
        else:
            with st.spinner("📧 Enviando resumen por email..."):
                ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono)
                if ok:
                    st.session_state["correo_enviado"] = True
                    st.success("✅ Email enviado exitosamente a administración")
                else:
                    st.error("❌ Error al enviar email. Contacta a soporte técnico.")
else:
    st.info("✅ El resumen ya fue enviado por email. Si requieres reenviarlo, refresca la página o usa el botón de 'Reenviar Email'.")

# --- Opción para reenviar manualmente (opcional) ---
if st.button("📧 Reenviar Email", key="reenviar_email"):
    faltantes = datos_completos_para_email()
    if faltantes:
        st.error(f"❌ No se puede reenviar el email. Faltan: {', '.join(faltantes)}")
    else:
        with st.spinner("📧 Reenviando resumen por email..."):
            ok = enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono)
            if ok:
                st.session_state["correo_enviado"] = True
                st.success("✅ Email reenviado exitosamente a administración")
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

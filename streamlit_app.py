import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
from eta_block import calcular_eta_automatico

# ==================== HELPER FUNCTIONS ====================

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

/* Wizard Specific Styles */
.wizard-progress-container {
    background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%);
    padding: 2rem;
    border-radius: 12px;
    border-left: 4px solid var(--mupai-yellow);
    margin: 1rem 0 2rem 0;
    box-shadow: 0 8px 25px rgba(244, 196, 48, 0.1);
}

.wizard-header h2 {
    color: var(--mupai-yellow);
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
    font-weight: bold;
}

.wizard-header p {
    color: #CCCCCC;
    margin: 0;
    font-size: 1.1rem;
}

.progress-bar-container {
    background: #333;
    height: 8px;
    border-radius: 4px;
    margin: 1.5rem 0 0.5rem 0;
    overflow: hidden;
}

.progress-bar {
    background: linear-gradient(90deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    height: 100%;
    transition: width 0.3s ease;
}

.progress-text {
    color: var(--mupai-yellow);
    margin: 0;
    font-weight: bold;
    text-align: right;
}

.wizard-step-container {
    background: linear-gradient(135deg, #1A1A1A 0%, #232323 100%);
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
    border: 1px solid #444;
}
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
with st.expander("👤 **Información Personal**", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(crear_tarjeta(
            "📋 Datos Básicos",
            "Información personal necesaria para personalizar tu evaluación.",
            "info"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "🔐 Privacidad",
            "Tus datos son confidenciales y solo se usan para generar tu plan personalizado.",
            "success"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta(
            "⚡ Precisión",
            "Datos precisos = recomendaciones más exactas y efectivas.",
            "warning"
        ), unsafe_allow_html=True)

    st.markdown("### Completa todos los campos para comenzar")
    
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
        st.success("✅ Datos registrados correctamente. ¡Continuemos con tu evaluación!")
    else:
        # Mostrar todos los errores de validación
        error_message = "⚠️ **Por favor corrige los siguientes errores:**\n\n" + "\n\n".join(validation_errors)
        st.error(error_message)

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

# ==================== MAIN APPLICATION LOGIC ====================
# Show all evaluation sections together in classic questionnaire format
if datos_personales_completos and st.session_state.datos_completos:
    
    st.markdown("## 📋 Evaluación MUPAI - Cuestionario Completo")
    st.info("Complete todas las secciones para obtener su análisis personalizado. Puede rellenar las secciones en cualquier orden.")
    
    # Show all wizard steps as sections without navigation
    st.markdown('<div class="questionnaire-container">', unsafe_allow_html=True)
    
    # SECTION 1: Body Composition (formerly Step 4)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid var(--mupai-yellow);
        margin: 1rem 0 2rem 0;
        box-shadow: 0 8px 25px rgba(244, 196, 48, 0.15);
    ">
        <h2 style="color: var(--mupai-yellow); margin: 0 0 0.5rem 0; font-size: 1.8rem;">
            📊 PASO 4: Composición Corporal y Antropometría
        </h2>
        <p style="color: #CCCCCC; margin: 0; font-size: 1.1rem;">
            🎯 Este paso es fundamental para calcular tu metabolismo basal y diseñar tu plan nutricional personalizado
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced instructional guidance
    st.info("""
    📋 **Instrucciones importantes:**
    - Introduce tu peso **en ayunas** y **sin ropa** para mayor precisión
    - La estatura debe medirse **sin zapatos**
    - Selecciona el **método exacto** utilizado para medir tu grasa corporal
    - Todos los campos son **obligatorios** para continuar
    """)
    
    # Informational cards with enhanced content
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(crear_tarjeta(
            "📊 Composición Corporal",
            "Medición precisa de tu masa magra, grasa corporal y distribución de tejidos para cálculos metabólicos exactos. Base fundamental para tu TMB.",
            "info"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "🔬 Métodos Científicos",
            "Utilizamos correcciones validadas según el método de medición para obtener valores equivalentes al estándar DEXA (Gold Standard).",
            "success"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta(
            "⚡ Precisión TMB",
            "Los datos antropométricos permiten calcular tu tasa metabólica basal con la fórmula de Cunningham, más precisa que Harris-Benedict.",
            "warning"
        ), unsafe_allow_html=True)

    st.markdown("#### 📊 Datos Antropométricos Requeridos")
    st.markdown("*Completa todos los campos para ver tus métricas calculadas automáticamente*")
    
    # Enhanced form inputs with validation feedback
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**⚖️ PESO CORPORAL**")
        # Ensure peso has a valid default
        peso_default = "70.0"
        peso_value = st.session_state.get("peso", peso_default)
        if peso_value == '' or peso_value is None or peso_value == 0:
            peso_value = peso_default
        
        peso_text = st.text_input(
            "Peso corporal (kg)",
            value=str(peso_value),
            key="peso_text",
            help="⚖️ Peso en ayunas, sin ropa. Fundamental para calcular tu metabolismo basal (TMB).",
            placeholder="Ej: 70.5"
        )
        
        # Validate peso input
        peso_valid = False
        peso = 0.0
        if peso_text:
            try:
                peso = float(peso_text)
                if 30.0 <= peso <= 200.0:
                    peso_valid = True
                    st.session_state.peso = peso
                    if peso < 40:
                        st.warning("⚠️ Peso muy bajo. Verifícalo.")
                    elif peso > 150:
                        st.info("📊 Peso elevado registrado.")
                    else:
                        st.success("✅ Peso registrado correctamente")
                else:
                    st.error("⚠️ El peso debe estar entre 30 y 200 kg.")
            except ValueError:
                st.error("⚠️ Por favor ingresa un número válido.")
        else:
            st.info("💡 Ingresa tu peso corporal en kilogramos.")
            
    with col2:
        st.markdown("**📏 ESTATURA**")
        # Ensure estatura has a valid default
        estatura_default = 170
        estatura_value = st.session_state.get("estatura", estatura_default)
        if estatura_value == '' or estatura_value is None or estatura_value == 0:
            estatura_value = estatura_default
        estatura = st.number_input(
            "Estatura (cm)",
            min_value=120,
            max_value=220,
            value=safe_int(estatura_value, estatura_default),
            key="estatura",
            help="📏 Medida sin zapatos. Necesaria para calcular IMC y FFMI."
        )
        # Validation feedback for estatura
        if estatura < 140:
            st.warning("⚠️ Estatura muy baja. Verifícala.")
        elif estatura > 200:
            st.info("📊 Estatura elevada registrada.")
        else:
            st.success("✅ Estatura registrada correctamente")
            
    with col3:
        st.markdown("**📊 MÉTODO DE MEDICIÓN**")
        metodo_grasa = st.selectbox(
            "Método de medición de grasa",
            ["Omron HBF-516 (BIA)", "InBody 270 (BIA profesional)", "Bod Pod (Pletismografía)", "DEXA (Gold Standard)"],
            key="metodo_grasa",
            help="🔬 Crucial para aplicar la corrección científica correcta según el método."
        )
        # Information about selected method
        method_info = {
            "Omron HBF-516 (BIA)": "Corrección: -1.5%. Método doméstico común.",
            "InBody 270 (BIA profesional)": "Corrección: -1.0%. BIA profesional.",
            "Bod Pod (Pletismografía)": "Corrección: +0.5%. Método muy preciso.",
            "DEXA (Gold Standard)": "Sin corrección. Método más preciso disponible."
        }
        st.info(f"ℹ️ {method_info.get(metodo_grasa, 'Método seleccionado')}")

    # Enhanced body fat percentage input
    st.markdown("**💪 PORCENTAJE DE GRASA CORPORAL**")
    grasa_default = "20.0"
    grasa_value = st.session_state.get("grasa_corporal", grasa_default)
    if grasa_value == '' or grasa_value is None or grasa_value == 0:
        grasa_value = grasa_default
        
    grasa_text = st.text_input(
        f"% de grasa corporal medido con {metodo_grasa.split('(')[0].strip()}",
        value=str(grasa_value),
        key="grasa_corporal_text",
        help=f"💪 Valor exacto medido con {metodo_grasa.split('(')[0].strip()}. Se aplicará corrección automática.",
        placeholder="Ej: 15.5"
    )
    
    # Validate grasa corporal input
    grasa_valid = False
    grasa_corporal = 0.0
    if grasa_text:
        try:
            grasa_corporal = float(grasa_text)
            if 3.0 <= grasa_corporal <= 60.0:
                grasa_valid = True
                st.session_state.grasa_corporal = grasa_corporal
                
                # Enhanced validation feedback for body fat
                sexo = st.session_state.get("sexo", "Hombre")
                if sexo == "Hombre":
                    if grasa_corporal < 6:
                        st.warning("⚠️ Grasa muy baja para hombres. Verifica la medición.")
                    elif grasa_corporal < 15:
                        st.success("💪 Excelente nivel de grasa corporal")
                    elif grasa_corporal < 25:
                        st.info("👍 Nivel de grasa saludable")
                    else:
                        st.warning("📊 Nivel de grasa elevado - ideal para fase de definición")
                else:  # Mujer
                    if grasa_corporal < 12:
                        st.warning("⚠️ Grasa muy baja para mujeres. Verifica la medición.")
                    elif grasa_corporal < 20:
                        st.success("💪 Excelente nivel de grasa corporal")
                    elif grasa_corporal < 30:
                        st.info("👍 Nivel de grasa saludable")
                    else:
                        st.warning("📊 Nivel de grasa elevado - ideal para fase de definición")
            else:
                st.error("⚠️ El porcentaje de grasa debe estar entre 3% y 60%.")
        except ValueError:
            st.error("⚠️ Por favor ingresa un número válido.")
    else:
        st.info("💡 Ingresa tu porcentaje de grasa corporal.")
    
    # Enhanced calculations display with educational content
    peso_from_session = st.session_state.get("peso", 0)
    grasa_from_session = st.session_state.get("grasa_corporal", 0)
    if peso_from_session > 0 and estatura > 0 and grasa_from_session > 0:
        # Add visual separator
        st.markdown("---")
        st.markdown("""
        <h3 style="color: var(--mupai-yellow); text-align: center; margin: 1rem 0;">
            🧮 CÁLCULOS ANTROPOMÉTRICOS AUTOMÁTICOS
        </h3>
        """, unsafe_allow_html=True)
        
        st.success("✅ **Todos los datos completos** - Cálculos realizados automáticamente")
        
        # Cálculos antropométricos
        sexo = st.session_state.sexo
        edad = st.session_state.edad
        
        # Calculate derived metrics
        imc = peso_from_session / ((estatura / 100) ** 2)
        masa_libre_grasa = peso_from_session * (1 - grasa_from_session / 100)
        ffmi = masa_libre_grasa / ((estatura / 100) ** 2)
        
        # DEXA correction with detailed explanation
        factores_correccion = {
            "Omron HBF-516 (BIA)": -1.5,
            "InBody 270 (BIA profesional)": -1.0, 
            "Bod Pod (Pletismografía)": +0.5,
            "DEXA (Gold Standard)": 0.0
        }
        factor_actual = factores_correccion.get(metodo_grasa, 0.0)
        grasa_corregida = grasa_from_session + factor_actual
        grasa_corregida = max(3.0, min(60.0, grasa_corregida))
        
        # Show correction explanation
        if factor_actual != 0:
            if factor_actual > 0:
                st.info(f"🔬 **Corrección aplicada:** +{factor_actual}% (tu método subestima la grasa)")
            else:
                st.info(f"🔬 **Corrección aplicada:** {factor_actual}% (tu método sobrestima la grasa)")
        else:
            st.info("🏆 **Método DEXA:** No requiere corrección (Gold Standard)")

        # Enhanced results display with explanations
        st.markdown("#### 📊 Resultados de tus Métricas Corporales")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # IMC with interpretation
            if imc < 18.5:
                imc_status = "📉 Bajo peso"
                imc_color = "orange"
            elif imc < 25:
                imc_status = "✅ Normal"
                imc_color = "green"
            elif imc < 30:
                imc_status = "⚠️ Sobrepeso"
                imc_color = "orange"
            else:
                imc_status = "🔴 Obesidad"
                imc_color = "red"
            
            st.metric(
                "IMC", 
                f"{imc:.1f}", 
                imc_status,
                help="Índice de Masa Corporal = Peso (kg) / Altura² (m). Indicador general de peso saludable."
            )
            
        with col2:
            # FFMI with interpretation
            if sexo == "Hombre":
                if ffmi < 16:
                    ffmi_status = "📉 Bajo"
                elif ffmi < 19:
                    ffmi_status = "👍 Normal"
                elif ffmi < 22:
                    ffmi_status = "💪 Bueno"
                else:
                    ffmi_status = "🏆 Excelente"
            else:  # Mujer
                if ffmi < 14:
                    ffmi_status = "📉 Bajo"
                elif ffmi < 17:
                    ffmi_status = "👍 Normal"
                elif ffmi < 19:
                    ffmi_status = "💪 Bueno"
                else:
                    ffmi_status = "🏆 Excelente"
            
            st.metric(
                "FFMI", 
                f"{ffmi:.1f}", 
                ffmi_status,
                help="Fat-Free Mass Index = Masa Libre de Grasa / Altura². Indica tu desarrollo muscular."
            )
            
        with col3:
            # Corrected body fat with interpretation
            diferencia = grasa_corregida - grasa_corporal
            if diferencia > 0:
                delta_text = f"+{diferencia:.1f}%"
            elif diferencia < 0:
                delta_text = f"{diferencia:.1f}%"
            else:
                delta_text = "Sin cambio"
                
            st.metric(
                "Grasa Corregida", 
                f"{grasa_corregida:.1f}%", 
                delta_text,
                help="Porcentaje de grasa ajustado al estándar DEXA para mayor precisión en cálculos."
            )
            
        with col4:
            # Lean body mass
            masa_grasa = peso_from_session - masa_libre_grasa
            st.metric(
                "Masa Libre Grasa", 
                f"{masa_libre_grasa:.1f} kg", 
                f"Grasa: {masa_grasa:.1f} kg",
                help="Peso total menos grasa corporal. Incluye músculos, huesos, órganos y agua."
            )

        # Educational explanations
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%); 
                   padding: 1.5rem; border-radius: 10px; margin: 1rem 0;
                   border-left: 4px solid #27AE60;">
            <h4 style="color: #27AE60; margin: 0 0 1rem 0;">💡 ¿Qué significan estos números?</h4>
            <ul style="color: #CCCCCC; margin: 0;">
                <li><strong>IMC:</strong> Relación peso/altura. Útil para población general, pero no considera composición corporal.</li>
                <li><strong>FFMI:</strong> Indica tu desarrollo muscular independiente de la grasa. Más útil que el IMC para deportistas.</li>
                <li><strong>Grasa Corregida:</strong> Ajuste científico según tu método de medición para mayor precisión.</li>
                <li><strong>Masa Libre de Grasa:</strong> Tu peso sin grasa corporal. Fundamental para calcular tu metabolismo basal.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Validation status for step completion
        st.success("🎯 **Paso 4 completado exitosamente** - Todos los datos antropométricos registrados correctamente")
        
    else:
        # Validation feedback when data is incomplete
        missing_fields = []
        if peso <= 0:
            missing_fields.append("Peso corporal")
        if estatura <= 0:
            missing_fields.append("Estatura")
        if grasa_corporal <= 0:
            missing_fields.append("Porcentaje de grasa corporal")
            
        if missing_fields:
            st.warning(f"⚠️ **Campos faltantes:** {', '.join(missing_fields)}")
            st.info("ℹ️ Complete todos los campos para ver sus métricas calculadas automáticamente")
        
    # SECTION 2: Functional Evaluation (formerly Step 5)
    st.markdown("---")
    # Step 5: Functional Evaluation and Experience
    st.markdown("### 💪 Evaluación Funcional y Nivel de Entrenamiento")
    
    # Experience section
    st.markdown("#### 🎯 Experiencia en Entrenamiento")
    experiencia = st.radio(
        "Selecciona tu nivel de experiencia en entrenamiento:",
        [
            "A) He entrenado de forma irregular, con semanas sin entrenar y sin un plan estructurado.",
            "B) He seguido rutinas de entrenamiento durante 3-6 meses de forma relativamente constante.",
            "C) Tengo 1-2 años de experiencia en entrenamiento sistemático con rutinas estructuradas.", 
            "D) Tengo más de 2 años de entrenamiento constante y conozco bien mi respuesta a diferentes estímulos."
        ],
        key="experiencia_entrenamiento",
        help="Tu experiencia determina la precisión de los cálculos de gasto energético del ejercicio."
    )
    
    # Functional tests section
    st.markdown("#### 🏃‍♂️ Evaluación Funcional")
    st.info("Realiza estos ejercicios y registra tu mejor marca. Si no puedes realizar algún ejercicio, indica 0.")
    
    # Get current sex for references
    sexo_actual = st.session_state.get("sexo", "Hombre")
    referencias = referencias_funcionales.get(sexo_actual, referencias_funcionales["Hombre"])
    
    # Exercise tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💪 Tren superior empuje", "🤲 Tren superior tracción", "🦵 Tren inferior empuje", "🍑 Tren inferior tracción", "🔥 Core"])
    
    ejercicios_data = {}
    
    with tab1:
        st.markdown("#### Tren superior empuje")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ejercicio:**")
            st.info("Flexiones")
            st.info("Fondos en paralelas")
        with col2:
            flexiones_reps = st.number_input(
                "¿Cuántas flexiones continuas realizas con buena forma?",
                min_value=0, max_value=100, value=safe_int(st.session_state.get("Flexiones_reps", 15), 15),
                help="Flexiones completas, pecho tocando el suelo.",
                key="flexiones_reps"
            )
            ejercicios_data["Flexiones"] = flexiones_reps
            
            fondos_reps = st.number_input(
                "¿Cuántos fondos en paralelas continuas realizas con buena forma?",
                min_value=0, max_value=50, value=safe_int(st.session_state.get("Fondos_reps", 8), 8),
                help="Fondos completos en paralelas o en banco.",
                key="fondos_reps"
            )
            ejercicios_data["Fondos"] = fondos_reps
    
    with tab2:
        st.markdown("#### Tren superior tracción")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ejercicio:**")
            st.info("Dominadas")
            st.info("Remo invertido")
        with col2:
            dominadas_reps = st.number_input(
                "¿Cuántas dominadas continuas realizas con buena forma?",
                min_value=0, max_value=30, value=safe_int(st.session_state.get("Dominadas_reps", 3), 3),
                help="Dominadas completas, desde brazo extendido hasta barbilla sobre la barra.",
                key="dominadas_reps"
            )
            ejercicios_data["Dominadas"] = dominadas_reps
            
            remo_reps = st.number_input(
                "¿Cuántas repeticiones continuas realizas de remo invertido?",
                min_value=0, max_value=50, value=safe_int(st.session_state.get("Remo invertido_reps", 10), 10),
                help="Remo invertido en barra o TRX, cuerpo recto.",
                key="remo_invertido_reps"
            )
            ejercicios_data["Remo invertido"] = remo_reps
    
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
                help="Puente con una pierna, contracción completa de glúteos.",
                key="puente_gluteo_reps"
            )
            ejercicios_data["Puente de glúteo unilateral"] = pierna_traccion_reps

    with tab5:
        st.markdown("#### Core")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ejercicio:**")
            st.info("Plancha (tiempo)")
            st.info("Ab wheel")
            st.info("L-sit (tiempo)")
        with col2:
            plancha_tiempo = st.number_input(
                "¿Cuántos segundos mantienes la plancha con buena forma?",
                min_value=0, max_value=300, value=safe_int(st.session_state.get("Plancha_tiempo", 30), 30),
                help="Plancha frontal, cuerpo recto.",
                key="plancha_tiempo"
            )
            ejercicios_data["Plancha"] = plancha_tiempo
            
            ab_wheel_reps = st.number_input(
                "¿Cuántas repeticiones continuas realizas con Ab wheel?",
                min_value=0, max_value=30, value=safe_int(st.session_state.get("Ab wheel_reps", 2), 2),
                help="Repeticiones completas de Ab wheel o rollout.",
                key="ab_wheel_reps"
            )
            ejercicios_data["Ab wheel"] = ab_wheel_reps
            
            l_sit_tiempo = st.number_input(
                "¿Cuántos segundos mantienes el L-sit?",
                min_value=0, max_value=120, value=safe_int(st.session_state.get("L-sit_tiempo", 5), 5),
                help="L-sit en paralelas o barras, piernas extendidas horizontalmente.",
                key="l_sit_tiempo"
            )
            ejercicios_data["L-sit"] = l_sit_tiempo
    
    # Store exercise data
    st.session_state.datos_ejercicios = ejercicios_data
    
    # SECTION 3: Physical Activity (formerly Step 6)
    st.markdown("---")
    # Step 6: Daily Physical Activity Level
    st.markdown("### 🚶 Nivel de Actividad Física Diaria")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(crear_tarjeta(
            "🎯 Factor GEAF",
            "El Gasto Energético de Actividad Física multiplica tu TMB según tu nivel de actividad diaria.",
            "info"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "📊 Precisión",
            "Una clasificación precisa de tu actividad mejora la exactitud del cálculo calórico.",
            "warning"
        ), unsafe_allow_html=True)
    
    st.markdown("#### Selecciona tu nivel de actividad diaria")
    
    nivel_actividad = st.radio(
        "¿Cuál describe mejor tu nivel de actividad física diaria?",
        [
            "Sedentario (trabajo de oficina, poco movimiento, menos de 5000 pasos/día)",
            "Moderadamente-activo (trabajo mixto, 6000-8000 pasos/día, actividades ligeras)",
            "Activo (trabajo físico ligero o muchas actividades diarias, 8000-12000 pasos/día)",
            "Muy-activo (trabajo físico intenso o muy activo durante el día, más de 12000 pasos/día)"
        ],
        key="actividad_diaria",
        help="No incluyas tu entrenamiento formal aquí, solo tu actividad diaria base."
    )
    
    # Show activity factor
    if nivel_actividad:
        nivel_corto = nivel_actividad.split('(')[0].strip()
        geaf = obtener_geaf(nivel_corto)
        
        st.success(f"""
        📊 **Tu factor de actividad (GEAF): {geaf}**
        
        Esto significa que tu gasto energético diario será {geaf} veces tu TMB.
        """)
        
    # SECTION 4: Strength Training (formerly Step 7)
    st.markdown("---")
    # Step 7: Strength Training
    st.markdown("### 🏋️ Entrenamiento de Fuerza")
    
    st.markdown("#### Frecuencia y características de tu entrenamiento")
    
    col1, col2 = st.columns(2)
    with col1:
        frecuencia_entrenamiento = st.slider(
            "¿Cuántos días por semana entrenas fuerza/resistencia?",
            min_value=0, max_value=7, value=st.session_state.get("frecuencia_entrenamiento", 3),
            key="frecuencia_entrenamiento",
            help="Incluye pesas, calistenia, CrossFit, etc."
        )
        
        duracion_sesion = st.slider(
            "¿Cuántos minutos dura cada sesión de entrenamiento?",
            min_value=0, max_value=180, value=st.session_state.get("duracion_sesion", 60),
            step=15,
            key="duracion_sesion",
            help="Tiempo efectivo de entrenamiento"
        )
    
    with col2:
        intensidad_entrenamiento = st.selectbox(
            "¿Cómo describirías la intensidad de tus entrenamientos?",
            ["Baja (descansos largos, no muy exigente)", 
             "Moderada (algo de esfuerzo, descansos moderados)",
             "Alta (entrenamientos exigentes, descansos cortos)",
             "Muy alta (entrenamientos muy intensos, al fallo)"],
            index=st.session_state.get("intensidad_idx", 1),
            key="intensidad_entrenamiento",
            help="Nivel de esfuerzo percibido durante el entrenamiento"
        )
        
        # Store intensity index for persistence
        intensidades = ["Baja (descansos largos, no muy exigente)", 
                       "Moderada (algo de esfuerzo, descansos moderados)",
                       "Alta (entrenamientos exigentes, descansos cortos)",
                       "Muy alta (entrenamientos muy intensos, al fallo)"]
        if intensidad_entrenamiento in intensidades:
            st.session_state.intensidad_idx = intensidades.index(intensidad_entrenamiento)
    
    # Calculate training energy expenditure if data is available
    if frecuencia_entrenamiento > 0:
        # Calculate GEE (Exercise Energy Expenditure)
        peso_actual = st.session_state.get("peso", 70)
        
        # Intensity factors
        factores_intensidad = {
            "Baja (descansos largos, no muy exigente)": 0.5,
            "Moderada (algo de esfuerzo, descansos moderados)": 0.7,
            "Alta (entrenamientos exigentes, descansos cortos)": 0.9,
            "Muy alta (entrenamientos muy intensos, al fallo)": 1.1
        }
        
        factor_intensidad = factores_intensidad.get(intensidad_entrenamiento, 0.7)
        
        # Calculate calories per session (approximate)
        calorias_por_sesion = peso_actual * factor_intensidad * (duracion_sesion / 60) * 6  # ~6 kcal/kg/hour base
        gee_semanal = calorias_por_sesion * frecuencia_entrenamiento
        gee_por_dia = gee_semanal / 7
        
        st.session_state.gee_por_dia = gee_por_dia
        
        st.success(f"""
        🔥 **Gasto energético del ejercicio calculado:**
        - Calorías por sesión: ~{calorias_por_sesion:.0f} kcal
        - Gasto semanal: ~{gee_semanal:.0f} kcal
        - Promedio diario: ~{gee_por_dia:.0f} kcal/día
        """)
        
    # SECTION 5: ETA (formerly Step 8)
    st.markdown("---")
    # Step 8: Thermal Effect of Food (ETA)
    from eta_block import mostrar_bloque_eta
    mostrar_bloque_eta()
    
    # End of questionnaire sections
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show results when all sections are complete
    datos_suficientes = (
        st.session_state.get("peso", 0) > 0 and 
        st.session_state.get("estatura", 0) > 0 and 
        st.session_state.get("grasa_corporal", 0) > 0 and
        st.session_state.get("experiencia_entrenamiento", "") and
        st.session_state.get("actividad_diaria", "") and
        st.session_state.get("frecuencia_entrenamiento", 0) > 0
    )
    
    if datos_suficientes:
        # Show results and plans
        st.markdown("## 🎉 ¡Evaluación Completada!")
        st.success("Has completado exitosamente todos los pasos de la evaluación MUPAI.")
        
        # Get all necessary data from session state for calculations
        peso = st.session_state.get("peso", 0)
        estatura = st.session_state.get("estatura", 0) 
        grasa_corporal = st.session_state.get("grasa_corporal", 0)
        sexo = st.session_state.get("sexo", "Hombre")
        edad = st.session_state.get("edad", 25)
        
        # Display basic results
        col1, col2, col3 = st.columns(3)
        with col1:
            imc = peso / ((estatura / 100) ** 2) if estatura > 0 else 0
            st.metric("IMC", f"{imc:.1f}", help="Índice de Masa Corporal")
        with col2:
            st.metric("Peso", f"{peso:.1f} kg", help="Peso corporal")
        with col3:
            st.metric("Estatura", f"{estatura} cm", help="Estatura")
            
        st.success("📊 Evaluación completada. Todos los cálculos han sido realizados.")
        
        # Email functionality would go here
        if st.button("📧 Solicitar Resumen por Email"):
            st.info("Funcionalidad de email estará disponible próximamente.")
            
    else:
        st.warning("⚠️ Complete todas las secciones para ver sus resultados personalizados.")
        
        # Show what's missing
        missing = []
        if not st.session_state.get("peso", 0) > 0:
            missing.append("Peso")
        if not st.session_state.get("estatura", 0) > 0:
            missing.append("Estatura") 
        if not st.session_state.get("grasa_corporal", 0) > 0:
            missing.append("% Grasa corporal")
        if not st.session_state.get("experiencia_entrenamiento", ""):
            missing.append("Experiencia en entrenamiento")
        if not st.session_state.get("actividad_diaria", ""):
            missing.append("Nivel de actividad")
        if not st.session_state.get("frecuencia_entrenamiento", 0) > 0:
            missing.append("Frecuencia de entrenamiento")
            
        if missing:
            st.info(f"Faltan completar: {', '.join(missing)}")

else:
    st.info("Por favor completa los datos personales para comenzar la evaluación.")

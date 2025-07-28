import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

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
    Si el método es Omron, ajusta con tabla.
    Si InBody, aplica factor.
    Si BodPod, aplica factor por sexo.
    Si DEXA, devuelve el valor medido.
    """
    try:
        medido = float(medido)
    except (TypeError, ValueError):
        medido = 0.0

    if metodo == "Omron HBF-516 (BIA)":
        tabla = {
            5: 2.5, 6: 3.5, 7: 4.5, 8: 5.5, 9: 6.5,
            10: 7.5, 11: 8.5, 12: 9.5, 13: 10.5, 14: 11.5,
            15: 13.5, 16: 14.5, 17: 15.5, 18: 16.5, 19: 17.5,
            20: 20.5, 21: 21.5, 22: 22.5, 23: 23.5, 24: 24.5,
            25: 27.0, 26: 28.0, 27: 29.0, 28: 30.0, 29: 31.0,
            30: 33.5, 31: 34.5, 32: 35.5, 33: 36.5, 34: 37.5,
            35: 40.0, 36: 41.0, 37: 42.0, 38: 43.0, 39: 44.0,
            40: 45.0
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
    Calcula los parámetros para PSMF (Very Low Calorie Diet) con automatización científica.
    
    REQUISITOS AUTOMÁTICOS IMPLEMENTADOS:
    ====================================
    
    1. MULTIPLICADOR CALÓRICO AUTOMÁTICO según % grasa corporal (NO MODIFICABLE):
       - >31% grasa corporal: multiplicador = 8.3 (protocolo tradicional PSMF)
       - 25%-30% grasa corporal: multiplicador = 9.0 (nivel moderado)
       - <25% grasa corporal: multiplicador = 9.5 (nivel bajo/magro)
    
    2. GRASAS FIJAS: 40g diarios (VALOR NO MODIFICABLE por el usuario)
    
    3. PROTEÍNA: 1.8g/kg peso corporal total (consistente con literatura científica)
    
    4. CARBOHIDRATOS: Resto de calorías de vegetales fibrosos únicamente
    
    LÓGICA DEL MULTIPLICADOR:
    ========================
    - Personas con más grasa (>31%) pueden tolerar déficits más agresivos → multiplicador menor (8.3)
    - Nivel moderado (25-30%) necesita enfoque balanceado → multiplicador medio (9.0)
    - Personas más magras (<25%) requieren enfoque más conservador → multiplicador mayor (9.5)
    
    Args:
        sexo: "Hombre" o "Mujer"
        peso: Peso corporal en kg
        grasa_corregida: % de grasa corporal corregido a equivalente DEXA
        mlg: Masa libre de grasa en kg (no se usa actualmente pero se mantiene por compatibilidad)
    
    Returns:
        dict: Diccionario con todos los parámetros PSMF calculados automáticamente
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
        
        # MULTIPLICADOR CALÓRICO AUTOMÁTICO según % grasa corporal (REQUERIMIENTOS EXACTOS)
        # Esta es la lógica central de automatización solicitada
        if grasa_corregida > 30:  # >30% grasa corporal (incluye 31% como especificado)
            multiplicador = 8.3
            perfil_grasa = "alto % grasa (>30%)"
        elif grasa_corregida >= 25:  # 25%-30% grasa corporal
            multiplicador = 9.0
            perfil_grasa = "% grasa moderado (25-30%)"
        else:  # <25% grasa corporal
            multiplicador = 9.5
            perfil_grasa = "% grasa bajo (<25%)"
        
        # CALORÍAS = proteína (g) × multiplicador automático
        # Esta fórmula garantiza consistencia científica
        calorias_dia = round(proteina_g_dia * multiplicador, 0)
        
        # Verificar que no esté por debajo del piso mínimo
        if calorias_dia < calorias_piso_dia:
            calorias_dia = calorias_piso_dia
        
        # GRASAS: VALOR FIJO 40g (no modificable por usuario)
        # Cumple con el requisito de automatización y consistencia
        grasa_g_fija = 40.0
        
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
            "grasa_g_fija": grasa_g_fija,  # Valor fijo de 40g
            "perdida_semanal_kg": (perdida_semanal_min, perdida_semanal_max),
            "criterio": f"{criterio} - Multiplicador automático: {multiplicador} ({perfil_grasa})"
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

def calcular_macros_centralizados(plan_elegido, psmf_recs, peso, ingesta_calorica_tradicional, tmb):
    """
    Función centralizada para calcular macros de manera consistente.
    
    PROPÓSITO DE CENTRALIZACIÓN:
    ===========================
    Esta función garantiza que todos los bloques de la app muestren exactamente los mismos valores:
    - Advertencia/warning blocks
    - Resumen visual de macros
    - Proyección científica
    - Email de resumen
    - Comparativas de planes
    
    LÓGICA DE CÁLCULO:
    =================
    
    PARA PSMF (Plan automatizado):
    - Proteína: 1.8g/kg peso total (consistente)
    - Grasas: FIJAS 40g (no modificables, cumple requisito)
    - Carbohidratos: Resto de calorías (solo vegetales fibrosos)
    - Multiplicador: Automático según % grasa corporal
    
    PARA PLAN TRADICIONAL:
    - Proteína: 1.8g/kg peso total (misma base que PSMF)
    - Grasas: 40% TMB, limitado entre 20-40% de calorías totales
    - Carbohidratos: Resto de calorías
    
    Args:
        plan_elegido: Plan seleccionado por el usuario
        psmf_recs: Diccionario con recomendaciones PSMF automáticas
        peso: Peso corporal en kg
        ingesta_calorica_tradicional: Calorías del plan tradicional
        tmb: Tasa metabólica basal
    
    Returns:
        dict: Diccionario con todos los valores de macros y metadata
    """
    if psmf_recs.get("psmf_aplicable") and "PSMF" in str(plan_elegido):
        # ============ PSMF AUTOMATIZADO ============
        # Valores ya calculados automáticamente por calculate_psmf()
        
        ingesta_calorica = psmf_recs['calorias_dia']
        proteina_g = psmf_recs['proteina_g_dia']
        proteina_kcal = proteina_g * 4
        
        # GRASAS: VALOR FIJO 40g (cumple requisito de no modificabilidad)
        grasa_g = psmf_recs['grasa_g_fija']  # Siempre 40g
        grasa_kcal = grasa_g * 9
        
        # CARBOHIDRATOS: El resto de calorías de vegetales fibrosos únicamente
        carbo_kcal = max(ingesta_calorica - proteina_kcal - grasa_kcal, 0)
        carbo_g = round(carbo_kcal / 4, 1)
        
        # Información adicional para mostrar consistencia automática
        multiplicador = psmf_recs.get('multiplicador', 8.3)
        perfil_grasa = psmf_recs.get('perfil_grasa', 'automatizado')
        perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
        
        return {
            "tipo_plan": "PSMF",
            "ingesta_calorica": ingesta_calorica,
            "proteina_g": proteina_g,
            "proteina_kcal": proteina_kcal,
            "grasa_g": grasa_g,
            "grasa_kcal": grasa_kcal,
            "carbo_g": carbo_g,
            "carbo_kcal": carbo_kcal,
            "multiplicador": multiplicador,
            "perfil_grasa": perfil_grasa,
            "perdida_rango": (perdida_min, perdida_max),
            "grasa_fija": True  # Indica que la grasa es fija y no modificable
        }
    else:
        # ============ PLAN TRADICIONAL ============
        # Cálculo estándar con flexibilidad en grasas
        
        ingesta_calorica = ingesta_calorica_tradicional

        # PROTEÍNA: 1.8g/kg peso corporal total (consistencia con PSMF)
        proteina_g = round(peso * 1.8, 1)
        proteina_kcal = proteina_g * 4

        # GRASA: 40% TMB/REE, nunca menos del 20% ni más del 40% de calorías totales
        # Esta lógica permite flexibilidad mientras mantiene límites saludables
        grasa_min_kcal = ingesta_calorica * 0.20  # Mínimo 20% de calorías
        grasa_ideal_kcal = tmb * 0.40  # Ideal: 40% del TMB
        grasa_ideal_g = round(grasa_ideal_kcal / 9, 1)
        grasa_min_g = round(grasa_min_kcal / 9, 1)
        grasa_max_kcal = ingesta_calorica * 0.40  # Máximo 40% de calorías
        grasa_g = max(grasa_min_g, grasa_ideal_g)
        if grasa_g * 9 > grasa_max_kcal:
            grasa_g = round(grasa_max_kcal / 9, 1)
        grasa_kcal = grasa_g * 9

        # CARBOHIDRATOS: el resto de las calorías
        carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
        carbo_g = round(carbo_kcal / 4, 1)
        
        return {
            "tipo_plan": "Tradicional",
            "ingesta_calorica": ingesta_calorica,
            "proteina_g": proteina_g,
            "proteina_kcal": proteina_kcal,
            "grasa_g": grasa_g,
            "grasa_kcal": grasa_kcal,
            "carbo_g": carbo_g,
            "carbo_kcal": carbo_kcal,
            "grasa_fija": False  # En plan tradicional la grasa es calculada, no fija
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
    if all([nombre, telefono, email_cliente]):
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
        st.error("⚠️ Por favor completa todos los campos obligatorios")

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
                        <span style="font-size:1.3rem;">🍽️</span> <b>Paso 6:</b> Cuestionario de patrones alimenticios<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos tus hábitos alimentarios actuales, frecuencia de comidas, horarios y tipos de alimentos.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">😋</span> <b>Paso 7:</b> Cuestionario de alimentación emocional<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Analizamos tu relación emocional con la comida y patrones de comportamiento alimentario.
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
        progress_text.text("Paso 1 de 7: Evaluación de composición corporal")

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
    progress_text.text("Paso 2 de 7: Evaluación de capacidades funcionales")

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

# Ponderación: 40% FFMI, 40% funcional, 20% experiencia
puntaje_total = (puntos_ffmi / 5 * 0.4) + (puntos_funcional / 4 * 0.4) + (puntos_exp / 4 * 0.2)

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
    progress_text.text("Paso 3 de 7: Evaluación de actividad diaria")

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
    progress_text.text("Paso 4 de 7: Cálculo del efecto térmico")

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
    progress_text.text("Paso 5 de 7: Cálculo del gasto por ejercicio")

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

    # BLOQUE 6: Cuestionario de Patrones Alimenticios
with st.expander("🍽️ **Paso 6: Cuestionario de Patrones Alimenticios**", expanded=True):
    progress.progress(85)
    progress_text.text("Paso 6 de 7: Evaluación de patrones alimenticios")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🥗 Evalúa tus hábitos alimentarios actuales")
    
    # Initialize session state for dietary patterns
    if 'patrones_alimenticios' not in st.session_state:
        st.session_state.patrones_alimenticios = {}
    
    # Dietary patterns questions
    patrones_preguntas = {
        "frecuencia_comidas": {
            "pregunta": "¿Con qué frecuencia comes al día?",
            "opciones": ["1-2 comidas", "3 comidas", "4-5 comidas", "Más de 5 comidas", "Como constantemente/picoteo"]
        },
        "horarios_regulares": {
            "pregunta": "¿Mantienes horarios regulares de comida?",
            "opciones": ["Siempre, muy regulares", "Casi siempre", "A veces", "Raramente", "Nunca, como cuando puedo"]
        },
        "desayuno": {
            "pregunta": "¿Qué tan frecuentemente desayunas?",
            "opciones": ["Todos los días", "5-6 días/semana", "3-4 días/semana", "1-2 días/semana", "Nunca o casi nunca"]
        },
        "cena_tardía": {
            "pregunta": "¿Con qué frecuencia cenas después de las 9 PM?",
            "opciones": ["Nunca", "1-2 veces/semana", "3-4 veces/semana", "5-6 veces/semana", "Todos los días"]
        },
        "comida_procesada": {
            "pregunta": "¿Qué porcentaje de tu alimentación proviene de comida procesada/empaquetada?",
            "opciones": ["Menos del 10%", "10-25%", "25-50%", "50-75%", "Más del 75%"]
        },
        "preparación_comida": {
            "pregunta": "¿Con qué frecuencia preparas tu propia comida?",
            "opciones": ["Todos los días", "5-6 días/semana", "3-4 días/semana", "1-2 días/semana", "Nunca, siempre compro hecha"]
        },
        "verduras_frutas": {
            "pregunta": "¿Cuántas porciones de verduras y frutas consumes diariamente?",
            "opciones": ["5 o más porciones", "3-4 porciones", "2 porciones", "1 porción", "Menos de 1 porción"]
        },
        "agua_diaria": {
            "pregunta": "¿Cuántos litros de agua pura tomas al día?",
            "opciones": ["Más de 2.5 litros", "2-2.5 litros", "1.5-2 litros", "1-1.5 litros", "Menos de 1 litro"]
        },
        "alcohol": {
            "pregunta": "¿Con qué frecuencia consumes bebidas alcohólicas?",
            "opciones": ["Nunca", "Ocasionalmente (fiestas)", "1-2 veces/semana", "3-4 veces/semana", "Diariamente"]
        },
        "planificación": {
            "pregunta": "¿Planificas tus comidas con anticipación?",
            "opciones": ["Siempre, planifico toda la semana", "Casi siempre", "A veces", "Raramente", "Nunca, improviso"]
        }
    }
    
    # Display questions
    for key, pregunta_data in patrones_preguntas.items():
        respuesta = st.radio(
            pregunta_data["pregunta"],
            pregunta_data["opciones"],
            key=f"patron_{key}",
            help="Selecciona la opción que mejor describe tu situación actual"
        )
        st.session_state.patrones_alimenticios[key] = {
            "pregunta": pregunta_data["pregunta"],
            "respuesta": respuesta
        }
    
    st.success("✅ Cuestionario de patrones alimenticios completado")
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 7: Cuestionario de Alimentación Emocional
with st.expander("😋 **Paso 7: Cuestionario de Alimentación Emocional**", expanded=True):
    progress.progress(90)
    progress_text.text("Paso 7 de 7: Evaluación de alimentación emocional")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Evalúa tu relación emocional con la comida")
    
    # Initialize session state for emotional eating
    if 'alimentacion_emocional' not in st.session_state:
        st.session_state.alimentacion_emocional = {}
    
    # Emotional eating questions
    emocional_preguntas = {
        "comer_estresado": {
            "pregunta": "¿Comes más cuando te sientes estresado/a o ansioso/a?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        },
        "comer_aburrido": {
            "pregunta": "¿Comes cuando te aburres, aunque no tengas hambre?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        },
        "comer_triste": {
            "pregunta": "¿Recurres a la comida cuando te sientes triste o deprimido/a?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        },
        "comer_celebrar": {
            "pregunta": "¿Usas la comida para celebrar o premiarte?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        },
        "control_porciones": {
            "pregunta": "¿Qué tan difícil te resulta controlar las porciones cuando comes?",
            "opciones": ["Muy fácil, siempre controlo", "Fácil, casi siempre", "Moderado, a veces", "Difícil, raramente", "Muy difícil, nunca controlo"]
        },
        "comer_rapido": {
            "pregunta": "¿Con qué frecuencia comes muy rápido?",
            "opciones": ["Nunca, siempre despacio", "Raramente", "A veces", "Frecuentemente", "Siempre como rápido"]
        },
        "hambre_fisica": {
            "pregunta": "¿Puedes distinguir entre hambre física y hambre emocional?",
            "opciones": ["Siempre, muy claramente", "Casi siempre", "A veces", "Raramente", "Nunca, no distingo"]
        },
        "culpa_comer": {
            "pregunta": "¿Sientes culpa después de comer ciertos alimentos?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        },
        "comida_consuelo": {
            "pregunta": "¿Tienes alimentos específicos que consideras 'de consuelo'?",
            "opciones": ["No, no tengo", "Tengo pocos", "Tengo algunos", "Tengo varios", "Tengo muchos"]
        },
        "comer_social": {
            "pregunta": "¿Comes más de lo planeado en situaciones sociales?",
            "opciones": ["Nunca", "Raramente", "A veces", "Frecuentemente", "Siempre"]
        }
    }
    
    # Display questions
    for key, pregunta_data in emocional_preguntas.items():
        respuesta = st.radio(
            pregunta_data["pregunta"],
            pregunta_data["opciones"],
            key=f"emocional_{key}",
            help="Responde con honestidad sobre tu comportamiento habitual"
        )
        st.session_state.alimentacion_emocional[key] = {
            "pregunta": pregunta_data["pregunta"],
            "respuesta": respuesta
        }
    
    st.success("✅ Cuestionario de alimentación emocional completado")
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 8: Cálculo final con comparativa PSMF
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
            help="PSMF es muy efectivo pero requiere mucha disciplina. Las grasas están fijas en 40g diarios."
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
            deficit_psmf = int((1 - psmf_recs['calorias_dia']/GE) * 100) if GE > 0 else 40
            perdida_min, perdida_max = psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))
            multiplicador = psmf_recs.get('multiplicador', 8.3)
            perfil_grasa = psmf_recs.get('perfil_grasa', 'automatizado')
            grasa_fija = psmf_recs.get('grasa_g_fija', 40.0)
            
            st.markdown('<div class="content-card card-psmf">', unsafe_allow_html=True)
            st.markdown("#### ⚡ Protocolo PSMF Automatizado")
            st.metric("Déficit", f"~{deficit_psmf}%", "Agresivo")
            st.metric("Calorías", f"{psmf_recs['calorias_dia']:.0f} kcal/día")
            st.metric("Multiplicador", f"{multiplicador}", f"Perfil: {perfil_grasa}")
            st.metric("Pérdida esperada", f"{perdida_min}-{perdida_max} kg/semana")
            st.markdown(f"""
            **Características automáticas:**
            - 🔒 **Multiplicador automático:** {multiplicador} (según % grasa)
            - 🔒 **Grasas fijas:** {grasa_fija}g diarios (no modificables)
            - ⚠️ Proteína: {psmf_recs['proteina_g_dia']}g/día (1.8g/kg mínimo)
            - ⚠️ Carbos: resto de calorías (solo vegetales fibrosos)
            - ⚠️ Máximo 6-8 semanas de duración
            - ⚠️ Requiere supervisión médica
            - ⚠️ Suplementación necesaria
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    # FORZAR actualización de variables clave desde session_state
    peso = st.session_state.get("peso", 0)
    estatura = st.session_state.get("estatura", 0)
    grasa_corporal = st.session_state.get("grasa_corporal", 0)
    sexo = st.session_state.get("sexo", "Hombre")
    edad = st.session_state.get("edad", 0)

    # ========================================================================
    # CÁLCULO DE MACROS CENTRALIZADO - GARANTIZA CONSISTENCIA TOTAL
    # ========================================================================
    # 
    # Este enfoque centralizado asegura que todos los bloques de la aplicación 
    # muestren exactamente los mismos valores:
    # - Comparativa de planes
    # - Resumen de macronutrientes  
    # - Advertencias PSMF
    # - Email de resumen
    # - Proyecciones científicas
    #
    # AUTOMATIZACIÓN IMPLEMENTADA:
    # - PSMF: Multiplicador automático según % grasa + grasas fijas 40g
    # - Tradicional: Cálculo estándar con flexibilidad
    # ========================================================================
    
    macros = calcular_macros_centralizados(
        plan_elegido, 
        psmf_recs, 
        peso, 
        ingesta_calorica_tradicional, 
        tmb
    )
    
    # Extraer valores centralizados
    ingesta_calorica = macros['ingesta_calorica']
    proteina_g = macros['proteina_g']
    proteina_kcal = macros['proteina_kcal']
    grasa_g = macros['grasa_g']
    grasa_kcal = macros['grasa_kcal']
    carbo_g = macros['carbo_g']
    carbo_kcal = macros['carbo_kcal']
    
    # Mostrar advertencia específica según el tipo de plan
    if macros['tipo_plan'] == "PSMF":
        multiplicador = macros['multiplicador']
        perfil_grasa = macros['perfil_grasa']
        perdida_min, perdida_max = macros['perdida_rango']
        deficit_psmf = int((1 - ingesta_calorica/GE) * 100) if GE > 0 else 40
        
        fase = f"PSMF Automatizado - Pérdida rápida (déficit ~{deficit_psmf}%, multiplicador {multiplicador})"

        st.error(f"""
        ⚠️ **ADVERTENCIA IMPORTANTE SOBRE PSMF AUTOMATIZADO:**
        - Es un protocolo **MUY RESTRICTIVO** con cálculo automatizado basado en % grasa corporal
        - **Duración máxima:** 6-8 semanas
        - **Multiplicador automático:** {multiplicador} (perfil: {perfil_grasa})
        - **Proteína:** {proteina_g}g/día (1.8g/kg peso total)
        - **Grasas fijas:** {grasa_g}g/día (valor fijo, no modificable)
        - **Carbohidratos:** {carbo_g}g (solo de vegetales fibrosos)
        - **Pérdida proyectada:** {perdida_min}-{perdida_max} kg/semana
        - **Requiere:** Supervisión médica y análisis de sangre regulares
        - **Suplementación obligatoria:** Multivitamínico, omega-3, electrolitos, magnesio
        - **No apto para:** Personas con historial de TCA, problemas médicos o embarazo
        """)
    else:
        # Plan tradicional - verificar carbohidratos bajos
        if carbo_g < 50:
            st.warning(f"⚠️ Tus carbohidratos han quedado muy bajos ({carbo_g}g). Considera aumentar calorías o reducir grasa para una dieta más sostenible.")

    # --- DESGLOSE FINAL VISUAL CENTRALIZADO ---
    st.markdown("### 🍽️ Distribución de macronutrientes")
    st.write(f"- **Proteína:** {proteina_g}g ({proteina_kcal:.0f} kcal, {proteina_kcal/ingesta_calorica*100:.1f}%)")
    if macros['grasa_fija']:
        st.write(f"- **Grasas:** {grasa_g}g ({grasa_kcal:.0f} kcal, {grasa_kcal/ingesta_calorica*100:.1f}%) 🔒 *FIJAS*")
    else:
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
# Usar macros centralizados para el email (garantiza consistencia total)
try:
    # Recalcular macros usando la función centralizada para el email
    macros_email = calcular_macros_centralizados(
        plan_elegido if 'plan_elegido' in locals() else "",
        psmf_recs if 'psmf_recs' in locals() else {},
        peso,
        ingesta_calorica_tradicional if 'ingesta_calorica_tradicional' in locals() else 2000,
        tmb
    )
    
    # Extraer valores centralizados para el email
    ingesta_calorica_email = macros_email['ingesta_calorica']
    proteina_g_email = macros_email['proteina_g']
    proteina_kcal_email = macros_email['proteina_kcal']
    grasa_g_email = macros_email['grasa_g']
    grasa_kcal_email = macros_email['grasa_kcal']
    carbo_g_email = macros_email['carbo_g']
    carbo_kcal_email = macros_email['carbo_kcal']
    
    # Calcular porcentajes
    ratio_kcal_kg = ingesta_calorica_email/peso if peso > 0 else 0
    proteina_percent = round(proteina_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    grasa_percent = round(grasa_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    carbo_percent = round(carbo_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    
    # Información adicional para PSMF
    info_psmf = ""
    if macros_email['tipo_plan'] == "PSMF":
        multiplicador_email = macros_email['multiplicador']
        perfil_grasa_email = macros_email['perfil_grasa']
        info_psmf = f"""
- PROTOCOLO PSMF AUTOMATIZADO:
  * Multiplicador automático: {multiplicador_email} ({perfil_grasa_email})
  * Grasas fijas: {grasa_g_email}g (valor no modificable)
  * Pérdida proyectada: {macros_email['perdida_rango'][0]}-{macros_email['perdida_rango'][1]} kg/semana"""
        
except Exception as e:
    # Fallback a valores existentes en caso de error
    ingesta_calorica_email = ingesta_calorica if 'ingesta_calorica' in locals() else 2000
    proteina_g_email = proteina_g if 'proteina_g' in locals() else 100
    proteina_kcal_email = proteina_g_email * 4
    grasa_g_email = grasa_g if 'grasa_g' in locals() else 60
    grasa_kcal_email = grasa_g_email * 9
    carbo_g_email = carbo_g if 'carbo_g' in locals() else 200
    carbo_kcal_email = carbo_g_email * 4
    ratio_kcal_kg = ingesta_calorica_email/peso if peso > 0 else 0
    proteina_percent = round(proteina_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    grasa_percent = round(grasa_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    carbo_percent = round(carbo_kcal_email/ingesta_calorica_email*100, 1) if ingesta_calorica_email > 0 else 0
    info_psmf = ""

# Calculate additional safe values for email
try:
    imc = peso/(estatura/100)**2 if estatura > 0 else 0
except:
    imc = 0

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
PLAN NUTRICIONAL CALCULADO (CENTRALIZADO):
=====================================
- Fase: {fase}
- Factor FBEO: {fbeo:.2f}
- Ingesta calórica: {ingesta_calorica_email:.0f} kcal/día
- Ratio kcal/kg: {ratio_kcal_kg:.1f}

DISTRIBUCIÓN DE MACRONUTRIENTES (AUTOMATIZADA):
- Proteína: {proteina_g_email}g ({proteina_kcal_email:.0f} kcal) = {proteina_percent}%
- Grasas: {grasa_g_email}g ({grasa_kcal_email:.0f} kcal) = {grasa_percent}%
- Carbohidratos: {carbo_g_email}g ({carbo_kcal_email:.0f} kcal) = {carbo_percent}%

{info_psmf}

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

tabla_resumen += f"""

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

=====================================
PLAN TRADICIONAL - CÁLCULO DETALLADO:
=====================================
- Ingesta calórica tradicional: {ingesta_calorica_tradicional if 'ingesta_calorica_tradicional' in locals() else 'No calculado':.0f} kcal/día
- Déficit/Superávit: {porcentaje if 'porcentaje' in locals() else 0:+.0f}%
- Factor FBEO tradicional: {fbeo:.2f}

MACRONUTRIENTES PLAN TRADICIONAL:
"""

# Calculate traditional plan macros for email
try:
    macros_tradicional = calcular_macros_centralizados(
        "Plan Tradicional",
        {},  # No PSMF recommendations
        peso,
        ingesta_calorica_tradicional if 'ingesta_calorica_tradicional' in locals() else 2000,
        tmb
    )
    
    tabla_resumen += f"""- Proteína tradicional: {macros_tradicional['proteina_g']}g ({macros_tradicional['proteina_kcal']:.0f} kcal) = {round(macros_tradicional['proteina_kcal']/macros_tradicional['ingesta_calorica']*100, 1)}%
- Grasas tradicionales: {macros_tradicional['grasa_g']}g ({macros_tradicional['grasa_kcal']:.0f} kcal) = {round(macros_tradicional['grasa_kcal']/macros_tradicional['ingesta_calorica']*100, 1)}%
- Carbohidratos tradicionales: {macros_tradicional['carbo_g']}g ({macros_tradicional['carbo_kcal']:.0f} kcal) = {round(macros_tradicional['carbo_kcal']/macros_tradicional['ingesta_calorica']*100, 1)}%
"""
except:
    tabla_resumen += "- Error calculando macros tradicionales\n"

if psmf_recs.get("psmf_aplicable"):
    tabla_resumen += f"""
=====================================
PLAN PSMF - CÁLCULO DETALLADO:
=====================================
- Ingesta calórica PSMF: {psmf_recs['calorias_dia']:.0f} kcal/día
- Déficit PSMF: ~{int((1 - psmf_recs['calorias_dia']/GE) * 100) if GE > 0 else 40}%
- Multiplicador automático: {psmf_recs.get('multiplicador', 8.3)} ({psmf_recs.get('perfil_grasa', 'automatizado')})

MACRONUTRIENTES PLAN PSMF:
- Proteína PSMF: {psmf_recs['proteina_g_dia']}g ({psmf_recs['proteina_g_dia'] * 4:.0f} kcal) = {round(psmf_recs['proteina_g_dia'] * 4 / psmf_recs['calorias_dia'] * 100, 1)}%
- Grasas PSMF (FIJAS): {psmf_recs['grasa_g_fija']}g ({psmf_recs['grasa_g_fija'] * 9:.0f} kcal) = {round(psmf_recs['grasa_g_fija'] * 9 / psmf_recs['calorias_dia'] * 100, 1)}%
- Carbohidratos PSMF: {round((psmf_recs['calorias_dia'] - psmf_recs['proteina_g_dia'] * 4 - psmf_recs['grasa_g_fija'] * 9) / 4, 1)}g ({psmf_recs['calorias_dia'] - psmf_recs['proteina_g_dia'] * 4 - psmf_recs['grasa_g_fija'] * 9:.0f} kcal) = {round((psmf_recs['calorias_dia'] - psmf_recs['proteina_g_dia'] * 4 - psmf_recs['grasa_g_fija'] * 9) / psmf_recs['calorias_dia'] * 100, 1)}%
- Pérdida proyectada PSMF: {psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[0]}-{psmf_recs.get('perdida_semanal_kg', (0.6, 1.0))[1]} kg/semana
"""
else:
    tabla_resumen += f"""
=====================================
PLAN PSMF NO APLICABLE:
=====================================
- Razón: % grasa corporal no cumple criterios mínimos
- Criterio hombre: >18% grasa | Criterio mujer: >23% grasa
- Tu % grasa actual: {grasa_corregida:.1f}%
"""

# Indicate which plan was selected
plan_seleccionado_texto = plan_elegido if 'plan_elegido' in locals() and plan_elegido else "Plan tradicional"
tabla_resumen += f"""
=====================================
PLAN FINALMENTE ELEGIDO:
=====================================
** {plan_seleccionado_texto.upper()} **

=====================================
CUESTIONARIO DE PATRONES ALIMENTICIOS:
=====================================
"""

# Add dietary patterns questionnaire results
if hasattr(st.session_state, 'patrones_alimenticios') and st.session_state.patrones_alimenticios:
    for i, (key, data) in enumerate(st.session_state.patrones_alimenticios.items(), 1):
        tabla_resumen += f"{i}. {data['pregunta']}\n   Respuesta: {data['respuesta']}\n\n"
else:
    tabla_resumen += "No se completó el cuestionario de patrones alimenticios.\n\n"

tabla_resumen += f"""
=====================================
CUESTIONARIO DE ALIMENTACIÓN EMOCIONAL:
=====================================
"""

# Add emotional eating questionnaire results
if hasattr(st.session_state, 'alimentacion_emocional') and st.session_state.alimentacion_emocional:
    for i, (key, data) in enumerate(st.session_state.alimentacion_emocional.items(), 1):
        tabla_resumen += f"{i}. {data['pregunta']}\n   Respuesta: {data['respuesta']}\n\n"
else:
    tabla_resumen += "No se completó el cuestionario de alimentación emocional.\n\n"

tabla_resumen += """

=====================================
FECHA Y HORA DE EVALUACIÓN:
=====================================
Evaluación completada el: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

¡Gracias por completar la evaluación MUPAI!
Para cualquier consulta adicional, contacta con el equipo técnico.

=====================================
FIN DEL REPORTE
=====================================
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
    if st.button("📧 Terminar cuestionario y enviar resumen por email", key="enviar_email"):
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

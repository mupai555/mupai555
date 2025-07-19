import streamlit as st
from datetime import date
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64
import io
from PIL import Image
import requests

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="MUPAI - Cuestionario Digital",
    page_icon="💪",
    layout="centered"
)



# ---------- LOGO Y ESTILOS ----------
# URL del logo (debes subir tu logo a un servicio de hosting de imágenes)
LOGO_URL = "https://raw.githubusercontent.com/mupai555/mupai555/main/LOGO%20(1).png"

# Función para obtener imagen desde URL
@st.cache_data
def get_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except:
        pass
    return None

# ---------- ESTILOS PERSONALIZADOS MODERNOS ----------
st.markdown("""
    <style>
    /* === LAYOUT BASE === */
    .logo-container {
        text-align: center; 
        margin-bottom: 20px;
    }
    .logo-img {
        width: 340px; 
        max-width: 90vw;
    }
    .main {
        background-color: #191b1f;
    }
    .block-container {
        background-color: #23262b; 
        border-radius: 20px; 
        padding: 2.5rem;
        max-width: 900px;
        margin: auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6, p, .stTextInput > label, .stSelectbox > label, .stNumberInput > label {
        color: #fff !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }
    h1 {
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    h2 {
        font-weight: 600;
        font-size: 2rem;
        margin-bottom: 0.8rem;
    }
    h3 {
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 0.6rem;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #ffb300 0%, #ff8f00 100%); 
        color: #191b1f; 
        border-radius: 12px; 
        font-weight: 600;
        width: 100%;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 179, 0, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #fff 0%, #f5f5f5 100%); 
        color: #ff8f00;
        border: 2px solid #ffb300;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 179, 0, 0.4);
    }
    
    /* === CONTAINERS AND CARDS === */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 179, 0, 0.1) 0%, rgba(255, 143, 0, 0.1) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 179, 0, 0.2);
        text-align: center;
    }
    
    /* === ALERTS AND NOTIFICATIONS === */
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px;
        background-color: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border-color: rgba(76, 175, 80, 0.3);
    }
    .stInfo {
        background-color: rgba(33, 150, 243, 0.1);
        border-color: rgba(33, 150, 243, 0.3);
    }
    .stWarning {
        background-color: rgba(255, 152, 0, 0.1);
        border-color: rgba(255, 152, 0, 0.3);
    }
    .stError {
        background-color: rgba(244, 67, 54, 0.1);
        border-color: rgba(244, 67, 54, 0.3);
    }
    
    /* === FORM ELEMENTS === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #fff;
    }
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #ffb300;
        box-shadow: 0 0 0 2px rgba(255, 179, 0, 0.2);
    }
    
    /* === PROGRESS BAR === */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ffb300 0%, #ff8f00 100%);
        border-radius: 10px;
    }
    
    /* === CHECKBOXES === */
    .stCheckbox {
        color: #fff;
    }
    .stCheckbox > label > div {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* === METRICS === */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: rgba(255, 255, 255, 0.05);
        color: #fff;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #ffb300;
        color: #191b1f;
    }
    
    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 0 0 8px 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: none;
    }
    
    /* === MULTISELECT === */
    .stMultiSelect > div > div > div {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main > div {
        animation: fadeIn 0.6s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar logo
logo_image = get_image_from_url(LOGO_URL)
if logo_image:
    st.image(logo_image, width=340)
else:
    st.markdown("# MUPAI")

# ---------- PIE DE PÁGINA STREAMLIT ----------
def pie_streamlit():
    st.markdown("""
        <hr style="margin-top:40px; margin-bottom:8px; border:1px solid #444;">
        <div style='text-align: center; color: #fff; font-size: 0.95em;'>
            Dirigido por <b>Erick De Luna</b>, Lic. en Ciencias del Ejercicio (UANL), Maestría en Fuerza y Acondicionamiento Físico (FSI).
        </div>
    """, unsafe_allow_html=True)

# ---------- FUNCIONES PARA TABLAS ----------
def tabla_bf(genero):
    if genero == "Hombre":
        return [
            ("<6%", "Preparación concurso"),
            ("6-10%", "Atlético/competidor"),
            ("10-17%", "Normal saludable"),
            ("17-25%", "Sobrepeso"),
            (">25%", "Obesidad"),
        ]
    else:
        return [
            ("<14%", "Preparación concurso"),
            ("14-21%", "Atlética/competidora"),
            ("21-28%", "Normal saludable"),
            ("28-35%", "Sobrepeso"),
            (">35%", "Obesidad"),
        ]

def tabla_ffmi(genero):
    if genero == "Hombre":
        return [
            ("<18", "Novato"),
            ("18-20", "Intermedio"),
            ("20-22", "Avanzado"),
            ("22-25", "Elite (Natty max)"),
            (">25", "Posible uso de anabólicos"),
        ]
    else:
        return [
            ("<14", "Novata"),
            ("14-16", "Intermedia"),
            ("16-18", "Avanzada"),
            ("18-20", "Elite (Natty max)"),
            (">20", "Posible uso de anabólicos"),
        ]

def render_tabla(tabla):
    out = "| Rango | Nivel |\n|---|---|\n"
    for r, n in tabla:
        out += f"| {r} | {n} |\n"
    return out

# ---------- PDF CON PIE DE PÁGINA ----------
class PDFConPie(FPDF):
    def __init__(self, logo_image=None):
        super().__init__()
        self.logo_image = logo_image
        
    def header(self):
        if self.logo_image:
            try:
                # Guardar imagen temporalmente
                temp_logo = io.BytesIO()
                self.logo_image.save(temp_logo, format='PNG')
                temp_logo.seek(0)
                # Usar la imagen desde memoria
                self.image(temp_logo, x=60, y=8, w=90)
            except:
                # Si falla, solo poner texto
                self.set_font('Arial', 'B', 20)
                self.cell(0, 10, 'MUPAI', 0, 0, 'C')
        else:
            self.set_font('Arial', 'B', 20)
            self.cell(0, 10, 'MUPAI', 0, 0, 'C')
        self.ln(30)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(80,80,80)
        self.cell(0, 10, 'Dirigido por Erick De Luna, Lic. en Ciencias del Ejercicio (UANL), Maestría en Fuerza y Acondicionamiento Físico (FSI).', 0, 0, 'C')

def generar_pdf(usuario, resumen, tabla_bf_txt, tabla_ffmi_txt, logo_image=None):
    pdf = PDFConPie(logo_image)
    pdf.add_page()
    pdf.set_font("Arial", size=13)
    pdf.ln(35)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, "Datos personales", ln=True)
    for k, v in usuario.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Resumen de composición corporal", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in resumen.items():
        pdf.multi_cell(0, 8, f"{k}: {v}")
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Tabla de %BF", ln=True)
    pdf.set_font("Arial", size=10)
    for linea in tabla_bf_txt.splitlines()[2:]:
        pdf.cell(0, 8, linea, ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Tabla de FFMI", ln=True)
    pdf.set_font("Arial", size=10)
    for linea in tabla_ffmi_txt.splitlines()[2:]:
        pdf.cell(0, 8, linea, ln=True)
    return pdf.output(dest='S')

# ---------- ENVÍO DE EMAIL CON PDF ----------
def enviar_email(remitente, password, destinatario, asunto, body, pdf_bytes, pdf_filename):
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(body, 'html'))
    part = MIMEApplication(pdf_bytes, Name=pdf_filename)
    part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
    msg.attach(part)
    try:
        with smtplib.SMTP_SSL('smtp.zoho.com', 465) as server:
            server.login(remitente, password)
            server.sendmail(remitente, destinatario, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Error al enviar email: {str(e)}")
        return False

# ---------- CORRECCIÓN DE GRASA ----------
def corregir_grasa_omron_a_dexa(grasa_omron):
    tabla = {
        5.0: 2.5, 6.0: 3.5, 7.0: 4.5, 8.0: 5.5, 9.0: 6.5,
        10.0: 7.5, 11.0: 8.5, 12.0: 9.5, 13.0: 10.5, 14.0: 11.5,
        15.0: 13.5, 16.0: 14.5, 17.0: 15.5, 18.0: 16.5, 19.0: 17.5,
        20.0: 20.5, 21.0: 21.5, 22.0: 22.5, 23.0: 23.5, 24.0: 24.5,
        25.0: 27.0, 26.0: 28.0, 27.0: 29.0, 28.0: 30.0, 29.0: 31.0,
        30.0: 33.5, 31.0: 34.5, 32.0: 35.5, 33.0: 36.5, 34.0: 37.5,
        35.0: 40.0, 36.0: 41.0, 37.0: 42.0, 38.0: 43.0, 39.0: 44.0,
        40.0: 45.0
    }
    grasa_redondeada = round(float(grasa_omron))
    grasa_redondeada = min(max(grasa_redondeada, 5), 40)
    return tabla.get(grasa_redondeada, grasa_omron)

# ---------- SESSION STATE INITIALIZATION ----------
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# ---------- STEP CONFIGURATION ----------
STEPS = {
    1: {"title": "📝 Información Personal", "icon": "👤"},
    2: {"title": "📊 Composición Corporal", "icon": "⚖️"},
    3: {"title": "🏃‍♂️ Nivel de Actividad", "icon": "💪"},
    4: {"title": "🎯 Objetivos y Entrenamiento", "icon": "🎯"},
    5: {"title": "🍽️ Requerimientos Calóricos", "icon": "🔥"},
    6: {"title": "🥗 Recomendaciones Nutricionales", "icon": "🥗"},
    7: {"title": "📋 Resumen y Resultados", "icon": "📊"}
}

# ---------- NAVIGATION FUNCTIONS ----------
def go_to_step(step_number):
    st.session_state.current_step = step_number
    st.rerun()

def next_step():
    if st.session_state.current_step < len(STEPS):
        st.session_state.current_step += 1
        st.rerun()

def prev_step():
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1
        st.rerun()

# ---------- ENHANCED PROGRESS INDICATOR ----------
def render_progress_bar():
    current = st.session_state.current_step
    total = len(STEPS)
    
    # Modern progress bar with percentage
    progress = current / total
    st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #ffb300;">Progreso del Cuestionario</h4>
                <span style="color: #ffb300; font-weight: 600; font-size: 1.1rem;">{current}/{total} pasos</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)
    
    # Enhanced step indicators with better visual hierarchy
    st.markdown("<div style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    cols = st.columns(total)
    
    for i, (step_num, step_info) in enumerate(STEPS.items(), 1):
        with cols[i-1]:
            if i == current:
                st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem; background: linear-gradient(135deg, #ffb300, #ff8f00); 
                                border-radius: 12px; color: #191b1f; font-weight: 600; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem;">{step_info['icon']}</div>
                    </div>
                    <div style="text-align: center; color: #ffb300; font-weight: 600; font-size: 0.85rem;">
                        Paso {i}
                    </div>
                """, unsafe_allow_html=True)
            elif i < current:
                st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem; background: rgba(76, 175, 80, 0.2); 
                                border-radius: 12px; color: #4caf50; font-weight: 600; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem;">✅</div>
                    </div>
                    <div style="text-align: center; color: #4caf50; font-weight: 600; font-size: 0.85rem;">
                        Completado
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); 
                                border-radius: 12px; color: #888; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem;">{step_info['icon']}</div>
                    </div>
                    <div style="text-align: center; color: #888; font-size: 0.85rem;">
                        Paso {i}
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

# ---------- APP PRINCIPAL ----------
# Enhanced header with better visual hierarchy
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; 
                   background: linear-gradient(135deg, #ffb300, #ff8f00); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text;">
            📋 Cuestionario Digital MUPAI
        </h1>
        <p style="font-size: 1.3rem; color: #ffb300; font-weight: 600; margin-bottom: 0;">
            Digital Training Science
        </p>
        <p style="color: #aaa; font-size: 1rem; margin-top: 0.5rem;">
            Tu evaluación personalizada de composición corporal y nutrición
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Show progress
render_progress_bar()

# Enhanced current step display
current_step_info = STEPS[st.session_state.current_step]
st.markdown(f"""
    <div style="background: rgba(255, 179, 0, 0.1); border-radius: 16px; padding: 1.5rem; 
                border: 1px solid rgba(255, 179, 0, 0.3); margin-bottom: 2rem;">
        <h2 style="color: #ffb300; margin-bottom: 0.5rem; font-size: 2.2rem;">
            {current_step_info['icon']} {current_step_info['title']}
        </h2>
        <p style="color: #ccc; margin: 0; font-size: 1.1rem;">
            Paso {st.session_state.current_step} de {len(STEPS)}
        </p>
    </div>
""", unsafe_allow_html=True)

# ---------- STEP CONTENT ----------
if st.session_state.current_step == 1:
    # STEP 1: Personal Information
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">👋 ¡Bienvenido/a a MUPAI!</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    📝 Completa tu información personal básica para comenzar tu evaluación personalizada. 
                    Todos los campos marcados con (*) son obligatorios.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step1_form"):
            # Personal data section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">👤 Datos Personales</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="large")
            with col1:
                with st.container():
                    nombre = st.text_input("Nombre completo*", 
                                         value=st.session_state.form_data.get('nombre', ''),
                                         placeholder="Juan Pérez",
                                         help="Nombre completo como aparece en tu identificación")
                    edad = st.number_input("Edad*", 
                                         min_value=10, max_value=90, step=1, 
                                         value=st.session_state.form_data.get('edad', 25),
                                         help="Tu edad actual en años")
                    genero = st.selectbox("Género*", 
                                        ["Hombre", "Mujer"],
                                        index=0 if st.session_state.form_data.get('genero', 'Hombre') == 'Hombre' else 1,
                                        help="Selecciona tu género biológico para cálculos precisos")
            
            with col2:
                with st.container():
                    estatura = st.number_input("Estatura (cm)*", 
                                             min_value=120, max_value=230, step=1, 
                                             value=st.session_state.form_data.get('estatura', 170),
                                             help="Tu altura en centímetros")
                    peso = st.number_input("Peso (kg)*", 
                                         min_value=30.0, max_value=200.0, step=0.1, 
                                         value=st.session_state.form_data.get('peso', 70.0),
                                         help="Tu peso actual en kilogramos")
            
            # Contact information section
            st.markdown("""
                <div style="margin: 2.5rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">📧 Información de Contacto</h3>
                    <p style="color: #ccc; font-size: 0.95rem; margin-bottom: 1rem;">
                        Esta información nos permitirá enviarte tu reporte personalizado
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            email_usuario = st.text_input("Tu correo electrónico*", 
                                         value=st.session_state.form_data.get('email_usuario', ''),
                                         placeholder="ejemplo@email.com",
                                         help="Dirección de email donde recibirás tu reporte")
            telefono = st.text_input("Número de teléfono (opcional)", 
                                    value=st.session_state.form_data.get('telefono', ''),
                                    placeholder="+52 1234567890",
                                    help="Número de contacto opcional")
            
            # Terms and conditions section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">📋 Términos y Condiciones</h3>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📖 Leer Política de Privacidad y Términos de Uso"):
                st.markdown("""
                **Política de Privacidad:**
                - Tus datos personales son tratados con absoluta confidencialidad
                - La información se utiliza únicamente para generar tu reporte personalizado
                - No compartimos tus datos con terceros sin tu consentimiento
                - Puedes solicitar la eliminación de tus datos en cualquier momento
                
                **Términos de Uso:**
                - Las recomendaciones son de carácter informativo y educativo
                - Consulta siempre con un profesional de la salud antes de realizar cambios significativos
                - MUPAI no se hace responsable por el mal uso de las recomendaciones
                - Los resultados pueden variar según factores individuales
                """)
            
            descargo = st.checkbox("✅ He leído y acepto la política de privacidad y términos de uso",
                                  value=st.session_state.form_data.get('descargo', False),
                                  help="Debes aceptar los términos para continuar")
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("<div style='opacity: 0.5;'>⬅️ Primer paso</div>", unsafe_allow_html=True)
            with col2:
                continue_step1 = st.form_submit_button("➡️ Continuar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if continue_step1:
                # Enhanced validation
                missing_fields = []
                if not nombre: missing_fields.append("Nombre completo")
                if not edad: missing_fields.append("Edad")
                if not genero: missing_fields.append("Género")
                if not estatura: missing_fields.append("Estatura")
                if not peso: missing_fields.append("Peso")
                if not email_usuario: missing_fields.append("Correo electrónico")
                if not descargo: missing_fields.append("Aceptación de términos")
                
                if missing_fields:
                    st.error(f"❌ Por favor, completa los siguientes campos obligatorios: {', '.join(missing_fields)}")
                else:
                    # Save data and show success message
                    st.session_state.form_data.update({
                        'nombre': nombre,
                        'edad': edad,
                        'genero': genero,
                        'estatura': estatura,
                        'peso': peso,
                        'email_usuario': email_usuario,
                        'telefono': telefono,
                        'descargo': descargo
                    })
                    st.success("✅ ¡Información guardada correctamente! Avanzando al siguiente paso...")
                    next_step()

elif st.session_state.current_step == 2:
    # STEP 2: Body Composition
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">⚖️ Análisis de Composición Corporal</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    Proporciona información sobre tu composición corporal actual. Esta información es crucial 
                    para calcular tus métricas de salud y generar recomendaciones precisas.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step2_form"):
            # Body composition measurement section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">📊 Medición de Grasa Corporal</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1], gap="large")
            
            with col1:
                metodo_grasa = st.selectbox("¿Qué método usaste para medir tu porcentaje de grasa?", 
                                           ["Omron HBF-516 (BIA)", "DEXA (Gold Standard)"],
                                           index=0 if st.session_state.form_data.get('metodo_grasa', 'Omron HBF-516 (BIA)') == 'Omron HBF-516 (BIA)' else 1,
                                           help="Selecciona el método que usaste para medir tu grasa corporal")
                
                grasa_reportada = st.number_input("Porcentaje de grasa reportado (%)", 
                                                min_value=5.0, max_value=50.0, step=0.1, 
                                                value=st.session_state.form_data.get('grasa_reportada', 20.0),
                                                help="El valor exacto que te mostró tu dispositivo o estudio")
            
            with col2:
                # Visual feedback based on method
                if st.session_state.form_data.get('metodo_grasa', 'Omron HBF-516 (BIA)') == 'Omron HBF-516 (BIA)':
                    st.markdown("""
                        <div class="metric-card">
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">⚡ BIA</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                Ajustaremos automáticamente tu valor para mayor precisión
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="metric-card">
                            <h4 style="color: #4caf50; margin-bottom: 0.5rem;">🏆 DEXA</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                El estándar de oro en medición corporal
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Educational content in expandable section
            with st.expander("ℹ️ ¿Cómo interpretar estos valores? 📚"):
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: #ffb300;">🔬 Métodos de medición de grasa corporal:</h4>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #ffb300;">⚡ Omron HBF-516 (BIA)</h5>
                        <p style="color: #ccc;">
                            <strong>Bioimpedancia eléctrica:</strong> Conveniente y accesible, pero puede sobreestimar 
                            el porcentaje de grasa corporal. Factores como hidratación, hora del día y comidas recientes 
                            pueden afectar los resultados.
                        </p>
                        <p style="color: #4caf50;"><strong>✅ Ventajas:</strong> Rápido, económico, fácil de usar</p>
                        <p style="color: #ff9800;"><strong>⚠️ Limitaciones:</strong> Menos preciso, afectado por hidratación</p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #ffb300;">🏆 DEXA (Densitometría)</h5>
                        <p style="color: #ccc;">
                            <strong>Estándar de oro:</strong> La medición más precisa disponible. Utiliza rayos X 
                            de baja energía para distinguir entre hueso, músculo y grasa con alta precisión.
                        </p>
                        <p style="color: #4caf50;"><strong>✅ Ventajas:</strong> Máxima precisión, no afectado por hidratación</p>
                        <p style="color: #ff9800;"><strong>⚠️ Limitaciones:</strong> Más costoso, requiere equipo especializado</p>
                    </div>
                    
                    <div style="background: rgba(255, 179, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffb300;">
                        <p style="color: #ffb300; margin: 0;"><strong>💡 Nota importante:</strong> 
                        Si usaste Omron, aplicaremos automáticamente una corrección basada en estudios científicos 
                        para obtener un valor más cercano al DEXA y darte recomendaciones más precisas.</p>
                    </div>
                </div>
                """)
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                prev_step2 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
            with col2:
                continue_step2 = st.form_submit_button("➡️ Continuar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if prev_step2:
                prev_step()
            elif continue_step2:
                st.session_state.form_data.update({
                    'metodo_grasa': metodo_grasa,
                    'grasa_reportada': grasa_reportada
                })
                st.success("✅ ¡Datos de composición corporal guardados! Continuando...")
                next_step()

elif st.session_state.current_step == 3:
    # STEP 3: Activity Level
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">💪 Evaluación de Actividad Física</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    Evalúa tu nivel de actividad física actual para personalizar tus recomendaciones calóricas 
                    y nutricionales. Esta información es clave para calcular tu gasto energético total.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step3_form"):
            # Work activity section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">💼 Actividad Laboral</h3>
                </div>
            """, unsafe_allow_html=True)
            
            actividad_trabajo = st.selectbox("¿Cuál describe mejor tu trabajo/actividad diaria?",
                                           ["Sedentario (oficina, computadora)", 
                                            "Ligeramente activo (caminar ocasionalmente)",
                                            "Moderadamente activo (de pie frecuentemente)",
                                            "Muy activo (trabajo físico)"],
                                           index=0,
                                           help="Selecciona el nivel que mejor describe tu actividad durante las horas de trabajo")
            
            # Exercise section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">🏋️‍♂️ Rutina de Ejercicio</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                ejercicio_frecuencia = st.selectbox("¿Con qué frecuencia haces ejercicio?",
                                                  ["No hago ejercicio",
                                                   "1-2 veces por semana",
                                                   "3-4 veces por semana", 
                                                   "5-6 veces por semana",
                                                   "Todos los días"],
                                                  index=2,
                                                  help="Incluye cualquier actividad física estructurada")
                
                ejercicio_intensidad = st.selectbox("¿Cuál es la intensidad de tu ejercicio típico?",
                                                  ["Ligero (caminar, yoga suave)",
                                                   "Moderado (trotar, natación, pesas ligeras)",
                                                   "Vigoroso (correr, crossfit, pesas pesadas)",
                                                   "Muy intenso (deportes competitivos, entrenamiento atlético)"],
                                                  index=1,
                                                  help="Considera la intensidad promedio de tus entrenamientos")
            
            with col2:
                ejercicio_duracion = st.number_input("Duración promedio de cada sesión de ejercicio (minutos)", 
                                                   min_value=0, max_value=300, step=15, value=60,
                                                   help="Tiempo total incluyendo calentamiento y enfriamiento")
                
                # Visual activity summary
                st.markdown("""
                    <div class="metric-card" style="margin-top: 1rem;">
                        <h4 style="color: #ffb300; margin-bottom: 0.5rem;">📊 Tu Perfil</h4>
                        <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                            Usaremos esta información para calcular tu factor de actividad personalizado
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Educational content in expandable section
            with st.expander("ℹ️ ¿Por qué es importante el nivel de actividad? 📚"):
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: #ffb300;">🔥 El nivel de actividad afecta directamente:</h4>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #4caf50;">📈 Gasto calórico total (TDEE)</h5>
                        <p style="color: #ccc;">
                            Tu nivel de actividad determina cuántas calorías quemas diariamente. Esto incluye 
                            tanto tu trabajo como tu ejercicio estructurado.
                        </p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #4caf50;">🥗 Requerimientos nutricionales</h5>
                        <p style="color: #ccc;">
                            Mayor actividad significa mayores necesidades de macronutrientes, especialmente 
                            carbohidratos para energía y proteínas para recuperación.
                        </p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #4caf50;">🎯 Objetivos realistas</h5>
                        <p style="color: #ccc;">
                            Establecemos metas alcanzables según tu estilo de vida actual, evitando 
                            cambios demasiado drásticos que son difíciles de mantener.
                        </p>
                    </div>
                    
                    <div style="background: rgba(255, 179, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffb300;">
                        <p style="color: #ffb300; margin: 0;"><strong>💡 Consejo:</strong> 
                        Sé honesto/a con tu nivel actual de actividad. Es mejor ser realista y construir 
                        gradualmente que sobreestimar y frustrarse.</p>
                    </div>
                </div>
                """)
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                prev_step3 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
            with col2:
                continue_step3 = st.form_submit_button("➡️ Continuar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if prev_step3:
                prev_step()
            elif continue_step3:
                st.session_state.form_data.update({
                    'actividad_trabajo': actividad_trabajo,
                    'ejercicio_frecuencia': ejercicio_frecuencia,
                    'ejercicio_intensidad': ejercicio_intensidad,
                    'ejercicio_duracion': ejercicio_duracion
                })
                st.success("✅ ¡Perfil de actividad guardado! Continuando...")
                next_step()

elif st.session_state.current_step == 4:
    # STEP 4: Training Goals and Experience
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">🎯 Objetivos y Experiencia de Entrenamiento</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    Define tus objetivos principales y experiencia para crear un plan completamente personalizado. 
                    Esta información nos ayuda a establecer expectativas realistas y estrategias efectivas.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step4_form"):
            # Goals section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">🎯 Tu Objetivo Principal</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1], gap="large")
            
            with col1:
                objetivo_principal = st.selectbox("¿Cuál es tu objetivo principal?",
                                                ["Perder grasa corporal",
                                                 "Ganar masa muscular",
                                                 "Mantener peso actual",
                                                 "Mejorar rendimiento deportivo",
                                                 "Mejorar salud general"],
                                                index=0,
                                                help="Selecciona el objetivo más importante para ti en este momento")
            
            with col2:
                # Visual goal indicator
                goal_icons = {
                    "Perder grasa corporal": "🔥",
                    "Ganar masa muscular": "💪", 
                    "Mantener peso actual": "⚖️",
                    "Mejorar rendimiento deportivo": "🏃‍♂️",
                    "Mejorar salud general": "❤️"
                }
                selected_goal = st.session_state.form_data.get('objetivo_principal', 'Perder grasa corporal')
                st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #ffb300; margin-bottom: 0.5rem; font-size: 3rem;">
                            {goal_icons.get(objetivo_principal, "🎯")}
                        </h2>
                        <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                            Tu objetivo seleccionado
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Experience and availability section
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">💡 Experiencia y Disponibilidad</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                experiencia_entrenamiento = st.selectbox("¿Cuál es tu experiencia con el entrenamiento?",
                                                        ["Principiante (menos de 6 meses)",
                                                         "Novato (6 meses - 2 años)",
                                                         "Intermedio (2-5 años)",
                                                         "Avanzado (más de 5 años)"],
                                                        index=1,
                                                        help="Tu experiencia total con entrenamiento estructurado")
                
                tiempo_disponible = st.selectbox("¿Cuánto tiempo puedes dedicar al entrenamiento por semana?",
                                               ["Menos de 3 horas",
                                                "3-5 horas",
                                                "5-8 horas",
                                                "Más de 8 horas"],
                                               index=1,
                                               help="Tiempo total disponible para entrenamiento semanal")
            
            with col2:
                tiempo_objetivo = st.selectbox("¿En cuánto tiempo esperas ver resultados significativos?",
                                             ["1-2 meses",
                                              "3-4 meses", 
                                              "5-6 meses",
                                              "Más de 6 meses"],
                                             index=1,
                                             help="Timeline realista para ver cambios notables")
                
                # Experience level indicator
                exp_colors = {
                    "Principiante (menos de 6 meses)": "#ff9800",
                    "Novato (6 meses - 2 años)": "#ffb300",
                    "Intermedio (2-5 años)": "#4caf50", 
                    "Avanzado (más de 5 años)": "#2196f3"
                }
                exp_color = exp_colors.get(experiencia_entrenamiento, "#ffb300")
                st.markdown(f"""
                    <div class="metric-card" style="border-color: {exp_color};">
                        <h4 style="color: {exp_color}; margin-bottom: 0.5rem;">📊 Nivel</h4>
                        <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                            {experiencia_entrenamiento.split(' ')[0]}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Limitations section  
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">⚠️ Limitaciones y Preferencias</h3>
                </div>
            """, unsafe_allow_html=True)
            
            limitaciones = st.multiselect("¿Tienes alguna limitación física o preferencia? (opcional)",
                                        ["Lesión de rodilla",
                                         "Lesión de espalda",
                                         "Lesión de hombro",
                                         "Problemas cardiovasculares",
                                         "Prefiero entrenar en casa",
                                         "Solo ejercicios de peso corporal",
                                         "Ninguna"],
                                        help="Selecciona todas las que apliquen para personalizar tu plan")
            
            # Educational content in expandable section
            with st.expander("ℹ️ Estableciendo expectativas realistas 📚"):
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: #ffb300;">⏰ Cronogramas típicos para resultados:</h4>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #ff9800;">🔥 Pérdida de grasa</h5>
                        <p style="color: #ccc;">
                            <strong>0.5-1kg por semana</strong> es sostenible y saludable. Pérdidas más rápidas 
                            pueden comprometer la masa muscular y ser difíciles de mantener.
                        </p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #4caf50;">💪 Ganancia muscular</h5>
                        <p style="color: #ccc;">
                            <strong>Principiantes:</strong> 0.5-1kg por mes<br>
                            <strong>Intermedios:</strong> 0.25-0.5kg por mes<br>
                            <strong>Avanzados:</strong> 0.1-0.25kg por mes
                        </p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #2196f3;">👁️ Cambios visibles</h5>
                        <p style="color: #ccc;">
                            <strong>4-6 semanas</strong> para notar cambios con un plan consistente<br>
                            <strong>8-12 semanas</strong> para cambios evidentes para otros
                        </p>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="color: #9c27b0;">🔄 Transformaciones significativas</h5>
                        <p style="color: #ccc;">
                            <strong>3-6 meses</strong> de dedicación constante para cambios dramáticos<br>
                            <strong>1-2 años</strong> para transformaciones completas del physique
                        </p>
                    </div>
                    
                    <div style="background: rgba(255, 179, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffb300;">
                        <p style="color: #ffb300; margin: 0;"><strong>🎯 Clave del éxito:</strong> 
                        La consistencia supera a la perfección. Es mejor un plan bueno que sigas al 80% 
                        que un plan perfecto que abandones a las 2 semanas.</p>
                    </div>
                </div>
                """)
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                prev_step4 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
            with col2:
                continue_step4 = st.form_submit_button("➡️ Continuar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if prev_step4:
                prev_step()
            elif continue_step4:
                st.session_state.form_data.update({
                    'objetivo_principal': objetivo_principal,
                    'experiencia_entrenamiento': experiencia_entrenamiento,
                    'tiempo_disponible': tiempo_disponible,
                    'limitaciones': limitaciones,
                    'tiempo_objetivo': tiempo_objetivo
                })
                st.success("✅ ¡Objetivos y experiencia guardados! Continuando...")
                next_step()

elif st.session_state.current_step == 5:
    # STEP 5: Caloric Requirements and Deficit/Surplus
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">🔥 Cálculo de Necesidades Calóricas</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    Calculamos tus necesidades calóricas personalizadas basadas en tu metabolismo, actividad 
                    y objetivos. Estos cálculos forman la base de tu estrategia nutricional.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step5_form"):
            # Calculate BMR and TDEE based on collected data
            if st.session_state.form_data:
                peso = st.session_state.form_data.get('peso', 70)
                estatura = st.session_state.form_data.get('estatura', 170)
                edad = st.session_state.form_data.get('edad', 25)
                genero = st.session_state.form_data.get('genero', 'Hombre')
                
                # Mifflin-St Jeor Equation
                if genero == "Hombre":
                    bmr = (10 * peso) + (6.25 * estatura) - (5 * edad) + 5
                else:
                    bmr = (10 * peso) + (6.25 * estatura) - (5 * edad) - 161
                
                # Activity multiplier based on step 3 data
                actividad_trabajo = st.session_state.form_data.get('actividad_trabajo', 'Sedentario (oficina, computadora)')
                ejercicio_frecuencia = st.session_state.form_data.get('ejercicio_frecuencia', '3-4 veces por semana')
                
                # Calculate activity factor
                base_activity = {
                    "Sedentario (oficina, computadora)": 1.2,
                    "Ligeramente activo (caminar ocasionalmente)": 1.375,
                    "Moderadamente activo (de pie frecuentemente)": 1.55,
                    "Muy activo (trabajo físico)": 1.725
                }.get(actividad_trabajo, 1.2)
                
                exercise_bonus = {
                    "No hago ejercicio": 0,
                    "1-2 veces por semana": 0.1,
                    "3-4 veces por semana": 0.2,
                    "5-6 veces por semana": 0.3,
                    "Todos los días": 0.4
                }.get(ejercicio_frecuencia, 0.2)
                
                activity_factor = base_activity + exercise_bonus
                tdee = bmr * activity_factor
                
                # Enhanced metabolic calculations display
                st.markdown("""
                    <div style="margin: 2rem 0 1rem 0;">
                        <h3 style="color: #ffb300;">📊 Tus Cálculos Metabólicos</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Enhanced metrics display
                col1, col2, col3 = st.columns(3, gap="large")
                with col1:
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #4caf50;">
                            <h2 style="color: #4caf50; margin-bottom: 0.5rem; font-size: 2.5rem;">{bmr:.0f}</h2>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">BMR</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                Metabolismo Basal<br>
                                <small>Energía en reposo</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #2196f3;">
                            <h2 style="color: #2196f3; margin-bottom: 0.5rem; font-size: 2.5rem;">{tdee:.0f}</h2>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">TDEE</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                Gasto Total Diario<br>
                                <small>Incluye actividad</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    factor_pct = (activity_factor - 1) * 100
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #ff9800;">
                            <h2 style="color: #ff9800; margin-bottom: 0.5rem; font-size: 2.5rem;">+{factor_pct:.0f}%</h2>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Factor</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                Actividad<br>
                                <small>Sobre BMR</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Goal-specific caloric adjustment
            objetivo = st.session_state.form_data.get('objetivo_principal', 'Mantener peso actual')
            
            st.markdown("""
                <div style="margin: 2rem 0 1rem 0;">
                    <h3 style="color: #ffb300;">🎯 Estrategia Calórica</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Smart recommendations based on goal
            if objetivo == "Perder grasa corporal":
                st.info("🔥 **Para pérdida de grasa**: Recomendamos un déficit calórico moderado para preservar masa muscular")
                deficit_surplus = st.selectbox("Ajuste calórico recomendado:", 
                                             ["Déficit moderado (-300 kcal/día)", 
                                              "Déficit agresivo (-500 kcal/día)",
                                              "Déficit suave (-200 kcal/día)"], 
                                             index=0,
                                             help="Un déficit moderado es óptimo para la mayoría de personas")
            elif objetivo == "Ganar masa muscular":
                st.info("💪 **Para ganancia muscular**: Recomendamos un superávit controlado para minimizar ganancia de grasa")
                deficit_surplus = st.selectbox("Ajuste calórico recomendado:",
                                             ["Superávit moderado (+300 kcal/día)",
                                              "Superávit suave (+200 kcal/día)",
                                              "Superávit agresivo (+500 kcal/día)"], 
                                             index=0,
                                             help="Un superávit moderado maximiza ganancia muscular vs grasa")
            else:
                deficit_surplus = st.selectbox("Ajuste calórico según tu objetivo:",
                                             ["Déficit agresivo (-500 kcal/día)",
                                              "Déficit moderado (-300 kcal/día)", 
                                              "Déficit suave (-200 kcal/día)",
                                              "Mantenimiento (0 kcal)",
                                              "Superávit suave (+200 kcal/día)",
                                              "Superávit moderado (+300 kcal/día)",
                                              "Superávit agresivo (+500 kcal/día)"],
                                             index=3,
                                             help="Selecciona la estrategia que mejor se adapte a tu objetivo")
            
            # Calculate target calories
            adjustment = {
                "Déficit agresivo (-500 kcal/día)": -500,
                "Déficit moderado (-300 kcal/día)": -300,
                "Déficit suave (-200 kcal/día)": -200,
                "Mantenimiento (0 kcal)": 0,
                "Superávit suave (+200 kcal/día)": 200,
                "Superávit moderado (+300 kcal/día)": 300,
                "Superávit agresivo (+500 kcal/día)": 500
            }.get(deficit_surplus, 0)
            
            target_calories = tdee + adjustment
            
            # Enhanced target calories display
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255, 179, 0, 0.2), rgba(255, 143, 0, 0.2)); 
                            border-radius: 16px; padding: 2rem; margin: 2rem 0; text-align: center;
                            border: 2px solid rgba(255, 179, 0, 0.5);">
                    <h2 style="color: #ffb300; margin-bottom: 1rem;">🎯 Tu Objetivo Calórico Diario</h2>
                    <h1 style="color: #fff; font-size: 3.5rem; margin: 0.5rem 0; font-weight: 700;">
                        {target_calories:.0f} <span style="font-size: 2rem;">kcal</span>
                    </h1>
                    <p style="color: #ccc; font-size: 1.2rem; margin: 0;">
                        {deficit_surplus} • {adjustment:+.0f} kcal del TDEE
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Educational content in expandable section
            with st.expander("ℹ️ Entendiendo tu gasto calórico 📚"):
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: #ffb300;">🔬 Desglose científico de tu metabolismo:</h4>
                    
                    <div style="margin: 1.5rem 0;">
                        <h5 style="color: #4caf50;">🏠 BMR - Metabolismo Basal ({bmr:.0f} kcal)</h5>
                        <p style="color: #ccc;">
                            La energía que tu cuerpo necesita para funciones vitales en reposo absoluto: 
                            respiración, circulación, producción celular, procesamiento de nutrientes.
                        </p>
                        <p style="color: #888; font-size: 0.9rem;">
                            <strong>Representa ~{(bmr/tdee)*100:.0f}% de tu gasto total</strong>
                        </p>
                    </div>
                    
                    <div style="margin: 1.5rem 0;">
                        <h5 style="color: #2196f3;">🔥 Actividad Diaria (+{(tdee-bmr):.0f} kcal)</h5>
                        <p style="color: #ccc;">
                            Energía adicional por tu trabajo ({actividad_trabajo.split(' ')[0]}) 
                            y ejercicio ({ejercicio_frecuencia}).
                        </p>
                        <p style="color: #888; font-size: 0.9rem;">
                            <strong>Factor de actividad: {activity_factor:.2f}x del BMR</strong>
                        </p>
                    </div>
                    
                    <div style="margin: 1.5rem 0;">
                        <h5 style="color: #ff9800;">🎯 Tu Estrategia ({deficit_surplus})</h5>
                        <p style="color: #ccc;">
                            Objetivo calórico: <strong>{target_calories:.0f} kcal/día</strong><br>
                            Diferencia del TDEE: <strong>{adjustment:+.0f} kcal/día</strong><br>
                            Cambio semanal esperado: <strong>{abs(adjustment)*7/7700:.2f} kg/semana</strong>
                        </p>
                    </div>
                    
                    <div style="background: rgba(255, 179, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffb300;">
                        <p style="color: #ffb300; margin: 0;"><strong>💡 Importante:</strong> 
                        Estos cálculos son un punto de partida excelente. Tu cuerpo puede responder 
                        ligeramente diferente, así que ajustaremos según tu progreso real.</p>
                    </div>
                </div>
                """)
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                prev_step5 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
            with col2:
                continue_step5 = st.form_submit_button("➡️ Continuar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if prev_step5:
                prev_step()
            elif continue_step5:
                st.session_state.form_data.update({
                    'bmr': bmr,
                    'tdee': tdee,
                    'activity_factor': activity_factor,
                    'deficit_surplus': deficit_surplus,
                    'adjustment': adjustment,
                    'target_calories': target_calories
                })
                st.success("✅ ¡Estrategia calórica establecida! Continuando...")
                next_step()

elif st.session_state.current_step == 6:
    # STEP 6: Macronutrient Recommendations
    with st.container():
        # Enhanced intro section
        st.markdown("""
            <div class="info-card">
                <h3 style="color: #ffb300; margin-bottom: 1rem;">🥗 Plan Nutricional Personalizado</h3>
                <p style="color: #ccc; font-size: 1.1rem; margin: 0;">
                    Recomendaciones de macronutrientes diseñadas específicamente para tu objetivo, peso corporal 
                    y nivel de actividad. Este plan optimizará tu composición corporal y rendimiento.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("step6_form"):
            if st.session_state.form_data:
                target_calories = st.session_state.form_data.get('target_calories', 2000)
                peso = st.session_state.form_data.get('peso', 70)
                objetivo = st.session_state.form_data.get('objetivo_principal', 'Mantener peso actual')
                
                # Macronutrient calculations based on goal
                if objetivo == "Perder grasa corporal":
                    # Higher protein for satiety and muscle preservation
                    protein_g_per_kg = 2.2
                    fat_percentage = 25
                elif objetivo == "Ganar masa muscular":
                    # Adequate protein for muscle building
                    protein_g_per_kg = 2.0
                    fat_percentage = 25
                elif objetivo == "Mejorar rendimiento deportivo":
                    # Higher carbs for performance
                    protein_g_per_kg = 1.8
                    fat_percentage = 20
                else:
                    # Balanced approach
                    protein_g_per_kg = 1.8
                    fat_percentage = 25
                
                # Calculate macros
                protein_g = peso * protein_g_per_kg
                protein_calories = protein_g * 4
                
                fat_calories = target_calories * (fat_percentage / 100)
                fat_g = fat_calories / 9
                
                carb_calories = target_calories - protein_calories - fat_calories
                carb_g = carb_calories / 4
                
                # Enhanced macronutrient display
                st.markdown("""
                    <div style="margin: 2rem 0 1rem 0;">
                        <h3 style="color: #ffb300;">🎯 Tu Distribución de Macronutrientes</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3, gap="large")
                with col1:
                    protein_pct = (protein_calories / target_calories) * 100
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #e91e63;">
                            <h2 style="color: #e91e63; margin-bottom: 0.5rem; font-size: 2.5rem;">🥩</h2>
                            <h3 style="color: #fff; margin-bottom: 0.5rem;">{protein_g:.0f}g</h3>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Proteínas</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                {protein_pct:.0f}% • {protein_calories:.0f} kcal<br>
                                <small>{protein_g_per_kg}g por kg de peso</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    carb_pct = (carb_calories / target_calories) * 100
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #ff9800;">
                            <h2 style="color: #ff9800; margin-bottom: 0.5rem; font-size: 2.5rem;">🍞</h2>
                            <h3 style="color: #fff; margin-bottom: 0.5rem;">{carb_g:.0f}g</h3>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Carbohidratos</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                {carb_pct:.0f}% • {carb_calories:.0f} kcal<br>
                                <small>Energía y rendimiento</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    fat_pct = (fat_calories / target_calories) * 100
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: #4caf50;">
                            <h2 style="color: #4caf50; margin-bottom: 0.5rem; font-size: 2.5rem;">🥑</h2>
                            <h3 style="color: #fff; margin-bottom: 0.5rem;">{fat_g:.0f}g</h3>
                            <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Grasas</h4>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                {fat_pct:.0f}% • {fat_calories:.0f} kcal<br>
                                <small>Hormonas y vitaminas</small>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Meal timing section
                st.markdown("""
                    <div style="margin: 2.5rem 0 1rem 0;">
                        <h3 style="color: #ffb300;">⏰ Distribución de Comidas</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1], gap="large")
                
                with col1:
                    meals = st.selectbox("¿Cuántas comidas prefieres hacer al día?",
                                        ["3 comidas principales",
                                         "4 comidas (3 principales + 1 snack)",
                                         "5 comidas (3 principales + 2 snacks)",
                                         "6 comidas pequeñas"],
                                        help="Elige la frecuencia que mejor se adapte a tu estilo de vida")
                    
                    num_meals = {
                        "3 comidas principales": 3,
                        "4 comidas (3 principales + 1 snack)": 4, 
                        "5 comidas (3 principales + 2 snacks)": 5,
                        "6 comidas pequeñas": 6
                    }.get(meals, 4)
                    
                    calories_per_meal = target_calories / num_meals
                    protein_per_meal = protein_g / num_meals
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: #ffb300; margin-bottom: 1rem;">🍽️ Por Comida</h4>
                            <p style="color: #fff; font-size: 1.1rem; margin: 0.5rem 0;">
                                <strong>{calories_per_meal:.0f} kcal</strong>
                            </p>
                            <p style="color: #e91e63; font-size: 1rem; margin: 0.5rem 0;">
                                <strong>{protein_per_meal:.0f}g proteína</strong>
                            </p>
                            <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                                {num_meals} comidas/día
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Hydration and supplements section
                st.markdown("""
                    <div style="margin: 2.5rem 0 1rem 0;">
                        <h3 style="color: #ffb300;">💧 Hidratación y Suplementos</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    hidratacion = st.selectbox("¿Cuánta agua bebes normalmente al día?",
                                             ["Menos de 1 litro",
                                              "1-2 litros",
                                              "2-3 litros", 
                                              "Más de 3 litros"],
                                             index=1,
                                             help="La hidratación afecta rendimiento y recuperación")
                
                with col2:
                    suplementos = st.multiselect("¿Qué suplementos usas actualmente? (opcional)",
                                               ["Proteína en polvo",
                                                "Creatina",
                                                "Multivitamínico",
                                                "Omega-3",
                                                "Pre-entreno",
                                                "BCAA",
                                                "Ninguno"],
                                               help="Nos ayuda a personalizar las recomendaciones")
                
                # Enhanced educational content
                with st.expander("💡 Consejos nutricionales personalizados 📚"):
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.02); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                        <h4 style="color: #ffb300;">🎯 Estrategia específica para: {objetivo}</h4>
                        
                        <div style="margin: 1.5rem 0;">
                            <h5 style="color: #e91e63;">🥩 Proteínas ({protein_g:.0f}g/día)</h5>
                            <p style="color: #ccc;">
                                <strong>Objetivo:</strong> {protein_g_per_kg}g por kg de peso corporal<br>
                                <strong>Fuentes principales:</strong> Pollo, pescado, huevos, lácteos, legumbres<br>
                                <strong>Post-entreno:</strong> 20-30g de proteína rápida (whey protein, claras)<br>
                                <strong>Distribución:</strong> ~{protein_per_meal:.0f}g en cada comida principal
                            </p>
                        </div>
                        
                        <div style="margin: 1.5rem 0;">
                            <h5 style="color: #ff9800;">🍞 Carbohidratos ({carb_g:.0f}g/día)</h5>
                            <p style="color: #ccc;">
                                <strong>Pre-entreno:</strong> 30-50g carbohidratos de absorción media (avena, plátano)<br>
                                <strong>Post-entreno:</strong> {carb_g*0.3:.0f}g para óptima recuperación muscular<br>
                                <strong>Fuentes recomendadas:</strong> Avena, arroz, quinoa, frutas, verduras<br>
                                <strong>Timing:</strong> Concentra el 60% alrededor del entrenamiento
                            </p>
                        </div>
                        
                        <div style="margin: 1.5rem 0;">
                            <h5 style="color: #4caf50;">🥑 Grasas ({fat_g:.0f}g/día)</h5>
                            <p style="color: #ccc;">
                                <strong>Timing importante:</strong> Evita 2h antes y 1h después del entrenamiento<br>
                                <strong>Fuentes óptimas:</strong> Aguacate, frutos secos, aceite de oliva, salmón<br>
                                <strong>Función:</strong> Producción hormonal y absorción de vitaminas liposolubles<br>
                                <strong>Distribución:</strong> Equilibra entre comidas alejadas del entrenamiento
                            </p>
                        </div>
                        
                        <div style="margin: 1.5rem 0;">
                            <h5 style="color: #2196f3;">💧 Hidratación Óptima</h5>
                            <p style="color: #ccc;">
                                <strong>Objetivo mínimo:</strong> 35ml por kg de peso = {peso*0.035:.1f} litros/día<br>
                                <strong>Con ejercicio:</strong> +500-750ml por hora de entrenamiento<br>
                                <strong>Indicador:</strong> Orina amarillo claro durante todo el día<br>
                                <strong>Electrolitos:</strong> Añade sal natural si sudas mucho
                            </p>
                        </div>
                        
                        <div style="background: rgba(255, 179, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffb300;">
                            <p style="color: #ffb300; margin: 0;"><strong>🏆 Consejo de oro:</strong> 
                            La consistencia supera a la perfección. Sigue el plan al 80% consistentemente 
                            en lugar de intentar ser perfecto al 100% y abandonar.</p>
                        </div>
                    </div>
                    """)
            
            # Navigation buttons
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                prev_step6 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
            with col2:
                continue_step6 = st.form_submit_button("➡️ Ver Resumen Final", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if prev_step6:
                prev_step()
            elif continue_step6:
                st.session_state.form_data.update({
                    'protein_g': protein_g,
                    'carb_g': carb_g,
                    'fat_g': fat_g,
                    'protein_calories': protein_calories,
                    'carb_calories': carb_calories,
                    'fat_calories': fat_calories,
                    'meals': meals,
                    'num_meals': num_meals,
                    'hidratacion': hidratacion,
                    'suplementos': suplementos
                })
                st.success("✅ ¡Plan nutricional personalizado completado! Generando resumen final...")
                next_step()

elif st.session_state.current_step == 7:
    # STEP 7: Summary and Results - Enhanced with modern UI
    enviar = True  # Since we've validated everything in previous steps
    
    # Enhanced completion header
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(67, 160, 71, 0.2)); 
                    border-radius: 20px; padding: 2rem; margin: 2rem 0; text-align: center;
                    border: 2px solid rgba(76, 175, 80, 0.5);">
            <h1 style="color: #4caf50; margin-bottom: 1rem; font-size: 2.5rem;">
                🎉 ¡Evaluación Completada!
            </h1>
            <p style="color: #ccc; font-size: 1.3rem; margin: 0;">
                Tu reporte personalizado de composición corporal y nutrición está listo
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get all the data from session state
    form_data = st.session_state.form_data
    
    nombre = form_data.get('nombre')
    edad = form_data.get('edad')
    genero = form_data.get('genero')
    estatura = form_data.get('estatura')
    peso = form_data.get('peso')
    email_usuario = form_data.get('email_usuario')
    telefono = form_data.get('telefono')
    metodo_grasa = form_data.get('metodo_grasa')
    grasa_reportada = form_data.get('grasa_reportada')

    # Continue with existing calculation logic but using form_data
    with st.spinner("🔄 Procesando tu información y generando reporte..."):
        # --- LÓGICA Y CÁLCULOS (PRESERVED EXACTLY) ---
        if metodo_grasa == "Omron HBF-516 (BIA)":
            grasa_corregida = corregir_grasa_omron_a_dexa(grasa_reportada)
        else:
            grasa_corregida = grasa_reportada
            
        estatura_m = estatura / 100
        mlg = peso * (1 - grasa_corregida / 100)
        ffmi = mlg / (estatura_m ** 2)

        # Clasificación % de grasa corporal
        if genero == "Hombre":
            if grasa_corregida < 6:
                nivel_grasa = "Preparación concurso"
            elif grasa_corregida < 10:
                nivel_grasa = "Atlético/competidor"
            elif grasa_corregida < 17:
                nivel_grasa = "Normal saludable"
            elif grasa_corregida < 25:
                nivel_grasa = "Sobrepeso"
            else:
                nivel_grasa = "Obesidad"
        else:
            if grasa_corregida < 14:
                nivel_grasa = "Preparación concurso"
            elif grasa_corregida < 21:
                nivel_grasa = "Atlética/competidora"
            elif grasa_corregida < 28:
                nivel_grasa = "Normal saludable"
            elif grasa_corregida < 35:
                nivel_grasa = "Sobrepeso"
            else:
                nivel_grasa = "Obesidad"

        # Clasificación FFMI
        if genero == "Hombre":
            if ffmi < 18:
                nivel_ffmi = "Novato"
            elif ffmi < 20:
                nivel_ffmi = "Intermedio"
            elif ffmi < 22:
                nivel_ffmi = "Avanzado"
            elif ffmi < 25:
                nivel_ffmi = "Elite (Natty max)"
            else:
                nivel_ffmi = "Posible uso de anabólicos"
        else:
            if ffmi < 14:
                nivel_ffmi = "Novata"
            elif ffmi < 16:
                nivel_ffmi = "Intermedia"
            elif ffmi < 18:
                nivel_ffmi = "Avanzada"
            elif ffmi < 20:
                nivel_ffmi = "Elite (Natty max)"
            else:
                nivel_ffmi = "Posible uso de anabólicos"

        # Enhanced user data with all new fields
        usuario = {
            "Nombre": nombre,
            "Edad": f"{edad} años",
            "Género": genero,
            "Estatura": f"{estatura} cm",
            "Peso": f"{peso} kg",
            "Email": email_usuario,
            "Teléfono": telefono if telefono else "No proporcionado",
            "Método %BF": metodo_grasa,
            "%BF reportado": f"{grasa_reportada:.1f}%",
            "%BF corregido (DEXA)": f"{grasa_corregida:.1f}%",
            "Objetivo principal": form_data.get('objetivo_principal', 'No especificado'),
            "Experiencia": form_data.get('experiencia_entrenamiento', 'No especificado'),
            "Nivel de actividad": form_data.get('ejercicio_frecuencia', 'No especificado'),
        }
        
        # Enhanced summary with all calculations
        resumen = {
            "Nivel de grasa corporal": nivel_grasa,
            "FFMI": f"{ffmi:.2f} - {nivel_ffmi}",
            "MLG (Masa Libre de Grasa)": f"{mlg:.1f} kg",
            "BMR (Metabolismo Basal)": f"{form_data.get('bmr', 0):.0f} kcal/día",
            "TDEE (Gasto Total Diario)": f"{form_data.get('tdee', 0):.0f} kcal/día",
            "Calorías objetivo": f"{form_data.get('target_calories', 0):.0f} kcal/día",
            "Estrategia calórica": form_data.get('deficit_surplus', 'No especificado'),
            "Proteínas diarias": f"{form_data.get('protein_g', 0):.0f}g",
            "Carbohidratos diarios": f"{form_data.get('carb_g', 0):.0f}g", 
            "Grasas diarias": f"{form_data.get('fat_g', 0):.0f}g",
        }
        
        tabla_bf_txt = render_tabla(tabla_bf(genero))
        tabla_ffmi_txt = render_tabla(tabla_ffmi(genero))

        # --- ENHANCED COMPREHENSIVE RESULTS DISPLAY ---
        st.markdown("## 📊 Tu Evaluación Completa MUPAI")
        
        # Enhanced key metrics overview
        st.markdown("""
            <div style="margin: 2rem 0 1rem 0;">
                <h3 style="color: #ffb300;">🏆 Métricas Principales</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            delta_bf = f"{grasa_corregida - grasa_reportada:.1f}%" if metodo_grasa == "Omron HBF-516 (BIA)" else None
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #fff; margin-bottom: 0.5rem;">{peso} kg</h3>
                    <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Peso</h4>
                    <p style="color: #4caf50; font-size: 0.9rem; margin: 0;">
                        {grasa_corregida:.1f}% grasa corporal
                        {f'<br><small>({delta_bf} ajuste)</small>' if delta_bf else ''}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #fff; margin-bottom: 0.5rem;">{mlg:.1f} kg</h3>
                    <h4 style="color: #ffb300; margin-bottom: 0.5rem;">MLG</h4>
                    <p style="color: #e91e63; font-size: 0.9rem; margin: 0;">
                        FFMI: {ffmi:.2f}<br>
                        <small>{nivel_ffmi}</small>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #fff; margin-bottom: 0.5rem;">{form_data.get('tdee', 0):.0f}</h3>
                    <h4 style="color: #ffb300; margin-bottom: 0.5rem;">TDEE</h4>
                    <p style="color: #2196f3; font-size: 0.9rem; margin: 0;">
                        Objetivo: {form_data.get('target_calories', 0):.0f} kcal<br>
                        <small>{form_data.get('deficit_surplus', 'N/A').split(' ')[0]}</small>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #fff; margin-bottom: 0.5rem;">{form_data.get('protein_g', 0):.0f}g</h3>
                    <h4 style="color: #ffb300; margin-bottom: 0.5rem;">Proteína</h4>
                    <p style="color: #ff9800; font-size: 0.9rem; margin: 0;">
                        Diaria<br>
                        <small>{form_data.get('experiencia_entrenamiento', 'N/A').split(' ')[0]}</small>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Enhanced detailed sections with modern tabs
        st.markdown("""
            <div style="margin: 3rem 0 1rem 0;">
                <h3 style="color: #ffb300;">📋 Análisis Detallado</h3>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Composición Corporal", "🍽️ Plan Nutricional", "🏃‍♂️ Perfil de Actividad", "🎯 Plan Personalizado"])
        
        with tab1:
            col1, col2 = st.columns([2, 1], gap="large")
            
            with col1:
                st.markdown("""
                    <div class="info-card">
                        <h4 style="color: #ffb300; margin-bottom: 1rem;">📊 Análisis de Composición</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**🎯 Clasificación de grasa corporal:** {nivel_grasa}")
                st.markdown(f"**💪 Clasificación FFMI:** {nivel_ffmi}")
                
                if metodo_grasa == "Omron HBF-516 (BIA)":
                    st.info(f"**📝 Ajuste aplicado:** Tu % de grasa fue corregido de {grasa_reportada:.1f}% (Omron) a {grasa_corregida:.1f}% (equivalente DEXA) para mayor precisión en las recomendaciones.")
            
            with col2:
                st.markdown("**📋 Tabla de Referencia - % Grasa Corporal**")
                st.markdown(tabla_bf_txt)
        
        with tab2:
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("""
                    <div class="info-card">
                        <h4 style="color: #ffb300; margin-bottom: 1rem;">🎯 Distribución de Macronutrientes</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                protein_kcal = form_data.get('protein_calories', 0)
                carb_kcal = form_data.get('carb_calories', 0)
                fat_kcal = form_data.get('fat_calories', 0)
                
                st.markdown(f"""
                🥩 **Proteínas:** {form_data.get('protein_g', 0):.0f}g ({protein_kcal:.0f} kcal)  
                🍞 **Carbohidratos:** {form_data.get('carb_g', 0):.0f}g ({carb_kcal:.0f} kcal)  
                🥑 **Grasas:** {form_data.get('fat_g', 0):.0f}g ({fat_kcal:.0f} kcal)
                """)
            
            with col2:
                st.markdown("""
                    <div class="info-card">
                        <h4 style="color: #ffb300; margin-bottom: 1rem;">⚡ Estrategia Calórica</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                **📈 Objetivo:** {form_data.get('objetivo_principal', 'N/A')}  
                **🎯 Estrategia:** {form_data.get('deficit_surplus', 'N/A')}  
                **🍽️ Comidas:** {form_data.get('meals', 'N/A')}  
                **💧 Hidratación:** {form_data.get('hidratacion', 'N/A')}
                """)
        
        with tab3:
            st.markdown("""
                <div class="info-card">
                    <h4 style="color: #ffb300; margin-bottom: 1rem;">🏃‍♂️ Tu Perfil de Actividad</h4>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown(f"""
                **💼 Actividad laboral:** {form_data.get('actividad_trabajo', 'N/A')}  
                **🏋️‍♂️ Frecuencia de ejercicio:** {form_data.get('ejercicio_frecuencia', 'N/A')}  
                **⚡ Intensidad:** {form_data.get('ejercicio_intensidad', 'N/A')}
                """)
            
            with col2:
                st.markdown(f"""
                **⏱️ Duración promedio:** {form_data.get('ejercicio_duracion', 0)} minutos  
                **🎯 Timeline objetivo:** {form_data.get('tiempo_objetivo', 'N/A')}  
                **⏰ Tiempo disponible:** {form_data.get('tiempo_disponible', 'N/A')}
                """)
        
        with tab4:
            objetivo = form_data.get('objetivo_principal', '')
            
            st.markdown("""
                <div class="info-card">
                    <h4 style="color: #ffb300; margin-bottom: 1rem;">🎯 Tu Plan de Acción Personalizado</h4>
                </div>
            """, unsafe_allow_html=True)
            
            if objetivo == "Perder grasa corporal":
                st.markdown("""
                    <div style="background: rgba(255, 152, 0, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ff9800;">
                        <h4 style="color: #ff9800;">🔥 Plan de Pérdida de Grasa</h4>
                        <p style="color: #ccc;"><strong>Estrategia recomendada:</strong></p>
                        <ul style="color: #ccc;">
                            <li>Mantén un déficit calórico constante y sostenible</li>
                            <li>Prioriza proteína en cada comida para preservar masa muscular</li>
                            <li>Incluye entrenamiento de resistencia 3-4 veces por semana</li>
                            <li>Añade cardio moderado 2-3 veces por semana</li>
                            <li>Monitorea progreso semanal con mediciones corporales</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            elif objetivo == "Ganar masa muscular":
                st.markdown("""
                    <div style="background: rgba(76, 175, 80, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #4caf50;">
                        <h4 style="color: #4caf50;">💪 Plan de Ganancia Muscular</h4>
                        <p style="color: #ccc;"><strong>Estrategia recomendada:</strong></p>
                        <ul style="color: #ccc;">
                            <li>Mantén un superávit calórico controlado</li>
                            <li>Enfócate en entrenamiento de resistencia progresivo</li>
                            <li>Consume 20-30g de proteína dentro de 2h post-entreno</li>
                            <li>Prioriza descanso (7-9h de sueño) para recuperación</li>
                            <li>Ajusta calorías según ganancia de peso semanal</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background: rgba(33, 150, 243, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2196f3;">
                        <h4 style="color: #2196f3;">⚖️ Plan de Mantenimiento y Salud General</h4>
                        <p style="color: #ccc;"><strong>Estrategia recomendada:</strong></p>
                        <ul style="color: #ccc;">
                            <li>Mantén calorías en balance energético</li>
                            <li>Combina entrenamiento de fuerza y cardio equilibradamente</li>
                            <li>Enfócate en la consistencia a largo plazo</li>
                            <li>Ajusta según progreso y sensaciones corporales</li>
                            <li>Prioriza adherencia sobre perfección</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            if form_data.get('limitaciones'):
                st.warning(f"⚠️ **Consideraciones especiales a tener en cuenta:** {', '.join(form_data.get('limitaciones', []))}")

        # --- Enhanced PDF generation and download section ---
        enhanced_resumen = {**resumen, 
                          "Objetivo": form_data.get('objetivo_principal', 'N/A'),
                          "Experiencia entrenamiento": form_data.get('experiencia_entrenamiento', 'N/A'),
                          "Distribución comidas": form_data.get('meals', 'N/A')}
        
        pdf_bytes = generar_pdf(usuario, enhanced_resumen, tabla_bf_txt, tabla_ffmi_txt, logo_image)

        # Enhanced download section
        st.markdown("""
            <div style="margin: 3rem 0 2rem 0;">
                <h3 style="color: #ffb300;">📄 Descarga tu Reporte Completo</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1], gap="large")
        
        with col1:
            st.download_button(
                label="📄 Descargar Reporte Completo en PDF",
                data=pdf_bytes,
                file_name=f"Reporte_MUPAI_{nombre.replace(' ','_')}_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            st.markdown("""
                <div class="info-card">
                    <h4 style="color: #ffb300; margin-bottom: 0.5rem;">📋 Incluye</h4>
                    <p style="color: #ccc; font-size: 0.9rem; margin: 0;">
                        • Análisis completo<br>
                        • Plan nutricional<br>
                        • Recomendaciones<br>
                        • Tablas de referencia
                    </p>
                </div>
            """, unsafe_allow_html=True)

        # --- Email sending (preserved exactly) ---
        try:
            remitente = st.secrets.get("email_remitente", "administracion@muscleupgym.fitness")
            password = st.secrets.get("email_password", "")
            destinatario = st.secrets.get("email_destinatario", "administracion@muscleupgym.fitness")
            
            if password:
                asunto = f"Nuevo cuestionario MUPAI: {nombre} ({date.today().strftime('%d/%m/%Y')})"
                body = f"""
                <h2>Nuevo cuestionario MUPAI recibido</h2>
                <h3>Datos del usuario:</h3>
                {"<br>".join([f"<b>{k}:</b> {v}" for k, v in usuario.items()])}
                <br><br>
                <h3>Resumen de composición corporal:</h3>
                {"<br>".join([f"<b>{k}:</b> {v}" for k, v in enhanced_resumen.items()])}
                """
                
                if enviar_email(remitente, password, destinatario, asunto, body, pdf_bytes, f"{nombre}_MUPAI.pdf"):
                    st.success("📧 ¡Tus datos han sido enviados exitosamente a tu entrenador!")
                else:
                    st.warning("⚠️ No se pudo enviar el email automáticamente. Por favor, envía el PDF descargado a tu entrenador.")
            else:
                st.info("💡 Recuerda enviar el PDF descargado a tu entrenador para seguimiento personalizado.")
                
        except Exception as e:
            st.info("💡 Recuerda enviar el PDF descargado a tu entrenador para seguimiento personalizado.")
    
    # Enhanced navigation for final step
    st.markdown("""
        <div style="margin: 3rem 0 2rem 0;">
            <h3 style="color: #ffb300;">🚀 ¿Qué sigue ahora?</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        if st.button("⬅️ Volver a Nutrición", use_container_width=True):
            prev_step()
    with col2:
        if st.button("🔄 Realizar Nuevo Cuestionario", use_container_width=True):
            # Clear all session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Validation and processing
# --- PIE DE PÁGINA ---
pie_streamlit()

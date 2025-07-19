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

# ---------- ESTILOS PERSONALIZADOS ----------
st.markdown("""
    <style>
    .logo-container {text-align:center; margin-bottom: 10px;}
    .logo-img {width: 340px; max-width:90vw;}
    .main {background-color: #191b1f;}
    .block-container {
        background-color: #23262b; 
        border-radius: 16px; 
        padding: 2em;
        max-width: 800px;
        margin: auto;
    }
    h1, h2, h3, h4, h5, h6, p, .stTextInput > label, .stSelectbox > label, .stNumberInput > label {
        color: #fff !important;
        font-family: 'Montserrat', 'Lato', 'Open Sans', 'Roboto', sans-serif;
    }
    .stButton>button {
        background: #ffb300; 
        color: #191b1f; 
        border-radius: 8px; 
        font-weight: bold;
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: #fff; 
        color: #ffb300;
        border: 2px solid #ffb300;
    }
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px;
        background-color: rgba(255,255,255,0.1);
    }
    .stCheckbox {
        color: #fff;
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

# ---------- PROGRESS INDICATOR ----------
def render_progress_bar():
    current = st.session_state.current_step
    total = len(STEPS)
    
    # Progress bar
    progress = current / total
    st.progress(progress)
    
    # Step indicators
    cols = st.columns(total)
    for i, (step_num, step_info) in enumerate(STEPS.items(), 1):
        with cols[i-1]:
            if i == current:
                st.markdown(f"🔵 **{step_info['icon']}**")
                st.markdown(f"<small><b>Paso {i}</b></small>", unsafe_allow_html=True)
            elif i < current:
                st.markdown(f"✅ {step_info['icon']}")
                st.markdown(f"<small>Paso {i}</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"⭕ {step_info['icon']}")
                st.markdown(f"<small>Paso {i}</small>", unsafe_allow_html=True)
    
    st.markdown("---")

# ---------- APP PRINCIPAL ----------
st.title("📋 Cuestionario Digital MUPAI")
st.write("**Digital Training Science**")
st.markdown("---")

# Show progress
render_progress_bar()

# Show current step title
current_step_info = STEPS[st.session_state.current_step]
st.title(f"{current_step_info['icon']} {current_step_info['title']}")
st.markdown("---")

# ---------- STEP CONTENT ----------
if st.session_state.current_step == 1:
    # STEP 1: Personal Information
    with st.form("step1_form"):
        st.info("📝 Completa tu información personal básica para comenzar tu evaluación.")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo*", 
                                 value=st.session_state.form_data.get('nombre', ''),
                                 placeholder="Juan Pérez")
            edad = st.number_input("Edad*", 
                                 min_value=10, max_value=90, step=1, 
                                 value=st.session_state.form_data.get('edad', 25))
            genero = st.selectbox("Género*", 
                                ["Hombre", "Mujer"],
                                index=0 if st.session_state.form_data.get('genero', 'Hombre') == 'Hombre' else 1)
        
        with col2:
            estatura = st.number_input("Estatura (cm)*", 
                                     min_value=120, max_value=230, step=1, 
                                     value=st.session_state.form_data.get('estatura', 170))
            peso = st.number_input("Peso (kg)*", 
                                 min_value=30.0, max_value=200.0, step=0.1, 
                                 value=st.session_state.form_data.get('peso', 70.0))
        
        st.subheader("📧 Información de Contacto")
        email_usuario = st.text_input("Tu correo electrónico*", 
                                     value=st.session_state.form_data.get('email_usuario', ''),
                                     placeholder="ejemplo@email.com")
        telefono = st.text_input("Número de teléfono (opcional)", 
                                value=st.session_state.form_data.get('telefono', ''),
                                placeholder="+52 1234567890")
        
        st.markdown("---")
        descargo = st.checkbox("✅ He leído y acepto la política de privacidad y términos de uso",
                              value=st.session_state.form_data.get('descargo', False))
        
        col1, col2 = st.columns(2)
        with col1:
            prev_disabled = True  # First step
        with col2:
            continue_step1 = st.form_submit_button("➡️ Continuar", use_container_width=True)
        
        if continue_step1:
            # Validation
            if not all([nombre, edad, genero, estatura, peso, email_usuario, descargo]):
                st.error("❌ Por favor, completa todos los campos obligatorios y acepta los términos.")
            else:
                # Save data and go to next step
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
                next_step()

elif st.session_state.current_step == 2:
    # STEP 2: Body Composition
    with st.form("step2_form"):
        st.info("⚖️ Proporciona información sobre tu composición corporal actual.")
        
        metodo_grasa = st.selectbox("¿Qué método usaste para medir tu porcentaje de grasa?", 
                                   ["Omron HBF-516 (BIA)", "DEXA (Gold Standard)"],
                                   index=0 if st.session_state.form_data.get('metodo_grasa', 'Omron HBF-516 (BIA)') == 'Omron HBF-516 (BIA)' else 1)
        grasa_reportada = st.number_input("Porcentaje de grasa reportado (%)", 
                                        min_value=5.0, max_value=50.0, step=0.1, 
                                        value=st.session_state.form_data.get('grasa_reportada', 20.0))
        
        # Educational content
        with st.expander("ℹ️ ¿Cómo interpretar estos valores?"):
            st.markdown("""
            **Métodos de medición de grasa corporal:**
            - **Omron HBF-516 (BIA)**: Bioimpedancia eléctrica, conveniente pero puede sobreestimar
            - **DEXA**: Considerado el estándar de oro para medición de composición corporal
            
            **Nota**: Si usas Omron, ajustaremos automáticamente el valor para mayor precisión.
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            prev_step2 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with col2:
            continue_step2 = st.form_submit_button("➡️ Continuar", use_container_width=True)
        
        if prev_step2:
            prev_step()
        elif continue_step2:
            st.session_state.form_data.update({
                'metodo_grasa': metodo_grasa,
                'grasa_reportada': grasa_reportada
            })
            next_step()

elif st.session_state.current_step == 3:
    # STEP 3: Activity Level
    with st.form("step3_form"):
        st.info("💪 Evalúa tu nivel de actividad física actual para personalizar tus recomendaciones.")
        
        # Activity level assessment
        actividad_trabajo = st.selectbox("¿Cuál describe mejor tu trabajo/actividad diaria?",
                                       ["Sedentario (oficina, computadora)", 
                                        "Ligeramente activo (caminar ocasionalmente)",
                                        "Moderadamente activo (de pie frecuentemente)",
                                        "Muy activo (trabajo físico)"],
                                       index=0)
        
        ejercicio_frecuencia = st.selectbox("¿Con qué frecuencia haces ejercicio?",
                                          ["No hago ejercicio",
                                           "1-2 veces por semana",
                                           "3-4 veces por semana", 
                                           "5-6 veces por semana",
                                           "Todos los días"],
                                          index=2)
        
        ejercicio_intensidad = st.selectbox("¿Cuál es la intensidad de tu ejercicio típico?",
                                          ["Ligero (caminar, yoga suave)",
                                           "Moderado (trotar, natación, pesas ligeras)",
                                           "Vigoroso (correr, crossfit, pesas pesadas)",
                                           "Muy intenso (deportes competitivos, entrenamiento atlético)"],
                                          index=1)
        
        ejercicio_duracion = st.number_input("Duración promedio de cada sesión de ejercicio (minutos)", 
                                           min_value=0, max_value=300, step=15, value=60)
        
        # Educational content
        with st.expander("ℹ️ ¿Por qué es importante el nivel de actividad?"):
            st.markdown("""
            **El nivel de actividad afecta:**
            - **Gasto calórico total**: Determina cuántas calorías quemas diariamente
            - **Requerimientos nutricionales**: Necesidades de macronutrientes
            - **Objetivos realistas**: Metas alcanzables según tu estilo de vida
            - **Recomendaciones personalizadas**: Estrategias adaptadas a tu rutina
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            prev_step3 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with col2:
            continue_step3 = st.form_submit_button("➡️ Continuar", use_container_width=True)
        
        if prev_step3:
            prev_step()
        elif continue_step3:
            st.session_state.form_data.update({
                'actividad_trabajo': actividad_trabajo,
                'ejercicio_frecuencia': ejercicio_frecuencia,
                'ejercicio_intensidad': ejercicio_intensidad,
                'ejercicio_duracion': ejercicio_duracion
            })
            next_step()

elif st.session_state.current_step == 4:
    # STEP 4: Training Goals and Experience
    with st.form("step4_form"):
        st.info("🎯 Define tus objetivos y experiencia para crear un plan personalizado.")
        
        objetivo_principal = st.selectbox("¿Cuál es tu objetivo principal?",
                                        ["Perder grasa corporal",
                                         "Ganar masa muscular",
                                         "Mantener peso actual",
                                         "Mejorar rendimiento deportivo",
                                         "Mejorar salud general"],
                                        index=0)
        
        experiencia_entrenamiento = st.selectbox("¿Cuál es tu experiencia con el entrenamiento?",
                                                ["Principiante (menos de 6 meses)",
                                                 "Novato (6 meses - 2 años)",
                                                 "Intermedio (2-5 años)",
                                                 "Avanzado (más de 5 años)"],
                                                index=1)
        
        tiempo_disponible = st.selectbox("¿Cuánto tiempo puedes dedicar al entrenamiento por semana?",
                                       ["Menos de 3 horas",
                                        "3-5 horas",
                                        "5-8 horas",
                                        "Más de 8 horas"],
                                       index=1)
        
        limitaciones = st.multiselect("¿Tienes alguna limitación física o preferencia? (opcional)",
                                    ["Lesión de rodilla",
                                     "Lesión de espalda",
                                     "Lesión de hombro",
                                     "Problemas cardiovasculares",
                                     "Prefiero entrenar en casa",
                                     "Solo ejercicios de peso corporal",
                                     "Ninguna"])
        
        # Timeline expectations
        tiempo_objetivo = st.selectbox("¿En cuánto tiempo esperas ver resultados significativos?",
                                     ["1-2 meses",
                                      "3-4 meses", 
                                      "5-6 meses",
                                      "Más de 6 meses"],
                                     index=1)
        
        with st.expander("ℹ️ Estableciendo expectativas realistas"):
            st.markdown("""
            **Cronogramas típicos para resultados:**
            - **Pérdida de grasa**: 0.5-1kg por semana es sostenible
            - **Ganancia muscular**: 0.25-0.5kg por mes para principiantes
            - **Cambios visibles**: 4-6 semanas con plan consistente
            - **Transformaciones significativas**: 3-6 meses de dedicación
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            prev_step4 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with col2:
            continue_step4 = st.form_submit_button("➡️ Continuar", use_container_width=True)
        
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
            next_step()

elif st.session_state.current_step == 5:
    # STEP 5: Caloric Requirements and Deficit/Surplus
    with st.form("step5_form"):
        st.info("🔥 Calculamos tus necesidades calóricas personalizadas.")
        
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
            
            st.success(f"🔥 **Tus cálculos metabólicos:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BMR (Metabolismo Basal)", f"{bmr:.0f} kcal")
            with col2:
                st.metric("TDEE (Gasto Total)", f"{tdee:.0f} kcal")
            with col3:
                factor_pct = (activity_factor - 1) * 100
                st.metric("Factor de Actividad", f"+{factor_pct:.0f}%")
        
        # Goal-specific caloric adjustment
        objetivo = st.session_state.form_data.get('objetivo_principal', 'Mantener peso actual')
        
        deficit_surplus = st.selectbox("Ajuste calórico recomendado según tu objetivo:",
                                     ["Déficit agresivo (-500 kcal/día)",
                                      "Déficit moderado (-300 kcal/día)", 
                                      "Déficit suave (-200 kcal/día)",
                                      "Mantenimiento (0 kcal)",
                                      "Superávit suave (+200 kcal/día)",
                                      "Superávit moderado (+300 kcal/día)",
                                      "Superávit agresivo (+500 kcal/día)"])
        
        # Auto-select based on goal
        if objetivo == "Perder grasa corporal":
            deficit_surplus = st.selectbox("Ajuste calórico recomendado:", 
                                         ["Déficit moderado (-300 kcal/día)", 
                                          "Déficit agresivo (-500 kcal/día)",
                                          "Déficit suave (-200 kcal/día)"], index=0)
        elif objetivo == "Ganar masa muscular":
            deficit_surplus = st.selectbox("Ajuste calórico recomendado:",
                                         ["Superávit moderado (+300 kcal/día)",
                                          "Superávit suave (+200 kcal/día)",
                                          "Superávit agresivo (+500 kcal/día)"], index=0)
        
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
        
        st.info(f"🎯 **Calorías objetivo diarias: {target_calories:.0f} kcal**")
        
        with st.expander("ℹ️ Entendiendo tu gasto calórico"):
            st.markdown(f"""
            **Desglose de tu metabolismo:**
            - **BMR ({bmr:.0f} kcal)**: Energía que tu cuerpo necesita en reposo
            - **Actividad diaria**: +{(tdee-bmr):.0f} kcal por trabajo y ejercicio
            - **TDEE total**: {tdee:.0f} kcal por día
            
            **Tu estrategia ({deficit_surplus}):**
            - Objetivo calórico: {target_calories:.0f} kcal/día
            - Diferencia: {adjustment:+.0f} kcal/día
            - Pérdida/ganancia semanal esperada: {abs(adjustment)*7/7700:.2f} kg/semana
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            prev_step5 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with col2:
            continue_step5 = st.form_submit_button("➡️ Continuar", use_container_width=True)
        
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
            next_step()

elif st.session_state.current_step == 6:
    # STEP 6: Macronutrient Recommendations
    with st.form("step6_form"):
        st.info("🥗 Recomendaciones de macronutrientes personalizadas para tu objetivo.")
        
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
            
            # Display recommendations
            st.success("🎯 **Tu distribución de macronutrientes:**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                protein_pct = (protein_calories / target_calories) * 100
                st.metric("🥩 Proteínas", f"{protein_g:.0f}g", f"{protein_pct:.0f}%")
                st.caption(f"{protein_calories:.0f} kcal")
            
            with col2:
                carb_pct = (carb_calories / target_calories) * 100
                st.metric("🍞 Carbohidratos", f"{carb_g:.0f}g", f"{carb_pct:.0f}%")
                st.caption(f"{carb_calories:.0f} kcal")
            
            with col3:
                fat_pct = (fat_calories / target_calories) * 100
                st.metric("🥑 Grasas", f"{fat_g:.0f}g", f"{fat_pct:.0f}%")
                st.caption(f"{fat_calories:.0f} kcal")
            
            # Timing recommendations
            st.subheader("⏰ Distribución de comidas recomendada")
            
            meals = st.selectbox("¿Cuántas comidas prefieres hacer al día?",
                                ["3 comidas principales",
                                 "4 comidas (3 principales + 1 snack)",
                                 "5 comidas (3 principales + 2 snacks)",
                                 "6 comidas pequeñas"])
            
            num_meals = {
                "3 comidas principales": 3,
                "4 comidas (3 principales + 1 snack)": 4, 
                "5 comidas (3 principales + 2 snacks)": 5,
                "6 comidas pequeñas": 6
            }.get(meals, 4)
            
            calories_per_meal = target_calories / num_meals
            protein_per_meal = protein_g / num_meals
            
            st.info(f"🍽️ **Distribución por comida:**")
            st.write(f"- Calorías por comida: ~{calories_per_meal:.0f} kcal")
            st.write(f"- Proteína por comida: ~{protein_per_meal:.0f}g")
            
            with st.expander("💡 Consejos nutricionales personalizados"):
                st.markdown(f"""
                **Para tu objetivo ({objetivo}):**
                
                **Proteínas ({protein_g:.0f}g/día):**
                - Consume {protein_g_per_kg}g por kg de peso corporal
                - Incluye en cada comida: pollo, pescado, huevos, legumbres
                - Post-entreno: 20-30g de proteína rápida (whey, claras)
                
                **Carbohidratos ({carb_g:.0f}g/día):**
                - Pre-entreno: 30-50g de carbos de absorción media
                - Post-entreno: {carb_g*0.3:.0f}g para recuperación
                - Fuentes: avena, arroz, frutas, verduras
                
                **Grasas ({fat_g:.0f}g/día):**
                - Evita antes y después del entrenamiento
                - Fuentes: aguacate, frutos secos, aceite de oliva
                - Importante para hormonas y absorción de vitaminas
                """)
        
        hidratacion = st.selectbox("¿Cuánta agua bebes normalmente al día?",
                                 ["Menos de 1 litro",
                                  "1-2 litros",
                                  "2-3 litros", 
                                  "Más de 3 litros"],
                                 index=1)
        
        suplementos = st.multiselect("¿Qué suplementos usas actualmente? (opcional)",
                                   ["Proteína en polvo",
                                    "Creatina",
                                    "Multivitamínico",
                                    "Omega-3",
                                    "Pre-entreno",
                                    "BCAA",
                                    "Ninguno"])
        
        col1, col2 = st.columns(2)
        with col1:
            prev_step6 = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with col2:
            continue_step6 = st.form_submit_button("➡️ Ver Resumen", use_container_width=True)
        
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
            next_step()

elif st.session_state.current_step == 7:
    # STEP 7: Summary and Results - this will replace the old validation and processing logic
    enviar = True  # Since we've validated everything in previous steps
    st.success("🎉 ¡Evaluación completada! Aquí tienes tu resumen personalizado.")
    
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
    with st.spinner("🔄 Procesando tu información..."):
        # --- LÓGICA Y CÁLCULOS ---
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

        # --- COMPREHENSIVE RESULTS DISPLAY ---
        st.markdown("## 📊 Tu Evaluación Completa MUPAI")
        
        # Key metrics overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Peso", f"{peso} kg")
            st.metric("% Grasa Corporal", f"{grasa_corregida:.1f}%", 
                     f"{grasa_corregida - grasa_reportada:.1f}%" if metodo_grasa == "Omron HBF-516 (BIA)" else None)
        with col2:
            st.metric("MLG", f"{mlg:.1f} kg")
            st.metric("FFMI", f"{ffmi:.2f}")
        with col3:
            st.metric("TDEE", f"{form_data.get('tdee', 0):.0f} kcal")
            st.metric("Calorías Objetivo", f"{form_data.get('target_calories', 0):.0f} kcal")
        with col4:
            st.metric("Proteína Diaria", f"{form_data.get('protein_g', 0):.0f}g")
            st.metric("Experiencia", form_data.get('experiencia_entrenamiento', 'N/A').split(' ')[0])
        
        # Detailed sections
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Composición Corporal", "🔥 Nutrición", "🏃‍♂️ Actividad", "📋 Plan Personalizado"])
        
        with tab1:
            st.subheader("Análisis de Composición Corporal")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Clasificación de grasa corporal:** {nivel_grasa}")
                st.markdown(f"**Clasificación FFMI:** {nivel_ffmi}")
                
                if metodo_grasa == "Omron HBF-516 (BIA)":
                    st.info(f"**Nota:** Tu % de grasa fue ajustado de {grasa_reportada:.1f}% (Omron) a {grasa_corregida:.1f}% (equivalente DEXA)")
            
            with col2:
                st.markdown("**Tabla de % Grasa Corporal**")
                st.markdown(tabla_bf_txt)
        
        with tab2:
            st.subheader("Plan Nutricional Personalizado")
            
            # Macronutrient breakdown chart
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Distribución de Macronutrientes:**")
                protein_kcal = form_data.get('protein_calories', 0)
                carb_kcal = form_data.get('carb_calories', 0)
                fat_kcal = form_data.get('fat_calories', 0)
                
                st.write(f"🥩 Proteínas: {form_data.get('protein_g', 0):.0f}g ({protein_kcal:.0f} kcal)")
                st.write(f"🍞 Carbohidratos: {form_data.get('carb_g', 0):.0f}g ({carb_kcal:.0f} kcal)")
                st.write(f"🥑 Grasas: {form_data.get('fat_g', 0):.0f}g ({fat_kcal:.0f} kcal)")
            
            with col2:
                st.markdown("**Estrategia Calórica:**")
                st.write(f"📈 Objetivo: {form_data.get('objetivo_principal', 'N/A')}")
                st.write(f"🎯 {form_data.get('deficit_surplus', 'N/A')}")
                st.write(f"🍽️ {form_data.get('meals', 'N/A')}")
        
        with tab3:
            st.subheader("Perfil de Actividad")
            st.write(f"💼 Actividad laboral: {form_data.get('actividad_trabajo', 'N/A')}")
            st.write(f"🏋️‍♂️ Frecuencia de ejercicio: {form_data.get('ejercicio_frecuencia', 'N/A')}")
            st.write(f"⚡ Intensidad: {form_data.get('ejercicio_intensidad', 'N/A')}")
            st.write(f"⏱️ Duración promedio: {form_data.get('ejercicio_duracion', 0)} minutos")
            st.write(f"💧 Hidratación: {form_data.get('hidratacion', 'N/A')}")
        
        with tab4:
            st.subheader("Tu Plan Personalizado")
            objetivo = form_data.get('objetivo_principal', '')
            experiencia = form_data.get('experiencia_entrenamiento', '')
            
            if objetivo == "Perder grasa corporal":
                st.success("🎯 **Plan de Pérdida de Grasa**")
                st.markdown("""
                **Estrategia recomendada:**
                - Mantén un déficit calórico constante
                - Prioriza proteína para preservar músculo
                - Incluye entrenamiento de resistencia 3-4 veces por semana
                - Cardio moderado 2-3 veces por semana
                """)
            elif objetivo == "Ganar masa muscular":
                st.success("🎯 **Plan de Ganancia Muscular**")
                st.markdown("""
                **Estrategia recomendada:**
                - Mantén un superávit calórico controlado
                - Enfócate en entrenamiento de resistencia progresivo
                - Consume proteína después del entrenamiento
                - Prioriza descanso y recuperación
                """)
            else:
                st.success("🎯 **Plan de Mantenimiento y Salud General**")
                st.markdown("""
                **Estrategia recomendada:**
                - Mantén calorías en balance
                - Combina entrenamiento de fuerza y cardio
                - Enfócate en la consistencia a largo plazo
                - Ajusta según progreso y sensaciones
                """)
            
            if form_data.get('limitaciones'):
                st.warning(f"⚠️ **Consideraciones especiales:** {', '.join(form_data.get('limitaciones', []))}")

        # --- Generar PDF mejorado ---
        # Update PDF generation to include all new data
        enhanced_resumen = {**resumen, 
                          "Objetivo": form_data.get('objetivo_principal', 'N/A'),
                          "Experiencia entrenamiento": form_data.get('experiencia_entrenamiento', 'N/A'),
                          "Distribución comidas": form_data.get('meals', 'N/A')}
        
        pdf_bytes = generar_pdf(usuario, enhanced_resumen, tabla_bf_txt, tabla_ffmi_txt, logo_image)

        # Botón de descarga
        st.download_button(
            label="📄 Descargar resumen completo en PDF",
            data=pdf_bytes,
            file_name=f"Resumen_MUPAI_{nombre.replace(' ','_')}_{date.today().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # --- Enviar email (keep existing logic) ---
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
                    st.success("📧 ¡Tus datos han sido enviados a tu entrenador!")
                else:
                    st.warning("⚠️ No se pudo enviar el email automáticamente. Por favor, envía el PDF descargado a tu entrenador.")
            else:
                st.info("💡 Recuerda enviar el PDF descargado a tu entrenador.")
                
        except Exception as e:
            st.info("💡 Recuerda enviar el PDF descargado a tu entrenador.")
    
    # Navigation for final step
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Volver a Nutrición", use_container_width=True):
            prev_step()
    with col2:
        if st.button("🔄 Reiniciar Cuestionario", use_container_width=True):
            # Clear all session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Validation and processing
# --- PIE DE PÁGINA ---
pie_streamlit()

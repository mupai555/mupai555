import streamlit as st
from datetime import date
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit_authenticator as stauth
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

# ---------- AUTENTICACIÓN ----------
AUTH_USERS = [
    {"name": "Cliente de Prueba", "username": "cliente", "password": "$2b$12$SYdbuSXOAYIk/ydLR5T9IuLhL1K6.npxRzn6AuYGdVMpJDN/7bWTG"},  # contraseña: "mupai2025"
]

credentials = {
    "usernames": {
        user["username"]: {
            "name": user["name"],
            "password": user["password"]
        } for user in AUTH_USERS
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "mupai_cuestionario",  # cookie_name
    "abcdef",              # key
    cookie_expiry_days=1
)

# ---------- AUTENTICACIÓN CON FALLBACK MANUAL ----------
# Primero intentamos con streamlit-authenticator, luego con sistema manual
name, authentication_status, username = None, None, None

# Intentar autenticación con streamlit-authenticator
try:
    result = authenticator.login(location='main')
    if result is not None and len(result) == 3:
        name, authentication_status, username = result
except Exception:
    # Si streamlit-authenticator falla, usar sistema manual
    pass

# Si streamlit-authenticator no funciona, usar sistema manual
if authentication_status is None:
    # Inicializar session state para autenticación manual
    if 'manual_auth' not in st.session_state:
        st.session_state.manual_auth = {'authenticated': False, 'username': None, 'name': None}
    
    # Si no está autenticado manualmente, mostrar formulario
    if not st.session_state.manual_auth['authenticated']:
        with st.form("manual_login"):
            st.subheader("🔐 Login")
            manual_username = st.text_input("Usuario")
            manual_password = st.text_input("Contraseña", type="password")
            manual_submit = st.form_submit_button("Iniciar Sesión")
            
            if manual_submit:
                # Verificar credenciales manualmente
                hasher = stauth.Hasher()
                user_data = AUTH_USERS[0]  # Solo tenemos un usuario
                
                if (manual_username == user_data['username'] and 
                    hasher.check_pw(manual_password, user_data['password'])):
                    st.session_state.manual_auth = {
                        'authenticated': True,
                        'username': user_data['username'],
                        'name': user_data['name']
                    }
                    st.success("✅ ¡Autenticación exitosa!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    # Si está autenticado manualmente, usar esos datos
    if st.session_state.manual_auth['authenticated']:
        name = st.session_state.manual_auth['name']
        username = st.session_state.manual_auth['username']
        authentication_status = True

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
    return pdf.output(dest='S').encode('latin1')

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

# ---------- APP PRINCIPAL ----------
if authentication_status is False:
    st.error("❌ Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.info("🔐 Por favor, ingresa tus datos para continuar")
    st.markdown("""
    ### Credenciales de prueba:
    - **Usuario:** cliente
    - **Contraseña:** mupai2025
    """)
elif authentication_status:
    # Botón de logout en sidebar
    with st.sidebar:
        st.write(f"Bienvenido, **{name}**")
        
        # Logout manual si usamos autenticación manual
        if 'manual_auth' in st.session_state and st.session_state.manual_auth['authenticated']:
            if st.button("Cerrar Sesión"):
                st.session_state.manual_auth = {'authenticated': False, 'username': None, 'name': None}
                st.rerun()
        else:
            # Usar logout de streamlit-authenticator si está disponible
            try:
                authenticator.logout(location="sidebar")
            except:
                # Fallback logout manual
                if st.button("Cerrar Sesión"):
                    st.session_state.clear()
                    st.rerun()

    st.title("📋 Cuestionario Digital MUPAI")
    st.write("**Digital Training Science**")
    st.markdown("---")

    # --- FORMULARIO ---
    with st.form("formulario_mupai"):
        st.subheader("📝 Información Personal")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo*", placeholder="Juan Pérez")
            edad = st.number_input("Edad*", min_value=10, max_value=90, step=1, value=25)
            genero = st.selectbox("Género*", ["Hombre", "Mujer"])
        
        with col2:
            estatura = st.number_input("Estatura (cm)*", min_value=120, max_value=230, step=1, value=170)
            peso = st.number_input("Peso (kg)*", min_value=30.0, max_value=200.0, step=0.1, value=70.0)
        
        st.subheader("📧 Información de Contacto")
        email_usuario = st.text_input("Tu correo electrónico*", placeholder="ejemplo@email.com")
        telefono = st.text_input("Número de teléfono (opcional)", placeholder="+52 1234567890")
        
        st.subheader("📊 Medición de Grasa Corporal")
        metodo_grasa = st.selectbox("¿Qué método usaste para medir tu porcentaje de grasa?", 
                                   ["Omron HBF-516 (BIA)", "DEXA (Gold Standard)"])
        grasa_reportada = st.number_input("Porcentaje de grasa reportado (%)", 
                                        min_value=5.0, max_value=50.0, step=0.1, value=20.0)
        
        st.markdown("---")
        descargo = st.checkbox("✅ He leído y acepto la política de privacidad y términos de uso")
        
        enviar = st.form_submit_button("🚀 Enviar y ver mi resumen", use_container_width=True)

    # Validación y procesamiento
    if enviar:
        campos_ok = all([nombre, edad, genero, estatura, peso, email_usuario, grasa_reportada, descargo])
        
        if campos_ok:
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
                }
                
                resumen = {
                    "Nivel de grasa corporal": nivel_grasa,
                    "FFMI": f"{ffmi:.2f} — {nivel_ffmi}",
                    "MLG (Masa Libre de Grasa)": f"{mlg:.1f} kg",
                }
                
                tabla_bf_txt = render_tabla(tabla_bf(genero))
                tabla_ffmi_txt = render_tabla(tabla_ffmi(genero))

                # --- Generar PDF ---
                pdf_bytes = generar_pdf(usuario, resumen, tabla_bf_txt, tabla_ffmi_txt, logo_image)

                # --- Mostrar resumen al usuario ---
                st.success("✅ ¡Análisis completado!")
                st.markdown("## 📊 Resumen de tus resultados")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Peso", f"{peso} kg")
                    st.metric("Estatura", f"{estatura} cm")
                
                with col2:
                    st.metric("% Grasa Corporal", f"{grasa_corregida:.1f}%", 
                             f"{grasa_corregida - grasa_reportada:.1f}%" if metodo_grasa == "Omron HBF-516 (BIA)" else None)
                    st.metric("MLG", f"{mlg:.1f} kg")
                
                with col3:
                    st.metric("FFMI", f"{ffmi:.2f}")
                    st.metric("Edad", f"{edad} años")
                
                # Información detallada
                with st.expander("📋 Ver información detallada"):
                    st.markdown(f"**Clasificación de grasa corporal:** {nivel_grasa}")
                    st.markdown(f"**Clasificación FFMI:** {nivel_ffmi}")
                    
                    if metodo_grasa == "Omron HBF-516 (BIA)":
                        st.info(f"**Nota:** Tu % de grasa fue ajustado de {grasa_reportada:.1f}% (Omron) a {grasa_corregida:.1f}% (equivalente DEXA)")
                    
                    st.markdown("### 📊 Tablas de referencia")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tabla de % Grasa Corporal**")
                        st.markdown(tabla_bf_txt)
                    
                    with col2:
                        st.markdown("**Tabla de FFMI**")
                        st.markdown(tabla_ffmi_txt)

                # Botón de descarga
                st.download_button(
                    label="📄 Descargar resumen completo en PDF",
                    data=pdf_bytes,
                    file_name=f"Resumen_MUPAI_{nombre.replace(' ','_')}_{date.today().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                # --- Enviar email ---
                # Usar secrets de Streamlit para credenciales
                try:
                    # En Streamlit Cloud, configura estos valores en Settings > Secrets
                    remitente = st.secrets.get("email_remitente", "administracion@muscleupgym.fitness")
                    password = st.secrets.get("email_password", "")
                    destinatario = st.secrets.get("email_destinatario", "administracion@muscleupgym.fitness")
                    
                    if password:  # Solo enviar si hay password configurado
                        asunto = f"Nuevo cuestionario MUPAI: {nombre} ({date.today().strftime('%d/%m/%Y')})"
                        body = f"""
                        <h2>Nuevo cuestionario MUPAI recibido</h2>
                        <h3>Datos del usuario:</h3>
                        {"<br>".join([f"<b>{k}:</b> {v}" for k, v in usuario.items()])}
                        <br><br>
                        <h3>Resumen de composición corporal:</h3>
                        {"<br>".join([f"<b>{k}:</b> {v}" for k, v in resumen.items()])}
                        """
                        
                        if enviar_email(remitente, password, destinatario, asunto, body, pdf_bytes, f"{nombre}_MUPAI.pdf"):
                            st.success("📧 ¡Tus datos han sido enviados a tu entrenador!")
                        else:
                            st.warning("⚠️ No se pudo enviar el email automáticamente. Por favor, envía el PDF descargado a tu entrenador.")
                    else:
                        st.info("💡 Recuerda enviar el PDF descargado a tu entrenador.")
                        
                except Exception as e:
                    st.info("💡 Recuerda enviar el PDF descargado a tu entrenador.")

        else:
            st.error("❌ Por favor, completa todos los campos obligatorios y acepta la política de privacidad.")

    # --- PIE DE PÁGINA ---
    pie_streamlit()

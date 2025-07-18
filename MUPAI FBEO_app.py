import streamlit as st
from datetime import date
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit_authenticator as stauth

# ---------- AUTENTICACIÓN ----------
AUTH_USERS = [
    {"name": "Cliente de Prueba", "username": "cliente", "password": "$2b$12$YIYx/NsEqCwN6qF8y8s9Zep9Q7Ax8i5CQZp2pPj1KkDLiB9yFZqZa"},  # contraseña: "mupai2025"
]
names = [u["name"] for u in AUTH_USERS]
usernames = [u["username"] for u in AUTH_USERS]
passwords = [u["password"] for u in AUTH_USERS]
authenticator = stauth.Authenticate(names, usernames, passwords, "mupai_cuestionario", "abcdef", cookie_expiry_days=1)
name, authentication_status, username = authenticator.login("Iniciar sesión", "main")

# ---------- ESTILOS PERSONALIZADOS Y LOGO ----------
st.markdown("""
    <style>
    .logo-container {text-align:center; margin-bottom: 10px;}
    .logo-img {width: 340px; max-width:90vw;}
    body, .stApp {background-color: #191b1f;}
    .block-container {background-color: #23262b; border-radius: 16px; padding: 2em;}
    h1, h2, h3, h4, h5, h6, .title, .subtitle, .stTextInput > label, .stSelectbox > label, .stNumberInput > label {
        color: #fff !important;
        font-family: 'Montserrat', 'Lato', 'Open Sans', 'Roboto', sans-serif;
    }
    .stButton>button {background: #ffb300; color: #191b1f; border-radius: 8px; font-weight: bold;}
    .stButton>button:hover {background: #fff; color: #ffb300;}
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {border-radius: 8px;}
    </style>
    <div class="logo-container">
        <img src="LOGO (1).png" class="logo-img" alt="MUPAI Logo">
    </div>
""", unsafe_allow_html=True)

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

# ---------- PDF CON PIE DE PÁGINA Y LOGO ----------
class PDFConPie(FPDF):
    def header(self):
        self.image("LOGO (1).png", x=60, y=8, w=90)
        self.ln(30)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(80,80,80)
        self.cell(0, 10, 'Dirigido por Erick De Luna, Lic. en Ciencias del Ejercicio (UANL), Maestría en Fuerza y Acondicionamiento Físico (FSI).', 0, 0, 'C')

def generar_pdf(usuario, resumen, tabla_bf_txt, tabla_ffmi_txt):
    pdf = PDFConPie()
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
    with smtplib.SMTP_SSL('smtp.zoho.com', 465) as server:
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())

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
    st.error("Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.info("Por favor, ingresa tus datos para continuar")
elif authentication_status:
    authenticator.logout("Cerrar sesión", "sidebar")

    st.title("Cuestionario Digital MUPAI")
    st.write("**Digital Training Science**")

    # --- FORMULARIO ---
    nombre = st.text_input("Nombre completo*")
    edad = st.number_input("Edad*", min_value=10, max_value=90, step=1)
    genero = st.selectbox("Género*", ["Hombre", "Mujer"])
    estatura = st.number_input("Estatura (cm)*", min_value=120, max_value=230, step=1)
    peso = st.number_input("Peso (kg)*", min_value=30.0, max_value=200.0, step=0.1)
    email_usuario = st.text_input("Tu correo electrónico*")
    telefono = st.text_input("Número de teléfono (opcional)")
    metodo_grasa = st.selectbox("¿Qué método usaste para medir tu porcentaje de grasa?", ["Omron HBF-516 (BIA)", "DEXA (Gold Standard)"])
    grasa_reportada = st.number_input("Porcentaje de grasa reportado (%)", min_value=5.0, max_value=50.0, step=0.1)
    descargo = st.checkbox("He leído y acepto la política de privacidad...")

    enviar = st.button("Enviar y ver mi resumen")
    campos_ok = all([nombre, edad, genero, estatura, peso, email_usuario, grasa_reportada, descargo])

    if enviar and campos_ok:
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
            "Teléfono": telefono,
            "Método %BF": metodo_grasa,
            "%BF reportado": f"{grasa_reportada:.1f}%",
            "%BF corregido (DEXA)": f"{grasa_corregida:.1f}%",
        }
        resumen = {
            "Nivel de grasa corporal": nivel_grasa,
            "FFMI": f"{ffmi:.2f} — {nivel_ffmi}",
            "MLG": f"{mlg:.1f} kg",
        }
        tabla_bf_txt = render_tabla(tabla_bf(genero))
        tabla_ffmi_txt = render_tabla(tabla_ffmi(genero))

        # --- Generar PDF ---
        pdf_bytes = generar_pdf(usuario, resumen, tabla_bf_txt, tabla_ffmi_txt)
        st.download_button(
            label="Descargar mi resumen en PDF",
            data=pdf_bytes,
            file_name=f"Resumen_MUPAI_{nombre.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

        # --- Mostrar resumen simplificado al usuario ---
        st.markdown("## Resumen de tus resultados")
        st.info(f"**Nombre:** {nombre}")
        st.info(f"**Edad:** {edad} años")
        st.info(f"**Género:** {genero}")
        st.info(f"**Estatura:** {estatura} cm")
        st.info(f"**Peso:** {peso} kg")
        st.info(f"**% de grasa corporal reportado:** {grasa_reportada:.1f}% ({metodo_grasa})")
        if metodo_grasa == "Omron HBF-516 (BIA)":
            st.info(f"**% de grasa corporal corregido (DEXA):** {grasa_corregida:.1f}%")
        st.success(f"**Clasificación de grasa corporal:** {nivel_grasa}")
        st.success(f"**FFMI:** {ffmi:.2f} — {nivel_ffmi}")

        st.markdown("### Tablas de referencia")
        st.markdown(tabla_bf_txt)
        st.markdown(tabla_ffmi_txt)
        st.markdown("> Tu resumen profesional completo será revisado por tu entrenador.")

        # --- Enviar TODO por email a ti ---
        remitente = "administracion@muscleupgym.fitness"
        destinatario = "administracion@muscleupgym.fitness"
        ZOHO_APP_PASSWORD = "AQUI_TU_PASSWORD_DE_APP"  # Cambia por tu password de app Zoho
        asunto = f"Nuevo cuestionario MUPAI: {nombre} ({date.today().strftime('%d/%m/%Y')})"
        body = "<br>".join([f"<b>{k}:</b> {v}" for k, v in {**usuario, **resumen}.items()])
        try:
            enviar_email(remitente, ZOHO_APP_PASSWORD, destinatario, asunto, body, pdf_bytes, f"{nombre}_MUPAI.pdf")
            st.success("¡Tus datos han sido enviados a tu entrenador! Pronto te contactaremos.")
        except Exception as e:
            st.warning("No se pudo enviar tu información por email. Contacta a tu entrenador para confirmar recepción.")
            print(str(e))

    elif enviar:
        st.warning("Completa todos los campos obligatorios y acepta el descargo para enviar.")

    # --- PIE DE PÁGINA ---
    pie_streamlit()

# ---------- DISPLAY YOUR OWN CODE ----------
st.markdown("---")
st.header("Código fuente de la app")
with open(__file__, "r", encoding="utf-8") as f:
    code = f.read()
st.code(code, language="python")

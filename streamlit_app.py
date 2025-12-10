import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
import random
import string

# ==================== CONSTANTES PARA FFMI CONFIDENCE ====================
# Rangos de grasa corporal saludable (límite superior) por sexo
HEALTHY_UPPER = {
    'Hombre': 25.0,
    'Mujer': 32.0
}

# Punto donde la confianza llega a cero (soft zero) - muy alto % de grasa
SOFT_ZERO_AT = {
    'Hombre': 38.0,
    'Mujer': 42.0
}

# Factores de confianza del método de medición
METHOD_CONFIDENCE = {
    'DEXA (Gold Standard)': 1.0,
    'InBody 270 (BIA profesional)': 0.97,
    'Bod Pod (Pletismografía)': 0.98,
    'Omron HBF-516 (BIA)': 0.92
}

# Umbral mínimo de confianza para considerar el FFMI evaluable
FFMI_CONFIDENCE_THRESHOLD = 0.50

# ==================== CONFIGURABLES NUEVOS (AUTO EXTRAPOLATION & LBM) ===
MAX_EXTRAPOLATE = 60.0
AUTO_EXTRAPOLATE_THRESHOLD = 45.0   # >= este valor extrapola automáticamente
SLOPE_LAST_SEGMENT = 1.0            # %DEXA por cada 1 unidad Omron (según tabla actual)
PSMF_LBM_THRESHOLD = {"Hombre": 35.0, "Mujer": 40.0}
PROTEIN_FACTOR_PSMF_LBM = 1.8
PROTEIN_FACTOR_TRAD_LBM = 1.6
CARB_MIN_G = 50.0
FAT_FLOOR_G = 20.0
TEI_MIN = {"Hombre": 1400, "Mujer": 1200}
MAX_DEFICIT = 0.35
# ======================================================================

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
... (remaining CSS and file content unchanged) ...
""")
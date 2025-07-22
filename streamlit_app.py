import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Configuración de página con tema personalizado
st.set_page_config(
    page_title="MUPAI - Evaluación Fitness Personalizada",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado con paleta de colores MUPAI
st.markdown("""
<style>
    /* Variables de color */
    :root {
        --mupai-yellow: #F4C430;
        --mupai-dark-yellow: #DAA520;
        --mupai-black: #1E1E1E;
        --mupai-gray: #2D2D2D;
        --mupai-light-gray: #F5F5F5;
        --mupai-white: #FFFFFF;
        --mupai-success: #27AE60;
        --mupai-warning: #F39C12;
        --mupai-danger: #E74C3C;
    }
    
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
        color: var(--mupai-black);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(244, 196, 48, 0.3);
    }
    
    /* Tarjetas de contenido */
    .content-card {
        background: var(--mupai-white);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--mupai-yellow);
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
        color: var(--mupai-black);
        border: none;
        padding: 0.75rem 2rem;
        font-weight: bold;
        border-radius: 25px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(244, 196, 48, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(244, 196, 48, 0.4);
    }
    
    /* Inputs estilizados */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid var(--mupai-light-gray);
        border-radius: 10px;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--mupai-yellow);
        box-shadow: 0 0 0 2px rgba(244, 196, 48, 0.2);
    }
    
    /* Métricas estilizadas */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, var(--mupai-light-gray) 0%, var(--mupai-white) 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--mupai-yellow);
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Expander personalizado */
    .streamlit-expanderHeader {
        background: var(--mupai-light-gray);
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* Alertas personalizadas */
    .stAlert > div {
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Tablas estilizadas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: var(--mupai-light-gray);
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Tooltips */
    [data-baseweb="tooltip"] {
        background: var(--mupai-black) !important;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Sombras para profundidad */
    .shadow-sm { box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .shadow-md { box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
    .shadow-lg { box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
    
    /* Badges personalizados */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
    }
    
    .badge-success {
        background: var(--mupai-success);
        color: white;
    }
    
    .badge-warning {
        background: var(--mupai-warning);
        color: white;
    }
    
    .badge-danger {
        background: var(--mupai-danger);
        color: white;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        .content-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal con logo y título
st.markdown("""
<div class="main-header fade-in">
    <h1 style="font-size: 3rem; margin: 0; font-weight: 900;">🏋️ MUPAI</h1>
    <p style="font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;">Evaluación Fitness Personalizada</p>
    <p style="font-size: 1rem; margin: 0; opacity: 0.8;">Tu experiencia fitness basada en ciencia y profesionalismo</p>
</div>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if "datos_completos" not in st.session_state:
    st.session_state.datos_completos = False
if "correo_enviado" not in st.session_state:
    st.session_state.correo_enviado = False

# Función para crear tarjetas de contenido
def crear_tarjeta(titulo, contenido, tipo="info"):
    colores = {
        "info": "--mupai-yellow",
        "success": "--mupai-success",
        "warning": "--mupai-warning",
        "danger": "--mupai-danger"
    }
    color = colores.get(tipo, "--mupai-yellow")
    
    return f"""
    <div class="content-card" style="border-left-color: var({color});">
        <h3 style="color: var(--mupai-black); margin-bottom: 1rem;">{titulo}</h3>
        <div style="color: var(--mupai-gray);">{contenido}</div>
    </div>
    """

# Misión, Visión y Compromiso
with st.expander("🎯 **Misión, Visión y Compromiso MUPAI**", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(crear_tarjeta(
            "🎯 Misión",
            "Hacer accesible el entrenamiento basado en ciencia, ofreciendo planes personalizados a todos los niveles de condición física."
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(crear_tarjeta(
            "👁️ Visión",
            "Ser referente global en entrenamiento digital personalizado, uniendo investigación y experiencia práctica."
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(crear_tarjeta(
            "🤝 Política",
            "Nos guiamos por la ética, responsabilidad y precisión científica para ofrecer resultados reales y sostenibles."
        ), unsafe_allow_html=True)

# Funciones auxiliares
def calcular_tmb_cunningham(mlg):
    return 500 + (22 * mlg)

def calcular_mlg(peso, porcentaje_grasa):
    return peso * (1 - porcentaje_grasa / 100)

def corregir_porcentaje_grasa(medido, metodo, sexo):
    if metodo == "Omron HBF-306 o similar (BIA básico)":
        factor = 1.1 if sexo == "Mujer" else 1.15
    elif metodo == "Omron HBF-516 o similar (BIA avanzado)":
        factor = 1.05 if sexo == "Mujer" else 1.06
    elif metodo == "InBody 270 (BIA profesional)":
        factor = 1.02
    elif metodo == "Bod Pod (Pletismografía)":
        factor = 1.0 if sexo == "Mujer" else 1.03
    else:
        factor = 1.0
    return medido * factor

def calcular_ffmi(mlg, estatura_cm):
    estatura_m = estatura_cm / 100
    ffmi = mlg / (estatura_m ** 2)
    ffmi_normalizado = ffmi + 6.3 * (1.8 - estatura_m)
    return ffmi_normalizado

def clasificar_ffmi(ffmi, sexo):
    if sexo == "Hombre":
        limites = [(18, "Bajo"), (20, "Promedio"), (22, "Bueno"), (25, "Avanzado"), (100, "Élite")]
    else:
        limites = [(15, "Bajo"), (17, "Promedio"), (19, "Bueno"), (21, "Avanzado"), (100, "Élite")]
    
    for limite, clasificacion in limites:
        if ffmi < limite:
            return clasificacion
    return "Élite"

def calculate_psmf(sexo, peso, grasa_corregida, mlg):
    if sexo == "Hombre" and grasa_corregida > 18:
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": round(mlg * 2.2, 1),
            "calorias_dia": round(mlg * 24, 0),
            "calorias_piso_dia": 800,
            "criterio": "PSMF recomendado por % grasa"
        }
    elif sexo == "Mujer" and grasa_corregida > 23:
        return {
            "psmf_aplicable": True,
            "proteina_g_dia": round(mlg * 2, 1),
            "calorias_dia": round(mlg * 22, 0),
            "calorias_piso_dia": 700,
            "criterio": "PSMF recomendado por % grasa"
        }
    else:
        return {"psmf_aplicable": False}

def sugerir_deficit(porcentaje_grasa, sexo):
    rangos_hombre = [
        (0, 8, 3), (8.1, 10.5, 5), (10.6, 13, 10), (13.1, 15.5, 15),
        (15.6, 18, 20), (18.1, 20.5, 25), (20.6, 23, 27), (23.1, 25.5, 29),
        (25.6, 30, 30), (30.1, 32.5, 35), (32.6, 35, 40), (35.1, 37.5, 45), (37.6, 100, 50)
    ]
    rangos_mujer = [
        (0, 14, 3), (14.1, 16.5, 5), (16.6, 19, 10), (19.1, 21.5, 15),
        (21.6, 24, 20), (24.1, 26.5, 25), (26.6, 29, 27), (29.1, 31.5, 29),
        (31.6, 35, 30), (35.1, 37.5, 35), (37.6, 40, 40), (40.1, 42.5, 45), (42.6, 100, 50)
    ]
    
    if sexo.lower() == "hombre":
        tabla = rangos_hombre
        tope = 30
        limite_extra = 30
    elif sexo.lower() == "mujer":
        tabla = rangos_mujer
        tope = 30
        limite_extra = 35
    else:
        return None
    
    for minimo, maximo, deficit in tabla:
        if minimo <= porcentaje_grasa <= maximo:
            if porcentaje_grasa > limite_extra:
                return deficit
            else:
                return min(deficit, tope)
    return None

def calcular_edad_metabolica(edad_cronologica, porcentaje_grasa, sexo):
    if sexo == "Hombre":
        grasa_ideal = 15
    else:
        grasa_ideal = 22
    
    diferencia_grasa = porcentaje_grasa - grasa_ideal
    ajuste_edad = diferencia_grasa * 0.3
    edad_metabolica = edad_cronologica + ajuste_edad
    
    return max(18, min(80, round(edad_metabolica)))

def enviar_email_resumen(contenido, nombre_cliente, email_cliente, fecha, edad, telefono):
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("email_password", "tu_contraseña_aquí")
        
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

# BLOQUE 0: Datos personales
st.markdown('<div class="content-card shadow-md fade-in">', unsafe_allow_html=True)
st.markdown("### 👤 Datos Personales")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez García")
    telefono = st.text_input("Teléfono", placeholder="Ej: 8661234567")
    email_cliente = st.text_input("Email", placeholder="Ej: correo@ejemplo.com")

with col2:
    edad = st.number_input("Edad (años)", min_value=15, max_value=80, value=25)
    sexo = st.selectbox("Sexo biológico", ["Hombre", "Mujer"])
    fecha_llenado = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

st.markdown('</div>', unsafe_allow_html=True)

# Validación de datos personales
datos_personales_completos = all([nombre, telefono, email_cliente])

if datos_personales_completos:
    st.success("✅ Datos personales completos. Continúa con tu evaluación.")
    
    # BLOQUE 1: Datos antropométricos
    with st.expander("📊 **Paso 1: Datos Antropométricos y Composición Corporal**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            peso = st.number_input("⚖️ Peso corporal (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        with col2:
            estatura = st.number_input("📏 Estatura (cm)", min_value=120, max_value=220, value=170)
        
        metodo_grasa = st.selectbox(
            "Método utilizado para medir grasa corporal",
            ["Omron HBF-306 o similar (BIA básico)",
             "Omron HBF-516 o similar (BIA avanzado)",
             "InBody 270 (BIA profesional)",
             "Bod Pod (Pletismografía)",
             "DEXA (Gold Standard)"]
        )
        
        with col3:
            grasa_corporal = st.number_input(
                f"% de grasa corporal medido con {metodo_grasa.split('(')[0].strip()}",
                min_value=3.0, max_value=60.0, value=20.0, step=0.1
            )
        
        # Cálculos
        grasa_corregida = corregir_porcentaje_grasa(grasa_corporal, metodo_grasa, sexo)
        mlg = calcular_mlg(peso, grasa_corregida)
        tmb = calcular_tmb_cunningham(mlg)
        ffmi = calcular_ffmi(mlg, estatura)
        nivel = clasificar_ffmi(ffmi, sexo)
        edad_metabolica = calcular_edad_metabolica(edad, grasa_corregida, sexo)
        
        # Mostrar resultados con diseño mejorado
        st.markdown("### 📈 Resultados de composición corporal:")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("% Grasa (DEXA)", f"{grasa_corregida:.1f}%", 
                     f"Corregido desde {grasa_corporal}%")
        with col2:
            st.metric("MLG", f"{mlg:.1f} kg", "Masa Libre de Grasa")
        with col3:
            st.metric("TMB", f"{tmb:.0f} kcal", "Tasa Metabólica Basal")
        with col4:
            st.metric("Edad Metabólica", f"{edad_metabolica} años",
                     f"{'+' if edad_metabolica > edad else ''}{edad_metabolica - edad} años")
        
        # FFMI con indicador visual
        st.markdown("### 💪 Índice de Masa Libre de Grasa (FFMI)")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric("Tu FFMI", f"{ffmi:.2f}", f"Nivel: {nivel}")
            
            # Barra de progreso visual
            if sexo == "Hombre":
                ffmi_max = 25
                rangos = {"Bajo": 18, "Promedio": 20, "Bueno": 22, "Avanzado": 25}
            else:
                ffmi_max = 21
                rangos = {"Bajo": 15, "Promedio": 17, "Bueno": 19, "Avanzado": 21}
            
            progreso = min(ffmi / ffmi_max, 1.0)
            st.progress(progreso)
            st.caption(f"Progreso hacia el potencial natural máximo: {progreso*100:.0f}%")
        
        with col2:
            st.info(f"""
            **Referencia FFMI ({sexo}):**
            - Bajo: <{rangos['Bajo']}
            - Promedio: {rangos['Bajo']}-{rangos['Promedio']}
            - Bueno: {rangos['Promedio']}-{rangos['Bueno']}
            - Avanzado: {rangos['Bueno']}-{rangos['Avanzado']}
            - Élite: >{rangos['Avanzado']}
            """)
        
        # Cálculo y mostrar PSMF si aplica
        psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
        
        if psmf_recs["psmf_aplicable"]:
            st.warning(f"""
            ⚡ **Por tu % de grasa corporal ({grasa_corregida:.1f}%), podrías beneficiarte de una fase rápida PSMF:**
            - 🥩 Proteína: {psmf_recs['proteina_g_dia']} g/día
            - 🔥 Calorías: {psmf_recs['calorias_dia']} kcal/día
            - ⚠️ Piso calórico mínimo: {psmf_recs['calorias_piso_dia']} kcal/día
            - 📋 {psmf_recs['criterio']}
            """)
        
        # Advertencia sobre rango de grasa
        rango_grasa_ok = (4, 12) if sexo == "Hombre" else (10, 18)
        fuera_rango = grasa_corregida < rango_grasa_ok[0] or grasa_corregida > rango_grasa_ok[1]
        
        if fuera_rango:
            st.info(f"""
            ℹ️ Para estimar con mayor precisión el FFMI, tu porcentaje de grasa debería estar en el rango 
            recomendado: {rango_grasa_ok[0]}-{rango_grasa_ok[1]}%. El valor mostrado puede 
            {'subestimar' if grasa_corregida < rango_grasa_ok[0] else 'sobrestimar'} tu potencial muscular natural.
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BLOQUE 2: Evaluación integral del nivel de entrenamiento
    with st.expander("💪 **Evaluación Integral de tu Nivel de Entrenamiento**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        experiencia = st.radio(
            "¿Cuál describe mejor tu experiencia reciente?",
            ["A) Entreno solo ocasionalmente",
             "B) Entreno regular (2+ veces/semana)",
             "C) Entreno constante y estructurado",
             "D) Diseño mis propios planes"]
        )
        
        # Sistema de evaluación por ejercicios
        st.markdown("### 🏋️ Evaluación de rendimiento por categoría")
        st.info("Selecciona tu mejor ejercicio en cada categoría y proporciona tu rendimiento máximo")
        
        ejercicios_data = {}
        
        # Empuje superior
        col1, col2 = st.columns(2)
        with col1:
            empuje = st.selectbox(
                "Empuje superior - Elige tu mejor ejercicio:",
                ["Flexiones", "Fondos", "Press banca"]
            )
        with col2:
            if empuje in ["Flexiones", "Fondos"]:
                empuje_reps = st.number_input(f"Repeticiones máximas en {empuje}", 
                                             min_value=0, max_value=100, value=10)
                ejercicios_data[empuje] = empuje_reps
            else:
                col2a, col2b = st.columns(2)
                with col2a:
                    press_reps = st.number_input("Repeticiones en Press banca", 
                                                min_value=1, max_value=30, value=8)
                with col2b:
                    press_peso = st.number_input("Peso (kg) en Press banca", 
                                               min_value=20, max_value=300, value=60)
                ejercicios_data[empuje] = (press_reps, press_peso)
        
        # Tracción superior
        col1, col2 = st.columns(2)
        with col1:
            traccion = st.selectbox(
                "Tracción superior - Elige tu mejor ejercicio:",
                ["Dominadas", "Remo invertido"]
            )
        with col2:
            traccion_reps = st.number_input(f"Repeticiones máximas en {traccion}", 
                                          min_value=0, max_value=50, value=5)
            ejercicios_data[traccion] = traccion_reps
        
        # Pierna
        col1, col2 = st.columns(2)
        with col1:
            pierna = st.selectbox(
                "Pierna - Elige tu mejor ejercicio:",
                ["Sentadilla", "Peso muerto", "Hip thrust"]
            )
        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                pierna_reps = st.number_input(f"Repeticiones en {pierna}", 
                                            min_value=1, max_value=30, value=8)
            with col2b:
                pierna_peso = st.number_input(f"Peso (kg) en {pierna}", 
                                            min_value=0, max_value=400, value=80)
            ejercicios_data[pierna] = (pierna_reps, pierna_peso)
        
        # Core
        col1, col2 = st.columns(2)
        with col1:
            core = st.selectbox(
                "Core - Elige tu mejor ejercicio:",
                ["Plancha", "Ab wheel", "L-sit"]
            )
        with col2:
            if core == "Plancha":
                core_tiempo = st.number_input("Tiempo máximo en Plancha (segundos)", 
                                            min_value=0, max_value=600, value=60)
                ejercicios_data[core] = core_tiempo
            else:
                core_reps = st.number_input(f"Repeticiones máximas en {core}", 
                                          min_value=0, max_value=100, value=10)
                ejercicios_data[core] = core_reps
        
        # Cálculo del nivel funcional
        niveles_ejercicios = {}
        referencias = {
            "Flexiones": {"Hombre": [(5, "Bajo"), (12, "Promedio"), (25, "Bueno"), (40, "Avanzado")],
                         "Mujer": [(2, "Bajo"), (8, "Promedio"), (15, "Bueno"), (25, "Avanzado")]},
            "Fondos": {"Hombre": [(5, "Bajo"), (12, "Promedio"), (20, "Bueno"), (30, "Avanzado")],
                      "Mujer": [(2, "Bajo"), (5, "Promedio"), (10, "Bueno"), (15, "Avanzado")]},
            "Dominadas": {"Hombre": [(2, "Bajo"), (5, "Promedio"), (10, "Bueno"), (15, "Avanzado")],
                         "Mujer": [(0, "Bajo"), (2, "Promedio"), (5, "Bueno"), (8, "Avanzado")]},
            "Plancha": {"Hombre": [(20, "Bajo"), (40, "Promedio"), (60, "Bueno"), (90, "Avanzado")],
                       "Mujer": [(15, "Bajo"), (30, "Promedio"), (45, "Bueno"), (70, "Avanzado")]}
        }
        
        # Mostrar nivel para cada ejercicio
        st.markdown("### 📊 Tu nivel en cada ejercicio:")
        for ejercicio, valor in ejercicios_data.items():
            if ejercicio in referencias and sexo in referencias[ejercicio]:
                tabla_ref = referencias[ejercicio][sexo]
                nivel_ej = "Bajo"
                for limite, niv in tabla_ref:
                    if isinstance(valor, tuple):
                        # Para ejercicios con peso
                        nivel_ej = niv  # Simplificado para el ejemplo
                    else:
                        if valor >= limite:
                            nivel_ej = niv
                niveles_ejercicios[ejercicio] = nivel_ej
                
                # Crear badge de color según nivel
                color_badge = {
                    "Bajo": "danger",
                    "Promedio": "warning", 
                    "Bueno": "success",
                    "Avanzado": "success"
                }[nivel_ej]
                
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <strong>{ejercicio}:</strong> {valor} {'reps' if not isinstance(valor, tuple) else f'reps x {valor[1]}kg'} 
                    <span class="badge badge-{color_badge}" style="margin-left: 1rem;">{nivel_ej}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Calcular nivel de entrenamiento combinado
        puntos_ffmi = {"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4, "Élite": 5}[nivel]
        puntos_exp = {"A)": 1, "B)": 2, "C)": 3, "D)": 4}[experiencia[0:2]]
        puntos_funcional = sum([{"Bajo": 1, "Promedio": 2, "Bueno": 3, "Avanzado": 4}.get(n, 1) 
                               for n in niveles_ejercicios.values()]) / len(niveles_ejercicios)
        
        puntaje_total = (puntos_ffmi/5 + puntos_funcional/4 + puntos_exp/4) / 3
        
        if puntaje_total < 0.3:
            nivel_entrenamiento = "principiante"
        elif puntaje_total < 0.5:
            nivel_entrenamiento = "intermedio"
        elif puntaje_total < 0.7:
            nivel_entrenamiento = "avanzado"
        else:
            nivel_entrenamiento = "élite"
        
        # Mostrar resumen con diseño atractivo
        st.markdown("### 🎯 Resumen de tu evaluación:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("FFMI", f"{puntos_ffmi}/5", nivel)
        with col2:
            st.metric("Funcional", f"{puntos_funcional:.1f}/4", "Rendimiento")
        with col3:
            st.metric("Experiencia", f"{puntos_exp}/4", experiencia[3:20])
        with col4:
            st.metric("Nivel Global", nivel_entrenamiento.capitalize(), f"Score: {puntaje_total:.2f}")
        
        # Cálculo del potencial genético
        if sexo == "Hombre":
            ffmi_genetico_max = {
                "principiante": 22, "intermedio": 23.5,
                "avanzado": 24.5, "élite": 25
            }[nivel_entrenamiento]
        else:
            ffmi_genetico_max = {
                "principiante": 19, "intermedio": 20,
                "avanzado": 20.5, "élite": 21
            }[nivel_entrenamiento]
        
        porc_potencial = (ffmi / ffmi_genetico_max) * 100
        
        st.info(f"""
        📈 **Tu desarrollo muscular actual:** Has alcanzado aproximadamente el **{porc_potencial:.0f}%** 
        de tu potencial muscular natural estimado (FFMI máximo estimado: {ffmi_genetico_max:.1f})
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BLOQUE 3: Nivel de actividad física diaria
    with st.expander("🚶 **Paso 2: Nivel de Actividad Física Diaria (GEAF/PA)**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        nivel_actividad = st.radio(
            "Selecciona tu nivel de actividad física diaria:",
            ["Sedentario (trabajo de oficina, <5,000 pasos/día)",
             "Moderadamente activo (trabajo mixto, 5,000-10,000 pasos/día)",
             "Activo (trabajo físico o deportes regulares, 10,000-12,500 pasos/día)",
             "Muy activo (trabajo muy físico o atleta, >12,500 pasos/día)"]
        )
        
        # Asignar GEAF según nivel
        geaf_valores = {
            "Sedentario": 1.1,
            "Moderadamente activo": 1.15,
            "Activo": 1.25,
            "Muy activo": 1.35
        }
        geaf = geaf_valores[nivel_actividad.split()[0]]
        
        st.success(f"""
        ✅ Tu nivel de actividad física diaria es **{nivel_actividad.split()[0]}**
        
        Factor GEAF/PA: **{geaf}**
        """)
        
        # Visualización del nivel de actividad
        col1, col2 = st.columns([3, 1])
        with col1:
            nivel_idx = list(geaf_valores.keys()).index(nivel_actividad.split()[0])
            st.progress((nivel_idx + 1) / 4)
        with col2:
            st.metric("GEAF", geaf)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BLOQUE 4: Efecto térmico de los alimentos
    with st.expander("🍽️ **Paso 3: Efecto Térmico de los Alimentos (ETA)**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # ETA basado en composición corporal
        if grasa_corregida <= 10 and sexo == "Hombre":
            eta = 1.15
            eta_desc = "ETA alto (muy magro)"
        elif grasa_corregida <= 20 and sexo == "Mujer":
            eta = 1.15
            eta_desc = "ETA alto (muy magra)"
        elif grasa_corregida <= 20 and sexo == "Hombre":
            eta = 1.12
            eta_desc = "ETA medio (magro)"
        elif grasa_corregida <= 30 and sexo == "Mujer":
            eta = 1.12
            eta_desc = "ETA medio (normal)"
        else:
            eta = 1.10
            eta_desc = "ETA bajo (más de 20% grasa en hombres o 30% en mujeres)"
        
        st.info(f"""
        📊 Tu ETA estimado es **{eta}** ({eta_desc})
        
        El ETA representa el gasto calórico de digerir y procesar los alimentos, 
        y varía según tu composición corporal.
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BLOQUE 5: Entrenamiento de fuerza
    with st.expander("🏋️ **Paso 4: Entrenamiento de fuerza y GEE**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        dias_fuerza = st.slider(
            "¿Cuántos días por semana entrenas fuerza?",
            min_value=0, max_value=7, value=3
        )
        
        # Cálculo del GEE según nivel
        if nivel in ["Bajo", "Promedio"]:
            kcal_sesion = 300
            nivel_gee = "300 kcal/sesión (nivel muscular bajo/promedio)"
        elif nivel in ["Bueno", "Avanzado"]:
            kcal_sesion = 400
            nivel_gee = "400 kcal/sesión (nivel muscular bueno/avanzado)"
        else:
            kcal_sesion = 500
            nivel_gee = "500 kcal/sesión (nivel muscular élite)"
        
        gee_semanal = dias_fuerza * kcal_sesion
        gee_prom_dia = gee_semanal / 7
        
        # Mostrar resultados con visualización
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Días/semana", dias_fuerza)
        with col2:
            st.metric("Gasto/sesión", f"{kcal_sesion} kcal")
        with col3:
            st.metric("Promedio diario", f"{gee_prom_dia:.0f} kcal")
        
        st.success(f"""
        💪 Según tu nivel muscular ({nivel}), tu gasto es de {nivel_gee}
        
        📊 Gasto semanal total: **{gee_semanal} kcal** (~{gee_prom_dia:.0f} kcal/día promedio)
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BLOQUE 6: Cálculo final y comparativa
    with st.expander("📈 **Paso 5: Ingesta Calórica Total Diaria (Personalizado)**", expanded=True):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Determinar fase nutricional
        if sexo == "Hombre":
            if grasa_corregida < 10:
                fase = "Superávit recomendado: 10-15%"
                porcentaje = -12.5
            elif grasa_corregida <= 18:
                fase = "Mantenimiento o minivolumen"
                porcentaje = 0
            else:
                porcentaje = sugerir_deficit(grasa_corregida, sexo)
                fase = f"Déficit recomendado: {porcentaje}%"
        else:
            if grasa_corregida < 16:
                fase = "Superávit recomendado: 10%"
                porcentaje = -10
            elif grasa_corregida <= 23:
                fase = "Mantenimiento"
                porcentaje = 0
            else:
                porcentaje = sugerir_deficit(grasa_corregida, sexo)
                fase = f"Déficit recomendado: {porcentaje}%"
        
        fbeo = 1 - porcentaje / 100
        
        # Mostrar perfil del usuario con diseño atractivo
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);">
            <h4>📋 Tu perfil:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"• **Sexo:** {sexo}")
            st.write(f"• **% Grasa corporal (DEXA):** {grasa_corregida:.1f}%")
            st.write(f"• **FFMI:** {ffmi:.2f} ({nivel})")
        with col2:
            st.write(f"• **Nivel de entrenamiento:** {nivel_entrenamiento.capitalize()}")
            st.write(f"• **Edad metabólica:** {edad_metabolica} años")
            st.write(f"• **Fase sugerida:** {fase}")
        
        # Cálculo del gasto energético
        GE = tmb * geaf * eta + gee_prom_dia
        ingesta_calorica_tradicional = GE * fbeo
        
        # COMPARATIVA SI APLICA PSMF
        if psmf_recs["psmf_aplicable"]:
            st.warning("⚠️ **Eres candidato para protocolo PSMF**")
            
            # Selector de plan
            plan_elegido = st.radio(
                "🎯 **Elige tu estrategia nutricional:**",
                ["Plan Tradicional (déficit moderado, más sostenible)",
                 "Protocolo PSMF (pérdida rápida, más restrictivo)"],
                index=0
            )
            
            # Mostrar comparativa visual
            st.markdown("### 📊 Comparativa de planes:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="content-card" style="border-left-color: var(--mupai-success);">
                    <h4>✅ Plan Tradicional</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric("Déficit", f"{porcentaje}%")
                st.metric("Calorías", f"{ingesta_calorica_tradicional:.0f} kcal/día")
                st.metric("Pérdida esperada", "0.5-0.7 kg/semana")
                st.write("**Ventajas:**")
                st.write("• Mayor adherencia")
                st.write("• Más energía para entrenar")
                st.write("• Sostenible largo plazo")
                st.write("• Menor pérdida muscular")
            
            with col2:
                st.markdown("""
                <div class="content-card" style="border-left-color: var(--mupai-warning);">
                    <h4>⚡ Protocolo PSMF</h4>
                </div>
                """, unsafe_allow_html=True)
                
                deficit_psmf = int((1 - psmf_recs['calorias_dia']/GE) * 100)
                st.metric("Déficit", f"~{deficit_psmf}%")
                st.metric("Calorías", f"{psmf_recs['calorias_dia']:.0f} kcal/día")
                st.metric("Pérdida esperada", "0.8-1.2 kg/semana")
                st.write("**Consideraciones:**")
                st.write("• Muy restrictivo")
                st.write("• Máximo 6-8 semanas")
                st.write("• Requiere supervisión")
                st.write("• Solo proteína + verduras")
            
            # Aplicar plan elegido
            if plan_elegido == "Protocolo PSMF (pérdida rápida, más restrictivo)":
                ingesta_calorica = psmf_recs['calorias_dia']
                proteina_g = psmf_recs['proteina_g_dia']
                proteina_kcal = proteina_g * 4
                carbo_g = 30
                carbo_kcal = carbo_g * 4
                grasa_kcal = max(ingesta_calorica - proteina_kcal - carbo_kcal, 90)
                grasa_g = round(grasa_kcal / 9, 1)
                fase = f"PSMF - Pérdida rápida (déficit ~{deficit_psmf}%)"
                
                st.error("""
                ⚠️ **ADVERTENCIA IMPORTANTE SOBRE PSMF:**
                - Es un protocolo muy restrictivo
                - Duración máxima: 6-8 semanas
                - Requiere supervisión profesional
                - Suplementación recomendada: multivitamínico, omega-3, electrolitos
                """)
            else:
                ingesta_calorica = ingesta_calorica_tradicional
                # Cálculo de macros tradicional
                proteina_factor = 2.5 if grasa_corregida < 15 else 2.2 if grasa_corregida < 25 else 2.0
                proteina_g = round(mlg * proteina_factor, 1)
                proteina_kcal = proteina_g * 4
                
                if porcentaje > 20:
                    prop_grasa = 0.35
                elif porcentaje > 0:
                    prop_grasa = 0.30
                else:
                    prop_grasa = 0.25
                
                grasa_kcal = ingesta_calorica * prop_grasa
                grasa_g = round(grasa_kcal / 9, 1)
                carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
                carbo_g = round(carbo_kcal / 4, 1)
        else:
            # Sin PSMF, cálculo tradicional directo
            ingesta_calorica = ingesta_calorica_tradicional
            proteina_factor = 2.5 if grasa_corregida < 15 else 2.2 if grasa_corregida < 25 else 2.0
            proteina_g = round(mlg * proteina_factor, 1)
            proteina_kcal = proteina_g * 4
            
            if porcentaje > 20:
                prop_grasa = 0.35
            elif porcentaje > 0:
                prop_grasa = 0.30
            else:
                prop_grasa = 0.25
            
            grasa_kcal = ingesta_calorica * prop_grasa
            grasa_g = round(grasa_kcal / 9, 1)
            carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
            carbo_g = round(carbo_kcal / 4, 1)
        
        # Mostrar cálculo detallado
        st.markdown("### 🧮 Cálculo detallado:")
        st.code(f"""
Gasto Energético (GE) = TMB × GEAF × ETA + GEE
GE = {tmb:.0f} × {geaf} × {eta} + {gee_prom_dia:.0f} = {GE:.0f} kcal

Ingesta calórica = GE × FBEO
Ingesta = {GE:.0f} × {fbeo:.2f} = {ingesta_calorica:.0f} kcal/día
""")
        
        # Mostrar resultado final con diseño premium
        st.markdown("### 🎯 Tu plan nutricional personalizado:")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calorías totales", f"{ingesta_calorica:.0f} kcal/día", fase)
        with col2:
            st.metric("🥩 Proteína", f"{proteina_g} g", f"{proteina_kcal:.0f} kcal")
        with col3:
            st.metric("🥑 Grasas", f"{grasa_g} g", f"{grasa_kcal:.0f} kcal")
        with col4:
            st.metric("🍞 Carbohidratos", f"{carbo_g} g", f"{carbo_kcal:.0f} kcal")
        
        # Gráfico de distribución de macros
        st.markdown("### 📊 Distribución de macronutrientes:")
        macro_data = {
            "Macronutriente": ["Proteína", "Grasas", "Carbohidratos"],
            "Gramos": [proteina_g, grasa_g, carbo_g],
            "Calorías": [proteina_kcal, grasa_kcal, carbo_kcal],
            "Porcentaje": [
                round(proteina_kcal/ingesta_calorica*100, 1),
                round(grasa_kcal/ingesta_calorica*100, 1),
                round(carbo_kcal/ingesta_calorica*100, 1)
            ]
        }
        df_macros = pd.DataFrame(macro_data)
        st.dataframe(df_macros, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # RESUMEN FINAL
    st.markdown("---")
    st.markdown('<div class="content-card shadow-lg fade-in" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E;">', unsafe_allow_html=True)
    st.markdown("## 🎯 **Resumen Final de tu Evaluación MUPAI**")
    
    # Crear resumen visual con métricas clave
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        ### 👤 Datos Personales
        - **Nombre:** {nombre}
        - **Edad cronológica:** {edad} años
        - **Edad metabólica:** {edad_metabolica} años
        - **Fecha:** {fecha_llenado}
        """)
    
    with col2:
        st.markdown(f"""
        ### 💪 Composición Corporal
        - **Peso:** {peso} kg
        - **Estatura:** {estatura} cm
        - **% Grasa:** {grasa_corregida:.1f}%
        - **FFMI:** {ffmi:.2f} ({nivel})
        """)
    
    with col3:
        st.markdown(f"""
        ### 🍽️ Plan Nutricional
        - **Calorías:** {ingesta_calorica:.0f} kcal/día
        - **Nivel:** {nivel_entrenamiento.capitalize()}
        - **Potencial:** {porc_potencial:.0f}%
        - **Fase:** {fase}
        """)
    
    # Mensaje final personalizado
    diferencia_edad = edad_metabolica - edad
    mensaje_edad = ""
    if diferencia_edad > 2:
        mensaje_edad = f"Tu edad metabólica es {diferencia_edad} años mayor que tu edad cronológica, principalmente por tu % de grasa corporal."
    elif diferencia_edad < -2:
        mensaje_edad = f"¡Excelente! Tu edad metabólica es {abs(diferencia_edad)} años menor que tu edad cronológica."
    else:
        mensaje_edad = "Tu edad metabólica está alineada con tu edad cronológica."
    
    st.success(f"""
    ✅ **Tu evaluación MUPAI ha sido completada exitosamente**
    
    {mensaje_edad}
    
    Tu recomendación personalizada considera tu perfil actual, nivel de entrenamiento y composición corporal. 
    El ajuste calórico sugerido es **{fase}**. Tu ingesta calórica diaria sugerida es de aproximadamente 
    **{ingesta_calorica:.0f} kcal/día**.
    
    {f'⚠️ Nota: Para mayor precisión del FFMI, el % de grasa ideal es {rango_grasa_ok[0]}-{rango_grasa_ok[1]}%. Tu valor actual podría afectar la estimación.' if fuera_rango else ''}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Botón para nueva evaluación
    if st.button("🔄 Realizar nueva evaluación", key="nueva_eval"):
        st.session_state.clear()
        st.rerun()
    
    # ENVÍO DE EMAIL CON TODA LA INFORMACIÓN
    if not st.session_state.get("correo_enviado", False):
        # Construir comparativa si aplica PSMF
        comparativa_psmf = ""
        if psmf_recs["psmf_aplicable"]:
            deficit_psmf_email = int((1 - psmf_recs['calorias_dia']/GE) * 100)
            comparativa_psmf = f"""
COMPARATIVA DE PLANES:
====================
CANDIDATO PARA PSMF: SÍ (% grasa: {grasa_corregida:.1f}%)

1. PLAN TRADICIONAL (Calculado):
   - Déficit: {porcentaje}%
   - Calorías: {ingesta_calorica_tradicional:.0f} kcal/día
   - Proteína: {proteina_g} g (factor {proteina_factor}x MLG)
   - Grasas: {grasa_g} g
   - Carbohidratos: {carbo_g} g
   - Pérdida esperada: 0.5-0.7 kg/semana
   - Sostenibilidad: ALTA
   - Duración: Indefinida
   
2. PROTOCOLO PSMF (Alternativa rápida):
   - Déficit: ~{deficit_psmf_email}%
   - Calorías: {psmf_recs['calorias_dia']} kcal/día
   - Proteína: {psmf_recs['proteina_g_dia']} g
   - Grasas: 10-15 g (esenciales)
   - Carbohidratos: 20-30 g (verduras)
   - Pérdida esperada: 0.8-1.2 kg/semana
   - Sostenibilidad: BAJA
   - Duración máxima: 6-8 semanas
   
PLAN ELEGIDO POR EL USUARIO: {"PSMF" if "PSMF" in fase else "Tradicional"}

RECOMENDACIÓN: Evaluar adherencia del cliente y urgencia de resultados. 
PSMF solo si hay alta motivación y posibilidad de supervisión cercana.
"""
        
        # Construir advertencias mostradas
        advertencias = ""
        if fuera_rango:
            advertencias += f"""
ADVERTENCIAS MOSTRADAS:
- FFMI: % grasa fuera de rango ideal ({rango_grasa_ok[0]}-{rango_grasa_ok[1]}%)
  Actual: {grasa_corregida:.1f}%. Puede afectar precisión de estimaciones.
"""
        
        # Detalles de rendimiento
        detalles_rendimiento = f"""
DETALLES DE RENDIMIENTO:
========================"""
        for ejercicio, valor in ejercicios_data.items():
            nivel_ej = niveles_ejercicios.get(ejercicio, "No evaluado")
            if isinstance(valor, tuple):
                detalles_rendimiento += f"\n{ejercicio}: {valor[0]} reps × {valor[1]}kg - Nivel: {nivel_ej}"
            else:
                detalles_rendimiento += f"\n{ejercicio}: {valor} {'segundos' if ejercicio == 'Plancha' else 'repeticiones'} - Nivel: {nivel_ej}"
        
        # Etiqueta final que ve el usuario
        etiqueta_final = f"""
RESUMEN FINAL MOSTRADO AL USUARIO:
==================================
📅 Fecha: {fecha_llenado}              💪 % Grasa corporal: {grasa_corregida:.1f}%
👤 Nombre: {nombre}                    📊 FFMI: {ffmi:.2f}
🎂 Edad cronológica: {edad} años       🏆 Nivel muscular: {nivel}
🔥 Edad metabólica: {edad_metabolica} años    🎯 Nivel entrenamiento: {nivel_entrenamiento.capitalize()}
⚖️ Peso: {peso} kg                    📈 Potencial alcanzado: {porc_potencial:.0f}%
📏 Estatura: {estatura} cm             🍽️ Calorías diarias: {ingesta_calorica:.0f} kcal

MENSAJE FINAL AL USUARIO:
{mensaje_edad}

✅ Tu recomendación personalizada considera tu perfil actual, nivel de entrenamiento 
y composición corporal. El ajuste calórico sugerido es {fase}. 
Tu ingesta calórica diaria sugerida es de aproximadamente {ingesta_calorica:.0f} kcal/día.

{advertencias}
"""
        
        # Tabla resumen completa
        tabla_resumen = f"""
EVALUACIÓN MUPAI COMPLETA
========================
Generada: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DATOS DEL CLIENTE:
==================
- Nombre: {nombre}
- Edad: {edad} años
- Edad metabólica: {edad_metabolica} años ({'+' if edad_metabolica > edad else ''}{edad_metabolica - edad} años)
- Teléfono: {telefono}
- Email: {email_cliente}
- Fecha evaluación: {fecha_llenado}

EVALUACIÓN FÍSICA:
==================
- Peso: {peso} kg
- Estatura: {estatura} cm
- IMC: {peso/(estatura/100)**2:.1f} kg/m²
- % Grasa medido: {grasa_corporal}% (método: {metodo_grasa})
- % Grasa (DEXA corregido): {grasa_corregida:.1f}%
- MLG (Masa Libre de Grasa): {mlg:.1f} kg
- TMB (Cunningham): {tmb:.0f} kcal
- FFMI: {ffmi:.2f} ({nivel})
- FFMI máximo estimado: {ffmi_genetico_max:.1f}
- Nivel entrenamiento: {nivel_entrenamiento.capitalize()}
- Potencial genético alcanzado: {porc_potencial:.0f}%
- Experiencia declarada: {experiencia}

PARÁMETROS METABÓLICOS:
=======================
- Nivel de actividad: {nivel_actividad}
- GEAF/PA: {geaf}
- ETA: {eta} ({eta_desc})
- Días de fuerza/semana: {dias_fuerza}
- GEE por sesión: {kcal_sesion} kcal
- GEE promedio/día: {gee_prom_dia:.0f} kcal
- Gasto energético total (GE): {GE:.0f} kcal

PLAN NUTRICIONAL CALCULADO:
===========================
- Fase nutricional: {fase}
- FBEO aplicado: {fbeo:.2f}
- Ingesta calórica final: {ingesta_calorica:.0f} kcal/día
- Proteína: {proteina_g} g/día ({proteina_kcal:.0f} kcal) - {round(proteina_kcal/ingesta_calorica*100, 1)}%
- Grasas: {grasa_g} g/día ({grasa_kcal:.0f} kcal) - {round(grasa_kcal/ingesta_calorica*100, 1)}%
- Carbohidratos: {carbo_g} g/día ({carbo_kcal:.0f} kcal) - {round(carbo_kcal/ingesta_calorica*100, 1)}%

{comparativa_psmf}

{detalles_rendimiento}

ANÁLISIS Y RECOMENDACIONES:
===========================
- Método de medición usado: {metodo_grasa}
- Factor de corrección aplicado: {round(grasa_corregida/grasa_corporal, 2)}x
- Diferencia edad metabólica: {'+' if edad_metabolica > edad else ''}{edad_metabolica - edad} años
- Objetivo principal sugerido: {"Definición" if porcentaje > 0 else "Mantenimiento" if porcentaje == 0 else "Volumen"}

FORTALEZAS Y ÁREAS DE MEJORA:
=============================="""
        
        # Análisis de fortalezas
        fortalezas = []
        mejoras = []
        
        for ejercicio, nivel_ej in niveles_ejercicios.items():
            if nivel_ej in ["Bueno", "Avanzado"]:
                fortalezas.append(f"- {ejercicio}: {nivel_ej}")
            elif nivel_ej == "Bajo":
                mejoras.append(f"- {ejercicio}: {nivel_ej} (priorizar)")
        
        if fortalezas:
            tabla_resumen += "\nFortalezas detectadas:\n" + "\n".join(fortalezas)
        if mejoras:
            tabla_resumen += "\n\nÁreas a mejorar:\n" + "\n".join(mejoras)
        
        tabla_resumen += f"""

NOTAS PARA EL ENTRENADOR:
=========================
- Cliente {"autodidacta" if "D)" in experiencia else "con experiencia estructurada" if "C)" in experiencia else "regular" if "B)" in experiencia else "principiante"}
- Edad metabólica {"elevada" if edad_metabolica > edad + 2 else "normal" if abs(edad_metabolica - edad) <= 2 else "excelente"}
- Candidato PSMF: {"SÍ" if psmf_recs["psmf_aplicable"] else "NO"}
- Fase actual recomendada: {fase}
- Adherencia esperada: {"Alta" if "Tradicional" in str(plan_elegido) if 'plan_elegido' in locals() else "Media"}

{etiqueta_final}

==================================
EVALUACIÓN COMPLETADA CON ÉXITO
Email generado automáticamente por MUPAI
© 2025 Muscle Up Gym & Fitness
==================================
"""
        
        # Enviar email
        try:
            if enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, telefono):
                st.session_state["correo_enviado"] = True
                st.info("📧 Resumen enviado exitosamente a administración")
        except Exception as e:
            st.warning(f"⚠️ No se pudo enviar el email: {str(e)}")

else:
    # Si no hay datos personales completos
    st.warning("⚠️ Por favor completa todos los datos personales para continuar con la evaluación.")
    
    # Mostrar preview del sistema
    st.markdown("""
    <div class="content-card" style="text-align: center; padding: 3rem;">
        <h2>🏋️ Bienvenido al Sistema MUPAI</h2>
        <p style="font-size: 1.2rem; margin: 2rem 0;">
            Completa el formulario de datos personales para iniciar tu evaluación fitness personalizada
        </p>
        <div style="display: flex; justify-content: space-around; margin-top: 2rem;">
            <div>
                <h3>📊</h3>
                <p>Análisis de composición corporal</p>
            </div>
            <div>
                <h3>💪</h3>
                <p>Evaluación de rendimiento</p>
            </div>
            <div>
                <h3>🎯</h3>
                <p>Plan nutricional personalizado</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; opacity: 0.8;">
    <p>© 2025 MUPAI - Muscle Up Gym & Fitness | Desarrollado con ❤️ para transformar vidas</p>
    <p style="font-size: 0.9rem;">Sistema basado en evidencia científica y experiencia profesional</p>
</div>
""", unsafe_allow_html=True)

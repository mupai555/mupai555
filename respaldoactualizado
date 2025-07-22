import streamlit as st
import datetime
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Cuestionario MUPAI", layout="centered")

# ========== ESTILOS CSS INTERNOS ==========
st.markdown(
    """
    <style>
    /* Estilos personalizados MUPAI */
    .stApp {
        background-color: #ffffff;
    }
    
    .titulo-mupai {
        text-align: center;
        font-size: 2.3em;
        font-weight: bold;
        margin-bottom: 0.2em;
        color: #1e3a8a;
    }
    
    .subtitulo-mupai {
        text-align: center;
        font-size: 1.15em;
        color: #444444;
        margin-bottom: 1.3em;
    }
    
    .bloque {
        background-color: #f8f9fa;
        border-radius: 13px;
        padding: 1.2em 1.5em;
        margin-bottom: 1.6em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Personalización de inputs */
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
    }
    
    /* Botones personalizados */
    .stButton > button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1e40af;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Expandir/Colapsar */
    .streamlit-expanderHeader {
        font-weight: bold;
        font-size: 1.1em;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Logo profesional centrado
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.5em;">
        <img src="https://via.placeholder.com/180x60?text=MUPAI" width="180"/>
    </div>
    """,
    unsafe_allow_html=True
)

# Inicializar session state
if "datos_personales_ok" not in st.session_state:
    st.session_state["datos_personales_ok"] = False
if "correo_enviado" not in st.session_state:
    st.session_state["correo_enviado"] = False

# Título y subtítulo
st.markdown(
    """
    <div class="titulo-mupai">Bienvenido a MUPAI - Evaluación Personalizada</div>
    <div class="subtitulo-mupai">Tu experiencia fitness basada en ciencia y profesionalismo</div>
    """, 
    unsafe_allow_html=True
)

# ========== REFERENCIAS FUNCIONALES ==========
referencias_funcionales = {
    "Hombre": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 10), ("Promedio", 20), ("Bueno", 35), ("Avanzado", 50)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 12), ("Bueno", 20), ("Avanzado", 30)]},
        "Press banca": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 40)), ("Promedio", (8, 60)), ("Bueno", (10, 80)), ("Avanzado", (10, 100))]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 15), ("Avanzado", 20)]},
        "Sentadilla": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 60)), ("Promedio", (8, 80)), ("Bueno", (10, 110)), ("Avanzado", (10, 140))]},
        "Peso muerto": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 70)), ("Promedio", (8, 100)), ("Bueno", (10, 130)), ("Avanzado", (10, 180))]},
        "Hip thrust": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 60)), ("Promedio", (8, 90)), ("Bueno", (10, 120)), ("Avanzado", (10, 150))]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 20), ("Promedio", 40), ("Bueno", 60), ("Avanzado", 90)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 5), ("Promedio", 10), ("Bueno", 20), ("Avanzado", 30)]}
    },
    "Mujer": {
        "Flexiones": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]},
        "Fondos": {"tipo": "reps", "niveles": [("Bajo", 1), ("Promedio", 4), ("Bueno", 10), ("Avanzado", 18)]},
        "Press banca": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 15)), ("Promedio", (8, 25)), ("Bueno", (10, 35)), ("Avanzado", (10, 45))]},
        "Dominadas": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 1), ("Bueno", 3), ("Avanzado", 5)]},
        "Remo invertido": {"tipo": "reps", "niveles": [("Bajo", 2), ("Promedio", 5), ("Bueno", 10), ("Avanzado", 15)]},
        "Sentadilla": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 30)), ("Promedio", (8, 50)), ("Bueno", (10, 70)), ("Avanzado", (10, 90))]},
        "Peso muerto": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 30)), ("Promedio", (8, 50)), ("Bueno", (10, 70)), ("Avanzado", (10, 95))]},
        "Hip thrust": {"tipo": "reps_peso", "niveles": [("Bajo", (5, 30)), ("Promedio", (8, 60)), ("Bueno", (10, 90)), ("Avanzado", (10, 120))]},
        "Plancha": {"tipo": "tiempo", "niveles": [("Bajo", 15), ("Promedio", 30), ("Bueno", 50), ("Avanzado", 70)]},
        "Ab wheel": {"tipo": "reps", "niveles": [("Bajo", 0), ("Promedio", 3), ("Bueno", 7), ("Avanzado", 12)]},
        "L-sit": {"tipo": "tiempo", "niveles": [("Bajo", 3), ("Promedio", 8), ("Bueno", 15), ("Avanzado", 25)]}
    }
}

# ========== FUNCIONES AUXILIARES ==========
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
        return {
            "psmf_aplicable": False,
            "proteina_g_dia": 0,
            "calorias_dia": 0,
            "calorias_piso_dia": 0,
            "criterio": "No aplica"
        }

def calcular_edad_metabolica(sexo, tmb):
    if sexo == "Hombre":
        tmb_tabla = {18: 1760, 25: 1710, 35: 1660, 45: 1610, 55: 1560, 65: 1510}
    else:
        tmb_tabla = {18: 1500, 25: 1460, 35: 1420, 45: 1380, 55: 1340, 65: 1300}
    edades = sorted(tmb_tabla.keys())
    if tmb >= tmb_tabla[edades[0]]:
        return edades[0]
    if tmb <= tmb_tabla[edades[-1]]:
        return edades[-1]
    for i in range(len(edades)-1):
        e1, e2 = edades[i], edades[i+1]
        t1, t2 = tmb_tabla[e1], tmb_tabla[e2]
        if t1 >= tmb >= t2:
            edad_metabolica = e1 + (e2-e1)*(t1-tmb)/(t1-t2)
            return int(round(edad_metabolica))
    return edades[-1]

def obtener_geaf(sexo, nivel):
    tabla = {
        "Hombre": {
            "Sedentario": 1.00,
            "Moderadamente activo": 1.11,
            "Activo": 1.25,
            "Muy activo": 1.48,
        },
        "Mujer": {
            "Sedentario": 1.00,
            "Moderadamente activo": 1.12,
            "Activo": 1.27,
            "Muy activo": 1.45,
        }
    }
    return tabla[sexo][nivel]

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

def sugerir_superavit(porcentaje_grasa, sexo, nivel_entrenamiento, ffmi=None):
    if sexo.lower() == "hombre":
        rango_optimo = (9, 15)
        margen_max = 18
        ffmi_max = 24
    elif sexo.lower() == "mujer":
        rango_optimo = (16, 25)
        margen_max = 28
        ffmi_max = 21
    else:
        return None
    if porcentaje_grasa < rango_optimo[0]:
        return None
    if porcentaje_grasa > margen_max:
        return None
    if ffmi is not None and ffmi >= ffmi_max:
        if nivel_entrenamiento.lower() == "novato":
            return 5
        elif nivel_entrenamiento.lower() == "intermedio":
            return 2
        elif nivel_entrenamiento.lower() == "avanzado":
            return 1
        else:
            return None
    if nivel_entrenamiento.lower() == "novato":
        return 10
    elif nivel_entrenamiento.lower() == "intermedio":
        return 5
    elif nivel_entrenamiento.lower() == "avanzado":
        return 2
    else:
        return None

def enviar_email_resumen(tabla_resumen, nombre_cliente, email_cliente, fecha_llenado, edad, otros):
    msg = EmailMessage()
    msg['Subject'] = f'Resumen evaluación MUPAI - {nombre_cliente} ({fecha_llenado})'
    msg['From'] = "administracion@muscleupgym.fitness"
    msg['To'] = "administracion@muscleupgym.fitness"
    msg.set_content(f"""
Nombre completo: {nombre_cliente}
Email cliente: {email_cliente}
Fecha llenado: {fecha_llenado}
Edad: {edad}
---
{tabla_resumen}
---
Otros datos:
{otros}
""")
    smtp_server = "smtp.zoho.eu"
    smtp_port = 465
    smtp_user = "administracion@muscleupgym.fitness"
    smtp_pass = "TU_CONTRASENA_APP"  # CAMBIAR POR LA CONTRASEÑA REAL
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error enviando email: {e}")
        return False

# ========== INTERFAZ PRINCIPAL ==========

# Misión, Visión y Compromiso
with st.expander("Misión, Visión y Compromiso MUPAI", expanded=True):
    st.markdown(
        """
        <div class="bloque">
        <b>Misión:</b> Hacer accesible el entrenamiento basado en ciencia, ofreciendo planes personalizados a través de herramientas digitales y datos confiables, promoviendo tu bienestar integral.<br><br>
        <b>Visión:</b> Ser referente global en entrenamiento digital personalizado, integrando ciencia, tecnología e innovación para transformar tu experiencia fitness.<br><br>
        <b>Política:</b> Nos guiamos por la ética, responsabilidad, transparencia y respeto, asegurando el trato personalizado y la protección de tus datos.
        </div>
        """,
        unsafe_allow_html=True
    )

# Formulario de datos personales
if not st.session_state["datos_personales_ok"]:
    st.markdown("<div class='bloque'><b>Por favor, completa tus datos personales para comenzar:</b></div>", unsafe_allow_html=True)
    
    with st.form(key="form_datos_personales"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("👤 Nombre legal completo*", max_chars=60)
            telefono = st.text_input("📱 Número de teléfono*", max_chars=20)
            edad = st.number_input("🎂 Edad (años)*", min_value=10, max_value=99, step=1, value=25)
        with col2:
            email = st.text_input("📧 Correo electrónico*", max_chars=60)
        
        descargo = st.checkbox(
            "He leído y acepto la política de privacidad y el descargo de responsabilidad.",
            value=False
        )
        submit = st.form_submit_button("Comenzar cuestionario")

        if submit:
            if not (nombre and telefono and email and edad and descargo):
                st.error("⚠️ Debes llenar todos los campos y aceptar el descargo de responsabilidad para continuar.")
            else:
                st.session_state["datos_personales_ok"] = True
                st.session_state["nombre"] = nombre
                st.session_state["telefono"] = telefono
                st.session_state["email"] = email
                st.session_state["edad"] = edad
                st.success("¡Datos personales registrados! Continúa con tu evaluación MUPAI.")
                st.rerun()

# Cuestionario principal
if st.session_state["datos_personales_ok"]:
    nombre = st.session_state["nombre"]
    telefono = st.session_state["telefono"]
    email_cliente = st.session_state["email"]
    edad = st.session_state["edad"]
    fecha_llenado = datetime.datetime.now().strftime("%Y-%m-%d")

    # Variables para almacenar valores
    peso = 70.0
    estatura = 170
    sexo = "Hombre"
    grasa_corporal = 15.0
    ffmi = 20.0
    mlg = 60.0
    tmb = 1666.0
    nivel = "Promedio"
    nivel_entrenamiento = "intermedio"
    geaf = 1.11
    eta = 1.15
    dias_fuerza = 3
    gee_prom_dia = 0
    fase = "Mantenimiento"
    ingesta_calorica = 2000
    ffmi_max = 25

    # BLOQUE 1: DATOS ANTROPOMÉTRICOS
    with st.expander("Paso 1: Datos Antropométricos y Composición Corporal", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            peso = st.number_input("⚖️ Peso corporal (kg)", min_value=30.0, max_value=200.0, step=0.1, value=70.0)
            estatura = st.number_input("📏 Estatura (cm)", min_value=120, max_value=230, step=1, value=170)
            sexo = st.selectbox("Sexo biológico", ["Hombre", "Mujer"])
        with col_b:
            metodo_grasa = st.selectbox(
                "Método utilizado para determinar % de grasa corporal",
                ("Omron HBF-516 (BIA)", "DEXA (Gold Standard)")
            )
            grasa_corporal = st.number_input(
                "% de grasa corporal medido",
                min_value=5.0, max_value=50.0, step=0.1, value=15.0
            )

        if metodo_grasa == "Omron HBF-516 (BIA)":
            grasa_corregida = corregir_grasa_omron_a_dexa(grasa_corporal)
            st.info(f"% de grasa corregido (estimado DEXA): {grasa_corregida:.1f}%")
        else:
            grasa_corregida = grasa_corporal

        # Cálculos de composición corporal
        estatura_m = estatura / 100
        mlg = peso * (1 - grasa_corregida / 100)
        tmb = 370 + 21.6 * mlg
        ffmi = mlg / (estatura_m ** 2)

        st.markdown("<div class='bloque'><b>Resultados de composición corporal:</b></div>", unsafe_allow_html=True)
        st.success(f"**Masa libre de grasa (MLG):** {mlg:.1f} kg")
        st.success(f"**Tasa metabólica basal (TMB, fórmula Cunningham):** {tmb:.0f} kcal")
        st.info(f"**Tu FFMI (Índice de Masa Libre de Grasa):** {ffmi:.2f}")

        # Clasificación FFMI
        if sexo == "Hombre":
            ffmi_max = 25
            if ffmi < 18:
                nivel = "Bajo"
            elif ffmi < 20:
                nivel = "Promedio"
            elif ffmi < 22:
                nivel = "Bueno"
            elif ffmi < 25:
                nivel = "Avanzado"
            else:
                nivel = "Nivel natty max"
            ffmi_mensaje = """**Referencia FFMI natural (hombres):**
- <18: Bajo
- 18-20: Promedio
- 20-22: Bueno
- 22-25: Avanzado
- >25: Nivel "natty max"
"""
        else:
            ffmi_max = 20
            if ffmi < 14:
                nivel = "Bajo"
            elif ffmi < 16:
                nivel = "Promedio"
            elif ffmi < 18:
                nivel = "Bueno"
            elif ffmi < 20:
                nivel = "Avanzado"
            else:
                nivel = "Nivel natty max"
            ffmi_mensaje = """**Referencia FFMI natural (mujeres):**
- <14: Bajo
- 14-16: Promedio
- 16-18: Bueno
- 18-20: Avanzado
- >20: Nivel "natty max"
"""
        st.markdown(ffmi_mensaje)

        # PSMF
        psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
        if psmf_recs["psmf_aplicable"]:
            st.warning(
                f"⚡️ Por tu % de grasa corporal, podrías beneficiarte de una fase rápida PSMF:\n"
                f"- Proteína: {psmf_recs['proteina_g_dia']} g/día\n"
                f"- Calorías: {psmf_recs['calorias_dia']} kcal/día"
            )

        st.success(f"**Tu nivel de desarrollo muscular actual (FFMI):** {nivel}")
        porc_potencial = min(ffmi / ffmi_max * 100, 100)
        st.info(f"Has alcanzado aproximadamente el {porc_potencial:.0f}% del potencial muscular natural estimado.")

    # BLOQUE 2: NIVEL DE ENTRENAMIENTO
    with st.expander("Evaluación Integral de tu Nivel de Entrenamiento", expanded=False):
        st.markdown("Para determinar tu nivel de entrenamiento de forma objetiva, combinamos tu desarrollo muscular (FFMI), tu mejor rendimiento funcional y tu experiencia cualitativa.")
        
        experiencia = st.radio(
            "¿Cuál de estas opciones describe mejor tu experiencia reciente en entrenamiento?",
            [
                "A) Entreno solo ocasionalmente, sin un plan definido ni objetivos claros.",
                "B) Entreno de manera regular (al menos 2 veces por semana), sigo rutinas generales pero no personalizadas.",
                "C) Entreno de forma constante y estructurada, sigo un programa adaptado a mis metas.",
                "D) Además de lo anterior, diseño (o ajusto) mis propios planes de entrenamiento."
            ]
        )

        grupos = [
            ("Empuje superior", ["Flexiones", "Fondos", "Press banca"]),
            ("Tracción superior", ["Dominadas", "Remo invertido"]),
            ("Pierna", ["Sentadilla", "Peso muerto", "Hip thrust"]),
            ("Core", ["Plancha", "Ab wheel", "L-sit"])
        ]
        
        puntajes_funcionales = []
        for grupo, ejercicios in grupos:
            ejercicio = st.selectbox(f"{grupo} - Elige tu mejor ejercicio:", ["Ninguno"] + ejercicios, key=f"ej_{grupo}")
            nivel_ej = "No evaluado"
            puntaje = 1
            
            if ejercicio != "Ninguno" and ejercicio in referencias_funcionales[sexo]:
                tipo = referencias_funcionales[sexo][ejercicio]["tipo"]
                niveles = referencias_funcionales[sexo][ejercicio]["niveles"]
                
                if tipo == "reps":
                    reps = st.number_input(f"Repeticiones máximas en {ejercicio}:", min_value=0, step=1, key=f"reps_{ejercicio}")
                    if reps > 0:
                        for i, (nombre, umbral) in enumerate(niveles):
                            if reps < umbral:
                                nivel_ej = nombre
                                puntaje = i + 1
                                break
                        else:
                            nivel_ej = niveles[-1][0]
                            puntaje = len(niveles)
                    st.info(f"Nivel estimado para {ejercicio}: {nivel_ej}")
                    
                elif tipo == "reps_peso":
                    col1, col2 = st.columns(2)
                    with col1:
                        reps = st.number_input(f"Repeticiones en {ejercicio}:", min_value=0, step=1, key=f"reps_{ejercicio}")
                    with col2:
                        peso_kg = st.number_input(f"Peso (kg) en {ejercicio}:", min_value=0, step=1, key=f"peso_{ejercicio}")
                    if reps > 0 and peso_kg > 0:
                        for i, (nombre, (umbral_reps, umbral_peso)) in enumerate(niveles):
                            if reps < umbral_reps or peso_kg < umbral_peso:
                                nivel_ej = nombre
                                puntaje = i + 1
                                break
                        else:
                            nivel_ej = niveles[-1][0]
                            puntaje = len(niveles)
                    st.info(f"Nivel estimado para {ejercicio}: {nivel_ej}")
                    
                elif tipo == "tiempo":
                    tiempo = st.number_input(f"Tiempo máximo en {ejercicio} (segundos):", min_value=0, step=1, key=f"tiempo_{ejercicio}")
                    if tiempo > 0:
                        for i, (nombre, umbral) in enumerate(niveles):
                            if tiempo < umbral:
                                nivel_ej = nombre
                                puntaje = i + 1
                                break
                        else:
                            nivel_ej = niveles[-1][0]
                            puntaje = len(niveles)
                    st.info(f"Nivel estimado para {ejercicio}: {nivel_ej}")
                    
            puntajes_funcionales.append(puntaje)

        # Calcular nivel de entrenamiento combinado
        mapa_exp = {"A": 1, "B": 2, "C": 3, "D": 4}
        nivel_exp = mapa_exp[experiencia[0]]
        
        if sexo == "Hombre":
            if ffmi < 18:
                nivel_ffmi = 1
            elif ffmi < 20:
                nivel_ffmi = 2
            elif ffmi < 22:
                nivel_ffmi = 3
            elif ffmi < 25:
                nivel_ffmi = 4
            else:
                nivel_ffmi = 5
        else:
            if ffmi < 14:
                nivel_ffmi = 1
            elif ffmi < 16:
                nivel_ffmi = 2
            elif ffmi < 18:
                nivel_ffmi = 3
            elif ffmi < 20:
                nivel_ffmi = 4
            else:
                nivel_ffmi = 5

        nivel_funcional = sum(puntajes_funcionales) / len(puntajes_funcionales) if puntajes_funcionales else 1
        nivel_final = (nivel_ffmi * 0.4) + (nivel_funcional * 0.4) + (nivel_exp * 0.2)
        
        if nivel_final < 1.7:
            nivel_entrenamiento = "novato"
        elif nivel_final < 2.5:
            nivel_entrenamiento = "intermedio"
        else:
            nivel_entrenamiento = "avanzado"

        st.success(f"**Tu nivel de entrenamiento combinado es: {nivel_entrenamiento.capitalize()}**")
        st.info(f"- FFMI: {nivel_ffmi}/5\n- Funcional: {nivel_funcional:.2f}/4\n- Experiencia: {nivel_exp}/4\n- Ponderado: {nivel_final:.2f}/5")

    # BLOQUE 3: ACTIVIDAD FÍSICA
    with st.expander("Paso 2: Nivel de Actividad Física Diaria (GEAF/PA)", expanded=False):
        st.markdown("""
        <div class="bloque">
        <b>¿Cuál de los siguientes enunciados describe mejor tu actividad física diaria (fuera del ejercicio planificado)?</b><br>
        <span style='color:#888; font-size: 0.95em;'>Si tienes dudas, elige la opción más baja. No confundas actividad mental con física.</span>
        <ul>
            <li><b>Sedentario</b>: Trabajo de oficina, estudiante, teletrabajo. Menos de 7,500 pasos/día.</li>
            <li><b>Moderadamente activo</b>: Caminas ocasionalmente, paseas al perro. 7,500–9,999 pasos/día.</li>
            <li><b>Activo</b>: Trabajas de pie la mayoría del tiempo. 10,000–12,500 pasos/día.</li>
            <li><b>Muy activo</b>: Trabajo manual pesado, construcción. Más de 12,500 pasos/día.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        nivel_actividad = st.radio(
            "Selecciona tu nivel de actividad física diaria:",
            ["Sedentario", "Moderadamente activo", "Activo", "Muy activo"]
        )
        
        geaf = obtener_geaf(sexo, nivel_actividad)
        st.info(f"Tu nivel de actividad física diaria es **{nivel_actividad}**. Factor GEAF/PA: **{geaf}**")

    # BLOQUE 4: ETA
    with st.expander("Paso 3: Efecto Térmico de los Alimentos (ETA)", expanded=False):
        st.markdown("""
        <div class="bloque">
        El efecto térmico de los alimentos (ETA) es la energía que tu cuerpo utiliza para digerir y procesar los alimentos. 
        Se calcula automáticamente basado en tu porcentaje de grasa corporal.
        </div>
        """, unsafe_allow_html=True)
        
        if sexo == "Hombre":
            if grasa_corregida <= 15:
                eta = 1.20
                detalle = "ETA alto (magro, ≤ 15% de grasa corporal)"
            elif grasa_corregida <= 20:
                eta = 1.15
                detalle = "ETA intermedio (16–20% de grasa corporal)"
            else:
                eta = 1.10
                detalle = "ETA bajo (más de 20% de grasa corporal)"
        else:
            if grasa_corregida <= 25:
                eta = 1.20
                detalle = "ETA alto (magro, ≤ 25% de grasa corporal)"
            elif grasa_corregida <= 30:
                eta = 1.15
                detalle = "ETA intermedio (26–30% de grasa corporal)"
            else:
                eta = 1.10
                detalle = "ETA bajo (más de 30% de grasa corporal)"
        
        st.info(f"Tu ETA estimado es **{eta}** ({detalle})")

    # BLOQUE 5: ENTRENAMIENTO DE FUERZA
    with st.expander("Paso 4: Entrenamiento de fuerza y gasto energético del ejercicio (GEE)", expanded=False):
        st.markdown("""
        <div class="bloque">
        El gasto energético de tus entrenamientos se estima según tu nivel de desarrollo muscular, 
        no solo por el tiempo reportado. Esto asegura un cálculo más preciso y personalizado.
        </div>
        """, unsafe_allow_html=True)
        
        dias_fuerza = st.number_input(
            "¿Cuántos días por semana entrenas fuerza (pesas, calistenia, funcional)?",
            min_value=0, max_value=7, step=1, value=3
        )
        
        if sexo == "Hombre":
            if ffmi < 20:
                kcal_sesion = 300
                nivel_fuerza = "Bajo/Promedio"
            elif ffmi < 25:
                kcal_sesion = 400
                nivel_fuerza = "Bueno/Avanzado"
            else:
                kcal_sesion = 500
                nivel_fuerza = "Natty max"
        else:
            if ffmi < 16:
                kcal_sesion = 300
                nivel_fuerza = "Bajo/Promedio"
            elif ffmi < 20:
                kcal_sesion = 400
                nivel_fuerza = "Bueno/Avanzado"
            else:
                kcal_sesion = 500
                nivel_fuerza = "Natty max"
        
        gee_total = dias_fuerza * kcal_sesion
        gee_prom_dia = gee_total / 7 if dias_fuerza > 0 else 0
        
        st.info(f"Según tu nivel muscular (**{nivel_fuerza}**), tu gasto es de **{kcal_sesion} kcal/sesión**")
        st.info(f"Gasto semanal: **{gee_total:.0f} kcal** (~{gee_prom_dia:.0f} kcal/día)")

    # BLOQUE 6: CÁLCULO FINAL
    with st.expander("Paso 5: Ingesta Calórica Promedio Total Diaria (Personalizado)", expanded=True):
        st.markdown("""
        <div style='background-color:#f8f9fa; border-radius:14px; padding:1.1em 1.5em; margin-bottom:1.2em;'>
        <b>¿Cómo se determina tu ajuste energético?</b><br>
        Usamos tablas propias para sugerir el déficit o superávit óptimo según tu sexo, 
        nivel de entrenamiento y porcentaje de grasa corporal.
        </div>
        """, unsafe_allow_html=True)

        # Determinar objetivo
        if grasa_corregida > 18:
            objetivo = "deficit"
            porcentaje = sugerir_deficit(grasa_corregida, sexo)
            if porcentaje is None:
                porcentaje = 15
            fbeo = 1 - porcentaje / 100
            fase = f"Déficit recomendado: {porcentaje}%"
        elif grasa_corregida < 10:
            objetivo = "superavit"
            porcentaje = sugerir_superavit(grasa_corregida, sexo, nivel_entrenamiento, ffmi)
            if porcentaje is None:
                porcentaje = 5
            fbeo = 1 + porcentaje / 100
            fase = f"Superávit recomendado: {porcentaje}%"
        else:
            objetivo = "mantenimiento"
            porcentaje = 0
            fbeo = 1.00
            fase = "Mantenimiento"

        st.markdown(f"""
        <div class='bloque'>
        <b>Tu perfil:</b><br>
        <ul>
            <li><b>Sexo:</b> {sexo}</li>
            <li><b>% Grasa corporal (DEXA):</b> {grasa_corregida:.1f}%</li>
            <li><b>FFMI:</b> {ffmi:.2f} ({nivel})</li>
            <li><b>Nivel de entrenamiento:</b> {nivel_entrenamiento.capitalize()}</li>
        </ul>
        <span style='color:#364fc7;'><b>Fase sugerida:</b> {fase}</span>
        </div>
        """, unsafe_allow_html=True)

        # Cálculo calórico
        GE = tmb * geaf * eta + gee_prom_dia
        ingesta_calorica = GE * fbeo
        
        st.markdown("<b>Cálculo:</b> Ingesta calórica = GE x FBEO", unsafe_allow_html=True)
        st.success(f"Tu ingesta calórica diaria recomendada es: **{ingesta_calorica:.0f} kcal/día** ({fase})")

        # Macronutrientes
        proteina_g = round(peso * 1.8, 1)
        proteina_kcal = proteina_g * 4
        grasa_kcal = round(tmb * 0.40, 1)
        grasa_g = round(grasa_kcal / 9, 1)
        carbo_kcal = ingesta_calorica - proteina_kcal - grasa_kcal
        carbo_g = round(carbo_kcal / 4, 1)

        st.markdown("""
        ---
        ### <div style="text-align:center;">Distribución Recomendada de Macronutrientes</div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"**Proteína**\n{proteina_g} g/día\n({proteina_kcal:.0f} kcal)")
        with col2:
            st.info(f"**Grasas**\n{grasa_g} g/día\n({grasa_kcal:.0f} kcal)")
        with col3:
            st.success(f"**Carbohidratos**\n{carbo_g} g/día\n({carbo_kcal:.0f} kcal)")

        # RESUMEN PROFESIONAL
        st.markdown("""
        ---
        ### <div style="text-align:center;">Resumen profesional</div>
        """, unsafe_allow_html=True)
        
        resumen = {
            "Sexo": sexo,
            "Peso": f"{peso} kg",
            "Estatura": f"{estatura} cm",
            "% Grasa (DEXA)": f"{grasa_corregida:.1f}%",
            "FFMI": f"{ffmi:.2f} ({nivel})",
            "Nivel actividad física": nivel_actividad,
            "GEAF/PA": geaf,
            "ETA": eta,
            "Fuerza (días/sem)": dias_fuerza,
            "Kcal fuerza/sem": f"{gee_total} kcal",
            "TMB": f"{tmb:.0f} kcal",
            "GE (total)": f"{GE:.0f} kcal",
            "Balance energético": fase,
            "Ingesta calórica recomendada": f"{ingesta_calorica:.0f} kcal/día",
            "Proteína": f"{proteina_g} g ({proteina_kcal:.0f} kcal)",
            "Grasas": f"{grasa_g} g ({grasa_kcal:.0f} kcal)",
            "Carbohidratos": f"{carbo_g} g ({carbo_kcal:.0f} kcal)"
        }
        st.table(resumen)

    # RESUMEN FINAL Y EDAD METABÓLICA
    st.markdown("---")
    st.header("🎯 Resumen Final de tu Evaluación MUPAI")
    
    edad_metabolica = calcular_edad_metabolica(sexo, tmb)
    
    # Determinar rango de grasa ideal
    if sexo == "Hombre":
        rango_grasa_ok = (4, 12)
    else:
        rango_grasa_ok = (10, 22)
    fuera_rango = not (rango_grasa_ok[0] <= grasa_corregida <= rango_grasa_ok[1])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        **📅 Fecha:** {fecha_llenado}  
        **👤 Nombre:** {nombre}  
        **🎂 Edad cronológica:** {edad} años  
        **🔥 Edad metabólica:** {edad_metabolica} años  
        **⚖️ Peso:** {peso} kg  
        **📏 Estatura:** {estatura} cm
        """)
    with col2:
        st.markdown(f"""
        **💪 % Grasa corporal:** {grasa_corregida:.1f}%  
        **📊 FFMI:** {ffmi:.2f}  
        **🏆 Nivel muscular:** {nivel}  
        **🎯 Nivel entrenamiento:** {nivel_entrenamiento.capitalize()}  
        **📈 Potencial alcanzado:** {porc_potencial:.0f}%  
        **🍽️ Calorías diarias:** {ingesta_calorica:.0f} kcal
        """)
    
    if fuera_rango:
        st.warning(f"⚠️ Para mayor precisión del FFMI, el % de grasa ideal es {rango_grasa_ok[0]}-{rango_grasa_ok[1]}%. Tu valor actual podría afectar la estimación.")
    
    st.info(
        f"✅ Tu recomendación personalizada considera tu perfil actual, nivel de entrenamiento y composición corporal. "
        f"El ajuste calórico sugerido es **{fase}**. "
        f"Tu ingesta calórica diaria sugerida es de aproximadamente **{ingesta_calorica:.0f} kcal/día**."
    )
    
    # Enviar email (solo una vez)
    if not st.session_state.get("correo_enviado", False):
        tabla_resumen = f"""
Datos del cliente:
- Nombre: {nombre}
- Edad: {edad} años
- Edad metabólica: {edad_metabolica} años
- Teléfono: {telefono}
- Email: {email_cliente}

Evaluación física:
- Peso: {peso} kg
- Estatura: {estatura} cm
- % Grasa (DEXA): {grasa_corregida:.1f}%
- MLG: {mlg:.1f} kg
- TMB: {tmb:.0f} kcal
- FFMI: {ffmi:.2f} ({nivel})
- Nivel entrenamiento: {nivel_entrenamiento}
- Potencial alcanzado: {porc_potencial:.0f}%

Plan nutricional:
- Fase: {fase}
- Ingesta calórica: {ingesta_calorica:.0f} kcal/día
- Proteína: {proteina_g} g/día ({proteina_kcal:.0f} kcal)
- Grasas: {grasa_g} g/día ({grasa_kcal:.0f} kcal)  
- Carbohidratos: {carbo_g} g/día ({carbo_kcal:.0f} kcal)

Actividad:
- Nivel actividad: {nivel_actividad}
- Días de fuerza: {dias_fuerza}/semana
- Gasto ejercicio: {gee_prom_dia:.0f} kcal/día
"""
        # Descomentar la siguiente línea para activar el envío de emails
        # enviar_email_resumen(tabla_resumen, nombre, email_cliente, fecha_llenado, edad, f"Tel: {telefono}")
        st.session_state["correo_enviado"] = True
    
    st.success("✅ **Evaluación MUPAI completada con éxito**")
    
    # Botón para reiniciar
    if st.button("🔄 Realizar nueva evaluación"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

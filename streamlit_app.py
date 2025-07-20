import streamlit as st
from psmf_logic import calculate_psmf

st.set_page_config(page_title="Cuestionario MUPAI", layout="centered")

# Logo profesional centrado
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.5em;">
        <img src="Logo_url.png" width="180"/>
    </div>
    """,
    unsafe_allow_html=True
)

# Aplica estilos corporativos
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "datos_personales_ok" not in st.session_state:
    st.session_state["datos_personales_ok"] = False

st.markdown(
    """
    <style>
    .titulo-mupai {text-align:center; font-size:2.3em; font-weight:bold; margin-bottom:0.2em;}
    .subtitulo-mupai {text-align:center; font-size:1.15em; color:#444; margin-bottom:1.3em;}
    .bloque {background-color: #f8f9fa; border-radius: 13px; padding: 1.2em 1.5em 1.1em 1.5em; margin-bottom: 1.6em;}
    </style>
    <div class="titulo-mupai">Bienvenido a MUPAI - Evaluación Personalizada</div>
    <div class="subtitulo-mupai">Tu experiencia fitness basada en ciencia y profesionalismo</div>
    """, unsafe_allow_html=True
)

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

st.markdown("<div class='bloque'><b>Por favor, completa tus datos personales para comenzar:</b></div>", unsafe_allow_html=True)

if not st.session_state["datos_personales_ok"]:
    with st.form(key="form_datos_personales"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("👤 Nombre legal completo*", max_chars=60)
            telefono = st.text_input("📱 Número de teléfono*", max_chars=20)
        with col2:
            email = st.text_input("📧 Correo electrónico*", max_chars=60)
        descargo = st.checkbox(
            "He leído y acepto la política de privacidad y el descargo de responsabilidad.",
            value=False
        )
        submit = st.form_submit_button("Comenzar cuestionario")

    if submit:
        if not (nombre and telefono and email and descargo):
            st.error("⚠️ Debes llenar todos los campos y aceptar el descargo de responsabilidad para continuar.")
        else:
            st.session_state["datos_personales_ok"] = True
            st.success("¡Datos personales registrados! Continúa con tu evaluación MUPAI.")

if st.session_state["datos_personales_ok"]:
    # ====== BLOQUE 1: DATOS ANTROPOMÉTRICOS, % GRASA, SEXO ======
    with st.expander("Paso 1: Datos Antropométricos y Composición Corporal", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            peso = st.number_input("⚖️ Peso corporal (kg)", min_value=30.0, max_value=200.0, step=0.1)
            estatura = st.number_input("📏 Estatura (cm)", min_value=120, max_value=230, step=1)
            sexo = st.selectbox("Sexo biológico", ["Hombre", "Mujer"])
        with col_b:
            metodo_grasa = st.selectbox(
                "Método utilizado para determinar % de grasa corporal",
                ("Omron HBF-516 (BIA)", "DEXA (Gold Standard)")
            )
            grasa_corporal = st.number_input(
                "% de grasa corporal medido",
                min_value=5.0, max_value=50.0, step=0.1
            )

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

        if metodo_grasa == "Omron HBF-516 (BIA)":
            grasa_corregida = corregir_grasa_omron_a_dexa(grasa_corporal)
            st.info(f"% de grasa corregido (estimado DEXA): {grasa_corregida:.1f}%")
        else:
            grasa_corregida = grasa_corporal

        if peso and estatura and grasa_corporal:
            estatura_m = estatura / 100
            mlg = peso * (1 - grasa_corregida / 100)
            tmb = 370 + 21.6 * mlg
            ffmi = mlg / (estatura_m ** 2)

            st.markdown("<div class='bloque'><b>Resultados de composición corporal:</b></div>", unsafe_allow_html=True)
            st.success(f"**Masa libre de grasa (MLG):** {mlg:.1f} kg")
            st.success(f"**Tasa metabólica basal (TMB, fórmula Cunningham):** {tmb:.0f} kcal")
            st.info(f"**Tu FFMI (Índice de Masa Libre de Grasa):** {ffmi:.2f}")

            if sexo == "Hombre":
                ffmi_max = 25
                ffmi_mensaje = """**Referencia FFMI natural (hombres):**
- <18: Bajo
- 18-20: Promedio
- 20-22: Bueno
- 22-25: Avanzado
- >25: Nivel "natty max" (genética top o posible uso de anabólicos)
"""
            else:
                ffmi_max = 20
                ffmi_mensaje = """**Referencia FFMI natural (mujeres):**
- <14: Bajo
- 14-16: Promedio
- 16-18: Bueno
- 18-20: Avanzado
- >20: Nivel "natty max" (genética top o posible uso de anabólicos)
"""
            st.markdown(ffmi_mensaje)

            # INTEGRACIÓN PSMF
            psmf_recs = calculate_psmf(sexo, peso, grasa_corregida, mlg)
            if psmf_recs["psmf_aplicable"]:
                st.warning(
                    f"⚡️ Por tu % de grasa corporal, podrías beneficiarte de una fase rápida PSMF:"
                    f"\n- Proteína: {psmf_recs['proteina_g_dia']} g/día"
                    f"\n- Calorías: {psmf_recs['calorias_dia']} kcal/día"
                    + (f"\n- Piso calórico (si eres muy magro): {psmf_recs['calorias_piso_dia']} kcal/día" if psmf_recs['calorias_piso_dia'] else "")
                    + f"\n- ({psmf_recs['criterio']})"
                )
            # FIN INTEGRACIÓN PSMF

            # Clasificación automática
            if sexo == "Hombre":
                if ffmi < 18:
                    nivel = "Bajo"
                elif ffmi < 20:
                    nivel = "Promedio"
                elif ffmi < 22:
                    nivel = "Bueno"
                elif ffmi < 25:
                    nivel = "Avanzado"
                else:
                    nivel = "Nivel natty max (potencial genético extremo o indicio de uso de anabólicos)"
                grasa_min, grasa_max = 4, 12
            else:
                if ffmi < 14:
                    nivel = "Bajo"
                elif ffmi < 16:
                    nivel = "Promedio"
                elif ffmi < 18:
                    nivel = "Bueno"
                elif ffmi < 20:
                    nivel = "Avanzado"
                else:
                    nivel = "Nivel natty max (potencial genético extremo o indicio de uso de anabólicos)"
                grasa_min, grasa_max = 10, 22

            st.success(f"**Tu nivel de desarrollo muscular actual (FFMI):** {nivel}")

            porc_potencial = min(ffmi / ffmi_max * 100, 100)
            st.info(f"Actualmente has alcanzado aproximadamente el {porc_potencial:.0f}% del potencial muscular natural estimado para tu sexo.")

            if not (grasa_min <= grasa_corregida <= grasa_max):
                st.warning(
                    f"Para estimar con mayor precisión el FFMI, tu porcentaje de grasa debería estar en el rango recomendado: "
                    f"{grasa_min}-{grasa_max}%. El valor mostrado puede sobrestimar tu potencial muscular natural."
                )
        else:
            st.info("Completa todos los campos antropométricos para ver tus resultados.")

    # ====== BLOQUE 2: NIVEL DE ENTRENAMIENTO (FFMI + TESTS + EXPERIENCIA) ======
    with st.expander("Evaluación Integral de tu Nivel de Entrenamiento", expanded=False):
        st.markdown("""
        Para determinar tu nivel de entrenamiento de forma objetiva, combinamos tu desarrollo muscular (FFMI), tu mejor rendimiento funcional y tu experiencia cualitativa.
        """)

        experiencia = st.radio(
            "¿Cuál de estas opciones describe mejor tu experiencia reciente en entrenamiento de fuerza y acondicionamiento físico?",
            [
                "A) Entreno solo ocasionalmente, sin un plan definido ni objetivos claros.",
                "B) Entreno de manera regular (al menos 2 veces por semana), sigo rutinas generales pero no personalizadas, y a veces salto sesiones.",
                "C) Entreno de forma constante y estructurada, sigo un programa adaptado a mis metas, progreso en cargas o dificultad, y registro mis avances.",
                "D) Además de lo anterior, diseño (o ajusto) mis propios planes de entrenamiento, comprendo los principios de progresión y periodización y mantengo la constancia durante todo el año."
            ]
        )

        grupos = [
            ("Empuje superior", ["Flexiones", "Fondos", "Press banca"]),
            ("Tracción superior", ["Dominadas", "Remo invertido"]),
            ("Pierna", ["Sentadilla", "Peso muerto", "Hip thrust"]),
            ("Core", ["Plancha", "Ab wheel", "L-sit"])
        ]

        resultados_tests = []
        for grupo, ejercicios in grupos:
            ejercicio = st.selectbox(f"{grupo} - Elige tu mejor ejercicio:", ["Ninguno"] + ejercicios, key=f"ej_{grupo}")
            marca = st.text_input(f"Marca actual (reps/peso/tiempo) en {ejercicio}:", key=f"marca_{grupo}")
            nivel_test = 2 if marca else 1  # Personaliza esta lógica según tus tablas
            resultados_tests.append(nivel_test)

        # FFMI a nivel numérico
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

        mapa_exp = {"A": 1, "B": 2, "C": 3, "D": 4}
        nivel_exp = mapa_exp[experiencia[0]]
        nivel_tests = sum(resultados_tests) / len(resultados_tests)
        nivel_final = (nivel_ffmi * 0.4) + (nivel_tests * 0.4) + (nivel_exp * 0.2)
        if nivel_final < 1.7:
            nivel_entrenamiento = "novato"
        elif nivel_final < 2.5:
            nivel_entrenamiento = "intermedio"
        else:
            nivel_entrenamiento = "avanzado"
        st.success(f"**Tu nivel de entrenamiento combinado es: {nivel_entrenamiento.capitalize()}**")

    # ====== BLOQUE 3: ACTIVIDAD FÍSICA DIARIA (GEAF/PA) ======
    with st.expander("Paso 2: Nivel de Actividad Física Diaria (GEAF/PA)", expanded=False):
        st.markdown(
            """
            <div class="bloque">
            <b>¿Cuál de los siguientes enunciados describe mejor tu actividad física diaria (fuera del ejercicio planificado)?</b><br>
            <span style='color:#888; font-size: 0.95em;'>Si tienes dudas, elige la opción más baja. No confundas actividad mental con física.</span>
            <ul>
                <li><b>Sedentario</b><br>
                (Trabajo de oficina, estudiante, teletrabajo, o pasas la mayor parte del día sentado. Menos de 7,500 pasos/día.)</li>
                <li><b>Moderadamente activo</b><br>
                (Caminas o te mueves ocasionalmente, paseas al perro, usas bicicleta a veces, trabajas de pie ocasionalmente. 7,500–9,999 pasos/día.)</li>
                <li><b>Activo</b><br>
                (Trabajas de pie la mayoría del tiempo, eres entrenador, docente de deportes, comercio, salud, o acumulas 10,000–12,500 pasos/día.)</li>
                <li><b>Muy activo</b><br>
                (Trabajo manual pesado, construcción, agricultura, repartidor a pie/bicicleta, o más de 12,500 pasos/día con movimiento intenso.)</li>
            </ul>
            </div>
            """, unsafe_allow_html=True
        )
        nivel_actividad = st.radio(
            "Selecciona tu nivel de actividad física diaria:",
            options=[
                "Sedentario",
                "Moderadamente activo",
                "Activo",
                "Muy activo"
            ]
        )
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

        geaf = obtener_geaf(sexo, nivel_actividad)
        st.info(f"Tu nivel de actividad física diaria es **{nivel_actividad}**. Se usará un factor GEAF/PA de **{geaf}** para tus cálculos energéticos.")

    # ====== BLOQUE 4: Efecto Térmico de los Alimentos (ETA) ======
    with st.expander("Paso 3: Efecto Térmico de los Alimentos (ETA)", expanded=False):
        st.markdown(
            """
            <div class="bloque">
            El efecto térmico de los alimentos (ETA) es la energía que tu cuerpo utiliza para digerir y procesar los alimentos. En este cálculo, consideramos que tu dieta será diseñada con alimentos de calidad y mínimo ultraprocesado, por lo que <b>solo dependerá de tu porcentaje de grasa corporal</b>.
            </div>
            """, unsafe_allow_html=True
        )
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

        st.info(f"Tu ETA estimado es **{eta}** ({detalle}). Esto se usará para tus cálculos energéticos.")

    # ====== BLOQUE 5: Entrenamiento de fuerza y gasto energético (GEE) ======
    with st.expander("Paso 4: Entrenamiento de fuerza y gasto energético del ejercicio (GEE)", expanded=False):
        st.markdown(
            """
            <div class="bloque">
            Para mayor precisión, el gasto energético de tus entrenamientos de fuerza se estima según tu nivel de desarrollo muscular, no solo por el tiempo reportado. Esto evita sobreestimaciones frecuentes y asegura un cálculo personalizado.
            </div>
            """, unsafe_allow_html=True
        )
        dias_fuerza = st.number_input(
            "¿Cuántos días por semana entrenas fuerza (pesas, calistenia, funcional intenso, etc.)?", min_value=0, max_value=7, step=1
        )
        # Asignar kcal/sesión según nivel FFMI y sexo
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
        st.info(f"Según tu nivel de desarrollo muscular (**{nivel_fuerza}**), tu gasto energético estimado es de **{kcal_sesion} kcal/sesión**.")
        st.info(f"Gasto energético semanal por fuerza: **{gee_total:.0f} kcal/semana** (~{gee_prom_dia:.0f} kcal/día)")

    # ====== BLOQUE 6: DEFICIT Y SUPERAVIT PERSONALIZADO (UPGRADE VISUAL) ======
    with st.expander("Paso 5: Ingesta Calórica Promedio Total Diaria (Personalizado)", expanded=True):
        st.markdown(
            """
            <div style='background-color:#f8f9fa; border-radius:14px; padding:1.1em 1.5em; margin-bottom:1.2em;'>
            <b>¿Cómo se determina tu ajuste energético?</b><br>
            Usamos tablas propias para sugerir el déficit o superávit óptimo según tu sexo, nivel de entrenamiento y porcentaje de grasa corporal, logrando así una estrategia segura, eficiente y personalizada.
            </div>
            """, unsafe_allow_html=True
        )

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

        st.markdown(
            f"""
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
            """,
            unsafe_allow_html=True
        )

        if peso and estatura and grasa_corporal and dias_fuerza is not None:
            GE = tmb * geaf * eta + gee_prom_dia
            ingesta_calorica = GE * fbeo
            st.markdown("<b>Cálculo:</b> Ingesta calórica promedio total diaria = GE x FBEO", unsafe_allow_html=True)
            st.success(f"Tu ingesta calórica total diaria recomendada es: **{ingesta_calorica:.0f} kcal/día** ({fase})")

            # ========== CÁLCULO PURO DE MACRONUTRIENTES RECOMENDADOS ==========
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
            st.success(f"**Proteína:** {proteina_g} g/día ({proteina_kcal:.0f} kcal)")
            st.info(f"**Grasas:** {grasa_g} g/día ({grasa_kcal:.0f} kcal)")
            st.success(f"**Carbohidratos:** {carbo_g} g/día ({carbo_kcal:.0f} kcal)")

            # ========== RESUMEN PROFESIONAL ==========
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

            st.info(
                f"Tu recomendación personalizada considera tu perfil actual, nivel de entrenamiento y composición corporal. "
                f"El ajuste calórico sugerido es **{fase}**. "
                f"Tu ingesta calórica diaria sugerida es de aproximadamente **{ingesta_calorica:.0f} kcal/día**."
            )

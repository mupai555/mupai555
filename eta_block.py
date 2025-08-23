# BLOQUE 4: ETA (Efecto Térmico de los Alimentos)
with st.expander("🍽️ Paso 4: Efecto Térmico de los Alimentos (ETA)", expanded=True):
    progress.progress(70)
    progress_text.text("Paso 4 de 5: Cálculo del efecto térmico")

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
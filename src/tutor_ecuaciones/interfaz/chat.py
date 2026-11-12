"""Vista del Chat Interactivo con Tutor Pedagógico y Digitalización por Visión."""
from __future__ import annotations

import streamlit as st
from PIL import Image

from tutor_ecuaciones.agente import responder_tutor
from tutor_ecuaciones.explicacion import generar_explicacion_tutor
from tutor_ecuaciones.herramientas import calcular
from tutor_ecuaciones.interfaz.componentes import (
    badge_motor,
    mostrar_detalle_tecnico,
    render_header,
)
from tutor_ecuaciones.motor_local.parser import matriz_a_latex, vector_a_latex
from tutor_ecuaciones.vision import procesar_imagen_ejercicio

EJEMPLOS_RAPIDOS = [
    ("3x3 Única", "Resuelve: 2x + y - z = 8; -3x - y + 2z = -11; -2x + y + 2z = -3"),
    ("Regla de Cramer", "Resuelve por Cramer: 3x + 2y = 7; 4x - y = 2"),
    ("Matriz Inversa", "Calcula la inversa de [[2, 1], [5, 3]]"),
    ("Gauss-Seidel", "Resuelve por Gauss-Seidel: 4x + y + z = 6; x + 5y + 2z = 8; x + 2y + 6z = 9"),
    ("Infinitas Soluciones", "Resuelve: x + y + z = 6; 2x + 2y + 2z = 12"),
    ("Sin Solución", "Resuelve: x + y = 2; x + y = 5"),
]


def render_chat(preferir_ia: bool, api_key_personal: str | None = None):
    """Renderiza la experiencia de chat del tutor."""
    render_header()

    # -------------------------------------------------------------------------
    # PANEL DE DIGITALIZACIÓN DE EJERCICIOS (FOTO / CÁMARA)
    # -------------------------------------------------------------------------
    with st.expander("📸 Subir Foto o Captura de Ejercicio (Digitalización con Visión)", expanded=False):
        st.markdown(
            "Sube una foto manuscrita o captura de pantalla de un sistema de ecuaciones. "
            "El tutor la interpretará y te pedirá **confirmar o corregir los datos antes de resolverla**."
        )

        tab_archivo, tab_camara = st.tabs(["📁 Subir Imagen", "📷 Tomar Foto con Cámara"])
        imagen_cargada = None

        with tab_archivo:
            archivo_subido = st.file_uploader(
                "Seleccione una imagen (JPG, PNG)",
                type=["png", "jpg", "jpeg"],
                key="chat_file_upload",
            )
            if archivo_subido:
                imagen_cargada = Image.open(archivo_subido)

        with tab_camara:
            foto_camara = st.camera_input("Capturar foto del cuaderno", key="chat_camera_input")
            if foto_camara:
                imagen_cargada = Image.open(foto_camara)

        if imagen_cargada is not None:
            st.image(imagen_cargada, caption="Imagen del ejercicio cargada", width=340)

            if st.button("🔍 Leer e Interpretar Ecuaciones", type="primary", key="btn_leer_vision"):
                with st.spinner("Analizando ecuaciones con Visión Multimodal..."):
                    res_vision = procesar_imagen_ejercicio(
                        imagen_cargada,
                        api_key=api_key_personal,
                    )
                    st.session_state["vision_resultado_pendiente"] = res_vision
                    st.session_state["vision_imagen_activa"] = imagen_cargada

    # -------------------------------------------------------------------------
    # TARJETA DE CONFIRMACIÓN INTERACTIVA (Requisito 3.2)
    # -------------------------------------------------------------------------
    res_v = st.session_state.get("vision_resultado_pendiente")
    if res_v:
        st.markdown("---")
        st.markdown("### 📝 Confirmación del Sistema Detectado")
        if res_v.get("ok") and res_v.get("encontrado"):
            st.info(f"**Descripción:** {res_v.get('descripcion')}")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown("**Transcripción en LaTeX:**")
                st.latex(res_v.get("transcripcion_latex", ""))
            with col_v2:
                st.markdown("**Matriz $A$ y Vector $\\mathbf{b}$ extraídos:**")
                if res_v.get("A"):
                    st.latex(f"A = {matriz_a_latex(res_v['A'])}")
                if res_v.get("b"):
                    st.latex(f"\\mathbf{{b}} = {vector_a_latex(res_v['b'])}")

            st.markdown("¿Los datos son correctos? Puedes editarlos o confirmar directamente:")
            metodo_sel = st.selectbox(
                "Método sugerido para resolver:",
                ["resolver-sistema-lineal", "regla-de-cramer", "matriz-inversa", "metodos-iterativos"],
                index=["resolver-sistema-lineal", "regla-de-cramer", "matriz-inversa", "metodos-iterativos"].index(
                    res_v.get("metodo_sugerido", "resolver-sistema-lineal")
                )
                if res_v.get("metodo_sugerido") in ["resolver-sistema-lineal", "regla-de-cramer", "matriz-inversa", "metodos-iterativos"]
                else 0,
                format_func=lambda s: {
                    "resolver-sistema-lineal": "Gauss-Jordan (Exacto)",
                    "regla-de-cramer": "Regla de Cramer (Determinantes)",
                    "matriz-inversa": "Matriz Inversa (A^-1)",
                    "metodos-iterativos": "Métodos Iterativos (Gauss-Seidel)",
                }.get(s, s),
            )

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("✅ Confirmar y Resolver con Explicación", type="primary", key="btn_confirmar_vision"):
                    A_mat = res_v.get("A")
                    b_vec = res_v.get("b")
                    vars_v = res_v.get("variables") or [f"x{i+1}" for i in range(len(A_mat[0]))]

                    # Calcular con la skill seleccionada
                    resultado_calc = calcular(metodo_sel, A_mat, b_vec)
                    explicacion_tutor = generar_explicacion_tutor(
                        skill=metodo_sel,
                        A_raw=A_mat,
                        b_raw=b_vec,
                        variables=vars_v,
                        resultado=resultado_calc,
                    )

                    # Guardar en el historial del chat
                    st.session_state.setdefault("mensajes", []).append({
                        "role": "user",
                        "content": f"📷 [Foto de ejercicio]: {res_v.get('descripcion')}",
                        "imagen": st.session_state.get("vision_imagen_activa"),
                    })
                    st.session_state["mensajes"].append({
                        "role": "assistant",
                        "content": explicacion_tutor,
                        "motor": "gemini" if preferir_ia else "local",
                        "detalles": [{"skill": metodo_sel, "resultado": resultado_calc}],
                    })
                    # Limpiar estado pendiente
                    st.session_state.pop("vision_resultado_pendiente", None)
                    st.session_state.pop("vision_imagen_activa", None)
                    st.rerun()

            with col_btn2:
                if st.button("❌ Descartar y reintentar", key="btn_descartar_vision"):
                    st.session_state.pop("vision_resultado_pendiente", None)
                    st.session_state.pop("vision_imagen_activa", None)
                    st.rerun()

        else:
            st.error(res_v.get("error", "No se detectaron ecuaciones legibles en la imagen."))
            if st.button("Aceptar y cerrar", key="btn_cerrar_error_vision"):
                st.session_state.pop("vision_resultado_pendiente", None)
                st.rerun()
        st.markdown("---")

    # -------------------------------------------------------------------------
    # EJEMPLOS RÁPIDOS
    # -------------------------------------------------------------------------
    st.markdown("##### ⚡ Ejemplos Didácticos Rápidos:")
    cols_ej = st.columns(len(EJEMPLOS_RAPIDOS))
    for idx, (label_ej, prompt_ej) in enumerate(EJEMPLOS_RAPIDOS):
        if cols_ej[idx].button(label_ej, key=f"btn_ej_{idx}"):
            st.session_state["mensaje_pendiente"] = prompt_ej

    st.divider()

    # -------------------------------------------------------------------------
    # HISTORIAL DE MENSAJES DEL CHAT
    # -------------------------------------------------------------------------
    st.session_state.setdefault("mensajes", [])

    if not st.session_state["mensajes"]:
        st.info("👋 Escribe tu ejercicio o pregunta matemática en el recuadro inferior, o elige un ejemplo arriba.")

    for m in st.session_state["mensajes"]:
        with st.chat_message(m["role"]):
            if m.get("motor"):
                badge_motor(m["motor"])
            if m.get("imagen"):
                st.image(m["imagen"], width=300)
            st.markdown(m["content"])
            if m.get("detalles"):
                mostrar_detalle_tecnico(m["detalles"])

    # -------------------------------------------------------------------------
    # ENTRADA DEL CHAT
    # -------------------------------------------------------------------------
    entrada_usuario = st.chat_input("Escribe tu sistema de ecuaciones o consulta conceptual...")
    prompt_procesar = entrada_usuario or st.session_state.pop("mensaje_pendiente", None)

    if prompt_procesar:
        historial_previo = [{"role": m["role"], "content": m["content"]} for m in st.session_state["mensajes"]]
        st.session_state["mensajes"].append({"role": "user", "content": prompt_procesar})

        with st.chat_message("user"):
            st.markdown(prompt_procesar)

        with st.chat_message("assistant"):
            with st.spinner("El tutor está analizando y resolviendo el ejercicio..."):
                resultado_tutor = responder_tutor(
                    prompt_procesar,
                    historial=historial_previo,
                    api_key=api_key_personal,
                    preferir_ia=preferir_ia,
                )

            motor_usado = resultado_tutor.get("motor", "local")
            badge_motor(motor_usado)
            if resultado_tutor.get("aviso"):
                st.warning(resultado_tutor["aviso"])
            st.markdown(resultado_tutor["texto"])
            if resultado_tutor.get("detalles"):
                mostrar_detalle_tecnico(resultado_tutor["detalles"])

            st.session_state["mensajes"].append({
                "role": "assistant",
                "content": resultado_tutor["texto"],
                "motor": motor_usado,
                "detalles": resultado_tutor.get("detalles", []),
            })

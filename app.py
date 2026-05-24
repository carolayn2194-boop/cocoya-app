# =====================================================
# SISTEMA DE PEDIDOS Y ENTREGAS COCOYA
# =====================================================

import streamlit as st

from backups.backup import crear_backup

from styles import cargar_estilos
from auth import login
from modules.pedidos import mostrar_pedidos, mostrar_pedidos_registrados, editar_pedido
from modules.alertas import mostrar_alertas
from modules.reportes import mostrar_reportes
from modules.dashboard import mostrar_dashboard
from modules.pagos import mostrar_pagos
from modules.entregas import mostrar_entregas


st.set_page_config(
    page_title="COCOYA",
    page_icon="assets/logo.png",
    layout="wide"
)

cargar_estilos()


if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "rol" not in st.session_state:
    st.session_state.rol = ""


if st.session_state.login == False:

    login()

else:

    # =================================================
    # SIDEBAR
    # =================================================

    st.sidebar.image(
        "assets/logo.png",
        width=75
    )

    st.sidebar.markdown(
        "<h1 style='margin-top:-10px;'>COCOYA</h1>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        **Usuario:** {st.session_state.usuario}  
        **Rol:** {st.session_state.rol}
        """
    )

    st.sidebar.markdown("---")

    # =================================================
    # MENÚ SEGÚN ROL
    # =================================================

    if st.session_state.rol == "Administrador":

        opciones_menu = [
            "🏠 Dashboard",
            "➕ Nuevo",
            "📋 Pedidos",
            "🧵 Telas",
            "💳 Pagos",
            "🚚 Entregas",
            "🔔 Alertas",
            "📊 Reportes",
            "🚪 Cerrar Sesión"
        ]

    elif st.session_state.rol == "Personal":

        opciones_menu = [
            "📋 Pedidos",
            "🧵 Telas",
            "🚚 Entregas",
            "🔔 Alertas",
            "🚪 Cerrar Sesión"
        ]

    else:

        opciones_menu = [
            "🚪 Cerrar Sesión"
        ]

    menu = st.sidebar.radio(
        "MENÚ PRINCIPAL",
        opciones_menu,
        label_visibility="visible"
    )

    # =================================================
    # DASHBOARD
    # =================================================

    if menu == "🏠 Dashboard":

        if st.session_state.rol == "Administrador":
            mostrar_dashboard()
        else:
            st.error("No tienes permiso para ver esta sección.")

    # =================================================
    # NUEVO PEDIDO
    # =================================================

    elif menu == "➕ Nuevo":

        if st.session_state.rol == "Administrador":
            mostrar_pedidos()
        else:
            st.error("No tienes permiso para crear pedidos.")

    # =================================================
    # PEDIDOS REGISTRADOS
    # =================================================

    elif menu == "📋 Pedidos":

        mostrar_pedidos_registrados()

    # =================================================
    # TELAS PERSONALIZADAS
    # =================================================

    elif menu == "🧵 Telas":

        editar_pedido()

    # =================================================
    # PAGOS
    # =================================================

    elif menu == "💳 Pagos":

        if st.session_state.rol == "Administrador":
            mostrar_pagos()
        else:
            st.error("No tienes permiso para ver pagos.")

    # =================================================
    # ENTREGAS
    # =================================================

    elif menu == "🚚 Entregas":

        mostrar_entregas()

    # =================================================
    # ALERTAS
    # =================================================

    elif menu == "🔔 Alertas":

        mostrar_alertas()

    # =================================================
    # REPORTES
    # =================================================

    elif menu == "📊 Reportes":

        if st.session_state.rol == "Administrador":
            mostrar_reportes()
        else:
            st.error("No tienes permiso para ver reportes.")

    # =================================================
    # CERRAR SESIÓN
    # =================================================

    elif menu == "🚪 Cerrar Sesión":

        st.session_state.clear()
        st.rerun()
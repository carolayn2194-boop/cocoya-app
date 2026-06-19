import streamlit as st
import base64
from pathlib import Path
import streamlit.components.v1 as components


usuarios = {
    "caro": {
        "password": "caro2194",
        "rol": "Administrador"
    },

    "jaki": {
        "password": "202019",
        "rol": "Administrador"
    },

    "erroll": {
        "password": "erroll",
        "rol": "Personal"
    }
}


def convertir_base64(ruta):

    archivo = Path(ruta)

    return base64.b64encode(
        archivo.read_bytes()
    ).decode()


def cerrar_sesion():

    st.session_state.clear()

    st.rerun()


def login():

    if "login" not in st.session_state:
        st.session_state.login = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = ""

    if "rol" not in st.session_state:
        st.session_state.rol = ""

    # Cargar Bootstrap y Font Awesome
    st.markdown(
        """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        """,
        unsafe_allow_html=True
    )

    logo = convertir_base64(
        "assets/logo.png"
    )

    tortugas = convertir_base64(
        "assets/tortuguitas.png"
    )

    col1, col2 = st.columns([1, 1.3])

    with col1:

        components.html(
            f"""
            <div style="
                background: linear-gradient(
                    180deg,
                    #F6BDC1 0%,
                    #F5C7CC 100%
                );
                min-height: 880px;
                padding: 60px 35px;
                border-radius: 0px 28px 28px 0px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
                text-align: center;
                font-family: Arial, sans-serif;
            ">

                <img
                    src="data:image/png;base64,{logo}"
                    style="
                        width:260px;
                        max-width:90%;
                    "
                >

                <div>
                    <h1 style="
                        color:white;
                        font-size:52px;
                        font-weight:800;
                        margin-bottom:20px;
                    ">
                        Bienvenida a Cocoya
                    </h1>

                    <p style="
                        color:white;
                        font-size:21px;
                        line-height:1.8;
                    ">
                        Hecho a mano con amor
                    </p>
                </div>

                <img
                    src="data:image/png;base64,{tortugas}"
                    style="
                        width:340px;
                        max-width:95%;
                    "
                >

            </div>
            """,
            height=920
        )

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        st.title("Iniciar sesión")

        st.write("Ingresa tu usuario y contraseña")

        usuario = st.text_input(
            "Usuario",
            key="usuario_login"
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            key="password_login"
        )

        if st.button("Iniciar sesión"):

            usuario_limpio = usuario.strip().lower()
            password_limpio = password.strip()

            if (
                usuario_limpio in usuarios
                and usuarios[usuario_limpio]["password"] == password_limpio
            ):

                st.session_state.login = True
                st.session_state.usuario = usuario_limpio
                st.session_state.rol = usuarios[usuario_limpio]["rol"]

                st.success("Inicio de sesión correcto")

                st.rerun()

            else:

                st.error("Usuario o contraseña incorrectos")
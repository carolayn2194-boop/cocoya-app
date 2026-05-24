import streamlit as st
import base64
from pathlib import Path


usuarios = {
    "caro_admin": {"password": "cocoya123", "rol": "Administrador"},
    "admin2": {"password": "cocoya2025", "rol": "Administrador"},
    "personal": {"password": "personal123", "rol": "Personal"}
}


def convertir_base64(ruta):
    archivo = Path(ruta)
    return base64.b64encode(archivo.read_bytes()).decode()


def cargar_estilos_login():

    st.markdown(
        """
        <style>
        .login-left {
            background: linear-gradient(180deg, #F6BDC1 0%, #F3AEB8 100%);
            min-height: 100vh;
            padding: 55px 35px;
            border-radius: 0px 28px 28px 0px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            box-shadow: 8px 0px 25px rgba(246, 189, 193, 0.25);
        }

        .login-welcome {
            color: white;
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 18px;
        }

        .login-text {
            color: white;
            font-size: 18px;
            line-height: 1.7;
        }

        .login-right {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 90vh;
            padding: 30px;
        }

        .login-card {
            background-color: white;
            border: 1px solid #F2D6DA;
            border-radius: 28px;
            padding: 45px;
            box-shadow: 0px 14px 35px rgba(246, 189, 193, 0.25);
            width: 100%;
            max-width: 520px;
            text-align: center;
        }

        .login-title {
            font-size: 42px;
            font-weight: 800;
            color: #2F3142;
            margin-bottom: 10px;
        }

        .login-subtitle {
            font-size: 18px;
            color: #7A7A7A;
            margin-bottom: 28px;
        }

        .login-footer {
            margin-top: 25px;
            font-size: 14px;
            color: #A0A0A0;
        }

        .stTextInput input {
            border-radius: 14px !important;
            border: 1px solid #F6BDC1 !important;
            padding: 13px !important;
            color: #2F3142 !important;
        }

        .stTextInput input:focus {
            border-color: #EF8FA0 !important;
            box-shadow: 0px 0px 0px 2px rgba(239, 143, 160, 0.20) !important;
        }

        .stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #EF8FA0 0%, #F6BDC1 100%);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 14px;
            font-size: 17px;
            font-weight: 800;
            margin-top: 12px;
            transition: all 0.2s ease-in-out;
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #E67D91 0%, #F2A6B4 100%);
            color: white;
            transform: translateY(-1px);
            box-shadow: 0px 8px 18px rgba(239, 143, 160, 0.35);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def login():

    cargar_estilos_login()

    logo = convertir_base64("assets/logo.png")
    tortugas = convertir_base64("assets/tortuguitas.png")

    col1, col2 = st.columns([1, 1.45])

    with col1:

        st.markdown(
            f"""
            <div class="login-left">
                <img src="data:image/png;base64,{logo}" style="width:260px; max-width:90%;">

                <div>
                    <div class="login-welcome">
                        Bienvenida a Cocoya
                    </div>

                    <div class="login-text">
                        Inicia sesión para acceder al sistema<br>
                        de pedidos, pagos y entregas.
                    </div>
                </div>

                <img src="data:image/png;base64,{tortugas}" style="width:350px; max-width:95%;">
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="login-right">
                <div class="login-card">
                    <div class="login-title">
                        Iniciar sesión
                    </div>

                    <div class="login-subtitle">
                        Ingresa tu usuario y contraseña
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):

            if usuario.strip() == "" or password.strip() == "":

                st.warning("Completa usuario y contraseña.")

            elif usuario in usuarios and usuarios[usuario]["password"] == password:

                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.rol = usuarios[usuario]["rol"]

                st.rerun()

            else:

                st.error("Usuario o contraseña incorrectos")

        st.markdown(
            """
            <div style="text-align:center; margin-top:25px; color:#A0A0A0; font-size:14px;">
                Sistema interno Cocoya · Gestión de pedidos
            </div>
            """,
            unsafe_allow_html=True
        )
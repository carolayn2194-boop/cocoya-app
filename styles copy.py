import streamlit as st

from backups.backup import crear_backup


def cargar_estilos():

    if "backup_inicial" not in st.session_state:

        crear_backup()

        st.session_state.backup_inicial = True

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #FFFFFF;
        }

        section[data-testid="stSidebar"] {
            background-color: #F6BDC1;
        }

        .block-container {
            padding-top: 0rem;
            padding-left: 0rem;
            padding-right: 2rem;
            max-width: 100%;
        }

        .stButton > button {
            background-color: #F6BDC1;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 26px;
            font-size: 16px;
            font-weight: 700;
        }

        .stButton > button:hover {
            background-color: #F2AAB1;
            color: white;
        }

        div.stMetric {
            background-color: white;
            padding: 18px;
            border-radius: 15px;
            border: 1px solid #F6BDC1;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
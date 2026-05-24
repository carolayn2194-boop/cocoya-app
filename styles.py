import streamlit as st


def cargar_estilos():

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #FFFFFF;
            color: #2F3142;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 100%;
        }

        h1, h2, h3, h4 {
            color: #2F3142;
            font-weight: 800;
        }

        p, span, label {
            color: #2F3142;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #FDF7F2 0%,
                #F6BDC1 100%
            );
            border-radius: 0px 26px 26px 0px;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: #2F3142 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #E99AA6;
        }

        /* MENÚ */
        section[data-testid="stSidebar"] [role="radiogroup"] {
            margin-top: 22px;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label {
            display: flex !important;
            align-items: center !important;
            gap: 14px !important;
            padding: 15px 18px !important;
            margin-bottom: 13px !important;
            border-radius: 16px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            background-color: transparent !important;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label input {
            display: none !important;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label p {
            font-size: 18px !important;
            font-weight: 600 !important;
            margin: 0px !important;
            color: #2F3142 !important;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(
                90deg,
                #EF8FA0 0%,
                #F2A6B4 100%
            ) !important;
            box-shadow: 0px 8px 20px rgba(239, 143, 160, 0.35);
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color: white !important;
        }

        /* LOGIN */
        .left-panel {
            background: linear-gradient(
                180deg,
                #F6BDC1 0%,
                #F5C7CC 100%
            );
            min-height: 100vh;
            border-radius: 0px 24px 24px 0px;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
        }

        .welcome-title {
            color: white;
            font-size: 42px;
            font-weight: 700;
            margin-top: 40px;
        }

        .welcome-text {
            color: white;
            font-size: 19px;
            line-height: 1.8;
            margin-top: 20px;
        }

        .login-container {
            margin-top: 140px;
            padding-left: 50px;
            padding-right: 50px;
        }

        .login-title {
            font-size: 52px;
            font-weight: 800;
            color: #2F3142;
            margin-bottom: 15px;
        }

        .login-subtitle {
            font-size: 18px;
            color: #7A7A7A;
            margin-bottom: 30px;
        }

        /* INPUTS */
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea {
            border-radius: 12px !important;
            border: 1px solid #F6BDC1 !important;
            padding: 12px !important;
            color: #2F3142 !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTextArea textarea:focus {
            border-color: #EF8FA0 !important;
            box-shadow: 0px 0px 0px 2px rgba(239, 143, 160, 0.20) !important;
        }

        div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            border-color: #F6BDC1 !important;
        }

        /* BOTONES */
        .stButton > button {
            width: 100%;
            background-color: #F6BDC1;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-size: 17px;
            font-weight: 700;
            transition: all 0.2s ease-in-out;
        }

        .stButton > button:hover {
            background-color: #F0AAB0;
            color: white;
            transform: translateY(-1px);
            box-shadow: 0px 6px 14px rgba(246, 189, 193, 0.35);
        }

        .stButton > button:active {
            transform: translateY(0px);
        }

        /* MÉTRICAS */
        div.stMetric {
            background-color: white;
            padding: 18px;
            border-radius: 15px;
            border: 1px solid #F6BDC1;
            box-shadow: 0px 4px 12px rgba(246, 189, 193, 0.18);
        }

        div.stMetric label {
            color: #777777 !important;
            font-weight: 600 !important;
        }

        div.stMetric [data-testid="stMetricValue"] {
            color: #2F3142 !important;
            font-weight: 800 !important;
        }

        /* TARJETAS GENERALES */
        .cocoya-card {
            background: #FFFFFF;
            border: 1px solid #F6BDC1;
            border-radius: 22px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25);
        }

        .cocoya-section {
            background: #FFF7F8;
            border-radius: 16px;
            padding: 14px;
            margin-top: 12px;
        }

        .cocoya-title {
            font-size: 25px;
            font-weight: 800;
            color: #333333;
            margin-bottom: 4px;
        }

        .cocoya-subtitle {
            font-size: 18px;
            color: #777777;
            margin-bottom: 18px;
        }

        .cocoya-dato {
            font-size: 16px;
            margin-bottom: 7px;
            color: #333333;
        }

        .cocoya-pill {
            background: #F6BDC1;
            color: white;
            padding: 8px 14px;
            border-radius: 18px;
            font-weight: 700;
            display: inline-block;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        /* ALERTAS DE STREAMLIT */
        div[data-testid="stAlert"] {
            border-radius: 16px !important;
            border: 1px solid #F6BDC1 !important;
        }

        /* TABLAS */
        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid #F6BDC1;
        }

        /* EXPANDERS */
        details {
            border-radius: 16px !important;
            border: 1px solid #F6BDC1 !important;
            background-color: #FFF7F8 !important;
        }

        details summary {
            font-weight: 700 !important;
            color: #2F3142 !important;
        }

        /* DIVIDER */
        hr {
            border: none;
            border-top: 1px solid #F6BDC1;
            margin-top: 24px;
            margin-bottom: 24px;
        }

        /* RESPONSIVE */
        @media screen and (max-width: 768px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .login-container {
                margin-top: 40px;
                padding-left: 20px;
                padding-right: 20px;
            }

            .login-title {
                font-size: 38px;
            }

            .welcome-title {
                font-size: 32px;
            }

            .welcome-text {
                font-size: 16px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )
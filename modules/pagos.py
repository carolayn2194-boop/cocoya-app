import streamlit as st
import pandas as pd

from database.db import Pedido
from database.db import session


def formatear_precio(valor):
    return f"₡{valor:,.0f}"


def cargar_estilos_pagos():

    st.markdown(
        """
        <style>
        .pago-card {
            background: #FFFFFF;
            border: 1px solid #F6BDC1;
            border-radius: 22px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25);
        }

        .pago-titulo {
            font-size: 25px;
            font-weight: 800;
            color: #333333;
            margin-bottom: 4px;
        }

        .pago-subtitulo {
            font-size: 18px;
            color: #777777;
            margin-bottom: 18px;
        }

        .pago-dato {
            font-size: 16px;
            margin-bottom: 7px;
            color: #333333;
        }

        .pago-seccion {
            background: #FFF7F8;
            border-radius: 16px;
            padding: 14px;
            margin-top: 12px;
        }

        .pago-estado {
            background: #F6BDC1;
            color: white;
            padding: 8px 14px;
            border-radius: 18px;
            font-weight: 700;
            display: inline-block;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .pago-alerta {
            background: #E9F8EF;
            color: #2F7D4A;
            padding: 14px;
            border-radius: 16px;
            font-weight: 700;
            margin-bottom: 18px;
            border: 1px solid #BFE8CC;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def estilo_pago(estado):

    if estado == "Pendiente":
        return "🟡 Pendiente"

    elif estado == "Abonado":
        return "💵 Abonado"

    elif estado == "Cancelado":
        return "🟢 Cancelado"

    else:
        return estado


def mostrar_pagos():

    cargar_estilos_pagos()

    st.title("💳 Gestión de Pagos")

    if "pago_actualizado" not in st.session_state:
        st.session_state.pago_actualizado = False

    if st.session_state.pago_actualizado:

        st.markdown(
            """
            <div class="pago-alerta">
                ✅ Pago actualizado correctamente.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.session_state.pago_actualizado = False

    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:

        st.warning("No hay pedidos registrados.")
        return

    opciones = []

    for pedido in pedidos:

        opciones.append(
            f"{pedido.id} - {pedido.cliente} | Saldo: {formatear_precio(pedido.saldo)}"
        )

    seleccion = st.selectbox(
        "Seleccione el pedido",
        opciones
    )

    id_pedido = int(seleccion.split(" - ")[0])

    pedido = session.query(Pedido).filter_by(id=id_pedido).first()

    st.markdown(
        f"""
        <div class="pago-card">
            <div class="pago-titulo">💳 Pedido #{pedido.id}</div>
            <div class="pago-subtitulo">👤 {pedido.cliente}</div>
            <div class="pago-estado">{estilo_pago(pedido.estado_pago)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="pago-seccion">
                <div class="pago-dato">📦 <strong>Producto:</strong> {pedido.producto}</div>
                <div class="pago-dato">💰 <strong>Valor total:</strong> {formatear_precio(pedido.valor_total)}</div>
                <div class="pago-dato">💵 <strong>Total abonado:</strong> {formatear_precio(pedido.abono)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="pago-seccion">
                <div class="pago-dato">💳 <strong>Saldo pendiente:</strong> {formatear_precio(pedido.saldo)}</div>
                <div class="pago-dato">📌 <strong>Estado pago:</strong> {estilo_pago(pedido.estado_pago)}</div>
                <div class="pago-dato">📲 <strong>SINPE:</strong> {pedido.sinpe}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.subheader("Actualizar pago")

    nuevo_abono = st.number_input(
        "Agregar nuevo abono ₡",
        min_value=0.0,
        step=1000.0
    )

    sinpe_verificado = st.selectbox(
        "¿SINPE verificado?",
        ["No", "Sí"]
    )

    if st.button("Actualizar pago"):

        if nuevo_abono <= 0:

            st.error(
                "⚠️ Debes ingresar un monto mayor a ₡0."
            )

            return

        if nuevo_abono > pedido.saldo:

            st.error(
                f"⚠️ El abono supera el saldo pendiente de {formatear_precio(pedido.saldo)}"
            )

            return

        pedido.abono = pedido.abono + nuevo_abono

        pedido.saldo = pedido.valor_total - pedido.abono

        if pedido.saldo <= 0:

            pedido.saldo = 0
            pedido.estado_pago = "Cancelado"

        elif pedido.abono > 0:

            pedido.estado_pago = "Abonado"

        else:

            pedido.estado_pago = "Pendiente"

        pedido.sinpe = sinpe_verificado

        session.commit()

        st.session_state.pago_actualizado = True

        st.rerun()

    st.divider()

    st.subheader("Resumen de pagos")

    datos = []

    for p in pedidos:

        datos.append({

            "Cliente": p.cliente,
            "Producto": p.producto,
            "Valor Total": formatear_precio(p.valor_total),
            "Abonado": formatear_precio(p.abono),
            "Saldo": formatear_precio(p.saldo),
            "Estado Pago": estilo_pago(p.estado_pago),
            "SINPE": p.sinpe

        })

    df = pd.DataFrame(datos)

    st.dataframe(
        df,
        use_container_width=True
    )
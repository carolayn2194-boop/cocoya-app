import streamlit as st
from datetime import date

from database.db import Pedido
from database.db import session


def formatear_fecha(fecha):
    return fecha.strftime("%d-%m-%Y")


def formatear_precio(valor):
    return f"₡{valor:,.0f}"


def cargar_estilos_alertas():

    st.markdown(
        """
        <style>
        .alerta-card {
            background: #FFFFFF;
            border: 1px solid #F6BDC1;
            border-radius: 22px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25);
        }

        .alerta-titulo {
            font-size: 22px;
            font-weight: 800;
            color: #333333;
            margin-bottom: 8px;
        }

        .alerta-dato {
            font-size: 16px;
            color: #333333;
            margin-bottom: 6px;
        }

        .alerta-prioritaria {
            background: #FFF0F0;
            border-left: 8px solid #E57373;
        }

        .alerta-atrasada {
            background: #FFF4E5;
            border-left: 8px solid #F5A623;
        }

        .alerta-proxima {
            background: #FFFBEA;
            border-left: 8px solid #F6C343;
        }

        .alerta-pago {
            background: #F3F0FF;
            border-left: 8px solid #9B7EDE;
        }

        .alerta-ok {
            background: #E9F8EF;
            color: #2F7D4A;
            padding: 16px;
            border-radius: 18px;
            font-weight: 700;
            border: 1px solid #BFE8CC;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def tarjeta_alerta(tipo, titulo, cliente, producto, detalle):

    st.markdown(
        f"""
        <div class="alerta-card {tipo}">
            <div class="alerta-titulo">{titulo}</div>
            <div class="alerta-dato">👤 <strong>Cliente:</strong> {cliente}</div>
            <div class="alerta-dato">📦 <strong>Producto:</strong> {producto}</div>
            <div class="alerta-dato">📌 <strong>Detalle:</strong> {detalle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mostrar_alertas():

    cargar_estilos_alertas()

    st.title("🚨 Alertas ")

    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:
        st.info("No hay pedidos registrados.")
        return

    hoy = date.today()
    hay_alertas = False

    total_prioritarios = 0
    total_atrasados = 0
    total_proximos = 0
    total_pagos = 0

    for pedido in pedidos:

        if pedido.prioridad == "Sí" and pedido.estado != "Entregado":
            total_prioritarios += 1

        if pedido.fecha_entrega < hoy and pedido.estado != "Entregado":
            total_atrasados += 1

        dias_restantes = (pedido.fecha_entrega - hoy).days

        if 0 <= dias_restantes <= 3 and pedido.estado != "Entregado":
            total_proximos += 1

        if pedido.estado_pago != "Cancelado":
            total_pagos += 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🚨 Prioritarios", total_prioritarios)

    with col2:
        st.metric("⏰ Atrasados", total_atrasados)

    with col3:
        st.metric("⚠️ Próximos", total_proximos)

    with col4:
        st.metric("💰 Pagos pendientes", total_pagos)

    st.divider()

    for pedido in pedidos:

        if pedido.prioridad == "Sí" and pedido.estado != "Entregado":

            tarjeta_alerta(
                "alerta-prioritaria",
                "🚨 Pedido prioritario pendiente",
                pedido.cliente,
                pedido.producto,
                f"Este pedido está marcado como prioritario. Fecha de entrega: {formatear_fecha(pedido.fecha_entrega)}"
            )

            hay_alertas = True

        if pedido.fecha_entrega < hoy and pedido.estado != "Entregado":

            tarjeta_alerta(
                "alerta-atrasada",
                "⏰ Pedido atrasado",
                pedido.cliente,
                pedido.producto,
                f"Debía entregarse el {formatear_fecha(pedido.fecha_entrega)}"
            )

            hay_alertas = True

        dias_restantes = (pedido.fecha_entrega - hoy).days

        if 0 <= dias_restantes <= 3 and pedido.estado != "Entregado":

            tarjeta_alerta(
                "alerta-proxima",
                "⚠️ Pedido próximo a entregar",
                pedido.cliente,
                pedido.producto,
                f"Faltan {dias_restantes} días para la entrega. Fecha: {formatear_fecha(pedido.fecha_entrega)}"
            )

            hay_alertas = True

        if pedido.estado_pago != "Cancelado":

            tarjeta_alerta(
                "alerta-pago",
                "💰 Pago pendiente",
                pedido.cliente,
                pedido.producto,
                f"Saldo pendiente: {formatear_precio(pedido.saldo)}"
            )

            hay_alertas = True

    if hay_alertas == False:

        st.markdown(
            """
            <div class="alerta-ok">
                ✅ No hay alertas pendientes.
            </div>
            """,
            unsafe_allow_html=True
        )
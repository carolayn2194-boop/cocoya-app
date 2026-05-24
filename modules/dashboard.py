import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date, timedelta

from database.db import Pedido
from database.db import session


def mostrar_dashboard():

    COLOR_PRINCIPAL = "#F6BDC1"
    COLOR_TEXTO = "#2F3142"

    hoy = date.today()

    inicio_semana = hoy - timedelta(
        days=hoy.weekday()
    )

    fin_semana = inicio_semana + timedelta(
        days=6
    )

    st.markdown(
        f"""
        <h1 style='color:{COLOR_TEXTO};'>
            📊 Dashboard Semanal
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.info(
        f"Mostrando pedidos nuevos de la semana actual "
        f"({inicio_semana.strftime('%d-%m-%Y')} al {fin_semana.strftime('%d-%m-%Y')}) "
        f"y pedidos pendientes de semanas anteriores."
    )

    pedidos = session.query(Pedido).all()

    pedidos_semana = []
    pedidos_pendientes_anteriores = []

    for pedido in pedidos:

        fecha_pedido = pedido.fecha_pedido

        if hasattr(fecha_pedido, "date"):
            fecha_pedido = fecha_pedido.date()

        es_de_semana = (
            inicio_semana <= fecha_pedido <= fin_semana
        )

        sigue_pendiente = pedido.estado in [
            "Pendiente",
            "En proceso",
            "En confección",
            "Tela pendiente",
            "Tela pedida",
            "Tela recibida"
        ]

        if es_de_semana:

            pedidos_semana.append(pedido)

        elif sigue_pendiente:

            pedidos_pendientes_anteriores.append(pedido)

    pedidos_dashboard = (
        pedidos_pendientes_anteriores
        + pedidos_semana
    )

    total_pedidos = len(pedidos_dashboard)

    ventas = 0
    pendientes = 0
    en_proceso = 0
    en_confeccion = 0
    terminados = 0
    prioridad = 0

    nuevos_semana = len(pedidos_semana)

    pendientes_anteriores = len(
        pedidos_pendientes_anteriores
    )

    for pedido in pedidos_dashboard:

        ventas += pedido.valor_total

        if pedido.estado == "Pendiente":
            pendientes += 1

        elif pedido.estado == "En proceso":
            en_proceso += 1

        elif pedido.estado == "En confección":
            en_confeccion += 1

        elif pedido.estado == "Terminado":
            terminados += 1

        if pedido.prioridad == "Sí":
            prioridad += 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 Pedidos visibles", total_pedidos)

    with col2:
        st.metric("🆕 Nuevos semana", nuevos_semana)

    with col3:
        st.metric("⏳ Pendientes anteriores", pendientes_anteriores)

    with col4:
        st.metric("💰 Ventas visibles", f"₡{ventas:,.0f}")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("🟡 Pendientes", pendientes)

    with col6:
        st.metric("🟠 En proceso", en_proceso)

    with col7:
        st.metric("🔵 En confección", en_confeccion)

    with col8:
        st.metric("🟢 Terminados", terminados)

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Estado de pedidos visibles
        </h3>
        """,
        unsafe_allow_html=True
    )

    datos = pd.DataFrame(
        {
            "Estado": [
                "Pendiente",
                "En proceso",
                "En confección",
                "Terminado",
                "Prioritarios"
            ],
            "Cantidad": [
                pendientes,
                en_proceso,
                en_confeccion,
                terminados,
                prioridad
            ]
        }
    )

    fig = px.bar(
        datos,
        x="Estado",
        y="Cantidad",
        text="Cantidad"
    )

    fig.update_traces(
        marker_color=COLOR_PRINCIPAL,
        textposition="outside"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=COLOR_TEXTO,
        showlegend=False,
        xaxis_title="Estado",
        yaxis_title="Cantidad"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            📌 Pedidos pendientes de semanas anteriores
        </h3>
        """,
        unsafe_allow_html=True
    )

    if len(pedidos_pendientes_anteriores) == 0:

        st.success("No hay pedidos pendientes de semanas anteriores.")

    else:

        for pedido in pedidos_pendientes_anteriores:

            st.warning(
                f"#{pedido.id} | {pedido.cliente} - {pedido.producto} | "
                f"Estado: {pedido.estado} | "
                f"Entrega: {pedido.fecha_entrega.strftime('%d-%m-%Y')}"
            )

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            🆕 Pedidos nuevos de esta semana
        </h3>
        """,
        unsafe_allow_html=True
    )

    if len(pedidos_semana) == 0:

        st.info("No hay pedidos nuevos registrados esta semana.")

    else:

        for pedido in pedidos_semana:

            st.success(
                f"#{pedido.id} | {pedido.cliente} - {pedido.producto} | "
                f"Estado: {pedido.estado} | "
                f"Entrega: {pedido.fecha_entrega.strftime('%d-%m-%Y')}"
            )

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            🚨 Pedidos Prioritarios visibles
        </h3>
        """,
        unsafe_allow_html=True
    )

    encontrados = 0

    for pedido in pedidos_dashboard:

        if pedido.prioridad == "Sí":

            st.error(
                f"#{pedido.id} | {pedido.cliente} - {pedido.producto} | "
                f"Estado: {pedido.estado} | "
                f"Entrega: {pedido.fecha_entrega.strftime('%d-%m-%Y')}"
            )

            encontrados += 1

    if encontrados == 0:

        st.success("No hay pedidos prioritarios visibles.")
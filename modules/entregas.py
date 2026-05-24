import streamlit as st
import pandas as pd

from database.db import Pedido
from database.db import session


def mostrar_entregas():

    st.title("🚚 Información de Envíos")

    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:

        st.warning(
            "No hay pedidos registrados"
        )

        return

    st.subheader("Actualizar entrega")

    opciones = []

    for pedido in pedidos:

        opciones.append(
            f"{pedido.id} - {pedido.cliente} | {pedido.producto}"
        )

    seleccion = st.selectbox(
        "Seleccione el pedido",
        opciones
    )

    id_pedido = int(
        seleccion.split(" - ")[0]
    )

    pedido = session.query(Pedido).filter_by(
        id=id_pedido
    ).first()

    st.write(f"Cliente: {pedido.cliente}")

    st.write(f"Producto: {pedido.producto}")

    st.write(f"Provincia: {pedido.provincia}")

    st.write(f"Cantón: {pedido.canton}")

    st.write(f"Distrito: {pedido.distrito}")

    st.write(f"Zona: {pedido.zona}")

    st.write(f"Dirección: {pedido.direccion}")

    st.write(
        f"Fecha entrega: {pedido.fecha_entrega.strftime('%d-%m-%Y')}"
    )

    nuevo_estado = st.selectbox(
        "Estado entrega",
        [
            "Pendiente",
            "Enviado",
            "Entregado"
        ],
        index=[
            "Pendiente",
            "Enviado",
            "Entregado"
        ].index(pedido.estado)
        if pedido.estado in [
            "Pendiente",
            "Enviado",
            "Entregado"
        ]
        else 0
    )

    if st.button("Actualizar entrega"):

        pedido.estado = nuevo_estado

        session.commit()

        st.success(
            "✅ Entrega actualizada correctamente"
        )

        st.rerun()

    st.divider()

    st.subheader("Resumen de Entregas")

    datos = []

    for p in pedidos:

        datos.append({

            "Cliente": p.cliente,
            "Producto": p.producto,
            "Provincia": p.provincia,
            "Cantón": p.canton,
            "Distrito": p.distrito,
            "Zona": p.zona,
            "Dirección": p.direccion,
            "Fecha Entrega": p.fecha_entrega.strftime('%d-%m-%Y'),
            "Estado": p.estado

        })

    df = pd.DataFrame(datos)

    st.dataframe(
        df,
        use_container_width=True
    )
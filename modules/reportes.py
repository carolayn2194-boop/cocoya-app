import streamlit as st
import pandas as pd
import plotly.express as px
import re

from database.db import Pedido
from database.db import session


def formatear_precio(valor):
    return f"₡{valor:,.0f}"


def limpiar_nombre_producto(texto):
    texto = re.sub(r"x\s*\d+", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"₡\s*[\d,]+", "", texto)
    texto = re.sub(r"Subtotal\s*:.*", "", texto, flags=re.IGNORECASE)
    texto = texto.replace(";", "")
    texto = texto.strip()
    return texto


def extraer_productos(producto_texto, valor_total_pedido):

    productos = []

    partes = producto_texto.split(";")

    partes_limpias = []

    for parte in partes:
        if parte.strip() != "":
            partes_limpias.append(parte.strip())

    if len(partes_limpias) == 0:
        partes_limpias.append(producto_texto.strip())

    for parte in partes_limpias:

        cantidad = 1
        precio = 0
        subtotal = 0

        cantidad_encontrada = re.search(r"x\s*(\d+)", parte, flags=re.IGNORECASE)

        if cantidad_encontrada:
            cantidad = int(cantidad_encontrada.group(1))

        precios = re.findall(r"₡\s*([\d,]+)", parte)

        if len(precios) >= 1:
            precio = float(precios[0].replace(",", ""))

        if len(precios) >= 2:
            subtotal = float(precios[1].replace(",", ""))
        else:
            subtotal = precio * cantidad

        nombre = limpiar_nombre_producto(parte)

        if nombre != "":

            productos.append(
                {
                    "Producto": nombre,
                    "Cantidad": cantidad,
                    "Precio": precio,
                    "Subtotal": subtotal
                }
            )

    total_subtotales = 0

    for producto in productos:
        total_subtotales += producto["Subtotal"]

    if total_subtotales == 0 and len(productos) == 1:
        productos[0]["Subtotal"] = valor_total_pedido
        productos[0]["Precio"] = valor_total_pedido / productos[0]["Cantidad"]

    return productos


def cargar_estilos_reportes():

    st.markdown(
        """
        <style>
        .reporte-card {
            background: #FFFFFF;
            border: 1px solid #F6BDC1;
            border-radius: 22px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25);
        }

        .reporte-titulo {
            font-size: 25px;
            font-weight: 800;
            color: #333333;
            margin-bottom: 4px;
        }

        .reporte-subtitulo {
            font-size: 17px;
            color: #777777;
            margin-bottom: 10px;
        }

        .reporte-seccion {
            background: #FFF7F8;
            border-radius: 16px;
            padding: 16px;
            margin-top: 12px;
            margin-bottom: 18px;
        }

        .reporte-dato {
            font-size: 16px;
            color: #333333;
            margin-bottom: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def mostrar_reportes():

    cargar_estilos_reportes()

    COLOR_PRINCIPAL = "#F6BDC1"
    COLOR_SECUNDARIO = "#EF8FA0"
    COLOR_MENTA = "#C1D9C8"
    COLOR_TEXTO = "#2F3142"

    st.markdown(
        f"""
        <h1 style='color:{COLOR_TEXTO};'>
            📈 Reportes de Ventas
        </h1>
        """,
        unsafe_allow_html=True
    )

    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:
        st.warning("No hay datos registrados")
        return

    datos_pedidos = []
    datos_productos = []

    for pedido in pedidos:

        datos_pedidos.append(
            {
                "Cliente": pedido.cliente,
                "Producto": pedido.producto,
                "Provincia": pedido.provincia,
                "Zona": pedido.zona,
                "Valor": pedido.valor_total,
                "Fecha Pedido": pedido.fecha_pedido,
                "Estado Pago": pedido.estado_pago,
                "Estado": pedido.estado
            }
        )

        productos_extraidos = extraer_productos(
            pedido.producto,
            pedido.valor_total
        )

        for item in productos_extraidos:

            datos_productos.append(
                {
                    "Cliente": pedido.cliente,
                    "Producto": item["Producto"],
                    "Cantidad": item["Cantidad"],
                    "Precio": item["Precio"],
                    "Subtotal": item["Subtotal"],
                    "Provincia": pedido.provincia,
                    "Zona": pedido.zona,
                    "Fecha Pedido": pedido.fecha_pedido,
                    "Estado Pago": pedido.estado_pago,
                    "Estado": pedido.estado
                }
            )

    df_pedidos = pd.DataFrame(datos_pedidos)
    df_productos = pd.DataFrame(datos_productos)

    df_pedidos["Fecha Pedido"] = pd.to_datetime(df_pedidos["Fecha Pedido"])
    df_productos["Fecha Pedido"] = pd.to_datetime(df_productos["Fecha Pedido"])

    df_pedidos["Mes"] = df_pedidos["Fecha Pedido"].dt.month
    df_pedidos["Año"] = df_pedidos["Fecha Pedido"].dt.year

    df_productos["Mes"] = df_productos["Fecha Pedido"].dt.month
    df_productos["Año"] = df_productos["Fecha Pedido"].dt.year

    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }

    st.markdown(
        """
        <div class="reporte-card">
            <div class="reporte-titulo">🔍 Filtros del reporte</div>
            <div class="reporte-subtitulo">
                Selecciona el mes y el año que deseas analizar.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:

        año_seleccionado = st.selectbox(
            "Seleccione el año",
            sorted(df_pedidos["Año"].unique(), reverse=True)
        )

    with col_filtro2:

        meses_disponibles = sorted(
            df_pedidos[df_pedidos["Año"] == año_seleccionado]["Mes"].unique()
        )

        mes_numero = st.selectbox(
            "Seleccione el mes",
            meses_disponibles,
            format_func=lambda x: meses[x]
        )

    mes_nombre = meses[mes_numero]

    df_pedidos_mes = df_pedidos[
        (df_pedidos["Año"] == año_seleccionado) &
        (df_pedidos["Mes"] == mes_numero)
    ]

    df_productos_mes = df_productos[
        (df_productos["Año"] == año_seleccionado) &
        (df_productos["Mes"] == mes_numero)
    ]

    if len(df_pedidos_mes) == 0:
        st.warning("No hay ventas registradas para este mes.")
        return

    st.markdown(
        f"""
        <div class="reporte-seccion">
            <div class="reporte-titulo">📅 Reporte de {mes_nombre} {año_seleccionado}</div>
            <div class="reporte-subtitulo">
                Los productos se muestran por separado y solo con su nombre.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    cantidad_pedidos = len(df_pedidos_mes)
    cantidad_productos = df_productos_mes["Cantidad"].sum()
    ventas_totales = df_pedidos_mes["Valor"].sum()
    promedio_pedido = ventas_totales / cantidad_pedidos

    producto_mas_vendido = (
        df_productos_mes
        .groupby("Producto")["Cantidad"]
        .sum()
        .reset_index()
        .sort_values("Cantidad", ascending=False)
        .iloc[0]["Producto"]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 Pedidos", cantidad_pedidos)

    with col2:
        st.metric("🧸 Productos vendidos", int(cantidad_productos))

    with col3:
        st.metric("💰 Ventas totales", formatear_precio(ventas_totales))

    with col4:
        st.metric("🧾 Promedio pedido", formatear_precio(promedio_pedido))

    st.markdown(
        f"""
        <div class="reporte-card">
            <div class="reporte-titulo">🏆 Producto más vendido</div>
            <div class="reporte-dato">{producto_mas_vendido}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Cantidad vendida por producto
        </h3>
        """,
        unsafe_allow_html=True
    )

    cantidad_por_producto = (
        df_productos_mes
        .groupby("Producto")["Cantidad"]
        .sum()
        .reset_index()
        .sort_values("Cantidad", ascending=False)
    )

    fig_cantidad_producto = px.bar(
        cantidad_por_producto,
        x="Producto",
        y="Cantidad",
        text="Cantidad",
        color_discrete_sequence=[COLOR_PRINCIPAL]
    )

    fig_cantidad_producto.update_traces(
        textposition="outside"
    )

    fig_cantidad_producto.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=COLOR_TEXTO,
        xaxis_title="Producto",
        yaxis_title="Cantidad vendida",
        margin=dict(t=40, b=120)
    )

    fig_cantidad_producto.update_xaxes(
        tickangle=-35
    )

    st.plotly_chart(
        fig_cantidad_producto,
        use_container_width=True
    )

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Ventas por producto
        </h3>
        """,
        unsafe_allow_html=True
    )

    ventas_producto = (
        df_productos_mes
        .groupby("Producto")["Subtotal"]
        .sum()
        .reset_index()
        .sort_values("Subtotal", ascending=False)
    )

    ventas_producto = ventas_producto[
        ventas_producto["Subtotal"] > 0
    ]

    fig_producto = px.bar(
        ventas_producto,
        x="Producto",
        y="Subtotal",
        text="Subtotal",
        color_discrete_sequence=[COLOR_SECUNDARIO]
    )

    fig_producto.update_traces(
        texttemplate="₡%{text:,.0f}",
        textposition="outside"
    )

    fig_producto.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=COLOR_TEXTO,
        xaxis_title="Producto",
        yaxis_title="Ventas ₡",
        margin=dict(t=40, b=120)
    )

    fig_producto.update_xaxes(
        tickangle=-35
    )

    st.plotly_chart(
        fig_producto,
        use_container_width=True
    )

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Ventas por provincia
        </h3>
        """,
        unsafe_allow_html=True
    )

    ventas_provincia = (
        df_pedidos_mes
        .groupby("Provincia")["Valor"]
        .sum()
        .reset_index()
        .sort_values("Valor", ascending=False)
    )

    fig_provincia = px.bar(
        ventas_provincia,
        x="Provincia",
        y="Valor",
        text="Valor",
        color_discrete_sequence=[COLOR_MENTA]
    )

    fig_provincia.update_traces(
        texttemplate="₡%{text:,.0f}",
        textposition="outside"
    )

    fig_provincia.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=COLOR_TEXTO,
        xaxis_title="Provincia",
        yaxis_title="Ventas ₡",
        margin=dict(t=40)
    )

    st.plotly_chart(
        fig_provincia,
        use_container_width=True
    )

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Ventas GAM y Resto del País
        </h3>
        """,
        unsafe_allow_html=True
    )

    ventas_zona = (
        df_pedidos_mes
        .groupby("Zona")["Valor"]
        .sum()
        .reset_index()
        .sort_values("Valor", ascending=False)
    )

    fig_zona = px.pie(
        ventas_zona,
        names="Zona",
        values="Valor",
        color_discrete_sequence=[
            COLOR_PRINCIPAL,
            COLOR_MENTA
        ],
        hole=0.35
    )

    fig_zona.update_traces(
        textinfo="label+percent",
        hovertemplate="%{label}<br>Ventas: ₡%{value:,.0f}<extra></extra>"
    )

    fig_zona.update_layout(
        paper_bgcolor="white",
        font_color=COLOR_TEXTO
    )

    st.plotly_chart(
        fig_zona,
        use_container_width=True
    )

    st.divider()

    st.markdown(
        f"""
        <h3 style='color:{COLOR_TEXTO};'>
            Tabla resumen por producto
        </h3>
        """,
        unsafe_allow_html=True
    )

    tabla_productos = df_productos_mes.copy()

    tabla_productos["Fecha Pedido"] = tabla_productos["Fecha Pedido"].dt.strftime("%d-%m-%Y")

    tabla_productos["Precio"] = tabla_productos["Precio"].apply(
        lambda x: formatear_precio(x)
    )

    tabla_productos["Subtotal"] = tabla_productos["Subtotal"].apply(
        lambda x: formatear_precio(x)
    )

    tabla_productos = tabla_productos[
        [
            "Cliente",
            "Producto",
            "Cantidad",
            "Precio",
            "Subtotal",
            "Provincia",
            "Zona",
            "Fecha Pedido",
            "Estado Pago",
            "Estado"
        ]
    ]

    st.dataframe(
        tabla_productos,
        use_container_width=True
    )
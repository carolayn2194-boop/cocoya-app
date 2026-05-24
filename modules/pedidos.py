import streamlit as st
from datetime import timedelta
import os
import uuid

from database.db import Pedido
from database.db import session


def calcular_fecha_entrega(fecha_inicio):

    dias_agregados = 0
    fecha = fecha_inicio

    while dias_agregados < 22:

        fecha += timedelta(days=1)

        if fecha.weekday() != 6:
            dias_agregados += 1

    return fecha


def clasificar_zona(provincia):

    provincias_gam = [
        "San José",
        "Alajuela",
        "Heredia",
        "Cartago"
    ]

    if provincia in provincias_gam:
        return "GAM"

    else:
        return "Resto País"


def pedido_duplicado(cliente, producto, fecha_pedido):

    pedido = session.query(Pedido).filter_by(
        cliente=cliente.strip(),
        producto=producto.strip(),
        fecha_pedido=fecha_pedido
    ).first()

    return pedido is not None


def estilo_estado(estado):

    if estado == "Pendiente":
        return "🟡 Pendiente"

    elif estado == "En proceso":
        return "🟠 En proceso"

    elif estado == "En confección":
        return "🔵 En confección"

    elif estado == "Terminado":
        return "🟢 Terminado"

    elif estado == "Tela pedida":
        return "🧵 Tela pedida"

    elif estado == "Tela recibida":
        return "✅ Tela recibida"

    elif estado == "Tela pendiente":
        return "⏳ Tela pendiente"

    else:
        return estado


def mostrar_pedidos():

    if st.session_state.rol != "Administrador":

        st.error("No tienes permisos para crear pedidos.")
        return

    st.title("📦 Nuevo Pedido")

    st.subheader("Fechas y Prioridad")

    fecha_pedido = st.date_input(
        "Fecha del pedido",
        key="fecha_pedido_registro"
    )

    prioridad = st.selectbox(
        "¿Pedido prioritario?",
        ["No", "Sí"],
        key="prioridad_registro"
    )

    if prioridad == "Sí":

        fecha_entrega = st.date_input(
            "Fecha de entrega prioritaria",
            key="fecha_entrega_prioritaria_registro"
        )

        st.warning(
            f"Pedido prioritario para entregar el: {fecha_entrega.strftime('%d-%m-%Y')}"
        )

    else:

        fecha_entrega = calcular_fecha_entrega(fecha_pedido)

        st.info(
            f"Fecha estimada de entrega: {fecha_entrega.strftime('%d-%m-%Y')}"
        )

    st.divider()

    with st.form("formulario_pedido"):

        st.subheader("Información del Cliente")

        col1, col2 = st.columns(2)

        with col1:

            cliente = st.text_input("Nombre del Cliente")

            telefono = st.text_input("Teléfono")

            identificacion = st.text_input("Identificación (Opcional)")

        with col2:

            producto = st.text_input("Producto")

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                step=1
            )

            valor_total = st.number_input(
                "Valor Total ₡",
                min_value=0.0,
                step=1000.0
            )

        st.divider()

        st.subheader("Telas Personalizadas")

        tela_personalizada = st.selectbox(
            "¿Lleva tela personalizada?",
            ["No", "Sí"]
        )

        imagenes_tela = st.file_uploader(
            "Subir imágenes de tela",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        st.divider()

        st.subheader("Información de Pago")

        abono = st.number_input(
            "Abono Inicial ₡",
            min_value=0.0,
            step=1000.0
        )

        sinpe = st.selectbox(
            "SINPE Verificado",
            ["No", "Sí"]
        )

        saldo = valor_total - abono

        if saldo < 0:
            saldo = 0

        st.write(f"Saldo Pendiente: ₡{saldo:,.0f}")

        st.divider()

        st.subheader("Dirección")

        provincia = st.selectbox(
            "Provincia",
            [
                "San José",
                "Alajuela",
                "Cartago",
                "Heredia",
                "Guanacaste",
                "Puntarenas",
                "Limón"
            ]
        )

        canton = st.text_input("Cantón")

        distrito = st.text_input("Distrito")

        direccion = st.text_area("Dirección Completa")

        zona = clasificar_zona(provincia)

        st.write(f"Zona: {zona}")

        guardar = st.form_submit_button("Guardar Pedido")

        if guardar:

            faltantes = []

            if cliente.strip() == "":
                faltantes.append("Cliente")

            if telefono.strip() == "":
                faltantes.append("Teléfono")

            if producto.strip() == "":
                faltantes.append("Producto")

            if valor_total <= 0:
                faltantes.append("Valor Total")

            if canton.strip() == "":
                faltantes.append("Cantón")

            if distrito.strip() == "":
                faltantes.append("Distrito")

            if direccion.strip() == "":
                faltantes.append("Dirección")

            if len(faltantes) > 0:

                st.error(
                    "⚠️ Faltan campos obligatorios: "
                    + ", ".join(faltantes)
                )

                return

            if pedido_duplicado(cliente, producto, fecha_pedido):

                st.error("⚠️ Este pedido ya existe.")
                return

            estado_pago = "Pendiente"

            if abono > 0:
                estado_pago = "Abonado"

            if saldo == 0:
                estado_pago = "Cancelado"

            rutas_imagenes = []

            if imagenes_tela:

                carpeta = "assets/telas"

                os.makedirs(carpeta, exist_ok=True)

                for imagen in imagenes_tela:

                    extension = imagen.name.split(".")[-1]

                    nombre_archivo = str(uuid.uuid4()) + "." + extension

                    ruta_imagen = os.path.join(carpeta, nombre_archivo)

                    with open(ruta_imagen, "wb") as f:
                        f.write(imagen.getbuffer())

                    rutas_imagenes.append(ruta_imagen)

            rutas_guardadas = ";".join(rutas_imagenes)

            nuevo_pedido = Pedido(
                cliente=cliente,
                telefono=telefono,
                identificacion=identificacion,
                producto=producto,
                cantidad=cantidad,
                valor_total=valor_total,
                abono=abono,
                saldo=saldo,
                estado_pago=estado_pago,
                sinpe=sinpe,
                fecha_pedido=fecha_pedido,
                fecha_entrega=fecha_entrega,
                prioridad=prioridad,
                provincia=provincia,
                canton=canton,
                distrito=distrito,
                zona=zona,
                direccion=direccion,
                estado="Pendiente",
                tela_personalizada=tela_personalizada,
                imagen_tela=rutas_guardadas
            )

            session.add(nuevo_pedido)

            session.commit()

            st.success("✅ Pedido registrado correctamente")


def mostrar_pedidos_registrados():

    st.title("📋 Pedidos Registrados")

    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:

        st.warning("No hay pedidos registrados")
        return

    st.markdown(
        """
        <style>
        .pedido-card {
            background: #FFFFFF;
            border: 1px solid #F6BDC1;
            border-radius: 22px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25);
        }

        .pedido-titulo {
            font-size: 25px;
            font-weight: 800;
            color: #333333;
            margin-bottom: 4px;
        }

        .pedido-subtitulo {
            font-size: 18px;
            color: #777777;
            margin-bottom: 18px;
        }

        .pedido-dato {
            font-size: 16px;
            margin-bottom: 7px;
            color: #333333;
        }

        .pedido-estado {
            background: #F6BDC1;
            color: white;
            padding: 8px 14px;
            border-radius: 18px;
            font-weight: 700;
            display: inline-block;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .pedido-seccion {
            background: #FFF7F8;
            border-radius: 16px;
            padding: 14px;
            margin-top: 12px;
        }

        .pedido-mini {
            font-size: 15px;
            color: #555555;
            margin-bottom: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔍 Buscar pedido")

    col_buscar1, col_buscar2, col_buscar3 = st.columns(3)

    with col_buscar1:

        buscar = st.text_input(
            "Buscar por cliente, teléfono, producto, identificación o lugar",
            key="buscar_pedido"
        )

    with col_buscar2:

        filtro_estado = st.selectbox(
            "Filtrar por estado",
            [
                "Todos",
                "Pendiente",
                "En proceso",
                "En confección",
                "Terminado",
                "Tela pedida",
                "Tela pendiente",
                "Tela recibida"
            ],
            key="filtro_estado_pedido"
        )

    with col_buscar3:

        filtro_tela = st.selectbox(
            "Filtrar por tela personalizada",
            [
                "Todos",
                "Sí",
                "No"
            ],
            key="filtro_tela_pedido"
        )

    pedidos_filtrados = []

    texto_busqueda = buscar.strip().lower()

    for pedido in pedidos:

        coincide_busqueda = True
        coincide_estado = True
        coincide_tela = True

        if texto_busqueda != "":

            datos_pedido = (
                str(pedido.cliente).lower()
                + " "
                + str(pedido.telefono).lower()
                + " "
                + str(pedido.producto).lower()
                + " "
                + str(pedido.identificacion).lower()
                + " "
                + str(pedido.provincia).lower()
                + " "
                + str(pedido.canton).lower()
                + " "
                + str(pedido.distrito).lower()
                + " "
                + str(pedido.direccion).lower()
            )

            if texto_busqueda not in datos_pedido:
                coincide_busqueda = False

        if filtro_estado != "Todos":

            if pedido.estado != filtro_estado:
                coincide_estado = False

        if filtro_tela != "Todos":

            if pedido.tela_personalizada != filtro_tela:
                coincide_tela = False

        if coincide_busqueda and coincide_estado and coincide_tela:

            pedidos_filtrados.append(pedido)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric("📦 Pedidos", len(pedidos_filtrados))

    with col_m2:
        pendientes = len(
            [
                p for p in pedidos_filtrados
                if p.estado == "Pendiente"
            ]
        )
        st.metric("🟡 Pendientes", pendientes)

    with col_m3:
        terminados = len(
            [
                p for p in pedidos_filtrados
                if p.estado == "Terminado"
            ]
        )
        st.metric("🟢 Terminados", terminados)

    with col_m4:
        con_tela = len(
            [
                p for p in pedidos_filtrados
                if p.tela_personalizada == "Sí"
            ]
        )
        st.metric("🧵 Con tela", con_tela)

    st.divider()

    if len(pedidos_filtrados) == 0:

        st.warning("No se encontraron pedidos con esos filtros.")
        return

    for pedido in pedidos_filtrados:

        st.markdown(
            f"""
            <div class="pedido-card">
                <div class="pedido-titulo">📦 Pedido #{pedido.id}</div>
                <div class="pedido-subtitulo">👤 {pedido.cliente} | {pedido.producto}</div>
                <div class="pedido-estado">{estilo_estado(pedido.estado)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([2.2, 1.3, 1.4])

        with col1:

            st.markdown(
                f"""
                <div class="pedido-seccion">
                    <div class="pedido-dato">📞 <strong>Teléfono:</strong> {pedido.telefono}</div>
                    <div class="pedido-dato">🪪 <strong>Identificación:</strong> {pedido.identificacion if pedido.identificacion else "No registrada"}</div>
                    <div class="pedido-dato">📦 <strong>Cantidad:</strong> {pedido.cantidad}</div>
                    <div class="pedido-dato">📅 <strong>Fecha Pedido:</strong> {pedido.fecha_pedido.strftime('%d-%m-%Y')}</div>
                    <div class="pedido-dato">🚚 <strong>Fecha Entrega:</strong> {pedido.fecha_entrega.strftime('%d-%m-%Y')}</div>
                    <div class="pedido-dato">🧵 <strong>Tela personalizada:</strong> {pedido.tela_personalizada}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="pedido-seccion">
                    <div class="pedido-dato">📍 <strong>Provincia:</strong> {pedido.provincia}</div>
                    <div class="pedido-dato">🏠 <strong>Cantón:</strong> {pedido.canton}</div>
                    <div class="pedido-dato">📌 <strong>Distrito:</strong> {pedido.distrito}</div>
                    <div class="pedido-dato">🗺️ <strong>Zona:</strong> {pedido.zona}</div>
                    <div class="pedido-dato">🏡 <strong>Dirección:</strong> {pedido.direccion}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.session_state.rol == "Administrador":

                st.markdown(
                    f"""
                    <div class="pedido-seccion">
                        <div class="pedido-dato">💰 <strong>Valor:</strong> ₡{pedido.valor_total:,.0f}</div>
                        <div class="pedido-dato">💵 <strong>Abono:</strong> ₡{pedido.abono:,.0f}</div>
                        <div class="pedido-dato">💳 <strong>Saldo:</strong> ₡{pedido.saldo:,.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:

            st.markdown("#### 🖼️ Imágenes")

            if pedido.imagen_tela:

                imagenes = pedido.imagen_tela.split(";")

                for imagen in imagenes:

                    if imagen.strip() != "":

                        st.image(
                            imagen,
                            width=220
                        )

            else:

                st.caption("Este pedido no tiene imágenes cargadas.")

        with col3:

            st.markdown("#### ⚙️ Acciones")

            estados = [
                "Pendiente",
                "En proceso",
                "En confección",
                "Terminado"
            ]

            nuevo_estado = st.selectbox(
                "Estado",
                estados,
                index=estados.index(pedido.estado)
                if pedido.estado in estados
                else 0,
                key=f"estado_{pedido.id}"
            )

            if st.button(
                "Guardar Estado",
                key=f"guardar_estado_{pedido.id}"
            ):

                pedido.estado = nuevo_estado

                session.commit()

                st.success("Estado actualizado")

                st.rerun()

            if st.session_state.rol == "Administrador":

                with st.expander("✏️ Actualizar información"):

                    nuevo_telefono = st.text_input(
                        "Teléfono",
                        value=pedido.telefono,
                        key=f"telefono_edit_{pedido.id}"
                    )

                    nueva_identificacion = st.text_input(
                        "Identificación",
                        value=pedido.identificacion if pedido.identificacion else "",
                        key=f"identificacion_edit_{pedido.id}"
                    )

                    nueva_cantidad = st.number_input(
                        "Cantidad",
                        min_value=1,
                        value=pedido.cantidad,
                        step=1,
                        key=f"cantidad_edit_{pedido.id}"
                    )

                    nuevo_valor = st.number_input(
                        "Valor Total ₡",
                        min_value=0.0,
                        value=float(pedido.valor_total),
                        step=1000.0,
                        key=f"valor_edit_{pedido.id}"
                    )

                    nuevo_abono = st.number_input(
                        "Abono ₡",
                        min_value=0.0,
                        value=float(pedido.abono),
                        step=1000.0,
                        key=f"abono_edit_{pedido.id}"
                    )

                    nuevas_imagenes = st.file_uploader(
                        "Agregar más imágenes",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"imagenes_edit_{pedido.id}"
                    )

                    if st.button(
                        "Actualizar información",
                        key=f"actualizar_{pedido.id}"
                    ):
                

                        pedido.telefono = nuevo_telefono
                        pedido.identificacion = nueva_identificacion
                        pedido.cantidad = nueva_cantidad
                        pedido.valor_total = nuevo_valor
                        pedido.abono = nuevo_abono

                        nuevo_saldo = nuevo_valor - nuevo_abono

                        if nuevo_saldo < 0:
                            nuevo_saldo = 0

                        pedido.saldo = nuevo_saldo

                        if nuevas_imagenes:

                            carpeta = "assets/telas"

                            os.makedirs(carpeta, exist_ok=True)

                            rutas_nuevas = []

                            for imagen in nuevas_imagenes:

                                extension = imagen.name.split(".")[-1]

                                nombre_archivo = str(uuid.uuid4()) + "." + extension

                                ruta_imagen = os.path.join(carpeta, nombre_archivo)

                                with open(ruta_imagen, "wb") as f:
                                    f.write(imagen.getbuffer())

                                rutas_nuevas.append(ruta_imagen)

                            if pedido.imagen_tela:

                                pedido.imagen_tela += ";" + ";".join(rutas_nuevas)

                            else:

                                pedido.imagen_tela = ";".join(rutas_nuevas)

                        session.commit()

                        st.success("Información actualizada")

                        st.rerun()

                if st.button(
                    "🗑️ Eliminar Pedido",
                    key=f"eliminar_{pedido.id}"
                ):

                    session.delete(pedido)

                    session.commit()

                    st.success("Pedido eliminado")

                    st.rerun()

        st.divider()


def editar_pedido():

    st.title("🧵 Control de Telas Personalizadas")

    pedidos = session.query(Pedido).filter_by(
        tela_personalizada="Sí"
    ).all()

    if len(pedidos) == 0:

        st.warning("No hay pedidos con telas personalizadas.")
        return

    opciones = []

    for pedido in pedidos:

        opciones.append(
            f"{pedido.id} - {pedido.cliente} | {pedido.producto}"
        )

    seleccion = st.selectbox(
        "Seleccione el pedido",
        opciones
    )

    id_pedido = int(seleccion.split(" - ")[0])

    pedido = session.query(Pedido).filter_by(
        id=id_pedido
    ).first()

    st.subheader("Información de Telas")

    st.write(f"Cliente: {pedido.cliente}")

    st.write(f"Producto: {pedido.producto}")

    if pedido.imagen_tela:

        imagenes = pedido.imagen_tela.split(";")

        for imagen in imagenes:

            if imagen.strip() != "":

                st.image(imagen, width=260)

    st.divider()

    tela_pedida = st.selectbox(
        "¿Ya se pidió la tela?",
        ["No", "Sí"]
    )

    tela_llego = st.selectbox(
        "¿Ya llegó la tela?",
        ["No", "Sí"]
    )

    if st.button("Guardar información de telas"):

        if tela_pedida == "Sí":

            pedido.estado = "Tela pedida"

        else:

            pedido.estado = "Tela pendiente"

        if tela_llego == "Sí":

            pedido.estado = "Tela recibida"

        session.commit()

        st.success("✅ Información actualizada")

        st.rerun()




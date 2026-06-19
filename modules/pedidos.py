import streamlit as st
from datetime import timedelta
import os
import uuid
from sqlalchemy import text  # Importante para la migración automática

# Agrupamos los imports de la base de datos
from database.db import Pedido, session, engine


def verificar_y_actualizar_base_de_datos():
    """
    Esta función verifica si la columna 'descripcion' existe en la tabla 'pedidos'.
    Si no existe, la agrega automáticamente mediante un ALTER TABLE sin borrar datos.
    """
    try:
        with engine.connect() as conn:
            # Consultamos la estructura actual de la tabla pedidos
            # Si estás usando SQLite, PRAGMA es el comando estándar
            result = conn.execute(text("PRAGMA table_info(pedidos);")).fetchall()
            columnas = [row[1] for row in result]
            
            # Si 'descripcion' no está en las columnas, la creamos dinámicamente
            if "descripcion" not in columnas:
                conn.execute(text("ALTER TABLE pedidos ADD COLUMN descripcion TEXT;"))
                conn.commit()
    except Exception as e:
        # Si no es SQLite o falla por otra razón, dejamos que continúe para no congelar la app
        pass

# Ejecutamos la verificación apenas se carga este módulo
verificar_y_actualizar_base_de_datos()


def calcular_fecha_entrega(fecha_inicio):
    dias_agregados = 0
    fecha = fecha_inicio

    while dias_agregados < 22:
        fecha += timedelta(days=1)
        if fecha.weekday() != 6:  # Excluye domingos
            dias_agregados += 1

    return fecha


def clasificar_zona(provincia):
    provincias_gam = ["San José", "Alajuela", "Heredia", "Cartago"]
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
    estilos = {
        "Pendiente": "🟡 Pendiente",
        "En proceso": "🟠 En proceso",
        "En confección": "🔵 En confección",
        "Terminado": "🟢 Terminado",
        "Tela pedida": "🧵 Tela pedida",
        "Tela recibida": "✅ Tela recibida",
        "Tela pendiente": "⏳ Tela pendiente"
    }
    return estilos.get(estado, estado)


def mostrar_pedidos():
    # Evita errores si 'rol' no está inicializado en session_state
    if st.session_state.get("rol") != "Administrador":
        st.error("No tienes permisos para crear pedidos.")
        return

    st.title("📦 Nuevo Pedido")
    st.subheader("Fechas y Prioridad")

    fecha_pedido = st.date_input("Fecha del pedido", key="fecha_pedido_registro")
    prioridad = st.selectbox("¿Pedido prioritario?", ["No", "Sí"], key="prioridad_registro")

    if prioridad == "Sí":
        fecha_entrega = st.date_input("Fecha de entrega prioritaria", key="fecha_entrega_prioritaria_registro")
        st.warning(f"Pedido prioritario para entregar el: {fecha_entrega.strftime('%d-%m-%Y')}")
    else:
        fecha_entrega = calcular_fecha_entrega(fecha_pedido)
        st.info(f"Fecha estimada de entrega: {fecha_entrega.strftime('%d-%m-%Y')}")

    st.divider()

    with st.form("formulario_pedido"):
        st.subheader("Información del Cliente")
        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("Nombre del Cliente")
            telefono = st.text_input("Teléfono")
            identificacion = st.text_input("Identificación (Opcional)")

        with col2:
            cantidad_productos = st.number_input(
                "¿Cuántos productos desea agregar?",
                min_value=1, max_value=10, value=1, step=1
            )

        st.divider()
        st.subheader("Productos del Pedido")

        productos = []
        valor_total = 0
        cantidad_total = 0

        for i in range(cantidad_productos):
            st.markdown(f"### Producto {i + 1}")
            col_prod1, col_prod2, col_prod3 = st.columns(3)

            with col_prod1:
                nombre_producto = st.text_input(f"Nombre del producto {i + 1}", key=f"producto_{i}")
            with col_prod2:
                cantidad_producto = st.number_input(f"Cantidad {i + 1}", min_value=1, step=1, key=f"cantidad_{i}")
            with col_prod3:
                valor_producto = st.number_input(f"Valor unitario producto {i + 1} ₡", min_value=0.0, step=1000.0, key=f"valor_producto_{i}")

            subtotal_producto = cantidad_producto * valor_producto
            productos.append({
                "nombre": nombre_producto,
                "cantidad": cantidad_producto,
                "valor_unitario": valor_producto,
                "subtotal": subtotal_producto
            })

            valor_total += subtotal_producto
            cantidad_total += cantidad_producto
            st.write(f"Subtotal producto {i + 1}: ₡{subtotal_producto:,.0f}")

        st.success(f"Valor total del pedido: ₡{valor_total:,.0f}")
        st.divider()

        st.subheader("Telas Personalizadas")
        tela_personalizada = st.selectbox("¿Lleva tela personalizada?", ["No", "Sí"])
        imagenes_tela = st.file_uploader("Subir imágenes de tela", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        st.divider()
        st.subheader("Información de Pago")
        abono = st.number_input("Abono Inicial ₡", min_value=0.0, step=1000.0)
        sinpe = st.selectbox("SINPE Verificado", ["No", "Sí"])
        
        saldo = max(0.0, valor_total - abono)
        st.write(f"Saldo Pendiente: ₡{saldo:,.0f}")

        st.divider()
        st.subheader("Dirección")
        provincias_lista = ["", "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]
        provincia = st.selectbox("Provincia", provincias_lista)
        canton = st.text_input("Cantón")
        distrito = st.text_input("Distrito")
        direccion = st.text_area("Dirección Completa")

        zona = clasificar_zona(provincia) if provincia.strip() != "" else "Pendiente"
        st.write(f"Zona: {zona}")

        st.divider()
        st.subheader("📝 Detalles Adicionales")
        descripcion = st.text_area("Descripción, especificaciones o notas del pedido", placeholder="Escribe aquí detalles de costura, medidas especiales, etc...")

        # El pedido SOLO se guarda y procesa al presionar este botón formal
        guardar = st.form_submit_button("Guardar Pedido")

        if guardar:
            faltantes = []
            if cliente.strip() == "": faltantes.append("Cliente")
            if telefono.strip() == "": faltantes.append("Teléfono")

            productos_validos = [p for p in productos if p["nombre"].strip() != "" and p["subtotal"] > 0]
            if len(productos_validos) == 0:
                faltantes.append("Debe ingresar al menos un producto con valor")
            if valor_total <= 0:
                faltantes.append("Valor Total")

            if len(faltantes) > 0:
                st.error("⚠️ Faltan campos obligatorios: " + ", ".join(faltantes))
                return

            resumen_productos = [
                f"{p['cantidad']} x {p['nombre']} ₡{p['valor_unitario']:,.0f} c/u = ₡{p['subtotal']:,.0f}"
                for p in productos_validos
            ]
            producto_string = " | ".join(resumen_productos)

            if pedido_duplicado(cliente, producto_string, fecha_pedido):
                st.error("⚠️ Este pedido ya existe.")
                return

            estado_pago = "Cancelado" if saldo == 0 else ("Abonado" if abono > 0 else "Pendiente")

            rutas_imagenes = []
            if imagenes_tela:
                carpeta = "assets/telas"
                os.makedirs(carpeta, exist_ok=True)
                for imagen in imagenes_tela:
                    extension = imagen.name.split(".")[-1]
                    nombre_archivo = f"{uuid.uuid4()}.{extension}"
                    ruta_imagen = os.path.join(carpeta, nombre_archivo)
                    with open(ruta_imagen, "wb") as f:
                        f.write(imagen.getbuffer())
                    rutas_imagenes.append(ruta_imagen)

            nuevo_pedido = Pedido(
                cliente=cliente, telefono=telefono, identificacion=identificacion,
                producto=producto_string, cantidad=cantidad_total, valor_total=valor_total,
                abono=abono, saldo=saldo, estado_pago=estado_pago, sinpe=sinpe,
                fecha_pedido=fecha_pedido, fecha_entrega=fecha_entrega, prioridad=prioridad,
                provincia=provincia, canton=canton, distrito=distrito, zona=zona,
                direccion=direccion, estado="Pendiente", tela_personalizada=tela_personalizada,
                imagen_tela=";".join(rutas_imagenes), descripcion=descripcion
            )

            session.add(nuevo_pedido)
            session.commit()
            st.success("✅ Pedido registrado correctamente")
            st.rerun()


def mostrar_pedidos_registrados():
    st.title("📋 Pedidos Registrados")
    pedidos = session.query(Pedido).all()

    if len(pedidos) == 0:
        st.warning("No hay pedidos registrados")
        return

    st.markdown(
        """
        <style>
        .pedido-card { background: #FFFFFF; border: 1px solid #F6BDC1; border-radius: 22px; padding: 24px; margin-bottom: 24px; box-shadow: 0px 6px 18px rgba(246, 189, 193, 0.25); }
        .pedido-titulo { font-size: 25px; font-weight: 800; color: #333333; margin-bottom: 4px; }
        .pedido-subtitulo { font-size: 18px; color: #777777; margin-bottom: 18px; }
        .pedido-dato { font-size: 16px; margin-bottom: 7px; color: #333333; }
        .pedido-estado { background: #F6BDC1; color: white; padding: 8px 14px; border-radius: 18px; font-weight: 700; display: inline-block; margin-top: 8px; margin-bottom: 8px; }
        .pedido-seccion { background: #FFF7F8; border-radius: 16px; padding: 14px; margin-top: 12px; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔍 Buscar pedido")
    col_buscar1, col_buscar2, col_buscar3 = st.columns(3)

    with col_buscar1:
        buscar = st.text_input("Buscar por cliente, teléfono, producto, identificación o lugar", key="buscar_pedido")
    with col_buscar2:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Pendiente", "En proceso", "En confección", "Terminado", "Tela pedida", "Tela pendiente", "Tela recibida"], key="filtro_estado_pedido")
    with col_buscar3:
        filtro_tela = st.selectbox("Filtrar por tela personalizada", ["Todos", "Sí", "No"], key="filtro_tela_pedido")

    pedidos_filtrados = []
    texto_busqueda = buscar.strip().lower()

    for pedido in pedidos:
        if texto_busqueda != "":
            desc_segura = getattr(pedido, 'descripcion', '') or ''
            datos_pedido = f"{pedido.cliente} {pedido.telefono} {pedido.producto} {pedido.identificacion} {pedido.provincia} {pedido.canton} {pedido.direccion} {desc_segura}".lower()
            if texto_busqueda not in datos_pedido:
                continue
        if filtro_estado != "Todos" and pedido.estado != filtro_estado:
            continue
        if filtro_tela != "Todos" and pedido.tela_personalizada != filtro_tela:
            continue
        pedidos_filtrados.append(pedido)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("📦 Pedidos", len(pedidos_filtrados))
    col_m2.metric("🟡 Pendientes", len([p for p in pedidos_filtrados if p.estado == "Pendiente"]))
    col_m3.metric("🟢 Terminados", len([p for p in pedidos_filtrados if p.estado == "Terminado"]))
    col_m4.metric("🧵 Con tela", len([p for p in pedidos_filtrados if p.tela_personalizada == "Sí"]))

    st.divider()

    if len(pedidos_filtrados) == 0:
        st.warning("No se encontraron pedidos con esos filtros.")
        return

    provincias_lista = ["", "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]

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
                    <div class="pedido-dato">📅 <strong>Fecha Entrega:</strong> {pedido.fecha_entrega.strftime('%d-%m-%Y')}</div>
                    <div class="pedido-dato">📍 <strong>Provincia:</strong> {pedido.provincia or 'Pendiente'}</div>
                    <div class="pedido-dato">🏡 <strong>Dirección:</strong> {pedido.direccion or 'Pendiente'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Sección para renderizar la descripción del pedido si contiene datos
            desc_actual = getattr(pedido, 'descripcion', '')
            if desc_actual:
                st.markdown(
                    f"""
                    <div class="pedido-seccion" style="border-left: 5px solid #F6BDC1;">
                        <strong>📝 Descripción / Notas:</strong><br>
                        <p style="font-style: italic; margin-top: 5px; color: #555555; white-space: pre-wrap;">{desc_actual}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.session_state.get("rol") == "Administrador":
                st.markdown(
                    f"""
                    <div class="pedido-seccion">
                        <div class="pedido-dato">💰 <strong>Valor:</strong> ₡{pedido.valor_total:,.0f} | 💳 <strong>Saldo:</strong> ₡{pedido.saldo:,.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:
            st.markdown("#### 🖼️ Imágenes")
            if pedido.imagen_tela:
                for imagen in pedido.imagen_tela.split(";"):
                    if imagen.strip():
                        st.image(imagen, width=150)
            else:
                st.caption("Sin imágenes.")

        with col3:
            st.markdown("#### ⚙️ Acciones")
            estados = ["Pendiente", "En proceso", "En confección", "Terminado", "Tela pedida", "Tela pendiente", "Tela recibida"]
            
            idx_estado = estados.index(pedido.estado) if pedido.estado in estados else 0
            nuevo_estado = st.selectbox("Estado", estados, index=idx_estado, key=f"estado_{pedido.id}")

            if st.button("Guardar Estado", key=f"guardar_estado_{pedido.id}"):
                pedido.estado = nuevo_estado
                session.commit()
                st.toast("Estado actualizado")
                st.rerun()

            if st.session_state.get("rol") == "Administrador":
                with st.expander("✏️ Actualizar información"):
                    nuevo_telefono = st.text_input("Teléfono", value=pedido.telefono, key=f"telefono_edit_{pedido.id}")
                    nuevo_valor = st.number_input("Valor Total ₡", min_value=0.0, value=float(pedido.valor_total), key=f"valor_edit_{pedido.id}")
                    nuevo_abono = st.number_input("Abono ₡", min_value=0.0, value=float(pedido.abono), key=f"abono_edit_{pedido.id}")
                    
                    idx_prov = provincias_lista.index(pedido.provincia) if pedido.provincia in provincias_lista else 0
                    nueva_provincia = st.selectbox("Provincia", provincias_lista, index=idx_prov, key=f"provincia_edit_{pedido.id}")
                    
                    # Campo para poder editar las notas guardadas del pedido
                    nueva_descripcion = st.text_area("Editar Descripción", value=desc_actual or "", key=f"desc_edit_{pedido.id}")

                    if st.button("Actualizar información", key=f"actualizar_{pedido.id}"):
                        pedido.telefono = nuevo_telefono
                        pedido.valor_total = nuevo_valor
                        pedido.abono = nuevo_abono
                        pedido.provincia = nueva_provincia
                        pedido.descripcion = nueva_descripcion
                        pedido.saldo = max(0.0, nuevo_valor - nuevo_abono)
                        pedido.zona = clasificar_zona(nueva_provincia) if nueva_provincia else "Pendiente"
                        
                        session.commit()
                        st.rerun()

                if st.button("🗑️ Eliminar Pedido", key=f"eliminar_{pedido.id}"):
                    session.delete(pedido)
                    session.commit()
                    st.rerun()
        st.divider()


def editar_pedido():
    st.title("🧵 Control de Telas Personalizadas")
    pedidos = session.query(Pedido).filter_by(tela_personalizada="Sí").all()

    if len(pedidos) == 0:
        st.warning("No hay pedidos con telas personalizadas.")
        return

    opciones = [f"{p.id} - {p.cliente} | {p.producto}" for p in pedidos]
    seleccion = st.selectbox("Seleccione el pedido", opciones)
    id_pedido = int(seleccion.split(" - ")[0])

    pedido = session.query(Pedido).filter_by(id=id_pedido).first()

    st.subheader("Información de Telas")
    st.write(f"Cliente: {pedido.cliente}")
    st.write(f"Producto: {pedido.producto}")

    if pedido.imagen_tela:
        for imagen in pedido.imagen_tela.split(";"):
            if imagen.strip():
                st.image(imagen, width=200)

    st.divider()

    default_pedida = "Sí" if pedido.estado in ["Tela pedida", "Tela recibida"] else "No"
    default_llego = "Sí" if pedido.estado == "Tela recibida" else "No"

    tela_pedida = st.selectbox("¿Ya se pidió la tela?", ["No", "Sí"], index=["No", "Sí"].index(default_pedida))
    tela_llego = st.selectbox("¿Ya llegó la tela?", ["No", "Sí"], index=["No", "Sí"].index(default_llego))

    if st.button("Guardar información de telas"):
        if tela_llego == "Sí":
            pedido.estado = "Tela recibida"
        elif tela_pedida == "Sí":
            pedido.estado = "Tela pedida"
        else:
            pedido.estado = "Tela pendiente"

        session.commit()
        st.success("✅ Información de telas actualizada de forma segura")
        st.rerun()
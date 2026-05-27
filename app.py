# == Importación de librerias ==

import streamlit as st
import pandas as pd

# == Configuración de la página de la interfaz ==
st.set_page_config(
    page_title="Portal Sally Consultory",
    layout="wide"
)

# == Carga de datos CSV para convertirlos en DataFrames ==
df = pd.read_csv("fact_tareas_gestoria.csv")
df_facturacion = pd.read_csv("fact_facturacion_gestoria.csv")
df_clientes = pd.read_csv("dim_clientes_gestoria.csv")
df_empleados = pd.read_csv("dim_empleados_gestoria.csv")
df_servicios = pd.read_csv("dim_servicios_gestoria.csv")

# == Ordenar los clientes por ID ==
df_clientes = df_clientes.sort_values("dim_id_cliente")

# == Crear una label cliente ==
df_clientes["cliente_display"] = (
    df_clientes["dim_id_cliente"].astype(str)
    + " - "
    + df_clientes["dim_nombre_empresa"]
)

# == Reemplazar el ID del empleado por el nombre ==
df = df.merge(
    df_empleados[["dim_id_empleado", "dim_nombre"]],
    left_on="fact_id_empleado",
    right_on="dim_id_empleado",
    how="left"
)

# == Reemplazar el ID del servicio por el nombre ==
df = df.merge(
    df_servicios[["dim_id_servicio", "dim_nombre_servicio"]],
    left_on="fact_id_servicio",
    right_on="dim_id_servicio",
    how="left"
)

# == Establecer la estructura de la páginas usando columnas ==

col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    st.title("Portal Sally Consultory")

    # == Añadir selector del cliente ==
    st.subheader("Clientes")

    cliente_seleccionado = st.selectbox(
        "Selecciona cliente",
        df_clientes["cliente_display"]
    )

    cliente = int(cliente_seleccionado.split(" - ")[0])

    # == Filtros de clientes ==
    df_filtrado = df[df["fact_id_cliente"] == cliente]

    df_facturacion_filtrada = df_facturacion[
        df_facturacion["fact_id_cliente"] == cliente
    ]

    # == Definir el formato de los importes ==
    df_facturacion_filtrada["fact_importe_facturado"] = (
        df_facturacion_filtrada["fact_importe_facturado"]
        .map("{:,.2f} €".format)
    )

    # == Ordenar facturas por fecha de vencimiento == 
    df_facturacion_filtrada = df_facturacion_filtrada.sort_values(
        "fact_fecha_vencimiento"
    )

    # == Crear pestañas ==
    tab1, tab2 = st.tabs(["Gestión de tareas", "Gestión financiera"])

 
    # == Pestaña 1 - tareas ==

    with tab1:

        st.subheader("Resumen de tareas")

        total_tareas = len(df_filtrado)

        completadas = len(df_filtrado[df_filtrado["fact_estado"] == "completado"])
        retrasadas = len(df_filtrado[df_filtrado["fact_estado"] == "retrasado"])
        en_progreso = len(df_filtrado[df_filtrado["fact_estado"] == "en progreso"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total tareas", total_tareas)
        col2.metric("🟢 Completadas", completadas)
        col3.metric("🔴 Retrasadas", retrasadas)
        col4.metric("🟡 En progreso", en_progreso)

        st.divider()

        st.subheader("Detalle de tareas")

        st.dataframe(
            df_filtrado[
                [
                    "fact_id_tarea",
                    "dim_nombre",
                    "dim_nombre_servicio",
                    "fact_fecha_inicio",
                    "fact_fecha_fin",
                    "fact_estado",
                    "fact_prioridad",
                    "fact_horas_dedicadas"
                ]
            ].rename(
                columns={
                    "fact_id_tarea": "ID tarea",
                    "dim_nombre": "Empleado",
                    "dim_nombre_servicio": "Servicio",
                    "fact_fecha_inicio": "Fecha inicio",
                    "fact_fecha_fin": "Fecha fin",
                    "fact_estado": "Estado",
                    "fact_prioridad": "Prioridad",
                    "fact_horas_dedicadas": "Horas dedicadas"
                }
            ),
            hide_index=True,
            use_container_width=True
        )

    # == Pestaña 2 - facturación ==
    
    with tab2:

        st.subheader("Resumen financiero")

        total_facturado = (
            df_facturacion_filtrada["fact_importe_facturado"]
            .replace("[€,]", "", regex=True)
            .astype(float)
            .sum()
        )

        facturas_pagadas = len(df_facturacion_filtrada[df_facturacion_filtrada["fact_estado_pago"] == "pagado"])
        facturas_pendientes = len(df_facturacion_filtrada[df_facturacion_filtrada["fact_estado_pago"] == "pendiente"])
        facturas_vencidas = len(df_facturacion_filtrada[df_facturacion_filtrada["fact_estado_pago"] == "vencido"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total facturado", f"{total_facturado:,.2f} €")
        col2.metric("🟢 Pagadas", facturas_pagadas)
        col3.metric("🟡 Pendientes", facturas_pendientes)
        col4.metric("🔴 Vencidas", facturas_vencidas)

        st.divider()

        facturas_vencidas_df = df_facturacion_filtrada[
            df_facturacion_filtrada["fact_estado_pago"] == "vencido"
        ]

        if facturas_vencidas == 0:
            st.success("Cliente sin incidencias de pago")
        elif facturas_vencidas <= 2:
            st.warning("Cliente con riesgo moderado de impago")
        else:
            st.error("Cliente con riesgo alto de impago")

        if len(facturas_vencidas_df) > 0:

            st.error(f"El cliente tiene {len(facturas_vencidas_df)} facturas vencidas")

            st.subheader("Facturas vencidas")

            st.dataframe(
                facturas_vencidas_df[
                    [
                        "fact_numero_factura",
                        "fact_fecha_factura",
                        "fact_fecha_vencimiento",
                        "fact_importe_facturado",
                        "fact_estado_pago"
                    ]
                ].rename(
                    columns={
                        "fact_numero_factura": "Número factura",
                        "fact_fecha_factura": "Fecha factura",
                        "fact_fecha_vencimiento": "Fecha vencimiento",
                        "fact_importe_facturado": "Importe facturado",
                        "fact_estado_pago": "Estado pago"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader("Detalle de facturación")

        st.dataframe(
            df_facturacion_filtrada[
                [
                    "fact_numero_factura",
                    "fact_fecha_factura",
                    "fact_fecha_vencimiento",
                    "fact_importe_facturado",
                    "fact_estado_pago"
                ]
            ].rename(
                columns={
                    "fact_numero_factura": "Número factura",
                    "fact_fecha_factura": "Fecha factura",
                    "fact_fecha_vencimiento": "Fecha vencimiento",
                    "fact_importe_facturado": "Importe facturado",
                    "fact_estado_pago": "Estado pago"
                }
            ),
            hide_index=True,
            use_container_width=True
        )

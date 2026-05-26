# IMPORTACIONES

import streamlit as st
import pandas as pd

# CONFIGURACIÓN PÁGINA
st.set_page_config(
    page_title="Portal Sally Consultory",
    layout="wide"
)

# CARGA DE DATOS

df = pd.read_csv("fact_tareas_gestoria.csv")
df_facturacion = pd.read_csv("fact_facturacion_gestoria.csv")
df_clientes = pd.read_csv("dim_clientes_gestoria.csv")
df_empleados = pd.read_csv("dim_empleados_gestoria.csv")
df_servicios = pd.read_csv("dim_servicios_gestoria.csv")

# ORDENAR CLIENTES
df_clientes = df_clientes.sort_values("dim_id_cliente")

# CREAR LABEL CLIENTE (ANTES DE USARLO)
df_clientes["cliente_display"] = (
    df_clientes["dim_id_cliente"].astype(str)
    + " - "
    + df_clientes["dim_nombre_empresa"]
)

# SELECTOR CLIENTE

cliente_seleccionado = st.selectbox(
    "Selecciona cliente",
    ["ID Cliente - Nombre Empresa"] + list(df_clientes["cliente_display"])
)

if cliente_seleccionado == "ID Cliente - Nombre Empresa":
    st.stop()

cliente = int(cliente_seleccionado.split(" - ")[0])

# REEMPLAZAR ID EMPLEADO POR NOMBRE
df = df.merge(
    df_empleados[["dim_id_empleado", "dim_nombre"]],
    left_on="fact_id_empleado",
    right_on="dim_id_empleado",
    how="left"
)

# REEMPLAZAR ID SERVICIO POR NOMBRE
df = df.merge(
    df_servicios[["dim_id_servicio", "dim_nombre_servicio"]],
    left_on="fact_id_servicio",
    right_on="dim_id_servicio",
    how="left"
)

# FORMATO IMPORTE
df_facturacion_filtrada["fact_importe_facturado"] = (
        df_facturacion_filtrada["fact_importe_facturado"]
        .map("{:,.2f} €".format)
)

# ORDEN FACTURAS
df_facturacion_filtrada = df_facturacion_filtrada.sort_values(
        "fact_fecha_vencimiento"
)

# TABS
tab1, tab2 = st.tabs(["Gestión de tareas", "Gestión financiera"])

 
# TABLA 1 - TAREAS

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

# TABLA 2 - FACTURACIÓN
    
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

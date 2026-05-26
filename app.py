# IMPORTACIONES

import streamlit as st
import pandas as pd

# CONFIGURACIÓN PÁGINA
st.set_page_config(
    page_title="Portal Sally Consultory",
    layout="wide"
)

# =========================
# CARGA DE DATOS
# =========================

df = pd.read_csv("fact_tareas_gestoria.csv")
df_facturacion = pd.read_csv("fact_facturacion_gestoria.csv")
df_clientes = pd.read_csv("dim_clientes_gestoria.csv")
df_empleados = pd.read_csv("dim_empleados_gestoria.csv")
df_servicios = pd.read_csv("dim_servicios_gestoria.csv")

# =========================
# PREPARAR CLIENTES
# =========================

df_clientes = df_clientes.sort_values("dim_id_cliente")

df_clientes["cliente_display"] = (
    df_clientes["dim_id_cliente"].astype(str)
    + " - "
    + df_clientes["dim_nombre_empresa"]
)

# =========================
# SELECTOR CLIENTE (YA CON DATOS)
# =========================

cliente_seleccionado = st.selectbox(
    "Selecciona cliente",
    df_clientes["cliente_display"]
)

cliente = int(cliente_seleccionado.split(" - ")[0])

# =========================
# FILTROS
# =========================

df_filtrado = df[df["fact_id_cliente"] == cliente]

df_facturacion_filtrada = df_facturacion[
    df_facturacion["fact_id_cliente"] == cliente
]

# =========================
# MERGE DATOS
# =========================

df = df.merge(
    df_empleados[["dim_id_empleado", "dim_nombre"]],
    left_on="fact_id_empleado",
    right_on="dim_id_empleado",
    how="left"
)

df = df.merge(
    df_servicios[["dim_id_servicio", "dim_nombre_servicio"]],
    left_on="fact_id_servicio",
    right_on="dim_id_servicio",
    how="left"
)

# =========================
# FORMATO FACTURAS
# =========================

df_facturacion_filtrada["fact_importe_facturado"] = (
    df_facturacion_filtrada["fact_importe_facturado"]
    .map("{:,.2f} €".format)
)

df_facturacion_filtrada = df_facturacion_filtrada.sort_values(
    "fact_fecha_vencimiento"
)

# =========================
# TÍTULO
# =========================

st.title("Sally Consultory")

# =========================
# TABS
# =========================

tab1, tab2 = st.tabs(["Gestión de tareas", "Gestión financiera"])

# =========================
# TAB 1
# =========================

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

# =========================
# TAB 2
# =========================

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

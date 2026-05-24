import streamlit as st
import pandas as pd

# =====================================================
# CARGA DE DATOS CSV
# =====================================================

df = pd.read_csv("fact_tareas_gestoria.csv")

df_facturacion = pd.read_csv(
    "fact_facturacion_gestoria.csv"
)

df_clientes = pd.read_csv(
    "dim_clientes_gestoria.csv"
)

df_empleados = pd.read_csv(
    "dim_empleados_gestoria.csv"
)

df_servicios = pd.read_csv(
    "dim_servicios_gestoria.csv"
)

# =====================================================
# ORDENAR CLIENTES
# =====================================================

df_clientes = df_clientes.sort_values("dim_id_cliente")

# =====================================================
# TEXTO VISUAL CLIENTE
# =====================================================

df_clientes["cliente_display"] = (
    df_clientes["dim_id_cliente"].astype(str)
    + " - "
    + df_clientes["dim_nombre_empresa"]
)

# =====================================================
# TÍTULO
# =====================================================

st.title("Portal Sally Consultory")

# =====================================================
# FILTRO GLOBAL CLIENTE
# =====================================================

cliente_seleccionado = st.selectbox(
    "Selecciona cliente",
    df_clientes["cliente_display"]
)

cliente = int(cliente_seleccionado.split(" - ")[0])

# =====================================================
# FILTRADOS
# =====================================================

df_filtrado = df[
    df["fact_id_cliente"] == cliente
]

df_facturacion_filtrada = df_facturacion[
    df_facturacion["fact_id_cliente"] == cliente
]

# =====================================================
# JOIN EMPLEADOS
# =====================================================

df_filtrado = df_filtrado.merge(
    df_empleados[
        ["dim_id_empleado", "dim_nombre"]
    ],
    left_on="fact_id_empleado",
    right_on="dim_id_empleado",
    how="left"
)

# =====================================================
# JOIN SERVICIOS
# =====================================================

df_filtrado = df_filtrado.merge(
    df_servicios[
        ["dim_id_servicio", "dim_nombre_servicio"]
    ],
    left_on="fact_id_servicio",
    right_on="dim_id_servicio",
    how="left"
)

# =====================================================
# RENOMBRE COLUMNAS TAREAS
# =====================================================

df_filtrado = df_filtrado.rename(columns={
    "fact_id_tarea": "ID Tarea",
    "dim_nombre": "Empleado",
    "dim_nombre_servicio": "Servicio",
    "fact_estado": "Estado",
    "fact_prioridad": "Prioridad",
    "fact_fecha_inicio": "Fecha inicio",
    "fact_fecha_fin": "Fecha fin",
    "fact_fecha_entrega": "Fecha entrega",
    "fact_horas_dedicadas": "Horas dedicadas"
})

# =====================================================
# RENOMBRE COLUMNAS FACTURACIÓN
# =====================================================

df_facturacion_filtrada = df_facturacion_filtrada.rename(columns={
    "fact_numero_factura": "Número factura",
    "fact_fecha_factura": "Fecha factura",
    "fact_fecha_vencimiento": "Fecha vencimiento",
    "fact_importe_facturado": "Importe facturado (€)",
    "fact_estado_pago": "Estado pago"
})

# =====================================================
# PESTAÑAS
# =====================================================

tab1, tab2 = st.tabs(["Tareas", "Facturación"])

# =====================================================
# TAB 1 - TAREAS
# =====================================================

with tab1:

    st.subheader("Tareas del cliente")

    # KPI GENERAL
    st.metric("Total tareas", len(df_filtrado))

    # KPI ESTADOS
    completadas = len(
        df_filtrado[df_filtrado["Estado"] == "completado"]
    )

    retrasadas = len(
        df_filtrado[df_filtrado["Estado"] == "retrasado"]
    )

    en_progreso = len(
        df_filtrado[df_filtrado["Estado"] == "en progreso"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("🟢 Completadas", completadas)

    col2.metric("🔴 Retrasadas", retrasadas)

    col3.metric("🟡 En progreso", en_progreso)

    # TABLA
    st.subheader("Detalle de tareas")

    st.dataframe(
        df_filtrado[
            [
                "ID Tarea",
                "Empleado",
                "Servicio",
                "Estado",
                "Prioridad",
                "Fecha inicio",
                "Fecha fin",
                "Fecha entrega",
                "Horas dedicadas"
            ]
        ]
    )

# =====================================================
# TAB 2 - FACTURACIÓN
# =====================================================

with tab2:

    st.subheader("Facturación del cliente")

    # KPI FACTURACIÓN
    total_facturado = (
        df_facturacion_filtrada[
            "Importe facturado (€)"
        ].sum()
    )

    facturas_pagadas = len(
        df_facturacion_filtrada[
            df_facturacion_filtrada["Estado pago"] == "pagado"
        ]
    )

    facturas_pendientes = len(
        df_facturacion_filtrada[
            df_facturacion_filtrada["Estado pago"] == "pendiente"
        ]
    )

    facturas_vencidas = len(
        df_facturacion_filtrada[
            df_facturacion_filtrada["Estado pago"] == "vencido"
        ]
    )

    col1, col2, col3, col4 = st.columns([2,1,1,1])

    col1.metric(
        "Total facturado",
        f"{total_facturado:,.2f} €"
    )

    col2.metric(
        "🟢 Pagadas",
        facturas_pagadas
    )

    col3.metric(
        "🟡 Pendientes",
        facturas_pendientes
    )

    col4.metric(
        "🔴 Vencidas",
        facturas_vencidas
    )

    # TABLA FACTURACIÓN
    st.subheader("Detalle de facturación")

    st.dataframe(
        df_facturacion_filtrada[
            [
                "Número factura",
                "Fecha factura",
                "Fecha vencimiento",
                "Importe facturado (€)",
                "Estado pago"
            ]
        ]
    )
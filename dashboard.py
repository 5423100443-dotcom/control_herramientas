import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import base64
from streamlit_autorefresh import st_autorefresh
# Auto refresh cada 5 segundos
from supabase import create_client
import io

SUPABASE_URL = "https://jkoqclfxupxmudknavco.supabase.co"
SUPABASE_KEY = "sb_publishable_kZBqiDGMP0lQpQrm-PhYZg_hpkGb_xC"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Control Tool Crib CNC", layout="wide")
st_autorefresh(interval=5000, key="refresh")
# =========================
# USUARIOS
# =========================


# =========================
# FUNCIÓN LOGIN
# =========================
def login():
    st.title("🔐 Iniciar Sesión")

    usuario = st.text_input("Número de Empleado")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        response = supabase.table("usuarios") \
            .select("*") \
            .eq("empleado", usuario) \
            .eq("password", contraseña) \
            .execute()

        if response.data:

            usuario_data = response.data[0]

            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["rol"] = usuario_data["rol"]

            st.rerun()

        else:
            st.error("Usuario o contraseña incorrectos")
# =========================
# CONTROL DE SESIÓN
# =========================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

# =========================
# BOTÓN CERRAR SESIÓN
# =========================
if st.button("Cerrar sesión"):
    st.session_state["autenticado"] = False
    st.rerun()

# =========================
# FONDO INDUSTRIAL OSCURO (VERSIÓN ESTABLE)
# =========================
def poner_fondo():
    with open("fondo_cnc.png", "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()

    fondo_css = """
    <style>
    .stApp {
        background: linear-gradient(
            rgba(0,0,0,0.55),
            rgba(0,0,0,0.55)
        ),
        url("data:image/png;base64,%s");
        background-size: cover;
        background-attachment: fixed;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }

    .stSelectbox label {
        color: white !important;
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """ % encoded

    st.markdown(fondo_css, unsafe_allow_html=True)

poner_fondo()

# =========================
# TÍTULO
# =========================
st.title("🏭 Sistema de Control de Herramientas CNC")

st.markdown("## 💾 Backup de Datos")

if st.button("⬇ Descargar Backup Excel"):

    response = supabase.table("registros").select("*").execute()
    df_backup = pd.DataFrame(response.data)

    buffer = io.BytesIO()

    df_backup.to_excel(buffer, index=False, engine="openpyxl")

    st.download_button(
        label="📥 Descargar Archivo",
        data=buffer.getvalue(),
        file_name="backup_herramientas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =========================
# CARGAR BASE DE DATOS
# =========================
response = supabase.table("registros").select("*").execute()

df = pd.DataFrame(response.data)

if df.empty:
    st.warning("No hay registros en la base de datos.")
    st.stop()

# =========================
# PROCESAR FECHA Y MES
# =========================
df["fecha"] = pd.to_datetime(df["fecha"])
df["mes"] = df["fecha"].dt.strftime("%Y-%m")

# =========================
# FILTROS
# =========================
st.markdown("## 🔎 Filtros")

col1, col2, col3 = st.columns(3)

meses = ["Todos"] + sorted(df["mes"].unique(), reverse=True)
maquinas = ["Todas"] + sorted(df["maquina"].unique())
empleados = ["Todos"] + sorted(df["empleado"].unique())

with col1:
    mes_seleccionado = st.selectbox("📅 Selecciona Mes", meses)

with col2:
    maquina_seleccionada = st.selectbox("🏭 Selecciona Máquina", maquinas)

if st.session_state["rol"] == "Supervisor":
    with col3:
        empleado_seleccionado = st.selectbox("👷 Selecciona Empleado", empleados)
else:
    empleado_seleccionado = st.session_state["usuario"]
# =========================
# FILTRAR DATOS DINÁMICO
# =========================
df_filtrado = df.copy()
filtros_aplicados = False

# CONTROL POR ROL
if st.session_state["rol"] == "Operador":
    df_filtrado = df_filtrado[
        df_filtrado["empleado"] == st.session_state["usuario"]
    ]

if mes_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["mes"] == mes_seleccionado]
    filtros_aplicados = True

if maquina_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina_seleccionada]
    filtros_aplicados = True

if empleado_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["empleado"] == empleado_seleccionado]
    filtros_aplicados = True

# 🚫 Si no hay filtros, no mostrar nada
if not filtros_aplicados:
    st.info("Selecciona al menos un filtro para mostrar información.")
    st.stop()

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# =========================
# KPIs
# =========================
st.markdown("## 📌 Resumen General")

col1, col2 = st.columns(2)

total_gastado = df_filtrado["precio"].sum()
total_cambios = len(df_filtrado)

with col1:
    st.metric("💰 Total Gastado", f"${total_gastado:,.2f}")

with col2:
    st.metric("🔧 Total de Cambios", total_cambios)

# =========================
# HISTORIAL
# =========================
st.markdown("## 📋 Historial")

if not df_filtrado.empty:

    tabla = df_filtrado[[
        "fecha",
        "empleado",
        "maquina",
        "herramienta",
        "tipo_cambio",
        "motivo",
        "precio"
    ]].copy()

    # Calcular altura dinámica según cantidad de filas
    filas = len(tabla)
    alto_tabla = min(600, 60 + (filas * 35))  # 35px por fila + encabezado

    st.data_editor(
        tabla,
        hide_index=True,
        width="stretch",
        height=alto_tabla,
        column_config={
            "fecha": st.column_config.DatetimeColumn("Fecha"),
            "empleado": st.column_config.NumberColumn("Empleado"),
            "maquina": st.column_config.TextColumn("Máquina"),
            "herramienta": st.column_config.TextColumn("Herramienta"),
            "tipo_cambio": st.column_config.TextColumn("Tipo Cambio"),
            "motivo": st.column_config.TextColumn("Motivo"),
            "precio": st.column_config.NumberColumn(
                "Precio ($)",
                format="$ %.2f"
            )
        },
        disabled=True
    )

else:
    st.info("No hay registros para los filtros seleccionados.")
# =========================
# GRÁFICA 1 - CANTIDAD CAMBIOS
# =========================
df_cambios = (
    df_filtrado
    .groupby("herramienta")
    .size()
    .reset_index(name="cantidad_cambios")
    .sort_values(by="cantidad_cambios", ascending=False)
)

if not df_cambios.empty:

    fig_cambios = px.bar(
        df_cambios,
        x="herramienta",
        y="cantidad_cambios",
        text="cantidad_cambios",
        color="cantidad_cambios",
        color_continuous_scale="Blues",
        title="🔧 Cantidad de Cambios por Herramienta"
    )

    fig_cambios.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig_cambios.update_layout(
        template="plotly_dark",
        title_x=0.5,
        xaxis_title="Herramienta",
        yaxis_title="Cantidad de Cambios",
        margin=dict(t=120)  # 👈 espacio extra arriba
    )

    fig_cambios.update_layout(
        template="plotly_dark",
        title_x=0.5,
        xaxis_title="Herramienta",
        yaxis_title="Cantidad de Cambios"
    )

    st.plotly_chart(fig_cambios, use_container_width=True)

else:
    st.info("No hay datos para mostrar.")

# =========================
# GRÁFICA 2 - GASTO POR HERRAMIENTA
# =========================
df_gasto = (
    df_filtrado
    .groupby("herramienta")["precio"]
    .sum()
    .reset_index()
    .sort_values(by="precio", ascending=False)
)
if not df_gasto.empty:

    fig_gasto = px.bar(
        df_gasto,
        x="herramienta",
        y="precio",
        text="precio",
        color="precio",
        color_continuous_scale="Greens",
        title="💰 Gasto Total por Herramienta"
    )

    fig_gasto.update_traces(
        texttemplate='$%{text:,.2f}',
        textposition="outside",
        cliponaxis=False
    )

    fig_gasto.update_layout(
        template="plotly_dark",
        title_x=0.5,
        xaxis_title="Herramienta",
        yaxis_title="Total Gastado ($)",
        margin=dict(t=120)  # 👈 espacio arriba
    )

    fig_gasto.update_layout(
        template="plotly_dark",
        title_x=0.5,
        xaxis_title="Herramienta",
        yaxis_title="Total Gastado ($)"
    )

    st.plotly_chart(fig_gasto, use_container_width=True)

else:
    st.info("No hay datos para mostrar.")




 

   




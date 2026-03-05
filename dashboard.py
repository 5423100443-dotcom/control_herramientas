import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from streamlit_autorefresh import st_autorefresh
from supabase import create_client
import time

# =========================
# SUPABASE (SECRETS)
# =========================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# CONFIG STREAMLIT
# =========================

st.set_page_config(
    page_title="Control Tool Crib CNC",
    page_icon="logo.png",
    layout="centered"
)

# =========================
# CONTROL DE SESIÓN
# =========================

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "mostrar_bienvenida" not in st.session_state:
    st.session_state["mostrar_bienvenida"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

if "rol" not in st.session_state:
    st.session_state["rol"] = None

# refresh automático
if st.session_state["autenticado"]:
    st_autorefresh(interval=10000, key="refresh")

# =========================
# LOGIN
# =========================

def login():

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.image("logo.png", width=220)

        st.markdown(
        "<h2 style='text-align:center;'>Control Tool Crib CNC</h2>",
        unsafe_allow_html=True
        )

        st.markdown("---")

        usuario = st.text_input("Número de Empleado")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):

            try:

                response = supabase.table("usuarios") \
                    .select("*") \
                    .eq("empleado", usuario) \
                    .eq("password", password) \
                    .execute()

                if response.data:

                    usuario_data = response.data[0]

                    st.session_state["autenticado"] = True
                    st.session_state["mostrar_bienvenida"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["rol"] = usuario_data["rol"].lower()

                    st.rerun()

                else:
                    st.error("Usuario o contraseña incorrectos")

            except Exception as e:

                st.error("Error conectando con la base de datos")
                st.write(e)

# =========================
# BIENVENIDA
# =========================

def bienvenida():

    with open("bienvenida2.png","rb") as f:
        img = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>

    .stApp {{
        background-image:url("data:image/png;base64,{img}");
        background-size:cover;
        background-position:center;
    }}

    .center-box {{
        position:fixed;
        top:50%;
        left:50%;
        transform:translate(-50%,-50%);
        text-align:center;
        color:white;
    }}

    .titulo {{
        font-size:60px;
        font-weight:bold;
    }}

    .empleado {{
        font-size:28px;
    }}

    </style>

    <div class="center-box">
        <div class="titulo">BIENVENIDO</div>
        <div class="empleado">Empleado {st.session_state["usuario"]}</div>
    </div>

    """,unsafe_allow_html=True)

    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.02)
        progress.progress(i+1)

    st.session_state["mostrar_bienvenida"] = False
    st.rerun()

# =========================
# FLUJO
# =========================

if not st.session_state["autenticado"]:
    login()
    st.stop()

if st.session_state["mostrar_bienvenida"]:
    bienvenida()
    st.stop()

# =========================
# LOGOUT
# =========================

if st.button("Cerrar sesión"):
    st.session_state["autenticado"] = False
    st.rerun()

# =========================
# FONDO
# =========================

def poner_fondo():

    with open("fondo_cnc.png","rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>

    .stApp {{
    background:linear-gradient(
    rgba(0,0,0,0.55),
    rgba(0,0,0,0.55)
    ),
    url("data:image/png;base64,{encoded}");
    background-size:cover;
    }}

    h1,h2,h3,p,label {{
    color:white !important;
    }}

    </style>
    """,unsafe_allow_html=True)

poner_fondo()

# =========================
# TITULO
# =========================

st.title("🏭 Sistema de Control de Herramientas CNC")

rol = st.session_state["rol"]

# =========================
# TABS SEGUN ROL
# =========================

if rol == "operador":

    tab_dashboard = st.tabs(["📊 Dashboard"])[0]

elif rol == "toolcrib":

    tab_solicitudes, tab_dashboard = st.tabs([
        "📦 Solicitudes",
        "📊 Dashboard"
    ])

elif rol == "supervisor":

    tab_dashboard, tab_solicitudes, tab_empleados = st.tabs([
        "📊 Dashboard",
        "📦 Tool Crib",
        "👷 Empleados"
    ])

# =========================
# DASHBOARD
# =========================

with tab_dashboard:

    response = supabase.table("registros").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("No hay registros")
        st.stop()

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.strftime("%Y-%m")

    st.markdown("## 🔎 Filtros")

    col1,col2,col3 = st.columns(3)

    meses = ["Seleccionar"] + sorted(df["mes"].unique(), reverse=True)
    maquinas = ["Seleccionar"] + sorted(df["maquina"].unique())
    empleados = ["Seleccionar"] + sorted(df["empleado"].unique())

    with col1:
        mes = st.selectbox("Mes", meses)

    with col2:
        maquina = st.selectbox("Máquina", maquinas)

    if rol == "supervisor":
        with col3:
            empleado = st.selectbox("Empleado", empleados)
    else:
        empleado = st.session_state["usuario"]

    df_filtrado = df.copy()
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

        
    if rol == "operador":
        df_filtrado = df_filtrado[df_filtrado["empleado"] == empleado]

    if mes != "Todos":
        df_filtrado = df_filtrado[df_filtrado["mes"] == mes]

    if maquina != "Todas":
        df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina]

    if empleado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["empleado"] == empleado]

    df_filtrado = df_filtrado.sort_values("fecha", ascending=False)

    st.markdown("## 📌 Resumen")

    col1,col2 = st.columns(2)

    with col1:
        st.metric("💰 Total Gastado", f"${df_filtrado['precio'].sum():,.2f}")

    with col2:
        st.metric("🔧 Cambios", len(df_filtrado))

    st.markdown("## 📋 Historial")

    st.dataframe(df_filtrado)

# =========================
# TOOLCRIB
# =========================

if rol in ["toolcrib","supervisor"]:

    with tab_solicitudes:

        st.subheader("📦 Solicitudes")

        response = supabase.table("solicitudes_herramienta") \
        .select("*") \
        .eq("estado","pendiente") \
        .execute()

        df_sol = pd.DataFrame(response.data)

        if df_sol.empty:
            st.info("No hay solicitudes")

        else:

            for i,row in df_sol.iterrows():

                col1,col2,col3 = st.columns([2,2,1])

                with col1:
                    st.write("Empleado:",row["empleado"])
                    st.write("Máquina:",row["maquina"])

                with col2:
                    st.write("Herramienta:",row["herramienta"])
                    st.write("Motivo:",row["motivo"])

                with col3:

                    if st.button("Entregar",key=i):

                        data = {
                        "fecha":row["fecha"],
                        "empleado":row["empleado"],
                        "maquina":row["maquina"],
                        "herramienta":row["herramienta"],
                        "descripcion":row["descripcion"],
                        "tipo_cambio":row["tipo_cambio"],
                        "motivo":row["motivo"],
                        "precio":row["precio"],
                        "entregado_por":st.session_state["usuario"]
                        }

                        supabase.table("registros").insert(data).execute()

                        supabase.table("solicitudes_herramienta") \
                        .update({"estado":"entregado"}) \
                        .eq("id",row["id"]) \
                        .execute()

                        st.rerun()

# =========================
# SUPERVISOR EMPLEADOS
# =========================

if rol == "supervisor":

    response = supabase.table("registros").select("*").execute()
    df = pd.DataFrame(response.data)

    with tab_empleados:

        st.subheader("👷 Historial empleados")

        empleados_lista = sorted(df["empleado"].unique())

        tabs_emp = st.tabs([f"Empleado {e}" for e in empleados_lista])

        for i,emp in enumerate(empleados_lista):

            with tabs_emp[i]:

                df_emp = df[df["empleado"] == emp]

                st.dataframe(df_emp)



 

   







































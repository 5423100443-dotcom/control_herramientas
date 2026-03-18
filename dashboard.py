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

if "nombre" not in st.session_state:
    st.session_state["nombre"] = None

if "rol" not in st.session_state:
    st.session_state["rol"] = None

# refresh automático
if st.session_state["autenticado"] and not st.session_state["mostrar_bienvenida"]:
    st_autorefresh(interval=5000, key="refresh")
# =========================
# RESTAURAR SESIÓN
# =========================

params = st.query_params

if "usuario" in params and "rol" in params:

    st.session_state["autenticado"] = True
    st.session_state["usuario"] = params["usuario"]
    st.session_state["rol"] = params["rol"]

    response = supabase.table("usuarios") \
        .select("nombre") \
        .eq("empleado", params["usuario"]) \
        .execute()

    if response.data:
        st.session_state["nombre"] = response.data[0]["nombre"]

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
                    st.query_params["usuario"] = usuario
                    st.session_state["nombre"] = usuario_data["nombre"]
                    st.query_params["rol"] = usuario_data["rol"].lower()
                    

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
    st.session_state.clear()
    st.query_params.clear()
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

#=====================================================
#Configuracion color botones entregar y cerrar secion
#=====================================================

st.markdown("""
<style>

/* BOTON CERRAR SESION */
button[data-testid="baseButton-secondary"] {
    background-color: transparent !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
}

/* BOTON ENTREGAR */
button[kind="secondary"] {
    background-color: transparent !important;
    color: white !important;
}

/* HOVER */
button[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# =========================
# TITULO
# =========================

st.title("🏭 Sistema de Control de Herramientas CNC")
rol = (st.session_state.get("rol","")).lower()
col1, col2 = st.columns([8,2])

st.markdown("""
<style>

.user-info {
    color: white;
    font-size: 18px;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)


with col2:
    st.markdown(
        f"""
        <div style="text-align:right; font-size:16px; color:white; front-wheirht:600">
        👤 <b>{st.session_state.get('nombre','')}({st.session_state['usuario']})</b><br>
        🔐 {st.session_state['rol'].capitalize()}
        </div>
        """,
        unsafe_allow_html=True
    )



# =========================
# TABS
# =========================

if rol == "tecnico":

    tab_dashboard = st.tabs(["📊 Dashboard"])[0]

else:

    tab_dashboard, tab_solicitudes = st.tabs([
        "📊 Dashboard",
        "📦 Tool Crib"
    ])
# =========================
# DASHBOARD
# =========================

with tab_dashboard:

    response = supabase.table("registros").select("*").execute()
    df = pd.DataFrame(response.data)
        # Si no hay datos evitar crash
        
    
    # asegurar columnas necesarias
    columnas = [
        "fecha",
        "nombre",
        "empleado",
        "entregado_nombre",
        "entregado_por",
        "maquina",
        "herramienta",
        "tipo_cambio",
        "motivo",
        "precio"
    ]
    
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    
    # convertir fecha seguro
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if rol == "tecnico":
        df = df[df["empleado"] == st.session_state["usuario"]]

    elif rol == "toolcrib":
        df = df[df["entregado_por"] == st.session_state["usuario"]]

    elif rol == "supervisor":
        df = df

    if df.empty:
        st.warning("No hay registros")
        mostrar_dashboard = False
    else:
        mostrar_dashboard = True

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

    if rol == "supervisor":

        if mes == "Seleccionar" and maquina == "Seleccionar" and empleado == "Seleccionar":
            st.warning("Selecciona al menos un filtro para mostrar información.")
            mostrar_dashboard = False
        else:
            mostrar_dashboard = True

    else:

        if mes == "Seleccionar" and maquina == "Seleccionar":
            st.warning("Selecciona Mes o Máquina para ver información.")
            mostrar_dashboard = False
        else:
            mostrar_dashboard = True

    if mostrar_dashboard:
        

         # aplicar filtros
        if mes != "Seleccionar":
            df_filtrado = df_filtrado[df_filtrado["mes"] == mes]
                
        if maquina != "Seleccionar":
            df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina]
                
        if rol == "supervisor" and empleado != "Seleccionar":
            df_filtrado = df_filtrado[df_filtrado["empleado"] == empleado]
            
    
        
               
        # verificar si quedó vacío
        if df_filtrado.empty:
            st.warning("No hay datos con los filtros seleccionados.")
            
    
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
                "nombre",
                "empleado",
                "entregado_nombre",
                "entregado_por",
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
                    "nombre":st.column_config.TextColumn("Solicitado por"),
                    "empleado":st.column_config.NumberColumn("Empleado"),
                    "entregado_nombre":st.column_config.TextColumn("Entregado por"),
                    "entregado_por":st.column_config.TextColumn("ID ToolCrib"),
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

        response = supabase.table("solicitudes_herramienta").select("*").execute()

        df_sol = pd.DataFrame(response.data)
        st.write("solicitudes recibidas:",len(df_sol))
        
        if df_sol.empty:
            st.info("No hay solicitudes")
        
        else:
        
            if "estado" not in df_sol.columns:
                df_sol["estado"] = "pendiente"

            df_sol["estado"] = df_sol["estado"].fillna("pendiente")
            df_sol["estado"] = df_sol["estado"].astype(str).str.strip().str.lower()
            df_sol = df_sol[df_sol["estado"] == "pendiente"]
        
            if df_sol.empty:
                st.warning("No hay solicitudes pendientes")
        
            else:
        
                df_sol["fecha"] = pd.to_datetime(df_sol["fecha"],errors="coerce")
        
                pendientes=len(df_sol)
        
                st.subheader(f"Solicitudes ({pendientes})")
        
                for i,row in df_sol.iterrows():
        
                    st.markdown("---")
        
                    col1,col2,col3=st.columns([2,2,1])
        
                    with col1:
        
                        st.write(f"Empleado: {row.get('nombre','Sin nombre')} ({row.get('empleado','')})")
        
                        st.write(f"Máquina: {row.get('maquina','')}")
        
                        st.write(f"Herramienta: {row.get('herramienta','')}")
        
                    with col2:
        
                        if "inserto" in str(row.get("tipo_cambio","")).lower():
        
                            st.info(f"Inserto: {row.get('descripcion','')}")
        
                            st.write(f"Cantidad: {row.get('cantidad_insertos',0)}")
        
                        else:
        
                            st.success("Herramienta completa")
        
                        st.write(f"Motivo: {row.get('motivo','')}")
        
                    with col3:
        
                        if st.button("Entregar",key=f"entregar_{i}"):
        
                            data={

                                        "fecha": str(row.get("fecha")),
                                        "empleado": str(row.get("empleado")),
                                        "nombre": str(row.get("nombre","")),
                                        "maquina": str(row.get("maquina")),
                                        "herramienta": str(row.get("herramienta")),
                                        "descripcion": str(row.get("descripcion")),
                                        "tipo_cambio": str(row.get("tipo_cambio")),
                                        "motivo": str(row.get("motivo")),
                                        "precio": float(row.get("precio") or 0),
                                        "entregado_por": str(st.session_state["usuario"]),
                                        "entregado_nombre": str(st.session_state.get("nombre",""))
                                    
                                    }
                                        
                            supabase.table("registros").insert(data).execute()
        
                            supabase.table("solicitudes_herramienta")\
                            .update({"estado":"entregado"})\
                            .eq("empleado",row["empleado"])\
                            .eq("fecha",str(row["fecha"]))\
                            .execute()
        
                            st.rerun()




 

   















































































































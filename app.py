import tkinter as tk
from tkinter import messagebox
import os
import sys
import sqlite3
from datetime import datetime
import subprocess
from PIL import Image, ImageTk
import pandas as pd
from supabase import create_client

url = "https://jkoqclfxupxmudknavco.supabase.co"
key = "sb_publishable_kZBqiDGMP0lQpQrm-PhYZg_hpkGb_xC "
supabase = create_client(url, key)

# =========================
# RUTA BASE
# =========================
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

db_path = os.path.join(base_path, "toolcrib.db")

# =========================
# LOGIN
# =========================
def verificar_login():
    empleado = entry_login_empleado.get()
    password = entry_login_password.get()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT rol FROM usuarios WHERE empleado=? AND password=?",
        (empleado, password)
    )

    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        rol = usuario[0]
        ventana_login.destroy()
        abrir_app_principal(empleado, rol)
    else:
        messagebox.showerror("Error", "Empleado o contraseña incorrectos")

# ABRIR DASHBOARD
def abrir_dashboard():
    dashboard_path = os.path.join(base_path, "dashboard.py")
    subprocess.Popen(
        ["streamlit", "run", dashboard_path],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

# BUSCAR HERRAMIENTA
def buscar_herramienta(maquina, numero):
    maquina = maquina.upper().strip()
    if maquina.startswith("MC") and "_" not in maquina:
        maquina = maquina.replace("MC","MC-")

    df = pd.read_excel(
        "NLP-NHP5000 -6X HMC- 70 Pallet Mapping -LINE #1.xlsx",
        sheet_name=maquina,
        header=3,
        usecols="A:C"
    )

    df.columns = df.columns.str.strip()
    df["Tool Pot #"] = pd.to_numeric(df["Tool Pot #"], errors="coerce")


    numero =str(numero).upper().replace("T","").strip()
    numero = int(numero)

    herramienta = df[df["Tool Pot #"] == numero]

    if not herramienta.empty:
        fila = herramienta.iloc[0]

        return {
            "descripcion": f"{fila["Tool Type"]} - {fila[df.columns[2]]}",
            "detalle": fila[df.columns[2]],
            "precio_herramienta": 0,
            "precio_inserto": 0,
            "inserto": False
        }

    return None

# GUARDAR REGISTRO
def guardar_registro():

    maquina = entry_maquina.get().strip()
    herramienta = entry_herramienta.get().strip()
    motivo = entry_motivo.get().strip()
    tipo_cambio = opcion_cambio.get()
    empleado = empleado_logueado


    if not maquina or not herramienta:
        messagebox.showerror("Error", "Debes ingresar Máquina y Herramienta")
        return

    # Buscar datos en Excel
    datos = buscar_herramienta(maquina, herramienta)

    if not datos:
        messagebox.showerror("Error", "Herramienta no encontrada para esa máquina")
        return

    # Determinar precio según tipo de cambio
    if tipo_cambio == "Herramienta Completa":
        precio = datos["precio_herramienta"]
    else:
        precio = datos["precio_inserto"] if datos["inserto"] else 0

    # Fecha actual
    from datetime import datetime
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en Supabase
    data = {
        "fecha": fecha,
        "empleado": empleado,
        "maquina": maquina,
        "herramienta": herramienta,
        "tipo_cambio": tipo_cambio,
        "motivo": motivo,
        "precio": precio
    }

    supabase.table("registros").insert(data).execute()

    messagebox.showinfo("Éxito", "Registro guardado correctamente")

    # Limpiar campos
    entry_herramienta.delete(0, tk.END)
    entry_motivo.delete(0, tk.END)

# VENTANA PRINCIPAL
def abrir_app_principal(empleado, rol):
    global empleado_logueado
    empleado_logueado = empleado

    root = tk.Tk()
    root.title("Control de Herramientas CNC")
    root.geometry("420x500")
    root.resizable(False, False)
    root.configure(bg="#1e1e1e")

    # LOGO
    logo_path = os.path.join(base_path, "logo.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        img = img.resize((180, 80))
        logo = ImageTk.PhotoImage(img)
        label_logo = tk.Label(root, image=logo, bg="#1e1e1e")
        label_logo.image = logo
        label_logo.pack(pady=10)

    tk.Label(root, text=f"Empleado: {empleado}",
             bg="#1e1e1e", fg="white",
             font=("Arial", 10, "bold")).pack(pady=5)

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(pady=10)

    tk.Label(frame, text="Número de Máquina",
             bg="#1e1e1e", fg="white").pack()
    global entry_maquina
    entry_maquina = tk.Entry(frame, width=30)
    entry_maquina.pack(pady=5)

    tk.Label(frame,
             text="Número de Herramienta",
             bg="#1e1e1e",
             fg="white").pack()

    global entry_herramienta
    entry_herramienta = tk.Entry(frame, width=30)
    entry_herramienta.pack(pady=5)

    #  AQUI VA EL PASO 4
    entry_herramienta.bind("<FocusOut>", verificar_herramienta)

    #  LABEL DESCRIPCIÓN (VA DESPUÉS)
    global label_descripcion
    label_descripcion = tk.Label(frame,
                                 text="Descripción:",
                                 bg="#1e1e1e",
                                 fg="white")
    label_descripcion.pack(pady=5)

    global opcion_cambio
    opcion_cambio = tk.StringVar(value="Herramienta Completa")

    radio_completa = tk.Radiobutton(frame,
                                    text="Herramienta Completa",
                                    variable=opcion_cambio,
                                    value="Herramienta Completa",
                                    bg="#1e1e1e",
                                    fg="white",
                                    selectcolor="#1e1e1e")

    radio_completa.pack()

    global radio_inserto
    radio_inserto = tk.Radiobutton(frame,
                                   text="Solo Inserto",
                                   variable=opcion_cambio,
                                   value="Solo Inserto",
                                   bg="#1e1e1e",
                                   fg="white",
                                   selectcolor="#1e1e1e")

    radio_inserto.pack_forget()  #  oculto por defecto

    tk.Label(frame, text="Motivo de Cambio",
             bg="#1e1e1e", fg="white").pack()

    global entry_motivo
    entry_motivo = tk.Entry(frame, width=30)
    entry_motivo.pack(pady=5)

    tk.Button(root,
              text="Guardar Registro",
              bg="#007acc",
              fg="white",
              font=("Arial", 10, "bold"),
              width=22,
              height=2,
              command=guardar_registro).pack(pady=15)

    if rol == "Supervisor":
        tk.Button(root,
                  text="📊 Abrir Dashboard",
                  bg="#00a86b",
                  fg="white",
                  font=("Arial", 10, "bold"),
                  width=22,
                  height=2,
                  command=abrir_dashboard).pack(pady=5)

    root.mainloop()

def verificar_herramienta(event=None):

    maquina = entry_maquina.get().strip()
    herramienta = entry_herramienta.get().strip()

    datos = buscar_herramienta(maquina, herramienta)

    if datos:
        label_descripcion.config(text=f"Descripción: {datos['descripcion']}")

        if datos["inserto"]:
            radio_inserto.pack()  #  mostrar si lleva inserto
        else:
            radio_inserto.pack_forget()
            opcion_cambio.set("Herramienta Completa")

    else:
        label_descripcion.config(text="Descripción: No encontrada")
        radio_inserto.pack_forget()

# =========================
# VENTANA LOGIN
# =========================
ventana_login = tk.Tk()
ventana_login.title("Login Sistema CNC")
ventana_login.geometry("300x250")
ventana_login.resizable(False, False)
ventana_login.configure(bg="#1e1e1e")

tk.Label(ventana_login,
         text="Sistema Control Herramientas",
         bg="#1e1e1e",
         fg="white",
         font=("Arial", 12, "bold")).pack(pady=15)

tk.Label(ventana_login,
         text="Número de Empleado",
         bg="#1e1e1e",
         fg="white").pack()

entry_login_empleado = tk.Entry(ventana_login)
entry_login_empleado.pack(pady=5)

tk.Label(ventana_login,
         text="Contraseña",
         bg="#1e1e1e",
         fg="white").pack()

entry_login_password = tk.Entry(ventana_login, show="*")
entry_login_password.pack(pady=5)

tk.Button(ventana_login,
          text="Ingresar",
          bg="#007acc",
          fg="white",
          font=("Arial", 10, "bold"),
          width=15,
          command=verificar_login).pack(pady=15)

ventana_login.mainloop()
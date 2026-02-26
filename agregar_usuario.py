import sqlite3

def agregar_o_actualizar_usuario(numero, password, rol):
    conn = sqlite3.connect("toolcrib.db")
    cursor = conn.cursor()

    # Verificar si el usuario ya existe
    cursor.execute("SELECT * FROM usuarios WHERE empleado = ?", (numero,))
    usuario = cursor.fetchone()

    if usuario:
        # Si existe → actualizar
        cursor.execute("""
            UPDATE usuarios
            SET password = ?, rol = ?
            WHERE empleado = ?
        """, (password, rol, numero))

        print(f"🔄 Usuario {numero} actualizado correctamente")

    else:
        # Si no existe → agregar
        cursor.execute("""
            INSERT INTO usuarios (empleado, password, rol)
            VALUES (?, ?, ?)
        """, (numero, password, rol))

        print(f"✅ Usuario {numero} agregado correctamente")

    conn.commit()
    conn.close()


# EJEMPLOS
agregar_o_actualizar_usuario("26448", "1234", "Operador")
agregar_o_actualizar_usuario("26449", "1234", "Operador")
agregar_o_actualizar_usuario("40001", "admin1", "Supervisor")
agregar_o_actualizar_usuario("26447", "264518", "Operador")
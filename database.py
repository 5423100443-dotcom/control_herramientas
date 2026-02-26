import sqlite3

def crear_base():
    conn = sqlite3.connect("toolcrib.db")
    cursor = conn.cursor()

    # Tabla herramientas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS herramientas (
        numero TEXT PRIMARY KEY,
        descripcion TEXT,
        precio_herramienta REAL,
        precio_inserto REAL,
        lleva_inserto INTEGER
    )
    """)

    # Tabla movimientos con motivo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        empleado TEXT,
        maquina TEXT,
        herramienta TEXT,
        tipo_cambio TEXT,
        motivo TEXT,
        precio REAL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_base()
    print("Base de datos creada correctamente.")

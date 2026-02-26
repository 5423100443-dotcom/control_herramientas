import sqlite3

conn = sqlite3.connect("toolcrib.db")
cursor = conn.cursor()

# Agregar columna rol si no existe
try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT")
except:
    print("La columna ya existe")

# Actualizar usuario actual como supervisor
cursor.execute("""
UPDATE usuarios 
SET rol = 'Supervisor'
WHERE empleado = '26447'
""")

conn.commit()
conn.close()

print("Tabla actualizada correctamente")
import sqlite3

conn = sqlite3.connect("toolcrib.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios (empleado, password)
VALUES (?, ?)
""", ("26447", "1234"))

conn.commit()
conn.close()

print("Tabla usuarios creada correctamente")

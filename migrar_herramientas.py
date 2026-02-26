import sqlite3
import openpyxl

def migrar():
    conn = sqlite3.connect("toolcrib.db")
    cursor = conn.cursor()

    wb = openpyxl.load_workbook("herramientas_maestro.xlsx")
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        numero = row[0]
        descripcion = f"{row[2]} - {row[3]}"
        precio_herramienta = row[4]
        lleva_inserto = 1 if str(row[5]).strip().upper() in ["SI", "SÍ"] else 0
        precio_inserto = row[7] if lleva_inserto else 0

        cursor.execute("""
        INSERT OR REPLACE INTO herramientas
        (numero, descripcion, precio_herramienta, precio_inserto, lleva_inserto)
        VALUES (?, ?, ?, ?, ?)
        """, (numero, descripcion, precio_herramienta, precio_inserto, lleva_inserto))

    conn.commit()
    conn.close()
    print("Herramientas migradas correctamente.")

if __name__ == "__main__":
    migrar()

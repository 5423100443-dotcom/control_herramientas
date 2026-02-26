import sqlite3

conn = sqlite3.connect("toolcrib.db")
cursor = conn.cursor()

#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#print(cursor.fetchall())
cursor.execute("PRAGMA table_info(movimientos);")
#print(cursor.fetchall())
print(cursor.fetchall())
conn.close()
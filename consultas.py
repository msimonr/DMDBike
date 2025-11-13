import sqlite3
from datetime import datetime, UTC

DB_PATH = "bici.db"

def obtener_sesiones_con_km():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT * 
    FROM sesiones 
    WHERE km > 0;
    """)
    results = cur.fetchall()
    conn.close()

    if results:
        for row in results:
            print(row)
    else:
        print("No hay sesiones con kilómetros registrados.")

    print("Se subieron:", len(results), "personas")

def updateName(name, new_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    UPDATE sesiones 
    SET nombre = ? 
    WHERE nombre = ?;
    """, (new_name, name))
    conn.commit()
    conn.close()

def reemplazar_dia(old_day: str, new_day: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE sesiones
        SET creado_en = REPLACE(creado_en, ?, ?)
        WHERE creado_en LIKE ? || '%';
    """, (old_day, new_day, old_day))

    conn.commit()
    conn.close()

    

if __name__ == "__main__":
    obtener_sesiones_con_km()
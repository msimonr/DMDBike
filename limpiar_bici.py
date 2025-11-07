#!/usr/bin/env python3

import os
import sqlite3

DB_PATH = "bici.db"
UPLOADS_DIR = os.path.join("static", "uploads")

def reset_db():
    if not os.path.exists(DB_PATH):
        print(f"No existe {DB_PATH}, nada que limpiar.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # poner km en 0
    cur.execute("UPDATE estado SET km = 0.0 WHERE id = 1;")

    # borrar sesiones
    cur.execute("DELETE FROM sesiones;")

    conn.commit()
    conn.close()
    print("✔ Base reseteada (km=0, sesiones borradas).")

def limpiar_uploads():
    if not os.path.isdir(UPLOADS_DIR):
        print(f"No existe carpeta {UPLOADS_DIR}, me lo salto.")
        return

    borrados = 0
    for nombre in os.listdir(UPLOADS_DIR):
        ruta = os.path.join(UPLOADS_DIR, nombre)
        if os.path.isfile(ruta):
            os.remove(ruta)
            borrados += 1
    print(f"✔ Eliminadas {borrados} imágenes de {UPLOADS_DIR}.")

if __name__ == "__main__":
    reset_db()
    limpiar_uploads()

    # descomentá esto si también querés limpiar las fotos

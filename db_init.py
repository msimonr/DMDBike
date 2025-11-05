# db_init.py
import sqlite3
from datetime import datetime, UTC

conn = sqlite3.connect("bici.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS estado (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    km REAL NOT NULL,
    actualizado_en TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    km REAL,
    foto TEXT,
    veces_sorteada INTEGER NOT NULL DEFAULT 0,
    creado_en TEXT NOT NULL
);
""")

# insertar el registro único de estado si no existe
cur.execute("SELECT COUNT(*) FROM estado WHERE id = 1;")
if cur.fetchone()[0] == 0:
    cur.execute(
        "INSERT INTO estado (id, km, actualizado_en) VALUES (1, 0.0, ?);",
        (datetime.now(UTC).isoformat(),)
)

conn.commit()
conn.close()
print("DB lista.")